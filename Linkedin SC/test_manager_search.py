"""
Test Manager Search - QA and Testing Leaders
===========================================

Dedicated search for Test Managers, Head of Testing, QA Managers with location filtering
"""

import asyncio
import json
from datetime import datetime
from linkedin_people_search_scraper import LinkedInPeopleSearchScraper
from people_search_config import EXECUTIVE_TITLES, LOCATIONS

async def search_test_managers():
    """Search for Test Managers and QA Leaders"""
    
    print("🧪 TEST MANAGER SEARCH - QA and Testing Leaders")
    print("=" * 50)
    
    # Test Manager job titles
    test_titles = EXECUTIVE_TITLES['test_qa']
    print(f"💼 Searching for: {', '.join(test_titles[:4])}...")
    print(f"📊 Total job titles: {len(test_titles)}")
    
    # Target locations
    target_locations = LOCATIONS['usa'] + LOCATIONS['uk'] + LOCATIONS['europe'][:3]
    print(f"📍 Locations: {len(target_locations)} cities")
    print(f"🌍 Regions: USA, UK, Europe")
    print("-" * 55)
    
    scraper = LinkedInPeopleSearchScraper()
    
    try:
        results = await scraper.run_executive_search(
            job_titles=test_titles,
            locations=target_locations,
            max_profiles=30,
            pages_to_scrape=3
        )
        
        if results and len(results) > 0:
            print(f"\n✅ SUCCESS! Found {len(results)} Test Managers/QA Leaders:")
            print("=" * 55)
            
            # Display results
            for i, profile in enumerate(results[:12], 1):
                print(f"\n{i:2d}. {profile.get('name', 'N/A')}")
                print(f"    💼 {profile.get('title', 'N/A')}")
                print(f"    🏢 {profile.get('company', 'N/A')}")
                print(f"    📍 {profile.get('location', 'N/A')}")
                print(f"    🔗 {profile.get('linkedin_url', 'N/A')}")
            
            if len(results) > 12:
                print(f"\n... and {len(results) - 12} more Test Managers")
            
            # Categorize by role type
            print(f"\n📊 ROLE BREAKDOWN:")
            print("-" * 20)
            role_counts = {}
            for profile in results:
                title = profile.get('title', '').lower()
                if 'test manager' in title:
                    role_counts['Test Managers'] = role_counts.get('Test Managers', 0) + 1
                elif 'head of testing' in title or 'testing director' in title:
                    role_counts['Testing Leaders'] = role_counts.get('Testing Leaders', 0) + 1
                elif 'qa manager' in title or 'quality assurance' in title:
                    role_counts['QA Managers'] = role_counts.get('QA Managers', 0) + 1
                elif 'automation' in title:
                    role_counts['Automation Leaders'] = role_counts.get('Automation Leaders', 0) + 1
                else:
                    role_counts['Other QA/Testing'] = role_counts.get('Other QA/Testing', 0) + 1
            
            for role_type, count in role_counts.items():
                print(f"• {role_type}: {count}")
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'output/test_managers_{timestamp}.json'
            
            import os
            os.makedirs('output', exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n💾 Saved {len(results)} Test Manager profiles to {filename}")
            
        else:
            print("\n❌ No Test Manager profiles found")
            
    except Exception as e:
        print(f"\n❌ Error during Test Manager search: {str(e)}")
        
    finally:
        try:
            if hasattr(scraper, 'browser') and scraper.browser:
                await scraper.browser.close()
        except:
            pass

if __name__ == "__main__":
    print("🚀 Starting Test Manager Search...")
    asyncio.run(search_test_managers())
