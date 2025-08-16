"""
All Executive Roles Search
==========================

Unified search for CEO, CTO, CIO, CFO, and Test Managers with location filtering
Search all roles in one run or select specific roles
"""

import asyncio
import json
import os
from datetime import datetime
from linkedin_people_search_scraper import LinkedInPeopleSearchScraper
from people_search_config import get_search_config, EXECUTIVE_TITLES, LOCATIONS

class AllExecutiveSearch:
    """Search for all executive roles in one unified run"""
    
    def __init__(self):
        self.scraper = LinkedInPeopleSearchScraper()
        self.results = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    async def search_all_roles(self, target_locations=['usa', 'uk'], profiles_per_role=15):
        """Search for all executive roles: CEO, CTO, CIO, CFO, Test Managers"""
        
        print("🎯 ALL EXECUTIVE ROLES SEARCH")
        print("=" * 45)
        print(f"📍 Target Locations: {', '.join(target_locations)}")
        print(f"👥 Profiles per role: {profiles_per_role}")
        print("-" * 50)
        
        # Define all role searches
        role_searches = {
            'CEOs': {
                'job_titles': EXECUTIVE_TITLES['ceo_founder'],
                'description': 'Chief Executive Officers & Founders'
            },
            'CTOs': {
                'job_titles': EXECUTIVE_TITLES['cto_tech'], 
                'description': 'Chief Technology Officers & VPs Engineering'
            },
            'CIOs': {
                'job_titles': EXECUTIVE_TITLES['cio_it'],
                'description': 'Chief Information Officers & IT Directors'
            },
            'CFOs': {
                'job_titles': EXECUTIVE_TITLES['cfo_finance'],
                'description': 'Chief Financial Officers & Finance Directors'
            },
            'Test_Managers': {
                'job_titles': EXECUTIVE_TITLES['test_qa'],
                'description': 'Test Managers & QA Leaders'
            }
        }
        
        # Combine all target locations
        all_locations = []
        for loc_key in target_locations:
            if loc_key in LOCATIONS:
                all_locations.extend(LOCATIONS[loc_key])
        
        try:
            # Search each role
            for role_name, role_config in role_searches.items():
                print(f"\n🔍 SEARCHING {role_name.upper()}")
                print("-" * 35)
                print(f"📝 {role_config['description']}")
                print(f"💼 Job Titles: {', '.join(role_config['job_titles'][:3])}...")
                print(f"📍 Locations: {len(all_locations)} cities")
                
                # Perform the search
                results = await self.scraper.run_executive_search(
                    job_titles=role_config['job_titles'],
                    locations=all_locations,
                    max_profiles=profiles_per_role,
                    pages_to_scrape=2
                )
                
                if results and len(results) > 0:
                    print(f"✅ Found {len(results)} {role_name}")
                    
                    # Show sample results
                    for i, profile in enumerate(results[:3], 1):
                        print(f"  {i}. {profile.get('name', 'N/A')} - {profile.get('title', 'N/A')}")
                        print(f"     🏢 {profile.get('company', 'N/A')}")
                    
                    if len(results) > 3:
                        print(f"     ... and {len(results) - 3} more")
                        
                    # Store results
                    self.results[role_name] = results
                else:
                    print(f"❌ No {role_name} found")
                    self.results[role_name] = []
                    
                print()
                
        except Exception as e:
            print(f"❌ Error during search: {str(e)}")
            
        # Generate summary
        await self.generate_summary()
        
    async def search_specific_roles(self, selected_roles, target_locations=['usa', 'uk'], profiles_per_role=20):
        """Search for specific roles only"""
        
        print(f"🎯 SEARCHING SPECIFIC ROLES: {', '.join(selected_roles)}")
        print("=" * 60)
        
        # Role mapping
        role_mapping = {
            'ceo': ('CEOs', EXECUTIVE_TITLES['ceo_founder']),
            'cto': ('CTOs', EXECUTIVE_TITLES['cto_tech']),
            'cio': ('CIOs', EXECUTIVE_TITLES['cio_it']),
            'cfo': ('CFOs', EXECUTIVE_TITLES['cfo_finance']),
            'test': ('Test_Managers', EXECUTIVE_TITLES['test_qa'])
        }
        
        # Combine locations
        all_locations = []
        for loc_key in target_locations:
            if loc_key in LOCATIONS:
                all_locations.extend(LOCATIONS[loc_key])
        
        try:
            for role_key in selected_roles:
                if role_key in role_mapping:
                    role_name, job_titles = role_mapping[role_key]
                    
                    print(f"\n🔍 SEARCHING {role_name.upper()}")
                    print("-" * 40)
                    print(f"💼 Job Titles: {len(job_titles)} titles")
                    print(f"📍 Locations: {len(all_locations)} cities")
                    
                    results = await self.scraper.run_executive_search(
                        job_titles=job_titles,
                        locations=all_locations,
                        max_profiles=profiles_per_role,
                        pages_to_scrape=2
                    )
                    
                    if results and len(results) > 0:
                        print(f"✅ Found {len(results)} {role_name}")
                        self.results[role_name] = results
                        
                        # Show top results
                        for i, profile in enumerate(results[:5], 1):
                            print(f"  {i}. {profile.get('name', 'N/A')}")
                            print(f"     💼 {profile.get('title', 'N/A')}")
                            print(f"     🏢 {profile.get('company', 'N/A')}")
                            print(f"     📍 {profile.get('location', 'N/A')}")
                    else:
                        print(f"❌ No {role_name} found")
                        self.results[role_name] = []
                        
        except Exception as e:
            print(f"❌ Error during search: {str(e)}")
            
        await self.generate_summary()
        
    async def generate_summary(self):
        """Generate and save search summary"""
        
        total_profiles = sum(len(profiles) for profiles in self.results.values())
        
        print("\n" + "="*60)
        print("📊 SEARCH SUMMARY")
        print("="*60)
        
        for role_name, profiles in self.results.items():
            print(f"🎯 {role_name}: {len(profiles)} profiles")
            
        print(f"\n🎉 TOTAL PROFILES FOUND: {total_profiles}")
        
        if total_profiles > 0:
            # Save all results to files
            await self.save_results()
            
    async def save_results(self):
        """Save results to multiple formats"""
        
        print("\n💾 SAVING RESULTS...")
        print("-" * 25)
        
        # Create output directory
        os.makedirs('output', exist_ok=True)
        
        # Save individual role files
        for role_name, profiles in self.results.items():
            if profiles:
                # JSON format
                json_file = f'output/{role_name.lower()}_{self.timestamp}.json'
                with open(json_file, 'w') as f:
                    json.dump(profiles, f, indent=2)
                print(f"📄 {role_name}: {json_file}")
                
        # Save combined results
        combined_file = f'output/all_executives_{self.timestamp}.json'
        with open(combined_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"📄 Combined: {combined_file}")
        
        print(f"\n✅ All results saved to output/ directory")
        
    async def close(self):
        """Close browser connection"""
        try:
            if hasattr(self.scraper, 'browser') and self.scraper.browser:
                await self.scraper.browser.close()
        except:
            pass

async def main():
    """Main function with user options"""
    
    print("🚀 ALL EXECUTIVE ROLES SEARCH")
    print("=" * 35)
    print("Search for CEOs, CTOs, CIOs, CFOs, and Test Managers")
    print("-" * 50)
    
    print("\n📋 SEARCH OPTIONS:")
    print("1. Search ALL roles (CEO, CTO, CIO, CFO, Test Managers)")
    print("2. Search SPECIFIC roles only")
    print("3. Use PREDEFINED configurations")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    search_engine = AllExecutiveSearch()
    
    try:
        if choice == "1":
            # Search all roles
            print("\n🎯 Searching ALL executive roles...")
            await search_engine.search_all_roles(
                target_locations=['usa', 'uk', 'europe'],
                profiles_per_role=12
            )
            
        elif choice == "2":
            # Search specific roles
            print("\n📋 Available roles: ceo, cto, cio, cfo, test")
            roles_input = input("Enter roles (comma-separated): ").strip()
            selected_roles = [role.strip().lower() for role in roles_input.split(',')]
            
            locations_input = input("Enter location regions (usa, uk, europe, asia_pacific): ").strip()
            target_locations = [loc.strip() for loc in locations_input.split(',')]
            
            await search_engine.search_specific_roles(
                selected_roles=selected_roles,
                target_locations=target_locations,
                profiles_per_role=15
            )
            
        elif choice == "3":
            # Use predefined configs
            print("\n📋 Available predefined configs:")
            print("• global_cfos - CFOs in US and UK")
            print("• global_cios - CIOs in US and Europe") 
            print("• global_test_managers - Test Managers globally")
            print("• uk_tech_ceos - UK Technology CEOs")
            print("• us_ctos - US CTOs")
            
            config_name = input("Enter config name: ").strip()
            config = get_search_config(config_name)
            
            if config:
                results = await search_engine.scraper.run_executive_search(
                    job_titles=config['job_titles'],
                    locations=config['locations'],
                    max_profiles=20,
                    pages_to_scrape=2
                )
                
                if results:
                    search_engine.results[config_name] = results
                    await search_engine.generate_summary()
            else:
                print(f"❌ Configuration '{config_name}' not found!")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        
    finally:
        await search_engine.close()

if __name__ == "__main__":
    asyncio.run(main())
