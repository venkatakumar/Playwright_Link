"""
Executive Search Hub - All Roles Overview
=========================================

Complete overview and launcher for all executive search capabilities
"""

from people_search_config import EXECUTIVE_TITLES, LOCATIONS, SEARCH_CONFIGS

def show_all_executive_search_options():
    """Display all available executive search options"""
    
    print("🎯 EXECUTIVE SEARCH HUB - ALL ROLES")
    print("=" * 45)
    print("Complete LinkedIn executive search system")
    print("-" * 45)
    
    print("\n💼 EXECUTIVE ROLES SUPPORTED:")
    print("-" * 35)
    
    # CEO roles
    print("🔸 CEOs & FOUNDERS:")
    for title in EXECUTIVE_TITLES['ceo_founder'][:5]:
        print(f"  • {title}")
    print(f"  ... and {len(EXECUTIVE_TITLES['ceo_founder']) - 5} more CEO titles")
    
    # CTO roles  
    print("\n🔸 CTOs & TECH LEADERS:")
    for title in EXECUTIVE_TITLES['cto_tech'][:5]:
        print(f"  • {title}")
    print(f"  ... and {len(EXECUTIVE_TITLES['cto_tech']) - 5} more CTO titles")
    
    # CIO roles
    print("\n🔸 CIOs & IT DIRECTORS:")
    for title in EXECUTIVE_TITLES['cio_it'][:5]:
        print(f"  • {title}")
    print(f"  ... and {len(EXECUTIVE_TITLES['cio_it']) - 5} more CIO titles")
    
    # CFO roles
    print("\n🔸 CFOs & FINANCE DIRECTORS:")
    for title in EXECUTIVE_TITLES['cfo_finance'][:5]:
        print(f"  • {title}")
    print(f"  ... and {len(EXECUTIVE_TITLES['cfo_finance']) - 5} more CFO titles")
    
    # Test Manager roles
    print("\n🔸 TEST MANAGERS & QA LEADERS:")
    for title in EXECUTIVE_TITLES['test_qa'][:6]:
        print(f"  • {title}")
    print(f"  ... and {len(EXECUTIVE_TITLES['test_qa']) - 6} more QA titles")
    
    print("\n🌍 LOCATION COVERAGE:")
    print("-" * 25)
    for region, locations in LOCATIONS.items():
        print(f"🔸 {region.upper()}: {len(locations)} cities")
        print(f"   Examples: {', '.join(locations[:3])}")
    
    print("\n📋 PREDEFINED SEARCH CONFIGURATIONS:")
    print("-" * 40)
    for name, config in SEARCH_CONFIGS.items():
        print(f"🎯 {name}:")
        print(f"   📝 {config['description']}")
        print(f"   💼 {len(config['job_titles'])} job titles")
        print(f"   📍 {len(config['locations'])} locations")
    
    print("\n🚀 HOW TO RUN SEARCHES:")
    print("-" * 30)
    
    print("\n1️⃣ SEARCH ALL ROLES AT ONCE:")
    print("   python all_executive_search.py")
    print("   → Searches CEO, CTO, CIO, CFO, Test Managers in one run")
    
    print("\n2️⃣ SEARCH INDIVIDUAL ROLES:")
    print("   python ceo_cto_search.py     # CEOs and CTOs")
    print("   python cfo_search.py         # CFOs only")
    print("   python cio_search.py         # CIOs only") 
    print("   python test_manager_search.py # Test Managers only")
    
    print("\n3️⃣ PREDEFINED CONFIGURATIONS:")
    print("   python executive_search_demo.py")
    print("   → Choose from predefined configs")
    
    print("\n📊 DATA EXTRACTED FOR EACH EXECUTIVE:")
    print("-" * 40)
    data_fields = [
        "Full Name", "Job Title", "Company Name", "Location",
        "LinkedIn Profile URL", "Profile Summary", "Experience Details",
        "Education Background", "Skills & Endorsements", "Connection Count"
    ]
    for field in data_fields:
        print(f"  • {field}")
    
    print("\n💾 OUTPUT FORMATS:")
    print("-" * 20)
    print("• JSON files for each role")
    print("• Combined results file") 
    print("• CSV export capability")
    print("• Excel export capability")
    
    print("\n✅ FEATURES INCLUDED:")
    print("-" * 25)
    print("• Location filtering by city/country")
    print("• Multiple job title variations")
    print("• LinkedIn 2FA automatic handling")
    print("• Robust error handling and retries")
    print("• Progress tracking and reporting")
    print("• Duplicate detection and removal")
    
    print("\n🎯 READY TO SEARCH!")
    print("=" * 25)
    print("All executive roles (CEO, CTO, CIO, CFO, Test Managers)")
    print("can be searched with location filtering in one unified system!")

def show_quick_start_guide():
    """Show quick start guide"""
    
    print("\n" + "="*50)
    print("🚀 QUICK START GUIDE")
    print("="*50)
    
    print("\nSTEP 1: Choose your search approach")
    print("-" * 35)
    print("Option A: Search ALL roles at once")
    print("   → python all_executive_search.py")
    print("\nOption B: Search specific roles")
    print("   → python cfo_search.py (CFOs only)")
    print("   → python cio_search.py (CIOs only)")
    print("   → python test_manager_search.py (Test Managers only)")
    print("   → python ceo_cto_search.py (CEOs & CTOs)")
    
    print("\nSTEP 2: Results will be saved to output/ directory")
    print("-" * 45)
    print("• JSON files with detailed profile data")
    print("• Organized by role and timestamp")
    print("• LinkedIn URLs for direct access")
    
    print("\nSTEP 3: Review and analyze results")
    print("-" * 35)
    print("• Profile names, titles, companies")
    print("• LinkedIn profile URLs")
    print("• Location and experience data")

if __name__ == "__main__":
    show_all_executive_search_options()
    show_quick_start_guide()
