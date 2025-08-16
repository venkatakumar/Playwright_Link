"""
LinkedIn Scraper Scheduler with Cookie Management
===============================================

Automated scheduler for daily LinkedIn scraping with cookie persistence
Includes logging to CSV and Google Sheets integration
"""

import asyncio
import schedule
import time
import json
import csv
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging

from cookie_enhanced_scraper import CookieEnhancedLinkedInScraper, scheduled_linkedin_scrape
from people_search_config import SEARCH_CONFIGS

class LinkedInScrapingScheduler:
    """Scheduler for automated LinkedIn scraping with cookie management"""
    
    def __init__(self, config_file='scheduler_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        self.logger = self._setup_logging()
        self.scraping_log = 'daily_scraping_log.csv'
        self.results_dir = Path('scheduled_results')
        self.results_dir.mkdir(exist_ok=True)
        
    def _setup_logging(self):
        """Setup logging for scheduler"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scheduler.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def load_config(self):
        """Load scheduler configuration"""
        default_config = {
            'notification_email': None,
            'daily_searches': [
                {
                    'name': 'global_cfos',
                    'description': 'Daily CFO search',
                    'max_profiles': 30,
                    'pages': 2
                },
                {
                    'name': 'global_cios', 
                    'description': 'Daily CIO search',
                    'max_profiles': 25,
                    'pages': 2
                },
                {
                    'name': 'uk_tech_ceos',
                    'description': 'UK Tech CEO search',
                    'max_profiles': 20,
                    'pages': 2
                }
            ],
            'schedule_time': '09:00',  # 9 AM daily
            'headless': False,  # Changed to False so you can see login
            'google_sheets': {
                'enabled': False,
                'sheet_id': None,
                'credentials_file': 'google_credentials.json'
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")
                return default_config
        else:
            # Save default config
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def initialize_csv_log(self):
        """Initialize CSV log file with headers"""
        if not os.path.exists(self.scraping_log):
            with open(self.scraping_log, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'search_name', 'status', 'profiles_found',
                    'execution_time_seconds', 'error_message', 'output_file'
                ])
    
    async def run_daily_search(self, search_config):
        """Run a single scheduled search"""
        search_name = search_config['name']
        start_time = time.time()
        
        self.logger.info(f"🔍 Starting scheduled search: {search_name}")
        
        try:
            # Get predefined configuration
            linkedin_config = SEARCH_CONFIGS.get(search_name)
            if not linkedin_config:
                raise Exception(f"Configuration '{search_name}' not found")
            
            # Initialize scraper with cookies
            scraper = CookieEnhancedLinkedInScraper(
                headless=self.config['headless'],
                notification_email=self.config['notification_email']
            )
            
            # Run the search
            results = await scraper.run_executive_search_with_cookies(
                job_titles=linkedin_config['job_titles'],
                locations=linkedin_config['locations'],
                max_profiles=search_config['max_profiles'],
                pages_to_scrape=search_config['pages']
            )
            
            execution_time = time.time() - start_time
            
            if results and len(results) > 0:
                # Save results
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.results_dir / f"{search_name}_{timestamp}.json"
                
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=2)
                
                # Log success
                self.log_search_result(
                    search_name, 'success', len(results),
                    execution_time, None, str(output_file)
                )
                
                # Update Google Sheets if enabled
                if self.config['google_sheets']['enabled']:
                    await self.update_google_sheets(search_name, results)
                
                self.logger.info(f"✅ {search_name}: {len(results)} profiles found")
                return results
            else:
                # Log no results
                self.log_search_result(
                    search_name, 'no_results', 0,
                    execution_time, 'No profiles found', None
                )
                self.logger.warning(f"⚠️ {search_name}: No profiles found")
                return []
                
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            # Log failure
            self.log_search_result(
                search_name, 'failed', 0,
                execution_time, error_msg, None
            )
            
            self.logger.error(f"❌ {search_name} failed: {error_msg}")
            return []
            
        finally:
            # Cleanup
            try:
                if hasattr(scraper, 'browser') and scraper.browser:
                    await scraper.browser.close()
            except:
                pass
    
    def log_search_result(self, search_name, status, profiles_found, 
                         execution_time, error_message, output_file):
        """Log search result to CSV"""
        try:
            with open(self.scraping_log, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    search_name,
                    status,
                    profiles_found,
                    round(execution_time, 2),
                    error_message or '',
                    output_file or ''
                ])
        except Exception as e:
            self.logger.error(f"Failed to log result: {e}")
    
    async def update_google_sheets(self, search_name, results):
        """Update Google Sheets with results (placeholder)"""
        # This would require google-auth and gspread libraries
        # Placeholder implementation
        self.logger.info(f"📊 Would update Google Sheets for {search_name} with {len(results)} results")
        
        # Example of what this would do:
        # 1. Authenticate with Google Sheets API
        # 2. Open the specified spreadsheet
        # 3. Add new rows with the search results
        # 4. Update summary statistics
    
    async def run_all_daily_searches(self):
        """Run all configured daily searches"""
        self.logger.info("🚀 Starting daily LinkedIn scraping routine")
        
        total_profiles = 0
        successful_searches = 0
        
        for search_config in self.config['daily_searches']:
            try:
                results = await self.run_daily_search(search_config)
                total_profiles += len(results)
                if results:
                    successful_searches += 1
                
                # Add delay between searches to be respectful
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Search {search_config['name']} failed: {e}")
        
        # Summary
        self.logger.info("📊 DAILY SCRAPING SUMMARY")
        self.logger.info(f"✅ Successful searches: {successful_searches}/{len(self.config['daily_searches'])}")
        self.logger.info(f"👥 Total profiles found: {total_profiles}")
        
        # Generate daily summary file
        summary = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'successful_searches': successful_searches,
            'total_searches': len(self.config['daily_searches']),
            'total_profiles': total_profiles,
            'searches': self.config['daily_searches']
        }
        
        summary_file = self.results_dir / f"daily_summary_{datetime.now().strftime('%Y%m%d')}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def schedule_daily_runs(self):
        """Set up daily scheduled runs"""
        self.initialize_csv_log()
        
        schedule_time = self.config['schedule_time']
        self.logger.info(f"⏰ Scheduling daily LinkedIn scraping at {schedule_time}")
        
        # Schedule the daily run
        schedule.every().day.at(schedule_time).do(
            lambda: asyncio.run(self.run_all_daily_searches())
        )
        
        self.logger.info("🔄 Scheduler started. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("🛑 Scheduler stopped by user")
    
    def run_once_now(self):
        """Run all searches once immediately (for testing)"""
        self.logger.info("🧪 Running daily searches once for testing")
        asyncio.run(self.run_all_daily_searches())

def create_scheduler_config():
    """Create or update scheduler configuration"""
    print("🔧 LINKEDIN SCRAPER SCHEDULER CONFIGURATION")
    print("=" * 50)
    
    config = {
        'notification_email': input("Notification email (optional): ").strip() or None,
        'schedule_time': input("Daily run time (HH:MM, default 09:00): ").strip() or "09:00",
        'headless': input("Run headless? (y/n, default n): ").strip().lower() == 'y',  # Changed default to 'n'
        'daily_searches': []
    }
    
    print("\\n📋 Configure daily searches:")
    print("Available configurations:", list(SEARCH_CONFIGS.keys()))
    
    while True:
        search_name = input("\\nSearch configuration name (or 'done'): ").strip()
        if search_name.lower() == 'done':
            break
        
        if search_name in SEARCH_CONFIGS:
            max_profiles = input(f"Max profiles for {search_name} (default 25): ").strip()
            max_profiles = int(max_profiles) if max_profiles.isdigit() else 25
            
            pages = input(f"Pages to scrape for {search_name} (default 2): ").strip()
            pages = int(pages) if pages.isdigit() else 2
            
            config['daily_searches'].append({
                'name': search_name,
                'description': SEARCH_CONFIGS[search_name]['description'],
                'max_profiles': max_profiles,
                'pages': pages
            })
            
            print(f"✅ Added {search_name}")
        else:
            print(f"❌ Configuration '{search_name}' not found")
    
    # Save configuration
    with open('scheduler_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\\n✅ Configuration saved to scheduler_config.json")
    print(f"📅 Scheduled daily runs at {config['schedule_time']}")
    print(f"🔍 Will run {len(config['daily_searches'])} searches daily")

if __name__ == "__main__":
    print("⏰ LinkedIn Scraping Scheduler")
    print("=" * 35)
    print("1. Configure scheduler")
    print("2. Start scheduled runs")
    print("3. Run once now (testing)")
    print("4. View recent logs")
    
    choice = input("\\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        create_scheduler_config()
    elif choice == "2":
        scheduler = LinkedInScrapingScheduler()
        scheduler.schedule_daily_runs()
    elif choice == "3":
        scheduler = LinkedInScrapingScheduler()
        scheduler.run_once_now()
    elif choice == "4":
        # View recent logs
        log_file = 'daily_scraping_log.csv'
        if os.path.exists(log_file):
            print(f"\\n📊 Recent scraping results from {log_file}:")
            with open(log_file, 'r') as f:
                lines = f.readlines()
                for line in lines[-10:]:  # Show last 10 entries
                    print(line.strip())
        else:
            print("❌ No log file found")
    else:
        print("Invalid choice")
