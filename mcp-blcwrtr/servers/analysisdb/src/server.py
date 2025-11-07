#!/usr/bin/env python3
"""
AnalysisDB MCP Server
Database adapter for publisher profiles, anchor portfolios and event logging
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4

from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult

from adapters.postgres import PostgresAdapter

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('analysisdb')

# Initialize server
server = Server("analysisdb")
db_adapter = None


def calculate_anchor_risk(exact: int, partial: int, brand: int, generic: int) -> tuple[float, str]:
    """Calculate anchor portfolio risk score and level."""
    total = exact + partial + brand + generic
    if total == 0:
        return 0.0, "low"
    
    # Risk factors
    exact_ratio = exact / total
    diversity_score = 1 - max(exact_ratio, partial/total, brand/total, generic/total)
    
    # Calculate risk (0-1)
    risk = (exact_ratio * 0.7) + ((1 - diversity_score) * 0.3)
    
    # Determine level
    if risk <= 0.3:
        risk_level = "low"
    elif risk <= 0.6:
        risk_level = "medium"
    else:
        risk_level = "high"
    
    return round(risk, 2), risk_level


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="db.get_publisher_profile",
            description="Get publisher voice profile, LIX range and policies for a domain",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "format": "hostname",
                        "description": "Publisher domain to get profile for"
                    }
                },
                "required": ["domain"]
            }
        ),
        Tool(
            name="db.get_anchor_portfolio",
            description="Get anchor text distribution and risk assessment for target URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "target_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "Target URL to analyze anchor portfolio for"
                    },
                    "recalculate": {
                        "type": "boolean",
                        "default": False,
                        "description": "Force recalculation of portfolio metrics"
                    }
                },
                "required": ["target_url"]
            }
        ),
        Tool(
            name="db.get_pages",
            description="Get pages for customer or general inventory",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "Optional customer ID to filter pages"
                    },
                    "type": {
                        "type": "string",
                        "enum": ["landing", "article", "category", "product"],
                        "description": "Optional page type filter"
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20
                    }
                }
            }
        ),
        Tool(
            name="db.log_event",
            description="Log audit events for tracking and compliance",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["order_received", "preflight_complete", "qc_passed", "qc_failed", "delivered", "error"],
                        "description": "Event type"
                    },
                    "order_ref": {
                        "type": "string",
                        "format": "uuid",
                        "description": "Order reference UUID"
                    },
                    "payload": {
                        "type": "object",
                        "description": "Event-specific payload data"
                    }
                },
                "required": ["type", "payload"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> ToolResult:
    """Handle tool calls."""
    global db_adapter
    
    try:
        if name == "db.get_publisher_profile":
            domain = arguments["domain"]
            
            # Try to fetch from database
            profile = await db_adapter.get_publisher_profile(domain)
            
            if not profile:
                # Return mock data for demo
                profile = {
                    "domain": domain,
                    "voice": {
                        "tone": "conversational",
                        "perspective": "third_person",
                        "style_markers": ["berättande", "informativ", "personlig"]
                    },
                    "lix_range": "easy",
                    "policy": {
                        "nofollow": False,
                        "sponsored": True,
                        "ugc": False,
                        "restrictions": []
                    },
                    "examples": [
                        {
                            "url": f"https://{domain}/artikel/exempel",
                            "title": "Exempel på typisk artikel",
                            "excerpt": "Detta är hur vi brukar skriva..."
                        }
                    ]
                }
            
            return [TextContent(text=json.dumps(profile, indent=2))]
        
        elif name == "db.get_anchor_portfolio":
            target_url = arguments["target_url"]
            recalculate = arguments.get("recalculate", False)
            
            # Extract domain from URL
            from urllib.parse import urlparse
            target_domain = urlparse(target_url).netloc
            
            # Get or calculate portfolio
            portfolio = await db_adapter.get_anchor_portfolio(target_domain)
            
            if not portfolio or recalculate:
                # Mock calculation for demo
                portfolio = {
                    "target_domain": target_domain,
                    "exact": 12,
                    "partial": 8,
                    "brand": 15,
                    "generic": 5,
                    "total": 40
                }
                
                # Calculate risk
                risk, risk_level = calculate_anchor_risk(
                    portfolio["exact"],
                    portfolio["partial"],
                    portfolio["brand"],
                    portfolio["generic"]
                )
                
                portfolio["risk"] = risk
                portfolio["risk_level"] = risk_level
                portfolio["recommendations"] = []
                
                if risk_level == "high":
                    portfolio["recommendations"].append("Reduce exact match anchors")
                    portfolio["recommendations"].append("Increase brand and partial variations")
                elif risk_level == "medium":
                    portfolio["recommendations"].append("Good diversity, monitor exact match ratio")
            
            return [TextContent(text=json.dumps(portfolio, indent=2))]
        
        elif name == "db.get_pages":
            customer_id = arguments.get("customer_id")
            page_type = arguments.get("type")
            limit = arguments.get("limit", 20)
            
            # Fetch pages
            pages = await db_adapter.get_pages(customer_id, page_type, limit)
            
            # Return result
            result = {
                "pages": pages,
                "total": len(pages)
            }
            
            return [TextContent(text=json.dumps(result, indent=2))]
        
        elif name == "db.log_event":
            event_type = arguments["type"]
            order_ref = arguments.get("order_ref")
            payload = arguments["payload"]
            
            # Log event
            event_id = await db_adapter.log_event(event_type, order_ref, payload)
            
            result = {
                "ok": True,
                "event_id": str(event_id),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
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
    global db_adapter
    
    logger.info("Starting AnalysisDB MCP Server...")
    
    # Initialize database adapter
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL environment variable not set")
        raise ValueError("DATABASE_URL required")
    
    db_adapter = PostgresAdapter(db_url)
    await db_adapter.connect()
    
    logger.info("Database connected successfully")
    logger.info("READY: AnalysisDB MCP Server is ready to accept requests")
    
    # Run server
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read, write):
        await server.run(read, write)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
