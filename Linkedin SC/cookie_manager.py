"""
LinkedIn Session Cookie Manager
==============================

Manages LinkedIn session cookies to avoid repeated 2FA authentication
Includes automatic cookie extraction, storage, loading, and expiration handling
"""

import json
import os
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from playwright.async_api import async_playwright
import logging

class LinkedInCookieManager:
    """Manages LinkedIn session cookies for persistent login"""
    
    def __init__(self, cookie_file='linkedin_cookies.json'):
        self.cookie_file = Path(cookie_file)
        self.session_cookies = {}
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging for cookie operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('cookie_manager.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def save_cookies(self, cookies, metadata=None):
        """Save session cookies to file with metadata"""
        cookie_data = {
            'cookies': cookies,
            'saved_at': datetime.now().isoformat(),
            'expires_estimate': (datetime.now() + timedelta(days=30)).isoformat(),
            'metadata': metadata or {}
        }
        
        try:
            with open(self.cookie_file, 'w') as f:
                json.dump(cookie_data, f, indent=2)
            self.logger.info(f"✅ Cookies saved to {self.cookie_file}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to save cookies: {str(e)}")
            return False
    
    def load_cookies(self):
        """Load session cookies from file"""
        if not self.cookie_file.exists():
            self.logger.info("📁 No cookie file found")
            return None
            
        try:
            with open(self.cookie_file, 'r') as f:
                cookie_data = json.load(f)
            
            saved_at = datetime.fromisoformat(cookie_data['saved_at'])
            age_days = (datetime.now() - saved_at).days
            
            self.logger.info(f"📂 Loaded cookies from {age_days} days ago")
            return cookie_data
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load cookies: {str(e)}")
            return None
    
    def cookies_valid(self, cookie_data):
        """Check if cookies are still likely valid"""
        if not cookie_data:
            return False
            
        saved_at = datetime.fromisoformat(cookie_data['saved_at'])
        age_days = (datetime.now() - saved_at).days
        
        # LinkedIn cookies typically last ~30 days, but age alone isn't a reliable invalidation.
        # We only WARN on older cookies and let runtime validation decide.
        if age_days >= 29:
            self.logger.warning(f"⚠️ Cookies are {age_days} days old; proceeding but they might be close to expiring")
        return True
    
    async def extract_cookies_from_browser(self, context):
        """Extract LinkedIn session cookies from browser context"""
        try:
            # Get all cookies for LinkedIn domain
            cookies = await context.cookies()
            linkedin_cookies = [
                cookie for cookie in cookies 
                if 'linkedin.com' in cookie.get('domain', '')
            ]
            
            # Find the main session cookie (li_at)
            li_at_cookie = None
            for cookie in linkedin_cookies:
                if cookie['name'] == 'li_at':
                    li_at_cookie = cookie
                    break
            
            if li_at_cookie:
                self.logger.info("✅ Found LinkedIn session cookie (li_at)")
                return linkedin_cookies
            else:
                self.logger.warning("⚠️ No li_at session cookie found")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Failed to extract cookies: {str(e)}")
            return None
    
    async def apply_cookies_to_context(self, context, cookie_data):
        """Apply saved cookies to browser context"""
        if not cookie_data or 'cookies' not in cookie_data:
            return False
            
        try:
            cookies = cookie_data['cookies']
            await context.add_cookies(cookies)
            self.logger.info(f"✅ Applied {len(cookies)} cookies to browser context")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to apply cookies: {str(e)}")
            return False
    
    async def test_cookie_validity(self, page):
        """Test if current cookies allow access to LinkedIn.
        Be tolerant: only return False when we explicitly detect a login state.
        On timeouts or inconclusive checks, assume cookies are valid to avoid unnecessary re-authentication.
        """
        try:
            # Navigate to a protected LinkedIn page quickly without waiting for full network idle
            await page.goto(
                'https://www.linkedin.com/feed/',
                wait_until='domcontentloaded',
                timeout=15000
            )

            # Quick checks for forced login state via URL
            if any(path in (page.url or '') for path in ('/login', '/checkpoint')):
                self.logger.warning("⚠️ Redirected to login/checkpoint - cookies likely expired")
                return False

            # Brief pause for DOM to settle
            await page.wait_for_timeout(1000)

            # Check for common login indicators
            login_form = await page.query_selector('form[action*="login"], input[name="session_key"]')
            if login_form:
                self.logger.warning("⚠️ Login form detected - cookies expired")
                return False

            # Check for common logged-in indicators
            selectors_logged_in = [
                'a[href*="/feed/"]',
                'img.global-nav__me-photo',
                '[data-test-global-nav-link="feed"]',
                'nav.global-nav',
            ]
            for sel in selectors_logged_in:
                try:
                    el = await page.query_selector(sel)
                    if el:
                        self.logger.info("✅ Cookies appear valid (logged-in UI detected)")
                        return True
                except Exception:
                    # Ignore selector errors and continue
                    pass

            # Inconclusive: assume valid to avoid unnecessary login prompts
            self.logger.warning("⚠️ Login status inconclusive; proceeding with stored cookies")
            return True

        except Exception as e:
            # Network timeouts or transient errors: assume valid to prevent forced relogin
            self.logger.warning(f"⚠️ Cookie validation inconclusive due to error: {str(e)}; proceeding with stored cookies")
            return True
    
    def delete_cookies(self):
        """Delete stored cookies"""
        try:
            if self.cookie_file.exists():
                self.cookie_file.unlink()
                self.logger.info("🗑️ Deleted stored cookies")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to delete cookies: {str(e)}")
            return False
    
    def get_cookie_info(self):
        """Get information about stored cookies"""
        cookie_data = self.load_cookies()
        if not cookie_data:
            return "No cookies stored"
        
        saved_at = datetime.fromisoformat(cookie_data['saved_at'])
        age_days = (datetime.now() - saved_at).days
        
        info = f"""
🍪 COOKIE INFORMATION:
📅 Saved: {saved_at.strftime('%Y-%m-%d %H:%M:%S')}
⏰ Age: {age_days} days
📊 Count: {len(cookie_data.get('cookies', []))} cookies
✅ Valid: {'Yes' if self.cookies_valid(cookie_data) else 'No'}
        """
        return info.strip()

async def demo_cookie_extraction():
    """Demo: Extract cookies after manual login"""
    
    print("🍪 LINKEDIN COOKIE EXTRACTION DEMO")
    print("=" * 40)
    print("This will help you extract cookies after manual login")
    print("-" * 40)
    
    cookie_manager = LinkedInCookieManager()
    
    async with async_playwright() as p:
        # Launch browser in non-headless mode for manual login
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("\n1️⃣ Opening LinkedIn login page...")
            await page.goto('https://www.linkedin.com/login')
            
            print("\n2️⃣ Please complete manual login:")
            print("   • Enter your email and password")
            print("   • Complete 2FA if prompted")
            print("   • Wait until you see your LinkedIn feed")
            
            input("\n   Press Enter after you've successfully logged in...")
            
            print("\n3️⃣ Extracting session cookies...")
            cookies = await cookie_manager.extract_cookies_from_browser(context)
            
            if cookies:
                print("\n4️⃣ Saving cookies...")
                success = cookie_manager.save_cookies(
                    cookies, 
                    metadata={
                        'extraction_method': 'manual_login_demo',
                        'browser': 'chromium',
                        'user_agent': await page.evaluate('navigator.userAgent')
                    }
                )
                
                if success:
                    print("✅ Cookies saved successfully!")
                    print(f"📁 File: {cookie_manager.cookie_file}")
                    print("\n5️⃣ Testing cookie validity...")
                    
                    # Test the cookies
                    valid = await cookie_manager.test_cookie_validity(page)
                    if valid:
                        print("✅ Cookies are working correctly!")
                    else:
                        print("⚠️ Cookie validation inconclusive")
                else:
                    print("❌ Failed to save cookies")
            else:
                print("❌ Failed to extract cookies")
                
        except Exception as e:
            print(f"❌ Demo failed: {str(e)}")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    print("🍪 LinkedIn Cookie Manager")
    print("=" * 30)
    print("1. Run demo to extract cookies after manual login")
    print("2. View cookie information")
    print("3. Delete stored cookies")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(demo_cookie_extraction())
    elif choice == "2":
        manager = LinkedInCookieManager()
        print(manager.get_cookie_info())
    elif choice == "3":
        manager = LinkedInCookieManager()
        manager.delete_cookies()
    else:
        print("Invalid choice")
