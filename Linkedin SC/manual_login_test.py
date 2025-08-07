"""
Manual LinkedIn Login Helper
============================

This script helps you complete LinkedIn login with 2FA manually,
then tests search functionality to identify why you're getting 0 results.
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import time

load_dotenv()

async def manual_login_and_test_search():
    """Manual login helper with search testing"""
    
    print("🔐 MANUAL LINKEDIN LOGIN & SEARCH TEST")
    print("=" * 50)
    print("This will help you:")
    print("1. Complete LinkedIn login manually (including 2FA)")
    print("2. Test different search terms to see what works")
    print("3. Identify why you're getting 0 results")
    print("=" * 50)
    
    async with async_playwright() as p:
        # Launch browser in non-headless mode so you can see and interact
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            # Step 1: Navigate to LinkedIn
            print("🌐 Navigating to LinkedIn...")
            await page.goto("https://www.linkedin.com/login", wait_until="networkidle")
            
            # Enter credentials
            email = os.getenv('LINKEDIN_EMAIL')
            password = os.getenv('LINKEDIN_PASSWORD')
            
            if email and password:
                print(f"📧 Entering credentials for: {email}")
                await page.fill('input[name="session_key"]', email)
                await page.fill('input[name="session_password"]', password)
                await page.click('button[type="submit"]')
                
                print("🔑 Credentials entered. Waiting for response...")
                await page.wait_for_timeout(3000)
            
            # Check current URL to see where we are
            current_url = page.url
            print(f"📍 Current URL: {current_url}")
            
            if "checkpoint" in current_url or "challenge" in current_url:
                print("🔐 2FA DETECTED!")
                print("📱 Please complete the 2FA verification manually in the browser.")
                print("⏰ I'll wait for you to complete it...")
                print("💡 After completing 2FA, press Enter here to continue...")
                input("   Press Enter after completing 2FA...")
            
            # Wait for successful login
            print("⏳ Waiting for successful login...")
            try:
                await page.wait_for_url("**/feed/**", timeout=60000)
                print("✅ Successfully logged into LinkedIn!")
            except:
                print("⚠️ Not automatically redirected to feed. Checking current status...")
                current_url = page.url
                if "linkedin.com" in current_url and "login" not in current_url:
                    print("✅ Appears to be logged in!")
                else:
                    print("❌ Still on login page. Please complete login manually.")
                    input("   Press Enter after completing login...")
            
            # Step 2: Test search functionality
            print("\n🔍 TESTING SEARCH FUNCTIONALITY")
            print("=" * 40)
            
            # Test different search terms
            test_searches = [
                "AI",
                "automation",
                "testing", 
                "software testing",
                "automation testing",
                "AutomationTesting AIValidation"  # Your original terms
            ]
            
            for search_term in test_searches:
                print(f"\n🔍 Testing search: '{search_term}'")
                
                # Navigate to search page
                search_url = f"https://www.linkedin.com/search/results/content/?keywords={search_term.replace(' ', '+')}"
                print(f"   URL: {search_url}")
                
                try:
                    await page.goto(search_url, wait_until="networkidle", timeout=30000)
                    await page.wait_for_timeout(3000)  # Wait for results to load
                    
                    # Check for posts
                    posts = await page.query_selector_all('div[data-chameleon-result-urn]')
                    post_count = len(posts)
                    
                    print(f"   📊 Found {post_count} posts")
                    
                    if post_count > 0:
                        print(f"   ✅ SUCCESS! This search term returns results")
                        
                        # Get a sample post title for verification
                        try:
                            first_post = posts[0]
                            content_element = await first_post.query_selector('.feed-shared-text')
                            if content_element:
                                content = await content_element.inner_text()
                                preview = content[:100] + "..." if len(content) > 100 else content
                                print(f"   📄 Sample post: {preview}")
                        except:
                            print(f"   📄 Sample post content not accessible")
                    else:
                        print(f"   ❌ No posts found for this search term")
                    
                except Exception as e:
                    print(f"   ❌ Error testing search: {str(e)}")
                
                await page.wait_for_timeout(2000)  # Small delay between searches
            
            # Step 3: Recommendations
            print(f"\n💡 RECOMMENDATIONS")
            print("=" * 30)
            print("Based on the test results above:")
            print("1. Use search terms that returned results (✅)")
            print("2. Update SEARCH_KEYWORDS in .env file")
            print("3. Re-run your scraper with working terms")
            print()
            print("🔧 If 'AI' or 'automation' worked, update your .env:")
            print("   SEARCH_KEYWORDS=AI, automation, testing")
            print()
            print("Press Enter to close the browser...")
            input()
            
        except Exception as e:
            print(f"❌ Error during manual test: {str(e)}")
        finally:
            await browser.close()

async def quick_search_test():
    """Quick test of different search approaches"""
    
    print("\n🚀 QUICK SEARCH STRATEGY TEST")
    print("=" * 40)
    
    strategies = {
        "Very Broad": ["AI", "technology", "software"],
        "Broad": ["automation", "testing", "programming"], 
        "Moderate": ["software testing", "test automation", "AI testing"],
        "Specific": ["AutomationTesting", "AIValidation", "selenium testing"],
        "Your Original": ["AutomationTesting, AIValidation"]
    }
    
    print("Different search strategies to try:")
    for strategy, terms in strategies.items():
        print(f"\n📋 {strategy} Strategy:")
        for term in terms:
            search_url = f"https://www.linkedin.com/search/results/content/?keywords={term.replace(' ', '+').replace(',', '%2C+')}"
            print(f"   • '{term}': {search_url}")
    
    print(f"\n💡 RECOMMENDATION:")
    print("1. Start with 'Very Broad' terms to verify scraper works")
    print("2. Gradually get more specific") 
    print("3. Use terms that return results, then filter content after scraping")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Manual login and search testing (recommended)")
    print("2. Quick search strategy guide")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(manual_login_and_test_search())
    elif choice == "2":
        asyncio.run(quick_search_test())
    else:
        print("Invalid choice. Running search strategy guide...")
        asyncio.run(quick_search_test())
