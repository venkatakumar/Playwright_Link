"""
CEO & CTO Search with Cookie Authentication
==========================================

Run CEO and CTO search using stored cookies
"""

import asyncio
import sys
import os
import re
from cookie_enhanced_scraper import CookieEnhancedLinkedInScraper

async def run_ceo_cto_search():
    print('🎯 CEO & CTO SEARCH WITH COOKIE AUTHENTICATION')
    print('=' * 50)
    
    # Initialize cookie-enhanced scraper
    scraper = CookieEnhancedLinkedInScraper(headless=False)
    
    try:
        # Ensure logged in with cookies
        await scraper.ensure_logged_in()
        
        # Parse industries from env (LINKEDIN_INDUSTRIES), default to Financial Services & Insurance
        env_inds = os.getenv('LINKEDIN_INDUSTRIES', '').strip()
        industries = [s.strip() for s in re.split(r'[;,]', env_inds) if s.strip()] or [
            'Financial Services', 'Insurance'
        ]

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
                'United Kingdom'
            ],
            # UK region facet for precise filtering
            'geo_urns': ['101165590'],
            'industries': industries,
            'max_profiles': 30,
            'pages': 3
        }
        
        print(f'📍 Locations: {len(search_config["locations"])} regions')
        print(f'💼 Job Titles: {len(search_config["job_titles"])} variations')
        print(f'📊 Target: {search_config["max_profiles"]} profiles, {search_config["pages"]} pages')
        print(f'🏭 Industries: {", ".join(search_config["industries"]) if search_config["industries"] else "(none)"}')
        print('-' * 50)
        
        # Run the search (explicit params)
        results = await scraper.run_executive_search_with_cookies(
            job_titles=search_config['job_titles'],
            locations=search_config['locations'],
            max_profiles=search_config['max_profiles'],
            pages_to_scrape=search_config['pages'],
            geo_urns=search_config['geo_urns'],
            industries=search_config['industries']
        )
        
        if results:
            print(f'✅ SUCCESS: Found {len(results)} CEO/CTO profiles!')
            print(f'📁 Results saved to output directory')
            
            # Show sample of results
            print('\n📋 SAMPLE RESULTS:')
            for i, profile in enumerate(results[:5]):
                print(f'{i+1}. {profile.get("name", "N/A")} - {profile.get("current_role", "N/A")}')
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
        try:
            await scraper.shutdown()
        except Exception:
            pass

if __name__ == "__main__":
    # Use Selector policy on Windows to avoid unclosed transport warnings
    if sys.platform.startswith("win"):
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except Exception:
            pass
    asyncio.run(run_ceo_cto_search())
