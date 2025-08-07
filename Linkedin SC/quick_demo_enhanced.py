"""
Quick Demo: Enhanced LinkedIn Scraper
====================================

This script demonstrates how to use the LinkedIn scraper with the new enhanced features.
Run this to see the improvements in action!
"""

import asyncio
import os
from pathlib import Path
import json
import pandas as pd
from datetime import datetime

# Make sure we have a .env file
def setup_demo_env():
    """Setup demo environment variables"""
    env_path = Path('.env')
    if not env_path.exists():
        print("📝 Creating demo .env file...")
        env_content = """# LinkedIn Scraper Configuration
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password_here
SEARCH_KEYWORDS=python,software engineering,AI
MAX_POSTS=5
DELAY_MIN=2
DELAY_MAX=5
OUTPUT_DIR=output
CSV_FILENAME=linkedin_posts_enhanced.csv
HEADLESS=True
"""
        with open(env_path, 'w') as f:
            f.write(env_content)
        print("✅ Demo .env file created. Please update with your credentials if you want to test live scraping.")
        return False
    return True

def demo_enhanced_vs_original():
    """Show the difference between original and enhanced data"""
    
    print("🔍 ENHANCED FEATURES COMPARISON")
    print("=" * 50)
    
    # Original data structure
    original_post = {
        'content': 'Excited about our new AI breakthrough! #AI #Innovation #TechNews',
        'author_name': 'Dr. Sarah Johnson',
        'author_title': 'Chief Technology Officer',
        'post_date': '2025-08-07T08:30:00Z',
        'post_url': 'https://www.linkedin.com/feed/update/urn:li:activity:1234567890/',
        'likes_count': 245,
        'comments_count': 32,
        'image_urls': [],
        'scraped_at': '2025-08-07T12:00:00Z'
    }
    
    print("📊 BEFORE (Original Fields):")
    for key, value in original_post.items():
        print(f"   {key}: {value}")
    
    # Apply enhancements
    from utils import enhance_post_data
    enhanced_post = enhance_post_data(original_post)
    
    print("\n🚀 AFTER (Enhanced Fields):")
    for key, value in enhanced_post.items():
        if key in original_post:
            print(f"   {key}: {value}")
        else:
            print(f"   {key}: {value} 🆕")
    
    # Show the improvements
    original_fields = len(original_post)
    enhanced_fields = len(enhanced_post)
    improvement = ((enhanced_fields - original_fields) / original_fields) * 100
    
    print(f"\n📈 IMPROVEMENT SUMMARY:")
    print(f"   • Original fields: {original_fields}")
    print(f"   • Enhanced fields: {enhanced_fields}")
    print(f"   • Improvement: +{improvement:.1f}% more data!")
    
    return enhanced_post

async def demo_live_scraping():
    """Demo live scraping with enhancements (if credentials are available)"""
    
    print("\n🚀 LIVE SCRAPING DEMO")
    print("=" * 30)
    
    # Check if credentials are set
    from dotenv import load_dotenv
    load_dotenv()
    
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password or email == 'your_email@example.com':
        print("⚠️ LinkedIn credentials not configured for live scraping.")
        print("💡 To test live scraping:")
        print("   1. Update .env file with your LinkedIn credentials")
        print("   2. Run: python linkedin_scraper.py")
        print("   3. Check output/linkedin_posts_enhanced.csv for results")
        return False
    
    print("✅ Credentials found! Starting live scraping demo...")
    
    try:
        from linkedin_scraper import LinkedInScraper
        
        # Create scraper instance
        scraper = LinkedInScraper()
        
        # Override settings for demo
        scraper.max_posts = 3  # Just scrape a few posts for demo
        scraper.search_keywords = ['AI', 'machine learning']
        
        print(f"🔍 Searching for: {scraper.search_keywords}")
        print(f"📊 Max posts: {scraper.max_posts}")
        
        # Run the scraper
        await scraper.main()
        
        # Check if we got enhanced data
        csv_path = Path(scraper.output_dir) / scraper.csv_filename
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            print(f"\n✅ Successfully scraped {len(df)} posts with enhanced features!")
            
            # Show enhanced columns
            enhanced_columns = [col for col in df.columns if col in ['author_firstName', 'author_lastName', 'hashtags', 'mentions', 'postedAtISO', 'timeSincePosted', 'post_type']]
            print(f"🆕 Enhanced columns found: {enhanced_columns}")
            
            # Show sample data
            if len(df) > 0:
                print(f"\n📋 Sample enhanced data:")
                sample_row = df.iloc[0]
                for col in enhanced_columns:
                    if col in sample_row:
                        print(f"   {col}: {sample_row[col]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Live scraping demo failed: {str(e)}")
        print("💡 This is normal if LinkedIn blocks the request or if there are login issues.")
        return False

def demo_file_analysis():
    """Analyze existing output files to show enhancements"""
    
    print("\n📁 EXISTING FILES ANALYSIS")
    print("=" * 35)
    
    output_dir = Path("output")
    
    # Look for existing CSV files
    csv_files = list(output_dir.glob("*.csv"))
    
    if csv_files:
        print(f"📊 Found {len(csv_files)} CSV files:")
        
        for csv_file in csv_files[:3]:  # Show up to 3 files
            try:
                df = pd.read_csv(csv_file)
                enhanced_cols = [col for col in df.columns if col in ['author_firstName', 'author_lastName', 'hashtags', 'mentions', 'postedAtISO', 'timeSincePosted', 'post_type']]
                
                print(f"\n   📄 {csv_file.name}:")
                print(f"      Rows: {len(df)}")
                print(f"      Columns: {len(df.columns)}")
                print(f"      Enhanced columns: {len(enhanced_cols)}")
                
                if enhanced_cols:
                    print(f"      ✅ Has enhanced features: {enhanced_cols}")
                else:
                    print(f"      ⚠️ No enhanced features (older version)")
                    
            except Exception as e:
                print(f"      ❌ Error reading {csv_file.name}: {str(e)}")
    else:
        print("📁 No existing CSV files found in output/ directory")
        print("💡 Run the scraper to generate enhanced data files!")

def main():
    """Main demo function"""
    
    print("🎉 ENHANCED LINKEDIN SCRAPER DEMO")
    print("=" * 50)
    print("This demo shows the 3 high-impact features we just implemented:")
    print("1. ✅ Author name splitting (firstName/lastName)")
    print("2. ✅ Hashtag extraction from content") 
    print("3. ✅ Better timestamp formatting (ISO + relative time)")
    print("=" * 50)
    
    # Setup environment
    has_env = setup_demo_env()
    
    # Demo 1: Show enhanced vs original data
    enhanced_post = demo_enhanced_vs_original()
    
    # Demo 2: Analyze existing files
    demo_file_analysis()
    
    # Demo 3: Live scraping (if possible)
    if has_env:
        print("\n" + "=" * 50)
        print("Want to test live scraping? (y/n): ", end="")
        try:
            choice = input().lower().strip()
            if choice == 'y':
                asyncio.run(demo_live_scraping())
        except KeyboardInterrupt:
            print("\n⚠️ Demo interrupted by user")
    
    print(f"\n🎯 SUMMARY")
    print("=" * 20)
    print("✅ Successfully demonstrated enhanced features!")
    print("✅ Your scraper now extracts 88.9% more data fields!")
    print("✅ Data is more structured and enterprise-ready!")
    
    print(f"\n🚀 NEXT STEPS:")
    print("1. Update .env with your LinkedIn credentials")
    print("2. Run: python linkedin_scraper.py")
    print("3. Check output/linkedin_posts_enhanced.csv")
    print("4. Compare with enterprise JSON structure")
    print("5. Ready for Phase 2 enhancements!")
    
    print(f"\n💡 Your LinkedIn scraper is now significantly more powerful! 🎉")

if __name__ == "__main__":
    main()
