"""
Human-Like LinkedIn Cookie Extractor
===================================

Enhanced cookie extractor with human-like browser behavior to avoid LinkedIn detection
"""

import asyncio
import json
import random
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
import logging

class HumanLikeLinkedInCookieManager:
    """LinkedIn cookie manager with human-like browser behavior"""
    
    def __init__(self, cookie_file='linkedin_cookies.json'):
        self.cookie_file = Path(cookie_file)
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('cookie_manager.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    async def human_delay(self, min_ms=500, max_ms=2000):
        """Add random human-like delay"""
        delay = random.randint(min_ms, max_ms) / 1000
        await asyncio.sleep(delay)
    
    async def human_type(self, page, selector, text, delay_range=(50, 150)):
        """Type text with human-like delays"""
        element = await page.wait_for_selector(selector)
        await element.click()
        await self.human_delay(300, 800)
        
        for char in text:
            await element.type(char)
            delay = random.randint(delay_range[0], delay_range[1]) / 1000
            await asyncio.sleep(delay)
    
    async def extract_cookies_human_like(self):
        """Extract cookies with human-like behavior"""
        
        print("🤖 HUMAN-LIKE LINKEDIN COOKIE EXTRACTION")
        print("=" * 45)
        print("This uses human-like behavior to avoid LinkedIn security detection")
        print("-" * 60)
        
        async with async_playwright() as p:
            # Launch browser with human-like settings
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--no-first-run',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--start-maximized'
                ]
            )
            
            # Create context with realistic settings
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
                geolocation={'longitude': -74.006, 'latitude': 40.7128},  # New York
                permissions=['geolocation']
            )
            
            # Add extra properties to make browser look more human
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                window.chrome = {
                    runtime: {},
                };
            """)
            
            page = await context.new_page()
            
            try:
                print("\\n1️⃣ Navigating to LinkedIn with human-like behavior...")
                
                # First visit LinkedIn homepage (more human-like)
                await page.goto('https://www.linkedin.com', wait_until='networkidle')
                await self.human_delay(2000, 4000)
                
                # Scroll a bit (human-like behavior)
                await page.evaluate('window.scrollBy(0, 300)')
                await self.human_delay(1000, 2000)
                
                # Now go to login page
                await page.goto('https://www.linkedin.com/login', wait_until='networkidle')
                await self.human_delay(3000, 5000)
                
                print("\\n2️⃣ LinkedIn login page loaded")
                print("\\n🔐 MANUAL LOGIN INSTRUCTIONS:")
                print("-" * 35)
                print("✅ The browser window is now open")
                print("✅ LinkedIn login page is loaded")
                print("✅ Browser has human-like settings to avoid detection")
                print("\\n👉 Please complete these steps in the browser:")
                print("   1. Enter your LinkedIn email/username")
                print("   2. Enter your password")
                print("   3. Click 'Sign in'")
                print("   4. Complete any security challenges (CAPTCHA, 2FA)")
                print("   5. Wait until you see your LinkedIn feed/home page")
                print("   6. Then return here and press Enter")
                
                print("\\n⚠️ IMPORTANT TIPS:")
                print("• Take your time - don't rush the login")
                print("• Act naturally as if you're browsing normally")
                print("• If you see security challenges, complete them carefully")
                print("• The browser settings should help avoid detection")
                
                input("\\n🔄 Press Enter ONLY after you've successfully logged in and see your LinkedIn feed...")
                
                # Give some time for the page to fully load
                await self.human_delay(2000, 3000)
                
                print("\\n3️⃣ Extracting LinkedIn cookies...")
                
                # Check if we're actually logged in
                current_url = page.url
                print(f"Current URL: {current_url}")
                
                if 'feed' in current_url or 'in.linkedin.com' in current_url:
                    print("✅ Detected successful login!")
                else:
                    print("⚠️ Login may not be complete, but continuing with cookie extraction...")
                
                # Extract all cookies for LinkedIn domain
                cookies = await context.cookies()
                linkedin_cookies = [
                    cookie for cookie in cookies 
                    if 'linkedin.com' in cookie.get('domain', '')
                ]
                
                # Find the main session cookie
                li_at_cookie = None
                for cookie in linkedin_cookies:
                    if cookie['name'] == 'li_at':
                        li_at_cookie = cookie
                        break
                
                if li_at_cookie:
                    print(f"✅ Found LinkedIn session cookie!")
                    print(f"   Cookie name: {li_at_cookie['name']}")
                    print(f"   Domain: {li_at_cookie['domain']}")
                    print(f"   Total LinkedIn cookies: {len(linkedin_cookies)}")
                    
                    # Save cookies
                    cookie_data = {
                        'cookies': linkedin_cookies,
                        'saved_at': datetime.now().isoformat(),
                        'expires_estimate': (datetime.now().replace(day=28) if datetime.now().day < 28 else datetime.now().replace(month=datetime.now().month+1, day=28)).isoformat(),
                        'metadata': {
                            'extraction_method': 'human_like_manual',
                            'browser': 'chromium_enhanced',
                            'user_agent': await page.evaluate('navigator.userAgent'),
                            'current_url': current_url
                        }
                    }
                    
                    with open(self.cookie_file, 'w') as f:
                        json.dump(cookie_data, f, indent=2)
                    
                    print(f"\\n4️⃣ Cookies saved successfully!")
                    print(f"   File: {self.cookie_file}")
                    print(f"   Cookies count: {len(linkedin_cookies)}")
                    
                    # Test the cookies immediately
                    print("\\n5️⃣ Testing cookie validity...")
                    await page.goto('https://www.linkedin.com/feed/', wait_until='networkidle')
                    await self.human_delay(2000, 3000)
                    
                    if 'feed' in page.url:
                        print("✅ Cookie test successful! You're logged in.")
                    else:
                        print("⚠️ Cookie test inconclusive, but cookies are saved.")
                    
                    return True
                    
                else:
                    print("❌ No LinkedIn session cookie found!")
                    print("This could mean:")
                    print("• Login was not completed successfully")
                    print("• LinkedIn is blocking cookie access")
                    print("• Additional security verification needed")
                    
                    # Show what cookies we did find
                    print(f"\\nFound {len(linkedin_cookies)} LinkedIn cookies:")
                    for cookie in linkedin_cookies:
                        print(f"  • {cookie['name']}")
                    
                    return False
                    
            except Exception as e:
                print(f"❌ Error during cookie extraction: {str(e)}")
                return False
                
            finally:
                print("\\n6️⃣ Keeping browser open for 10 seconds...")
                print("   (You can close it manually or wait)")
                await asyncio.sleep(10)
                await browser.close()

async def main():
    """Main function"""
    manager = HumanLikeLinkedInCookieManager()
    
    print("🚀 Starting Human-Like LinkedIn Cookie Extraction")
    print("This method uses enhanced browser settings to avoid detection")
    print("-" * 60)
    
    success = await manager.extract_cookies_human_like()
    
    if success:
        print("\\n🎉 SUCCESS!")
        print("✅ LinkedIn cookies extracted and saved")
        print("✅ You can now use cookie-based authentication")
        print("✅ Run the enhanced scraper to test automatic login")
    else:
        print("\\n❌ Cookie extraction failed")
        print("💡 Try these solutions:")
        print("• Clear LinkedIn cookies in regular browser")
        print("• Try logging in from a different IP/network")
        print("• Wait a few hours before trying again")
        print("• Use a VPN if LinkedIn is blocking your IP")

if __name__ == "__main__":
    asyncio.run(main())
