"""
LinkedIn Feed Diagnostic Tool
============================
This tool helps diagnose why the feed scraper isn't finding posts
"""

import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import os

load_dotenv()

async def diagnose_feed_access():
    """Diagnose LinkedIn feed access and post detection"""
    
    print("🔍 LINKEDIN FEED DIAGNOSTIC TOOL")
    print("=" * 50)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        try:
            # Step 1: Login
            print("🔐 Step 1: Logging into LinkedIn...")
            
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
                await page.wait_for_timeout(3000)
            
            print("✅ Login completed")
            
            # Step 2: Go to feed and analyze
            print("\\n🔍 Step 2: Analyzing LinkedIn Feed...")
            await page.goto("https://www.linkedin.com/feed/")
            await page.wait_for_timeout(5000)
            
            # Check current URL
            current_url = page.url
            print(f"Current URL: {current_url}")
            
            # Step 3: Try different selectors to find posts
            print("\\n📊 Step 3: Testing Post Selectors...")
            
            selectors_to_test = [
                'div[data-chameleon-result-urn]',
                '.feed-shared-update-v2',
                'div.feed-shared-update-v2__content',
                '.update-components-feed-update',
                '[data-urn]',
                '.feed-shared-update-v2--minimal-padding',
                '.artdeco-card',
                '.feed-shared-update-v2__content-wrapper',
                'div[data-urn*="activity"]'
            ]
            
            for selector in selectors_to_test:
                try:
                    elements = await page.query_selector_all(selector)
                    print(f"  {selector:<40} | Found: {len(elements)} elements")
                    
                    if len(elements) > 0:
                        # Get sample content from first element
                        try:
                            first_element = elements[0]
                            text = await first_element.inner_text()
                            preview = text[:100].replace('\\n', ' ') + "..." if text else "No text"
                            print(f"    Sample content: {preview}")
                        except:
                            print(f"    Sample content: Could not extract text")
                        
                except Exception as e:
                    print(f"  {selector:<40} | Error: {str(e)}")
            
            # Step 4: Check page content
            print("\\n📄 Step 4: General Page Analysis...")
            
            # Get page title
            title = await page.title()
            print(f"Page title: {title}")
            
            # Check for any content
            all_divs = await page.query_selector_all('div')
            print(f"Total div elements: {len(all_divs)}")
            
            # Check for LinkedIn-specific elements
            linkedin_elements = await page.query_selector_all('[class*="feed"], [class*="post"], [class*="update"]')
            print(f"LinkedIn feed-related elements: {len(linkedin_elements)}")
            
            # Check if we're being blocked or redirected
            if "linkedin.com/feed" not in current_url:
                print("⚠️ WARNING: Not on LinkedIn feed page - possible redirect")
            
            # Step 5: Try manual detection
            print("\\n🔍 Step 5: Manual Content Detection...")
            
            # Look for any text that might indicate posts
            page_content = await page.content()
            
            # Check for common LinkedIn feed indicators
            indicators = ['activity', 'post', 'shared', 'update', 'feed']
            for indicator in indicators:
                count = page_content.lower().count(indicator)
                print(f"  Text '{indicator}' appears {count} times in page")
            
            print("\\n📋 Step 6: Recommendations...")
            
            if linkedin_elements == 0:
                print("❌ No LinkedIn feed elements found")
                print("Possible causes:")
                print("  1. LinkedIn has updated their HTML structure")
                print("  2. Account may be restricted")
                print("  3. Feed may be empty")
                print("  4. JavaScript hasn't loaded completely")
                
                print("\\nSolutions to try:")
                print("  1. Wait longer for page to load")
                print("  2. Use LinkedIn manually first")
                print("  3. Check if your feed has posts when browsing manually")
                print("  4. Try different selectors")
            else:
                print(f"✅ Found {len(linkedin_elements)} potential feed elements")
                print("The scraper selectors may need updating")
            
            input("\\nPress Enter to close browser...")
            
        except Exception as e:
            print(f"❌ Error during diagnosis: {str(e)}")
            input("Press Enter to close...")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(diagnose_feed_access())
