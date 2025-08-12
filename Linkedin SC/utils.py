"""
Utility functions for LinkedIn scraper
"""
import re
import os
import asyncio
import random
from typing import List, Dict, Optional, Union, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
import logging


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def extract_numbers_from_text(text: str) -> int:
    """
    Extract numbers from text (e.g., '15 reactions' -> 15, '1.2K likes' -> 1200)
    
    Args:
        text: Text containing numbers
        
    Returns:
        Extracted number as integer
    """
    if not text:
        return 0
    
    # Handle K (thousands) and M (millions) abbreviations
    text = text.lower().replace(',', '')
    
    if 'k' in text:
        numbers = re.findall(r'(\d+\.?\d*)k', text)
        if numbers:
            return int(float(numbers[0]) * 1000)
    
    if 'm' in text:
        numbers = re.findall(r'(\d+\.?\d*)m', text)
        if numbers:
            return int(float(numbers[0]) * 1000000)
    
    # Extract regular numbers
    numbers = re.findall(r'\d+', text)
    return int(numbers[0]) if numbers else 0


def clean_text(text: str) -> str:
    """
    Clean and normalize text content
    
    Args:
        text: Raw text content
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove common LinkedIn artifacts
    text = re.sub(r'…see more$', '', text)
    text = re.sub(r'Show more$', '', text)
    
    return text.strip()


def parse_linkedin_date(date_str: str) -> Optional[str]:
    """
    Parse LinkedIn date formats and return ISO format
    
    Args:
        date_str: Date string from LinkedIn
        
    Returns:
        ISO formatted date string or None
    """
    if not date_str:
        return None
    
    try:
        # Handle different LinkedIn date formats
        if 'now' in date_str.lower():
            return datetime.now().isoformat()
        
        # Extract time units (minutes, hours, days, weeks)
        time_patterns = {
            r'(\d+)\s*m': 'minutes',
            r'(\d+)\s*h': 'hours', 
            r'(\d+)\s*d': 'days',
            r'(\d+)\s*w': 'weeks'
        }
        
        for pattern, unit in time_patterns.items():
            match = re.search(pattern, date_str.lower())
            if match:
                value = int(match.group(1))
                if unit == 'minutes':
                    date = datetime.now() - timedelta(minutes=value)
                elif unit == 'hours':
                    date = datetime.now() - timedelta(hours=value)
                elif unit == 'days':
                    date = datetime.now() - timedelta(days=value)
                elif unit == 'weeks':
                    date = datetime.now() - timedelta(weeks=value)
                
                return date.isoformat()
        
        # Try to parse ISO format directly
        return datetime.fromisoformat(date_str.replace('Z', '+00:00')).isoformat()
        
    except Exception:
        return None


def is_valid_image_url(url: str) -> bool:
    """
    Check if URL is a valid image URL
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid image URL
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Check for image file extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        return any(url.lower().endswith(ext) for ext in image_extensions)
        
    except Exception:
        return False


def generate_filename(post_index: int, image_index: int, url: str) -> str:
    """
    Generate a unique filename for downloaded images
    
    Args:
        post_index: Index of the post
        image_index: Index of the image in the post
        url: Original image URL
        
    Returns:
        Generated filename
    """
    # Extract file extension from URL
    parsed = urlparse(url)
    path = parsed.path.lower()
    
    extension = '.jpg'  # default
    for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
        if ext in path:
            extension = ext
            break
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"post_{post_index:04d}_img_{image_index:02d}_{timestamp}{extension}"


def create_directories(base_path: str, subdirs: List[str]) -> None:
    """
    Create directory structure
    
    Args:
        base_path: Base directory path
        subdirs: List of subdirectories to create
    """
    from pathlib import Path
    
    base = Path(base_path)
    base.mkdir(exist_ok=True)
    
    for subdir in subdirs:
        (base / subdir).mkdir(exist_ok=True)


async def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
    """
    Add random delay to mimic human behavior
    
    Args:
        min_seconds: Minimum delay in seconds
        max_seconds: Maximum delay in seconds
    """
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)


def validate_environment_variables() -> List[str]:
    """
    Validate that required environment variables are set
    
    Returns:
        List of missing environment variables
    """
    required_vars = [
        'LINKEDIN_EMAIL',
        'LINKEDIN_PASSWORD',
        'SEARCH_KEYWORDS'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return missing_vars


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:95] + ext
    
    return filename


def create_search_url(keywords: List[str], search_type: str = 'content') -> str:
    """
    Create LinkedIn search URL with keywords
    
    Args:
        keywords: List of search keywords
        search_type: Type of search (content, people, companies)
        
    Returns:
        Formatted search URL
    """
    base_urls = {
        'content': 'https://www.linkedin.com/search/results/content/',
        'people': 'https://www.linkedin.com/search/results/people/',
        'companies': 'https://www.linkedin.com/search/results/companies/'
    }
    
    base_url = base_urls.get(search_type, base_urls['content'])
    
    # Format keywords for LinkedIn search
    if len(keywords) == 1:
        query = f'?keywords={keywords[0].strip()}'
    else:
        # Use OR for multiple keywords
        formatted_keywords = ' OR '.join([f'"{kw.strip()}"' for kw in keywords])
        query = f'?keywords={formatted_keywords}'
    
    return base_url + query


def estimate_scraping_time(max_posts: int, delay_avg: float = 3.0) -> str:
    """
    Estimate total scraping time
    
    Args:
        max_posts: Maximum number of posts to scrape
        delay_avg: Average delay between actions
        
    Returns:
        Estimated time string
    """
    # Rough estimation based on actions per post
    actions_per_post = 3  # scroll, parse, delay
    total_seconds = max_posts * actions_per_post * delay_avg
    
    if total_seconds < 60:
        return f"{total_seconds:.0f} seconds"
    elif total_seconds < 3600:
        return f"{total_seconds/60:.1f} minutes"
    else:
        return f"{total_seconds/3600:.1f} hours"


# ==========================================
# ENHANCEMENT FUNCTIONS - HIGH IMPACT FEATURES
# ==========================================

def split_author_name(full_name: str) -> Tuple[str, str]:
    """
    Split author name into firstName and lastName
    
    Args:
        full_name: Full name string (e.g., "John Smith", "Dr. Sarah Johnson")
        
    Returns:
        Tuple of (firstName, lastName)
    """
    import pandas as pd
    
    if not full_name or pd.isna(full_name) or str(full_name).strip() == "":
        return "", ""
    
    # Clean the name (remove extra whitespace and common prefixes)
    cleaned_name = str(full_name).strip()
    
    # Handle special cases
    if cleaned_name.lower() in ['unknown author', 'linkedin user', 'unknown']:
        return cleaned_name, ""
    
    # Remove common prefixes and titles
    prefixes = ['Dr.', 'Prof.', 'Mr.', 'Mrs.', 'Ms.', 'Dr', 'Prof']
    for prefix in prefixes:
        if cleaned_name.startswith(prefix):
            cleaned_name = cleaned_name[len(prefix):].strip()
    
    # Split by space and handle different cases
    name_parts = cleaned_name.split()
    
    if len(name_parts) == 0:
        return "", ""
    elif len(name_parts) == 1:
        # Only one name provided
        return name_parts[0], ""
    elif len(name_parts) == 2:
        # Standard first name + last name
        return name_parts[0], name_parts[1]
    else:
        # Multiple names - first word is firstName, rest is lastName
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:])
        return first_name, last_name


def extract_hashtags(text: str) -> List[str]:
    """
    Extract hashtags from post content
    
    Args:
        text: Post content text
        
    Returns:
        List of hashtags (without the # symbol)
    """
    if not text:
        return []
    
    # Use regex to find hashtags (# followed by word characters)
    hashtag_pattern = r'#(\w+)'
    hashtags = re.findall(hashtag_pattern, text, re.IGNORECASE)
    
    # Remove duplicates while preserving order
    unique_hashtags = []
    seen = set()
    for hashtag in hashtags:
        hashtag_lower = hashtag.lower()
        if hashtag_lower not in seen:
            seen.add(hashtag_lower)
            unique_hashtags.append(hashtag)
    
    return unique_hashtags


def extract_mentions(text: str) -> List[str]:
    """
    Extract @mentions from post content
    
    Args:
        text: Post content text
        
    Returns:
        List of mentions (without the @ symbol)
    """
    if not text:
        return []
    
    # Use regex to find mentions (@ followed by word characters, allowing hyphens and underscores)
    mention_pattern = r'@([\w\-_]+)'
    mentions = re.findall(mention_pattern, text, re.IGNORECASE)
    
    # Remove duplicates while preserving order
    unique_mentions = []
    seen = set()
    for mention in mentions:
        mention_lower = mention.lower()
        if mention_lower not in seen:
            seen.add(mention_lower)
            unique_mentions.append(mention)
    
    return unique_mentions


def format_timestamp_iso(timestamp_str: str) -> str:
    """
    Convert various timestamp formats to ISO format
    
    Args:
        timestamp_str: Raw timestamp string from LinkedIn
        
    Returns:
        ISO formatted timestamp string
    """
    if not timestamp_str:
        return ""
    
    try:
        # If it's already in ISO format, return as-is
        if 'T' in timestamp_str and timestamp_str.endswith('Z'):
            return timestamp_str
        
        # Handle LinkedIn datetime attributes (usually already ISO)
        if 'T' in timestamp_str:
            # Try to parse and re-format to ensure consistency
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return dt.isoformat() + 'Z'
        
        # Handle relative time strings (e.g., "2h", "1d", "3w")
        relative_time = parse_relative_time(timestamp_str)
        if relative_time:
            return relative_time.isoformat() + 'Z'
        
        # Try to parse common date formats
        common_formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%B %d, %Y',
            '%b %d, %Y'
        ]
        
        for fmt in common_formats:
            try:
                dt = datetime.strptime(timestamp_str, fmt)
                return dt.isoformat() + 'Z'
            except ValueError:
                continue
        
        # If all else fails, return the original string
        return timestamp_str
        
    except Exception:
        return timestamp_str


def calculate_relative_time(timestamp_str: str) -> str:
    """
    Calculate relative time from timestamp (e.g., "2 hours ago", "1 day ago")
    
    Args:
        timestamp_str: ISO timestamp string
        
    Returns:
        Human-readable relative time string
    """
    if not timestamp_str:
        return ""
    
    try:
        # Parse the timestamp
        if timestamp_str.endswith('Z'):
            dt = datetime.fromisoformat(timestamp_str[:-1])
        else:
            dt = datetime.fromisoformat(timestamp_str)
        
        # Calculate time difference
        now = datetime.now()
        diff = now - dt
        
        # Calculate relative time
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "just now"
        elif seconds < 3600:  # Less than 1 hour
            minutes = int(seconds // 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:  # Less than 1 day
            hours = int(seconds // 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif seconds < 604800:  # Less than 1 week
            days = int(seconds // 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
        elif seconds < 2629746:  # Less than 1 month (30.44 days)
            weeks = int(seconds // 604800)
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        else:
            months = int(seconds // 2629746)
            return f"{months} month{'s' if months != 1 else ''} ago"
            
    except Exception:
        return ""


def parse_relative_time(relative_str: str) -> Optional[datetime]:
    """
    Parse LinkedIn relative time strings (e.g., "2h", "1d", "3w") to datetime
    
    Args:
        relative_str: Relative time string from LinkedIn
        
    Returns:
        Datetime object or None if parsing fails
    """
    if not relative_str:
        return None
    
    try:
        # Clean the string
        clean_str = relative_str.strip().lower()
        
        # Extract number and unit
        pattern = r'(\d+)\s*([smhdw])'
        match = re.match(pattern, clean_str)
        
        if not match:
            return None
        
        number = int(match.group(1))
        unit = match.group(2)
        
        # Calculate timedelta
        now = datetime.now()
        
        if unit == 's':  # seconds
            return now - timedelta(seconds=number)
        elif unit == 'm':  # minutes
            return now - timedelta(minutes=number)
        elif unit == 'h':  # hours
            return now - timedelta(hours=number)
        elif unit == 'd':  # days
            return now - timedelta(days=number)
        elif unit == 'w':  # weeks
            return now - timedelta(weeks=number)
        
        return None
        
    except Exception:
        return None


def detect_post_type(content: str, image_urls: List[str], post_data: Dict) -> str:
    """
    Detect the type of LinkedIn post based on content and media
    
    Args:
        content: Post text content
        image_urls: List of image URLs in the post
        post_data: Additional post data for analysis
        
    Returns:
        Post type string ('text', 'image', 'video', 'article_share', 'poll')
    """
    # Check for images
    if image_urls and len(image_urls) > 0:
        return 'image_post'
    
    # Check for video indicators in content or URLs
    if content:
        video_indicators = ['video', 'watch', 'youtube', 'vimeo', '▶️', '🎥']
        if any(indicator in content.lower() for indicator in video_indicators):
            return 'video_post'
    
    # Check for article shares (external links)
    if content:
        # Look for URLs in content
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, content)
        if urls:
            return 'article_share'
    
    # Check for poll indicators
    if content:
        poll_indicators = ['poll', 'vote', 'survey', '📊', '🗳️']
        if any(indicator in content.lower() for indicator in poll_indicators):
            return 'poll'
    
    # Default to text post
    return 'text_post'


def enhance_post_data(post_data: Dict) -> Dict:
    """
    Enhance post data with additional computed fields
    
    Args:
        post_data: Original post data dictionary
        
    Returns:
        Enhanced post data dictionary with additional fields
    """
    enhanced_data = post_data.copy()
    
    # 1. Split author name into firstName and lastName
    author_name = post_data.get('author_name', '')
    first_name, last_name = split_author_name(author_name)
    enhanced_data['author_firstName'] = first_name
    enhanced_data['author_lastName'] = last_name
    
    # 2. Extract hashtags from content
    content = post_data.get('content', '')
    hashtags = extract_hashtags(content)
    enhanced_data['hashtags'] = hashtags
    
    # 3. Extract mentions from content
    mentions = extract_mentions(content)
    enhanced_data['mentions'] = mentions
    
    # 4. Format timestamp to ISO and calculate relative time
    post_date = post_data.get('timestamp', '') or post_data.get('post_date', '')
    iso_timestamp = format_timestamp_iso(post_date)
    enhanced_data['postedAtISO'] = iso_timestamp
    enhanced_data['timeSincePosted'] = calculate_relative_time(iso_timestamp)
    
    # 5. Detect post type
    image_urls = post_data.get('image_urls', [])
    post_type = detect_post_type(content, image_urls, post_data)
    enhanced_data['post_type'] = post_type
    
    # 6. Add metadata
    enhanced_data['enhanced_at'] = datetime.now().isoformat() + 'Z'
    enhanced_data['enhancement_version'] = '1.0'
    
    return enhanced_data
