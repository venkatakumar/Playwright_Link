"""
CIO Search - Chief Information Officers
======================================

Dedicated search for CIOs and IT Directors with location filtering
"""

import asyncio
import json
from datetime import datetime
from linkedin_people_search_scraper import LinkedInPeopleSearchScraper
from people_search_config import EXECUTIVE_TITLES, LOCATIONS

async def search_cios():
    """Search for Chief Information Officers"""
    
    print("💻 CIO SEARCH - Chief Information Officers")
    print("=" * 45)
    
    # CIO job titles
    cio_titles = EXECUTIVE_TITLES['cio_it']
    print(f"💼 Searching for: {', '.join(cio_titles[:4])}...")
    print(f"📊 Total job titles: {len(cio_titles)}")
    
    # Target locations
    target_locations = LOCATIONS['usa'] + LOCATIONS['uk'] + LOCATIONS['europe'][:4]
    print(f"📍 Locations: {len(target_locations)} cities")
    print(f"🌍 Regions: USA, UK, Europe")
    print("-" * 50)
    
    scraper = LinkedInPeopleSearchScraper()
    
    try:
        results = await scraper.run_executive_search(
            job_titles=cio_titles,
            locations=target_locations,
            max_profiles=25,
            pages_to_scrape=2
        )
        
        if results and len(results) > 0:
            print(f"\n✅ SUCCESS! Found {len(results)} CIOs:")
            print("=" * 40)
            
            # Display results
            for i, profile in enumerate(results[:10], 1):
                print(f"\n{i}. {profile.get('name', 'N/A')}")
                print(f"   💼 {profile.get('title', 'N/A')}")
                print(f"   🏢 {profile.get('company', 'N/A')}")
                print(f"   📍 {profile.get('location', 'N/A')}")
                print(f"   🔗 {profile.get('linkedin_url', 'N/A')}")
            
            if len(results) > 10:
                print(f"\n... and {len(results) - 10} more CIOs")
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'output/cios_{timestamp}.json'
            
            import os
            os.makedirs('output', exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n💾 Saved {len(results)} CIO profiles to {filename}")
            
        else:
            print("\n❌ No CIO profiles found")
            
    except Exception as e:
        print(f"\n❌ Error during CIO search: {str(e)}")
        
    finally:
        try:
            if hasattr(scraper, 'browser') and scraper.browser:
                await scraper.browser.close()
        except:
            pass

if __name__ == "__main__":
    print("🚀 Starting CIO Search...")
    asyncio.run(search_cios())
