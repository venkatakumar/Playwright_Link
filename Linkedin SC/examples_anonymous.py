"""
Example usage of Anonymous LinkedIn Scraper
Demonstrates various scraping scenarios without login
"""
import asyncio
import os
from anonymous_linkedin_scraper import AnonymousLinkedInScraper
from proxy_manager import setup_proxy_rotation


async def example_basic_scraping():
    """Basic anonymous scraping example"""
    print("🔹 Example 1: Basic Anonymous Scraping")
    print("=" * 50)
    
    # Set basic configuration
    os.environ['SEARCH_KEYWORDS'] = 'python programming,data science'
    os.environ['MAX_POSTS'] = '20'
    os.environ['HEADLESS'] = 'True'
    os.environ['STEALTH_MODE'] = 'True'
    
    scraper = AnonymousLinkedInScraper()
    await scraper.main()
    
    print(f"✅ Scraped {len(scraper.scraped_posts)} posts")
    return scraper.scraped_posts


async def example_with_proxies():
    """Example with proxy rotation"""
    print("\n🔹 Example 2: Scraping with Proxy Rotation")
    print("=" * 50)
    
    # First, set up proxy rotation
    working_proxies = await setup_proxy_rotation()
    
    if working_proxies:
        # Configure scraper with proxies
        os.environ['USE_PROXIES'] = 'True'
        os.environ['PROXY_LIST'] = ','.join(working_proxies[:5])  # Use top 5
        os.environ['SEARCH_KEYWORDS'] = 'machine learning,AI'
        os.environ['MAX_POSTS'] = '15'
        
        scraper = AnonymousLinkedInScraper()
        await scraper.main()
        
        print(f"✅ Scraped {len(scraper.scraped_posts)} posts using proxies")
    else:
        print("❌ No working proxies available, skipping proxy example")


async def example_stealth_mode():
    """Example with maximum stealth features"""
    print("\n🔹 Example 3: Maximum Stealth Scraping")
    print("=" * 50)
    
    # Configure for maximum stealth
    os.environ['HEADLESS'] = 'True'
    os.environ['STEALTH_MODE'] = 'True'
    os.environ['DELAY_MIN'] = '5'
    os.environ['DELAY_MAX'] = '12'
    os.environ['MAX_POSTS'] = '10'
    os.environ['SEARCH_KEYWORDS'] = 'software engineering'
    
    scraper = AnonymousLinkedInScraper()
    await scraper.main()
    
    print(f"✅ Stealth scraped {len(scraper.scraped_posts)} posts")


async def example_trending_content():
    """Example scraping trending content without specific keywords"""
    print("\n🔹 Example 4: Scraping Trending Content")
    print("=" * 50)
    
    # No search keywords = trending content
    os.environ['SEARCH_KEYWORDS'] = ''
    os.environ['MAX_POSTS'] = '25'
    os.environ['HEADLESS'] = 'False'  # Show browser for demo
    
    scraper = AnonymousLinkedInScraper()
    await scraper.main()
    
    print(f"✅ Scraped {len(scraper.scraped_posts)} trending posts")


async def example_high_volume_scraping():
    """Example for scraping larger volumes of data"""
    print("\n🔹 Example 5: High-Volume Scraping")
    print("=" * 50)
    
    # Configure for high-volume scraping
    os.environ['SEARCH_KEYWORDS'] = 'technology,innovation,startup'
    os.environ['MAX_POSTS'] = '100'
    os.environ['HEADLESS'] = 'True'
    os.environ['DELAY_MIN'] = '2'
    os.environ['DELAY_MAX'] = '5'
    os.environ['CSV_FILENAME'] = 'high_volume_posts.csv'
    
    scraper = AnonymousLinkedInScraper()
    await scraper.main()
    
    print(f"✅ High-volume scraped {len(scraper.scraped_posts)} posts")


def print_scraping_tips():
    """Print tips for effective anonymous scraping"""
    print("\n📋 Anonymous LinkedIn Scraping Tips:")
    print("=" * 50)
    print("✅ DO:")
    print("  • Use reasonable delays between requests (3-8 seconds)")
    print("  • Rotate user agents automatically")
    print("  • Save and reuse cookies")
    print("  • Use headless mode for production")
    print("  • Monitor rate limits")
    print("  • Scrape during off-peak hours")
    print("  • Use proxy rotation for large volumes")
    print("  • Respect robots.txt")
    
    print("\n❌ DON'T:")
    print("  • Make too many concurrent requests")
    print("  • Use the same IP for extended periods")
    print("  • Ignore rate limits")
    print("  • Scrape personal/private data")
    print("  • Violate terms of service")
    print("  • Use for commercial purposes without permission")
    
    print("\n🔧 Configuration Tips:")
    print("  • Start with small batches (10-20 posts)")
    print("  • Test with headless=False first")
    print("  • Use stealth mode for better success rates")
    print("  • Save cookies between sessions")
    print("  • Monitor response times and errors")


async def main():
    """Run all examples"""
    print("🚀 Anonymous LinkedIn Scraper Examples")
    print("=" * 60)
    print("⚠️ LEGAL NOTICE: These examples scrape only public data.")
    print("   Please respect LinkedIn's Terms of Service.")
    print("=" * 60)
    
    # Print tips first
    print_scraping_tips()
    
    # Ask user which example to run
    print("\nAvailable examples:")
    print("1. Basic anonymous scraping")
    print("2. Scraping with proxy rotation") 
    print("3. Maximum stealth scraping")
    print("4. Trending content scraping")
    print("5. High-volume scraping")
    print("6. Run all examples")
    
    choice = input("\nSelect example (1-6): ").strip()
    
    try:
        if choice == "1":
            await example_basic_scraping()
        elif choice == "2":
            await example_with_proxies()
        elif choice == "3":
            await example_stealth_mode()
        elif choice == "4":
            await example_trending_content()
        elif choice == "5":
            await example_high_volume_scraping()
        elif choice == "6":
            print("🔄 Running all examples...")
            await example_basic_scraping()
            await example_stealth_mode()
            await example_trending_content()
        else:
            print("Invalid choice. Running basic example...")
            await example_basic_scraping()
            
    except KeyboardInterrupt:
        print("\n👋 Examples stopped by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
