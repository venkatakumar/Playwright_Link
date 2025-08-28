"""
CEO & CTO Search with Cookie Authentication
==========================================

Run CEO and CTO search using stored cookies
"""

import asyncio
import sys
import os
import re
from cookie_enhanced_scraper import CookieEnhancedLinkedInScraper

async def run_ceo_cto_search():
    print('🎯 CEO & CTO SEARCH WITH COOKIE AUTHENTICATION')
    print('=' * 50)

    # Initialize cookie-enhanced scraper
    scraper = CookieEnhancedLinkedInScraper(headless=False)

    try:
        # Ensure logged in with cookies
        await scraper.ensure_logged_in()

        # Parse industries from env (LINKEDIN_INDUSTRIES), default to Financial Services & Insurance
        env_inds = os.getenv('LINKEDIN_INDUSTRIES', '').strip()
        industries = [s.strip() for s in re.split(r'[;,]', env_inds) if s.strip()] or [
            'Financial Services', 'Insurance'
        ]

        # Search configuration for CEOs, CTOs, Test/QA Managers, CIOs
        search_config = {
            'job_titles': [
                'Chief Executive Officer',
                'CEO',
                'Chief Technology Officer',
                'CTO',
                'Founder & CEO',
                'Co-Founder & CEO',
                'Founder & CTO',
                'Co-Founder & CTO',
                'Executive Director',
                'Managing Director',
                'Test Manager',
                'QA Manager',
                'Head of Testing',
                'CIO',
                'Chief Information Officer',
                'Founder',
                'Co-Founder'
            ],
            'locations': [
                'United Kingdom'
            ],
            # UK region facet for precise filtering
            'geo_urns': ['101165590'],
            'industries': industries,
            'max_profiles': 30,
            'pages': 3
        }
        print(f'📍 Locations: {len(search_config["locations"])} regions')
        print(f'💼 Job Titles: {len(search_config["job_titles"])} variations')
        print(f'📊 Target: {search_config["max_profiles"]} profiles, {search_config["pages"]} pages')
        print(f'🏭 Industries: {", ".join(search_config["industries"]) if search_config["industries"] else "(none)"}')
        print('-' * 50)

        # Run the search (explicit params)
        results = await scraper.run_executive_search_with_cookies(
            job_titles=search_config['job_titles'],
            locations=search_config['locations'],
            max_profiles=search_config['max_profiles'],
            pages_to_scrape=search_config['pages'],
            geo_urns=search_config['geo_urns'],
            industries=search_config['industries']
        )

        # Filter by company size threshold from env (default 200)
        max_size = int(os.getenv('COMPANY_SIZE_MAX', '200'))
        filtered = []
        for profile in results or []:
            size = profile.get('company_size')
            if size is not None:
                try:
                    if int(size) <= max_size:
                        filtered.append(profile)
                except Exception:
                    pass
            else:
                # If size not available, keep for now (optionally skip or enrich later)
                filtered.append(profile)

        if filtered:
            print(f'✅ SUCCESS: Found {len(filtered)} profiles with company size ≤{max_size}!')
            print(f'📁 Results saved to output directory')
            # Show sample of results
            print('\n📋 SAMPLE RESULTS:')
            for i, profile in enumerate(filtered[:5]):
                print(f'{i+1}. {profile.get("name", "N/A")} - {profile.get("current_role", "N/A")}')
                if profile.get('company'):
                    print(f'   🏢 {profile["company"]}')
                if profile.get('location'):
                    print(f'   📍 {profile["location"]}')
                print()

            # Step 2: Engage (connect) with filtered profiles
            print(f'🤝 Attempting to connect with up to {min(len(filtered), 3)} profiles (dry-run by default)...')
            engage_result = await scraper.engage_profiles(filtered, action='connect', limit=3, dry_run=True)
            print(f'✨ Engagement summary: {engage_result}')

            # Step 2b: After connect, send personalized message based on recent activity (stub/demo)
            print('⏳ Waiting before sending messages (simulated)...')
            await asyncio.sleep(2)  # Demo: 2 seconds; real: days
            print(f'✉️ Sending personalized messages to connected profiles (dry-run)...')
            import openai
            openai.api_key = os.getenv('OPENAI_API_KEY')
            for profile in filtered[:3]:
                url = profile.get('profile_url')
                name = profile.get('name', 'there')
                recent_posts = profile.get('recent_posts', [])  # In real code, scrape/feed API
                recent_content = recent_posts[0]['content'] if recent_posts else None
                if recent_content:
                    prompt = f"Write a short, friendly LinkedIn message to {name} referencing their recent post: '{recent_content}'. Keep it professional and relevant."
                    try:
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        message = response.choices[0].message.content.strip()
                    except Exception as e:
                        print(f"OpenAI error: {e}")
                        message = f"Hi {name}, I enjoyed your recent post! Would love to connect and discuss more."
                else:
                    message = f"Hi {name}, great to connect! Looking forward to learning more about your work."
                print(f"Sending to {name} ({url}):\n  {message}\n")
                # Actually attempt to send (dry-run)
                result = await scraper.engage_profiles([profile], action='message', limit=1, message_text=message, dry_run=True)
                print(f"Result: {result}\n")
        else:
            print('❌ No results found after company size filtering')

    # All exception handling is now inside the async function body

        # Search configuration for CEOs, CTOs, Test/QA Managers, CIOs
        search_config = {
            'job_titles': [
                'Chief Executive Officer',
                'CEO',
                'Chief Technology Officer',
                'CTO',
                'Founder & CEO',
                'Co-Founder & CEO',
                'Founder & CTO',
                'Co-Founder & CTO',
                'Executive Director',
                'Managing Director',
                'Test Manager',
                'QA Manager',
                'Head of Testing',
                'CIO',
                'Chief Information Officer',
                'Founder',
                'Co-Founder'
            ],
            'locations': [
                'United Kingdom'
            ],
            # UK region facet for precise filtering
            'geo_urns': ['101165590'],
            'industries': industries,
            'max_profiles': 30,
            'pages': 3
        }
        
        print(f'📍 Locations: {len(search_config["locations"])} regions')
        print(f'💼 Job Titles: {len(search_config["job_titles"])} variations')
        print(f'📊 Target: {search_config["max_profiles"]} profiles, {search_config["pages"]} pages')
        print(f'🏭 Industries: {", ".join(search_config["industries"]) if search_config["industries"] else "(none)"}')
        print('-' * 50)
        
        # Run the search (explicit params)
        results = await scraper.run_executive_search_with_cookies(
            job_titles=search_config['job_titles'],
            locations=search_config['locations'],
            max_profiles=search_config['max_profiles'],
            pages_to_scrape=search_config['pages'],
            geo_urns=search_config['geo_urns'],
            industries=search_config['industries']
        )

        # Filter by company size threshold from env (default 200)
        max_size = int(os.getenv('COMPANY_SIZE_MAX', '200'))
        filtered = []
        for profile in results or []:
            size = profile.get('company_size')
            if size is not None:
                try:
                    if int(size) <= max_size:
                        filtered.append(profile)
                except Exception:
                    pass
            else:
                # If size not available, keep for now (optionally skip or enrich later)
                filtered.append(profile)

        if filtered:
            print(f'✅ SUCCESS: Found {len(filtered)} profiles with company size ≤{max_size}!')
            print(f'📁 Results saved to output directory')
            # Show sample of results
            print('\n📋 SAMPLE RESULTS:')
            for i, profile in enumerate(filtered[:5]):
                print(f'{i+1}. {profile.get("name", "N/A")} - {profile.get("current_role", "N/A")}')
                if profile.get('company'):
                    print(f'   🏢 {profile["company"]}')
                if profile.get('location'):
                    print(f'   📍 {profile["location"]}')
                print()

            # Step 2: Engage (connect) with filtered profiles
            print(f'🤝 Attempting to connect with up to {min(len(filtered), 3)} profiles (dry-run by default)...')
            engage_result = await scraper.engage_profiles(filtered, action='connect', limit=3, dry_run=True)
            print(f'✨ Engagement summary: {engage_result}')

            # Step 2b: After connect, send personalized message based on recent activity (stub/demo)
            print('⏳ Waiting before sending messages (simulated)...')
            await asyncio.sleep(2)  # Demo: 2 seconds; real: days
            print(f'✉️ Sending personalized messages to connected profiles (dry-run)...')
            for profile in filtered[:3]:
                url = profile.get('profile_url')
                name = profile.get('name', 'there')
                recent_posts = profile.get('recent_posts', [])  # In real code, scrape/feed API
                recent_content = recent_posts[0]['content'] if recent_posts else None
                if recent_content:
                    message = f"Hi {name}, I enjoyed your recent post: '{recent_content[:60]}...' Would love to connect and discuss more."
                else:
                    message = f"Hi {name}, great to connect! Looking forward to learning more about your work."
                print(f"Sending to {name} ({url}):\n  {message}\n")
                # Actually attempt to send (dry-run)
                result = await scraper.engage_profiles([profile], action='message', limit=1, message_text=message, dry_run=True)
                print(f"Result: {result}\n")
        else:
            print('❌ No results found after company size filtering')

    except Exception as e:
        print(f'❌ Error: {str(e)}')
    finally:
        try:
            await scraper.shutdown()
        except Exception:
            pass

if __name__ == "__main__":
    # Use Selector policy on Windows to avoid unclosed transport warnings
    if sys.platform.startswith("win"):
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except Exception:
            pass
    asyncio.run(run_ceo_cto_search())
