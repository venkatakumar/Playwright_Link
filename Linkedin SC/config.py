"""
Configuration module for LinkedIn Scraper
Contains selector mappings and settings that can be easily updated
when LinkedIn changes their website layout.
"""

# CSS Selectors for LinkedIn elements
# Update these selectors if LinkedIn changes their website layout
SELECTORS = {
    # Login page selectors
    'email_input': 'input[name="session_key"]',
    'password_input': 'input[name="session_password"]',
    'login_button': 'button[type="submit"]',
    'captcha': '.challenge-form',
    
    # Search and navigation
    'search_box': 'input[placeholder*="Search"]',
    'search_button': 'button[type="submit"]',
    'load_more': 'button[aria-label*="Show more results"]',
    
    # Post container and content
    'post_container': 'article, div[data-urn], .feed-shared-update-v2',  # Multiple options for post wrapper
    'post_content': '.feed-shared-text, .feed-shared-inline-show-more-text, .update-components-text',  # Post text content
    'post_content_alt': '.feed-shared-update-v2__commentary, [data-test-id="main-feed-activity-card"]',  # Alternative selector
    
    # Author information
    'author_name': '.feed-shared-actor__name, .update-components-actor__name, [data-test-id="post-author-name"]',
    'author_name_alt': '.feed-shared-actor__name a, .update-components-actor__name a',
    'author_title': '.feed-shared-actor__description, .update-components-actor__description',
    'author_title_alt': '.feed-shared-actor__sub-description, .update-components-actor__sub-description',
    
    # Post metadata
    'post_date': 'time',
    'post_date_alt': '.update-components-actor__sub-description time',
    
    # Engagement metrics
    'likes_count': 'button[aria-label*="reaction"]',
    'likes_count_alt': '.social-counts-reactions__count',
    'comments_count': 'button[aria-label*="comment"]',
    'comments_count_alt': '.social-counts-comments__count',
    'shares_count': 'button[aria-label*="share"]',
    
    # Media content
    'post_images': '.feed-shared-image img, .update-components-image img, img[alt*="post"], img[alt*="shared"]',
    'post_images_alt': '.feed-shared-article__image img, [data-test-id="post-image"] img',
    'post_videos': '.feed-shared-video video, .update-components-video video',
    
    # Navigation and loading
    'feed_container': '.feed-container',
    'infinite_scroll': '.scaffold-finite-scroll__content',
}

# Alternative selectors to try if primary ones fail
SELECTOR_FALLBACKS = {
    'post_container': [
        'div[data-id]',
        '.feed-shared-update-v2',
        '.update-components-post',
        'article'
    ],
    'post_content': [
        '.feed-shared-text',
        '.feed-shared-update-v2__commentary',
        '.update-components-text',
        '.feed-shared-text__text-view'
    ],
    'author_name': [
        '.feed-shared-actor__name',
        '.update-components-actor__name',
        '.feed-shared-actor__name a',
        '.update-components-actor__container a'
    ]
}

# URLs and endpoints
URLS = {
    'login': 'https://www.linkedin.com/login',
    'feed': 'https://www.linkedin.com/feed/',
    'search_content': 'https://www.linkedin.com/search/results/content/',
    'search_people': 'https://www.linkedin.com/search/results/people/',
    'search_companies': 'https://www.linkedin.com/search/results/companies/',
}

# Browser configuration
BROWSER_CONFIG = {
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'viewport': {'width': 1920, 'height': 1080},
    'timeout': 30000,
    'navigation_timeout': 60000,
    'args': [
        '--no-sandbox',
        '--disable-blink-features=AutomationControlled',
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor'
    ]
}

# Rate limiting and delays
TIMING_CONFIG = {
    'min_delay': 2,
    'max_delay': 5,
    'scroll_delay': 3,
    'login_delay': 5,
    'search_delay': 3,
    'rate_limit': 1,  # requests per period
    'rate_period': 2,  # seconds
}

# File and output configuration
OUTPUT_CONFIG = {
    'csv_columns': [
        'content',
        'author_name',
        'author_title',
        'post_date',
        'likes_count',
        'comments_count',
        'shares_count',
        'image_urls',
        'image_files',
        'post_url',
        'scraped_at'
    ],
    'image_formats': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
    'max_image_size_mb': 10,
    'encoding': 'utf-8'
}
