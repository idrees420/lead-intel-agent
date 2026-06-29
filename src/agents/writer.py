import os
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

class WriterAgent:
    """The Secretary - Crafts personalized outreach emails"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.5,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
    
    async def draft_email(self, company_name: str, research_summary: str, 
                          research_notes: str, target_role: str = "CEO") -> Dict[str, str]:
        """
        Draft a personalized cold email based on research findings
        """
        try:
            system_prompt = """You are an expert B2B sales copywriter. Your emails are:
            - Professional and concise
            - Highly personalized based on specific company challenges
            - Focused on value proposition
            - Never generic or templated
            - Maximum 150 words
            - Include a clear call to action
            
            Format the email with:
            Subject: [subject line]
            
            Dear [Name],
            
            [Email body]
            
            Best regards,
            [Your name]"""
            
            user_message = f"""Write a cold email to the {target_role} of {company_name} based on this research:
            
            Research Summary:
            {research_summary}
            
            Detailed Research:
            {research_notes}
            
            The email should:
            1. Reference one specific challenge they're facing from the research
            2. Briefly introduce how our solution could help address this
            3. End with a soft call to action (e.g., brief 15-minute chat)
            
            Do not use placeholders like [Your Company] - instead use "we" and "our solution".
            Make it sound natural and human, not like a template.
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ])
            
            # Extract subject and body
            email_content = response.content
            subject = await self._generate_subject(company_name, research_summary)
            
            return {
                "email_draft": email_content,
                "email_subject": subject,
                "email_status": "drafted"
            }
            
        except Exception as e:
            print(f"Email drafting failed: {str(e)}")
            return {
                "error_message": f"Email drafting failed: {str(e)}",
                "email_status": "failed"
            }
    
    async def _generate_subject(self, company_name: str, research_summary: str) -> str:
        """Generate a compelling email subject line"""
        
        system_prompt = "Create a compelling email subject line that mentions the company name and hints at solving a specific challenge. Keep it under 60 characters. Return ONLY the subject line, nothing else."
        
        user_message = f"Based on this research about {company_name}: {research_summary[:200]}"
        
        response = await self.llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        
        return response.content.strip()