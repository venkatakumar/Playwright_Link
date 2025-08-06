"""
Utility functions for LinkedIn scraper
"""
import re
import os
import asyncio
import random
from typing import List, Dict, Optional, Union
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
