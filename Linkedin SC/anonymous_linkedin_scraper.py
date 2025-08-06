"""
Advanced LinkedIn Scraper - No Login Required
Professional scraping with proxy rotation, cookie management, and anti-detection
"""
import asyncio
import os
import csv
import re
import json
import random
import aiofiles
import aiohttp
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse, quote
from pathlib import Path
import hashlib

import pandas as pd
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from dotenv import load_dotenv
from asyncio_throttle import Throttler

# Load environment variables
load_dotenv()


class ProxyRotator:
    """Handle proxy rotation for anonymous scraping"""
    
    def __init__(self, proxy_list: List[str] = None):
        self.proxy_list = proxy_list or []
        self.current_index = 0
        self.failed_proxies = set()
    
    def get_next_proxy(self) -> Optional[Dict]:
        """Get next working proxy"""
        if not self.proxy_list:
            return None
            
        available_proxies = [p for i, p in enumerate(self.proxy_list) 
                           if i not in self.failed_proxies]
        
        if not available_proxies:
            # Reset failed proxies if all failed
            self.failed_proxies.clear()
            available_proxies = self.proxy_list
        
        if available_proxies:
            proxy = available_proxies[self.current_index % len(available_proxies)]
            self.current_index += 1
            
            # Parse proxy string (format: protocol://ip:port or ip:port)
            if '://' in proxy:
                return {'server': proxy}
            else:
                return {'server': f'http://{proxy}'}
        
        return None
    
    def mark_proxy_failed(self, proxy: str):
        """Mark proxy as failed"""
        try:
            proxy_index = self.proxy_list.index(proxy.replace('http://', ''))
            self.failed_proxies.add(proxy_index)
        except ValueError:
            pass


class UserAgentRotator:
    """Rotate user agents for better anonymity"""
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
    ]
    
    @classmethod
    def get_random_user_agent(cls) -> str:
        """Get random user agent"""
        return random.choice(cls.USER_AGENTS)


class AnonymousLinkedInScraper:
    """
    Anonymous LinkedIn Scraper - No Login Required
    
    Features:
    - No login required - scrapes public data only
    - Proxy rotation support
    - User agent rotation
    - Cookie management
    - Rate limiting and delays
    - Anti-detection measures
    - Stealth mode
    
    LEGAL NOTICE: This tool scrapes only publicly available data.
    Please respect LinkedIn's robots.txt and Terms of Service.
    Use responsibly and ensure compliance with applicable laws.
    """
    
    def __init__(self):
        # Configuration from environment variables
        self.search_keywords = os.getenv('SEARCH_KEYWORDS', '').split(',')
        self.max_posts = int(os.getenv('MAX_POSTS', 50))
        self.delay_min = int(os.getenv('DELAY_MIN', 3))
        self.delay_max = int(os.getenv('DELAY_MAX', 8))
        self.output_dir = os.getenv('OUTPUT_DIR', 'output')
        self.csv_filename = os.getenv('CSV_FILENAME', 'linkedin_posts.csv')
        self.images_dir = os.getenv('IMAGES_DIR', 'images')
        self.headless = os.getenv('HEADLESS', 'True').lower() == 'true'
        self.browser_timeout = int(os.getenv('BROWSER_TIMEOUT', 60000))
        
        # Anonymous scraping configuration
        self.use_proxies = os.getenv('USE_PROXIES', 'False').lower() == 'true'
        self.proxy_list = os.getenv('PROXY_LIST', '').split(',') if os.getenv('PROXY_LIST') else []
        self.stealth_mode = os.getenv('STEALTH_MODE', 'True').lower() == 'true'
        self.cookie_file = os.getenv('COOKIE_FILE', 'cookies.json')
        self.max_retry_attempts = int(os.getenv('MAX_RETRY_ATTEMPTS', 3))
        
        # Initialize components
        self.proxy_rotator = ProxyRotator(self.proxy_list)
        self.user_agent_rotator = UserAgentRotator()
        self.scraped_posts = []
        
        # Enhanced selectors for public LinkedIn pages
        self.selectors = {
            # Public post containers (no login required)
            'post_container': [
                'article[data-urn]',
                '.feed-shared-update-v2',
                '[data-test-id="main-feed-activity-card"]',
                'div[data-id*="activity"]',
                '.update-components-update-v2'
            ],
            
            # Content selectors
            'post_content': [
                '.feed-shared-text',
                '.feed-shared-inline-show-more-text',
                '.update-components-text',
                '[data-test-id="main-feed-activity-card"] .feed-shared-text'
            ],
            
            # Author information (public profiles)
            'author_name': [
                '.feed-shared-actor__name a',
                '.update-components-actor__name a',
                '[data-test-id="post-author-name"]'
            ],
            
            'author_title': [
                '.feed-shared-actor__description',
                '.update-components-actor__description'
            ],
            
            # Engagement metrics (publicly visible)
            'engagement_counts': [
                '.social-counts-reactions__count',
                '.feed-shared-social-action-bar__reaction-count',
                '[aria-label*="reaction"]'
            ],
            
            # Media content
            'post_images': [
                '.feed-shared-image img',
                '.update-components-image img',
                'img[alt*="post"]'
            ]
        }
    
    async def random_delay(self, min_delay: float = None, max_delay: float = None):
        """Random delay to avoid detection"""
        min_d = min_delay or self.delay_min
        max_d = max_delay or self.delay_max
        delay = random.uniform(min_d, max_d)
        await asyncio.sleep(delay)
    
    async def create_stealth_context(self, browser: Browser) -> BrowserContext:
        """Create a stealth browser context"""
        proxy = self.proxy_rotator.get_next_proxy() if self.use_proxies else None
        user_agent = self.user_agent_rotator.get_random_user_agent()
        
        context_options = {
            'user_agent': user_agent,
            'viewport': {'width': 1920, 'height': 1080},
            'locale': 'en-US',
            'timezone_id': 'America/New_York',
            'extra_http_headers': {
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'DNT': '1',
                'Connection': 'keep-alive',
            }
        }
        
        if proxy:
            context_options['proxy'] = proxy
            print(f"🔄 Using proxy: {proxy['server']}")
        
        context = await browser.new_context(**context_options)
        
        # Load cookies if available
        await self.load_cookies(context)
        
        return context
    
    async def load_cookies(self, context: BrowserContext):
        """Load cookies from file"""
        cookie_path = Path(self.cookie_file)
        if cookie_path.exists():
            try:
                with open(cookie_path, 'r') as f:
                    cookies = json.load(f)
                await context.add_cookies(cookies)
                print(f"🍪 Loaded {len(cookies)} cookies from {self.cookie_file}")
            except Exception as e:
                print(f"⚠️ Could not load cookies: {e}")
    
    async def save_cookies(self, context: BrowserContext):
        """Save cookies to file"""
        try:
            cookies = await context.cookies()
            with open(self.cookie_file, 'w') as f:
                json.dump(cookies, f, indent=2)
            print(f"🍪 Saved {len(cookies)} cookies to {self.cookie_file}")
        except Exception as e:
            print(f"⚠️ Could not save cookies: {e}")
    
    async def setup_stealth_page(self, page: Page):
        """Configure page for stealth scraping"""
        if self.stealth_mode:
            # Remove webdriver traces
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Cypress.utils.getRandomArbitrary(0, 1) > 0.5 ? 'granted' : 'denied' }) :
                        originalQuery(parameters)
                );
                
                // Randomize plugins length
                Object.defineProperty(navigator, 'plugins', {
                    get: () => { return [...Array(Math.floor(Math.random() * 5) + 1)]; },
                });
                
                // Override chrome object
                window.chrome = {
                    runtime: {},
                };
                
                // Override languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
            """)
        
        page.set_default_timeout(self.browser_timeout)
    
    def build_search_url(self, keywords: List[str], page_num: int = 1) -> str:
        """Build LinkedIn search URL for public content"""
        if not keywords or not keywords[0]:
            # Use LinkedIn public feed or trending topics
            return "https://www.linkedin.com/feed/"
        
        # Encode search query
        search_query = ' OR '.join([f'"{keyword.strip()}"' for keyword in keywords if keyword.strip()])
        encoded_query = quote(search_query)
        
        # Build URL for public content search
        return f"https://www.linkedin.com/search/results/content/?keywords={encoded_query}&page={page_num}"
    
    async def navigate_with_retry(self, page: Page, url: str, max_retries: int = 3) -> bool:
        """Navigate to URL with retry logic"""
        for attempt in range(max_retries):
            try:
                print(f"🌐 Navigating to: {url} (attempt {attempt + 1}/{max_retries})")
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                await self.random_delay(2, 4)
                return True
            except Exception as e:
                print(f"⚠️ Navigation attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    await self.random_delay(5, 10)
                    continue
                return False
        return False
    
    async def extract_post_data(self, page: Page, post_element) -> Dict:
        """Extract data from a single post element"""
        post_data = {
            'content': '',
            'author_name': '',
            'author_title': '',
            'post_date': '',
            'likes_count': 0,
            'comments_count': 0,
            'shares_count': 0,
            'image_urls': [],
            'post_url': '',
            'scraped_at': datetime.now().isoformat()
        }
        
        try:
            # Extract post content
            for selector in self.selectors['post_content']:
                try:
                    content_element = await post_element.query_selector(selector)
                    if content_element:
                        content = await content_element.text_content()
                        if content and len(content.strip()) > 0:
                            post_data['content'] = content.strip()
                            break
                except:
                    continue
            
            # Extract author information
            for selector in self.selectors['author_name']:
                try:
                    author_element = await post_element.query_selector(selector)
                    if author_element:
                        author = await author_element.text_content()
                        if author and len(author.strip()) > 0:
                            post_data['author_name'] = author.strip()
                            break
                except:
                    continue
            
            # Extract author title
            for selector in self.selectors['author_title']:
                try:
                    title_element = await post_element.query_selector(selector)
                    if title_element:
                        title = await title_element.text_content()
                        if title and len(title.strip()) > 0:
                            post_data['author_title'] = title.strip()
                            break
                except:
                    continue
            
            # Extract engagement metrics
            for selector in self.selectors['engagement_counts']:
                try:
                    elements = await post_element.query_selector_all(selector)
                    for i, element in enumerate(elements[:3]):  # likes, comments, shares
                        text = await element.text_content()
                        count = self.extract_number(text)
                        if i == 0:
                            post_data['likes_count'] = count
                        elif i == 1:
                            post_data['comments_count'] = count
                        elif i == 2:
                            post_data['shares_count'] = count
                except:
                    continue
            
            # Extract images
            for selector in self.selectors['post_images']:
                try:
                    img_elements = await post_element.query_selector_all(selector)
                    for img in img_elements[:3]:  # Limit to 3 images
                        src = await img.get_attribute('src')
                        if src and src.startswith('http'):
                            post_data['image_urls'].append(src)
                except:
                    continue
            
            # Try to get post URL
            try:
                url_element = await post_element.query_selector('a[href*=\"/posts/\"], a[href*=\"/activity-\"]')
                if url_element:
                    href = await url_element.get_attribute('href')
                    if href:
                        if href.startswith('/'):
                            post_data['post_url'] = f"https://www.linkedin.com{href}"
                        else:
                            post_data['post_url'] = href
            except:
                pass
        
        except Exception as e:
            print(f"⚠️ Error extracting post data: {str(e)}")
        
        return post_data
    
    def extract_number(self, text: str) -> int:
        """Extract number from text (e.g., '1.2K' -> 1200)"""
        if not text:
            return 0
        
        # Remove non-numeric characters except K, M, B
        clean_text = re.sub(r'[^0-9KMB.,]', '', text.upper())
        
        if not clean_text:
            return 0
        
        try:
            if 'K' in clean_text:
                number = float(clean_text.replace('K', '').replace(',', ''))
                return int(number * 1000)
            elif 'M' in clean_text:
                number = float(clean_text.replace('M', '').replace(',', ''))
                return int(number * 1000000)
            elif 'B' in clean_text:
                number = float(clean_text.replace('B', '').replace(',', ''))
                return int(number * 1000000000)
            else:
                return int(float(clean_text.replace(',', '')))
        except:
            return 0
    
    async def scroll_and_load_posts(self, page: Page, max_scrolls: int = 5) -> List:
        """Scroll page and load more posts"""
        print(f"📜 Starting to scroll page (max {max_scrolls} scrolls)...")
        
        all_posts = []
        last_height = 0
        
        for scroll in range(max_scrolls):
            # Scroll down
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self.random_delay(3, 6)
            
            # Get current posts
            current_posts = []
            for selector in self.selectors['post_container']:
                try:
                    posts = await page.query_selector_all(selector)
                    current_posts.extend(posts)
                except:
                    continue
            
            # Remove duplicates based on text content
            unique_posts = []
            seen_content = set()
            
            for post in current_posts:
                try:
                    # Get a unique identifier for the post
                    post_id = await post.get_attribute('data-urn') or await post.get_attribute('data-id')
                    if not post_id:
                        # Use content hash as identifier
                        content = await post.text_content()
                        post_id = hashlib.md5(content.encode()).hexdigest()[:16]
                    
                    if post_id not in seen_content:
                        seen_content.add(post_id)
                        unique_posts.append(post)
                except:
                    unique_posts.append(post)  # Add anyway if we can't get identifier
            
            all_posts = unique_posts
            print(f"📄 Scroll {scroll + 1}/{max_scrolls}: Found {len(all_posts)} total posts")
            
            # Check if we've reached our target
            if len(all_posts) >= self.max_posts:
                print(f"✅ Reached target of {self.max_posts} posts")
                break
            
            # Check if page height changed (no more content)
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                print("📄 No more content to load")
                break
            last_height = new_height
        
        return all_posts[:self.max_posts]
    
    async def process_posts(self, page: Page, post_elements: List) -> List[Dict]:
        """Process and extract data from post elements"""
        print(f"📊 Processing {len(post_elements)} posts...")
        processed_posts = []
        
        for i, post_element in enumerate(post_elements):
            try:
                post_data = await self.extract_post_data(page, post_element)
                
                # Only add posts with content
                if post_data['content'] or post_data['author_name']:
                    processed_posts.append(post_data)
                    print(f"✅ Processed post {i + 1}: {post_data['content'][:50]}...")
                
                # Random delay between posts
                if i < len(post_elements) - 1:
                    await self.random_delay(1, 3)
                    
            except Exception as e:
                print(f"⚠️ Error processing post {i + 1}: {str(e)}")
                continue
        
        return processed_posts
    
    async def save_to_csv(self, posts_data: List[Dict]):
        """Save scraped data to CSV file"""
        if not posts_data:
            print("❌ No data to save")
            return
        
        # Ensure output directory exists
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        output_path = Path(self.output_dir) / self.csv_filename
        
        # Convert to DataFrame and save
        df = pd.DataFrame(posts_data)
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"💾 Data saved to: {output_path}")
        print(f"📊 Total posts saved: {len(posts_data)}")
    
    async def main(self):
        """Main scraping function"""
        print("🚀 Starting Anonymous LinkedIn Scraper")
        print("=" * 50)
        print("⚠️ LEGAL NOTICE: Scraping public data only. Respect ToS.")
        print("=" * 50)
        
        # Validate configuration
        if not self.search_keywords or not self.search_keywords[0]:
            print("⚠️ No search keywords specified - will scrape trending content")
        
        async with async_playwright() as playwright:
            # Launch browser with anti-detection
            browser_args = [
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-extensions',
                '--no-first-run',
                '--disable-default-apps',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
            ]
            
            print(f"🌐 Launching browser (headless: {self.headless})...")
            browser = await playwright.chromium.launch(
                headless=self.headless,
                args=browser_args
            )
            
            try:
                # Create stealth context
                context = await self.create_stealth_context(browser)
                page = await context.new_page()
                await self.setup_stealth_page(page)
                
                # Build search URL
                search_url = self.build_search_url(self.search_keywords)
                
                # Navigate to LinkedIn
                if not await self.navigate_with_retry(page, search_url):
                    print("❌ Failed to navigate to LinkedIn")
                    return
                
                # Scroll and load posts
                post_elements = await self.scroll_and_load_posts(page)
                
                if not post_elements:
                    print("❌ No posts found")
                    return
                
                # Process posts
                self.scraped_posts = await self.process_posts(page, post_elements)
                
                if not self.scraped_posts:
                    print("❌ No post data extracted")
                    return
                
                # Save cookies for future use
                await self.save_cookies(context)
                
                # Save data
                await self.save_to_csv(self.scraped_posts)
                
                print("=" * 50)
                print("✅ Anonymous scraping completed successfully!")
                
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")
            finally:
                await browser.close()


# Run the scraper
if __name__ == "__main__":
    scraper = AnonymousLinkedInScraper()
    asyncio.run(scraper.main())
