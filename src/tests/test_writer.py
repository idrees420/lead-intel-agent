import pytest
import asyncio
from src.agents.writer import WriterAgent

@pytest.mark.asyncio
async def test_draft_email():
    """Test email drafting"""
    writer = WriterAgent()
    
    result = await writer.draft_email(
        company_name="Tesla",
        research_summary="Tesla faces battery supply chain issues and increasing competition.",
        research_notes="Detailed notes about Tesla's challenges..."
    )
    
    assert result is not None
    assert "email_draft"