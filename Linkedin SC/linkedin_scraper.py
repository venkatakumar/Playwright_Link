import asyncio
import os
import csv
import re
import json
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import random
import aiofiles
import aiohttp
from pathlib import Path

import pandas as pd
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from dotenv import load_dotenv
from asyncio_throttle import Throttler

# Import our enhancement utilities
from utils import (
    enhance_post_data,
    setup_logging,
    ProxyRotator,
    get_inner_text_first,
    dedupe_posts,
    clean_posts,
)
from cookie_manager import LinkedInCookieManager
from email_notifications import EmailNotificationSystem

# Load environment variables
load_dotenv()


class LinkedInScraper:
    """
    LinkedIn Posts Scraper using Playwright
    
    WARNING: This tool is for educational purposes only. Please respect LinkedIn's 
    Terms of Service and use responsibly. Only scrape public data and avoid 
    excessive requests that could be considered abuse.
    
    IMPORTANT: LinkedIn actively detects and blocks automated scraping. Use at your own risk.
    Consider using LinkedIn's official API for production applications.
    """
    
    def __init__(self):
        # Configuration from environment variables
        self.email = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        self.search_keywords = os.getenv('SEARCH_KEYWORDS', '').split(',')
        self.max_posts = int(os.getenv('MAX_POSTS', 50))
        self.delay_min = int(os.getenv('DELAY_MIN', 2))
        self.delay_max = int(os.getenv('DELAY_MAX', 5))
        self.output_dir = os.getenv('OUTPUT_DIR', 'output')
        self.csv_filename = os.getenv('CSV_FILENAME', 'linkedin_posts.csv')
        self.images_dir = os.getenv('IMAGES_DIR', 'images')
        self.headless = os.getenv('HEADLESS', 'False').lower() == 'true'
        self.browser_timeout = int(os.getenv('BROWSER_TIMEOUT', 30000))
        self.login_wait_time = int(os.getenv('LOGIN_WAIT_TIME', 60))
    self.two_factor_wait = os.getenv('TWO_FACTOR_WAIT', 'True').lower() == 'true'
    self.scrolls = int(os.getenv('SCROLL_ATTEMPTS', 5))
    self.sort_by_recent = os.getenv('SORT_BY_RECENT', 'False').lower() == 'true'
    self.enable_proxies = os.getenv('ENABLE_PROXIES', 'False').lower() == 'true'
    self.log_level = os.getenv('LOG_LEVEL', 'INFO')

        # Create output directories
        Path(self.output_dir).mkdir(exist_ok=True)
        Path(os.path.join(self.output_dir, self.images_dir)).mkdir(exist_ok=True)

        # Initialize data storage
        self.scraped_posts = []
        self.session = None
        self.throttler = Throttler(rate_limit=1, period=2)  # Rate limiting

        # Cookie + notifications
        self.cookie_manager = LinkedInCookieManager()
        self.email_notifier = EmailNotificationSystem()

    # Logging and proxies
    self.logger = setup_logging(self.log_level)
    self.proxy_rotator = ProxyRotator()

        # Selectors (update these if LinkedIn changes their layout)
        self.selectors = {
            'email_input': 'input[name="session_key"]',
            'password_input': 'input[name="session_password"]',
            'login_button': 'button[type="submit"]',
            'search_box': 'input[placeholder*="Search"]',
            'post_container': 'div[data-id]',
            'post_content': '.feed-shared-text',
            'author_name': '.feed-shared-actor__name',
            'author_title': '.feed-shared-actor__description',
            'post_date': 'time',
            'likes_count': 'button[aria-label*="reaction"]',
            'comments_count': 'button[aria-label*="comment"]',
            'post_images': '.feed-shared-image img',
            'load_more': 'button[aria-label*="Show more results"]',
            'captcha': '.challenge-form',
        }

    async def human_delay(self, min_delay: Optional[int] = None, max_delay: Optional[int] = None):
        """Add human-like delay between actions"""
        min_d = min_delay or self.delay_min
        max_d = max_delay or self.delay_max
        delay = random.uniform(min_d, max_d)
        await asyncio.sleep(delay)

    async def login_linkedin(self, page: Page) -> bool:
        """
        Cookie-based login only. Uses stored cookies; if invalid or missing, send an email and stop.
        """
        try:
            print("🔐 Ensuring LinkedIn session (cookies first)...")
            cookie_data = self.cookie_manager.load_cookies()
            if cookie_data:
                applied = await self.cookie_manager.apply_cookies_to_context(page.context, cookie_data)
                if applied:
                    valid = await self.cookie_manager.test_cookie_validity(page)
                    if valid:
                        print("✅ Using stored cookies for login")
                        return True
            # No cookies or invalid — notify and stop
            print("⚠️ No valid cookies found. Sending email notification for manual login...")
            try:
                self.email_notifier.send_cookie_expiry_notification()
            except Exception as e:
                print(f"⚠️ Failed to send email notification: {e}")
            print("👉 Please run: python cookie_manager.py and choose option 1 to refresh cookies.")
            return False
        except Exception as e:
            print(f"❌ Error during cookie-based login: {str(e)}")
            try:
                self.email_notifier.send_cookie_expiry_notification()
            except Exception:
                pass
            return False

    async def search_posts(self, page: Page, keywords: List[str]) -> bool:
        """
        Search for posts using specified keywords
        
        Args:
            page: Playwright page object
            keywords: List of search keywords
            
        Returns:
            bool: True if search was successful
        """
        try:
            # Combine keywords into search query
            search_query = ' OR '.join([f'"{keyword.strip()}"' for keyword in keywords])
            sort_param = '&sortBy=R' if self.sort_by_recent else ''
            search_url = f"https://www.linkedin.com/search/results/content/?keywords={search_query}{sort_param}"
            
            print(f"🔍 Searching for posts with keywords: {', '.join(keywords)}")
            await page.goto(search_url, wait_until='networkidle')
            await self.human_delay(self.delay_min, self.delay_max)
            
            return True
            
        except Exception as e:
            print(f"❌ Error during search: {str(e)}")
            return False

    async def scroll_page(self, page: Page, max_scrolls: int = 10) -> None:
        """
        Scroll the page to load more posts
        
        Args:
            page: Playwright page object
            max_scrolls: Maximum number of scroll attempts
        """
        print(f"📜 Starting to scroll page (max {max_scrolls} scrolls)...")
        
        for i in range(max_scrolls):
            # Scroll to bottom
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self.human_delay(self.delay_min, self.delay_max)
            
            # Check if "Show more results" button exists and click it
            try:
                load_more_button = await page.query_selector(self.selectors['load_more'])
                if load_more_button:
                    await load_more_button.click()
                    await self.human_delay(self.delay_min, self.delay_max)
                    print(f"📄 Clicked 'Show more results' button (scroll {i+1})")
                else:
                    print(f"📄 Scrolled page {i+1}/{max_scrolls}")
            except:
                print(f"📄 Scrolled page {i+1}/{max_scrolls}")
            
            # Check if we've reached the end or have enough posts
            posts_count = len(await page.query_selector_all(self.selectors['post_container']))
            if posts_count >= self.max_posts:
                print(f"✅ Reached target of {self.max_posts} posts")
                break

    async def parse_posts(self, page: Page) -> List[Dict]:
        """
        Parse and extract data from LinkedIn posts
        
        Args:
            page: Playwright page object
            
        Returns:
            List of dictionaries containing post data
        """
        print("📊 Parsing posts data...")
        posts_data = []
        
        # Find all post containers
        post_elements = await page.query_selector_all(self.selectors['post_container'])
        print(f"🔍 Found {len(post_elements)} posts to parse")
        
        for i, post_element in enumerate(post_elements[:self.max_posts]):
            try:
                post_data = {}
                
                # Extract post content with multiple selectors
                content_selectors = [
                    '.feed-shared-text',
                    '.feed-shared-inline-show-more-text', 
                    '.update-components-text',
                    '.feed-shared-update-v2__commentary',
                    '[data-test-id="main-feed-activity-card"] .feed-shared-text'
                ]
                post_data['content'] = await get_inner_text_first(post_element, content_selectors)
                
                # Extract author name with multiple selectors
                # Extract author name with more specific selectors
                author_selectors = [
                    '.feed-shared-actor__name .visually-hidden',
                    '.feed-shared-actor__name a',
                    '.update-components-actor__name a',
                    '.feed-shared-actor__name span[aria-hidden="true"]',
                    '.feed-shared-actor__name',
                    '[data-test-id="post-author-name"]'
                ]
                post_data['author_name'] = await get_inner_text_first(post_element, author_selectors)
                
                # Extract author title (job title, not follower count)
                title_selectors = [
                    '.feed-shared-actor__description .visually-hidden',  # Screen reader description
                    '.feed-shared-actor__description',  # Main description
                    '.update-components-actor__description',  # Alternative description
                    '.feed-shared-actor__sub-description .visually-hidden',  # Sub description screen reader
                ]
                author_title = await get_inner_text_first(post_element, title_selectors)
                if any(w in author_title.lower() for w in ['followers', 'connections']):
                    author_title = ''
                post_data['author_title'] = author_title
                
                # Extract post date with multiple selectors and formats
                post_date = ""
                date_selectors = [
                    '.feed-shared-actor__sub-description time',  # Time element in sub-description
                    '.update-components-actor__sub-description time',  # Alternative time element
                    'time[datetime]',  # Any time element with datetime attribute
                    '.feed-shared-actor__sub-description a',  # Date link in sub-description
                    '.update-components-actor__sub-description a',  # Alternative date link
                ]
                
                for selector in date_selectors:
                    try:
                        date_element = await post_element.query_selector(selector)
                        if date_element:
                            # Try to get datetime attribute first (most reliable)
                            date_attr = await date_element.get_attribute('datetime')
                            if date_attr:
                                post_date = date_attr
                                break
                            
                            # Fallback to text content
                            date_text = await date_element.inner_text()
                            if date_text and date_text.strip():
                                post_date = date_text.strip()
                                break
                    except:
                        continue
                
                post_data['post_date'] = post_date
                
                # Extract likes/reactions count with multiple selectors
                likes_count = 0
                likes_selectors = [
                    'button[aria-label*="reaction"]',
                    '.social-counts-reactions__count',
                    '.feed-shared-social-action-bar__reaction-count',
                    'button[data-control-name="reactions_count"]'
                ]
                
                for selector in likes_selectors:
                    try:
                        likes_element = await post_element.query_selector(selector)
                        if likes_element:
                            likes_text = await likes_element.get_attribute('aria-label') or await likes_element.inner_text()
                            if likes_text:
                                likes_count = self._extract_number(likes_text)
                                if likes_count > 0:
                                    break
                    except:
                        continue
                
                post_data['likes_count'] = likes_count
                
                # Extract comments count with multiple selectors
                comments_count = 0
                comments_selectors = [
                    'button[aria-label*="comment"]',
                    '.social-counts-comments__count',
                    'button[data-control-name="comments"]'
                ]
                
                for selector in comments_selectors:
                    try:
                        comments_element = await post_element.query_selector(selector)
                        if comments_element:
                            comments_text = await comments_element.get_attribute('aria-label') or await comments_element.inner_text()
                            if comments_text:
                                comments_count = self._extract_number(comments_text)
                                if comments_count > 0:
                                    break
                    except:
                        continue
                
                post_data['comments_count'] = comments_count
                
                # Extract image URLs (only actual post images, not profile pics)
                image_elements = await post_element.query_selector_all('img[src*="media.licdn.com"], img[src*="dms.licdn.com"]')
                image_urls = []
                for img_element in image_elements:
                    img_src = await img_element.get_attribute('src')
                    if img_src and '/media/' in img_src:  # Only actual media images
                        image_urls.append(img_src)
                
                post_data['image_urls'] = image_urls
                
                # Extract post URL
                post_url = ""
                
                # Method 1: Look for direct post links in the post
                post_link_selectors = [
                    'a[href*="/posts/"]',  # Direct post links
                    '.feed-shared-text-view a[href*="/posts/"]',  # Links within text
                    '.feed-shared-header a[href*="/posts/"]',  # Header links
                    'a[href*="/feed/update/"]',  # Activity update links
                ]
                
                for selector in post_link_selectors:
                    try:
                        link_element = await post_element.query_selector(selector)
                        if link_element:
                            href = await link_element.get_attribute('href')
                            if href and ('/posts/' in href or '/feed/update/' in href):
                                # Convert relative URLs to absolute
                                if href.startswith('/'):
                                    post_url = f"https://www.linkedin.com{href}"
                                elif 'linkedin.com' in href:
                                    post_url = href
                                break
                    except:
                        continue
                
                # Method 2: Look for share links that contain the post ID
                if not post_url:
                    try:
                        share_element = await post_element.query_selector('button[aria-label*="Share"], .share-via-app-button, .share-actions button')
                        if share_element:
                            # Sometimes share buttons have data attributes with the post ID
                            onclick = await share_element.get_attribute('onclick') or ''
                            if 'activity:' in onclick:
                                activity_id = onclick.split('activity:')[1].split(',')[0].strip('"\'')
                                post_url = f"https://www.linkedin.com/feed/update/urn:li:activity:{activity_id}/"
                    except:
                        pass
                
                # Method 3: Extract from data-urn attributes and construct proper LinkedIn URL
                if not post_url:
                    try:
                        # Look for elements with URN data
                        urn_selectors = [
                            '[data-urn*="activity:"]',
                            '[data-activity-urn]',
                            '.feed-shared-update-v2',
                            '.feed-shared-activity'
                        ]
                        
                        for urn_selector in urn_selectors:
                            urn_element = await post_element.query_selector(urn_selector)
                            if urn_element:
                                urn = await urn_element.get_attribute('data-urn') or await urn_element.get_attribute('data-activity-urn')
                                if urn and 'activity:' in urn:
                                    # Extract activity ID from URN like "urn:li:activity:1234567890"
                                    activity_id = urn.split('activity:')[1].split(',')[0]
                                    # Use LinkedIn's feed update URL format
                                    post_url = f"https://www.linkedin.com/feed/update/urn:li:activity:{activity_id}/"
                                    break
                    except:
                        pass
                
                # Method 4: Try to find permalink or timestamp links
                if not post_url:
                    try:
                        timestamp_element = await post_element.query_selector('.feed-shared-actor__sub-description a, .update-components-actor__sub-description a')
                        if timestamp_element:
                            href = await timestamp_element.get_attribute('href')
                            if href:
                                if href.startswith('/'):
                                    post_url = f"https://www.linkedin.com{href}"
                                elif 'linkedin.com' in href:
                                    post_url = href
                    except:
                        pass
                
                post_data['post_url'] = post_url
                post_data['scraped_at'] = datetime.now().isoformat()
                
                # 🚀 ENHANCEMENT: Apply our new features
                enhanced_post_data = enhance_post_data(post_data)
                posts_data.append(enhanced_post_data)
                
                if (i + 1) % 10 == 0:
                    print(f"✅ Parsed {i + 1} posts...")
                    
            except Exception as e:
                print(f"⚠️  Error parsing post {i+1}: {str(e)}")
                continue
        
    posts_data = clean_posts(dedupe_posts(posts_data))
    print(f"✅ Successfully parsed {len(posts_data)} posts")
    return posts_data

    def _extract_number(self, text: str) -> int:
        """Extract number from text (e.g., '15 reactions', '1.2K likes' -> 1200)"""
        if not text:
            return 0
        
        # Clean the text and convert to uppercase for easier parsing
        clean_text = re.sub(r'[^\d.,KMB]', '', text.upper())
        
        if not clean_text:
            return 0
        
        try:
            if 'K' in clean_text:
                number = float(clean_text.replace('K', '').replace(',', '.'))
                return int(number * 1000)
            elif 'M' in clean_text:
                number = float(clean_text.replace('M', '').replace(',', '.'))
                return int(number * 1000000)
            elif 'B' in clean_text:
                number = float(clean_text.replace('B', '').replace(',', '.'))
                return int(number * 1000000000)
            else:
                # Handle comma-separated numbers
                number_str = clean_text.replace(',', '')
                return int(float(number_str)) if number_str else 0
        except (ValueError, TypeError):
            # Fallback: extract first number found
            numbers = re.findall(r'\d+', text)
            return int(numbers[0]) if numbers else 0

    async def download_images(self, posts_data: List[Dict]) -> None:
        """
        Download images from posts and save locally
        
        Args:
            posts_data: List of post data dictionaries
        """
        if not any(post.get('image_urls') for post in posts_data):
            print("📷 No images found to download")
            return
        
        print("📷 Starting image downloads...")
        
        async with aiohttp.ClientSession() as session:
            for i, post in enumerate(posts_data):
                image_urls = post.get('image_urls', [])
                image_files = []
                
                for j, img_url in enumerate(image_urls):
                    try:
                        async with self.throttler:
                            # Create filename
                            filename = f"post_{i+1}_image_{j+1}.jpg"
                            filepath = os.path.join(self.output_dir, self.images_dir, filename)
                            
                            # Download image
                            async with session.get(img_url) as response:
                                if response.status == 200:
                                    content = await response.read()
                                    async with aiofiles.open(filepath, 'wb') as f:
                                        await f.write(content)
                                    
                                    image_files.append(filepath)
                                    print(f"📸 Downloaded: {filename}")
                                
                    except Exception as e:
                        print(f"❌ Error downloading image {img_url}: {str(e)}")
                
                post['image_files'] = image_files
        
        total_images = sum(len(post.get('image_files', [])) for post in posts_data)
        print(f"✅ Downloaded {total_images} images")

    async def save_to_csv(self, posts_data: List[Dict]) -> None:
        """
        Save scraped data to CSV file using pandas
        
        Args:
            posts_data: List of post data dictionaries
        """
        if not posts_data:
            print("❌ No data to save")
            return
        
        try:
            # Prepare data for CSV with enhanced fields
            csv_data = []
            for post in posts_data:
                csv_row = {
                    # Original fields
                    'content': post.get('content', ''),
                    'author_name': post.get('author_name', ''),
                    'author_title': post.get('author_title', ''),
                    'post_date': post.get('post_date', ''),
                    'post_url': post.get('post_url', ''),
                    'likes_count': post.get('likes_count', 0),
                    'comments_count': post.get('comments_count', 0),
                    'image_urls': '; '.join(post.get('image_urls', [])),
                    'scraped_at': post.get('scraped_at', ''),
                    
                    # 🚀 NEW ENHANCED FIELDS
                    'author_firstName': post.get('author_firstName', ''),
                    'author_lastName': post.get('author_lastName', ''),
                    'hashtags': '; '.join(post.get('hashtags', [])),
                    'mentions': '; '.join(post.get('mentions', [])),
                    'postedAtISO': post.get('postedAtISO', ''),
                    'timeSincePosted': post.get('timeSincePosted', ''),
                    'post_type': post.get('post_type', ''),
                    'enhanced_at': post.get('enhanced_at', ''),
                }
                csv_data.append(csv_row)
            
            # Create DataFrame and save to CSV
            df = pd.DataFrame(csv_data)
            csv_path = os.path.join(self.output_dir, self.csv_filename)
            df.to_csv(csv_path, index=False, encoding='utf-8')
            
            print(f"💾 Data saved to: {csv_path}")
            print(f"📊 Total posts saved: {len(csv_data)}")
            
        except Exception as e:
            print(f"❌ Error saving to CSV: {str(e)}")

    async def main(self) -> None:
        """
        Main orchestrator function that runs the complete scraping workflow
        """
        print("🚀 Starting LinkedIn Posts Scraper")
        print("=" * 50)

        # Cookie-first flow (credentials not required). If cookies are invalid, you'll get an email.
        print("🔒 Cookie-based authentication enabled. If cookies are expired, you'll receive an email to refresh them.")

        if not self.search_keywords or not self.search_keywords[0]:
            print("⚠️ No search keywords specified - will scrape from main feed")
            use_main_feed = True
        else:
            use_main_feed = False
        
        async with async_playwright() as p:
            # Launch browser
            print(f"🌐 Launching browser (headless: {self.headless})...")
            proxy_arg = None
            if self.enable_proxies and self.proxy_rotator.has_proxies():
                nxt = self.proxy_rotator.next()
                if nxt:
                    proxy_arg = {'server': f'http://{nxt}' if not nxt.startswith('http') else nxt}
                    print(f"🛡️ Using proxy: {nxt}")
            browser = await p.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-blink-features=AutomationControlled'],
                proxy=proxy_arg
            )
            
            # Create context with realistic user agent
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1366, 'height': 850},
                locale='en-GB',
                timezone_id='Europe/London'
            )
            
            page = await context.new_page()
            page.set_default_timeout(self.browser_timeout)
            
            try:
                # Step 1: Ensure session via cookies
                if not await self.login_linkedin(page):
                    return
                
                # Step 2: Search for posts or go to main feed
                if use_main_feed:
                    print("📱 Navigating to LinkedIn main feed...")
                    await page.goto("https://www.linkedin.com/feed/", wait_until='domcontentloaded')
                    await page.wait_for_timeout(5000)  # Wait for content to load
                    print("✅ Reached LinkedIn feed!")
                else:
                    if not await self.search_posts(page, self.search_keywords):
                        return
                
                # Step 3: Scroll to load more posts
                await self.scroll_page(page, max_scrolls=self.scrolls)
                
                # Step 4: Parse posts data
                posts_data = await self.parse_posts(page)
                
                if not posts_data:
                    print("❌ No posts found to process")
                    return
                
                # Step 5: Download images
                await self.download_images(posts_data)
                
                # Step 6: Save to CSV
                await self.save_to_csv(posts_data)
                
                print("=" * 50)
                print("✅ Scraping completed successfully!")
                
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")
                
            finally:
                await browser.close()


# Optional: OpenAI content ideas generator
async def generate_content_ideas(scraped_posts: List[Dict], api_key: str) -> List[str]:
    """
    Generate content ideas based on scraped posts using OpenAI GPT-4
    
    Args:
        scraped_posts: List of scraped post data
        api_key: OpenAI API key
        
    Returns:
        List of content idea suggestions
    """
    try:
        import openai
        openai.api_key = api_key
        
        # Prepare prompt with top posts content
        top_posts = sorted(scraped_posts, key=lambda x: x.get('likes_count', 0), reverse=True)[:5]
        posts_content = "\n\n".join([post.get('content', '')[:200] for post in top_posts])
        
        prompt = f"""
        Based on these popular LinkedIn posts, generate 5 content ideas for similar engaging posts:
        
        {posts_content}
        
        Please provide 5 specific, actionable content ideas that would likely perform well on LinkedIn.
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        ideas = response.choices[0].message.content.strip().split('\n')
        return [idea.strip() for idea in ideas if idea.strip()]
        
    except Exception as e:
        print(f"❌ Error generating content ideas: {str(e)}")
        return []


if __name__ == "__main__":
    # Create and run the scraper
    scraper = LinkedInScraper()
    asyncio.run(scraper.main())
