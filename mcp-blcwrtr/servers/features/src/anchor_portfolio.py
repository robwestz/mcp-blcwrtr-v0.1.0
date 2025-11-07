"""
Anchor Portfolio Analyzer
Analyzes and optimizes anchor text portfolio distribution
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger('features.anchor_portfolio')


class AnchorPortfolioAnalyzer:
    """Analyzes anchor text portfolios for risk and optimization."""
    
    def __init__(self):
        self.db_conn = None
        self.optimal_ratios = {
            "exact": (0.05, 0.15),    # 5-15% exact match
            "partial": (0.20, 0.40),  # 20-40% partial match
            "brand": (0.25, 0.45),    # 25-45% brand
            "generic": (0.15, 0.30)   # 15-30% generic
        }
    
    async def connect(self, db_url: str):
        """Connect to database."""
        try:
            self.db_conn = psycopg2.connect(db_url)
            logger.info("Connected to database for portfolio analysis")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
    
    async def get_current_portfolio(self, target_domain: str) -> Dict[str, int]:
        """Get current anchor portfolio from database or return default."""
        if self.db_conn:
            try:
                with self.db_conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT exact, partial, brand, generic
                        FROM anchor_portfolio
                        WHERE target_domain = %s
                        """,
                        (target_domain,)
                    )
                    result = cur.fetchone()
                    
                    if result:
                        return {
                            "exact": result["exact"],
                            "partial": result["partial"],
                            "brand": result["brand"],
                            "generic": result["generic"]
                        }
            except Exception as e:
                logger.error(f"Error fetching portfolio: {e}")
        
        # Return mock data for demo
        return {
            "exact": 12,
            "partial": 8,
            "brand": 15,
            "generic": 5
        }
    
    async def analyze_portfolio(
        self,
        target_domain: str,
        old_portfolio: Dict[str, int],
        new_portfolio: Dict[str, int],
        save_to_db: bool = False
    ) -> Dict[str, Any]:
        """Analyze portfolio changes and provide recommendations."""
        
        # Calculate totals
        old_total = sum(old_portfolio.values())
        new_total = sum(new_portfolio.values())
        
        # Calculate old risk
        old_risk, old_risk_level = self._calculate_risk(old_portfolio)
        
        # Calculate new risk
        new_risk, new_risk_level = self._calculate_risk(new_portfolio)
        
        # Calculate delta
        risk_change = new_risk - old_risk
        if abs(risk_change) < 0.01:
            risk_direction = "unchanged"
        elif risk_change < 0:
            risk_direction = "improved"
        else:
            risk_direction = "worsened"
        
        # Calculate mix changes
        mix_changes = {}
        for anchor_type in ["exact", "partial", "brand", "generic"]:
            old_count = old_portfolio.get(anchor_type, 0)
            new_count = new_portfolio.get(anchor_type, 0)
            if old_count != new_count:
                mix_changes[anchor_type] = {
                    "from": old_count,
                    "to": new_count,
                    "change": new_count - old_count
                }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(new_portfolio, new_risk_level)
        
        # Save to database if requested
        if save_to_db and self.db_conn:
            await self._save_portfolio(target_domain, new_portfolio, new_risk)
        
        return {
            "target_domain": target_domain,
            "old_mix": old_portfolio,
            "new_mix": new_portfolio,
            "old_risk": round(old_risk, 3),
            "new_risk": round(new_risk, 3),
            "risk_level": new_risk_level,
            "delta": {
                "risk_change": round(risk_change, 3),
                "risk_direction": risk_direction,
                "mix_changes": mix_changes
            },
            "recommendations": recommendations
        }
    
    def _calculate_risk(self, portfolio: Dict[str, int]) -> Tuple[float, str]:
        """Calculate portfolio risk score and level."""
        total = sum(portfolio.values())
        if total == 0:
            return 0.0, "low"
        
        # Calculate ratios
        ratios = {
            anchor_type: count / total
            for anchor_type, count in portfolio.items()
        }
        
        # Risk factors
        risk_score = 0.0
        
        # Exact match risk (highest weight)
        exact_ratio = ratios.get("exact", 0)
        if exact_ratio > self.optimal_ratios["exact"][1]:
            risk_score += (exact_ratio - self.optimal_ratios["exact"][1]) * 3.0
        
        # Diversity risk
        diversity_score = self._calculate_diversity(ratios)
        risk_score += (1 - diversity_score) * 1.5
        
        # Brand/Generic balance risk
        brand_ratio = ratios.get("brand", 0)
        generic_ratio = ratios.get("generic", 0)
        if brand_ratio < self.optimal_ratios["brand"][0] or generic_ratio < self.optimal_ratios["generic"][0]:
            risk_score += 0.3
        
        # Normalize risk score (0-1)
        risk_score = min(1.0, risk_score)
        
        # Determine risk level
        if risk_score <= 0.3:
            risk_level = "low"
        elif risk_score <= 0.6:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return risk_score, risk_level
    
    def _calculate_diversity(self, ratios: Dict[str, float]) -> float:
        """Calculate diversity score (0-1, higher is better)."""
        # Shannon entropy-inspired diversity measure
        diversity = 0.0
        
        for ratio in ratios.values():
            if ratio > 0:
                diversity -= ratio * (ratio ** 0.5)  # Modified entropy
        
        # Normalize to 0-1
        max_diversity = -4 * (0.25 * (0.25 ** 0.5))  # Perfect distribution
        diversity_score = 1 - (diversity / max_diversity)
        
        return max(0, min(1, diversity_score))
    
    def _generate_recommendations(
        self, 
        portfolio: Dict[str, int], 
        risk_level: str
    ) -> List[Dict[str, Any]]:
        """Generate portfolio optimization recommendations."""
        recommendations = []
        total = sum(portfolio.values())
        
        if total == 0:
            recommendations.append({
                "action": "increase",
                "anchor_type": "brand",
                "rationale": "Start building portfolio with brand anchors",
                "priority": "high"
            })
            return recommendations
        
        # Calculate current ratios
        ratios = {
            anchor_type: count / total
            for anchor_type, count in portfolio.items()
        }
        
        # Check exact match ratio
        exact_ratio = ratios.get("exact", 0)
        if exact_ratio > self.optimal_ratios["exact"][1]:
            recommendations.append({
                "action": "decrease",
                "anchor_type": "exact",
                "rationale": f"Exact match ratio ({exact_ratio:.1%}) exceeds safe threshold ({self.optimal_ratios['exact'][1]:.0%})",
                "priority": "high"
            })
        elif exact_ratio < self.optimal_ratios["exact"][0] and risk_level == "low":
            recommendations.append({
                "action": "increase",
                "anchor_type": "exact",
                "rationale": "Can safely add more exact matches for stronger relevance signals",
                "priority": "low"
            })
        
        # Check partial match ratio
        partial_ratio = ratios.get("partial", 0)
        if partial_ratio < self.optimal_ratios["partial"][0]:
            recommendations.append({
                "action": "increase",
                "anchor_type": "partial",
                "rationale": "Partial matches provide good balance of relevance and safety",
                "priority": "medium" if risk_level != "high" else "high"
            })
        
        # Check brand ratio
        brand_ratio = ratios.get("brand", 0)
        if brand_ratio < self.optimal_ratios["brand"][0]:
            recommendations.append({
                "action": "increase",
                "anchor_type": "brand",
                "rationale": "Brand anchors are safest and build brand awareness",
                "priority": "high" if risk_level == "high" else "medium"
            })
        
        # Check generic ratio
        generic_ratio = ratios.get("generic", 0)
        if generic_ratio < self.optimal_ratios["generic"][0]:
            recommendations.append({
                "action": "increase",
                "anchor_type": "generic",
                "rationale": "Generic anchors add natural diversity to portfolio",
                "priority": "medium"
            })
        
        # General diversity recommendation
        diversity = self._calculate_diversity(ratios)
        if diversity < 0.7 and len(recommendations) < 3:
            recommendations.append({
                "action": "diversify",
                "anchor_type": "generic",
                "rationale": "Improve anchor text diversity for more natural link profile",
                "priority": "medium"
            })
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order[x["priority"]])
        
        return recommendations[:4]  # Return top 4 recommendations
    
    async def _save_portfolio(
        self,
        target_domain: str,
        portfolio: Dict[str, int],
        risk: float
    ):
        """Save portfolio to database."""
        if not self.db_conn:
            return
        
        try:
            with self.db_conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO anchor_portfolio (
                        target_domain, exact, partial, brand, generic, risk, last_calculated
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (target_domain) 
                    DO UPDATE SET
                        exact = EXCLUDED.exact,
                        partial = EXCLUDED.partial,
                        brand = EXCLUDED.brand,
                        generic = EXCLUDED.generic,
                        risk = EXCLUDED.risk,
                        last_calculated = EXCLUDED.last_calculated
                    """,
                    (
                        target_domain,
                        portfolio.get("exact", 0),
                        portfolio.get("partial", 0),
                        portfolio.get("brand", 0),
                        portfolio.get("generic", 0),
                        risk,
                        datetime.now(timezone.utc)
                    )
                )
                self.db_conn.commit()
                logger.info(f"Saved portfolio for {target_domain}")
        except Exception as e:
            logger.error(f"Error saving portfolio: {e}")
            self.db_conn.rollback()
