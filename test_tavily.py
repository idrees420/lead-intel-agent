import os
from dotenv import load_dotenv
from tavily import TavilyClient

# Load environment variables from .env file
load_dotenv()

def test_tavily():
    print("=" * 50)
    print("🔑 TESTING TAVILY API")
    print("=" * 50)
    
    # Get API key
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not tavily_key:
        print("❌ ERROR: Tavily API key not found in .env file")
        print("\nPlease check your .env file and make sure it contains:")
        print("TAVILY_API_KEY=your_key_here")
        return
    
    # Show key info (safely)
    print(f"✅ API Key found")
    print(f"   Key starts with: {tavily_key[:10]}...")
    print(f"   Key length: {len(tavily_key)} characters")
    
    try:
        # Initialize client
        print("\n🔄 Initializing Tavily client...")
        client = TavilyClient(api_key=tavily_key)
        print("✅ Client initialized successfully")
        
        # Try a simple search
        print("\n🔄 Performing test search...")
        print("   Query: 'Microsoft news 2024'")
        
        result = client.search(
            query="Microsoft news 2024",
            search_depth="basic",
            max_results=2
        )
        
        print("✅ Search successful!")
        
        # Show results
        results_list = result.get('results', [])
        print(f"\n📊 Found {len(results_list)} results")
        
        if results_list:
            print("\n📄 Sample results:")
            for i, item in enumerate(results_list[:2], 1):
                print(f"\n  Result {i}:")
                print(f"  Title: {item.get('title', 'N/A')}")
                print(f"  URL: {item.get('url', 'N/A')}")
                
        print("\n✅✅✅ TAVILY API IS WORKING CORRECTLY! ✅✅✅")
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}")
        print(f"   Details: {str(e)}")
        
        # Specific error handling
        if "401" in str(e):
            print("\n🔧 FIX: Your API key appears to be invalid or unauthorized.")
            print("   1. Go to https://app.tavily.com")
            print("   2. Check if your key is active")
            print("   3. Try generating a new key")
            print("   4. Update your .env file with the new key")
        elif "429" in str(e):
            print("\n🔧 FIX: Rate limit exceeded. Try again later.")
        elif "Connection" in str(e):
            print("\n🔧 FIX: Network issue. Check your internet connection.")

if __name__ == "__main__":
    test_tavily()