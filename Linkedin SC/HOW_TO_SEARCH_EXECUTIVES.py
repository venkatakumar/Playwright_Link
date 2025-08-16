"""
HOW TO SCRAPE CEOs AND CTOs FROM LINKEDIN
=========================================

This guide shows you exactly how to search for and scrape executive profiles 
from LinkedIn using filters for location, job titles, and company information.

STEP 1: WHAT YOU CAN SEARCH FOR
-------------------------------
✅ Job Titles: CEO, CTO, CFO, CMO, Founder, President, VP, Director
✅ Locations: London, New York, San Francisco, Berlin, Tokyo, etc.
✅ Companies: Filter by company size, industry, or specific companies
✅ Data Extracted: Name, Job Title, Company, LinkedIn URL, Location

STEP 2: HOW TO USE THE EXISTING SCRAPER
---------------------------------------
"""

print("🎯 LINKEDIN EXECUTIVE SEARCH - COMPLETE GUIDE")
print("=" * 55)

print("\n📋 METHOD 1: Using the Executive Search Demo")
print("-" * 45)
print("1. Run: python executive_search_demo.py")
print("2. Choose from predefined configs:")
print("   - uk_tech_ceos: UK Technology CEOs")
print("   - us_ctos: US CTOs")
print("   - europe_fintech_execs: European FinTech Executives")
print("   - asia_startup_founders: Asia Pacific Founders")

print("\n📋 METHOD 2: Using the People Search Scraper Directly")
print("-" * 50)

code_example = '''
import asyncio
from linkedin_people_search_scraper import LinkedInPeopleSearchScraper

async def search_executives():
    scraper = LinkedInPeopleSearchScraper()
    
    # Search for CEOs in London
    profiles = await scraper.run_executive_search(
        job_titles=["CEO", "Chief Executive Officer", "Founder"],
        locations=["London", "Greater London"],
        max_profiles=25,
        pages_to_scrape=3
    )
    
    return profiles

# Run the search
profiles = asyncio.run(search_executives())
'''

print(code_example)

print("\n📊 WHAT DATA YOU GET:")
print("-" * 25)
print("✅ name: Full name of the executive")
print("✅ job_title: Their current role/title")  
print("✅ company: Company they work for")
print("✅ linkedin_url: Direct link to their LinkedIn profile")
print("✅ location: Their location/city")
print("✅ title_category: Categorized role (CEO, CTO, etc.)")
print("✅ company_size_estimate: Estimated company size")

print("\n📁 OUTPUT FORMATS:")
print("-" * 20)
print("✅ CSV: Excel-compatible spreadsheet")
print("✅ JSON: Structured data format")
print("✅ Excel: Native Excel file format")

print("\n🎯 COMMON SEARCH EXAMPLES:")
print("-" * 30)

examples = [
    {
        "title": "Tech Startup CEOs in San Francisco",
        "job_titles": ["CEO", "Founder & CEO"],
        "locations": ["San Francisco", "Bay Area"],
        "description": "Find technology startup leaders"
    },
    {
        "title": "CTOs in London Financial Services", 
        "job_titles": ["CTO", "Chief Technology Officer"],
        "locations": ["London", "Greater London"],
        "description": "Find tech leaders in finance"
    },
    {
        "title": "E-commerce Executives in Germany",
        "job_titles": ["CEO", "CTO", "Founder"],
        "locations": ["Berlin", "Munich", "Hamburg"],
        "description": "Find e-commerce leaders in Germany"
    }
]

for i, example in enumerate(examples, 1):
    print(f"\n{i}. {example['title']}")
    print(f"   Job Titles: {', '.join(example['job_titles'])}")
    print(f"   Locations: {', '.join(example['locations'])}")
    print(f"   Use Case: {example['description']}")

print("\n⚙️ CONFIGURATION OPTIONS:")
print("-" * 30)
print("📊 max_profiles: How many profiles to collect (10-100 recommended)")
print("📄 pages_to_scrape: How many search result pages to process (2-5 recommended)")
print("🎯 job_titles: List of job titles to search for")
print("📍 locations: List of cities/regions to search in")

print("\n🚀 QUICK START COMMANDS:")
print("-" * 25)
print("1. Run predefined search:")
print("   python executive_search_demo.py")
print("")
print("2. Test the scraper:")
print("   python simple_exec_test.py")
print("")
print("3. Custom search (modify job titles and locations as needed):")
print("   # Edit the parameters in the script files")

print("\n💡 PRO TIPS:")
print("-" * 15)
print("✅ Use multiple job title variations (CEO, Chief Executive Officer)")
print("✅ Include broader location terms (London, Greater London)")
print("✅ Start with smaller numbers (10-20 profiles) to test")
print("✅ Check the output folder for your data files")
print("✅ Ensure your LinkedIn credentials are set in .env file")

print("\n📝 NEXT STEPS:")
print("-" * 15)
print("1. Update your .env file with LinkedIn credentials")
print("2. Choose your search method (demo vs custom)")
print("3. Modify job titles and locations for your needs") 
print("4. Run the scraper and check the output folder")
print("5. Analyze the collected executive data")

print("\n🎉 Your executive search scraper is ready to use!")
print("Choose any of the methods above to start finding CEOs and CTOs!")
