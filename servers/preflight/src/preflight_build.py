"""
Preflight Builder
Builds preflight matrix and writer prompts for backlink content
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from urllib.parse import urlparse
from pathlib import Path
import random

import psycopg2
from psycopg2.extras import RealDictCursor
from jinja2 import Environment, FileSystemLoader
from jsonschema import validate, ValidationError

logger = logging.getLogger('preflight.builder')


class PreflightBuilder:
    """Builds preflight matrices for content planning."""
    
    def __init__(self):
        self.db_conn = None
        
        # Initialize Jinja2 environment
        template_dir = Path(__file__).parent.parent / 'templates'
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=False
        )
        
        # Load preflight matrix schema
        schema_path = Path(__file__).parent.parent / 'schemas' / 'preflight_matrix.schema.json'
        with open(schema_path, 'r') as f:
            self.matrix_schema = json.load(f)
    
    async def connect(self, db_url: str):
        """Connect to database."""
        try:
            self.db_conn = psycopg2.connect(db_url)
            logger.info("Connected to database for preflight operations")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
    
    async def build(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Build preflight matrix and writer prompt from order."""
        try:
            # Extract order data
            order_ref = order["order_ref"]
            customer_id = order["customer_id"]
            publication_domain = order["publication_domain"]
            target_url = order["target_url"]
            anchor_text = order["anchor_text"]
            topic = order["topic"]
            constraints = order.get("constraints", {})
            
            # Extract constraints
            word_count = constraints.get("word_count", 800)
            tone = constraints.get("tone", "informativ")
            compliance = constraints.get("compliance", [])
            
            # Analyze domains and entities
            query_or_cluster = self._extract_query_cluster(topic)
            intents = self._detect_intents(topic, target_url)
            target_entities = self._extract_entities(target_url, anchor_text)
            publication_entities = self._extract_entities(publication_domain, topic)
            
            # Find midpoint candidates
            candidate_midpoints = self._find_midpoint_candidates(
                publication_entities, 
                target_entities,
                topic
            )
            
            # Choose best midpoint
            chosen_midpoint = self._choose_midpoint(candidate_midpoints)
            
            # Plan anchor strategy
            anchor_plan = await self._plan_anchor_strategy(
                anchor_text,
                target_url,
                chosen_midpoint
            )
            
            # Generate LSI terms
            lsi_terms = self._generate_lsi_terms(
                topic,
                publication_domain,
                target_url
            )
            
            # Select trust sources
            trust_sources = await self._select_trust_sources(
                topic,
                publication_domain
            )
            
            # Build preflight matrix
            preflight_matrix = {
                "order_ref": order_ref,
                "publication_domain": publication_domain,
                "customer_id": customer_id,
                "query_or_cluster": query_or_cluster,
                "intents": intents,
                "target_entities": target_entities,
                "publication_entities": publication_entities,
                "candidate_midpoints": candidate_midpoints,
                "chosen_midpoint": chosen_midpoint,
                "target_url": target_url,
                "anchor_plan": anchor_plan,
                "lsi_near_window": {
                    "policy": {
                        "min": 6,
                        "max": 10,
                        "radius_sentences": 2,
                        "max_repeat": 2
                    },
                    "terms": lsi_terms
                },
                "trust": trust_sources,
                "guards": {
                    "no_anchor_in_headers": True,
                    "competitor_block": True,
                    "compliance": compliance
                }
            }
            
            # Validate matrix against schema
            validation_errors = self._validate_matrix(preflight_matrix)
            
            # Generate writer prompt
            writer_prompt = self._generate_writer_prompt(
                preflight_matrix,
                word_count,
                tone,
                compliance
            )
            
            # Log event if database connected
            if self.db_conn:
                await self._log_preflight_event(order_ref, "preflight_complete", preflight_matrix)
            
            return {
                "preflight_matrix": preflight_matrix,
                "writer_prompt": writer_prompt,
                "validation": {
                    "is_valid": len(validation_errors) == 0,
                    "errors": validation_errors,
                    "warnings": []
                }
            }
        
        except Exception as e:
            logger.error(f"Error building preflight: {e}")
            raise
    
    def _extract_query_cluster(self, topic: str) -> str:
        """Extract search query or cluster from topic."""
        # Simple extraction - take first meaningful phrase
        words = topic.lower().split()
        
        # Remove common words
        stopwords = {"så", "du", "din", "att", "för", "med", "om", "i", "på", "av"}
        filtered = [w for w in words if w not in stopwords and len(w) > 2]
        
        # Take 2-4 words as query
        if len(filtered) >= 2:
            return " ".join(filtered[:min(4, len(filtered))])
        
        return " ".join(words[:3])
    
    def _detect_intents(self, topic: str, target_url: str) -> List[str]:
        """Detect search intents from topic and target."""
        intents = []
        topic_lower = topic.lower()
        
        # Check for informational intent
        if any(word in topic_lower for word in ["guide", "tips", "hur", "vad", "varför", "undviker"]):
            intents.append("informational")
        
        # Check for commercial intent based on target
        if "casino" in target_url.lower() or "betting" in target_url.lower():
            intents.append("commercial")
        
        # Default to informational if no specific intent
        if not intents:
            intents.append("informational")
        
        return intents
    
    def _extract_entities(self, domain: str, context: str) -> List[str]:
        """Extract relevant entities from domain and context."""
        entities = []
        
        # Extract from domain name
        domain_parts = domain.replace(".", " ").replace("-", " ").split()
        entities.extend([p for p in domain_parts if len(p) > 3])
        
        # Extract from context
        context_lower = context.lower()
        
        # Domain-specific entities
        if "genealogi" in domain or "släkt" in context_lower:
            entities.extend(["släktforskning", "genealogi", "arkiv", "anor"])
        elif "casino" in domain or "casino" in context_lower:
            entities.extend(["casino", "spel", "underhållning"])
        
        # Remove duplicates and return top 5
        return list(set(entities))[:5]
    
    def _find_midpoint_candidates(
        self,
        publication_entities: List[str],
        target_entities: List[str],
        topic: str
    ) -> List[Dict[str, Any]]:
        """Find semantic midpoint candidates between domains."""
        candidates = []
        
        # Predefined midpoint concepts
        midpoint_concepts = {
            "pausunderhållning": {
                "bridges": ["forskning", "casino"],
                "score": 0.85,
                "rationale": "Naturlig brygga mellan intensivt arbete och avkoppling"
            },
            "koncentrationsövning": {
                "bridges": ["studie", "spel"],
                "score": 0.75,
                "rationale": "Gemensam nämnare i fokus och strategi"
            },
            "digitala verktyg": {
                "bridges": ["online", "internet"],
                "score": 0.70,
                "rationale": "Modern teknik som förenar olika aktiviteter"
            },
            "tidshantering": {
                "bridges": ["planering", "fritid"],
                "score": 0.65,
                "rationale": "Balans mellan arbete och vila"
            }
        }
        
        # Score each concept
        for concept, details in midpoint_concepts.items():
            # Check relevance to both domains
            pub_match = any(entity in " ".join(publication_entities).lower() 
                          for entity in details["bridges"])
            target_match = any(entity in " ".join(target_entities).lower() 
                             for entity in details["bridges"])
            
            if pub_match or target_match:
                score = details["score"]
                if pub_match and target_match:
                    score = min(1.0, score * 1.2)
                
                candidates.append({
                    "label": concept,
                    "score": round(score, 2),
                    "rationale": details["rationale"]
                })
        
        # Sort by score
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Ensure at least one candidate
        if not candidates:
            candidates.append({
                "label": "avkoppling",
                "score": 0.5,
                "rationale": "Generell brygga mellan olika aktiviteter"
            })
        
        return candidates[:3]
    
    def _choose_midpoint(self, candidates: List[Dict[str, Any]]) -> Dict[str, str]:
        """Choose the best midpoint from candidates."""
        if not candidates:
            return {
                "label": "avkoppling",
                "rationale": "Standardval för att koppla samman olika aktiviteter"
            }
        
        # Choose highest scoring
        best = candidates[0]
        return {
            "label": best["label"],
            "rationale": best["rationale"]
        }
    
    async def _plan_anchor_strategy(
        self,
        anchor_text: str,
        target_url: str,
        midpoint: Dict[str, str]
    ) -> Dict[str, Any]:
        """Plan anchor text strategy."""
        # Determine anchor type
        domain = urlparse(target_url).netloc
        brand_terms = domain.replace(".", " ").replace("-", " ").split()
        
        anchor_lower = anchor_text.lower()
        if anchor_lower in [bt.lower() for bt in brand_terms]:
            anchor_type = "brand"
        elif any(bt.lower() in anchor_lower for bt in brand_terms):
            anchor_type = "partial"
        elif len(anchor_lower.split()) == 1 and anchor_lower in ["casino", "spel", "betting"]:
            anchor_type = "exact"
        else:
            anchor_type = "generic"
        
        # Create backup anchor
        if anchor_type == "exact":
            backup = f"{anchor_text} online"
        elif anchor_type == "brand":
            backup = f"besök {anchor_text}"
        else:
            backup = anchor_text.replace(" ", " och ")
        
        return {
            "type": anchor_type,
            "primary": anchor_text,
            "backup": backup,
            "placement": {
                "section": "mittpunkt",
                "paragraph": random.randint(1, 3),
                "seeded": True
            }
        }
    
    def _generate_lsi_terms(
        self,
        topic: str,
        publication_domain: str,
        target_url: str
    ) -> List[str]:
        """Generate LSI terms for semantic relevance."""
        lsi_terms = []
        
        # Topic-based terms
        if "släktforskning" in topic.lower() or "genealogi" in publication_domain:
            lsi_terms.extend([
                "forskning", "källor", "arkiv", "dokument",
                "historia", "familj", "anor", "kyrkoböcker"
            ])
        
        # Target-based terms
        if "casino" in target_url.lower():
            lsi_terms.extend([
                "underhållning", "spel", "avkoppling", "fritid",
                "pausaktivitet", "digital", "online", "nöje"
            ])
        
        # Generic research/analysis terms
        lsi_terms.extend([
            "metod", "analys", "tips", "guide", "strategi",
            "verktyg", "process", "resultat"
        ])
        
        # Remove duplicates and select 6-10
        unique_terms = list(set(lsi_terms))
        random.shuffle(unique_terms)
        
        return unique_terms[:random.randint(6, 10)]
    
    async def _select_trust_sources(
        self,
        topic: str,
        publication_domain: str
    ) -> List[Dict[str, Any]]:
        """Select appropriate trust sources."""
        trust_sources = []
        
        # Try to get from database if connected
        if self.db_conn:
            try:
                with self.db_conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get T1/T2 sources
                    cur.execute(
                        """
                        SELECT domain, trust_level, pattern
                        FROM trust_registry
                        WHERE trust_level IN ('T1', 'T2')
                        AND competitor = false
                        LIMIT 5
                        """
                    )
                    results = cur.fetchall()
                    
                    for row in results[:2]:  # Take top 2
                        trust_sources.append({
                            "domain": row["domain"],
                            "level": row["trust_level"],
                            "rationale": self._get_trust_rationale(row["domain"], row["pattern"])
                        })
            except Exception as e:
                logger.error(f"Error fetching trust sources: {e}")
        
        # Add default sources if needed
        if len(trust_sources) < 1:
            if "släkt" in topic.lower() or "genealogi" in publication_domain:
                trust_sources.append({
                    "domain": "riksarkivet.se",
                    "level": "T1",
                    "rationale": "Officiell svensk myndighet för arkivfrågor"
                })
            else:
                trust_sources.append({
                    "domain": "PLATSFÖRSLAG",
                    "level": "T2",
                    "rationale": "Välj en relevant branschkälla eller nyhetssajt"
                })
        
        return trust_sources
    
    def _get_trust_rationale(self, domain: str, pattern: str) -> str:
        """Generate rationale for trust source."""
        rationales = {
            "government": "Officiell myndighet med hög trovärdighet",
            "news": "Etablerad nyhetskälla med redaktionell granskning",
            "encyclopedia": "Omfattande kunskapskälla med många bidragsgivare",
            "academic": "Akademisk källa med vetenskaplig grund"
        }
        
        return rationales.get(pattern, "Erkänd källa inom området")
    
    def _validate_matrix(self, matrix: Dict[str, Any]) -> List[str]:
        """Validate preflight matrix against schema."""
        errors = []
        
        try:
            validate(instance=matrix, schema=self.matrix_schema)
        except ValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
        
        # Additional business logic validation
        if len(matrix["lsi_near_window"]["terms"]) < 6:
            errors.append("Insufficient LSI terms (minimum 6 required)")
        
        if len(matrix["trust"]) < 1:
            errors.append("At least one trust source required")
        
        if matrix["anchor_plan"]["placement"]["paragraph"] > 5:
            errors.append("Anchor placement too far down (max paragraph 5)")
        
        return errors
    
    def _generate_writer_prompt(
        self,
        matrix: Dict[str, Any],
        word_count: int,
        tone: str,
        compliance: List[str]
    ) -> str:
        """Generate writer prompt from preflight matrix."""
        template = self.jinja_env.get_template('writer_prompt.md.j2')
        
        # Render template with matrix data
        prompt = template.render(
            **matrix,
            word_count=word_count,
            tone=tone,
            compliance=compliance
        )
        
        return prompt
    
    async def _log_preflight_event(
        self,
        order_ref: str,
        event_type: str,
        payload: Dict[str, Any]
    ):
        """Log preflight event to database."""
        if not self.db_conn:
            return
        
        try:
            with self.db_conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO audit_log (order_ref, step, status, payload, ts)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        order_ref,
                        event_type,
                        'success',
                        json.dumps(payload, ensure_ascii=False),
                        datetime.now(timezone.utc)
                    )
                )
                self.db_conn.commit()
        except Exception as e:
            logger.error(f"Error logging event: {e}")
            self.db_conn.rollback()
