"""
LinkedIn Scraper with 2FA Helper
=================================

This version helps handle LinkedIn's 2FA requirement and tests search functionality.
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import time

load_dotenv()

async def scraper_with_2fa_support():
    """LinkedIn scraper with 2FA support and search testing"""
    
    print("🚀 LINKEDIN SCRAPER WITH 2FA SUPPORT")
    print("=" * 50)
    
    # Get configuration
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    search_keywords = os.getenv('SEARCH_KEYWORDS', 'AI, automation, testing')
    max_posts = int(os.getenv('MAX_POSTS', 25))
    
    print(f"📧 Email: {email}")
    print(f"🔍 Search Keywords: {search_keywords}")
    print(f"📊 Max Posts: {max_posts}")
    print()
    
    async with async_playwright() as p:
        # Launch browser (non-headless so you can handle 2FA)
        print("🌐 Launching browser (visible for 2FA)...")
        browser = await p.chromium.launch(
            headless=False,  # Keep visible for 2FA
            slow_mo=500,     # Slow down for better visibility
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        try:
            # Step 1: Login with 2FA support
            print("🔐 Starting LinkedIn login...")
            await page.goto("https://www.linkedin.com/login", wait_until="networkidle")
            
            # Enter credentials
            await page.fill('input[name="session_key"]', email)
            await page.fill('input[name="session_password"]', password)
            await page.click('button[type="submit"]')
            
            print("⏳ Waiting for login response...")
            await page.wait_for_timeout(3000)
            
            # Handle 2FA if needed
            current_url = page.url
            if "checkpoint" in current_url or "challenge" in current_url:
                print("🔐 2FA DETECTED!")
                print("📱 Please complete the 2FA verification in the browser window.")
                print("⏰ Waiting for you to complete 2FA...")
                print("💡 Press Enter here AFTER completing 2FA successfully...")
                input("   Press Enter after 2FA completion...")
                
                # Wait a bit more for the redirect
                await page.wait_for_timeout(5000)
            
            # Verify login success
            try:
                await page.wait_for_url("**/feed/**", timeout=30000)
                print("✅ Successfully logged into LinkedIn!")
            except:
                current_url = page.url
                if "linkedin.com" in current_url and "login" not in current_url and "checkpoint" not in current_url:
                    print("✅ Login appears successful!")
                else:
                    print("❌ Login may have failed. Current URL:", current_url)
                    print("Please complete login manually if needed.")
                    input("Press Enter to continue...")
            
            # Step 2: Test search with current keywords
            print(f"\\n🔍 TESTING SEARCH: '{search_keywords}'")
            print("=" * 50)
            
            # Build search URL (same as scraper does)
            keywords_list = [k.strip() for k in search_keywords.split(',') if k.strip()]
            search_query = ' OR '.join(f'"{keyword}"' for keyword in keywords_list)
            
            from urllib.parse import quote_plus
            encoded_query = quote_plus(search_query)
            search_url = f"https://www.linkedin.com/search/results/content/?keywords={encoded_query}&page=1"
            
            print(f"🔗 Search URL: {search_url}")
            
            # Navigate to search
            await page.goto(search_url, wait_until="networkidle")
            await page.wait_for_timeout(5000)  # Wait for results to load
            
            # Check for posts
            posts = await page.query_selector_all('div[data-chameleon-result-urn]')
            post_count = len(posts)
            
            print(f"📊 Found {post_count} posts with search terms: {keywords_list}")
            
            if post_count == 0:
                print("❌ NO POSTS FOUND!")
                print()
                print("🔧 TRYING BROADER SEARCH TERMS...")
                
                # Test with broader terms
                broader_terms = ["AI", "automation", "testing"]
                for term in broader_terms:
                    print(f"\\n🔍 Testing broader term: '{term}'")
                    
                    broader_url = f"https://www.linkedin.com/search/results/content/?keywords={term}"
                    await page.goto(broader_url, wait_until="networkidle")
                    await page.wait_for_timeout(3000)
                    
                    broader_posts = await page.query_selector_all('div[data-chameleon-result-urn]')
                    broader_count = len(broader_posts)
                    
                    print(f"   📊 Found {broader_count} posts for '{term}'")
                    
                    if broader_count > 0:
                        print(f"   ✅ SUCCESS! '{term}' returns results")
                        
                        # Show sample content
                        try:
                            first_post = broader_posts[0]
                            content_element = await first_post.query_selector('.feed-shared-text')
                            if content_element:
                                content = await content_element.inner_text()
                                preview = content[:100] + "..." if len(content) > 100 else content
                                print(f"   📄 Sample: {preview}")
                        except:
                            pass
                        break
                    else:
                        print(f"   ❌ No posts for '{term}'")
                
                print(f"\\n💡 RECOMMENDATION:")
                print("Update your .env file with broader terms that return results:")
                print("SEARCH_KEYWORDS=AI, automation, testing")
                
            else:
                print("✅ SUCCESS! Your search terms return results")
                print("🚀 Your scraper should work with these terms")
                
                # Show sample posts
                for i in range(min(3, post_count)):
                    try:
                        post = posts[i]
                        content_element = await post.query_selector('.feed-shared-text')
                        if content_element:
                            content = await content_element.inner_text()
                            preview = content[:100] + "..." if len(content) > 100 else content
                            print(f"   📄 Post {i+1}: {preview}")
                    except:
                        print(f"   📄 Post {i+1}: [Content not accessible]")
            
            print(f"\\n🎯 NEXT STEPS:")
            print("1. If search returned results, run your scraper normally")
            print("2. If no results, update SEARCH_KEYWORDS with broader terms")
            print("3. You can filter scraped content afterwards for specific topics")
            
            input("\\nPress Enter to close browser...")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            input("Press Enter to close browser...")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scraper_with_2fa_support())
