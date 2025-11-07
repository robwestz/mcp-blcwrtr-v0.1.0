#!/usr/bin/env python3
"""
Collectors MCP Server
Data collectors for SERP, media signals and SEO metrics
"""

import os
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult

from adapters.serp import SerpAdapter
from adapters.news import NewsAdapter
from mocks.mock_collectors import MockCollectors

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('collectors')

# Initialize server
server = Server("collectors")

# Initialize adapters
use_mock = os.getenv('USE_MOCK_COLLECTORS', 'true').lower() == 'true'
if use_mock:
    logger.info("Using mock collectors")
    serp_adapter = MockCollectors()
    news_adapter = MockCollectors()
else:
    serp_api_key = os.getenv('SERP_API_KEY')
    if serp_api_key:
        serp_adapter = SerpAdapter(serp_api_key)
        news_adapter = NewsAdapter()
    else:
        logger.warning("No SERP_API_KEY found, defaulting to mock mode")
        serp_adapter = MockCollectors()
        news_adapter = MockCollectors()


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    tools = [
        Tool(
            name="serp.get_snapshot",
            description="Get SERP analysis with intents and LSI terms",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Search query to analyze"
                    },
                    "locale": {
                        "type": "string",
                        "default": "sv-SE",
                        "pattern": "^[a-z]{2}-[A-Z]{2}$",
                        "description": "Locale for search (e.g. sv-SE, en-US)"
                    },
                    "use_cache": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to use cached results if available"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="media.signals",
            description="Get news, video and podcast signals for topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Topic to search for in media sources"
                    },
                    "since": {
                        "type": "string",
                        "format": "date",
                        "description": "Get signals since this date (ISO format)"
                    },
                    "sources": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["news", "video", "podcasts"]
                        },
                        "default": ["news", "video", "podcasts"],
                        "description": "Media sources to include"
                    }
                },
                "required": ["topic"]
            }
        )
    ]
    
    # Add optional tools if API keys are present
    if os.getenv('AHREFS_KEY'):
        tools.append(Tool(
            name="ahrefs.metrics",
            description="[Optional] Get Ahrefs metrics for domain or URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Domain or URL to analyze"
                    },
                    "metrics": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["dr", "ur", "backlinks", "referring_domains", "organic_traffic"]
                        },
                        "default": ["dr", "backlinks"],
                        "description": "Specific metrics to retrieve"
                    }
                },
                "required": ["target"]
            }
        ))
    
    if os.getenv('SEMRUSH_KEY'):
        tools.append(Tool(
            name="semrush.metrics",
            description="[Optional] Get Semrush metrics for domain or URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Domain or URL to analyze"
                    },
                    "metrics": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["authority_score", "organic_traffic", "keywords", "backlinks", "competitors"]
                        },
                        "default": ["authority_score", "organic_traffic"],
                        "description": "Specific metrics to retrieve"
                    }
                },
                "required": ["target"]
            }
        ))
    
    return tools


def detect_search_intents(query: str, locale: str = "sv-SE") -> List[str]:
    """Detect search intents from query."""
    query_lower = query.lower()
    intents = []
    
    # Swedish intent signals
    if locale.startswith("sv"):
        if any(word in query_lower for word in ["köp", "pris", "billig", "bäst", "erbjudande"]):
            intents.append("commercial")
        if any(word in query_lower for word in ["vad är", "hur", "varför", "guide", "tips"]):
            intents.append("informational")
        if any(word in query_lower for word in ["nära", "stockholm", "göteborg", "malmö"]):
            intents.append("local")
        if any(word in query_lower for word in ["beställ", "boka", "registrera"]):
            intents.append("transactional")
    else:
        # English intent signals
        if any(word in query_lower for word in ["buy", "price", "cheap", "best", "deal"]):
            intents.append("commercial")
        if any(word in query_lower for word in ["what is", "how to", "why", "guide", "tips"]):
            intents.append("informational")
        if any(word in query_lower for word in ["near me", "local", "nearby"]):
            intents.append("local")
        if any(word in query_lower for word in ["order", "book", "register"]):
            intents.append("transactional")
    
    # Default to informational if no specific intent detected
    if not intents:
        intents.append("informational")
    
    return intents


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> ToolResult:
    """Handle tool calls."""
    try:
        if name == "serp.get_snapshot":
            query = arguments["query"]
            locale = arguments.get("locale", "sv-SE")
            use_cache = arguments.get("use_cache", True)
            
            # Check cache first if enabled
            if use_cache and hasattr(serp_adapter, 'check_cache'):
                cached = await serp_adapter.check_cache(query, locale)
                if cached:
                    return [TextContent(text=json.dumps(cached, indent=2))]
            
            # Get SERP data
            serp_data = await serp_adapter.get_serp_snapshot(query, locale)
            
            # Detect intents
            intents = detect_search_intents(query, locale)
            
            # Build result
            result = {
                "query": query,
                "locale": locale,
                "intents": intents,
                "lsi_terms": serp_data.get("lsi_terms", []),
                "top_urls": serp_data.get("top_urls", []),
                "features": serp_data.get("features", {}),
                "cached_at": datetime.now(timezone.utc).isoformat(),
                "ttl": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
            }
            
            return [TextContent(text=json.dumps(result, indent=2))]
        
        elif name == "media.signals":
            topic = arguments["topic"]
            since = arguments.get("since")
            sources = arguments.get("sources", ["news", "video", "podcasts"])
            
            # Collect signals from requested sources
            signals = {
                "topic": topic,
                "news": [],
                "video": [],
                "podcasts": [],
                "total_signals": 0
            }
            
            if "news" in sources:
                news_data = await news_adapter.get_news_signals(topic, since)
                signals["news"] = news_data
                signals["total_signals"] += len(news_data)
            
            if "video" in sources:
                video_data = await news_adapter.get_video_signals(topic, since)
                signals["video"] = video_data
                signals["total_signals"] += len(video_data)
            
            if "podcasts" in sources:
                podcast_data = await news_adapter.get_podcast_signals(topic, since)
                signals["podcasts"] = podcast_data
                signals["total_signals"] += len(podcast_data)
            
            return [TextContent(text=json.dumps(signals, indent=2))]
        
        elif name == "ahrefs.metrics":
            # Check if API key is available
            if not os.getenv('AHREFS_KEY'):
                return [TextContent(text=json.dumps({
                    "error": "Ahrefs API key not configured",
                    "hint": "Set AHREFS_KEY environment variable"
                }, indent=2))]
            
            # Mock response for now
            target = arguments["target"]
            metrics = arguments.get("metrics", ["dr", "backlinks"])
            
            result = {
                "target": target,
                "dr": 45.5 if "dr" in metrics else None,
                "ur": 38.2 if "ur" in metrics else None,
                "backlinks": 12500 if "backlinks" in metrics else None,
                "referring_domains": 850 if "referring_domains" in metrics else None,
                "organic_traffic": 5200 if "organic_traffic" in metrics else None,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Remove None values
            result = {k: v for k, v in result.items() if v is not None}
            
            return [TextContent(text=json.dumps(result, indent=2))]
        
        elif name == "semrush.metrics":
            # Check if API key is available
            if not os.getenv('SEMRUSH_KEY'):
                return [TextContent(text=json.dumps({
                    "error": "Semrush API key not configured",
                    "hint": "Set SEMRUSH_KEY environment variable"
                }, indent=2))]
            
            # Mock response for now
            target = arguments["target"]
            metrics = arguments.get("metrics", ["authority_score", "organic_traffic"])
            
            result = {
                "target": target,
                "authority_score": 52 if "authority_score" in metrics else None,
                "organic_traffic": 8500 if "organic_traffic" in metrics else None,
                "keywords": 1250 if "keywords" in metrics else None,
                "backlinks": 15800 if "backlinks" in metrics else None,
                "competitors": [
                    {"domain": "competitor1.com", "competition_level": 0.85},
                    {"domain": "competitor2.com", "competition_level": 0.72}
                ] if "competitors" in metrics else None,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Remove None values
            result = {k: v for k, v in result.items() if v is not None}
            
            return [TextContent(text=json.dumps(result, indent=2))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        error_result = {
            "error": {
                "code": "ERR_TOOL_INTERNAL",
                "message": str(e),
                "hint": "Check logs for details"
            }
        }
        return [TextContent(text=json.dumps(error_result, indent=2))]


async def main():
    """Main entry point."""
    logger.info("Starting Collectors MCP Server...")
    logger.info(f"Mock mode: {use_mock}")
    logger.info(f"Available API keys: SERP={'✓' if os.getenv('SERP_API_KEY') else '✗'}, "
                f"Ahrefs={'✓' if os.getenv('AHREFS_KEY') else '✗'}, "
                f"Semrush={'✓' if os.getenv('SEMRUSH_KEY') else '✗'}")
    logger.info("READY: Collectors MCP Server is ready to accept requests")
    
    # Run server
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read, write):
        await server.run(read, write)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
