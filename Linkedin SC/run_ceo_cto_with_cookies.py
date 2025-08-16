"""
CEO & CTO Search with Cookie Authentication
==========================================

Run CEO and CTO search using stored cookies
"""

import asyncio
from cookie_enhanced_scraper import CookieEnhancedLinkedInScraper

async def run_ceo_cto_search():
    print('🎯 CEO & CTO SEARCH WITH COOKIE AUTHENTICATION')
    print('=' * 50)
    
    # Initialize cookie-enhanced scraper
    scraper = CookieEnhancedLinkedInScraper(headless=False)
    
    try:
        # Ensure logged in with cookies
        await scraper.ensure_logged_in()
        
        # Search configuration for CEOs and CTOs
        search_config = {
            'job_titles': [
                'Chief Executive Officer',
                'CEO', 
                'Chief Technology Officer',
                'CTO',
                'Founder & CEO',
                'Co-Founder & CEO',
                'Founder & CTO',
                'Co-Founder & CTO',
                'Executive Director',
                'Managing Director'
            ],
            'locations': [
                'United States',
                'United Kingdom', 
                'San Francisco Bay Area',
                'New York',
                'London',
                'Silicon Valley',
                'Boston',
                'Seattle'
            ],
            'max_profiles': 30,
            'pages': 3
        }
        
        print(f'📍 Locations: {len(search_config["locations"])} regions')
        print(f'💼 Job Titles: {len(search_config["job_titles"])} variations')
        print(f'📊 Target: {search_config["max_profiles"]} profiles, {search_config["pages"]} pages')
        print('-' * 50)
        
        # Run the search
        results = await scraper.run_executive_search_with_cookies(search_config)
        
        if results:
            print(f'✅ SUCCESS: Found {len(results)} CEO/CTO profiles!')
            print(f'📁 Results saved to output directory')
            
            # Show sample of results
            print('\n📋 SAMPLE RESULTS:')
            for i, profile in enumerate(results[:5]):
                print(f'{i+1}. {profile.get("name", "N/A")} - {profile.get("title", "N/A")}')
                if profile.get('company'):
                    print(f'   🏢 {profile["company"]}')
                if profile.get('location'):
                    print(f'   📍 {profile["location"]}')
                print()
        else:
            print('❌ No results found')
            
    except Exception as e:
        print(f'❌ Error: {str(e)}')
    finally:
        if hasattr(scraper, 'browser') and scraper.browser:
            await scraper.browser.close()

if __name__ == "__main__":
    # Run the search
    asyncio.run(run_ceo_cto_search())
