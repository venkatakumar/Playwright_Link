"""
Author Name Extraction Debugger
===============================
This tool will help us find the correct selectors for author names in LinkedIn posts
"""

import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import os

load_dotenv()

async def debug_author_extraction():
    """Debug author name extraction from LinkedIn posts"""
    
    print("🔍 AUTHOR NAME EXTRACTION DEBUGGER")
    print("=" * 50)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        try:
            # Login
            print("🔐 Logging into LinkedIn...")
            
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
            
            # Go to feed
            await page.goto("https://www.linkedin.com/feed/")
            await page.wait_for_timeout(5000)
            
            print("✅ On LinkedIn feed, analyzing posts...")
            
            # Find post containers
            post_containers = await page.query_selector_all('.feed-shared-update-v2, [data-urn*="activity"]')
            print(f"📊 Found {len(post_containers)} post containers")
            
            # Analyze first few posts
            for i, container in enumerate(post_containers[:3]):
                print(f"\\n📄 POST {i+1} ANALYSIS:")
                print("-" * 30)
                
                # Try different selectors for author names
                author_selectors = [
                    '.feed-shared-actor__name',
                    '.feed-shared-actor__name a',
                    '.update-components-actor__name',
                    '.update-components-actor__name a',
                    '[data-chameleon-result-urn] .feed-shared-actor__name',
                    '.feed-shared-actor__name span',
                    '.feed-shared-actor__name-text',
                    '.feed-shared-actor__name .visually-hidden',
                    'span[dir="ltr"]',
                    '.feed-shared-actor .artdeco-entity-lockup__title',
                    '.artdeco-entity-lockup__title',
                    '.feed-shared-actor span span',
                ]
                
                found_names = []
                
                for selector in author_selectors:
                    try:
                        elements = await container.query_selector_all(selector)
                        for element in elements:
                            text = await element.inner_text()
                            if text and text.strip() and len(text.strip()) > 1:
                                found_names.append(f"{selector}: '{text.strip()}'")
                    except:
                        pass
                
                if found_names:
                    print("  ✅ Found potential author names:")
                    for name in found_names[:5]:  # Show first 5
                        print(f"    {name}")
                else:
                    print("  ❌ No author names found with current selectors")
                
                # Try to get all text and look for names manually
                try:
                    full_text = await container.inner_text()
                    lines = full_text.split('\\n')
                    print(f"  📝 First few lines of post:")
                    for line in lines[:5]:
                        if line.strip():
                            print(f"    '{line.strip()}'")
                except:
                    pass
                
                # Look for links that might contain profile info
                try:
                    profile_links = await container.query_selector_all('a[href*="/in/"]')
                    print(f"  🔗 Found {len(profile_links)} profile links")
                    for link in profile_links[:2]:
                        href = await link.get_attribute('href')
                        text = await link.inner_text()
                        if text and text.strip():
                            print(f"    Link text: '{text.strip()}' -> {href}")
                except:
                    pass
            
            print("\\n💡 RECOMMENDATIONS:")
            print("-" * 30)
            print("Based on the analysis above, update the scraper with:")
            print("1. The selector that consistently returns actual names")
            print("2. Proper filtering to avoid generic text")
            print("3. Fallback selectors for different post types")
            
            input("\\nPress Enter to close...")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            input("Press Enter to close...")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_author_extraction())
