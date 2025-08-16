import asyncio
from cookie_enhanced_scraper import CookieEnhancedLinkedInScraper


async def main():
    scraper = CookieEnhancedLinkedInScraper(headless=False)
    job_titles = ['CEO', 'Chief Executive Officer', 'CTO', 'Chief Technology Officer', 'Founder', 'Co-Founder']
    locations = ['United Kingdom']
    industries = ['Financial Services', 'Insurance']
    geo_urns = ['101165590']

    results = await scraper.run_executive_search_with_cookies(
        job_titles=job_titles,
        locations=locations,
        max_profiles=25,
        pages_to_scrape=2,
        industries=industries,
        geo_urns=geo_urns,
        origin='FACETED_SEARCH',
    )

    print(f"Done. Collected {len(results)} profiles.")


if __name__ == "__main__":
    asyncio.run(main())
