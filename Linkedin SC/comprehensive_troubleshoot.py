"""
LinkedIn Search Troubleshooter
==============================

This script will help identify exactly why search isn't working and provide solutions.
"""

import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import os

load_dotenv()

async def comprehensive_linkedin_troubleshoot():
    """Comprehensive LinkedIn search troubleshooting"""
    
    print("🔍 COMPREHENSIVE LINKEDIN SEARCH TROUBLESHOOTER")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        try:
            # Step 1: Login
            print("🔐 Step 1: Login to LinkedIn")
            print("-" * 30)
            
            email = os.getenv('LINKEDIN_EMAIL')
            password = os.getenv('LINKEDIN_PASSWORD')
            
            await page.goto("https://www.linkedin.com/login")
            await page.fill('input[name="session_key"]', email)
            await page.fill('input[name="session_password"]', password)
            await page.click('button[type="submit"]')
            
            await page.wait_for_timeout(3000)
            
            # Handle 2FA
            if "checkpoint" in page.url or "challenge" in page.url:
                print("🔐 Complete 2FA in the browser, then press Enter...")
                input()
                await page.wait_for_timeout(5000)
            
            print("✅ Login completed")
            
            # Step 2: Check if we're really logged in
            print("\\n🔍 Step 2: Verify Login Status")
            print("-" * 30)
            
            # Go to LinkedIn home/feed
            await page.goto("https://www.linkedin.com/feed/")
            await page.wait_for_timeout(3000)
            
            # Check for login indicators
            is_logged_in = False
            
            # Look for profile menu or user elements
            try:
                profile_elements = await page.query_selector_all('button[data-control-name="identity_welcome_message"]')
                if profile_elements:
                    is_logged_in = True
                    print("✅ Confirmed: Successfully logged in")
                else:
                    # Try alternative login check
                    nav_elements = await page.query_selector_all('.global-nav__me')
                    if nav_elements:
                        is_logged_in = True
                        print("✅ Confirmed: Successfully logged in (alternative check)")
            except:
                pass
            
            if not is_logged_in:
                print("❌ Warning: May not be properly logged in")
                print("Current URL:", page.url)
                print("Please ensure you're logged in manually")
                input("Press Enter to continue...")
            
            # Step 3: Test different search approaches
            print("\\n🔍 Step 3: Test Search Approaches")
            print("-" * 30)
            
            # Approach 1: Use LinkedIn's main search bar
            print("\\n📍 Testing main search bar...")
            try:
                await page.goto("https://www.linkedin.com/feed/")
                await page.wait_for_timeout(2000)
                
                # Find search box
                search_box = await page.query_selector('input[placeholder*="Search"]')
                if search_box:
                    await search_box.fill("AI")
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(3000)
                    
                    # Check for results
                    results = await page.query_selector_all('[data-chameleon-result-urn]')
                    print(f"   📊 Main search results: {len(results)}")
                    
                    if len(results) > 0:
                        print("   ✅ Main search works!")
                    else:
                        print("   ❌ No results from main search")
                else:
                    print("   ⚠️ Could not find search box")
            except Exception as e:
                print(f"   ❌ Main search error: {str(e)}")
            
            # Approach 2: Direct content search URL
            print("\\n📍 Testing direct content search...")
            try:
                # Try the simplest possible search
                simple_url = "https://www.linkedin.com/search/results/content/?keywords=AI"
                await page.goto(simple_url)
                await page.wait_for_timeout(5000)
                
                # Check current URL to see if we were redirected
                current_url = page.url
                print(f"   Current URL: {current_url}")
                
                if "search" not in current_url:
                    print("   ⚠️ Redirected away from search - LinkedIn may be blocking")
                
                # Look for posts
                posts = await page.query_selector_all('[data-chameleon-result-urn]')
                print(f"   📊 Direct search results: {len(posts)}")
                
                if len(posts) > 0:
                    print("   ✅ Direct search works!")
                    
                    # Get sample content
                    for i in range(min(2, len(posts))):
                        try:
                            post = posts[i]
                            text_element = await post.query_selector('.feed-shared-text')
                            if text_element:
                                text = await text_element.inner_text()
                                preview = text[:80] + "..." if len(text) > 80 else text
                                print(f"   📄 Sample {i+1}: {preview}")
                        except:
                            pass
                else:
                    print("   ❌ No results from direct search")
                    
                    # Check for error messages or blocks
                    error_elements = await page.query_selector_all('.search-no-results, .error-message')
                    if error_elements:
                        print("   ⚠️ LinkedIn showing 'no results' message")
                    
                    # Check if we're being blocked
                    if "checkpoint" in current_url or "challenge" in current_url:
                        print("   🚨 LinkedIn is challenging/blocking the search")
                    
            except Exception as e:
                print(f"   ❌ Direct search error: {str(e)}")
            
            # Approach 3: Try your feed instead
            print("\\n📍 Testing feed scraping as alternative...")
            try:
                await page.goto("https://www.linkedin.com/feed/")
                await page.wait_for_timeout(3000)
                
                # Look for posts in the feed
                feed_posts = await page.query_selector_all('div[data-chameleon-result-urn], .feed-shared-update-v2')
                print(f"   📊 Feed posts found: {len(feed_posts)}")
                
                if len(feed_posts) > 0:
                    print("   ✅ Feed scraping works as alternative!")
                    print("   💡 You could scrape from your feed instead of search")
                    
                    # Sample feed content
                    for i in range(min(2, len(feed_posts))):
                        try:
                            post = feed_posts[i]
                            text_element = await post.query_selector('.feed-shared-text')
                            if text_element:
                                text = await text_element.inner_text()
                                preview = text[:80] + "..." if len(text) > 80 else text
                                print(f"   📄 Feed Sample {i+1}: {preview}")
                        except:
                            pass
                else:
                    print("   ❌ No posts in feed either")
                    
            except Exception as e:
                print(f"   ❌ Feed test error: {str(e)}")
            
            # Step 4: Diagnosis and recommendations
            print("\\n🎯 Step 4: Diagnosis & Recommendations")
            print("-" * 30)
            
            print("\\n🔍 POSSIBLE ISSUES:")
            print("1. 🚫 LinkedIn Account Restrictions")
            print("   • New account or limited account")
            print("   • Search rate limiting")
            print("   • Geographic restrictions")
            print()
            print("2. 🤖 Bot Detection")
            print("   • LinkedIn detected automated activity")
            print("   • Need to use account manually first")
            print("   • Too many automation attempts")
            print()
            print("3. ⚙️ Technical Issues")
            print("   • Browser automation detected")
            print("   • Wrong selectors for current LinkedIn version")
            print("   • Network/connection issues")
            
            print("\\n💡 RECOMMENDED SOLUTIONS:")
            print("1. 🔧 Manual Account Usage")
            print("   • Use LinkedIn manually for a few days")
            print("   • Post, like, comment normally")
            print("   • Build account trust")
            print()
            print("2. 🕰️ Wait and Retry")
            print("   • Wait 24-48 hours")
            print("   • Try again with different search terms")
            print("   • Use account manually between attempts")
            print()
            print("3. 🎯 Alternative Approach")
            print("   • Scrape from your feed instead of search")
            print("   • Use company pages")
            print("   • Try different time of day")
            print()
            print("4. 🔄 Account Reset")
            print("   • Log out and back in manually")
            print("   • Clear browser cache")
            print("   • Try from different IP/location")
            
            input("\\nPress Enter to close browser and see final recommendations...")
            
        except Exception as e:
            print(f"❌ Error during troubleshooting: {str(e)}")
            input("Press Enter to close...")
        finally:
            await browser.close()
            
    # Final recommendations
    print("\\n🎯 FINAL RECOMMENDATIONS BASED ON RESULTS")
    print("=" * 50)
    print()
    print("If search didn't work:")
    print("1. 🕰️ WAIT: Use LinkedIn manually for 1-2 days")
    print("2. 🔄 TRY FEED: Scrape from feed instead of search")
    print("3. ⏰ TIMING: Try different times of day")
    print("4. 🌐 NETWORK: Try different internet connection")
    print()
    print("If you saw posts in feed but not search:")
    print("• LinkedIn is blocking search automation")
    print("• Feed scraping is still possible")
    print("• This is common with new automation detection")
    print()
    print("Would you like me to create a feed-based scraper instead?")

if __name__ == "__main__":
    asyncio.run(comprehensive_linkedin_troubleshoot())
