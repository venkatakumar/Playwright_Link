"""
Simple test script to debug LinkedIn scraping
"""
import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def test_linkedin_access():
    """Test basic LinkedIn access and feed viewing"""
    
    async with async_playwright() as playwright:
        # Launch browser
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to LinkedIn
            print("🔗 Navigating to LinkedIn...")
            await page.goto("https://www.linkedin.com/login")
            await page.wait_for_load_state('networkidle')
            
            # Login
            print("📧 Entering credentials...")
            await page.fill('input[name="session_key"]', os.getenv('LINKEDIN_EMAIL'))
            await page.fill('input[name="session_password"]', os.getenv('LINKEDIN_PASSWORD'))
            await page.click('button[type="submit"]')
            
            # Wait for either home page or 2FA
            print("⏳ Waiting for login...")
            await page.wait_for_timeout(5000)  # Wait 5 seconds for page to load
            
            current_url = page.url
            print(f"📍 Current URL: {current_url}")
            
            if "challenge" in current_url or "checkpoint" in current_url:
                print("🔐 2FA required - please complete authentication in browser")
                print("⏰ Waiting 60 seconds for you to complete 2FA...")
                await page.wait_for_timeout(60000)  # Wait 60 seconds for manual 2FA
                
            # Check final URL
            current_url = page.url
            print(f"📍 Final URL: {current_url}")
            
            if "feed" in current_url or "linkedin.com/in/" in current_url or current_url == "https://www.linkedin.com/":
                print("✅ Successfully logged in!")
            else:
                print(f"⚠️ Unexpected URL: {current_url}")
            
            # Now let's check what posts are visible
            print("\n🔍 Analyzing current page structure...")
            
            # Try different post selectors
            selectors_to_test = [
                'div[data-id]',  # Original selector
                'article',       # HTML5 article tag
                '.feed-shared-update-v2',  # LinkedIn feed update
                '.update-components-text',  # Alternative
                '[data-urn]',    # URN-based elements
                '.feed-shared-text',  # Post content
            ]
            
            for selector in selectors_to_test:
                elements = await page.query_selector_all(selector)
                print(f"📊 Selector '{selector}': Found {len(elements)} elements")
                
                if len(elements) > 0 and len(elements) < 20:  # Print details for reasonable amounts
                    for i, element in enumerate(elements[:3]):  # Show first 3
                        try:
                            text = await element.text_content()
                            text_preview = text[:100] + "..." if len(text) > 100 else text
                            print(f"   Element {i+1}: {text_preview}")
                        except:
                            print(f"   Element {i+1}: [Could not get text]")
            
            # Try going to a specific search page
            print("\n🔍 Testing search functionality...")
            search_url = "https://www.linkedin.com/search/results/content/?keywords=python"
            await page.goto(search_url)
            await page.wait_for_load_state('networkidle')
            
            # Check for posts on search page
            print("📊 Checking search results...")
            for selector in selectors_to_test:
                elements = await page.query_selector_all(selector)
                print(f"🔍 Search - Selector '{selector}': Found {len(elements)} elements")
            
            print("\n⏸️ Pausing for 10 seconds - you can inspect the browser...")
            await page.wait_for_timeout(10000)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_linkedin_access())
