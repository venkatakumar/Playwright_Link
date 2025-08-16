"""
Simple CEO & CTO Search with Stored Cookies
==========================================

Quick search using established cookie authentication
"""

import asyncio
from cookie_enhanced_scraper import CookieEnhancedLinkedInScraper

async def simple_ceo_cto_search():
    """Simple search for CEOs and CTOs using stored authentication"""
    
    print("🎯 SIMPLE CEO & CTO SEARCH")
    print("=" * 35)
    
    # Initialize cookie-enhanced scraper (visible browser)
    scraper = CookieEnhancedLinkedInScraper(headless=False)
    
    try:
        # Ensure logged in with cookies
        print("🔐 Checking authentication...")
        login_success = await scraper.ensure_logged_in()
        
        if not login_success:
            print("❌ Authentication failed")
            return
            
        print("✅ Authentication successful!")
        
        # Define simple search parameters
        job_titles = [
            'CEO',
            'Chief Executive Officer', 
            'CTO',
            'Chief Technology Officer',
            'Founder',
            'Co-Founder'
        ]
        
        locations = [
            'United Kingdom'
        ]
        # Preferred native geo URN codes for better filtering (examples)
        # United States country URN: 103644278; SF Bay Area: 90000084; New York City: 102571732; London Area: 102257491
        geo_urns = [
            '101165590',  # United Kingdom
        ]
        
        print(f"🔍 Searching for: {', '.join(job_titles[:3])}...")
        print(f"📍 In locations: {', '.join(locations[:2])}...")
        print("📊 Target: 15 profiles, 2 pages")
        print("-" * 35)
        
        # Optional industries
        industries = [
            'Financial Services',
            'Insurance'
        ]
        
        # Run the search using the correct method signature
        results = await scraper.run_executive_search_with_cookies(
            job_titles=job_titles,
            locations=locations, 
            max_profiles=15,
            pages_to_scrape=2,
            industries=industries,
            geo_urns=geo_urns,
            origin='GLOBAL_SEARCH_HEADER',
            enrich_profiles=True,
            enrich_csv_path='output/enriched_profiles.csv',
            enrich_limit=50
        )
        
        if results and len(results) > 0:
            print(f"✅ SUCCESS: Found {len(results)} executive profiles!")
            
            # Show results
            print("\n📋 FOUND EXECUTIVES:")
            print("-" * 40)
            for i, profile in enumerate(results[:10], 1):
                name = profile.get('name', 'N/A')
                title = profile.get('title', 'N/A')
                company = profile.get('company', 'N/A')
                location = profile.get('location', 'N/A')
                
                print(f"{i:2d}. {name}")
                print(f"    💼 {title}")
                if company != 'N/A':
                    print(f"    🏢 {company}")
                if location != 'N/A':
                    print(f"    📍 {location}")
                print()
                
            print("📁 Base results saved to output directory")
            print("✨ Enrichment enabled: appended up to 50 detailed profiles to output/enriched_profiles.csv")
            print("🎯 Search completed successfully!")
            
        else:
            print("❌ No results found")
            print("💡 This might be due to:")
            print("   • Network timeout issues")
            print("   • LinkedIn interface changes")
            print("   • Search filters too restrictive")
            
    except Exception as e:
        print(f"❌ Error during search: {str(e)}")
        print("💡 Try running the human-like cookie extractor first:")
        print("   python human_like_cookie_extractor.py")
        
    finally:
        try:
            if hasattr(scraper, 'browser') and scraper.browser:
                await scraper.browser.close()
                print("\n🔒 Browser closed")
        except:
            pass

if __name__ == "__main__":
    print("🚀 Starting CEO & CTO Search...")
    asyncio.run(simple_ceo_cto_search())
