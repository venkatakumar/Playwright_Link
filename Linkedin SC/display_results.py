"""
Display LinkedIn scraping results with post URLs
"""
import pandas as pd
import os

def display_results():
    """Display the scraped LinkedIn data with URLs"""
    csv_path = 'output/linkedin_posts_with_urls_fixed.csv'
    
    if not os.path.exists(csv_path):
        print("❌ CSV file not found")
        return
    
    df = pd.read_csv(csv_path)
    
    print("🎉 LinkedIn Scraping Results with Post URLs!")
    print("=" * 60)
    print(f"📊 Total posts scraped: {len(df)}")
    print(f"📋 Columns captured: {', '.join(df.columns.tolist())}")
    print()
    
    for i, row in df.iterrows():
        print(f"📝 POST {i+1}:")
        print(f"   👤 Author: {row['author_name'] or 'N/A'}")
        print(f"   💼 Title: {row['author_title'][:60] or 'N/A'}{'...' if len(str(row['author_title'])) > 60 else ''}")
        print(f"   📖 Content: {str(row['content'])[:80] or 'N/A'}{'...' if len(str(row['content'])) > 80 else ''}")
        print(f"   🔗 Post URL: {row['post_url'] or 'No URL found'}")
        print(f"   👍 Likes: {row['likes_count']}")
        print(f"   💬 Comments: {row['comments_count']}")
        print(f"   📅 Scraped: {row['scraped_at'][:19]}")
        print("-" * 60)
    
    # Summary
    total_likes = df['likes_count'].sum()
    total_comments = df['comments_count'].sum()
    posts_with_urls = df['post_url'].notna().sum()
    posts_with_content = df['content'].notna().sum()
    
    print("📊 SUMMARY:")
    print(f"   ✅ Posts with URLs: {posts_with_urls}/{len(df)}")
    print(f"   ✅ Posts with content: {posts_with_content}/{len(df)}")
    print(f"   👍 Total engagement: {total_likes} likes, {total_comments} comments")
    
    if posts_with_urls > 0:
        print("\n🔗 POST URLS:")
        for i, url in enumerate(df['post_url'].dropna()):
            print(f"   {i+1}. {url}")

if __name__ == "__main__":
    display_results()
