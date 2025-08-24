import asyncio
import os
import sys
from dotenv import load_dotenv

from linkedin_feed_scraper import LinkedInFeedScraper

load_dotenv()

async def main():
    scraper = LinkedInFeedScraper()
    max_posts = int(os.getenv('MAX_POSTS', '30'))
    scroll_attempts = int(os.getenv('SCROLL_ATTEMPTS', '8'))

    print('🎯 Running LinkedIn post scraper with cookie session (feed)')
    results = await scraper.run_feed_scraper(max_posts=max_posts, scroll_attempts=scroll_attempts)
    if results:
        print(f'✅ Done: {len(results)} posts saved to output folder')
    else:
        print('⚠️ No posts collected')

if __name__ == '__main__':
    if sys.platform.startswith('win'):
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except Exception:
            pass
    asyncio.run(main())
