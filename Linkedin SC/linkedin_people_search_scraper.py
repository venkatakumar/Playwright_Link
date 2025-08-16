"""
LinkedIn People Search Scraper
==============================

This scraper finds and extracts CEO/CTO profiles based on location and job title filters.
It uses LinkedIn's people search with specific filters to find executives.

Usage:
- Search for CEOs, CTOs, Founders, etc.
- Filter by location (city, country, region)
- Extract profile data: name, role, company, profile URL, location
- Export results in multiple formats
"""

import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import os
from datetime import datetime
import json
import urllib.parse

load_dotenv()

class LinkedInPeopleSearchScraper:
    def __init__(self):
        self.profiles_data = []
        self.browser = None
        self.page = None
        # Track seen profile URLs to avoid duplicates across strategies
        self._seen_profile_urls = set()
        
    def _normalize_codes(self, values):
        """Convert a list of values to list of string codes (e.g., 42 -> "42")."""
        if not values:
            return []
        out = []
        for v in values:
            s = str(v).strip()
            if s:
                out.append(s)
        return out

    def map_industries_to_codes(self, industries):
        """Map common industry names to LinkedIn industry codes. Accepts codes too."""
        if not industries:
            return []
        mapping = {
            'financial services': '42',
            'insurance': '43',
            'investment management': '41',
            'banking': '47',
            'capital markets': '48',
            'fintech': '42',
            'wealth management': '41',
        }
        codes = []
        for item in industries:
            s = str(item).strip()
            if s.isdigit():
                codes.append(s)
            else:
                key = s.lower()
                if key in mapping:
                    codes.append(mapping[key])
        # de-duplicate while preserving order
        seen = set()
        dedup = []
        for c in codes:
            if c not in seen:
                seen.add(c)
                dedup.append(c)
        return dedup
    
    async def dismiss_premium_popup(self):
        """Dismiss LinkedIn Premium/upgrade popups if present."""
        if not self.page:
            return False
        try:
            # Common close/dismiss buttons
            candidates = [
                '.artdeco-modal__dismiss',
                'button[aria-label="Dismiss"]',
                'button[aria-label="Close"]',
                'button[aria-label*="Close"]',
                'button:has-text("No thanks")',
                'button:has-text("Not now")',
                'button:has-text("Maybe later")',
                'button:has-text("Skip")',
                'button:has-text("Not Now")',
            ]
            # Quick scan for a dialog
            dialog = await self.page.query_selector('div[role="dialog"], .artdeco-modal')
            if dialog:
                for sel in candidates:
                    try:
                        btn = await self.page.query_selector(sel)
                        if btn:
                            await btn.click()
                            await self.page.wait_for_timeout(400)
                            return True
                    except Exception:
                        pass
                # Fallback: press Escape to close modal
                try:
                    await self.page.keyboard.press('Escape')
                    await self.page.wait_for_timeout(300)
                    return True
                except Exception:
                    pass
            else:
                # Sometimes the popup is inline; try clicking any visible dismiss button anyway
                for sel in candidates:
                    try:
                        btn = await self.page.query_selector(sel)
                        if btn:
                            await btn.click()
                            await self.page.wait_for_timeout(300)
                            return True
                    except Exception:
                        pass
        except Exception:
            # Non-fatal
            return False
        return False
        
    async def login_linkedin(self):
        """Login to LinkedIn with 2FA support"""
        print("🔐 Logging into LinkedIn...")
        
        email = os.getenv('LINKEDIN_EMAIL')
        password = os.getenv('LINKEDIN_PASSWORD')
        
        if not email or not password:
            raise ValueError("Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env file")
        
        await self.page.goto("https://www.linkedin.com/login")
        
        # Fill credentials
        await self.page.fill('input[name="session_key"]', email)
        await self.page.fill('input[name="session_password"]', password)
        await self.page.click('button[type="submit"]')
        
        await self.page.wait_for_timeout(3000)
        
        # Handle 2FA if needed
        if "checkpoint" in self.page.url or "challenge" in self.page.url:
            print("🔐 2FA detected. Complete verification in browser, then press Enter...")
            input()
            await self.page.wait_for_timeout(3000)
        
        # Verify login by going to search page
        await self.page.goto("https://www.linkedin.com/search/results/people/")
        await self.page.wait_for_timeout(2000)
        
        print("✅ Successfully logged in!")
    
    def build_people_search_url(self, job_titles, locations, industries=None, additional_filters=None, geo_urns=None, origin='GLOBAL_SEARCH_HEADER', sid=None, keywords_override: str | None = None):
        """
        Build LinkedIn people search URL with filters
        
        Args:
            job_titles: List of job titles (e.g., ['CEO', 'CTO', 'Chief Executive Officer'])
            locations: List of locations (e.g., ['London', 'United Kingdom', 'San Francisco'])
            additional_filters: Dict of additional filters
            
        Returns:
            Formatted LinkedIn people search URL
        """
        base_url = "https://www.linkedin.com/search/results/people/"

        # Build keywords parameter - use override when provided
        if keywords_override and keywords_override.strip():
            keywords = keywords_override.strip()
        else:
            # plain OR list without quotes/parentheses
            keywords = " OR ".join(job_titles) if job_titles else ""
        
        # URL encode the parameters
        # Choose origin: use FACETED_SEARCH when we have facets
        origin_param = origin
        if (industries or geo_urns) and origin_param == 'GLOBAL_SEARCH_HEADER':
            origin_param = 'FACETED_SEARCH'
        params = {
            'keywords': keywords,
            'origin': origin_param,
        }
        
        # Add industry codes if provided
        if industries:
            import json as _json
            codes = self.map_industries_to_codes(industries)
            if codes:
                params['industry'] = _json.dumps(codes, separators=(',', ':'))

        # Add geo URNs if provided (preferred to text locations)
        if geo_urns:
            import json as _json
            params['geoUrn'] = _json.dumps(self._normalize_codes(geo_urns), separators=(',', ':'))

        # Add additional filters
        if additional_filters:
            params.update(additional_filters)
        if sid:
            params['sid'] = sid

        # Build final URL
        query_string = urllib.parse.urlencode(params, safe='"[]:,')
        final_url = f"{base_url}?{query_string}"
        
        print(f"🔍 Search URL: {final_url}")
        return final_url
    
    async def apply_search_filters(self, job_titles, locations, industries=None):
        """
        Apply search filters using LinkedIn's filter interface
        
        Args:
            job_titles: List of job titles to search for
            locations: List of locations to filter by
        """
        print("🔍 Applying search filters...")
        
        # Go to people search page
        await self.page.goto("https://www.linkedin.com/search/results/people/")
        await self.page.wait_for_load_state('domcontentloaded')
        await self.page.wait_for_timeout(1200)
        # Dismiss optional upsell popup if shown
        await self.dismiss_premium_popup()
        
        # Enter job titles in search box
        search_box = await self.page.query_selector('input[placeholder*="Search"], input[aria-label*="Search"]')
        if search_box:
            # Combine job titles with industries if provided
            titles_expr = " OR ".join(job_titles) if job_titles else ""
            industry_expr = " OR ".join(industries) if industries else ""
            if titles_expr and industry_expr:
                search_keywords = f'({titles_expr}) AND ({industry_expr})'
            else:
                search_keywords = titles_expr or industry_expr
            await search_box.fill(search_keywords)
            await self.page.keyboard.press("Enter")
            await self.page.wait_for_load_state('domcontentloaded')
            await self.page.wait_for_timeout(1500)
            await self.dismiss_premium_popup()
        
        # Ensure People tab is active
        try:
            people_tab = await self.page.query_selector('button[aria-label="People"], a[aria-label="People"]')
            if people_tab:
                await people_tab.click()
                await self.page.wait_for_timeout(1200)
        except Exception:
            pass
        
        # Apply location filter
        if locations:
            try:
                # Look for "All filters" button
                all_filters_btn = await self.page.query_selector('button[aria-label="All filters"], button:has-text("All filters")')
                if all_filters_btn:
                    await all_filters_btn.click()
                    await self.page.wait_for_selector('div[role="dialog"], .search-reusables__secondary-filters', timeout=6000)
                    await self.page.wait_for_timeout(800)
                    
                    # Look for location input in filter modal
                    location_input = await self.page.query_selector('input[placeholder*="Add a location"], input[aria-label*="Add a location"], input[placeholder*="Location"]')
                    if location_input:
                        await location_input.fill(locations[0])  # Use first location
                        await self.page.wait_for_timeout(1200)
                        
                        # Click on location suggestion
                        location_suggestion = await self.page.query_selector('.basic-typeahead__triggered-content button, .search-reusables__secondary-filters button[role="option"]')
                        if location_suggestion:
                            await location_suggestion.click()
                            await self.page.wait_for_timeout(800)

                    # Apply industry filters by clicking labels
                    if industries:
                        for ind in industries:
                            try:
                                label = await self.page.query_selector(f'label:has-text("{ind}")')
                                if label:
                                    await label.click()
                                    await self.page.wait_for_timeout(400)
                            except Exception:
                                pass
                    
                    # Apply filters
                    apply_btn = await self.page.query_selector('button:has-text("Show results"), button:has-text("Apply"), button[data-control-name="filter_apply"]')
                    if apply_btn:
                        await apply_btn.click()
                        await self.page.wait_for_load_state('domcontentloaded')
                        await self.page.wait_for_timeout(2000)
                        await self.dismiss_premium_popup()
            except Exception as e:
                print(f"⚠️ Could not apply location filter: {str(e)}")
        
        print("✅ Filters applied successfully!")
    
    async def extract_profile_data(self, profile_element):
        """
        Extract data from a single profile search result
        
        Args:
            profile_element: Playwright element of the profile container
            
        Returns:
            Dictionary with profile data
        """
        profile_data = {}
        
        try:
            # Extract name
            name_element = await profile_element.query_selector('.entity-result__title-text a, .app-aware-link .actor-name')
            if name_element:
                profile_data['name'] = (await name_element.inner_text()).strip()
                # Extract profile URL
                profile_url = await name_element.get_attribute('href')
                if profile_url:
                    if profile_url.startswith('/'):
                        profile_data['profile_url'] = f"https://www.linkedin.com{profile_url}"
                    else:
                        profile_data['profile_url'] = profile_url
                else:
                    profile_data['profile_url'] = ""
            else:
                profile_data['name'] = "Unknown"
                profile_data['profile_url'] = ""
            
            # Extract current role/title
            title_element = await profile_element.query_selector('.entity-result__primary-subtitle, .actor-occupation')
            if title_element:
                profile_data['current_role'] = (await title_element.inner_text()).strip()
            else:
                profile_data['current_role'] = ""
            
            # Extract company
            company_element = await profile_element.query_selector('.entity-result__secondary-subtitle, .actor-meta .t-black--light')
            if company_element:
                profile_data['company'] = (await company_element.inner_text()).strip()
            else:
                profile_data['company'] = ""
            
            # Extract location
            location_element = await profile_element.query_selector('.entity-result__location, .actor-location')
            if location_element:
                profile_data['location'] = (await location_element.inner_text()).strip()
            else:
                profile_data['location'] = ""
            
            # Extract summary/headline if available
            summary_element = await profile_element.query_selector('.entity-result__summary')
            if summary_element:
                profile_data['summary'] = (await summary_element.inner_text()).strip()
            else:
                profile_data['summary'] = ""
            
            # Extract mutual connections if available
            connections_element = await profile_element.query_selector('.entity-result__connections')
            if connections_element:
                profile_data['mutual_connections'] = (await connections_element.inner_text()).strip()
            else:
                profile_data['mutual_connections'] = ""
            
            # Add metadata
            profile_data['scraped_at'] = datetime.now().isoformat()
            profile_data['search_type'] = 'people_search'
            
            return profile_data
            
        except Exception as e:
            print(f"⚠️ Error extracting profile data: {str(e)}")
            return None
    
    async def scrape_people_search_results(self, max_profiles=50, pages_to_scrape=5):
        """
        Scrape people search results across multiple pages
        
        Args:
            max_profiles: Maximum number of profiles to collect
            pages_to_scrape: Maximum number of pages to scrape
            
        Returns:
            List of profile data dictionaries
        """
        print(f"📊 Scraping up to {max_profiles} profiles across {pages_to_scrape} pages...")

        collected_profiles = 0
        current_page = 1

        while collected_profiles < max_profiles and current_page <= pages_to_scrape:
            print(f"\n📄 Scraping page {current_page}...")

            # Capture Voyager API responses for debugging/data fallback
            api_payloads = []

            async def _on_response(response):
                try:
                    url = response.url
                    if '/voyager/api/graphql' in url and 'search' in url.lower():
                        data = await response.json()
                        api_payloads.append(data)
                except Exception:
                    pass

            self.page.on('response', _on_response)

            # Wait for results to load
            try:
                await self.page.wait_for_selector(
                    '.reusable-search__entity-result-list, .search-reusables__filters-bar',
                    timeout=6000,
                )
            except Exception:
                # Fallback wait
                await self.page.wait_for_timeout(3000)

            # Close any upsell modal that might block content
            await self.dismiss_premium_popup()

            # Ensure People tab is active if tabs exist
            try:
                people_btn = await self.page.query_selector('button[aria-label="People"], a[aria-label="People"]')
                if people_btn:
                    await people_btn.click()
                    await self.page.wait_for_timeout(1200)
            except Exception:
                pass

            # Gentle scroll to trigger lazy rendering
            try:
                for _ in range(6):
                    await self.page.mouse.wheel(0, 1200)
                    await self.page.wait_for_timeout(600)
                await self.page.mouse.wheel(0, -2400)
                await self.page.wait_for_timeout(500)
            except Exception:
                pass

            # Find all profile containers
            profile_containers = await self.page.query_selector_all(
                '.entity-result__item, .reusable-search__result-container, .search-result__wrapper, '
                'ul.reusable-search__entity-result-list li, '
                'div[data-view-name="search-serp_entity-result"]'
            )

            # Fallback: try detecting profile anchors when container selectors fail
            if not profile_containers:
                anchors = await self.page.query_selector_all('a.app-aware-link[href*="/in/"]')
                print(f"📊 Container selectors empty; found {len(anchors)} profile links")
                for a in anchors:
                    try:
                        parent = await a.evaluate_handle(
                            'el => el.closest(".reusable-search__result-container, .entity-result__item") || el.parentElement'
                        )
                        if parent:
                            profile_containers.append(parent)
                    except Exception:
                        pass

            print(f"📊 Found {len(profile_containers)} profiles on page {current_page}")

            if len(profile_containers) == 0:
                # Try to parse captured GraphQL payloads as a fallback
                parsed_from_api = []
                try:
                    for payload in api_payloads:
                        parsed_from_api.extend(self._parse_profiles_from_voyager_payload(payload))
                except Exception:
                    pass

                # Deduplicate by profile_url and respect max_profiles
                added_from_api = 0
                for prof in parsed_from_api:
                    url = prof.get('profile_url')
                    if not url or url in self._seen_profile_urls:
                        continue
                    self._seen_profile_urls.add(url)
                    self.profiles_data.append(prof)
                    collected_profiles += 1
                    added_from_api += 1
                    print(
                        f"✅ (API) Profile {collected_profiles}: {prof.get('name','')} - {prof.get('current_role','')}"
                    )
                    if collected_profiles >= max_profiles:
                        break
                if added_from_api > 0:
                    print(
                        f"📡 Recovered {added_from_api} profiles from network payloads on page {current_page}"
                    )

                try:
                    cur_url = self.page.url
                    title = await self.page.title()
                    print(f"🔎 Debug: URL={cur_url}")
                    print(f"🔎 Debug: Title={title}")
                    # Save debug artifacts
                    os.makedirs('output', exist_ok=True)
                    await self.page.screenshot(
                        path=f'output/debug_search_page_{current_page}.png', full_page=True
                    )
                    html = await self.page.content()
                    with open(
                        f'output/debug_search_page_{current_page}.html', 'w', encoding='utf-8'
                    ) as f:
                        f.write(html)
                    # Save any captured API payloads
                    if api_payloads:
                        for i, payload in enumerate(api_payloads, 1):
                            try:
                                with open(
                                    f'output/api_debug_page_{current_page}_{i}.json',
                                    'w',
                                    encoding='utf-8',
                                ) as jf:
                                    json.dump(payload, jf, ensure_ascii=False, indent=2)
                            except Exception:
                                pass
                    print(
                        f"🧪 Saved debug artifacts for page {current_page} in output/ directory"
                    )
                except Exception:
                    pass

            # Extract data from each profile
            for container in profile_containers:
                if collected_profiles >= max_profiles:
                    break

                profile_data = await self.extract_profile_data(container)
                if profile_data and profile_data['name'] != "Unknown":
                    # de-dup by URL
                    url = profile_data.get('profile_url')
                    if url and url in self._seen_profile_urls:
                        continue
                    if url:
                        self._seen_profile_urls.add(url)
                    self.profiles_data.append(profile_data)
                    collected_profiles += 1
                    print(
                        f"✅ Profile {collected_profiles}: {profile_data['name']} - {profile_data['current_role']}"
                    )

            # Try to go to next page
            if current_page < pages_to_scrape and collected_profiles < max_profiles:
                try:
                    next_button = await self.page.query_selector(
                        'button[aria-label="Next"], .artdeco-pagination__button--next'
                    )
                    if next_button and not await next_button.is_disabled():
                        await next_button.click()
                        await self.page.wait_for_timeout(3000)
                        await self.dismiss_premium_popup()
                        current_page += 1
                    else:
                        print("📄 No more pages available")
                        # Clean up listener before breaking
                        try:
                            self.page.off('response', _on_response)
                        except Exception:
                            pass
                        break
                except Exception as e:
                    print(f"⚠️ Could not navigate to next page: {str(e)}")
                    try:
                        self.page.off('response', _on_response)
                    except Exception:
                        pass
                    break
            else:
                # Clean up listener before breaking
                try:
                    self.page.off('response', _on_response)
                except Exception:
                    pass
                break

        print(f"\n🎉 Collected {len(self.profiles_data)} profiles total!")
        return self.profiles_data

    def _parse_profiles_from_voyager_payload(self, payload):
        """Traverse LinkedIn voyager GraphQL payloads and extract profile-like entities.

        Heuristics-based to be resilient to schema changes.
        Returns a list of dicts compatible with save_profiles_data columns.
        """
        results = []

        def build_profile(node):
            name = None
            profile_url = None
            current_role = ''
            company = ''
            location = ''

            # URL via publicIdentifier or navigationUrl
            public_id = node.get('publicIdentifier') if isinstance(node, dict) else None
            if isinstance(public_id, str) and public_id:
                profile_url = f"https://www.linkedin.com/in/{public_id}"
            nav_url = node.get('navigationUrl') if isinstance(node, dict) else None
            if isinstance(nav_url, str) and '/in/' in nav_url:
                # Strip query params for cleanliness
                profile_url = nav_url.split('?')[0]

            # Name via first/last or title/name
            if isinstance(node, dict):
                fn = node.get('firstName')
                ln = node.get('lastName')
                if isinstance(fn, str) or isinstance(ln, str):
                    name = ' '.join([s for s in [fn, ln] if isinstance(s, str) and s.strip()]).strip() or None
                if not name:
                    title = node.get('title') or node.get('name') or node.get('label')
                    if isinstance(title, str):
                        name = title

                # Role/headline
                headline = node.get('headline') or node.get('primarySubtitle') or node.get('subline') or node.get('subtitle') or node.get('occupation')
                if isinstance(headline, str):
                    current_role = headline

                # Company not reliably separate; sometimes in headline
                # Location
                loc = node.get('location') or node.get('secondarySubtitle') or node.get('locationName')
                if isinstance(loc, str):
                    location = loc

            if profile_url and name:
                return {
                    'name': name.strip(),
                    'profile_url': profile_url,
                    'current_role': (current_role or '').strip(),
                    'company': (company or '').strip(),
                    'location': (location or '').strip(),
                    'summary': '',
                    'mutual_connections': '',
                    'scraped_at': datetime.now().isoformat(),
                    'search_type': 'people_search'
                }
            return None

        def traverse(node):
            if isinstance(node, dict):
                # Candidate profile nodes often live under keys like 'entity', 'miniProfile', 'item', 'hitInfo'
                for key, val in node.items():
                    if isinstance(val, (dict, list)):
                        traverse(val)
                # Try to build from this dict itself
                prof = build_profile(node)
                if prof:
                    results.append(prof)
            elif isinstance(node, list):
                for item in node:
                    traverse(item)

        try:
            traverse(payload)
        except Exception:
            return []

        # Deduplicate by profile_url while preserving order
        seen = set()
        uniq = []
        for r in results:
            url = r.get('profile_url')
            if url and url not in seen:
                seen.add(url)
                uniq.append(r)
        return uniq
    
    async def save_profiles_data(self, filename_base="linkedin_executives"):
        """Save collected profile data in multiple formats"""
        print("💾 Saving profile data...")
        
        # Create output directory
        os.makedirs('output', exist_ok=True)
        
        # Create DataFrame
        # Ensure we always produce files with headers even if empty
        columns = [
            'name','profile_url','current_role','company','location','summary',
            'mutual_connections','scraped_at','search_type','title_category','company_size'
        ]
        df = pd.DataFrame(self.profiles_data) if self.profiles_data else pd.DataFrame(columns=columns)
        
        # Add analysis columns
        df['title_category'] = df['current_role'].apply(self.categorize_title)
        df['company_size'] = df['company'].apply(self.estimate_company_size)

        # Save as CSV
        csv_path = f"output/{filename_base}.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"✅ Saved {len(self.profiles_data)} profiles to {csv_path}")
        
        # Save as JSON
        json_path = f"output/{filename_base}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.profiles_data, f, indent=2, ensure_ascii=False, default=str)
        print(f"✅ Saved JSON to {json_path}")
        
        # Save as Excel
        excel_path = f"output/{filename_base}.xlsx"
        df.to_excel(excel_path, index=False)
        print(f"✅ Saved Excel to {excel_path}")
        
        # Print summary
        print(f"\n📊 PROFILE COLLECTION SUMMARY:")
        print(f"Total Profiles: {len(self.profiles_data)}")
        if not df.empty:
            print(f"Unique Companies: {df['company'].nunique()}")
            print(f"Locations: {df['location'].nunique()}")
            title_counts = df['title_category'].value_counts()
            print(f"\nTitle Distribution:")
            for title, count in title_counts.items():
                print(f"  {title}: {count}")
        else:
            print("(No data rows; files created with headers)")
        
        return self.profiles_data
    
    def categorize_title(self, title):
        """Categorize job titles"""
        if not title:
            return "Unknown"
        
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['ceo', 'chief executive', 'founder', 'co-founder']):
            return "CEO/Founder"
        elif any(word in title_lower for word in ['cto', 'chief technology', 'chief technical']):
            return "CTO"
        elif any(word in title_lower for word in ['cfo', 'chief financial']):
            return "CFO"
        elif any(word in title_lower for word in ['coo', 'chief operating']):
            return "COO"
        elif any(word in title_lower for word in ['vp', 'vice president', 'director']):
            return "VP/Director"
        elif any(word in title_lower for word in ['president', 'managing director']):
            return "President/MD"
        else:
            return "Other Executive"
    
    def estimate_company_size(self, company):
        """Estimate company size based on known companies"""
        if not company:
            return "Unknown"
        
        # This is a simplified categorization
        # In a real implementation, you'd use a company database
        company_lower = company.lower()
        
        large_companies = ['google', 'microsoft', 'apple', 'amazon', 'meta', 'tesla', 'netflix']
        if any(comp in company_lower for comp in large_companies):
            return "Large (10000+)"
        else:
            return "To be determined"
    
    async def run_executive_search(self, job_titles, locations, max_profiles=50, pages_to_scrape=5):
        """
        Main execution function for executive search
        
        Args:
            job_titles: List of executive titles to search for
            locations: List of locations to filter by
            max_profiles: Maximum profiles to collect
            pages_to_scrape: Maximum pages to scrape
        """
        print("🎯 LINKEDIN EXECUTIVE SEARCH SCRAPER")
        print("=" * 50)
        print(f"🔍 Searching for: {', '.join(job_titles)}")
        print(f"📍 Locations: {', '.join(locations)}")
        print(f"🎯 Target: {max_profiles} profiles, {pages_to_scrape} pages")
        print()
        
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(
                headless=False,
                slow_mo=500,
                args=['--no-blink-features=AutomationControlled']
            )
            
            context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            self.page = await context.new_page()
            
            try:
                # Login
                await self.login_linkedin()
                
                # Apply search filters
                await self.apply_search_filters(job_titles, locations)
                
                # Scrape results
                profiles = await self.scrape_people_search_results(max_profiles, pages_to_scrape)
                
                if profiles:
                    # Save data
                    await self.save_profiles_data("linkedin_executives")
                    
                    print("\\n🎉 SUCCESS! Executive profiles scraped successfully!")
                    print("✨ Data includes:")
                    print("   • Executive names and LinkedIn URLs")
                    print("   • Current roles and companies")
                    print("   • Location information")
                    print("   • Title categorization")
                    print("   • Multiple export formats")
                    
                    return profiles
                else:
                    print("❌ No profiles collected. Try adjusting search terms or location.")
                    return []
                    
            except Exception as e:
                print(f"❌ Error during scraping: {str(e)}")
                return []
            finally:
                if self.browser:
                    await self.browser.close()

# Demo function
async def run_executive_search_demo():
    """Demo function to run the executive search"""
    scraper = LinkedInPeopleSearchScraper()
    
    print("🎯 LINKEDIN EXECUTIVE SEARCH SETUP")
    print("=" * 40)
    
    # Get user preferences
    print("\\nExample job titles: CEO, CTO, Chief Executive Officer, Chief Technology Officer, Founder")
    job_titles_input = input("Enter job titles (comma-separated): ").strip()
    job_titles = [title.strip() for title in job_titles_input.split(',')] if job_titles_input else ['CEO', 'CTO']
    
    print("\\nExample locations: London, United Kingdom, San Francisco, New York")
    locations_input = input("Enter locations (comma-separated): ").strip()
    locations = [loc.strip() for loc in locations_input.split(',')] if locations_input else ['London', 'United Kingdom']
    
    max_profiles = input("How many profiles to collect? (default: 30): ").strip()
    max_profiles = int(max_profiles) if max_profiles.isdigit() else 30
    
    pages = input("How many pages to scrape? (default: 3): ").strip()
    pages = int(pages) if pages.isdigit() else 3
    
    print(f"\\n🚀 Starting executive search...")
    print(f"Titles: {job_titles}")
    print(f"Locations: {locations}")
    print(f"Target: {max_profiles} profiles, {pages} pages")
    
    profiles = await scraper.run_executive_search(job_titles, locations, max_profiles, pages)
    
    if profiles:
        print(f"\\n🎉 Successfully scraped {len(profiles)} executive profiles!")
        print("📁 Check the 'output' folder for your data files")
    else:
        print("\\n😔 No profiles were collected. Try:")
        print("1. Using different search terms")
        print("2. Checking your LinkedIn access manually")
        print("3. Using broader location criteria")

if __name__ == "__main__":
    asyncio.run(run_executive_search_demo())
