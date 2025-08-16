"""
CEO and CTO Search Demo
=======================

Direct search for CEOs and CTOs with location filtering as requested by user
"""

import asyncio
from linkedin_people_search_scraper import LinkedInPeopleSearchScraper

async def search_ceo_cto():
    """Search for CEOs and CTOs with location filtering"""
    
    print("🎯 SEARCHING FOR CEOs AND CTOs")
    print("=" * 40)
    
    # Initialize scraper
    scraper = LinkedInPeopleSearchScraper()
    
    try:
        # Define search parameters for CEOs and CTOs
        search_config = {
            'job_titles': [
                'Chief Executive Officer',
                'CEO', 
                'Chief Technology Officer',
                'CTO',
                'Founder & CEO',
                'Co-Founder & CEO',
                'Founder & CTO',
                'Co-Founder & CTO'
            ],
            'locations': [
                'United States',
                'United Kingdom', 
                'San Francisco Bay Area',
                'New York',
                'London',
                'Silicon Valley'
            ],
            'max_profiles': 25,
            'pages': 2
        }
        
        print(f"📍 Searching in locations: {', '.join(search_config['locations'][:3])}...")
        print(f"💼 Job titles: {', '.join(search_config['job_titles'][:4])}...")
        print(f"📊 Target: {search_config['max_profiles']} profiles, {search_config['pages']} pages")
        print("-" * 50)
        
        # Run the search
        results = await scraper.run_executive_search(
            job_titles=search_config['job_titles'],
            locations=search_config['locations'],
            max_profiles=search_config['max_profiles'],
            pages_to_scrape=search_config['pages']
        )
        
        if results and len(results) > 0:
            print(f"\n✅ SUCCESS! Found {len(results)} executives:")
            print("=" * 50)
            
            # Display results
            for i, profile in enumerate(results[:10], 1):  # Show first 10
                print(f"\n{i}. {profile.get('name', 'N/A')}")
                print(f"   🏢 {profile.get('company', 'N/A')}")
                print(f"   💼 {profile.get('title', 'N/A')}")
                print(f"   📍 {profile.get('location', 'N/A')}")
                print(f"   🔗 {profile.get('linkedin_url', 'N/A')}")
            
            if len(results) > 10:
                print(f"\n... and {len(results) - 10} more profiles")
                
            # Show data categories
            print(f"\n📊 DATA EXTRACTED:")
            print("-" * 30)
            if results:
                sample = results[0]
                for key in sample.keys():
                    print(f"• {key}")
                    
        else:
            print("\n❌ No profiles found. This could be due to:")
            print("• LinkedIn selector changes")
            print("• Network issues")
            print("• Search parameters too specific")
            print("• Account restrictions")
            
    except Exception as e:
        print(f"\n❌ Error during search: {str(e)}")
        print("This could be due to LinkedIn UI changes or network issues")
        
    finally:
        # Close browser if it exists
        try:
            if hasattr(scraper, 'browser') and scraper.browser:
                await scraper.browser.close()
        except:
            pass

if __name__ == "__main__":
    print("🚀 Starting CEO/CTO Executive Search...")
    print("This will log into LinkedIn and search for executives")
    print("-" * 50)
    
    asyncio.run(search_ceo_cto())
