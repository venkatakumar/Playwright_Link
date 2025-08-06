"""
LinkedIn Selector Discovery Tool
This script will help us find the current post selectors that LinkedIn is using
"""
import asyncio
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv

load_dotenv()

async def discover_selectors():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=False,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        page.set_default_timeout(60000)
        
        try:
            # Login process
            print("🔐 Logging into LinkedIn...")
            await page.goto("https://www.linkedin.com/login")
            await page.fill('input[name="session_key"]', os.getenv('LINKEDIN_EMAIL'))
            await page.fill('input[name="session_password"]', os.getenv('LINKEDIN_PASSWORD'))
            await page.click('button[type="submit"]')
            
            # Handle 2FA if needed
            await page.wait_for_timeout(5000)
            if "challenge" in page.url:
                print("🔐 Complete 2FA and press Enter...")
                input("Press Enter after completing 2FA...")
            
            # Go to feed and wait for content
            print("📱 Navigating to LinkedIn feed...")
            await page.goto("https://www.linkedin.com/feed/")
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(5000)  # Let content load
            
            print("🔍 Analyzing page for post elements...")
            
            # Use JavaScript to find elements that look like posts
            post_analysis = await page.evaluate('''
                () => {
                    const results = {
                        'data_elements': [],
                        'article_elements': [],
                        'feed_classes': [],
                        'post_like_elements': [],
                        'sample_html': ''
                    };
                    
                    // Find elements with data attributes
                    const dataElements = document.querySelectorAll('[data-urn], [data-id], [data-activity-urn]');
                    results.data_elements = Array.from(dataElements).map(el => ({
                        tag: el.tagName,
                        classes: el.className,
                        id: el.id,
                        dataAttrs: Array.from(el.attributes).filter(attr => attr.name.startsWith('data-')).map(attr => attr.name + '=' + attr.value)
                    }));
                    
                    // Find article elements
                    const articles = document.querySelectorAll('article');
                    results.article_elements = Array.from(articles).map(el => ({
                        classes: el.className,
                        role: el.getAttribute('role'),
                        dataAttrs: Array.from(el.attributes).filter(attr => attr.name.startsWith('data-')).map(attr => attr.name + '=' + attr.value)
                    }));
                    
                    // Find elements with feed-related classes
                    const feedElements = document.querySelectorAll('[class*="feed"], [class*="post"], [class*="update"], [class*="activity"]');
                    const feedClasses = new Set();
                    Array.from(feedElements).forEach(el => {
                        el.className.split(' ').forEach(cls => {
                            if (cls.includes('feed') || cls.includes('post') || cls.includes('update') || cls.includes('activity')) {
                                feedClasses.add(cls);
                            }
                        });
                    });
                    results.feed_classes = Array.from(feedClasses);
                    
                    // Find elements that might be posts (with text content)
                    const textElements = document.querySelectorAll('div, article, section');
                    const postLikeElements = [];
                    Array.from(textElements).forEach(el => {
                        const text = el.textContent || '';
                        if (text.length > 50 && text.length < 2000 && 
                            (el.className.includes('feed') || el.className.includes('post') || 
                             el.className.includes('update') || el.getAttribute('data-urn') ||
                             el.getAttribute('data-id'))) {
                            postLikeElements.push({
                                tag: el.tagName,
                                classes: el.className,
                                textLength: text.length,
                                textPreview: text.substring(0, 100) + '...',
                                dataAttrs: Array.from(el.attributes).filter(attr => attr.name.startsWith('data-')).map(attr => attr.name)
                            });
                        }
                    });
                    results.post_like_elements = postLikeElements.slice(0, 5); // Top 5
                    
                    // Get sample HTML from main content area
                    const main = document.querySelector('main, [role="main"], .scaffold-layout__main, .feed-container');
                    if (main) {
                        results.sample_html = main.innerHTML.substring(0, 2000);
                    }
                    
                    return results;
                }
            ''')
            
            print(f"\n📊 Analysis Results:")
            print(f"🔗 Data elements found: {len(post_analysis['data_elements'])}")
            print(f"📄 Article elements found: {len(post_analysis['article_elements'])}")
            print(f"🏷️ Feed-related classes: {len(post_analysis['feed_classes'])}")
            print(f"📝 Post-like elements: {len(post_analysis['post_like_elements'])}")
            
            if post_analysis['data_elements']:
                print("\n🔗 Data elements (first 3):")
                for i, elem in enumerate(post_analysis['data_elements'][:3]):
                    print(f"  {i+1}. {elem['tag']}.{elem['classes'][:50]}")
                    print(f"     Data attrs: {elem['dataAttrs']}")
            
            if post_analysis['article_elements']:
                print("\n📄 Article elements:")
                for i, elem in enumerate(post_analysis['article_elements'][:3]):
                    print(f"  {i+1}. Classes: {elem['classes'][:100]}")
                    print(f"     Data attrs: {elem['dataAttrs']}")
            
            if post_analysis['feed_classes']:
                print(f"\n🏷️ Feed classes: {post_analysis['feed_classes'][:10]}")
            
            if post_analysis['post_like_elements']:
                print("\n📝 Post-like elements:")
                for i, elem in enumerate(post_analysis['post_like_elements']):
                    print(f"  {i+1}. {elem['tag']}.{elem['classes'][:50]}")
                    print(f"     Text: {elem['textPreview']}")
                    print(f"     Data attrs: {elem['dataAttrs']}")
            
            print("\n⏸️ Browser will stay open for manual inspection...")
            print("Press Ctrl+C to close when done.")
            
            # Keep browser open for manual inspection
            await page.wait_for_timeout(300000)  # 5 minutes
            
        except KeyboardInterrupt:
            print("\n👋 Closing browser...")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(discover_selectors())
