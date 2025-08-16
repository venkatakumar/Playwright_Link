"""
CFO Search - Chief Financial Officers
====================================

Dedicated search for CFOs and Finance Directors with location filtering
"""

import asyncio
import json
from datetime import datetime
from linkedin_people_search_scraper import LinkedInPeopleSearchScraper
from people_search_config import EXECUTIVE_TITLES, LOCATIONS

async def search_cfos():
    """Search for Chief Financial Officers"""
    
    print("💰 CFO SEARCH - Chief Financial Officers")
    print("=" * 45)
    
    # CFO job titles
    cfo_titles = EXECUTIVE_TITLES['cfo_finance']
    print(f"💼 Searching for: {', '.join(cfo_titles[:4])}...")
    print(f"📊 Total job titles: {len(cfo_titles)}")
    
    # Target locations
    target_locations = LOCATIONS['usa'] + LOCATIONS['uk'] + LOCATIONS['europe'][:3]
    print(f"📍 Locations: {len(target_locations)} cities")
    print(f"🌍 Regions: USA, UK, Europe")
    print("-" * 50)
    
    scraper = LinkedInPeopleSearchScraper()
    
    try:
        results = await scraper.run_executive_search(
            job_titles=cfo_titles,
            locations=target_locations,
            max_profiles=25,
            pages_to_scrape=2
        )
        
        if results and len(results) > 0:
            print(f"\n✅ SUCCESS! Found {len(results)} CFOs:")
            print("=" * 40)
            
            # Display results
            for i, profile in enumerate(results[:10], 1):
                print(f"\n{i}. {profile.get('name', 'N/A')}")
                print(f"   💼 {profile.get('title', 'N/A')}")
                print(f"   🏢 {profile.get('company', 'N/A')}")
                print(f"   📍 {profile.get('location', 'N/A')}")
                print(f"   🔗 {profile.get('linkedin_url', 'N/A')}")
            
            if len(results) > 10:
                print(f"\n... and {len(results) - 10} more CFOs")
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'output/cfos_{timestamp}.json'
            
            import os
            os.makedirs('output', exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n💾 Saved {len(results)} CFO profiles to {filename}")
            
        else:
            print("\n❌ No CFO profiles found")
            
    except Exception as e:
        print(f"\n❌ Error during CFO search: {str(e)}")
        
    finally:
        try:
            if hasattr(scraper, 'browser') and scraper.browser:
                await scraper.browser.close()
        except:
            pass

if __name__ == "__main__":
    print("🚀 Starting CFO Search...")
    asyncio.run(search_cfos())
