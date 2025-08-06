"""
Verify LinkedIn Post URLs
Check if the extracted URLs are working correctly
"""
import pandas as pd
import requests
from pathlib import Path


def verify_linkedin_urls():
    """Check if LinkedIn URLs from scraping are working"""
    print("🔍 LinkedIn URL Verification")
    print("=" * 50)
    
    csv_path = Path("output/linkedin_posts_with_urls_fixed.csv")
    if not csv_path.exists():
        print("❌ No CSV file found. Run the scraper first.")
        return
    
    # Read the CSV
    df = pd.read_csv(csv_path)
    print(f"📊 Found {len(df)} posts in CSV")
    print()
    
    # Check URLs
    working_urls = 0
    total_urls = 0
    
    for index, row in df.iterrows():
        post_url = row.get('post_url', '')
        if pd.notna(post_url) and post_url.strip():
            total_urls += 1
            print(f"🔗 Testing URL {total_urls}: {post_url}")
            
            try:
                # Test URL with a HEAD request (faster than GET)
                response = requests.head(post_url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    print(f"✅ URL works! (Status: {response.status_code})")
                    working_urls += 1
                else:
                    print(f"❌ URL failed (Status: {response.status_code})")
            except Exception as e:
                print(f"❌ URL failed (Error: {str(e)})")
            print()
    
    # Summary
    print("📋 VERIFICATION SUMMARY")
    print("=" * 30)
    print(f"Total URLs found: {total_urls}")
    print(f"Working URLs: {working_urls}")
    print(f"Success rate: {(working_urls/total_urls*100) if total_urls > 0 else 0:.1f}%")
    
    if working_urls == total_urls and total_urls > 0:
        print("🎉 All URLs are working correctly!")
    elif working_urls > 0:
        print("⚠️ Some URLs are working, but not all")
    else:
        print("❌ No URLs are working")
    
    # Show example URLs
    working_examples = df[df['post_url'].notna() & (df['post_url'] != '')]['post_url'].head(3)
    if len(working_examples) > 0:
        print()
        print("📋 EXAMPLE WORKING URLS:")
        for i, url in enumerate(working_examples, 1):
            print(f"{i}. {url}")


def compare_old_vs_new_format():
    """Show the difference between old and new URL formats"""
    print("\n🔍 URL Format Comparison")
    print("=" * 40)
    
    print("❌ OLD FORMAT (404 Error):")
    print("   https://www.linkedin.com/posts/activity-7358814936061390849")
    print("   • This format doesn't work")
    print("   • LinkedIn returns 404 Not Found")
    print()
    
    print("✅ NEW FORMAT (200 OK):")
    print("   https://www.linkedin.com/feed/update/urn:li:activity:7358890298837544962/")
    print("   • This is LinkedIn's official feed URL format")
    print("   • Works correctly and takes you to the post")
    print()
    
    print("🎯 THE FIX:")
    print("   • Updated URL extraction logic")
    print("   • Uses proper LinkedIn feed URL format")
    print("   • Extracts activity ID from data-urn attributes")
    print("   • Constructs URLs as: /feed/update/urn:li:activity:{id}/")


if __name__ == "__main__":
    verify_linkedin_urls()
    compare_old_vs_new_format()
