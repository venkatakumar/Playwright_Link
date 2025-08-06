# Anonymous LinkedIn Scraper 🔓

A professional-grade LinkedIn scraper that works **without login credentials** - just like Apify's enterprise solution!

## 🌟 Features

### ✅ No Login Required
- **Zero account risk** - no LinkedIn credentials needed
- **No 2FA hassles** - completely anonymous
- **No account restrictions** - won't get your account banned

### 🔄 Advanced Anti-Detection
- **Proxy rotation** with automatic failover
- **User agent rotation** with realistic headers
- **Stealth mode** removes webdriver traces
- **Cookie management** for session persistence
- **Random delays** to mimic human behavior

### 🛡️ Enterprise-Level Security
- **IP rotation** to avoid blocks
- **Request throttling** respects rate limits
- **Error recovery** with retry mechanisms
- **Configurable timeouts** and delays

### 📊 Professional Data Extraction
- **Public posts** from LinkedIn feed
- **Author information** and profiles
- **Engagement metrics** (likes, comments, shares)
- **Media URLs** (images, videos)
- **Export to CSV** with clean formatting

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install playwright pandas aiohttp python-dotenv asyncio-throttle
playwright install chromium
```

### 2. Basic Configuration
```bash
# Copy the anonymous configuration
cp .env.anonymous .env

# Edit search keywords
SEARCH_KEYWORDS=python,data science,machine learning
MAX_POSTS=50
HEADLESS=True
STEALTH_MODE=True
```

### 3. Run Anonymous Scraper
```bash
python anonymous_linkedin_scraper.py
```

## 📋 Configuration Options

### Basic Settings
```env
# What to scrape
SEARCH_KEYWORDS=python,AI,startup
MAX_POSTS=100

# Output
OUTPUT_DIR=output
CSV_FILENAME=linkedin_posts_anonymous.csv

# Browser behavior
HEADLESS=True
STEALTH_MODE=True
DELAY_MIN=3
DELAY_MAX=8
```

### Proxy Configuration
```env
# Enable proxy rotation
USE_PROXIES=True
PROXY_LIST=proxy1.com:8080,proxy2.com:8080,proxy3.com:8080

# Proxy authentication (if needed)
PROXY_USERNAME=your_username
PROXY_PASSWORD=your_password
```

### Advanced Anti-Detection
```env
# Stealth features
ROTATE_USER_AGENT=True
COOKIE_FILE=linkedin_cookies.json
MAX_RETRY_ATTEMPTS=3

# Rate limiting
REQUESTS_PER_MINUTE=10
CONCURRENT_REQUESTS=2

# Content filtering
MIN_CONTENT_LENGTH=50
SKIP_PROMOTED_POSTS=True
```

## 🔧 Proxy Setup (Optional but Recommended)

### Get Free Proxies
```bash
# Run proxy manager to find working proxies
python proxy_manager.py
```

### Use Premium Proxies
```env
# Add your premium proxy list
PROXY_LIST=premium1.proxy.com:8080,premium2.proxy.com:8080
PROXY_USERNAME=your_username
PROXY_PASSWORD=your_password
```

## 📖 Examples

### Basic Anonymous Scraping
```python
from anonymous_linkedin_scraper import AnonymousLinkedInScraper
import os

# Configure
os.environ['SEARCH_KEYWORDS'] = 'python programming'
os.environ['MAX_POSTS'] = '20'
os.environ['STEALTH_MODE'] = 'True'

# Scrape
scraper = AnonymousLinkedInScraper()
await scraper.main()

print(f"Scraped {len(scraper.scraped_posts)} posts!")
```

### With Proxy Rotation
```python
# Set up proxies
os.environ['USE_PROXIES'] = 'True'
os.environ['PROXY_LIST'] = 'proxy1:8080,proxy2:8080'

# Scrape with proxies
scraper = AnonymousLinkedInScraper()
await scraper.main()
```

### Interactive Examples
```bash
# Run interactive examples
python examples_anonymous.py
```

## 🆚 Comparison with Apify

| Feature | This Scraper | Apify Actor | Traditional Scrapers |
|---------|-------------|-------------|---------------------|
| **No Login** | ✅ Yes | ✅ Yes | ❌ Requires login |
| **Proxy Rotation** | ✅ Built-in | ✅ Yes | ⚠️ Manual setup |
| **Anti-Detection** | ✅ Advanced | ✅ Professional | ❌ Basic |
| **Cookie Management** | ✅ Automatic | ✅ Yes | ⚠️ Manual |
| **Rate Limiting** | ✅ Configurable | ✅ Yes | ❌ Often missing |
| **Cost** | 🆓 Free | 💰 $30/month | 🆓 Free |
| **Account Risk** | ✅ Zero | ✅ Zero | ❌ High |
| **Stealth Mode** | ✅ Yes | ✅ Yes | ❌ No |

## 📊 Sample Output

```csv
content,author_name,author_title,likes_count,comments_count,image_urls,scraped_at
"Just launched our new Python framework...",John Doe,Senior Developer,125,23,"https://media.licdn.com/image1.jpg",2025-08-06T10:30:00
"Data science trends for 2025...",Jane Smith,Data Scientist,89,15,,2025-08-06T10:35:00
```

## 🛡️ Legal & Ethical Usage

### ✅ What's Allowed
- Scraping **public posts** visible without login
- **Personal research** and analysis
- **Small-scale data collection** with respect
- **Academic purposes** and learning

### ❌ What to Avoid
- Scraping private or login-required content
- Commercial use without LinkedIn permission
- High-frequency requests that strain servers
- Personal data collection without consent

### 📋 Best Practices
1. **Respect rate limits** - don't overwhelm LinkedIn's servers
2. **Use reasonable delays** - 3-8 seconds between requests
3. **Monitor your usage** - check response times and errors
4. **Save cookies** - reduces detection and improves performance
5. **Use proxies for scale** - rotate IPs for larger datasets
6. **Check robots.txt** - follow LinkedIn's crawling guidelines

## 🔍 Troubleshooting

### Common Issues

**"No posts found"**
```bash
# Try different search keywords
SEARCH_KEYWORDS=technology,innovation

# Or scrape trending content
SEARCH_KEYWORDS=
```

**"Timeout errors"**
```bash
# Increase timeouts
BROWSER_TIMEOUT=90000
DELAY_MAX=12
```

**"Proxy errors"**
```bash
# Test your proxies first
python proxy_manager.py

# Or disable proxies temporarily
USE_PROXIES=False
```

**"Detection issues"**
```bash
# Enable maximum stealth
STEALTH_MODE=True
HEADLESS=True
DELAY_MIN=5
DELAY_MAX=15
```

## 📈 Performance Tips

### For Small Scale (< 100 posts)
```env
HEADLESS=False
USE_PROXIES=False
DELAY_MIN=3
DELAY_MAX=6
```

### For Medium Scale (100-1000 posts)
```env
HEADLESS=True
USE_PROXIES=True
DELAY_MIN=4
DELAY_MAX=8
STEALTH_MODE=True
```

### For Large Scale (1000+ posts)
```env
HEADLESS=True
USE_PROXIES=True
DELAY_MIN=6
DELAY_MAX=12
CONCURRENT_REQUESTS=1
```

## 🔄 Updates & Maintenance

LinkedIn occasionally updates their website structure. If scraping stops working:

1. **Check selectors** - run `discover_selectors.py`
2. **Update user agents** - newer browser versions
3. **Test proxies** - refresh your proxy list
4. **Check LinkedIn changes** - they may have updated their layout

## 🤝 Contributing

Contributions welcome! Please:
1. Follow ethical scraping practices
2. Test changes thoroughly
3. Update documentation
4. Respect LinkedIn's Terms of Service

## 📄 License

This project is for educational purposes only. Users are responsible for complying with LinkedIn's Terms of Service and applicable laws.

---

**⚡ Ready to scrape LinkedIn like a pro? No login required!**
