"""
Example usage of Enhanced LinkedIn Scraper
==========================================

This script demonstrates all the new features:
1. Profile-based scraping
2. URL-based scraping  
3. Multiple export formats
4. Enhanced data extraction
"""

import asyncio
import os
from enhanced_linkedin_scraper import EnhancedLinkedInScraper
from dotenv import load_dotenv

load_dotenv()


async def example_profile_scraping():
    """Example: Scrape posts from specific LinkedIn profiles"""
    print("📱 EXAMPLE 1: Profile-based Scraping")
    print("=" * 50)
    
    scraper = EnhancedLinkedInScraper()
    
    # Configure scraper
    scraper.email = os.getenv('LINKEDIN_EMAIL', 'your_email@example.com')
    scraper.password = os.getenv('LINKEDIN_PASSWORD', 'your_password')
    scraper.max_posts = 10
    scraper.headless = False
    
    # Set profile URLs to scrape
    profile_urls = [
        "https://www.linkedin.com/in/satya-nadella/",
        "https://www.linkedin.com/in/sundarpichai/",
        "https://www.linkedin.com/in/jeffweiner08/"
    ]
    scraper.set_profile_urls(profile_urls)
    
    # Set export format
    scraper.set_export_format('json')
    
    # Run scraping
    await scraper.main_enhanced('profiles')
    print("✅ Profile scraping completed!")


async def example_url_scraping():
    """Example: Scrape specific post URLs"""
    print("\n🔗 EXAMPLE 2: URL-based Scraping")
    print("=" * 50)
    
    scraper = EnhancedLinkedInScraper()
    
    # Configure scraper
    scraper.email = os.getenv('LINKEDIN_EMAIL', 'your_email@example.com')
    scraper.password = os.getenv('LINKEDIN_PASSWORD', 'your_password')
    scraper.headless = False
    
    # Set specific post URLs to scrape
    post_urls = [
        "https://www.linkedin.com/posts/satya-nadella_ai-innovation-microsoft-activity-1234567890-abcd",
        "https://www.linkedin.com/posts/sundarpichai_google-ai-technology-activity-1234567891-efgh"
    ]
    scraper.set_post_urls(post_urls)
    
    # Set export format
    scraper.set_export_format('excel')
    
    # Run scraping
    await scraper.main_enhanced('urls')
    print("✅ URL scraping completed!")


async def example_enhanced_search():
    """Example: Enhanced search with better filters"""
    print("\n🔍 EXAMPLE 3: Enhanced Search Scraping")
    print("=" * 50)
    
    scraper = EnhancedLinkedInScraper()
    
    # Configure scraper
    scraper.email = os.getenv('LINKEDIN_EMAIL', 'your_email@example.com')
    scraper.password = os.getenv('LINKEDIN_PASSWORD', 'your_password')
    scraper.search_keywords = "artificial intelligence,machine learning"
    scraper.max_posts = 20
    scraper.headless = False
    
    # Set export format
    scraper.set_export_format('csv')
    
    # Run scraping
    await scraper.main_enhanced('search')
    print("✅ Enhanced search scraping completed!")


async def example_feed_scraping_with_enhanced_data():
    """Example: Feed scraping with enhanced data extraction"""
    print("\n📰 EXAMPLE 4: Enhanced Feed Scraping")
    print("=" * 50)
    
    scraper = EnhancedLinkedInScraper()
    
    # Configure scraper
    scraper.email = os.getenv('LINKEDIN_EMAIL', 'your_email@example.com')
    scraper.password = os.getenv('LINKEDIN_PASSWORD', 'your_password')
    scraper.max_posts = 15
    scraper.headless = False
    
    # Set export format to JSON for rich data structure
    scraper.set_export_format('json')
    
    # Run scraping (default feed mode)
    await scraper.main_enhanced('feed')
    print("✅ Enhanced feed scraping completed!")


async def demonstrate_all_features():
    """Demonstrate all enhanced features"""
    print("🚀 Enhanced LinkedIn Scraper - Feature Demonstration")
    print("=" * 70)
    print()
    print("NEW FEATURES ADDED:")
    print("✅ Profile-based post scraping")
    print("✅ Direct post URL scraping")
    print("✅ JSON export format")
    print("✅ Excel export format") 
    print("✅ Enhanced data extraction:")
    print("   • Author profile URLs")
    print("   • Company information")
    print("   • Hashtags extraction")
    print("   • Mentions extraction")
    print("   • Links within posts")
    print("   • Post type classification")
    print("   • Enhanced engagement metrics")
    print()
    
    # Uncomment the examples you want to run:
    
    # await example_profile_scraping()
    # await example_url_scraping()
    # await example_enhanced_search()
    # await example_feed_scraping_with_enhanced_data()
    
    print("\n📋 To run examples:")
    print("1. Uncomment the example functions above")
    print("2. Update profile URLs and post URLs with real ones")
    print("3. Make sure your .env file has valid credentials")
    print("4. Run: python examples_enhanced.py")


if __name__ == "__main__":
    asyncio.run(demonstrate_all_features())
