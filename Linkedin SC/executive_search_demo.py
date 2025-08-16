"""
LinkedIn Executive Search Demo
=============================

Easy-to-use demo script for searching LinkedIn executives with predefined configurations
"""

import asyncio
from linkedin_people_search_scraper import LinkedInPeopleSearchScraper
from people_search_config import SEARCH_CONFIGS, get_search_config, list_available_configs

async def run_predefined_search():
    """Run a search using predefined configurations"""
    
    print("🎯 LINKEDIN EXECUTIVE SEARCH - PREDEFINED CONFIGS")
    print("=" * 55)
    
    # Show available configurations
    list_available_configs()
    
    # Let user choose a configuration
    config_name = input("\\nEnter configuration name (or 'custom' for custom search): ").strip()
    
    scraper = LinkedInPeopleSearchScraper()
    
    if config_name == 'custom':
        # Custom search
        print("\\n🔧 CUSTOM SEARCH SETUP")
        print("-" * 30)
        
        job_titles = input("Enter job titles (comma-separated): ").strip()
        job_titles = [title.strip() for title in job_titles.split(',')]
        
        locations = input("Enter locations (comma-separated): ").strip() 
        locations = [loc.strip() for loc in locations.split(',')]
        
        max_profiles = input("Max profiles (default 30): ").strip()
        max_profiles = int(max_profiles) if max_profiles.isdigit() else 30
        
        pages = input("Max pages (default 3): ").strip()
        pages = int(pages) if pages.isdigit() else 3
        
    else:
        # Use predefined configuration
        config = get_search_config(config_name)
        if not config:
            print(f"❌ Configuration '{config_name}' not found!")
            return
        
        print(f"\\n🎯 Using configuration: {config['description']}")
        
        job_titles = config['job_titles'][:5]  # Limit to first 5 titles
        locations = config['locations'][:3]   # Limit to first 3 locations
        
        max_profiles = input(f"Max profiles (default 30): ").strip()
        max_profiles = int(max_profiles) if max_profiles.isdigit() else 30
        
        pages = input("Max pages (default 3): ").strip()
        pages = int(pages) if pages.isdigit() else 3
    
    print(f"\\n🚀 Starting search...")
    print(f"Job Titles: {job_titles}")
    print(f"Locations: {locations}")
    print(f"Target: {max_profiles} profiles, {pages} pages")
    
    # Run the search
    profiles = await scraper.run_executive_search(job_titles, locations, max_profiles, pages)
    
    if profiles:
        print(f"\\n🎉 Successfully found {len(profiles)} executive profiles!")
        print("\\n📊 QUICK SUMMARY:")
        
        # Show some stats
        unique_companies = len(set(p['company'] for p in profiles if p['company']))
        unique_locations = len(set(p['location'] for p in profiles if p['location']))
        
        print(f"   👥 Profiles: {len(profiles)}")
        print(f"   🏢 Companies: {unique_companies}")
        print(f"   📍 Locations: {unique_locations}")
        
        # Show first few profiles
        print(f"\\n📄 SAMPLE PROFILES:")
        for i, profile in enumerate(profiles[:3]):
            print(f"   {i+1}. {profile['name']}")
            print(f"      Role: {profile['current_role']}")
            print(f"      Company: {profile['company']}")
            print(f"      Location: {profile['location']}")
            print(f"      URL: {profile['profile_url']}")
            print()
        
        print("📁 Check the 'output' folder for complete data files (CSV, JSON, Excel)")
    
    else:
        print("\\n😔 No profiles found. Try:")
        print("   1. Different job titles or locations")
        print("   2. Broader search terms")
        print("   3. Check LinkedIn manually first")

if __name__ == "__main__":
    asyncio.run(run_predefined_search())
