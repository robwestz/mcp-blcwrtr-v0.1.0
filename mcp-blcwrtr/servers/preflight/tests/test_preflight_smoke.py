"""
Smoke tests for Preflight MCP Server
"""

import json
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from uuid import uuid4

from src.server import list_tools, call_tool
from src.preflight_build import PreflightBuilder
from src.qc_validate import QCValidator


@pytest.mark.asyncio
async def test_list_tools():
    """Test that all tools are listed correctly."""
    tools = await list_tools()
    
    assert len(tools) == 2
    tool_names = [tool.name for tool in tools]
    
    assert "preflight.build" in tool_names
    assert "qc.validate" in tool_names


@pytest.mark.asyncio
async def test_preflight_build():
    """Test preflight matrix building."""
    order = {
        "order_ref": str(uuid4()),
        "customer_id": "cust_001",
        "publication_domain": "genline.se",
        "target_url": "https://happycasino.se/casino",
        "anchor_text": "casino",
        "topic": "Så undviker du falska ledtrådar i släktforskningen",
        "constraints": {
            "word_count": 800,
            "tone": "informativ",
            "compliance": ["gambling"]
        }
    }
    
    result = await call_tool("preflight.build", {"order": order})
    
    assert len(result) == 1
    data = json.loads(result[0].text)
    
    # Check structure
    assert "preflight_matrix" in data
    assert "writer_prompt" in data
    assert "validation" in data
    
    # Check preflight matrix
    matrix = data["preflight_matrix"]
    assert matrix["order_ref"] == order["order_ref"]
    assert matrix["publication_domain"] == order["publication_domain"]
    assert matrix["target_url"] == order["target_url"]
    assert matrix["anchor_plan"]["primary"] == order["anchor_text"]
    
    # Check required fields
    assert "query_or_cluster" in matrix
    assert "intents" in matrix
    assert "target_entities" in matrix
    assert "publication_entities" in matrix
    assert "candidate_midpoints" in matrix
    assert "chosen_midpoint" in matrix
    assert "lsi_near_window" in matrix
    assert "trust" in matrix
    assert "guards" in matrix
    
    # Check LSI terms
    assert len(matrix["lsi_near_window"]["terms"]) >= 6
    assert matrix["lsi_near_window"]["policy"]["min"] == 6
    assert matrix["lsi_near_window"]["policy"]["max"] == 10
    
    # Check trust sources
    assert len(matrix["trust"]) >= 1
    assert all("domain" in t and "level" in t and "rationale" in t for t in matrix["trust"])
    
    # Check guards
    assert matrix["guards"]["no_anchor_in_headers"] is True
    assert matrix["guards"]["competitor_block"] is True
    assert "gambling" in matrix["guards"]["compliance"]
    
    # Check writer prompt
    assert len(data["writer_prompt"]) > 100
    assert order["topic"] in data["writer_prompt"]
    assert order["anchor_text"] in data["writer_prompt"]


@pytest.mark.asyncio
async def test_qc_validate_approved():
    """Test QC validation with approved article."""
    article_text = """
## Introduktion till släktforskning

Släktforskning är en fascinerande hobby som låter oss utforska våra rötter och förstå vår historia.
Men som med all forskning kan det vara lätt att gå vilse i falska spår.

## Vanliga misstag och hur du undviker dem

En av de största utmaningarna inom släktforskning är att verifiera källor och undvika felaktiga
antaganden. Här kommer några konkreta tips för att hålla din forskning på rätt spår.

## Pausunderhållning när forskningen blir intensiv

När du spenderat timmar med att granska gamla kyrkoböcker och arkivdokument kan det vara skönt
med en paus. Forskning kräver fokus och koncentration, och ibland behöver hjärnan lite avkoppling.
För vissa kan [[casino]] vara ett sätt att koppla bort tankarna en stund. Denna digitala form
av underhållning erbjuder en helt annan typ av mental stimulans. Online-plattformar ger möjlighet
till kortare pausaktiviteter mellan forskningssessionerna.

*Spela ansvarsfullt. Läs mer om spelansvar på spelpaus.se. 18+ årsgräns.*

## Källkritik och verifiering

Enligt Riksarkivet är det viktigt att alltid dubbelkolla information från flera källor.
Detta gäller särskilt när du arbetar med äldre dokument där handstilen kan vara svårtolkad.

## Sammanfattning

Släktforskning kräver tålamod, noggrannhet och en kritisk blick. Genom att undvika vanliga
fallgropar och ta regelbundna pauser kan du göra din forskning både mer effektiv och njutbar.
"""
    
    result = await call_tool("qc.validate", {
        "article_text": article_text
    })
    
    assert len(result) == 1
    data = json.loads(result[0].text)
    
    # Check structure
    assert "status" in data
    assert "score" in data
    assert "breakdown" in data
    assert "issues" in data
    assert "recommendations" in data
    
    # Should pass basic validation
    assert data["score"] > 70  # At least LIGHT_EDITS level


@pytest.mark.asyncio
async def test_qc_validate_with_preflight():
    """Test QC validation with preflight matrix context."""
    # First build a preflight matrix
    order = {
        "order_ref": str(uuid4()),
        "customer_id": "cust_001",
        "publication_domain": "genline.se",
        "target_url": "https://happycasino.se/casino",
        "anchor_text": "casino online",
        "topic": "Digital släktforskning",
        "constraints": {"compliance": ["gambling"]}
    }
    
    preflight_result = await call_tool("preflight.build", {"order": order})
    preflight_data = json.loads(preflight_result[0].text)
    preflight_matrix = preflight_data["preflight_matrix"]
    
    # Article with correct anchor
    article_text = f"""
## Digital släktforskning

Modern teknik har revolutionerat släktforskningen.

## Online-resurser

När du tar en paus från forskningen kan [[{order["anchor_text"]}]] vara avkopplande.

*Spela ansvarsfullt. 18+ årsgräns.*
"""
    
    result = await call_tool("qc.validate", {
        "article_text": article_text,
        "preflight_matrix": preflight_matrix
    })
    
    data = json.loads(result[0].text)
    
    # Should detect the matching anchor
    anchor_issues = [i for i in data["issues"] if i["category"] == "anchor"]
    missing_anchor_issues = [i for i in anchor_issues if i["code"] == "MISSING_PRIMARY_ANCHOR"]
    assert len(missing_anchor_issues) == 0


@pytest.mark.asyncio
async def test_qc_validate_blocked():
    """Test QC validation with critical issues."""
    article_text = """
## [[Casino]] - En guide

Detta är en artikel utan mycket innehåll och med länk i rubrik.
"""
    
    result = await call_tool("qc.validate", {
        "article_text": article_text
    })
    
    data = json.loads(result[0].text)
    
    # Should be blocked due to anchor in header
    assert data["status"] == "BLOCKED"
    assert any(i["code"] == "ANCHOR_IN_HEADER" for i in data["issues"])


@pytest.mark.asyncio
async def test_qc_validate_compliance():
    """Test compliance validation."""
    preflight_matrix = {
        "anchor_plan": {"primary": "spel online"},
        "guards": {"compliance": ["gambling"]},
        "lsi_near_window": {"terms": [], "policy": {"min": 6, "max": 10, "radius_sentences": 2}},
        "trust": []
    }
    
    # Article without disclaimer
    article_text = """
## Test artikel

Här kan du hitta [[spel online]] för underhållning.
"""
    
    result = await call_tool("qc.validate", {
        "article_text": article_text,
        "preflight_matrix": preflight_matrix
    })
    
    data = json.loads(result[0].text)
    
    # Should detect missing disclaimer
    compliance_issues = [i for i in data["issues"] if i["category"] == "compliance"]
    assert len(compliance_issues) > 0
    assert any("disclaimer" in i["message"].lower() for i in compliance_issues)


def test_preflight_builder_helpers():
    """Test PreflightBuilder helper methods."""
    builder = PreflightBuilder()
    
    # Test query extraction
    query = builder._extract_query_cluster("Så undviker du falska ledtrådar i släktforskningen")
    assert len(query) > 0
    assert "undviker" in query or "falska" in query
    
    # Test intent detection
    intents = builder._detect_intents("Guide till släktforskning", "https://example.com")
    assert "informational" in intents
    
    # Test entity extraction
    entities = builder._extract_entities("genline.se", "släktforskning tips")
    assert len(entities) > 0
    assert any("släkt" in e.lower() for e in entities)


def test_qc_validator_helpers():
    """Test QCValidator helper methods."""
    validator = QCValidator()
    
    # Test sentence splitting
    sentences = validator._split_sentences("Detta är mening ett. Här kommer mening två! Och en tredje?")
    assert len(sentences) == 3
    
    # Test article parsing
    article_text = """## Rubrik 1

Första paragrafen med [[en länk]] i texten.

## Rubrik 2

Andra paragrafen utan länkar."""
    
    parsed = validator._parse_article(article_text)
    assert len(parsed["sections"]) == 2
    assert len(parsed["links"]) == 1
    assert parsed["links"][0]["text"] == "en länk"


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling for invalid inputs."""
    # Test with missing required fields
    result = await call_tool("preflight.build", {"order": {}})
    
    data = json.loads(result[0].text)
    assert "error" in data
    assert data["error"]["code"] == "ERR_TOOL_INTERNAL"
    
    # Test with invalid tool
    result = await call_tool("invalid.tool", {})
    
    data = json.loads(result[0].text)
    assert "error" in data
    assert "Unknown tool" in data["error"]["message"]


@pytest.mark.asyncio
async def test_auto_fix():
    """Test auto-fix functionality."""
    preflight_matrix = {
        "anchor_plan": {"primary": "casino"},
        "guards": {"compliance": ["gambling"]},
        "lsi_near_window": {"terms": [], "policy": {"min": 6, "max": 10, "radius_sentences": 2}},
        "trust": []
    }
    
    # Article missing gambling disclaimer
    article_text = """
## Test

Besök [[casino]] för underhållning.
"""
    
    result = await call_tool("qc.validate", {
        "article_text": article_text,
        "preflight_matrix": preflight_matrix,
        "auto_fix": True
    })
    
    data = json.loads(result[0].text)
    
    # Should have attempted fixes
    assert "auto_fixes" in data
    if data["auto_fixes"]:
        assert any(fix["type"] == "add_disclaimer" for fix in data["auto_fixes"])
