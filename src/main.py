#!/usr/bin/env python3
"""
Lead-Intel Agent - Automated B2B Sales Prospecting System
Main entry point for the application
"""

import asyncio
import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.graph import LeadIntelGraph
from src.utils.validators import validate_company_name

# Load environment variables
load_dotenv()

async def main():
    """Main entry point"""
    
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="Lead-Intel Agent - Automated B2B Sales Prospecting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py "Tesla"
  python src/main.py "Microsoft" --industry "Cloud Computing"
  python src/main.py "Apple" --max-attempts 5
        """
    )
    
    parser.add_argument(
        "company",
        type=str,
        help="Name of the company to research"
    )
    
    parser.add_argument(
        "--industry",
        type=str,
        help="Target industry (optional)",
        default=None
    )
    
    parser.add_argument(
        "--max-attempts",
        type=int,
        help="Maximum review attempts (default: 3)",
        default=3
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Lead-Intel Agent 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not validate_company_name(args.company):
        print("❌ Error: Invalid company name format")
        print("Company name should contain only letters, numbers, spaces, &, -, .")
        sys.exit(1)
    
    # Check API keys
    if not os.getenv("MISTRAL_API_KEY"):
        print("❌ Error: MISTRAL_API_KEY not found in .env file")
        sys.exit(1)
    
    if not os.getenv("TAVILY_API_KEY"):
        print("❌ Error: TAVILY_API_KEY not found in .env file")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🤖 LEAD-INTEL AGENT - B2B Sales Intelligence")
    print("="*60)
    print(f"\n🎯 Target: {args.company}")
    if args.industry:
        print(f"🏭 Industry: {args.industry}")
    print(f"🔄 Max Review Attempts: {args.max_attempts}")
    print("\n🚀 Starting research workflow...\n")
    
    try:
        # Initialize and run the graph
        agent = LeadIntelGraph()
        result = await agent.run(
            company_name=args.company,
            target_industry=args.industry,
            max_review_attempts=args.max_attempts
        )
        
        print("\n" + "="*60)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"\n📊 Session ID: {result['session_id']}")
        print(f"📝 Status: {result.get('email_status', 'completed')}")
        
        # Save final output to file
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{args.company.replace(' ', '_')}_{result['session_id'][:8]}.txt"
        
        with open(output_file, 'w') as f:
            f.write(f"Company: {args.company}\n")
            f.write(f"Session ID: {result['session_id']}\n")
            f.write(f"Generated: {result['updated_at']}\n\n")
            f.write("="*50 + "\n")
            f.write("RESEARCH SUMMARY\n")
            f.write("="*50 + "\n")
            f.write(result['research_summary'])
            f.write("\n\n" + "="*50 + "\n")
            f.write("GENERATED EMAIL\n")
            f.write("="*50 + "\n")
            f.write(f"Subject: {result['email_subject']}\n\n")
            f.write(result['email_draft'])
        
        print(f"\n💾 Output saved to: {output_file}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Workflow interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())