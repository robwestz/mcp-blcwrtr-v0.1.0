"""
Smoke tests for Collectors MCP Server
"""

import json
import pytest
from unittest.mock import patch
from datetime import datetime

from src.server import list_tools, call_tool, detect_search_intents


@pytest.mark.asyncio
async def test_list_tools():
    """Test that core tools are always listed."""
    with patch.dict('os.environ', {}, clear=True):
        tools = await list_tools()
    
    assert len(tools) >= 2  # At least serp and media tools
    tool_names = [tool.name for tool in tools]
    
    assert "serp.get_snapshot" in tool_names
    assert "media.signals" in tool_names
    
    # Optional tools should not be present without API keys
    assert "ahrefs.metrics" not in tool_names
    assert "semrush.metrics" not in tool_names


@pytest.mark.asyncio
async def test_list_tools_with_api_keys():
    """Test that optional tools appear when API keys are set."""
    with patch.dict('os.environ', {'AHREFS_KEY': 'test', 'SEMRUSH_KEY': 'test'}):
        tools = await list_tools()
    
    tool_names = [tool.name for tool in tools]
    assert "ahrefs.metrics" in tool_names
    assert "semrush.metrics" in tool_names


def test_detect_search_intents_swedish():
    """Test Swedish search intent detection."""
    # Commercial intent
    assert "commercial" in detect_search_intents("köp billig laptop", "sv-SE")
    assert "commercial" in detect_search_intents("bästa pris iphone", "sv-SE")
    
    # Informational intent
    assert "informational" in detect_search_intents("vad är släktforskning", "sv-SE")
    assert "informational" in detect_search_intents("hur fungerar det", "sv-SE")
    
    # Local intent
    assert "local" in detect_search_intents("restaurang nära stockholm", "sv-SE")
    assert "local" in detect_search_intents("gym göteborg centrum", "sv-SE")
    
    # Default to informational
    intents = detect_search_intents("random query", "sv-SE")
    assert "informational" in intents


def test_detect_search_intents_english():
    """Test English search intent detection."""
    # Commercial intent
    assert "commercial" in detect_search_intents("buy cheap laptop", "en-US")
    assert "commercial" in detect_search_intents("best price iphone", "en-US")
    
    # Informational intent
    assert "informational" in detect_search_intents("what is genealogy", "en-US")
    assert "informational" in detect_search_intents("how to guide", "en-US")


@pytest.mark.asyncio
async def test_serp_get_snapshot():
    """Test SERP snapshot retrieval."""
    result = await call_tool("serp.get_snapshot", {
        "query": "släktforskning tips",
        "locale": "sv-SE"
    })
    
    assert len(result) == 1
    data = json.loads(result[0].text)
    
    # Check required fields
    assert "query" in data
    assert "locale" in data
    assert "intents" in data
    assert "lsi_terms" in data
    assert "top_urls" in data
    
    # Check data quality
    assert len(data["intents"]) > 0
    assert len(data["lsi_terms"]) >= 6  # Minimum LSI terms
    assert len(data["top_urls"]) > 0
    
    # Check top URLs structure
    if data["top_urls"]:
        url = data["top_urls"][0]
        assert "url" in url
        assert "title" in url
        assert "position" in url
        assert "domain" in url


@pytest.mark.asyncio
async def test_media_signals():
    """Test media signals collection."""
    result = await call_tool("media.signals", {
        "topic": "artificial intelligence",
        "sources": ["news", "video", "podcasts"]
    })
    
    assert len(result) == 1
    data = json.loads(result[0].text)
    
    # Check required fields
    assert "topic" in data
    assert "news" in data
    assert "video" in data
    assert "podcasts" in data
    assert "total_signals" in data
    
    # Check that we got some signals
    assert data["total_signals"] > 0
    assert isinstance(data["news"], list)
    assert isinstance(data["video"], list)
    assert isinstance(data["podcasts"], list)


@pytest.mark.asyncio
async def test_media_signals_filtered_sources():
    """Test media signals with filtered sources."""
    result = await call_tool("media.signals", {
        "topic": "test topic",
        "sources": ["news"]  # Only news
    })
    
    data = json.loads(result[0].text)
    
    # Should have news data but empty video/podcasts
    assert len(data["news"]) > 0
    assert len(data["video"]) == 0
    assert len(data["podcasts"]) == 0


@pytest.mark.asyncio
async def test_ahrefs_without_key():
    """Test Ahrefs metrics without API key."""
    with patch.dict('os.environ', {}, clear=True):
        result = await call_tool("ahrefs.metrics", {
            "target": "example.com"
        })
    
    data = json.loads(result[0].text)
    assert "error" in data
    assert "API key not configured" in data["error"]


@pytest.mark.asyncio
async def test_ahrefs_with_key():
    """Test Ahrefs metrics with API key (mock mode)."""
    with patch.dict('os.environ', {'AHREFS_KEY': 'test-key'}):
        result = await call_tool("ahrefs.metrics", {
            "target": "example.com",
            "metrics": ["dr", "backlinks"]
        })
    
    data = json.loads(result[0].text)
    assert "target" in data
    assert "dr" in data
    assert "backlinks" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling for invalid tool."""
    result = await call_tool("invalid.tool", {})
    
    data = json.loads(result[0].text)
    assert "error" in data
    assert data["error"]["code"] == "ERR_TOOL_INTERNAL"
    assert "Unknown tool" in data["error"]["message"]


@pytest.mark.asyncio
async def test_schema_compliance():
    """Test that outputs match declared schemas."""
    # Test SERP snapshot
    serp_result = await call_tool("serp.get_snapshot", {
        "query": "test query"
    })
    serp_data = json.loads(serp_result[0].text)
    
    # Validate required fields from schema
    assert isinstance(serp_data["query"], str)
    assert isinstance(serp_data["locale"], str)
    assert isinstance(serp_data["intents"], list)
    assert isinstance(serp_data["lsi_terms"], list)
    assert isinstance(serp_data["top_urls"], list)
    
    # Test media signals
    media_result = await call_tool("media.signals", {
        "topic": "test topic"
    })
    media_data = json.loads(media_result[0].text)
    
    assert isinstance(media_data["topic"], str)
    assert isinstance(media_data["news"], list)
    assert isinstance(media_data["video"], list) 
    assert isinstance(media_data["podcasts"], list)
    assert isinstance(media_data["total_signals"], int)
