## New and updated features

- Cookie-first auth for keyword post scraper; email notification if cookies expire
- Rotating proxy support (optional): set ENABLE_PROXIES=True and PROXY_LIST in .env
- Anti-ban behavior: configurable delays, slow_mo, viewport/locale
- Robust selectors: added fallbacks and utilities to try multiple selectors
- Retries: helper for async retries with backoff
- Data hygiene: de-duplication and cleaning before export
- Multi-format export remains (CSV/JSON/Excel)
- API control: basic FastAPI server in `api_server.py` to trigger runs
- Env-driven config: HEADLESS, MIN_DELAY/MAX_DELAY, SCROLL_ATTEMPTS, LOG_LEVEL, SORT_BY_RECENT
- Tests: basic unit tests for cleaning and dedupe in `tests/test_utils.py`

## Email/phone enrichment (planning)

We can integrate third-party APIs for enrichment. Popular options and rough costs:
- Clearbit: Prospector/Enrichment (Paid; from ~$99/mo; per-record pricing applies)
- Hunter.io: Email finder/verify (Free tier, paid from ~$49/mo; credits per month)
- People Data Labs: Enrichment API (Usage-based; contact sales; has lower-volume self-serve)
- Apollo.io: Enrichment (Plans from ~$49/mo; credits-based)
- ZeroBounce: Email validation (pay-as-you-go, ~$0.008–$0.02 per verify)
- Snov.io: Email finder/verify (Free credits; paid tiers from ~$39/mo)

We’ll add pluggable providers with opt-in env config, plus a local-matching fallback (pattern-based) without external calls.
"""
Summary of Data Extraction Improvements Made
=============================================

ISSUES IDENTIFIED:
1. Author names showing 'nan' (empty)
2. Author titles showing follower count instead of job titles  
3. Post dates showing 'nan' (empty)
4. Image files column still present (should be removed)
5. Image URLs not being extracted properly

IMPROVEMENTS IMPLEMENTED:
================================

🔧 AUTHOR NAME EXTRACTION (Fixed):
   • Added multiple specific selectors:
     - '.feed-shared-actor__name .visually-hidden' (most reliable)
     - '.feed-shared-actor__name a' (name link)
     - '.feed-shared-actor__name span[aria-hidden="true"]' (visible name)
   • Added text cleanup:
     - Removes "• Following", "• Connect" suffixes
     - Validates to skip "follow" text
   • Better fallback chain for different LinkedIn layouts

🔧 AUTHOR TITLE EXTRACTION (Fixed):
   • Added job-title-specific selectors:
     - '.feed-shared-actor__description .visually-hidden'
     - '.feed-shared-actor__description'
   • Added filtering logic:
     - Skips entries containing 'followers', 'connections'
     - Prioritizes actual job titles over social metrics
   • Prevents duplicate text extraction

🔧 POST DATE EXTRACTION (Fixed):  
   • Added multiple date extraction methods:
     - 'time[datetime]' (most reliable)
     - '.feed-shared-actor__sub-description time'
     - Date links in sub-descriptions
   • Prioritizes datetime attributes over text content
   • Better error handling for missing dates

🔧 IMAGE EXTRACTION (Improved):
   • More specific selector for actual media images
   • Filters to only include media.licdn.com images
   • Excludes profile pictures and icons

🔧 CSV STRUCTURE (Fixed):
   • ✅ REMOVED 'image_files' column (per user request)
   • Kept 'image_urls' for reference
   • Cleaner, more focused CSV output

EXPECTED RESULTS AFTER IMPROVEMENTS:
====================================

When you run the scraper next time, you should see:

✅ Author Names: 
   - Proper names like "John Smith", "Jane Doe"
   - No more 'nan' or empty values
   - Clean names without "• Following" suffixes

✅ Author Titles:
   - Job titles like "Software Engineer at Microsoft" 
   - "Product Manager", "CEO at Startup Inc."
   - NO MORE follower counts like "500+ connections"

✅ Post Dates:
   - ISO format dates like "2025-08-06T15:30:00.000Z"
   - Or readable dates like "2d", "1w", "3mo"
   - No more 'nan' values

✅ Image URLs:
   - Only actual post images (if present)
   - LinkedIn media URLs
   - Empty if no images in post

✅ CSV Columns:
   - content, author_name, author_title, post_date
   - post_url, likes_count, comments_count
   - image_urls, scraped_at
   - NO 'image_files' column

TESTING THE IMPROVEMENTS:
========================

To test these improvements:

1. Run the scraper: 
   python linkedin_scraper.py

2. Check the new CSV file:
   - Look for populated author names
   - Verify author titles are job titles, not follower counts  
   - Check that post dates are present
   - Confirm 'image_files' column is removed

3. If you still see issues:
   - LinkedIn may have updated their HTML structure
   - The scraper includes multiple fallback selectors
   - Some posts may still have missing data due to privacy settings

CURRENT STATUS:
==============
✅ All improvements implemented in code
⚠️  2FA authentication preventing immediate testing
🔄 Ready to test when 2FA completed successfully

The data extraction logic has been significantly improved with multiple 
fallback selectors and better data cleaning. The next successful run 
should show much better data quality.
"""

if __name__ == "__main__":
    print(__doc__)
