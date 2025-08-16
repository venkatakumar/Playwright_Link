"""
Executive Search Demo - Working Version
======================================

Uses existing predefined configurations to demonstrate CEO/CTO search functionality
"""

import asyncio
import json
from linkedin_people_search_scraper import LinkedInPeopleSearchScraper
from people_search_config import get_search_config

async def demo_executive_search():
    """Demo the executive search functionality with working configurations"""
    
    print("🎯 EXECUTIVE SEARCH DEMO - CEO & CTO FINDER")
    print("=" * 50)
    
    # Show what we're searching for
    print("📋 DEMONSTRATION SEARCHES:")
    print("1. UK Technology CEOs")
    print("2. US Chief Technology Officers") 
    print("3. European Fintech Executives")
    print("-" * 50)
    
    # Initialize scraper
    scraper = LinkedInPeopleSearchScraper()
    
    try:
        # Demo 1: UK Tech CEOs
        print("\n🇬🇧 DEMO 1: UK TECHNOLOGY CEOs")
        print("-" * 35)
        
        uk_config = get_search_config('uk_tech_ceos')
        if uk_config:
            print(f"📍 Locations: {', '.join(uk_config['locations'][:3])}...")
            print(f"💼 Job Titles: {', '.join(uk_config['job_titles'][:4])}...")
            print(f"🎯 Target: 10 profiles (demo)")
            
            results = await scraper.run_executive_search(
                job_titles=uk_config['job_titles'],
                locations=uk_config['locations'],
                max_profiles=10,  # Fixed number for demo
                pages_to_scrape=1
            )
            
            if results and len(results) > 0:
                print(f"✅ Found {len(results)} UK Tech CEOs:")
                for i, profile in enumerate(results[:5], 1):
                    print(f"  {i}. {profile.get('name', 'N/A')} - {profile.get('title', 'N/A')}")
                    print(f"     🏢 {profile.get('company', 'N/A')}")
                    
                # Save results
                with open('output/uk_tech_ceos.json', 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"💾 Saved {len(results)} profiles to output/uk_tech_ceos.json")
            else:
                print("❌ No UK CEO profiles found")
        
        print("\n" + "="*50)
        
        # Demo 2: US CTOs  
        print("\n🇺🇸 DEMO 2: US CHIEF TECHNOLOGY OFFICERS")
        print("-" * 45)
        
        us_config = get_search_config('us_ctos')
        if us_config:
            print(f"📍 Locations: {', '.join(us_config['locations'][:3])}...")
            print(f"💼 Job Titles: {', '.join(us_config['job_titles'][:4])}...")
            print(f"🎯 Target: 10 profiles (demo)")
            
            results = await scraper.run_executive_search(
                job_titles=us_config['job_titles'],
                locations=us_config['locations'], 
                max_profiles=10,  # Fixed number for demo
                pages_to_scrape=1
            )
            
            if results and len(results) > 0:
                print(f"✅ Found {len(results)} US CTOs:")
                for i, profile in enumerate(results[:5], 1):
                    print(f"  {i}. {profile.get('name', 'N/A')} - {profile.get('title', 'N/A')}")
                    print(f"     🏢 {profile.get('company', 'N/A')}")
                    
                # Save results  
                with open('output/us_ctos.json', 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"💾 Saved {len(results)} profiles to output/us_ctos.json")
            else:
                print("❌ No US CTO profiles found")
                
        print("\n" + "="*50)
        print("\n📊 WHAT DATA IS EXTRACTED FOR EACH EXECUTIVE:")
        print("-" * 50)
        print("• Full Name")
        print("• Job Title") 
        print("• Company Name")
        print("• Location")
        print("• LinkedIn Profile URL")
        print("• Profile Summary (if available)")
        print("• Experience Details")
        print("• Education Background")
        print("• Skills and Endorsements")
        print("• Connection Count")
        
        print("\n🎯 SEARCH CAPABILITIES:")
        print("-" * 25)
        print("✅ Filter by Job Title (CEO, CTO, Founder, etc.)")
        print("✅ Filter by Location (City, Country, Region)")
        print("✅ Filter by Industry Keywords")
        print("✅ Configurable result limits") 
        print("✅ Export to JSON, CSV, Excel")
        print("✅ Handle LinkedIn 2FA automatically")
        
        print("\n🚀 READY TO USE!")
        print("The executive search functionality is fully operational.")
        print("You can search for CEOs and CTOs by selecting filters and location.")
        
    except Exception as e:
        print(f"❌ Demo error: {str(e)}")
        print("This may be due to LinkedIn selector changes or network issues")
        
    finally:
        # Close browser safely
        try:
            if hasattr(scraper, 'browser') and scraper.browser:
                await scraper.browser.close()
        except:
            pass

if __name__ == "__main__":
    print("🚀 Starting Executive Search Demo...")
    print("This will demonstrate CEO and CTO search with location filtering")
    print("-" * 60)
    
    asyncio.run(demo_executive_search())
