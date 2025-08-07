"""
LinkedIn Search Diagnostic Tool
==============================

This script helps diagnose why LinkedIn searches return 0 results
and provides solutions for better search success.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

def analyze_search_keywords():
    """Analyze current search configuration"""
    
    print("🔍 LINKEDIN SEARCH DIAGNOSTIC")
    print("=" * 50)
    
    # Get current configuration
    search_keywords = os.getenv('SEARCH_KEYWORDS', '').strip()
    max_posts = os.getenv('MAX_POSTS', '25')
    
    print(f"Current Configuration:")
    print(f"   • SEARCH_KEYWORDS: '{search_keywords}'")
    print(f"   • MAX_POSTS: {max_posts}")
    print()
    
    # Analyze the search terms
    keywords = [k.strip() for k in search_keywords.split(',') if k.strip()]
    
    print(f"📊 Search Keywords Analysis:")
    print(f"   • Number of keywords: {len(keywords)}")
    print(f"   • Keywords: {keywords}")
    print()
    
    # Check for common issues
    issues = []
    suggestions = []
    
    if len(keywords) == 0:
        issues.append("❌ No search keywords defined")
        suggestions.append("Add search keywords to SEARCH_KEYWORDS in .env file")
    
    if len(keywords) > 5:
        issues.append("⚠️ Too many keywords (LinkedIn may ignore some)")
        suggestions.append("Use 3-5 most important keywords")
    
    # Check keyword specificity
    niche_keywords = ['AutomationTesting', 'AIValidation']
    broad_keywords = ['AI', 'automation', 'testing', 'software', 'technology']
    
    has_niche = any(kw in search_keywords for kw in niche_keywords)
    has_broad = any(kw in search_keywords.lower() for kw in broad_keywords)
    
    if has_niche and not has_broad:
        issues.append("⚠️ Keywords may be too specific/niche")
        suggestions.append("Add broader keywords like 'AI', 'automation', 'testing'")
    
    # Show issues and suggestions
    if issues:
        print("🚨 POTENTIAL ISSUES:")
        for issue in issues:
            print(f"   {issue}")
        print()
    
    if suggestions:
        print("💡 SUGGESTIONS:")
        for suggestion in suggestions:
            print(f"   • {suggestion}")
        print()
    
    return keywords, issues, suggestions

def suggest_better_keywords():
    """Suggest better search keywords"""
    
    print("🎯 BETTER SEARCH KEYWORD SUGGESTIONS")
    print("=" * 50)
    
    categories = {
        "Automation Testing": {
            "broad": ["automation", "testing", "QA", "software testing"],
            "specific": ["selenium", "cypress", "test automation", "automated testing"],
            "trending": ["AI testing", "test automation", "DevOps testing"]
        },
        "AI/ML": {
            "broad": ["AI", "artificial intelligence", "machine learning", "ML"],
            "specific": ["GPT", "LLM", "neural networks", "deep learning"],
            "trending": ["generative AI", "ChatGPT", "AI automation"]
        },
        "General Tech": {
            "broad": ["technology", "software", "programming", "development"],
            "specific": ["Python", "JavaScript", "cloud", "DevOps"],
            "trending": ["remote work", "tech career", "startup"]
        }
    }
    
    for category, keywords in categories.items():
        print(f"📋 {category}:")
        print(f"   Broad terms: {', '.join(keywords['broad'])}")
        print(f"   Specific terms: {', '.join(keywords['specific'])}")
        print(f"   Trending terms: {', '.join(keywords['trending'])}")
        print()
    
    # Recommended combinations
    print("🚀 RECOMMENDED KEYWORD COMBINATIONS:")
    recommendations = [
        "AI, automation, testing",
        "software testing, automation, QA",
        "artificial intelligence, machine learning, AI",
        "technology, software, programming",
        "automation, DevOps, testing",
        "AI testing, test automation, QA"
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    return recommendations

def generate_linkedin_search_urls():
    """Generate LinkedIn search URLs for testing"""
    
    print("\n🔗 LINKEDIN SEARCH URL TESTING")
    print("=" * 50)
    
    test_keywords = [
        "AI",
        "automation testing", 
        "software testing",
        "AI, automation",
        "testing, QA, automation",
        "artificial intelligence"
    ]
    
    print("Generated LinkedIn search URLs for testing:")
    for keywords in test_keywords:
        encoded_keywords = quote_plus(keywords)
        url = f"https://www.linkedin.com/search/results/content/?keywords={encoded_keywords}"
        print(f"   • '{keywords}': {url}")
    
    print("\n💡 How to test manually:")
    print("   1. Copy any URL above")
    print("   2. Open in browser while logged into LinkedIn")
    print("   3. Check if posts appear")
    print("   4. Use keywords that show posts in your scraper")

def check_current_search_url():
    """Check what URL the scraper is actually using"""
    
    print("\n🔍 CURRENT SCRAPER SEARCH URL")
    print("=" * 40)
    
    search_keywords = os.getenv('SEARCH_KEYWORDS', '').strip()
    
    if search_keywords:
        # This is how the scraper builds the URL
        keywords_list = [k.strip() for k in search_keywords.split(',') if k.strip()]
        search_query = ' OR '.join(f'"{keyword}"' for keyword in keywords_list)
        encoded_query = quote_plus(search_query)
        
        url = f"https://www.linkedin.com/search/results/content/?keywords={encoded_query}&page=1"
        
        print(f"Current search terms: {keywords_list}")
        print(f"Search query: {search_query}")
        print(f"Generated URL: {url}")
        print()
        print("💡 Test this URL manually in your browser to see if it returns posts!")
    else:
        print("❌ No search keywords configured in .env file")

async def test_broader_search():
    """Test with broader search terms"""
    
    print("\n🧪 TESTING WITH BROADER SEARCH TERMS")
    print("=" * 50)
    
    print("Recommendation: Try these search term combinations:")
    print("1. 'AI' (very broad - should return many posts)")
    print("2. 'automation' (broad - should return posts)")
    print("3. 'testing' (broad - should return posts)")
    print("4. 'software testing' (moderate - should return some posts)")
    print("5. 'automation testing' (specific - may return fewer posts)")
    print()
    print("💡 Start with #1 (AI) to verify your scraper works,")
    print("   then gradually make searches more specific!")

def main():
    """Main diagnostic function"""
    
    keywords, issues, suggestions = analyze_search_keywords()
    recommendations = suggest_better_keywords()
    generate_linkedin_search_urls()
    check_current_search_url()
    
    print("\n🎯 QUICK FIX RECOMMENDATIONS")
    print("=" * 40)
    print("1. 🔧 IMMEDIATE FIX - Try broader keywords:")
    print("   Update SEARCH_KEYWORDS in .env to: AI, automation, testing")
    print()
    print("2. 🧪 TEST APPROACH:")
    print("   • Start with 'AI' only (should get many results)")
    print("   • Then try 'automation, testing'")
    print("   • Finally use your specific terms")
    print()
    print("3. 🔍 MANUAL VERIFICATION:")
    print("   • Copy the generated URL above")
    print("   • Test in browser while logged into LinkedIn")
    print("   • Verify posts appear before running scraper")
    print()
    print("4. ⚙️ ALTERNATIVE APPROACH:")
    print("   • Use broader terms to get posts")
    print("   • Filter results after scraping")
    print("   • Look for your keywords in the content")

if __name__ == "__main__":
    main()
