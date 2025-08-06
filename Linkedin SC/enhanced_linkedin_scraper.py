"""
Enhanced LinkedIn Scraper with Profile and URL-based Scraping
============================================================

This enhanced version adds the missing features to match Apify's capabilities:
1. Scrape posts from specific profile URLs
2. Scrape individual posts from direct URLs  
3. Export to JSON and Excel formats
4. Enhanced search filters
"""

import asyncio
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs

from linkedin_scraper import LinkedInScraper


class EnhancedLinkedInScraper(LinkedInScraper):
    """Enhanced LinkedIn scraper with additional features"""
    
    def __init__(self):
        super().__init__()
        self.profile_urls = []
        self.post_urls = []
        self.export_format = 'csv'  # csv, json, excel
        
    def set_profile_urls(self, urls: List[str]):
        """Set list of profile URLs to scrape posts from"""
        self.profile_urls = [url.strip() for url in urls if url.strip()]
        print(f"📋 Set {len(self.profile_urls)} profile URLs for scraping")
        
    def set_post_urls(self, urls: List[str]):
        """Set list of individual post URLs to scrape"""
        self.post_urls = [url.strip() for url in urls if url.strip()]
        print(f"📋 Set {len(self.post_urls)} post URLs for scraping")
        
    def set_export_format(self, format_type: str):
        """Set export format: csv, json, or excel"""
        if format_type.lower() in ['csv', 'json', 'excel']:
            self.export_format = format_type.lower()
            print(f"📊 Export format set to: {self.export_format}")
        else:
            print(f"⚠️ Invalid format '{format_type}'. Using CSV.")
            
    async def scrape_from_profile_urls(self) -> List[Dict]:
        """Scrape posts from specific profile URLs"""
        if not self.profile_urls:
            print("❌ No profile URLs provided")
            return []
            
        all_posts = []
        print(f"🔍 Starting to scrape {len(self.profile_urls)} profiles...")
        
        for i, profile_url in enumerate(self.profile_urls, 1):
            print(f"\n📱 Scraping profile {i}/{len(self.profile_urls)}: {profile_url}")
            
            try:
                # Navigate to profile
                await self.page.goto(profile_url, wait_until='networkidle')
                await asyncio.sleep(2)
                
                # Check if we need to navigate to posts section
                current_url = self.page.url
                if '/recent-activity/' not in current_url:
                    # Try to find and click "See all activity" or navigate to posts
                    activity_url = profile_url.rstrip('/') + '/recent-activity/all/'
                    print(f"🔗 Navigating to activity page: {activity_url}")
                    await self.page.goto(activity_url, wait_until='networkidle')
                    await asyncio.sleep(2)
                
                # Scroll and extract posts from this profile
                await self.scroll_page()
                profile_posts = await self.parse_posts()
                
                # Add profile URL to each post for reference
                for post in profile_posts:
                    post['source_profile_url'] = profile_url
                    
                all_posts.extend(profile_posts)
                print(f"✅ Found {len(profile_posts)} posts from this profile")
                
                # Rate limiting between profiles
                if i < len(self.profile_urls):
                    await asyncio.sleep(3)
                    
            except Exception as e:
                print(f"❌ Error scraping profile {profile_url}: {str(e)}")
                continue
                
        print(f"\n🎉 Total posts collected from all profiles: {len(all_posts)}")
        return all_posts
        
    async def scrape_from_post_urls(self) -> List[Dict]:
        """Scrape individual posts from direct URLs"""
        if not self.post_urls:
            print("❌ No post URLs provided")
            return []
            
        all_posts = []
        print(f"🔍 Starting to scrape {len(self.post_urls)} individual posts...")
        
        for i, post_url in enumerate(self.post_urls, 1):
            print(f"\n📱 Scraping post {i}/{len(self.post_urls)}: {post_url}")
            
            try:
                # Navigate directly to the post
                await self.page.goto(post_url, wait_until='networkidle')
                await asyncio.sleep(2)
                
                # Find the post element on the individual post page
                post_selectors = [
                    '.feed-shared-update-v2',
                    '[data-urn*="activity:"]',
                    '.scaffold-layout__main .core-rail',
                    'main [role="main"]'
                ]
                
                post_element = None
                for selector in post_selectors:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        post_element = elements[0]
                        break
                        
                if not post_element:
                    print(f"❌ Could not find post content on page")
                    continue
                    
                # Extract post data from the individual post page
                post_data = await self.extract_single_post_data(post_element)
                post_data['source_post_url'] = post_url
                post_data['scraping_method'] = 'direct_url'
                
                all_posts.append(post_data)
                print(f"✅ Successfully extracted post data")
                
                # Rate limiting between posts
                if i < len(self.post_urls):
                    await asyncio.sleep(2)
                    
            except Exception as e:
                print(f"❌ Error scraping post {post_url}: {str(e)}")
                continue
                
        print(f"\n🎉 Total posts collected from URLs: {len(all_posts)}")
        return all_posts
        
    async def extract_single_post_data(self, post_element) -> Dict:
        """Extract data from a single post element (enhanced version)"""
        post_data = {
            'content': '',
            'author_name': '',
            'author_title': '',
            'author_profile_url': '',
            'company': '',
            'post_date': '',
            'post_url': '',
            'likes_count': 0,
            'comments_count': 0,
            'shares_count': 0,
            'image_urls': [],
            'hashtags': [],
            'mentions': [],
            'links': [],
            'post_type': '',
            'scraped_at': datetime.now().isoformat()
        }
        
        try:
            # Extract content
            content_selectors = [
                '.feed-shared-text .break-words',
                '.feed-shared-text',
                '.update-components-text',
                '.feed-shared-update-v2__commentary'
            ]
            
            for selector in content_selectors:
                try:
                    content_element = await post_element.query_selector(selector)
                    if content_element:
                        content = await content_element.inner_text()
                        if content and content.strip():
                            post_data['content'] = content.strip()
                            break
                except:
                    continue
                    
            # Extract enhanced author data
            await self.extract_enhanced_author_data(post_element, post_data)
            
            # Extract engagement metrics (enhanced)
            await self.extract_enhanced_engagement_data(post_element, post_data)
            
            # Extract hashtags and mentions
            await self.extract_hashtags_and_mentions(post_element, post_data)
            
            # Extract links within post
            await self.extract_post_links(post_element, post_data)
            
            # Extract post type
            post_data['post_type'] = await self.determine_post_type(post_element)
            
        except Exception as e:
            print(f"⚠️ Error extracting post data: {str(e)}")
            
        return post_data
        
    async def extract_enhanced_author_data(self, post_element, post_data: Dict):
        """Extract enhanced author information including company"""
        try:
            # Author name with better selectors
            name_selectors = [
                '.feed-shared-actor__name .visually-hidden',
                '.feed-shared-actor__name a span[aria-hidden="true"]',
                '.feed-shared-actor__name a',
                '.feed-shared-actor__name'
            ]
            
            for selector in name_selectors:
                try:
                    name_element = await post_element.query_selector(selector)
                    if name_element:
                        name = await name_element.inner_text()
                        if name and name.strip() and not name.lower().startswith('follow'):
                            post_data['author_name'] = name.strip()
                            break
                except:
                    continue
                    
            # Author profile URL
            try:
                profile_link = await post_element.query_selector('.feed-shared-actor__name a')
                if profile_link:
                    href = await profile_link.get_attribute('href')
                    if href:
                        if href.startswith('/'):
                            post_data['author_profile_url'] = f"https://www.linkedin.com{href}"
                        else:
                            post_data['author_profile_url'] = href
            except:
                pass
                
            # Author title and company
            title_selectors = [
                '.feed-shared-actor__description .visually-hidden',
                '.feed-shared-actor__description',
                '.feed-shared-actor__sub-description'
            ]
            
            for selector in title_selectors:
                try:
                    title_element = await post_element.query_selector(selector)
                    if title_element:
                        title_text = await title_element.inner_text()
                        if title_text and not any(word in title_text.lower() for word in ['followers', 'connections']):
                            # Try to split title and company
                            if ' at ' in title_text:
                                parts = title_text.split(' at ', 1)
                                post_data['author_title'] = parts[0].strip()
                                post_data['company'] = parts[1].strip()
                            else:
                                post_data['author_title'] = title_text.strip()
                            break
                except:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error extracting author data: {str(e)}")
            
    async def extract_enhanced_engagement_data(self, post_element, post_data: Dict):
        """Extract enhanced engagement metrics including shares"""
        try:
            # Likes
            like_selectors = [
                'button[aria-label*="Like"] .social-counts-reactions__count',
                '.social-counts-reactions__count',
                'button[data-control-name="like"] span'
            ]
            
            for selector in like_selectors:
                try:
                    like_element = await post_element.query_selector(selector)
                    if like_element:
                        likes_text = await like_element.inner_text()
                        post_data['likes_count'] = self.parse_count(likes_text)
                        break
                except:
                    continue
                    
            # Comments
            comment_selectors = [
                'button[aria-label*="Comment"] .social-counts__reactions-count',
                'button[data-control-name="comment"] span',
                '.social-counts__reactions-count'
            ]
            
            for selector in comment_selectors:
                try:
                    comment_element = await post_element.query_selector(selector)
                    if comment_element:
                        comments_text = await comment_element.inner_text()
                        post_data['comments_count'] = self.parse_count(comments_text)
                        break
                except:
                    continue
                    
            # Shares/Reposts
            share_selectors = [
                'button[aria-label*="Share"] span',
                'button[data-control-name="share"] span',
                '.social-counts__reshares-count'
            ]
            
            for selector in share_selectors:
                try:
                    share_element = await post_element.query_selector(selector)
                    if share_element:
                        shares_text = await share_element.inner_text()
                        post_data['shares_count'] = self.parse_count(shares_text)
                        break
                except:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error extracting engagement data: {str(e)}")
            
    async def extract_hashtags_and_mentions(self, post_element, post_data: Dict):
        """Extract hashtags and mentions from post content"""
        try:
            content = post_data.get('content', '')
            if content:
                # Extract hashtags
                import re
                hashtags = re.findall(r'#\w+', content)
                post_data['hashtags'] = list(set(hashtags))  # Remove duplicates
                
                # Extract mentions
                mentions = re.findall(r'@\w+', content)
                post_data['mentions'] = list(set(mentions))  # Remove duplicates
                
        except Exception as e:
            print(f"⚠️ Error extracting hashtags/mentions: {str(e)}")
            
    async def extract_post_links(self, post_element, post_data: Dict):
        """Extract links within the post content"""
        try:
            link_elements = await post_element.query_selector_all('a[href]')
            links = []
            
            for link_element in link_elements:
                href = await link_element.get_attribute('href')
                if href and not href.startswith('#') and 'linkedin.com' not in href:
                    # External links only
                    links.append(href)
                    
            post_data['links'] = list(set(links))  # Remove duplicates
            
        except Exception as e:
            print(f"⚠️ Error extracting links: {str(e)}")
            
    async def determine_post_type(self, post_element) -> str:
        """Determine the type of post (text, image, video, article, etc.)"""
        try:
            # Check for images
            if await post_element.query_selector('img[src*="media.licdn.com"]'):
                return 'image'
                
            # Check for videos
            if await post_element.query_selector('video'):
                return 'video'
                
            # Check for shared articles
            if await post_element.query_selector('.feed-shared-article'):
                return 'article'
                
            # Check for polls
            if await post_element.query_selector('.feed-shared-poll'):
                return 'poll'
                
            # Default to text
            return 'text'
            
        except:
            return 'unknown'
            
    def parse_count(self, count_text: str) -> int:
        """Parse engagement count text to integer"""
        if not count_text:
            return 0
            
        count_text = count_text.strip().replace(',', '')
        
        # Handle K, M suffixes
        if count_text.endswith('K'):
            return int(float(count_text[:-1]) * 1000)
        elif count_text.endswith('M'):
            return int(float(count_text[:-1]) * 1000000)
        
        try:
            return int(count_text)
        except:
            return 0
            
    async def export_data(self, posts_data: List[Dict], filename_prefix: str = "linkedin_posts"):
        """Export data in the specified format"""
        if not posts_data:
            print("❌ No data to export")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.export_format == 'csv':
            await self.export_to_csv(posts_data, f"{filename_prefix}_{timestamp}.csv")
        elif self.export_format == 'json':
            await self.export_to_json(posts_data, f"{filename_prefix}_{timestamp}.json")
        elif self.export_format == 'excel':
            await self.export_to_excel(posts_data, f"{filename_prefix}_{timestamp}.xlsx")
            
    async def export_to_json(self, posts_data: List[Dict], filename: str):
        """Export data to JSON format"""
        try:
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(posts_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Data exported to JSON: {filepath}")
        except Exception as e:
            print(f"❌ Error exporting to JSON: {str(e)}")
            
    async def export_to_excel(self, posts_data: List[Dict], filename: str):
        """Export data to Excel format"""
        try:
            import openpyxl
            df = pd.DataFrame(posts_data)
            filepath = os.path.join(self.output_dir, filename)
            df.to_excel(filepath, index=False, engine='openpyxl')
            print(f"💾 Data exported to Excel: {filepath}")
        except ImportError:
            print("❌ openpyxl not installed. Install with: pip install openpyxl")
        except Exception as e:
            print(f"❌ Error exporting to Excel: {str(e)}")
            
    async def main_enhanced(self, scraping_mode: str = 'feed'):
        """
        Enhanced main function with multiple scraping modes
        
        Args:
            scraping_mode: 'feed', 'profiles', 'urls', or 'search'
        """
        try:
            # Setup browser and login
            await self.setup_browser()
            if self.email and self.password:
                await self.login_linkedin()
            
            posts_data = []
            
            if scraping_mode == 'profiles' and self.profile_urls:
                print("🎯 Mode: Profile-based scraping")
                posts_data = await self.scrape_from_profile_urls()
                
            elif scraping_mode == 'urls' and self.post_urls:
                print("🎯 Mode: URL-based scraping")
                posts_data = await self.scrape_from_post_urls()
                
            elif scraping_mode == 'search':
                print("🎯 Mode: Search-based scraping")
                await self.search_posts()
                await self.scroll_page()
                posts_data = await self.parse_posts()
                
            else:  # Default: feed scraping
                print("🎯 Mode: Feed scraping")
                await self.navigate_to_feed()
                await self.scroll_page()
                posts_data = await self.parse_posts()
            
            # Export data in specified format
            if posts_data:
                await self.export_data(posts_data, f"linkedin_posts_{scraping_mode}")
            
        except Exception as e:
            print(f"❌ Error during scraping: {str(e)}")
        finally:
            if hasattr(self, 'browser'):
                await self.browser.close()


# Example usage and configuration
if __name__ == "__main__":
    print("🚀 Enhanced LinkedIn Scraper with Profile & URL Support")
    print("=" * 60)
    print("This enhanced scraper supports:")
    print("• Profile-based post scraping")
    print("• Direct post URL scraping")
    print("• Multiple export formats (CSV, JSON, Excel)")
    print("• Enhanced data extraction (hashtags, mentions, links)")
    print("• Company information extraction")
    print("• Post type classification")
    print()
    print("To use this enhanced scraper, import and configure:")
    print("from enhanced_linkedin_scraper import EnhancedLinkedInScraper")
    print()
    print("scraper = EnhancedLinkedInScraper()")
    print("scraper.set_profile_urls(['https://linkedin.com/in/username'])")
    print("scraper.set_export_format('json')")
    print("await scraper.main_enhanced('profiles')")
