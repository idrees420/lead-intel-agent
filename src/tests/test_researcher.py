import pytest
import asyncio
from src.agents.researcher import ResearcherAgent

@pytest.mark.asyncio
async def test_research_company():
    """Test the researcher agent"""
    researcher = ResearcherAgent()
    result = await researcher.research_company("Microsoft")
    
    assert result is not None
    assert "research_notes" in result
    assert "research_summary" in result
    assert "research_sources" in result

def test_generate_search_queries():
    """Test search query generation"""
    researcher = ResearcherAgent()
    queries = researcher._generate_search_queries("Tesla", "Automotive")
    
    assert len(queries) > 0
    assert any("Tesla" in q for q in queries)