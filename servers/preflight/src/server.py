#!/usr/bin/env python3
"""
Preflight MCP Server
Preflight planning and QC validation for backlink content
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from uuid import UUID

from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult

from preflight_build import PreflightBuilder
from qc_validate import QCValidator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('preflight')

# Initialize server
server = Server("preflight")

# Initialize components
preflight_builder = PreflightBuilder()
qc_validator = QCValidator()


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="preflight.build",
            description="Build preflight matrix and writer prompt from order",
            inputSchema={
                "type": "object",
                "properties": {
                    "order": {
                        "type": "object",
                        "properties": {
                            "order_ref": {
                                "type": "string",
                                "format": "uuid"
                            },
                            "customer_id": {
                                "type": "string"
                            },
                            "publication_domain": {
                                "type": "string",
                                "format": "hostname"
                            },
                            "target_url": {
                                "type": "string",
                                "format": "uri"
                            },
                            "anchor_text": {
                                "type": "string",
                                "minLength": 1
                            },
                            "topic": {
                                "type": "string",
                                "minLength": 10
                            },
                            "constraints": {
                                "type": "object",
                                "properties": {
                                    "word_count": {
                                        "type": "integer",
                                        "minimum": 300,
                                        "maximum": 3000,
                                        "default": 800
                                    },
                                    "tone": {
                                        "type": "string",
                                        "enum": ["informativ", "konversation", "professionell", "akademisk"],
                                        "default": "informativ"
                                    },
                                    "compliance": {
                                        "type": "array",
                                        "items": {
                                            "type": "string",
                                            "enum": ["gambling", "finance", "health", "legal", "crypto"]
                                        }
                                    }
                                }
                            }
                        },
                        "required": ["order_ref", "customer_id", "publication_domain", 
                                    "target_url", "anchor_text", "topic"]
                    }
                },
                "required": ["order"]
            }
        ),
        Tool(
            name="qc.validate",
            description="Validate article against QC thresholds",
            inputSchema={
                "type": "object",
                "properties": {
                    "article_text": {
                        "type": "string",
                        "minLength": 100,
                        "description": "Full article text to validate"
                    },
                    "preflight_matrix": {
                        "type": "object",
                        "description": "Optional preflight matrix for validation context"
                    },
                    "auto_fix": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether to attempt automatic fixes"
                    },
                    "strict_mode": {
                        "type": "boolean",
                        "default": False,
                        "description": "Apply stricter validation rules"
                    }
                },
                "required": ["article_text"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> ToolResult:
    """Handle tool calls."""
    try:
        if name == "preflight.build":
            order = arguments["order"]
            
            # Build preflight matrix
            preflight_result = await preflight_builder.build(order)
            
            return [TextContent(text=json.dumps(preflight_result, indent=2, ensure_ascii=False))]
        
        elif name == "qc.validate":
            article_text = arguments["article_text"]
            preflight_matrix = arguments.get("preflight_matrix")
            auto_fix = arguments.get("auto_fix", False)
            strict_mode = arguments.get("strict_mode", False)
            
            # Validate article
            validation_result = await qc_validator.validate(
                article_text=article_text,
                preflight_matrix=preflight_matrix,
                auto_fix=auto_fix,
                strict_mode=strict_mode
            )
            
            return [TextContent(text=json.dumps(validation_result, indent=2, ensure_ascii=False))]
        
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
    logger.info("Starting Preflight MCP Server...")
    
    # Initialize database connection if needed
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        await preflight_builder.connect(db_url)
        await qc_validator.connect(db_url)
        logger.info("Database connected for preflight operations")
    
    logger.info("READY: Preflight MCP Server is ready to accept requests")
    
    # Run server
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read, write):
        await server.run(read, write)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
