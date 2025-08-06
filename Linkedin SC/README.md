# LinkedIn Posts Scraper

A comprehensive Python tool for scraping public LinkedIn posts using Playwright automation.

## ⚠️ Important Disclaimer

**This tool is for educational and research purposes only.** Please respect LinkedIn's Terms of Service and use responsibly:

- Only scrape **public data** that you have permission to access
- Avoid excessive requests that could be considered abuse
- Be mindful of rate limits and use appropriate delays
- Consider using LinkedIn's official API for production applications
- LinkedIn actively detects and blocks automated scraping - use at your own risk

## 🚀 Features

- **Automated LinkedIn Login**: Secure credential management via environment variables
- **Keyword-based Search**: Search posts by multiple keywords with flexible queries
- **Smart Scrolling**: Automatic page scrolling to load more results
- **Comprehensive Data Extraction**:
  - Post content (text)
  - Author name and job title/occupation
  - Post date/time
  - Engagement metrics (likes, comments)
  - Image downloads with local storage
- **CSV Export**: Clean data export using pandas
- **Human-like Behavior**: Random delays and realistic browsing patterns
- **Error Handling**: Robust error handling for captcha and login issues
- **Rate Limiting**: Built-in throttling to respect server resources
- **Modular Design**: Easy to maintain and extend

## 📋 Prerequisites

- Python 3.8 or higher
- Windows/Linux/macOS
- LinkedIn account
- Stable internet connection

## 🛠️ Installation

1. **Clone or download the project**:
   ```bash
   git clone <repository-url>
   cd linkedin-scraper
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

4. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Fill in your LinkedIn credentials and configuration:
   ```env
   LINKEDIN_EMAIL=your_email@example.com
   LINKEDIN_PASSWORD=your_password
   SEARCH_KEYWORDS=artificial intelligence,machine learning,data science
   MAX_POSTS=50
   HEADLESS=False
   ```

## 📊 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LINKEDIN_EMAIL` | Your LinkedIn email | - | ✅ |
| `LINKEDIN_PASSWORD` | Your LinkedIn password | - | ✅ |
| `SEARCH_KEYWORDS` | Comma-separated search keywords | - | ✅ |
| `MAX_POSTS` | Maximum posts to scrape | 50 | ❌ |
| `DELAY_MIN` | Minimum delay between actions (seconds) | 2 | ❌ |
| `DELAY_MAX` | Maximum delay between actions (seconds) | 5 | ❌ |
| `HEADLESS` | Run browser in headless mode | False | ❌ |
| `OUTPUT_DIR` | Output directory for results | output | ❌ |
| `CSV_FILENAME` | Name of the CSV output file | linkedin_posts.csv | ❌ |
| `IMAGES_DIR` | Directory for downloaded images | images | ❌ |

### Optional: OpenAI Integration

For content idea generation, add your OpenAI API key:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 🏃‍♂️ Quick Start

1. **Setup Environment**:
   ```bash
   # Copy environment template
   copy .env.example .env  # Windows
   # cp .env.example .env  # Linux/macOS
   
   # Edit .env file with your LinkedIn credentials
   ```

2. **Run Setup Validation**:
   ```bash
   python setup_validation.py
   ```

3. **Start Scraping**:
   ```bash
   python linkedin_scraper.py
   ```

### VS Code Tasks

Use VS Code's built-in task runner (Ctrl+Shift+P → "Tasks: Run Task"):

- **Run LinkedIn Scraper**: Execute the main scraper
- **Install Dependencies**: Install Python packages  
- **Install Playwright Browsers**: Install browser automation tools
- **Run Example Usage**: Run example scenarios
- **Setup Environment**: Display environment setup instructions

## 🏃‍♂️ Usage

### Basic Usage

```bash
python linkedin_scraper.py
```

### Advanced Usage

The scraper is organized into modular functions:

```python
from linkedin_scraper import LinkedInScraper

# Create scraper instance
scraper = LinkedInScraper()

# Run the complete workflow
await scraper.main()
```

### Individual Functions

```python
# Login to LinkedIn
success = await scraper.login_linkedin(page)

# Search for posts
await scraper.search_posts(page, ["AI", "machine learning"])

# Scroll to load more posts
await scraper.scroll_page(page, max_scrolls=5)

# Parse post data
posts_data = await scraper.parse_posts(page)

# Download images
await scraper.download_images(posts_data)

# Save to CSV
await scraper.save_to_csv(posts_data)
```

## 📁 Output

The scraper creates the following output structure:

```
output/
├── linkedin_posts.csv      # Main data file
├── images/                 # Downloaded images
│   ├── post_0001_img_01_20240101_120000.jpg
│   ├── post_0001_img_02_20240101_120001.jpg
│   └── ...
└── scraper.log            # Execution logs
```

### CSV Columns

| Column | Description |
|--------|-------------|
| `content` | Post text content |
| `author_name` | Post author's name |
| `author_title` | Author's job title/occupation |
| `post_date` | Post publication date (ISO format) |
| `likes_count` | Number of likes/reactions |
| `comments_count` | Number of comments |
| `image_urls` | Original image URLs (semicolon-separated) |
| `image_files` | Local image file paths (semicolon-separated) |
| `scraped_at` | Timestamp when data was scraped |

## ⏰ Scheduling Automated Runs

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily, weekly, etc.)
4. Set action to start program:
   - Program: `python`
   - Arguments: `C:\path\to\linkedin_scraper.py`
   - Start in: `C:\path\to\project`

### Linux/macOS (Cron)

```bash
# Edit crontab
crontab -e

# Add entry for daily run at 9 AM
0 9 * * * cd /path/to/project && python linkedin_scraper.py

# Add entry for weekly run on Mondays at 6 AM
0 6 * * 1 cd /path/to/project && python linkedin_scraper.py
```

## 🔧 Customization

### Updating Selectors

If LinkedIn changes their website layout, update the selectors in `config.py`:

```python
SELECTORS = {
    'post_container': 'div[data-id]',  # Update this selector
    'post_content': '.feed-shared-text',  # Update this selector
    # ... other selectors
}
```

### Adding New Data Fields

1. Update the `parse_posts` function in `linkedin_scraper.py`
2. Add new selectors to `config.py`
3. Update CSV columns in the `save_to_csv` function

### Custom Search Queries

Modify search behavior in the `search_posts` function:

```python
# Current: OR logic
search_query = ' OR '.join([f'"{keyword.strip()}"' for keyword in keywords])

# Custom: AND logic
search_query = ' AND '.join([f'"{keyword.strip()}"' for keyword in keywords])

# Custom: Hashtag search
search_query = ' '.join([f'#{keyword.strip()}' for keyword in keywords])
```

## 🐛 Troubleshooting

### Common Issues

1. **Login Failed**
   - Verify credentials in `.env` file
   - Check for CAPTCHA requirements
   - Ensure account is not locked

2. **No Posts Found**
   - Verify search keywords
   - Check LinkedIn search results manually
   - Update selectors if layout changed

3. **Browser Launch Failed**
   - Install Playwright browsers: `playwright install chromium`
   - Check system requirements
   - Try different browser: change `p.chromium` to `p.firefox`

4. **Image Download Errors**
   - Check internet connection
   - Verify image URLs are accessible
   - Check disk space in output directory

### Debug Mode

Enable debug logging by setting log level:

```python
from utils import setup_logging
logger = setup_logging("DEBUG")
```

### Selector Updates

If scraping fails, LinkedIn may have updated their selectors. Check the browser's developer tools:

1. Right-click on target element
2. Select "Inspect"
3. Copy the new CSS selector
4. Update `config.py` with new selectors

## 📈 Performance Tips

1. **Reduce MAX_POSTS** for faster testing
2. **Increase delays** if getting blocked
3. **Use HEADLESS=True** for better performance
4. **Monitor rate limits** to avoid IP blocks
5. **Run during off-peak hours** for better success rates

## 🔐 Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use strong, unique LinkedIn password**
3. **Consider using LinkedIn app passwords** if available
4. **Monitor account for suspicious activity**
5. **Rotate credentials regularly**

## 📝 Legal and Ethical Considerations

- **Respect robots.txt**: Check LinkedIn's robots.txt file
- **Public data only**: Don't scrape private/restricted content
- **Rate limiting**: Don't overwhelm LinkedIn's servers
- **Terms of Service**: Review and comply with LinkedIn's ToS
- **Data privacy**: Handle scraped data responsibly
- **Attribution**: Give credit when using scraped data

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section
2. Review error logs in `scraper.log`
3. Update selectors if LinkedIn layout changed
4. Consider LinkedIn's official API for production use

## 📄 License

This project is for educational purposes only. Use responsibly and in compliance with LinkedIn's Terms of Service.

---

**Remember: Always respect the platforms you're scraping and use automation responsibly!** 🤖✨
