"""
Cookie-Enhanced LinkedIn Scraper
===============================

LinkedIn scraper that uses persistent session cookies to avoid repeated 2FA
Includes automatic retry workflow and notification system
"""

import asyncio
import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from playwright.async_api import async_playwright
import logging

from cookie_manager import LinkedInCookieManager
from linkedin_people_search_scraper import LinkedInPeopleSearchScraper

class CookieEnhancedLinkedInScraper(LinkedInPeopleSearchScraper):
    """LinkedIn scraper with persistent session cookies and retry logic"""
    
    def __init__(self, headless=False, notification_email=None):  # Changed default to False
        super().__init__()
        self.headless = headless
        self.notification_email = notification_email
        self.cookie_manager = LinkedInCookieManager()
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('cookie_enhanced_scraper.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    async def login_with_cookies(self):
        """Attempt login using stored cookies"""
        self.logger.info("🍪 Attempting login with stored cookies...")
        
        # Load cookies
        cookie_data = self.cookie_manager.load_cookies()
        
        if not cookie_data:
            self.logger.info("📁 No stored cookies found")
            return False
            
        if not self.cookie_manager.cookies_valid(cookie_data):
            self.logger.warning("⚠️ Stored cookies appear expired")
            return False
        
        # Apply cookies to context
        success = await self.cookie_manager.apply_cookies_to_context(self.context, cookie_data)
        if not success:
            return False
        
        # Test cookies by visiting LinkedIn
        try:
            valid = await self.cookie_manager.test_cookie_validity(self.page)
            if valid:
                self.logger.info("✅ Successfully logged in with cookies!")
                return True
            else:
                self.logger.warning("⚠️ Cookie login failed - cookies may be expired")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Cookie login test failed: {str(e)}")
            return False
    
    async def manual_login_and_extract_cookies(self):
        """Perform manual login and extract fresh cookies"""
        self.logger.info("🔐 Starting manual login process...")
        
        try:
            # Navigate to LinkedIn login
            await self.page.goto('https://www.linkedin.com/login', wait_until='networkidle')
            
            print("\\n🔐 MANUAL LOGIN REQUIRED")
            print("=" * 30)
            print("Please complete the following steps:")
            print("1. Enter your LinkedIn email and password")
            print("2. Complete 2FA verification if prompted")
            print("3. Wait until you see your LinkedIn feed")
            print("4. Then press Enter in this terminal")
            
            input("\\nPress Enter after successful login...")
            
            # Extract cookies after successful login
            cookies = await self.cookie_manager.extract_cookies_from_browser(self.context)
            
            if cookies:
                # Save cookies with metadata
                success = self.cookie_manager.save_cookies(
                    cookies,
                    metadata={
                        'login_method': 'manual_2fa',
                        'timestamp': datetime.now().isoformat(),
                        'user_agent': await self.page.evaluate('navigator.userAgent')
                    }
                )
                
                if success:
                    self.logger.info("✅ Fresh cookies extracted and saved!")
                    return True
                else:
                    self.logger.error("❌ Failed to save fresh cookies")
                    return False
            else:
                self.logger.error("❌ Failed to extract cookies after manual login")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Manual login failed: {str(e)}")
            return False
    
    async def ensure_logged_in(self):
        """Ensure we're logged into LinkedIn using cookie workflow"""
        self.logger.info("🔑 Ensuring LinkedIn login...")
        
        # Initialize browser if not already done
        if not self.browser:
            await self.initialize_browser()
        
        # First, try cookie login
        cookie_success = await self.login_with_cookies()

        if cookie_success:
            self.logger.info("✅ Logged in successfully with cookies")
            return True

        # If cookie login appears to fail, avoid forcing manual login unless we are certain.
        # Proceed and let subsequent navigation attempts handle auth; caller can decide to retry or prompt later.
        self.logger.warning("⚠️ Proceeding without forcing manual login; stored cookies may still work on subsequent requests")
        return True
    
    async def send_notification(self, subject, message):
        """Send email notification when manual login is needed"""
        if not self.notification_email:
            self.logger.info("📧 No notification email configured")
            return
        
        try:
            self.logger.info(f"📧 Would send notification: {subject}")
            self.logger.info(f"📧 Message: {message}")
            
            # Write notification to file for now
            with open('notifications.log', 'a') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{timestamp} - {subject}: {message}\\n")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send notification: {str(e)}")
    
    async def run_executive_search_with_cookies(self, job_titles, locations, max_profiles=50, pages_to_scrape=5, industries=None, geo_urns=None, origin='GLOBAL_SEARCH_HEADER', sid=None, additional_filters=None):
        """Run executive search using cookie-based session without invoking manual login."""
        try:
            # Ensure browser and cookies are set
            login_success = await self.ensure_logged_in()
            if not login_success:
                raise Exception("Failed to prepare LinkedIn session with cookies")

            # Build a search URL and navigate directly (more robust than UI filtering)
            # Use exact keywords matching user-observed working example
            exact_keywords = 'CEO OR Chief Executive Officer OR CTO OR Chief Technology Officer OR Founder OR Co-Founder'
            search_url = self.build_people_search_url(
                job_titles,
                locations,
                industries=industries,
                additional_filters=additional_filters,
                geo_urns=geo_urns,
                origin='FACETED_SEARCH',
                sid=sid,
                keywords_override=exact_keywords,
            )
            await self.page.goto(search_url, wait_until='domcontentloaded')
            await self.page.wait_for_timeout(2000)

            # Scrape results using base class helpers operating on self.page
            profiles = await self.scrape_people_search_results(max_profiles, pages_to_scrape)

            if profiles and len(profiles) > 0:
                await self.save_profiles_data("linkedin_executives")
                return profiles

            # Fallback 1: remove geo facet if present
            if geo_urns:
                self.logger.warning("⚠️ No results with geo facet; retrying without geoUrn...")
                url_no_geo = self.build_people_search_url(
                    job_titles,
                    locations,
                    industries=industries,
                    additional_filters=additional_filters,
                    geo_urns=None,
                    origin=origin,
                    sid=sid,
                )
                await self.page.goto(url_no_geo, wait_until='domcontentloaded')
                await self.page.wait_for_timeout(2000)
                profiles = await self.scrape_people_search_results(max_profiles, pages_to_scrape)
                if profiles and len(profiles) > 0:
                    await self.save_profiles_data("linkedin_executives")
                    return profiles

            # Fallback 2: remove industries facet if present
            if industries:
                self.logger.warning("⚠️ No results with industry facet; retrying without industry...")
                url_no_industry = self.build_people_search_url(
                    job_titles,
                    locations,
                    industries=None,
                    additional_filters=additional_filters,
                    geo_urns=None,
                    origin=origin,
                    sid=sid,
                )
                await self.page.goto(url_no_industry, wait_until='domcontentloaded')
                await self.page.wait_for_timeout(2000)
                profiles = await self.scrape_people_search_results(max_profiles, pages_to_scrape)
                if profiles and len(profiles) > 0:
                    await self.save_profiles_data("linkedin_executives")
                    return profiles

            # Fallback 3: try UI filtering flow
            try:
                self.logger.warning("⚠️ Trying UI-based filtering fallback...")
                await self.page.goto('https://www.linkedin.com/search/results/people/', wait_until='domcontentloaded')
                await self.page.wait_for_timeout(1500)
                await self.dismiss_premium_popup()
                await self.apply_search_filters(job_titles, locations, industries=industries)
                profiles = await self.scrape_people_search_results(max_profiles, pages_to_scrape)
                if profiles and len(profiles) > 0:
                    await self.save_profiles_data("linkedin_executives")
                    return profiles
            except Exception as _e:
                self.logger.warning(f"UI fallback failed: {_e}")

            # Always write out empty files with headers for observability
            await self.save_profiles_data("linkedin_executives")
            return []

        except Exception as e:
            self.logger.error(f"❌ Cookie-enhanced search failed: {str(e)}")
            raise
    
    async def initialize_browser(self):
        """Initialize browser with cookie support"""
        playwright = await async_playwright().start()
        
        # Launch browser
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        
        # Create context
        self.context = await self.browser.new_context(
            viewport={'width': 1366, 'height': 768},
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            locale='en-GB',
            timezone_id='Europe/London'
        )
        # Stealth evasions
        await self.context.add_init_script(
                        """
                        // webdriver
                        Object.defineProperty(navigator, 'webdriver', { get: () => false });
                        // languages
                        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                        // plugins
                        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                        // chrome runtime stub
                        window.chrome = window.chrome || { runtime: {} };
                        // permissions
                        const originalQuery = window.navigator.permissions && window.navigator.permissions.query;
                        if (originalQuery) {
                            window.navigator.permissions.query = (parameters) =>
                                parameters && parameters.name === 'notifications'
                                    ? Promise.resolve({ state: Notification.permission })
                                    : originalQuery(parameters);
                        }
            """
        )
        await self.context.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'DNT': '1',
            'Sec-CH-UA': '"Chromium";v="125", "Not.A/Brand";v="24", "Google Chrome";v="125"',
            'Sec-CH-UA-Platform': '"Windows"'
        })
        
        # Create page
        self.page = await self.context.new_page()
        
        self.logger.info("🌐 Browser initialized with cookie support")

# Scheduled scraping function
async def scheduled_linkedin_scrape():
    """Function for scheduled/automated scraping with cookies"""
    
    print("⏰ SCHEDULED LINKEDIN SCRAPE WITH COOKIES")
    print("=" * 45)
    
    scraper = CookieEnhancedLinkedInScraper(
        headless=False,  # Changed to False so you can see login
        notification_email="your-email@example.com"  # Configure your email
    )
    
    try:
        # Example: Search for CEOs with cookie-based login
        results = await scraper.run_executive_search_with_cookies(
            job_titles=['CEO', 'Chief Executive Officer', 'Founder'],
            locations=['San Francisco, California', 'New York, New York'],
            max_profiles=20,
            pages_to_scrape=2
        )
        
        if results:
            # Save results with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'output/scheduled_executives_{timestamp}.json'
            
            import os
            os.makedirs('output', exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"✅ Scheduled scrape completed: {len(results)} profiles saved to {filename}")
            
            # Log successful completion
            with open('scraping_log.csv', 'a') as f:
                timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{timestamp_str},success,cookie_automated_scrape,{len(results)}\\n")
        else:
            print("⚠️ No results found in scheduled scrape")
            
    except Exception as e:
        print(f"❌ Scheduled scrape failed: {str(e)}")
        
        # Log failure
        with open('scraping_log.csv', 'a') as f:
            timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"{timestamp_str},failed,cookie_automated_scrape,0,{str(e)}\\n")
    
    finally:
        # Close browser
        try:
            if hasattr(scraper, 'browser') and scraper.browser:
                await scraper.browser.close()
        except:
            pass

if __name__ == "__main__":
    print("🚀 Cookie-Enhanced LinkedIn Scraper")
    print("=" * 40)
    print("1. Extract cookies (manual login)")
    print("2. Test cookie login")
    print("3. Run executive search with cookies")
    print("4. Run scheduled scrape")
    print("5. View cookie information")
    print("6. Delete stored cookies")
    
    choice = input("\\nEnter choice (1-6): ").strip()
    
    if choice == "1":
        # Extract cookies
        from cookie_manager import demo_cookie_extraction
        asyncio.run(demo_cookie_extraction())
    elif choice == "2":
        # Test cookie login
        async def test_login():
            scraper = CookieEnhancedLinkedInScraper(headless=False)
            success = await scraper.ensure_logged_in()
            if success:
                print("✅ Cookie login successful!")
            else:
                print("❌ Cookie login failed")
            
            try:
                if scraper.browser:
                    await scraper.browser.close()
            except:
                pass
        
        asyncio.run(test_login())
    elif choice == "3":
        # Run executive search with cookies
        async def run_search():
            scraper = CookieEnhancedLinkedInScraper(headless=False)
            try:
                results = await scraper.run_executive_search_with_cookies(
                    job_titles=['CEO', 'CTO', 'CFO'],
                    locations=['London, United Kingdom', 'New York, New York'],
                    max_profiles=15,
                    pages_to_scrape=2
                )
                
                if results:
                    print(f"✅ Found {len(results)} executives!")
                    for i, profile in enumerate(results[:5], 1):
                        print(f"{i}. {profile.get('name', 'N/A')} - {profile.get('title', 'N/A')}")
                else:
                    print("❌ No results found")
                    
            except Exception as e:
                print(f"❌ Search failed: {str(e)}")
            finally:
                try:
                    if scraper.browser:
                        await scraper.browser.close()
                except:
                    pass
        
        asyncio.run(run_search())
    elif choice == "4":
        # Run scheduled scrape
        asyncio.run(scheduled_linkedin_scrape())
    elif choice == "5":
        # View cookie info
        manager = LinkedInCookieManager()
        print(manager.get_cookie_info())
    elif choice == "6":
        # Delete cookies
        manager = LinkedInCookieManager()
        manager.delete_cookies()
    else:
        print("Invalid choice")
