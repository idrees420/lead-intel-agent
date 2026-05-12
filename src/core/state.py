from typing import TypedDict, List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ResearchStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    REVIEW_PENDING = "review_pending"
    REJECTED = "rejected"
    APPROVED = "approved"

class LeadState(TypedDict):
    """State management for the lead intelligence agent"""
    
    # Input
    company_name: str
    target_industry: Optional[str]
    
    # Research phase
    research_notes: Optional[str]
    research_summary: Optional[str]
    research_sources: List[str]
    research_timestamp: Optional[datetime]
    research_status: ResearchStatus
    
    # Human feedback
    human_feedback: Optional[str]
    review_attempts: int
    max_review_attempts: int
    
    # Email generation
    email_draft: Optional[str]
    email_subject: Optional[str]
    email_status: str
    
    # Metadata
    session_id: str
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    
class LeadStateInput(TypedDict):
    """Input schema for lead state"""
    company_name: str
    target_industry: Optional[str]
    max_review_attempts: Optional[int]