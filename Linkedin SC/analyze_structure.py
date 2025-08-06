"""
Advanced LinkedIn structure analyzer
"""
import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def analyze_linkedin_structure():
    """Analyze the actual LinkedIn page structure"""
    
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate and login
            print("🔗 Navigating to LinkedIn...")
            await page.goto("https://www.linkedin.com/login")
            await page.wait_for_load_state('networkidle')
            
            # Login
            await page.fill('input[name="session_key"]', os.getenv('LINKEDIN_EMAIL'))
            await page.fill('input[name="session_password"]', os.getenv('LINKEDIN_PASSWORD'))
            await page.click('button[type="submit"]')
            
            # Wait and handle 2FA
            await page.wait_for_timeout(5000)
            current_url = page.url
            
            if "challenge" in current_url:
                print("🔐 Complete 2FA in browser...")
                await page.wait_for_timeout(60000)
            
            # Go to feed
            await page.goto("https://www.linkedin.com/feed/")
            await page.wait_for_load_state('networkidle')
            print("✅ On LinkedIn feed!")
            
            # Wait for content to load
            await page.wait_for_timeout(5000)
            
            # Get page content and analyze
            print("\n📝 Analyzing page structure...")
            
            # Check main containers
            main_selectors = [
                'main',
                '[role="main"]',
                '.scaffold-layout__main',
                '.core-rail',
                '.feed-container',
                '.application-outlet'
            ]
            
            for selector in main_selectors:
                elements = await page.query_selector_all(selector)
                print(f"🏗️ Main container '{selector}': {len(elements)} found")
            
            # Look for any divs with data attributes
            data_divs = await page.query_selector_all('div[data-*]')
            print(f"\n📊 Found {len(data_divs)} divs with data attributes")
            
            # Check for post-like structures
            post_indicators = [
                'div[data-urn]',
                'div[data-id*="urn"]',
                '[data-test-id]',
                '.feed-shared-update-v2',
                '.feed-shared-post',
                '[aria-label*="post"]',
                '[data-activity-urn]'
            ]
            
            for selector in post_indicators:
                elements = await page.query_selector_all(selector)
                print(f"📰 Post indicator '{selector}': {len(elements)} found")
                
                if len(elements) > 0:
                    # Get some sample data-* attributes
                    try:
                        first_element = elements[0]
                        attributes = await first_element.evaluate('el => Array.from(el.attributes).map(attr => attr.name + "=" + attr.value)')
                        print(f"   Sample attributes: {attributes[:3]}")
                    except:
                        pass
            
            # Check for text content areas
            text_selectors = [
                '.feed-shared-text',
                '.feed-shared-inline-show-more-text',
                '[data-test-id="main-feed-activity-card"]',
                '.update-components-text',
                '.update-components-header',
                '.feed-shared-header'
            ]
            
            for selector in text_selectors:
                elements = await page.query_selector_all(selector)
                print(f"📝 Text area '{selector}': {len(elements)} found")
            
            # Look for any recent class names
            print("\n🔍 Looking for feed-related classes...")
            all_elements = await page.query_selector_all('[class*="feed"], [class*="post"], [class*="update"], [class*="activity"]')
            print(f"📊 Found {len(all_elements)} elements with feed/post/update/activity classes")
            
            if len(all_elements) > 0:
                # Get unique class names
                class_names = set()
                for element in all_elements[:10]:  # Check first 10 elements
                    try:
                        classes = await element.get_attribute('class')
                        if classes:
                            class_names.update(classes.split())
                    except:
                        pass
                
                feed_classes = [cls for cls in class_names if any(keyword in cls.lower() for keyword in ['feed', 'post', 'update', 'activity'])]
                print(f"🏷️ Relevant classes found: {feed_classes[:10]}")
            
            # Get a sample of the HTML structure
            print("\n📋 Getting HTML sample...")
            try:
                main_content = await page.query_selector('main, [role="main"], .scaffold-layout__main')
                if main_content:
                    html_sample = await main_content.inner_html()
                    # Get first 1000 characters
                    print(f"📄 HTML sample (first 1000 chars):")
                    print(html_sample[:1000])
                    print("...")
            except Exception as e:
                print(f"Could not get HTML sample: {e}")
            
            print("\n⏸️ Pausing 15 seconds for manual inspection...")
            await page.wait_for_timeout(15000)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(analyze_linkedin_structure())
