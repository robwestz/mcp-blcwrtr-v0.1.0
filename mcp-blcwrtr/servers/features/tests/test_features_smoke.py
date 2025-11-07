"""
Smoke tests for Features MCP Server
"""

import json
import pytest
from unittest.mock import Mock, AsyncMock, patch

from src.server import list_tools, call_tool
from src.entity_graph import EntityGraphBuilder
from src.anchor_portfolio import AnchorPortfolioAnalyzer


@pytest.mark.asyncio
async def test_list_tools():
    """Test that all tools are listed correctly."""
    tools = await list_tools()
    
    assert len(tools) == 2
    tool_names = [tool.name for tool in tools]
    
    assert "features.entity_graph" in tool_names
    assert "features.anchor_portfolio.recalc" in tool_names


@pytest.mark.asyncio
async def test_entity_graph_basic():
    """Test basic entity graph generation."""
    result = await call_tool("features.entity_graph", {
        "seed_terms": ["släktforskning", "casino"],
        "depth": 2,
        "max_nodes": 20
    })
    
    assert len(result) == 1
    data = json.loads(result[0].text)
    
    # Check structure
    assert "nodes" in data
    assert "edges" in data
    assert "metadata" in data
    
    # Check nodes
    assert len(data["nodes"]) > 2  # More than just seed nodes
    assert len(data["nodes"]) <= 20  # Respects max_nodes
    
    # Check seed nodes are present
    seed_ids = [n["id"] for n in data["nodes"] if n["type"] == "seed"]
    assert "släktforskning" in seed_ids
    assert "casino" in seed_ids
    
    # Check edges exist
    assert len(data["edges"]) > 0
    
    # Check metadata
    assert data["metadata"]["seed_terms"] == ["släktforskning", "casino"]
    assert data["metadata"]["node_count"] == len(data["nodes"])
    assert data["metadata"]["edge_count"] == len(data["edges"])


@pytest.mark.asyncio
async def test_entity_graph_language():
    """Test entity graph with different languages."""
    # Test Swedish
    result_sv = await call_tool("features.entity_graph", {
        "seed_terms": ["forskning"],
        "language": "sv",
        "depth": 1
    })
    
    data_sv = json.loads(result_sv[0].text)
    swedish_terms = [n["label"] for n in data_sv["nodes"]]
    
    # Should contain Swedish expansions
    assert any(term in swedish_terms for term in ["studie", "analys", "metod"])
    
    # Test English
    result_en = await call_tool("features.entity_graph", {
        "seed_terms": ["research"],
        "language": "en",
        "depth": 1
    })
    
    data_en = json.loads(result_en[0].text)
    english_terms = [n["label"] for n in data_en["nodes"]]
    
    # Should contain English expansions
    assert any("research" in term.lower() for term in english_terms)


@pytest.mark.asyncio
async def test_anchor_portfolio_recalc():
    """Test anchor portfolio recalculation."""
    result = await call_tool("features.anchor_portfolio.recalc", {
        "target_domain": "example.com",
        "new_anchor": {
            "text": "casino online",
            "type": "partial"
        }
    })
    
    assert len(result) == 1
    data = json.loads(result[0].text)
    
    # Check structure
    assert "target_domain" in data
    assert "old_mix" in data
    assert "new_mix" in data
    assert "old_risk" in data
    assert "new_risk" in data
    assert "risk_level" in data
    assert "delta" in data
    assert "recommendations" in data
    
    # Check that partial count increased
    assert data["new_mix"]["partial"] == data["old_mix"]["partial"] + 1
    
    # Check risk calculation
    assert 0 <= data["new_risk"] <= 1
    assert data["risk_level"] in ["low", "medium", "high"]
    
    # Check delta
    assert "risk_change" in data["delta"]
    assert "risk_direction" in data["delta"]
    assert data["delta"]["risk_direction"] in ["improved", "worsened", "unchanged"]


@pytest.mark.asyncio
async def test_anchor_portfolio_remove():
    """Test removing anchor from portfolio."""
    result = await call_tool("features.anchor_portfolio.recalc", {
        "target_domain": "example.com",
        "removed_anchor": {
            "text": "click here",
            "type": "generic"
        }
    })
    
    data = json.loads(result[0].text)
    
    # Check that generic count decreased (if it was > 0)
    if data["old_mix"]["generic"] > 0:
        assert data["new_mix"]["generic"] == data["old_mix"]["generic"] - 1


@pytest.mark.asyncio
async def test_anchor_portfolio_recommendations():
    """Test that recommendations are generated."""
    result = await call_tool("features.anchor_portfolio.recalc", {
        "target_domain": "test.com"
    })
    
    data = json.loads(result[0].text)
    recommendations = data["recommendations"]
    
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    
    # Check recommendation structure
    for rec in recommendations:
        assert "action" in rec
        assert "anchor_type" in rec
        assert "rationale" in rec
        assert "priority" in rec
        assert rec["action"] in ["increase", "decrease", "maintain", "diversify"]
        assert rec["anchor_type"] in ["exact", "partial", "brand", "generic"]
        assert rec["priority"] in ["high", "medium", "low"]


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling for invalid inputs."""
    # Test with missing required parameter
    result = await call_tool("features.entity_graph", {})
    
    data = json.loads(result[0].text)
    assert "error" in data
    assert data["error"]["code"] == "ERR_TOOL_INTERNAL"
    
    # Test with invalid tool name
    result = await call_tool("features.invalid", {})
    
    data = json.loads(result[0].text)
    assert "error" in data
    assert "Unknown tool" in data["error"]["message"]


def test_entity_graph_builder():
    """Test EntityGraphBuilder directly."""
    builder = EntityGraphBuilder()
    
    # Test ID normalization
    assert builder._normalize_id("Test Term") == "test_term"
    assert builder._normalize_id("test-term") == "test_term"
    
    # Test categorization
    assert builder._categorize_term("släktforskning", "sv") == "genealogy"
    assert builder._categorize_term("casino", "sv") == "gaming"
    assert builder._categorize_term("online", "sv") == "digital"
    
    # Test edge classification
    assert builder._classify_edge("forskning", "forskningsmetod", "sv") == "hierarchical"


def test_anchor_portfolio_analyzer():
    """Test AnchorPortfolioAnalyzer directly."""
    analyzer = AnchorPortfolioAnalyzer()
    
    # Test risk calculation
    portfolio = {"exact": 5, "partial": 10, "brand": 10, "generic": 5}
    risk, level = analyzer._calculate_risk(portfolio)
    
    assert 0 <= risk <= 1
    assert level in ["low", "medium", "high"]
    
    # Test high risk portfolio
    high_risk_portfolio = {"exact": 25, "partial": 5, "brand": 3, "generic": 2}
    risk, level = analyzer._calculate_risk(high_risk_portfolio)
    
    assert risk > 0.6
    assert level == "high"
    
    # Test diversity calculation
    equal_portfolio = {"exact": 10, "partial": 10, "brand": 10, "generic": 10}
    diverse_ratios = {k: v/40 for k, v in equal_portfolio.items()}
    diversity = analyzer._calculate_diversity(diverse_ratios)
    
    assert diversity > 0.8  # High diversity for equal distribution


@pytest.mark.asyncio
async def test_schema_compliance():
    """Test that outputs match declared schemas."""
    # Test entity graph
    graph_result = await call_tool("features.entity_graph", {
        "seed_terms": ["test"]
    })
    graph_data = json.loads(graph_result[0].text)
    
    # Validate node structure
    for node in graph_data["nodes"]:
        assert "id" in node
        assert "label" in node
        assert "type" in node
        assert "weight" in node
        assert node["type"] in ["seed", "primary", "secondary", "related"]
    
    # Validate edge structure
    for edge in graph_data["edges"]:
        assert "source" in edge
        assert "target" in edge
        assert "weight" in edge
        assert "type" in edge
        assert edge["type"] in ["semantic", "hierarchical", "associative", "causal", "related"]
    
    # Test portfolio recalc
    portfolio_result = await call_tool("features.anchor_portfolio.recalc", {
        "target_domain": "test.com"
    })
    portfolio_data = json.loads(portfolio_result[0].text)
    
    # Validate required fields
    required_fields = ["target_domain", "new_mix", "new_risk", "risk_level", "delta"]
    for field in required_fields:
        assert field in portfolio_data
