"""
QC Validator
Validates backlink content against quality thresholds
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from collections import Counter
import yaml

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger('preflight.qc')


class QCValidator:
    """Validates content against QC thresholds."""
    
    def __init__(self):
        self.db_conn = None
        
        # Load QC thresholds
        self.thresholds = {
            "approved_min": 85,
            "light_edits_min": 70,
            "weights": {
                "preflight": 0.25,
                "draft": 0.15,
                "anchor": 0.20,
                "trust": 0.15,
                "lsi": 0.15,
                "fit": 0.05,
                "compliance": 0.05
            }
        }
        
        self.auto_fix_attempts = 0
        self.max_auto_fixes = 1  # AUTO_FIX_ONCE
    
    async def connect(self, db_url: str):
        """Connect to database."""
        try:
            self.db_conn = psycopg2.connect(db_url)
            logger.info("Connected to database for QC operations")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
    
    async def validate(
        self,
        article_text: str,
        preflight_matrix: Optional[Dict[str, Any]] = None,
        auto_fix: bool = False,
        strict_mode: bool = False
    ) -> Dict[str, Any]:
        """Validate article against QC thresholds."""
        
        # Initialize scoring
        scores = {
            "preflight": 0,
            "draft": 0,
            "anchor": 0,
            "trust": 0,
            "lsi": 0,
            "fit": 0,
            "compliance": 0
        }
        
        issues = []
        auto_fixes = []
        
        # Parse article structure
        article_data = self._parse_article(article_text)
        
        # Validate preflight compliance
        if preflight_matrix:
            preflight_score, preflight_issues = self._validate_preflight_compliance(
                article_data, preflight_matrix
            )
            scores["preflight"] = preflight_score
            issues.extend(preflight_issues)
        else:
            scores["preflight"] = 50  # Default if no matrix
        
        # Validate draft quality
        draft_score, draft_issues = self._validate_draft_quality(article_data)
        scores["draft"] = draft_score
        issues.extend(draft_issues)
        
        # Validate anchor placement
        anchor_score, anchor_issues = self._validate_anchor_placement(
            article_data, preflight_matrix
        )
        scores["anchor"] = anchor_score
        issues.extend(anchor_issues)
        
        # Validate trust signals
        trust_score, trust_issues = self._validate_trust_signals(
            article_data, preflight_matrix
        )
        scores["trust"] = trust_score
        issues.extend(trust_issues)
        
        # Validate LSI terms
        lsi_score, lsi_issues = self._validate_lsi_terms(
            article_data, preflight_matrix
        )
        scores["lsi"] = lsi_score
        issues.extend(lsi_issues)
        
        # Validate voice fit
        fit_score, fit_issues = self._validate_voice_fit(
            article_data, preflight_matrix
        )
        scores["fit"] = fit_score
        issues.extend(fit_issues)
        
        # Validate compliance
        compliance_score, compliance_issues = self._validate_compliance(
            article_data, preflight_matrix
        )
        scores["compliance"] = compliance_score
        issues.extend(compliance_issues)
        
        # Calculate total score
        total_score = sum(
            score * self.thresholds["weights"][category]
            for category, score in scores.items()
        )
        total_score = round(total_score, 1)
        
        # Determine status
        if total_score >= self.thresholds["approved_min"]:
            status = "APPROVED"
        elif total_score >= self.thresholds["light_edits_min"]:
            status = "LIGHT_EDITS"
        else:
            status = "BLOCKED"
        
        # Attempt auto-fix if requested and allowed
        if auto_fix and self.auto_fix_attempts < self.max_auto_fixes:
            fixed_text, fixes = await self._attempt_auto_fix(
                article_text, article_data, issues, preflight_matrix
            )
            
            if fixed_text != article_text:
                self.auto_fix_attempts += 1
                auto_fixes.extend(fixes)
                
                # Re-validate with fixed text
                return await self.validate(
                    fixed_text,
                    preflight_matrix,
                    auto_fix=False,  # Don't recurse
                    strict_mode=strict_mode
                )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(scores, issues)
        
        # Check if human signoff required
        human_signoff_required = self._requires_human_signoff(issues, scores)
        
        # Determine next actions
        next_actions = self._determine_next_actions(status, issues, scores)
        
        return {
            "status": status,
            "score": total_score,
            "breakdown": scores,
            "issues": issues,
            "auto_fixes": auto_fixes,
            "recommendations": recommendations,
            "human_signoff_required": human_signoff_required,
            "next_actions": next_actions
        }
    
    def _parse_article(self, article_text: str) -> Dict[str, Any]:
        """Parse article into structured data."""
        lines = article_text.split('\n')
        
        sections = []
        current_section = None
        
        for i, line in enumerate(lines):
            # Check for headers
            if line.startswith('##'):
                if current_section:
                    sections.append(current_section)
                
                header_level = len(re.match(r'^#+', line).group())
                header_text = line.lstrip('#').strip()
                
                current_section = {
                    "type": "section",
                    "level": header_level,
                    "title": header_text,
                    "paragraphs": [],
                    "line_number": i
                }
            
            elif line.strip() and current_section:
                # Add to current section
                current_section["paragraphs"].append({
                    "text": line.strip(),
                    "line_number": i,
                    "has_link": "[[" in line and "]]" in line,
                    "sentences": self._split_sentences(line)
                })
        
        # Add last section
        if current_section:
            sections.append(current_section)
        
        # Extract all links
        links = self._extract_links(article_text)
        
        # Calculate word count
        word_count = len(re.findall(r'\b\w+\b', article_text))
        
        return {
            "sections": sections,
            "links": links,
            "word_count": word_count,
            "full_text": article_text
        }
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitter for Swedish/English
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_links(self, text: str) -> List[Dict[str, Any]]:
        """Extract all links from text."""
        links = []
        
        # Find [[link]] style links
        pattern = r'\[\[(.*?)\]\]'
        for match in re.finditer(pattern, text):
            links.append({
                "text": match.group(1),
                "start": match.start(),
                "end": match.end(),
                "full_match": match.group(0)
            })
        
        return links
    
    def _validate_preflight_compliance(
        self,
        article_data: Dict[str, Any],
        preflight_matrix: Dict[str, Any]
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """Validate compliance with preflight matrix."""
        score = 100
        issues = []
        
        # Check if target URL is linked
        if not any(link["text"] == preflight_matrix["anchor_plan"]["primary"] 
                  for link in article_data["links"]):
            score -= 30
            issues.append({
                "type": "error",
                "category": "anchor",
                "code": "MISSING_PRIMARY_ANCHOR",
                "message": f"Primary anchor text '{preflight_matrix['anchor_plan']['primary']}' not found"
            })
        
        # Check word count
        target_word_count = preflight_matrix.get("word_count", 800)
        word_diff = abs(article_data["word_count"] - target_word_count)
        if word_diff > target_word_count * 0.2:  # 20% tolerance
            score -= 10
            issues.append({
                "type": "warning",
                "category": "content",
                "code": "WORD_COUNT_MISMATCH",
                "message": f"Word count {article_data['word_count']} differs from target {target_word_count}"
            })
        
        return score, issues
    
    def _validate_draft_quality(
        self,
        article_data: Dict[str, Any]
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """Validate overall draft quality."""
        score = 100
        issues = []
        
        # Check structure
        if len(article_data["sections"]) < 3:
            score -= 20
            issues.append({
                "type": "warning",
                "category": "structure",
                "code": "INSUFFICIENT_SECTIONS",
                "message": "Article should have at least 3 sections"
            })
        
        # Check for empty sections
        for section in article_data["sections"]:
            if not section["paragraphs"]:
                score -= 10
                issues.append({
                    "type": "warning",
                    "category": "structure",
                    "code": "EMPTY_SECTION",
                    "message": f"Section '{section['title']}' has no content",
                    "location": {"section": section["title"]}
                })
        
        return score, issues
    
    def _validate_anchor_placement(
        self,
        article_data: Dict[str, Any],
        preflight_matrix: Optional[Dict[str, Any]]
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """Validate anchor placement rules."""
        score = 100
        issues = []
        
        if not preflight_matrix:
            return 70, []  # Default score without matrix
        
        target_anchor = preflight_matrix["anchor_plan"]["primary"]
        target_section = preflight_matrix["anchor_plan"]["placement"]["section"]
        target_paragraph = preflight_matrix["anchor_plan"]["placement"]["paragraph"]
        
        # Find anchor in article
        anchor_found = False
        anchor_location = None
        
        for s_idx, section in enumerate(article_data["sections"]):
            # Check if anchor is in header (not allowed)
            if target_anchor in section["title"]:
                score = 0  # Critical failure
                issues.append({
                    "type": "error",
                    "category": "anchor",
                    "code": "ANCHOR_IN_HEADER",
                    "message": "Anchor text found in header - this is not allowed",
                    "location": {"section": section["title"]}
                })
                return score, issues
            
            for p_idx, paragraph in enumerate(section["paragraphs"]):
                if paragraph["has_link"]:
                    for link in article_data["links"]:
                        if link["text"] == target_anchor:
                            anchor_found = True
                            anchor_location = {
                                "section_idx": s_idx,
                                "section": section["title"],
                                "paragraph": p_idx + 1
                            }
                            break
        
        if not anchor_found:
            score = 0
            issues.append({
                "type": "error",
                "category": "anchor",
                "code": "ANCHOR_NOT_FOUND",
                "message": f"Target anchor '{target_anchor}' not found in article"
            })
        else:
            # Check placement
            if target_section == "mittpunkt":
                # Should be in middle section
                middle_idx = len(article_data["sections"]) // 2
                if abs(anchor_location["section_idx"] - middle_idx) > 1:
                    score -= 20
                    issues.append({
                        "type": "warning",
                        "category": "anchor",
                        "code": "ANCHOR_PLACEMENT_WRONG",
                        "message": f"Anchor should be in middle section, found in {anchor_location['section']}",
                        "location": anchor_location
                    })
            
            # Check paragraph placement
            if anchor_location["paragraph"] > 5:
                score -= 15
                issues.append({
                    "type": "warning",
                    "category": "anchor",
                    "code": "ANCHOR_TOO_DEEP",
                    "message": f"Anchor in paragraph {anchor_location['paragraph']}, should be in 1-3",
                    "location": anchor_location
                })
        
        return score, issues
    
    def _validate_trust_signals(
        self,
        article_data: Dict[str, Any],
        preflight_matrix: Optional[Dict[str, Any]]
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """Validate trust signal requirements."""
        score = 100
        issues = []
        
        if not preflight_matrix or "trust" not in preflight_matrix:
            return 70, []
        
        required_trust = preflight_matrix["trust"]
        
        # Look for trust signals in text
        found_trust = 0
        article_lower = article_data["full_text"].lower()
        
        for trust_source in required_trust:
            domain = trust_source["domain"]
            
            if domain == "PLATSFÖRSLAG":
                # Check for any credible source pattern
                credible_patterns = [
                    r'enligt\s+\w+\.(se|com|org)',
                    r'rapporterar\s+\w+',
                    r'studier\s+från',
                    r'forskning\s+visar'
                ]
                
                if any(re.search(pattern, article_lower) for pattern in credible_patterns):
                    found_trust += 1
            
            elif domain.lower() in article_lower:
                found_trust += 1
        
        if found_trust < 1:
            score = 0
            issues.append({
                "type": "error",
                "category": "trust",
                "code": "MISSING_TRUST_SIGNALS",
                "message": "No trust signals found - at least 1 required"
            })
        elif found_trust < len(required_trust):
            score -= 20 * (len(required_trust) - found_trust)
            issues.append({
                "type": "warning",
                "category": "trust",
                "code": "INSUFFICIENT_TRUST_SIGNALS",
                "message": f"Only {found_trust} of {len(required_trust)} trust signals found"
            })
        
        return score, issues
    
    def _validate_lsi_terms(
        self,
        article_data: Dict[str, Any],
        preflight_matrix: Optional[Dict[str, Any]]
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """Validate LSI term requirements."""
        score = 100
        issues = []
        
        if not preflight_matrix or "lsi_near_window" not in preflight_matrix:
            return 70, []
        
        lsi_config = preflight_matrix["lsi_near_window"]
        required_terms = lsi_config["terms"]
        min_count = lsi_config["policy"]["min"]
        max_count = lsi_config["policy"]["max"]
        radius = lsi_config["policy"]["radius_sentences"]
        
        # Find anchor location
        anchor_text = preflight_matrix["anchor_plan"]["primary"]
        anchor_sentence_idx = None
        
        # Flatten all sentences with indices
        all_sentences = []
        for section in article_data["sections"]:
            for paragraph in section["paragraphs"]:
                for sentence in paragraph["sentences"]:
                    all_sentences.append(sentence.lower())
                    if anchor_text.lower() in sentence.lower():
                        anchor_sentence_idx = len(all_sentences) - 1
        
        if anchor_sentence_idx is None:
            return 0, [{
                "type": "error",
                "category": "lsi",
                "code": "ANCHOR_NOT_FOUND_FOR_LSI",
                "message": "Cannot validate LSI terms - anchor not found"
            }]
        
        # Count LSI terms in window
        window_start = max(0, anchor_sentence_idx - radius)
        window_end = min(len(all_sentences), anchor_sentence_idx + radius + 1)
        window_text = " ".join(all_sentences[window_start:window_end])
        
        found_terms = []
        for term in required_terms:
            if term.lower() in window_text:
                found_terms.append(term)
        
        # Check counts
        if len(found_terms) < min_count:
            score = 0
            issues.append({
                "type": "error",
                "category": "lsi",
                "code": "INSUFFICIENT_LSI_TERMS",
                "message": f"Only {len(found_terms)} LSI terms near anchor, minimum {min_count} required"
            })
        elif len(found_terms) > max_count:
            score -= 10
            issues.append({
                "type": "warning",
                "category": "lsi",
                "code": "EXCESSIVE_LSI_TERMS",
                "message": f"{len(found_terms)} LSI terms near anchor, maximum {max_count} recommended"
            })
        
        return score, issues
    
    def _validate_voice_fit(
        self,
        article_data: Dict[str, Any],
        preflight_matrix: Optional[Dict[str, Any]]
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """Validate voice and tone fit."""
        score = 90  # Default good score
        issues = []
        
        # Simple tone analysis
        text_lower = article_data["full_text"].lower()
        
        # Check for overly promotional language
        promo_phrases = ["bästa", "fantastisk", "otrolig", "missa inte", "unikt erbjudande"]
        promo_count = sum(1 for phrase in promo_phrases if phrase in text_lower)
        
        if promo_count > 3:
            score -= 20
            issues.append({
                "type": "warning",
                "category": "content",
                "code": "OVERLY_PROMOTIONAL",
                "message": "Content appears overly promotional"
            })
        
        return score, issues
    
    def _validate_compliance(
        self,
        article_data: Dict[str, Any],
        preflight_matrix: Optional[Dict[str, Any]]
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """Validate compliance requirements."""
        score = 100
        issues = []
        
        if not preflight_matrix or not preflight_matrix.get("guards", {}).get("compliance"):
            return score, issues
        
        compliance_types = preflight_matrix["guards"]["compliance"]
        text_lower = article_data["full_text"].lower()
        
        for comp_type in compliance_types:
            disclaimer_found = False
            
            if comp_type == "gambling":
                gambling_disclaimers = [
                    "spela ansvarsfullt",
                    "18+",
                    "spelpaus.se",
                    "stodlinjen"
                ]
                disclaimer_found = any(disc in text_lower for disc in gambling_disclaimers)
            
            elif comp_type == "finance":
                finance_disclaimers = [
                    "inte finansiell rådgivning",
                    "konsultera",
                    "professionell rådgivare"
                ]
                disclaimer_found = any(disc in text_lower for disc in finance_disclaimers)
            
            elif comp_type == "health":
                health_disclaimers = [
                    "inte medicinsk rådgivning",
                    "konsultera läkare",
                    "professionell medicinsk"
                ]
                disclaimer_found = any(disc in text_lower for disc in health_disclaimers)
            
            if not disclaimer_found:
                score = 0  # Critical failure
                issues.append({
                    "type": "error",
                    "category": "compliance",
                    "code": f"MISSING_{comp_type.upper()}_DISCLAIMER",
                    "message": f"Required {comp_type} disclaimer not found"
                })
        
        return score, issues
    
    async def _attempt_auto_fix(
        self,
        article_text: str,
        article_data: Dict[str, Any],
        issues: List[Dict[str, Any]],
        preflight_matrix: Optional[Dict[str, Any]]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Attempt to auto-fix issues."""
        fixed_text = article_text
        fixes = []
        
        # Only attempt fixes for specific issues
        for issue in issues:
            if issue["code"] == "MISSING_GAMBLING_DISCLAIMER" and preflight_matrix:
                # Add gambling disclaimer
                disclaimer = "\n\n*Spela ansvarsfullt. Läs mer om spelansvar på spelpaus.se. 18+ årsgräns.*"
                fixed_text += disclaimer
                fixes.append({
                    "type": "add_disclaimer",
                    "description": "Added gambling responsibility disclaimer",
                    "applied": True
                })
                break  # AUTO_FIX_ONCE
            
            elif issue["code"] == "INSUFFICIENT_LSI_TERMS" and preflight_matrix:
                # Try to inject LSI terms near anchor
                # (Complex implementation would go here)
                fixes.append({
                    "type": "inject_lsi",
                    "description": "Would inject LSI terms near anchor",
                    "applied": False  # Not implemented in this version
                })
        
        return fixed_text, fixes
    
    def _generate_recommendations(
        self,
        scores: Dict[str, float],
        issues: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Prioritize by lowest scores
        sorted_categories = sorted(scores.items(), key=lambda x: x[1])
        
        for category, score in sorted_categories[:3]:  # Top 3 problem areas
            if score < 70:
                if category == "anchor":
                    recommendations.append("Kontrollera att länken är korrekt placerad enligt preflight-instruktioner")
                elif category == "trust":
                    recommendations.append("Lägg till minst en referens till en trovärdig källa")
                elif category == "lsi":
                    recommendations.append("Inkludera fler LSI-termer inom 2 meningar från länken")
                elif category == "compliance":
                    recommendations.append("Lägg till nödvändiga bransch-disclaimers")
        
        return recommendations
    
    def _requires_human_signoff(
        self,
        issues: List[Dict[str, Any]],
        scores: Dict[str, float]
    ) -> bool:
        """Determine if human signoff is required."""
        # Critical issues requiring human review
        critical_codes = [
            "ANCHOR_IN_HEADER",
            "ERR_TRUST_COMPETITOR",
            "ERR_COMPLIANCE"
        ]
        
        for issue in issues:
            if issue["code"] in critical_codes:
                return True
        
        # Very low scores
        if any(score < 50 for score in scores.values()):
            return True
        
        return False
    
    def _determine_next_actions(
        self,
        status: str,
        issues: List[Dict[str, Any]],
        scores: Dict[str, float]
    ) -> List[str]:
        """Determine next actions based on validation results."""
        actions = []
        
        if status == "APPROVED":
            actions.append("Proceed to delivery")
        elif status == "LIGHT_EDITS":
            actions.append("Apply recommended edits")
            actions.append("Re-run QC validation")
        else:  # BLOCKED
            actions.append("Address critical issues")
            
            # Specific actions based on issues
            issue_codes = {issue["code"] for issue in issues}
            
            if "ANCHOR_NOT_FOUND" in issue_codes:
                actions.append("Add target anchor link to article")
            if "MISSING_TRUST_SIGNALS" in issue_codes:
                actions.append("Add references to credible sources")
            if "INSUFFICIENT_LSI_TERMS" in issue_codes:
                actions.append("Add LSI terms near anchor link")
            
            actions.append("Request human review if needed")
        
        return actions
