"""
Simple Executive Search Test
===========================
"""

import asyncio
from linkedin_people_search_scraper import LinkedInPeopleSearchScraper

async def test_executive_search():
    print("🎯 TESTING EXECUTIVE SEARCH")
    print("=" * 40)
    
    scraper = LinkedInPeopleSearchScraper()
    
    # Test search for CEOs
    print("\\n🔍 Searching for CEOs in London...")
    
    try:
        profiles = await scraper.run_executive_search(
            job_titles=["CEO", "Chief Executive Officer"],
            locations=["London"], 
            max_profiles=10,
            pages_to_scrape=2
        )
        
        if profiles:
            print(f"✅ Found {len(profiles)} profiles!")
            print("\\nSample results:")
            for i, profile in enumerate(profiles[:3]):
                name = profile.get('name', 'Unknown')
                title = profile.get('job_title', 'Unknown')
                company = profile.get('company', 'Unknown')
                print(f"  {i+1}. {name}")
                print(f"     Title: {title}")
                print(f"     Company: {company}")
                print()
        else:
            print("❌ No profiles found")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_executive_search())
