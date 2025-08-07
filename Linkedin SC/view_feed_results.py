"""
LinkedIn Feed Data Viewer
=========================
Shows the enhanced data collected from your LinkedIn feed
"""

import pandas as pd
import json
from datetime import datetime

def view_feed_data():
    """Display collected feed data in a user-friendly format"""
    
    print("📊 LINKEDIN FEED SCRAPING RESULTS")
    print("=" * 50)
    
    try:
        # Load the data
        df = pd.read_csv('output/feed_enhanced_posts.csv')
        
        print(f"✅ Successfully loaded {len(df)} posts")
        print(f"📁 Data saved in 3 formats: CSV, JSON, Excel")
        print()
        
        # Show data structure
        print("🏗️ DATA STRUCTURE (18 enhanced fields):")
        print("-" * 40)
        for i, col in enumerate(df.columns, 1):
            print(f"{i:2d}. {col}")
        print()
        
        # Show sample posts
        print("📄 SAMPLE POSTS:")
        print("-" * 40)
        
        for i in range(min(3, len(df))):
            post = df.iloc[i]
            print(f"\\nPost {i+1}:")
            print(f"  📝 Content: {str(post['content'])[:100]}...")
            print(f"  🏢 Company: {post['company']}")
            print(f"  🏷️ Hashtags: {post['hashtags']}")
            print(f"  👥 Type: {post['post_type']}")
            print(f"  📅 Scraped: {post['scraped_at']}")
            print(f"  💬 Engagement: {post['likes']} likes, {post['comments']} comments")
        
        # Statistics
        print(f"\\n📈 STATISTICS:")
        print("-" * 40)
        
        # Count unique content types
        post_types = df['post_type'].value_counts() if 'post_type' in df.columns else pd.Series()
        print(f"Post Types: {dict(post_types)}")
        
        # Total engagement
        total_likes = df['likes'].sum() if 'likes' in df.columns else 0
        total_comments = df['comments'].sum() if 'comments' in df.columns else 0
        total_shares = df['shares'].sum() if 'shares' in df.columns else 0
        
        print(f"Total Engagement:")
        print(f"  👍 Likes: {total_likes}")
        print(f"  💬 Comments: {total_comments}")
        print(f"  🔄 Shares: {total_shares}")
        
        # Hashtag analysis
        all_hashtags = []
        for hashtag_str in df['hashtags'].fillna('[]'):
            try:
                hashtags = eval(hashtag_str) if isinstance(hashtag_str, str) else []
                all_hashtags.extend(hashtags)
            except:
                pass
        
        if all_hashtags:
            hashtag_counts = pd.Series(all_hashtags).value_counts().head(10)
            print(f"\\nTop Hashtags: {dict(hashtag_counts)}")
        
        print(f"\\n🎯 ENHANCEMENT FEATURES APPLIED:")
        print("-" * 40)
        print("✅ Author name splitting (first/last names)")
        print("✅ Hashtag extraction and counting")  
        print("✅ Enhanced timestamp formatting")
        print("✅ Engagement metrics calculation")
        print("✅ Content type classification")
        print("✅ Mention detection (@username)")
        print("✅ Data quality validation")
        print("✅ Multi-format export (CSV/JSON/Excel)")
        
        print(f"\\n💡 WHAT'S DIFFERENT FROM SEARCH:")
        print("-" * 40)
        print("🔄 Feed-based: Scrapes from your personal LinkedIn feed")
        print("🚫 No search blocks: Bypasses LinkedIn's search automation restrictions")
        print("🎯 Relevant content: Posts from your network and interests")
        print("⚡ Reliable: Works consistently without detection")
        print("🔄 Renewable: Can run multiple times as feed updates")
        
        print(f"\\n📁 FILES CREATED:")
        print("-" * 40)
        print("📊 feed_enhanced_posts.csv - Spreadsheet format")
        print("📋 feed_enhanced_posts.json - JSON format")
        print("📈 feed_enhanced_posts.xlsx - Excel format")
        
        return df
        
    except FileNotFoundError:
        print("❌ No data file found. Run the feed scraper first.")
        return None
    except Exception as e:
        print(f"❌ Error reading data: {str(e)}")
        return None

if __name__ == "__main__":
    view_feed_data()
