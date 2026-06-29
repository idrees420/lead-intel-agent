import os
from typing import Dict, Any, List
from datetime import datetime
from tavily import TavilyClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv
import json
import asyncio

load_dotenv()

class ResearcherAgent:
    """The Detective - Researches company challenges and pain points"""
    
    def __init__(self):
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.3,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        self.max_search_results = int(os.getenv("MAX_SEARCH_RESULTS", 5))
    
    async def research_company(self, company_name: str, target_industry: str = None) -> Dict[str, Any]:
        """
        Perform deep-dive research on a company
        """
        try:
            print(f"Researching {company_name}...")
            
            # Step 1: Search for recent news and challenges
            search_queries = self._generate_search_queries(company_name, target_industry)
            all_results = []
            
            for query in search_queries:
                print(f"  Searching: {query}")
                results = self.tavily_client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=self.max_search_results,
                    include_raw_content=True
                )
                all_results.extend(results.get("results", []))
            
            print(f"  Found {len(all_results)} results")
            
            # Step 2: Synthesize the research
            print("  Synthesizing research...")
            synthesis = await self._synthesize_research(company_name, all_results)
            
            # Step 3: Create structured research notes
            research_notes = {
                "company_name": company_name,
                "research_timestamp": datetime.now().isoformat(),
                "key_findings": synthesis["key_findings"],
                "pain_points": synthesis["pain_points"],
                "recent_developments": synthesis["recent_developments"],
                "market_position": synthesis["market_position"],
                "sources": [r.get("url") for r in all_results if r.get("url")][:10]
            }
            
            # Step 4: Create a sharp two-point summary
            print("  Creating summary...")
            summary = await self._create_summary(company_name, research_notes)
            
            print("Research complete!")
            
            # Format research notes into markdown for the UI
            md_notes = f"### 🏢 {company_name}\n\n"
            if research_notes['key_findings']:
                md_notes += "#### 🔑 Key Findings\n" + "\n".join([f"- {x}" for x in research_notes['key_findings']]) + "\n\n"
            if research_notes['pain_points']:
                md_notes += "#### ⚠️ Pain Points\n" + "\n".join([f"- {x}" for x in research_notes['pain_points']]) + "\n\n"
            if research_notes['recent_developments']:
                md_notes += "#### 📈 Recent Developments\n" + "\n".join([f"- {x}" for x in research_notes['recent_developments']]) + "\n\n"
            if research_notes['market_position']:
                md_notes += "#### 🎯 Market Position\n" + str(research_notes['market_position']) + "\n\n"
            if research_notes['sources']:
                md_notes += "#### 🔗 Sources\n" + "\n".join([f"- [{x}]({x})" for x in set(research_notes['sources'])])
            
            return {
                "research_notes": md_notes,
                "research_summary": summary,
                "research_sources": research_notes["sources"],
                "research_timestamp": datetime.now(),
                "research_status": "completed",
                "raw_data": all_results
            }
            
        except Exception as e:
            print(f"Research failed: {str(e)}")
            return {
                "error_message": f"Research failed: {str(e)}",
                "research_status": "failed"
            }
    
    def _generate_search_queries(self, company_name: str, industry: str = None) -> List[str]:
        """Generate targeted search queries"""
        base_queries = [
            f"{company_name} business challenges 2024",
            f"{company_name} recent news financial performance",
            f"{company_name} strategic initiatives",
            f"{company_name} market position competitors",
        ]
        
        if industry:
            base_queries.append(f"{industry} industry challenges {company_name}")
        
        return base_queries
    
    async def _synthesize_research(self, company_name: str, results: List[Dict]) -> Dict[str, Any]:
        """Use LLM to synthesize research findings"""
        
        system_prompt = """You are a senior business analyst specializing in B2B sales intelligence.
        Analyze the provided search results and extract:
        1. Key business challenges the company is facing
        2. Recent developments or changes
        3. Strategic priorities
        4. Market position and competitive landscape
        
        Be specific and cite your sources.
        
        Format your response with clear sections:
        
        Key Findings:
        - Finding 1
        - Finding 2
        
        Pain Points:
        - Pain point 1
        - Pain point 2
        
        Recent Developments:
        - Development 1
        - Development 2
        
        Market Position:
        [Description of market position]
        """
        
        # Prepare context from results
        context = "\n\n".join([
            f"Source {i+1}: {r.get('title', 'No title')}\n{r.get('content', 'No content')}"
            for i, r in enumerate(results[:10])
        ])
        
        user_message = f"""Based on these search results about {company_name}, provide a synthesized analysis:
        
        {context}
        """
        
        response = await self.llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        
        # Parse the response
        return self._parse_synthesis(response.content)
    
    def _parse_synthesis(self, content: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        sections = {
            "key_findings": [],
            "pain_points": [],
            "recent_developments": [],
            "market_position": ""
        }
        
        current_section = None
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            line_lower = line.lower()
            
            if 'key findings' in line_lower or 'key findings:' in line_lower:
                current_section = "key_findings"
            elif 'pain points' in line_lower or 'pain points:' in line_lower:
                current_section = "pain_points"
            elif 'recent developments' in line_lower or 'recent developments:' in line_lower:
                current_section = "recent_developments"
            elif 'market position' in line_lower or 'market position:' in line_lower:
                current_section = "market_position"
            elif current_section:
                if current_section == "market_position":
                    sections[current_section] += line + " "
                elif line.startswith('-') or line.startswith('*') or line[0].isdigit() or line.startswith('•'):
                    # Remove the bullet/number and add to list
                    clean_line = line.lstrip('-*0123456789.• ').strip()
                    if clean_line:
                        sections[current_section].append(clean_line)
        
        # Clean up market position
        if isinstance(sections["market_position"], str):
            sections["market_position"] = sections["market_position"].strip()
        
        return sections
    
    async def _create_summary(self, company_name: str, research_notes: Dict) -> str:
        """Create a sharp two-point summary of the biggest hurdles"""
        
        system_prompt = """You are a sales intelligence expert. Create a concise, impactful summary 
        of the company's biggest business challenges. Focus on 2-3 key points that would be most 
        relevant for a sales conversation.
        
        Format your response as:
        
        Challenge 1: [Title]
        [1-2 sentences explaining the challenge]
        
        Challenge 2: [Title]
        [1-2 sentences explaining the challenge]
        
        Challenge 3: [Title] (optional)
        [1-2 sentences explaining the challenge]
        """
        
        user_message = f"""Based on this research about {company_name}, create a sharp summary 
        of their biggest challenges and pain points:
        
        {json.dumps(research_notes, indent=2)}
        """
        
        response = await self.llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        
        return response.content