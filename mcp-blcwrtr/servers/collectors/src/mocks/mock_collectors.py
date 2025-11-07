"""
Mock implementations for collectors
Used when USE_MOCK_COLLECTORS=true or when API keys are missing
"""

import random
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional


class MockCollectors:
    """Mock collector implementations for testing and development."""
    
    async def get_serp_snapshot(self, query: str, locale: str = "sv-SE") -> Dict[str, Any]:
        """Mock SERP snapshot data."""
        # Generate mock LSI terms based on query
        query_words = query.lower().split()
        base_lsi_terms = [
            "guide", "tips", "metod", "verktyg", "process", "analys",
            "exempel", "strategi", "teknik", "resultat", "forskning", "studie"
        ]
        
        # Mix query words with base terms
        lsi_terms = []
        for word in query_words:
            if len(word) > 3:  # Only use meaningful words
                lsi_terms.extend([
                    f"{word}guide",
                    f"{word}tips",
                    f"bästa {word}",
                    f"{word} online"
                ])
        
        # Add random base terms
        lsi_terms.extend(random.sample(base_lsi_terms, min(6, len(base_lsi_terms))))
        
        # Ensure we have at least 6-10 unique terms
        lsi_terms = list(set(lsi_terms))[:10]
        
        # Generate mock top URLs
        domains = [
            "wikipedia.org", "example.se", "guide.se", "tips.se", 
            "blogg.se", "forum.se", "nyheter.se", "akademi.se"
        ]
        
        top_urls = []
        for i in range(10):
            domain = random.choice(domains)
            top_urls.append({
                "url": f"https://{domain}/{'-'.join(query_words[:2])}-{i+1}",
                "title": f"{query} - {'Guide' if i < 3 else 'Tips'} #{i+1}",
                "position": i + 1,
                "domain": domain,
                "snippet": f"Läs vår kompletta guide om {query}. Experttips och råd för bästa resultat..."
            })
        
        # Mock SERP features
        features = {
            "featured_snippet": random.random() > 0.7,
            "knowledge_panel": random.random() > 0.8,
            "local_pack": "lokal" in query.lower() or "nära" in query.lower(),
            "shopping_results": any(word in query.lower() for word in ["köp", "pris", "billig"])
        }
        
        return {
            "lsi_terms": lsi_terms,
            "top_urls": top_urls,
            "features": features
        }
    
    async def check_cache(self, query: str, locale: str) -> Optional[Dict[str, Any]]:
        """Mock cache check - always returns None (no cache)."""
        return None
    
    async def get_news_signals(self, topic: str, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """Mock news signals."""
        sources = ["DN.se", "SVT.se", "Aftonbladet.se", "Expressen.se", "SvD.se"]
        
        news = []
        for i in range(random.randint(3, 8)):
            published_at = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))
            news.append({
                "title": f"{topic} - Senaste nyheterna och utvecklingen",
                "url": f"https://{random.choice(sources).lower()}/artikel/{topic.lower()}-{i+1}",
                "source": random.choice(sources),
                "published_at": published_at.isoformat(),
                "snippet": f"Läs mer om {topic} och de senaste händelserna. Experter kommenterar...",
                "relevance_score": round(random.uniform(0.7, 1.0), 2)
            })
        
        # Sort by relevance
        news.sort(key=lambda x: x["relevance_score"], reverse=True)
        return news
    
    async def get_video_signals(self, topic: str, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """Mock video signals."""
        channels = ["SVT Play", "TV4 Play", "UR Play", "Utbildning SE", "Expert TV"]
        
        videos = []
        for i in range(random.randint(2, 5)):
            published_at = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 60))
            videos.append({
                "title": f"{topic} - Förklarad på 5 minuter",
                "url": f"https://video.example.com/watch?v={topic.lower()}{i}",
                "channel": random.choice(channels),
                "duration": f"{random.randint(3, 15)}:{random.randint(10, 59):02d}",
                "views": random.randint(1000, 50000),
                "published_at": published_at.isoformat()
            })
        
        return videos
    
    async def get_podcast_signals(self, topic: str, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """Mock podcast signals."""
        shows = ["P3 Dokumentär", "Vetenskapsradion", "Framtidspodden", "Teknikpodden", "Samhällspodden"]
        
        podcasts = []
        for i in range(random.randint(1, 3)):
            published_at = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 90))
            podcasts.append({
                "title": f"Avsnitt {random.randint(50, 200)}: {topic}",
                "episode": f"S{random.randint(1, 5)}E{random.randint(1, 20)}",
                "url": f"https://podcast.example.com/{topic.lower()}-episode-{i+1}",
                "show": random.choice(shows),
                "duration": f"{random.randint(20, 60)}:00",
                "published_at": published_at.isoformat()
            })
        
        return podcasts
