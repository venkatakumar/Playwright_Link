"""
Enhanced LinkedIn Scraper Demo - HIGH IMPACT FEATURES
=====================================================

This script demonstrates the newly implemented high-impact features:
1. Author name splitting (firstName/lastName)
2. Hashtag extraction from content
3. Better timestamp formatting (ISO + relative time)
"""

import asyncio
from pathlib import Path
import json
import pandas as pd
from utils import enhance_post_data


def demo_enhanced_features():
    """Demonstrate the new enhancement features with sample data"""
    
    print("🚀 ENHANCED LINKEDIN SCRAPER FEATURES DEMO")
    print("=" * 60)
    print("Demonstrating 3 high-impact, easy-to-implement features:")
    print("1. ✅ Author name splitting (firstName/lastName)")
    print("2. ✅ Hashtag extraction from content")
    print("3. ✅ Better timestamp formatting (ISO + relative time)")
    print()
    
    # Sample post data (before enhancement)
    sample_posts = [
        {
            "content": "Excited to announce our new AI breakthrough! 🚀 This technology will revolutionize the industry. #AI #Innovation #TechNews #MachineLearning",
            "author_name": "Dr. Sarah Johnson",
            "author_title": "Chief Technology Officer at TechCorp",
            "post_date": "2025-08-07T08:30:00Z",
            "post_url": "https://www.linkedin.com/feed/update/urn:li:activity:1234567890/",
            "likes_count": 245,
            "comments_count": 32,
            "image_urls": [],
            "scraped_at": "2025-08-07T12:00:00Z"
        },
        {
            "content": "Just finished an amazing conference on machine learning. Key takeaways: 1) Data quality is crucial 2) Model interpretability matters 3) Ethics in AI is non-negotiable. Thanks @DataConf @MLConference for organizing! 📈 #DataScience #Ethics",
            "author_name": "Michael Chen",
            "author_title": "Senior Data Scientist at AI Solutions Inc",
            "post_date": "2025-08-06T16:45:00Z",
            "post_url": "https://www.linkedin.com/feed/update/urn:li:activity:1234567891/",
            "likes_count": 156,
            "comments_count": 24,
            "image_urls": ["https://media.licdn.com/dms/image/example1.jpg"],
            "scraped_at": "2025-08-07T12:00:00Z"
        },
        {
            "content": "Proud to share our team's latest research paper on neural networks. This represents 2 years of hard work! 🧠💡 #Research #DeepLearning #AI #NeuralNetworks #Academia",
            "author_name": "Prof. Elena Rodriguez",
            "author_title": "Research Director at University Tech Lab",
            "post_date": "2025-08-05T10:15:00Z",
            "post_url": "https://www.linkedin.com/feed/update/urn:li:activity:1234567892/",
            "likes_count": 89,
            "comments_count": 15,
            "image_urls": [],
            "scraped_at": "2025-08-07T12:00:00Z"
        }
    ]
    
    print("📊 PROCESSING SAMPLE POSTS...")
    print("-" * 40)
    
    enhanced_posts = []
    
    for i, post in enumerate(sample_posts, 1):
        print(f"\n🔄 Processing Post {i}:")
        print(f"   Original Author: '{post['author_name']}'")
        print(f"   Original Content Preview: '{post['content'][:50]}...'")
        print(f"   Original Date: '{post['post_date']}'")
        
        # Apply enhancements
        enhanced_post = enhance_post_data(post)
        enhanced_posts.append(enhanced_post)
        
        # Show the enhancements
        print(f"   ✅ First Name: '{enhanced_post['author_firstName']}'")
        print(f"   ✅ Last Name: '{enhanced_post['author_lastName']}'")
        print(f"   ✅ Hashtags: {enhanced_post['hashtags']}")
        print(f"   ✅ Mentions: {enhanced_post['mentions']}")
        print(f"   ✅ ISO Timestamp: '{enhanced_post['postedAtISO']}'")
        print(f"   ✅ Relative Time: '{enhanced_post['timeSincePosted']}'")
        print(f"   ✅ Post Type: '{enhanced_post['post_type']}'")
    
    # Save enhanced data to demonstrate export capabilities
    print(f"\n💾 SAVING ENHANCED DATA...")
    print("-" * 30)
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Save as JSON
    json_path = output_dir / "enhanced_demo_posts.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(enhanced_posts, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON saved: {json_path}")
    
    # Save as CSV
    csv_path = output_dir / "enhanced_demo_posts.csv"
    
    # Prepare CSV data
    csv_data = []
    for post in enhanced_posts:
        csv_row = {
            # Original fields
            'content': post.get('content', ''),
            'author_name': post.get('author_name', ''),
            'author_title': post.get('author_title', ''),
            'post_date': post.get('post_date', ''),
            'post_url': post.get('post_url', ''),
            'likes_count': post.get('likes_count', 0),
            'comments_count': post.get('comments_count', 0),
            'image_urls': '; '.join(post.get('image_urls', [])),
            'scraped_at': post.get('scraped_at', ''),
            
            # 🚀 NEW ENHANCED FIELDS
            'author_firstName': post.get('author_firstName', ''),
            'author_lastName': post.get('author_lastName', ''),
            'hashtags': '; '.join(post.get('hashtags', [])),
            'mentions': '; '.join(post.get('mentions', [])),
            'postedAtISO': post.get('postedAtISO', ''),
            'timeSincePosted': post.get('timeSincePosted', ''),
            'post_type': post.get('post_type', ''),
            'enhanced_at': post.get('enhanced_at', ''),
        }
        csv_data.append(csv_row)
    
    df = pd.DataFrame(csv_data)
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"✅ CSV saved: {csv_path}")
    
    # Save as Excel if openpyxl is available
    try:
        excel_path = output_dir / "enhanced_demo_posts.xlsx"
        df.to_excel(excel_path, index=False, engine='openpyxl')
        print(f"✅ Excel saved: {excel_path}")
    except ImportError:
        print("⚠️ Excel export requires openpyxl: pip install openpyxl")
    except Exception as e:
        print(f"⚠️ Excel export failed: {str(e)}")
    
    # Show analytics
    print(f"\n📈 ENHANCED DATA ANALYTICS")
    print("-" * 30)
    
    total_hashtags = sum(len(post['hashtags']) for post in enhanced_posts)
    total_mentions = sum(len(post['mentions']) for post in enhanced_posts)
    
    all_hashtags = []
    for post in enhanced_posts:
        all_hashtags.extend(post['hashtags'])
    
    unique_hashtags = list(set(all_hashtags))
    
    print(f"📊 Posts processed: {len(enhanced_posts)}")
    print(f"📊 Total hashtags found: {total_hashtags}")
    print(f"📊 Unique hashtags: {len(unique_hashtags)}")
    print(f"📊 Total mentions found: {total_mentions}")
    print(f"📊 Most common hashtags: {unique_hashtags[:5]}")
    
    post_types = [post['post_type'] for post in enhanced_posts]
    type_counts = {ptype: post_types.count(ptype) for ptype in set(post_types)}
    print(f"📊 Post types: {type_counts}")
    
    return enhanced_posts


def demo_field_comparison():
    """Show before/after field comparison"""
    
    print(f"\n🔍 FIELD COMPARISON: BEFORE vs AFTER")
    print("=" * 60)
    
    before_fields = [
        'content', 'author_name', 'author_title', 'post_date', 'post_url',
        'likes_count', 'comments_count', 'image_urls', 'scraped_at'
    ]
    
    after_fields = before_fields + [
        'author_firstName', 'author_lastName', 'hashtags', 'mentions',
        'postedAtISO', 'timeSincePosted', 'post_type', 'enhanced_at'
    ]
    
    print(f"📊 BEFORE Enhancement: {len(before_fields)} fields")
    for field in before_fields:
        print(f"   • {field}")
    
    print(f"\n📊 AFTER Enhancement: {len(after_fields)} fields (+{len(after_fields) - len(before_fields)} new)")
    for field in after_fields:
        if field in before_fields:
            print(f"   • {field}")
        else:
            print(f"   • {field} 🆕")
    
    improvement = ((len(after_fields) - len(before_fields)) / len(before_fields)) * 100
    print(f"\n🎯 Feature Improvement: +{improvement:.1f}% more data fields!")


if __name__ == "__main__":
    # Run the demo
    enhanced_posts = demo_enhanced_features()
    demo_field_comparison()
    
    print(f"\n🎉 ENHANCEMENT DEMO COMPLETE!")
    print("=" * 50)
    print("✅ Successfully implemented 3 high-impact features:")
    print("   1. Author name splitting (firstName/lastName)")
    print("   2. Hashtag extraction from post content")
    print("   3. Better timestamp formatting (ISO + relative time)")
    print()
    print("🚀 NEXT STEPS:")
    print("   • Run the real scraper: python linkedin_scraper.py")
    print("   • Check enhanced output files in the output/ folder")
    print("   • Compare with enterprise-level JSON structure")
    print("   • Ready to implement Phase 2 enhancements!")
    print()
    print("💡 Your scraper now extracts significantly more valuable data!")
