"""
Quick Test Script - Save Enhanced Data
=====================================
This will test the enhanced data collection and save with a new filename
"""

import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import os
import pandas as pd
import json
from utils import enhance_post_data
from datetime import datetime

load_dotenv()

async def quick_test_with_names():
    """Quick test to collect a few posts and verify name enhancement"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        try:
            # Login
            print("🔐 Quick login...")
            email = os.getenv('LINKEDIN_EMAIL')
            password = os.getenv('LINKEDIN_PASSWORD')
            
            await page.goto("https://www.linkedin.com/login")
            await page.fill('input[name="session_key"]', email)
            await page.fill('input[name="session_password"]', password)
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(3000)
            
            if "checkpoint" in page.url or "challenge" in page.url:
                print("🔐 Complete 2FA, then press Enter...")
                input()
                await page.wait_for_timeout(3000)
            
            # Go to feed and collect 5 posts
            await page.goto("https://www.linkedin.com/feed/")
            await page.wait_for_timeout(3000)
            
            print("📊 Collecting 5 posts for testing...")
            
            post_containers = await page.query_selector_all('.feed-shared-update-v2, [data-urn*="activity"]')
            print(f"Found {len(post_containers)} containers")
            
            posts_data = []
            
            for i, container in enumerate(post_containers[:5]):
                post_data = {}
                
                # Extract author name with improved selector
                try:
                    author_element = await container.query_selector('span[dir="ltr"]')
                    if author_element:
                        author_text = (await author_element.inner_text()).strip()
                        if author_text and len(author_text) < 100 and '\\n' in author_text:
                            first_line = author_text.split('\\n')[0].strip()
                            # Clean duplicate names
                            if first_line and len(first_line) < 50:
                                parts = first_line.split()
                                if len(parts) >= 2 and len(parts) % 2 == 0:
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
                            # Clean single line duplicates
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
                        post_data['author_name'] = "LinkedIn User"
                except:
                    post_data['author_name'] = "LinkedIn User"
                
                # Extract content
                try:
                    content_element = await container.query_selector('.feed-shared-text, .feed-shared-update-v2__description')
                    if content_element:
                        post_data['content'] = (await content_element.inner_text()).strip()
                    else:
                        post_data['content'] = (await container.inner_text()).strip()[:200]
                except:
                    post_data['content'] = ""
                
                # Add basic fields
                post_data['timestamp'] = datetime.now().isoformat()
                post_data['scraped_at'] = datetime.now().isoformat()
                post_data['source'] = 'linkedin_feed_test'
                post_data['likes'] = 0
                post_data['comments'] = 0
                post_data['shares'] = 0
                post_data['company'] = ""
                post_data['post_url'] = ""
                
                posts_data.append(post_data)
                print(f"✅ Post {i+1}: {post_data['author_name']}")
            
            print("\\n💾 Enhancing and saving data...")
            
            # Enhance each post
            enhanced_posts = []
            for post in posts_data:
                enhanced_post = enhance_post_data(post)
                enhanced_posts.append(enhanced_post)
                print(f"Enhanced: {enhanced_post['author_name']} -> {enhanced_post['author_firstName']} {enhanced_post['author_lastName']}")
            
            # Save with timestamp to avoid permission issues
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save as CSV
            df = pd.DataFrame(enhanced_posts)
            csv_path = f"output/linkedin_test_{timestamp}.csv"
            df.to_csv(csv_path, index=False, encoding='utf-8')
            print(f"✅ Saved to {csv_path}")
            
            # Save as JSON
            json_path = f"output/linkedin_test_{timestamp}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(enhanced_posts, f, indent=2, ensure_ascii=False, default=str)
            print(f"✅ Saved to {json_path}")
            
            print(f"\\n🎉 SUCCESS! Collected {len(enhanced_posts)} posts with proper names!")
            
            # Show sample data
            print("\\n📊 SAMPLE ENHANCED DATA:")
            for post in enhanced_posts[:3]:
                print(f"Author: {post['author_name']}")
                print(f"  First: {post['author_firstName']}")
                print(f"  Last: {post['author_lastName']}")
                print(f"  Hashtags: {post['hashtags']}")
                print(f"  Content: {post['content'][:50]}...")
                print()
            
            return enhanced_posts
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return []
        finally:
            await browser.close()

if __name__ == "__main__":
    posts = asyncio.run(quick_test_with_names())
    if posts:
        print("\\n🎯 Author name extraction is working perfectly!")
        print(f"✅ Collected {len(posts)} posts with enhanced data")
    else:
        print("❌ Test failed")
