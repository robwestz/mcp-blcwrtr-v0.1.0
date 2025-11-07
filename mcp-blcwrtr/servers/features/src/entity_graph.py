"""
Entity Graph Builder
Builds semantic entity graphs from seed terms
"""

import logging
from typing import List, Dict, Any, Set, Tuple
from datetime import datetime, timezone
import random
import networkx as nx

logger = logging.getLogger('features.entity_graph')


class EntityGraphBuilder:
    """Builds entity graphs for semantic expansion."""
    
    def __init__(self):
        self.swedish_expansions = {
            # Genealogy/Research domain
            "släktforskning": ["genealogi", "anor", "släktträd", "arkiv", "kyrkoböcker"],
            "forskning": ["studie", "undersökning", "analys", "vetenskap", "metod"],
            "arkiv": ["dokument", "register", "databas", "samling", "källa"],
            "historia": ["historik", "förflutna", "tradition", "arv", "minne"],
            
            # Casino/Gaming domain
            "casino": ["spel", "gambling", "hasardspel", "spelande", "betting"],
            "spel": ["game", "underhållning", "nöje", "aktivitet", "tidsfördriv"],
            "underhållning": ["nöje", "avkoppling", "rekreation", "fritid", "hobby"],
            
            # Bridge concepts
            "paus": ["rast", "avbrott", "vila", "återhämtning", "mellanrum"],
            "koncentration": ["fokus", "uppmärksamhet", "noggrannhet", "precision"],
            "strategi": ["taktik", "metod", "planering", "tillvägagångssätt"],
            "digital": ["online", "internet", "webb", "virtuell", "elektronisk"],
            
            # Common expansion patterns
            "guide": ["handledning", "manual", "instruktion", "vägledning"],
            "tips": ["råd", "rekommendation", "förslag", "knep"],
            "misstag": ["fel", "miss", "felsteg", "brist", "problem"],
            "verktyg": ["redskap", "hjälpmedel", "resurs", "instrument"]
        }
        
        self.english_expansions = {
            "genealogy": ["family history", "ancestry", "lineage", "heritage"],
            "research": ["study", "investigation", "analysis", "examination"],
            "casino": ["gaming", "gambling", "betting", "wagering"],
            "entertainment": ["amusement", "recreation", "leisure", "fun"],
            "strategy": ["tactics", "approach", "method", "plan"]
        }
    
    async def build_graph(
        self, 
        seed_terms: List[str],
        depth: int = 2,
        max_nodes: int = 50,
        language: str = "sv"
    ) -> Dict[str, Any]:
        """Build an entity graph from seed terms."""
        
        # Initialize graph
        G = nx.Graph()
        nodes = []
        edges = []
        visited = set()
        
        # Add seed nodes
        for term in seed_terms:
            node_id = self._normalize_id(term)
            nodes.append({
                "id": node_id,
                "label": term,
                "type": "seed",
                "weight": 1.0,
                "attributes": {
                    "category": "seed",
                    "relevance": 1.0
                }
            })
            G.add_node(node_id, label=term, type="seed")
            visited.add(node_id)
        
        # Expand graph
        current_level = set(self._normalize_id(term) for term in seed_terms)
        
        for level in range(1, depth + 1):
            if len(nodes) >= max_nodes:
                break
            
            next_level = set()
            level_type = "primary" if level == 1 else "secondary"
            
            for node_id in current_level:
                if len(nodes) >= max_nodes:
                    break
                
                # Get expansions
                label = next(n["label"] for n in nodes if n["id"] == node_id)
                expansions = self._get_expansions(label, language)
                
                for expansion in expansions[:3]:  # Limit expansions per node
                    if len(nodes) >= max_nodes:
                        break
                    
                    exp_id = self._normalize_id(expansion)
                    if exp_id not in visited:
                        # Add node
                        weight = 0.8 / level  # Decrease weight with distance
                        nodes.append({
                            "id": exp_id,
                            "label": expansion,
                            "type": level_type,
                            "weight": round(weight, 2),
                            "attributes": {
                                "category": self._categorize_term(expansion, language),
                                "relevance": round(weight * 0.9, 2)
                            }
                        })
                        G.add_node(exp_id, label=expansion, type=level_type)
                        visited.add(exp_id)
                        next_level.add(exp_id)
                    
                    # Add edge
                    edge_weight = 0.9 / level
                    edges.append({
                        "source": node_id,
                        "target": exp_id,
                        "weight": round(edge_weight, 2),
                        "type": self._classify_edge(label, expansion, language)
                    })
                    G.add_edge(node_id, exp_id, weight=edge_weight)
            
            current_level = next_level
        
        # Add some cross-connections for related nodes
        self._add_cross_connections(G, nodes, edges, max_connections=5)
        
        # Calculate graph metrics
        metadata = {
            "seed_terms": seed_terms,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "density": round(nx.density(G), 3) if len(nodes) > 1 else 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": metadata
        }
    
    def _normalize_id(self, term: str) -> str:
        """Normalize term to create consistent IDs."""
        return term.lower().replace(" ", "_").replace("-", "_")
    
    def _get_expansions(self, term: str, language: str) -> List[str]:
        """Get semantic expansions for a term."""
        term_lower = term.lower()
        
        if language == "sv":
            expansions = self.swedish_expansions.get(term_lower, [])
            if not expansions:
                # Try to find partial matches
                for key, values in self.swedish_expansions.items():
                    if key in term_lower or term_lower in key:
                        expansions.extend(values[:2])
        else:
            expansions = self.english_expansions.get(term_lower, [])
        
        # Add some generic expansions if none found
        if not expansions:
            if language == "sv":
                expansions = [f"{term} online", f"{term} guide", f"{term} tips"]
            else:
                expansions = [f"{term} online", f"{term} guide", f"{term} tips"]
        
        # Randomize order for variety
        random.shuffle(expansions)
        return expansions
    
    def _categorize_term(self, term: str, language: str) -> str:
        """Categorize a term into semantic categories."""
        term_lower = term.lower()
        
        if language == "sv":
            if any(word in term_lower for word in ["släkt", "genealogi", "anor", "arkiv"]):
                return "genealogy"
            elif any(word in term_lower for word in ["casino", "spel", "gambling", "betting"]):
                return "gaming"
            elif any(word in term_lower for word in ["forskning", "studie", "analys", "metod"]):
                return "research"
            elif any(word in term_lower for word in ["digital", "online", "internet", "webb"]):
                return "digital"
            elif any(word in term_lower for word in ["paus", "vila", "avkoppling", "fritid"]):
                return "leisure"
        
        return "general"
    
    def _classify_edge(self, source: str, target: str, language: str) -> str:
        """Classify the relationship type between two terms."""
        source_lower = source.lower()
        target_lower = target.lower()
        
        # Check for hierarchical relationships
        if source_lower in target_lower or target_lower in source_lower:
            return "hierarchical"
        
        # Check for semantic similarity
        if self._categorize_term(source, language) == self._categorize_term(target, language):
            return "semantic"
        
        # Check for causal relationships
        if any(word in source_lower for word in ["metod", "method", "strategi", "strategy"]):
            return "causal"
        
        # Default to associative
        return "associative"
    
    def _add_cross_connections(
        self, 
        G: nx.Graph, 
        nodes: List[Dict], 
        edges: List[Dict],
        max_connections: int = 5
    ):
        """Add cross-connections between related nodes."""
        added = 0
        
        # Find nodes with same category
        categories = {}
        for node in nodes:
            cat = node["attributes"]["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(node["id"])
        
        # Connect nodes within same category
        for cat, node_ids in categories.items():
            if len(node_ids) < 2:
                continue
            
            for i in range(len(node_ids) - 1):
                if added >= max_connections:
                    break
                
                for j in range(i + 1, len(node_ids)):
                    if added >= max_connections:
                        break
                    
                    # Don't add if already connected
                    if not G.has_edge(node_ids[i], node_ids[j]):
                        weight = 0.5  # Lower weight for cross-connections
                        edges.append({
                            "source": node_ids[i],
                            "target": node_ids[j],
                            "weight": weight,
                            "type": "related"
                        })
                        G.add_edge(node_ids[i], node_ids[j], weight=weight)
                        added += 1
