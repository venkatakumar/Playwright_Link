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
        
        # Create output directories
        Path(self.output_dir).mkdir(exist_ok=True)
        Path(os.path.join(self.output_dir, self.images_dir)).mkdir(exist_ok=True)
        
        # Initialize data storage
        self.scraped_posts = []
        self.session = None
        self.throttler = Throttler(rate_limit=1, period=2)  # Rate limiting
        
        # Selectors (update these if LinkedIn changes their layout)
        self.selectors = {
            'email_input': 'input[name="session_key"]',
            'password_input': 'input[name="session_password"]',
            'login_button': 'button[type="submit"]',
            'search_box': 'input[placeholder*="Search"]',
            'post_container': 'div[data-id]',  # Main post container
            'post_content': '.feed-shared-text',  # Post text content
            'author_name': '.feed-shared-actor__name',  # Author name
            'author_title': '.feed-shared-actor__description',  # Author job title
            'post_date': 'time',  # Post timestamp
            'likes_count': 'button[aria-label*="reaction"]',  # Likes/reactions
            'comments_count': 'button[aria-label*="comment"]',  # Comments
            'post_images': '.feed-shared-image img',  # Post images
            'load_more': 'button[aria-label*="Show more results"]',  # Load more button
            'captcha': '.challenge-form',  # CAPTCHA detection
        }

    async def human_delay(self, min_delay: Optional[int] = None, max_delay: Optional[int] = None):
        """Add human-like delay between actions"""
        min_d = min_delay or self.delay_min
        max_d = max_delay or self.delay_max
        delay = random.uniform(min_d, max_d)
        await asyncio.sleep(delay)

    async def login_linkedin(self, page: Page) -> bool:
        """
        Log into LinkedIn using credentials from environment variables
        
        Args:
            page: Playwright page object
            
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            print("🔐 Navigating to LinkedIn login page...")
            await page.goto('https://www.linkedin.com/login', wait_until='networkidle')
            await self.human_delay()
            
            # Check for CAPTCHA
            captcha_element = await page.query_selector(self.selectors['captcha'])
            if captcha_element:
                print("⚠️  CAPTCHA detected. Please solve it manually and press Enter to continue...")
                input("Press Enter after solving CAPTCHA...")
            
            # Enter email
            print("📧 Entering email...")
            await page.fill(self.selectors['email_input'], self.email)
            await self.human_delay(1, 2)
            
            # Enter password
            print("🔑 Entering password...")
            await page.fill(self.selectors['password_input'], self.password)
            await self.human_delay(1, 2)
            
            # Click login button
            print("🚀 Clicking login button...")
            await page.click(self.selectors['login_button'])
            
            # Extended wait for 2FA/authenticator app
            print("⏳ Waiting for login response (may require 2FA/authenticator app)...")
            print("💡 If you need to use an authenticator app, please do so now...")
            
            # Wait longer for potential 2FA
            await asyncio.sleep(5)  # Initial wait
            
            # Check multiple times over configured wait time
            max_wait_attempts = self.login_wait_time // 5  # 5 second intervals
            for attempt in range(max_wait_attempts):
                current_url = page.url
                print(f"🔍 Checking login status... (attempt {attempt + 1}/{max_wait_attempts})")
                
                # Check if we're redirected to the feed (successful login)
                if 'feed' in current_url or '/in/' in current_url or 'mynetwork' in current_url:
                    print("✅ Login successful!")
                    return True
                
                # Check for 2FA challenge page
                if 'challenge' in current_url or 'checkpoint' in current_url:
                    print("🔐 Two-factor authentication detected.")
                    print("📱 Please complete the 2FA verification (authenticator app, SMS, etc.)")
                    print(f"⏰ Waiting up to {self.login_wait_time} seconds for you to complete 2FA...")
                
                # Check for error messages
                error_elements = await page.query_selector_all('.form__input--error, .alert, .error')
                if error_elements:
                    error_text = await error_elements[0].inner_text() if error_elements else ""
                    print(f"⚠️  Potential error detected: {error_text}")
                
                # Wait before next check
                await asyncio.sleep(5)
            
            # Final check after extended wait
            current_url = page.url
            if 'feed' in current_url or '/in/' in current_url or 'mynetwork' in current_url:
                print("✅ Login successful after extended wait!")
                return True
            else:
                print(f"❌ Login failed or timed out after {self.login_wait_time} seconds.")
                print(f"📍 Current URL: {current_url}")
                print("💡 If you're on a 2FA page, please complete it manually and run the scraper again.")
                return False
                
        except Exception as e:
            print(f"❌ Error during login: {str(e)}")
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
            search_url = f"https://www.linkedin.com/search/results/content/?keywords={search_query}"
            
            print(f"🔍 Searching for posts with keywords: {', '.join(keywords)}")
            await page.goto(search_url, wait_until='networkidle')
            await self.human_delay(3, 5)
            
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
            await self.human_delay(2, 4)
            
            # Check if "Show more results" button exists and click it
            try:
                load_more_button = await page.query_selector(self.selectors['load_more'])
                if load_more_button:
                    await load_more_button.click()
                    await self.human_delay(3, 5)
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
                
                # Extract post content
                content_element = await post_element.query_selector(self.selectors['post_content'])
                post_data['content'] = await content_element.inner_text() if content_element else ""
                
                # Extract author name
                author_element = await post_element.query_selector(self.selectors['author_name'])
                post_data['author_name'] = await author_element.inner_text() if author_element else ""
                
                # Extract author title/occupation
                title_element = await post_element.query_selector(self.selectors['author_title'])
                post_data['author_title'] = await title_element.inner_text() if title_element else ""
                
                # Extract post date
                date_element = await post_element.query_selector(self.selectors['post_date'])
                if date_element:
                    date_attr = await date_element.get_attribute('datetime')
                    post_data['post_date'] = date_attr if date_attr else ""
                else:
                    post_data['post_date'] = ""
                
                # Extract likes/reactions count
                likes_element = await post_element.query_selector(self.selectors['likes_count'])
                if likes_element:
                    likes_text = await likes_element.get_attribute('aria-label') or ""
                    post_data['likes_count'] = self._extract_number(likes_text)
                else:
                    post_data['likes_count'] = 0
                
                # Extract comments count
                comments_element = await post_element.query_selector(self.selectors['comments_count'])
                if comments_element:
                    comments_text = await comments_element.get_attribute('aria-label') or ""
                    post_data['comments_count'] = self._extract_number(comments_text)
                else:
                    post_data['comments_count'] = 0
                
                # Extract image URLs
                image_elements = await post_element.query_selector_all(self.selectors['post_images'])
                image_urls = []
                for img_element in image_elements:
                    img_src = await img_element.get_attribute('src')
                    if img_src:
                        image_urls.append(img_src)
                
                post_data['image_urls'] = image_urls
                post_data['image_files'] = []  # Will be populated after download
                post_data['scraped_at'] = datetime.now().isoformat()
                
                posts_data.append(post_data)
                
                if (i + 1) % 10 == 0:
                    print(f"✅ Parsed {i + 1} posts...")
                    
            except Exception as e:
                print(f"⚠️  Error parsing post {i+1}: {str(e)}")
                continue
        
        print(f"✅ Successfully parsed {len(posts_data)} posts")
        return posts_data

    def _extract_number(self, text: str) -> int:
        """Extract number from text (e.g., '15 reactions' -> 15)"""
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
            # Prepare data for CSV
            csv_data = []
            for post in posts_data:
                csv_row = {
                    'content': post.get('content', ''),
                    'author_name': post.get('author_name', ''),
                    'author_title': post.get('author_title', ''),
                    'post_date': post.get('post_date', ''),
                    'likes_count': post.get('likes_count', 0),
                    'comments_count': post.get('comments_count', 0),
                    'image_urls': '; '.join(post.get('image_urls', [])),
                    'image_files': '; '.join(post.get('image_files', [])),
                    'scraped_at': post.get('scraped_at', '')
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
        
        # Validate credentials
        if not self.email or not self.password:
            print("❌ LinkedIn credentials not found in .env file")
            return
        
        if not self.search_keywords or not self.search_keywords[0]:
            print("⚠️ No search keywords specified - will scrape from main feed")
            use_main_feed = True
        else:
            use_main_feed = False
        
        async with async_playwright() as p:
            # Launch browser
            print(f"🌐 Launching browser (headless: {self.headless})...")
            browser = await p.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
            )
            
            # Create context with realistic user agent
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            page.set_default_timeout(self.browser_timeout)
            
            try:
                # Step 1: Login to LinkedIn
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
                await self.scroll_page(page, max_scrolls=5)
                
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
