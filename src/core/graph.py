import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from src.core.state import LeadState, ResearchStatus
from src.agents.researcher import ResearcherAgent
from src.agents.writer import WriterAgent
from src.database.db_manager import DatabaseManager
import asyncio

class LeadIntelGraph:
    """Main workflow orchestration using LangGraph"""
    
    def __init__(self):
        self.researcher = ResearcherAgent()
        self.writer = WriterAgent()
        self.db = DatabaseManager()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        workflow = StateGraph(LeadState)
        
        # Add nodes
        workflow.add_node("research", self.research_node)
        workflow.add_node("review", self.review_node)
        workflow.add_node("write", self.write_node)
        # Remove refine node since we're not using it yet
        
        # Add edges
        workflow.set_entry_point("research")
        
        # Research -> Review
        workflow.add_edge("research", "review")
        
        # Conditional edges from review
        workflow.add_conditional_edges(
            "review",
            self.should_continue,
            {
                "approve": "write",  # If approved, go to write
                "reject": "research",  # If rejected, go back to research
                "max_attempts": END  # If max attempts reached, end
            }
        )
        
        # Write -> End
        workflow.add_edge("write", END)
        
        return workflow.compile()
    
    async def research_node(self, state: LeadState) -> LeadState:
        """Node: Perform research on the company"""
        print("\n🔬 Research Node: Gathering intelligence...")
        
        # Check if we have feedback for re-research
        if state.get("human_feedback"):
            print(f"📝 Re-researching based on feedback: {state['human_feedback']}")
            # You could incorporate feedback here
        
        research_result = await self.researcher.research_company(
            state["company_name"],
            state.get("target_industry")
        )
        
        # Update state
        new_state = state.copy()
        new_state.update({
            "research_notes": research_result.get("research_notes"),
            "research_summary": research_result.get("research_summary"),
            "research_sources": research_result.get("research_sources", []),
            "research_timestamp": research_result.get("research_timestamp", datetime.now()),
            "research_status": ResearchStatus.REVIEW_PENDING,
            "updated_at": datetime.now()
        })
        
        # Save to database
        self.db.save_research_state(state["session_id"], new_state)
        
        return new_state
    
    async def review_node(self, state: LeadState) -> LeadState:
        """Node: Pause for human review"""
        
        print("\n" + "="*50)
        print(f"📋 RESEARCH REVIEW FOR: {state['company_name']}")
        print("="*50)
        print("\n📊 Research Summary:")
        print(state["research_summary"])
        print("\n📝 Detailed Notes (first 500 chars):")
        print(state["research_notes"][:500] + "...")
        print("\n🔗 Top Sources:")
        for source in state["research_sources"][:3]:
            print(f"  • {source}")
        
        # This is a blocking call for human input
        while True:
            response = input("\n✅ Approve research? (yes/no): ").lower().strip()
            
            if response == 'yes':
                feedback = None
                break
            elif response == 'no':
                feedback = input("📝 Provide feedback for re-research: ")
                break
            else:
                print("⚠️ Please enter 'yes' or 'no'")
        
        # Update state based on feedback
        new_state = state.copy()
        new_state["human_feedback"] = feedback
        
        if feedback is None:
            new_state["research_status"] = ResearchStatus.APPROVED
            print("✅ Research approved! Moving to email generation...")
        else:
            new_state["research_status"] = ResearchStatus.REJECTED
            new_state["review_attempts"] = state.get("review_attempts", 0) + 1
            print(f"🔄 Research rejected. Attempt {new_state['review_attempts']} of {state.get('max_review_attempts', 3)}")
        
        new_state["updated_at"] = datetime.now()
        
        # Save review to database
        self.db.save_research_state(state["session_id"], new_state)
        
        return new_state
    
    def should_continue(self, state: LeadState) -> str:
        """Determine next step based on review"""
        
        if state["research_status"] == ResearchStatus.APPROVED:
            return "approve"
        elif state["research_status"] == ResearchStatus.REJECTED:
            if state.get("review_attempts", 0) >= state.get("max_review_attempts", 3):
                print(f"\n⚠️ Max review attempts ({state['max_review_attempts']}) reached. Exiting.")
                return "max_attempts"
            return "reject"
        else:
            return "reject"
    
    async def write_node(self, state: LeadState) -> LeadState:
        """Node: Write the email"""
        print("\n✍️ Writer Node: Crafting personalized email...")
        
        email_result = await self.writer.draft_email(
            state["company_name"],
            state["research_summary"],
            state["research_notes"]
        )
        
        # Update state
        new_state = state.copy()
        new_state.update({
            "email_draft": email_result.get("email_draft"),
            "email_subject": email_result.get("email_subject"),
            "email_status": email_result.get("email_status", "drafted"),
            "updated_at": datetime.now()
        })
        
        # Display the email
        print("\n" + "="*50)
        print("📧 GENERATED EMAIL")
        print("="*50)
        print(f"📌 Subject: {new_state['email_subject']}")
        print("\n📄 Body:")
        print(new_state["email_draft"])
        print("\n" + "="*50)
        
        # Save to database
        self.db.save_email_state(state["session_id"], new_state)
        
        return new_state
    
    async def run(self, company_name: str, target_industry: Optional[str] = None,
                  max_review_attempts: int = 3) -> Dict[str, Any]:
        """
        Run the complete lead intelligence workflow
        """
        
        # Initialize state
        initial_state: LeadState = {
            "company_name": company_name,
            "target_industry": target_industry,
            "research_notes": None,
            "research_summary": None,
            "research_sources": [],
            "research_timestamp": None,
            "research_status": ResearchStatus.PENDING,
            "human_feedback": None,
            "review_attempts": 0,
            "max_review_attempts": max_review_attempts,
            "email_draft": None,
            "email_subject": None,
            "email_status": "pending",
            "session_id": str(uuid.uuid4()),
            "error_message": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Save initial session
        self.db.save_session(
            initial_state["session_id"],
            company_name,
            target_industry
        )
        
        print(f"\n📋 Session ID: {initial_state['session_id']}")
        
        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        return final_state