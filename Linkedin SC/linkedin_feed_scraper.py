"""
LinkedIn Feed Scraper - Enhanced Version
========================================

This scraper works by extracting posts from your LinkedIn feed instead of search.
Since LinkedIn blocks automated search but allows feed access, this approach works reliably.
"""

import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from cookie_manager import LinkedInCookieManager
import os
from datetime import datetime
import json
from utils import enhance_post_data, ProxyRotator, setup_logging, dedupe_posts, clean_posts

load_dotenv()

class LinkedInFeedScraper:
    def __init__(self):
        self.posts_data = []
        self.browser = None
        self.page = None
        self.context = None
        self.cookie_manager = LinkedInCookieManager()
        # Env-driven config
        self.headless = os.getenv('HEADLESS', 'False').lower() == 'true'
        self.min_delay = float(os.getenv('MIN_DELAY', '1.5'))
        self.max_delay = float(os.getenv('MAX_DELAY', '3.5'))
        self.scroll_attempts = int(os.getenv('SCROLL_ATTEMPTS', '10'))
        self.enable_proxies = os.getenv('ENABLE_PROXIES', 'False').lower() == 'true'
        self.slow_mo_ms = int(os.getenv('SLOW_MO_MS', '400'))
        self.logger = setup_logging(os.getenv('LOG_LEVEL', 'INFO'))
        self.proxy_rotator = ProxyRotator()
        
    async def login_linkedin(self):
        """Login using stored cookies if available; optionally fall back based on env flags."""
        print("🔐 Ensuring LinkedIn session (cookies first)...")
        cookie_only = os.getenv('COOKIE_ONLY', 'false').lower() == 'true'
        interactive = os.getenv('INTERACTIVE_LOGIN', 'false').lower() == 'true'

        # Try cookie-based login first
        try:
            cookie_data = self.cookie_manager.load_cookies()
            if cookie_data and self.context:
                applied = await self.cookie_manager.apply_cookies_to_context(self.context, cookie_data)
                if applied:
                    valid = await self.cookie_manager.test_cookie_validity(self.page)
                    if valid:
                        print("✅ Using stored cookies for login")
                        return True
        except Exception as e:
            print(f"⚠️ Cookie login attempt failed: {e}")

        if cookie_only:
            print("⚠️ COOKIE_ONLY is set and no valid cookies available; skipping credential login.")
            return False

        # Fallback: credential login with optional 2FA
        print("🔐 Falling back to credential login...")
        email = os.getenv('LINKEDIN_EMAIL')
        password = os.getenv('LINKEDIN_PASSWORD')
        if not email or not password:
            print("⚠️ Credentials not set; cannot perform credential login.")
            return False

        await self.page.goto("https://www.linkedin.com/login")
        await self.page.fill('input[name="session_key"]', email)
        await self.page.fill('input[name="session_password"]', password)
        await self.page.click('button[type="submit"]')
        await self.page.wait_for_timeout(3000)

        if "checkpoint" in self.page.url or "challenge" in self.page.url:
            print("🔐 2FA detected.")
            if interactive:
                print("Complete verification in browser, then press Enter...")
                try:
                    input()
                except Exception:
                    pass
                await self.page.wait_for_timeout(3000)
            else:
                print("⚠️ Non-interactive mode; skipping manual 2FA flow.")
                return False

        await self.page.goto("https://www.linkedin.com/feed/")
        await self.page.wait_for_timeout(2000)
        print("✅ Successfully logged in!")
        return True
    
    async def scroll_and_collect_posts(self, max_posts=50, scroll_attempts=10):
        """Scroll through feed and collect posts"""
        print(f"📜 Scrolling through feed to collect up to {max_posts} posts...")
        
        # Robust navigation with a quick retry
        try:
            await self.page.goto("https://www.linkedin.com/feed/", wait_until='domcontentloaded', timeout=20000)
        except Exception:
            await self.page.wait_for_timeout(1000)
            await self.page.goto("https://www.linkedin.com/feed/", wait_until='domcontentloaded', timeout=30000)
        
        collected_posts = 0
        scroll_count = 0
        
        while collected_posts < max_posts and scroll_count < scroll_attempts:
            # Find all post containers - updated selectors based on current LinkedIn structure
            post_containers = await self.page.query_selector_all(
                '.feed-shared-update-v2, [data-urn*="activity"], .feed-shared-update-v2--minimal-padding'
            )
            
            print(f"📊 Found {len(post_containers)} post containers on page")
            
            # Parse new posts
            for container in post_containers[collected_posts:]:
                if collected_posts >= max_posts:
                    break
                    
                post_data = await self.parse_single_post(container)
                if post_data and post_data not in self.posts_data:
                    self.posts_data.append(post_data)
                    collected_posts += 1
                    print(f"✅ Collected post {collected_posts}: {post_data.get('author_name', 'Unknown')[:30]}...")
            
            # Scroll down
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            # Anti-ban human-like delay
            delay_ms = int(1000 * self.min_delay)
            await self.page.wait_for_timeout(delay_ms)
            scroll_count += 1
            
            print(f"📜 Scroll {scroll_count}/{scroll_attempts}, Posts: {collected_posts}/{max_posts}")
        
        print(f"🎉 Collected {len(self.posts_data)} posts total!")
        return self.posts_data
    
    async def parse_single_post(self, container):
        """Parse a single post container to extract data"""
        try:
            post_data = {}
            
            # Author name - updated with correct selectors found from debugging
            try:
                # Primary selector that works - span with dir="ltr" often contains names
                author_element = await container.query_selector('span[dir="ltr"]')
                if author_element:
                    author_text = (await author_element.inner_text()).strip()
                    # Filter out long text that's clearly not a name (content vs name)
                    if author_text and len(author_text) < 100 and '\n' in author_text:
                        # Take first line which is usually the name, and clean duplicates
                        first_line = author_text.split('\n')[0].strip()
                        # Remove duplicate names (e.g., "John Smith\nJohn Smith" -> "John Smith")
                        if first_line and len(first_line) < 50:
                            # Check if it's a duplicate name pattern
                            parts = first_line.split()
                            if len(parts) >= 2 and len(parts) % 2 == 0:
                                # Check if first half equals second half (duplicate pattern)
                                mid = len(parts) // 2
                                first_half = ' '.join(parts[:mid])
                                second_half = ' '.join(parts[mid:])
                                if first_half == second_half:
                                    post_data['author_name'] = first_half
                                else:
                                    post_data['author_name'] = first_line
                            else:
                                post_data['author_name'] = first_line
                        else:
                            post_data['author_name'] = "LinkedIn User"
                    elif author_text and len(author_text) < 50:
                        # Single line name, check for duplicates
                        parts = author_text.split()
                        if len(parts) >= 2 and len(parts) % 2 == 0:
                            mid = len(parts) // 2
                            first_half = ' '.join(parts[:mid])
                            second_half = ' '.join(parts[mid:])
                            if first_half == second_half:
                                post_data['author_name'] = first_half
                            else:
                                post_data['author_name'] = author_text
                        else:
                            post_data['author_name'] = author_text
                    else:
                        post_data['author_name'] = "LinkedIn User"
                else:
                    # Fallback to profile links
                    profile_links = await container.query_selector_all('a[href*="/in/"]')
                    if profile_links:
                        link_text = await profile_links[0].inner_text()
                        if link_text and len(link_text.strip()) < 50:
                            # Take first line if multiple lines and clean duplicates
                            first_line = link_text.strip().split('\n')[0].strip()
                            post_data['author_name'] = first_line if first_line else "LinkedIn User"
                        else:
                            post_data['author_name'] = "LinkedIn User"
                    else:
                        post_data['author_name'] = "LinkedIn User"
            except Exception as e:
                print(f"⚠️ Error extracting author: {str(e)}")
                post_data['author_name'] = "LinkedIn User"
            
            # Post content - updated selectors
            try:
                content_element = await container.query_selector(
                    '.feed-shared-text, .feed-shared-update-v2__description, .update-components-text, .feed-shared-text__text-view'
                )
                if content_element:
                    post_data['content'] = (await content_element.inner_text()).strip()
                else:
                    # Try to get any text content from the container
                    post_data['content'] = (await container.inner_text()).strip()
            except Exception as e:
                print(f"⚠️ Error extracting content: {str(e)}")
                post_data['content'] = ""
            
            # Skip if no meaningful content
            if not post_data['content'] or len(post_data['content'].strip()) < 10:
                return None
            
            # Company/Organization
            try:
                company_element = await container.query_selector(
                    '.feed-shared-actor__sub-description, .update-components-actor__description'
                )
                if company_element:
                    post_data['company'] = await company_element.inner_text()
                else:
                    post_data['company'] = ""
            except:
                post_data['company'] = ""
            
            # Post URL - improved extraction
            try:
                # Try multiple approaches to find post URLs
                link_element = await container.query_selector('a[href*="/posts/"], a[href*="/activity-"], .feed-shared-control-menu__trigger')
                if link_element:
                    href = await link_element.get_attribute('href')
                    if href:
                        # Ensure full URL
                        if href.startswith('/'):
                            post_data['post_url'] = f"https://www.linkedin.com{href}"
                        else:
                            post_data['post_url'] = href
                    else:
                        post_data['post_url'] = ""
                else:
                    # Try to find any post-related link
                    all_links = await container.query_selector_all('a[href]')
                    for link in all_links:
                        href = await link.get_attribute('href')
                        if href and ('/posts/' in href or '/activity-' in href):
                            if href.startswith('/'):
                                post_data['post_url'] = f"https://www.linkedin.com{href}"
                            else:
                                post_data['post_url'] = href
                            break
                    else:
                        post_data['post_url'] = ""
            except:
                post_data['post_url'] = ""
            
            # Engagement metrics - improved selectors
            try:
                # Likes - try multiple selectors
                likes_element = await container.query_selector(
                    '[aria-label*="like"], .social-counts-reactions__count, .social-action-bar button[aria-label*="like"]'
                )
                if likes_element:
                    likes_text = await likes_element.get_attribute('aria-label')
                    if not likes_text:
                        likes_text = await likes_element.inner_text()
                    post_data['likes'] = self.extract_number(likes_text)
                else:
                    # Try counting reaction icons
                    reaction_elements = await container.query_selector_all('.reactions-icon, .like-icon')
                    post_data['likes'] = len(reaction_elements) if reaction_elements else 0
                
                # Comments - improved extraction
                comments_element = await container.query_selector(
                    '[aria-label*="comment"], .social-counts-comments, button[aria-label*="comment"]'
                )
                if comments_element:
                    comments_text = await comments_element.get_attribute('aria-label')
                    if not comments_text:
                        comments_text = await comments_element.inner_text()
                    post_data['comments'] = self.extract_number(comments_text)
                else:
                    post_data['comments'] = 0
                
                # Shares/Reposts - improved extraction
                shares_element = await container.query_selector(
                    '[aria-label*="repost"], [aria-label*="share"], .social-counts-shares, button[aria-label*="repost"]'
                )
                if shares_element:
                    shares_text = await shares_element.get_attribute('aria-label')
                    if not shares_text:
                        shares_text = await shares_element.inner_text()
                    post_data['shares'] = self.extract_number(shares_text)
                else:
                    post_data['shares'] = 0
                    
            except Exception as e:
                print(f"⚠️ Error extracting engagement: {str(e)}")
                post_data['likes'] = 0
                post_data['comments'] = 0
                post_data['shares'] = 0
            
            # Timestamp - improved extraction
            try:
                time_element = await container.query_selector(
                    'time, .feed-shared-actor__sub-description time, [data-chameleon-result-urn] time, .update-components-actor__description time'
                )
                if time_element:
                    # Try to get datetime attribute first
                    datetime_attr = await time_element.get_attribute('datetime')
                    if datetime_attr:
                        post_data['timestamp'] = datetime_attr
                    else:
                        # Get text content and try to parse
                        time_text = await time_element.inner_text()
                        post_data['timestamp'] = time_text.strip()
                else:
                    # Look for any time-related text
                    time_texts = await container.query_selector_all('span')
                    for span in time_texts:
                        text = await span.inner_text()
                        if any(word in text.lower() for word in ['ago', 'hour', 'day', 'week', 'month', 'min']):
                            post_data['timestamp'] = text.strip()
                            break
                    else:
                        post_data['timestamp'] = datetime.now().isoformat()
            except Exception as e:
                print(f"⚠️ Error extracting timestamp: {str(e)}")
                post_data['timestamp'] = datetime.now().isoformat()
            
            # Add collection metadata
            post_data['scraped_at'] = datetime.now().isoformat()
            post_data['source'] = 'linkedin_feed'
            
            return post_data
            
        except Exception as e:
            print(f"⚠️ Error parsing post: {str(e)}")
            return None
    
    def extract_number(self, text):
        """Extract numeric value from text like '1,234 likes'"""
        import re
        if not text:
            return 0
        
        # Remove commas and extract numbers
        numbers = re.findall(r'[\\d,]+', str(text))
        if numbers:
            return int(numbers[0].replace(',', ''))
        return 0
    
    async def save_data(self, filename_base="linkedin_feed_posts"):
        """Save collected data in multiple formats"""
        if not self.posts_data:
            print("❌ No data to save!")
            return
        
        print("💾 Enhancing and saving data...")
        
        # Clean, dedupe, and enhance each post with our utility functions
        enhanced_posts = []
        cleaned = clean_posts(dedupe_posts(self.posts_data))
        for post in cleaned:
            enhanced_post = enhance_post_data(post)
            enhanced_posts.append(enhanced_post)
        
        # Create output directory
        os.makedirs('output', exist_ok=True)
        
        # Save as CSV
        df = pd.DataFrame(enhanced_posts)
        csv_path = f"output/{filename_base}.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"✅ Saved {len(enhanced_posts)} posts to {csv_path}")
        
        # Save as JSON
        json_path = f"output/{filename_base}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_posts, f, indent=2, ensure_ascii=False, default=str)
        print(f"✅ Saved JSON to {json_path}")
        
        # Save as Excel
        excel_path = f"output/{filename_base}.xlsx"
        df.to_excel(excel_path, index=False)
        print(f"✅ Saved Excel to {excel_path}")
        
        # Print summary
        print(f"\\n📊 COLLECTION SUMMARY:")
        print(f"Total Posts: {len(enhanced_posts)}")
        print(f"Authors: {len(set(post.get('author_name', '') for post in enhanced_posts))}")
        print(f"Total Engagement: {sum(post.get('total_engagement', 0) for post in enhanced_posts)}")
        
        return enhanced_posts
    
    async def run_feed_scraper(self, max_posts=50, scroll_attempts=10):
        """Main execution function"""
        print("🚀 LINKEDIN FEED SCRAPER - ENHANCED VERSION")
        print("=" * 50)
        
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo_ms,
                args=['--no-blink-features=AutomationControlled'],
                proxy={ 'server': (self.proxy_rotator.next() if self.enable_proxies and self.proxy_rotator.has_proxies() else None) } if (self.enable_proxies and self.proxy_rotator.has_proxies()) else None
            )
            
            context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            self.context = context
            self.page = await context.new_page()
            
            try:
                # Login
                ok = await self.login_linkedin()
                if not ok:
                    print("⚠️ Login not established; stopping feed scrape in non-interactive mode.")
                    return []
                
                # Collect posts from feed
                posts = await self.scroll_and_collect_posts(max_posts, scroll_attempts)
                
                if posts:
                    # Save enhanced data
                    enhanced_posts = await self.save_data("feed_enhanced_posts")
                    
                    print("\n🎉 SUCCESS! Your LinkedIn feed has been scraped!")
                    print("✨ All enhancement features applied:")
                    print("   • Author name splitting (first/last)")
                    print("   • Hashtag extraction")
                    print("   • Enhanced timestamp formatting")
                    print("   • Engagement calculations")
                    print("   • Content analysis")
                    print("   • 18 total data fields!")
                    
                    return enhanced_posts
                else:
                    print("❌ No posts collected. Check your LinkedIn feed manually.")
                    return []
                    
            except Exception as e:
                print(f"❌ Error during scraping: {str(e)}")
                return []
            finally:
                if self.browser:
                    await self.browser.close()

# Demo function
async def run_feed_scraper_demo():
    """Demo function to run the feed scraper"""
    scraper = LinkedInFeedScraper()
    
    # Get user preferences
    print("🎯 LINKEDIN FEED SCRAPER SETUP")
    print("=" * 40)
    
    max_posts = input("How many posts to collect? (default: 30): ").strip()
    max_posts = int(max_posts) if max_posts.isdigit() else 30
    
    scroll_attempts = input("How many scroll attempts? (default: 8): ").strip()
    scroll_attempts = int(scroll_attempts) if scroll_attempts.isdigit() else 8
    
    print(f"\\n🚀 Starting feed scraper...")
    print(f"Target: {max_posts} posts, {scroll_attempts} scroll attempts")
    
    posts = await scraper.run_feed_scraper(max_posts, scroll_attempts)
    
    if posts:
        print(f"\n🎉 Successfully scraped {len(posts)} posts from your LinkedIn feed!")
        print("📁 Check the 'output' folder for your data files")
    else:
        print("\n😔 No posts were collected. Try:")
        print("1. Using LinkedIn manually first")
        print("2. Checking your internet connection") 
        print("3. Running again in a few hours")

if __name__ == "__main__":
    asyncio.run(run_feed_scraper_demo())
