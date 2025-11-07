#!/usr/bin/env python3
"""
Features MCP Server
Feature builders for entity graphs and anchor portfolio analysis
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse

from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult

from entity_graph import EntityGraphBuilder
from anchor_portfolio import AnchorPortfolioAnalyzer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('features')

# Initialize server
server = Server("features")

# Initialize feature builders
graph_builder = EntityGraphBuilder()
portfolio_analyzer = AnchorPortfolioAnalyzer()


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="features.entity_graph",
            description="Build entity graph from seed terms",
            inputSchema={
                "type": "object",
                "properties": {
                    "seed_terms": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "minLength": 1
                        },
                        "minItems": 1,
                        "maxItems": 10,
                        "description": "Seed terms to build entity graph from"
                    },
                    "depth": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 3,
                        "default": 2,
                        "description": "Depth of entity expansion"
                    },
                    "max_nodes": {
                        "type": "integer",
                        "minimum": 10,
                        "maximum": 100,
                        "default": 50,
                        "description": "Maximum number of nodes in graph"
                    },
                    "language": {
                        "type": "string",
                        "default": "sv",
                        "enum": ["sv", "en"],
                        "description": "Language for entity expansion"
                    }
                },
                "required": ["seed_terms"]
            }
        ),
        Tool(
            name="features.anchor_portfolio.recalc",
            description="Recalculate anchor portfolio mix and risk",
            inputSchema={
                "type": "object",
                "properties": {
                    "target_domain": {
                        "type": "string",
                        "format": "hostname",
                        "description": "Target domain to recalculate portfolio for"
                    },
                    "new_anchor": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "minLength": 1
                            },
                            "type": {
                                "type": "string",
                                "enum": ["exact", "partial", "brand", "generic"]
                            }
                        },
                        "description": "New anchor to add to portfolio (optional)"
                    },
                    "removed_anchor": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "minLength": 1
                            },
                            "type": {
                                "type": "string",
                                "enum": ["exact", "partial", "brand", "generic"]
                            }
                        },
                        "description": "Anchor to remove from portfolio (optional)"
                    },
                    "save_to_db": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether to save updated portfolio to database"
                    }
                },
                "required": ["target_domain"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> ToolResult:
    """Handle tool calls."""
    try:
        if name == "features.entity_graph":
            seed_terms = arguments["seed_terms"]
            depth = arguments.get("depth", 2)
            max_nodes = arguments.get("max_nodes", 50)
            language = arguments.get("language", "sv")
            
            # Build entity graph
            graph_data = await graph_builder.build_graph(
                seed_terms=seed_terms,
                depth=depth,
                max_nodes=max_nodes,
                language=language
            )
            
            return [TextContent(text=json.dumps(graph_data, indent=2))]
        
        elif name == "features.anchor_portfolio.recalc":
            target_domain = arguments["target_domain"]
            new_anchor = arguments.get("new_anchor")
            removed_anchor = arguments.get("removed_anchor")
            save_to_db = arguments.get("save_to_db", False)
            
            # Get current portfolio
            current_portfolio = await portfolio_analyzer.get_current_portfolio(target_domain)
            
            # Apply changes
            updated_portfolio = current_portfolio.copy()
            
            if removed_anchor:
                anchor_type = removed_anchor["type"]
                if updated_portfolio.get(anchor_type, 0) > 0:
                    updated_portfolio[anchor_type] -= 1
            
            if new_anchor:
                anchor_type = new_anchor["type"]
                updated_portfolio[anchor_type] = updated_portfolio.get(anchor_type, 0) + 1
            
            # Calculate risk and recommendations
            result = await portfolio_analyzer.analyze_portfolio(
                target_domain=target_domain,
                old_portfolio=current_portfolio,
                new_portfolio=updated_portfolio,
                save_to_db=save_to_db
            )
            
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
    logger.info("Starting Features MCP Server...")
    
    # Initialize connections if needed
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        await portfolio_analyzer.connect(db_url)
        logger.info("Database connected for portfolio analysis")
    
    logger.info("READY: Features MCP Server is ready to accept requests")
    
    # Run server
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read, write):
        await server.run(read, write)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
