"""
Demo: People search + profile enrichment
"""
import asyncio
from cookie_enhanced_scraper import CookieEnhancedLinkedInScraper


async def main():
    scraper = CookieEnhancedLinkedInScraper(headless=False)
    try:
        results = await scraper.run_executive_search_with_cookies(
            job_titles=['CEO','CTO','Founder'],
            locations=['United Kingdom'],
            industries=['Financial Services','Insurance'],
            geo_urns=['101165590'],
            max_profiles=10,
            pages_to_scrape=1,
            enrich_profiles=True,
            enrich_csv_path='output/enriched_profiles.csv',
            enrich_limit=2,
        )
        print(f"Enrichment demo completed. Base profiles: {len(results) if results else 0}")
        print("Detailed rows appended to output/enriched_profiles.csv")
    finally:
        try:
            if scraper.browser:
                await scraper.browser.close()
        except Exception:
            pass


if __name__ == '__main__':
    asyncio.run(main())
