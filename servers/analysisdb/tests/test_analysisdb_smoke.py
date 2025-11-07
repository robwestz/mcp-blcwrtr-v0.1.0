"""
Smoke tests for AnalysisDB MCP Server
"""

import json
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone
from uuid import uuid4

from src.server import list_tools, call_tool, calculate_anchor_risk


@pytest.mark.asyncio
async def test_list_tools():
    """Test that all tools are listed correctly."""
    tools = await list_tools()
    
    assert len(tools) == 4
    tool_names = [tool.name for tool in tools]
    
    assert "db.get_publisher_profile" in tool_names
    assert "db.get_anchor_portfolio" in tool_names
    assert "db.get_pages" in tool_names
    assert "db.log_event" in tool_names


def test_calculate_anchor_risk():
    """Test anchor risk calculation."""
    # Test low risk (well distributed)
    risk, level = calculate_anchor_risk(10, 10, 10, 10)
    assert level == "low"
    assert 0 <= risk <= 0.3
    
    # Test medium risk (moderate exact match)
    risk, level = calculate_anchor_risk(20, 10, 5, 5)
    assert level == "medium"
    assert 0.3 < risk <= 0.6
    
    # Test high risk (high exact match)
    risk, level = calculate_anchor_risk(35, 5, 3, 2)
    assert level == "high"
    assert risk > 0.6
    
    # Test empty portfolio
    risk, level = calculate_anchor_risk(0, 0, 0, 0)
    assert risk == 0.0
    assert level == "low"


@pytest.mark.asyncio
async def test_get_publisher_profile():
    """Test getting publisher profile."""
    with patch('src.server.db_adapter') as mock_adapter:
        # Mock the adapter method
        mock_adapter.get_publisher_profile = AsyncMock(return_value={
            "domain": "test.se",
            "voice": {"tone": "formal", "perspective": "third_person", "style_markers": []},
            "lix_range": "medium",
            "policy": {"nofollow": False, "sponsored": False, "ugc": False, "restrictions": []},
            "examples": []
        })
        
        result = await call_tool("db.get_publisher_profile", {"domain": "test.se"})
        
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["domain"] == "test.se"
        assert data["voice"]["tone"] == "formal"
        assert data["lix_range"] == "medium"


@pytest.mark.asyncio
async def test_get_anchor_portfolio():
    """Test getting anchor portfolio."""
    with patch('src.server.db_adapter') as mock_adapter:
        # Mock the adapter method
        mock_adapter.get_anchor_portfolio = AsyncMock(return_value={
            "target_domain": "example.com",
            "exact": 15,
            "partial": 10,
            "brand": 20,
            "generic": 5,
            "total": 50,
            "risk": 0.35,
            "risk_level": "medium"
        })
        
        result = await call_tool("db.get_anchor_portfolio", {"target_url": "https://example.com/page"})
        
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["target_domain"] == "example.com"
        assert data["total"] == 50
        assert data["risk_level"] == "medium"


@pytest.mark.asyncio
async def test_get_pages():
    """Test getting pages."""
    with patch('src.server.db_adapter') as mock_adapter:
        # Mock the adapter method
        mock_adapter.get_pages = AsyncMock(return_value=[
            {
                "id": str(uuid4()),
                "url": "https://example.com/article1",
                "type": "article",
                "customer_id": None,
                "metadata": {}
            },
            {
                "id": str(uuid4()),
                "url": "https://example.com/landing",
                "type": "landing",
                "customer_id": None,
                "metadata": {}
            }
        ])
        
        result = await call_tool("db.get_pages", {"limit": 10})
        
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert len(data["pages"]) == 2
        assert data["total"] == 2


@pytest.mark.asyncio
async def test_log_event():
    """Test logging an event."""
    with patch('src.server.db_adapter') as mock_adapter:
        event_id = uuid4()
        
        # Mock the adapter method
        mock_adapter.log_event = AsyncMock(return_value=event_id)
        
        result = await call_tool("db.log_event", {
            "type": "order_received",
            "order_ref": str(uuid4()),
            "payload": {"test": "data"}
        })
        
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["ok"] is True
        assert data["event_id"] == str(event_id)
        assert "timestamp" in data


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in tool calls."""
    with patch('src.server.db_adapter') as mock_adapter:
        # Mock a database error
        mock_adapter.get_publisher_profile = AsyncMock(side_effect=Exception("Database connection failed"))
        
        result = await call_tool("db.get_publisher_profile", {"domain": "error.com"})
        
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert "error" in data
        assert data["error"]["code"] == "ERR_TOOL_INTERNAL"
        assert "Database connection failed" in data["error"]["message"]


@pytest.mark.asyncio
async def test_invalid_tool():
    """Test calling an invalid tool."""
    result = await call_tool("invalid.tool", {})
    
    assert len(result) == 1
    data = json.loads(result[0].text)
    assert "error" in data
    assert "Unknown tool" in data["error"]["message"]


@pytest.mark.asyncio
async def test_schema_validation():
    """Test that tool schemas are valid."""
    tools = await list_tools()
    
    for tool in tools:
        # Check that inputSchema is present and valid
        assert "type" in tool.inputSchema
        assert tool.inputSchema["type"] == "object"
        assert "properties" in tool.inputSchema
        
        # Check specific tool requirements
        if tool.name == "db.get_publisher_profile":
            assert "domain" in tool.inputSchema["properties"]
            assert "required" in tool.inputSchema
            assert "domain" in tool.inputSchema["required"]
