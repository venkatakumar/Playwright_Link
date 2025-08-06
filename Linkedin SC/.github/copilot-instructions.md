<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# LinkedIn Scraper Project Instructions

This is a Python-based LinkedIn posts scraper using Playwright for browser automation. When working on this project, please follow these guidelines:

## Project Overview
- **Purpose**: Educational tool for scraping public LinkedIn posts using Playwright
- **Language**: Python 3.8+
- **Main Framework**: Playwright for browser automation
- **Data Processing**: Pandas for CSV operations
- **Architecture**: Async/await pattern with modular functions

## Key Technologies
- `playwright.async_api` for browser automation
- `pandas` for data manipulation and CSV export
- `aiohttp` for async HTTP requests (image downloads)
- `python-dotenv` for environment variable management
- `asyncio-throttle` for rate limiting

## Code Style and Patterns
- Use async/await for all I/O operations
- Follow modular design with separate functions for each major task
- Include comprehensive error handling and logging
- Add human-like delays to avoid detection
- Use type hints for better code documentation
- Include detailed docstrings for all functions

## Important Files
- `linkedin_scraper.py`: Main scraper class and orchestration
- `config.py`: Selectors and configuration that may need updates when LinkedIn changes
- `utils.py`: Helper functions for text processing, validation, and file operations
- `.env`: Environment variables (never commit this file)

## Key Functions to Maintain
- `login_linkedin()`: Handle authentication with error handling for CAPTCHA
- `search_posts()`: Navigate to search results with proper URL construction
- `scroll_page()`: Infinite scroll implementation with load detection
- `parse_posts()`: Extract data using CSS selectors (update selectors as needed)
- `download_images()`: Async image downloading with proper error handling
- `save_to_csv()`: Data export using pandas

## Selector Management
- All CSS selectors are in `config.py` for easy maintenance
- Include fallback selectors for common elements
- When LinkedIn updates their UI, update selectors in `config.py`
- Test selectors manually in browser dev tools before updating

## Ethics and Compliance
- Always include warnings about LinkedIn Terms of Service
- Implement rate limiting and human-like delays
- Only scrape public data
- Include error handling for CAPTCHA and account restrictions
- Provide clear documentation about responsible use

## Error Handling Priorities
1. Login failures and CAPTCHA detection
2. Network timeouts and connection issues
3. Changed selectors when LinkedIn updates their UI
4. File I/O errors for downloads and CSV export
5. Rate limiting and IP blocking scenarios

## Performance Considerations
- Use async operations for I/O-bound tasks
- Implement throttling to avoid overwhelming LinkedIn's servers
- Provide configurable delays and batch sizes
- Include progress reporting for long-running operations

## Testing and Debugging
- Include detailed logging at different levels
- Provide debug mode with extra verbose output
- Test selector updates thoroughly
- Include validation for environment variables and configuration

When suggesting improvements or fixes, prioritize:
1. Compliance with LinkedIn's terms of service
2. Robustness against UI changes
3. Performance and efficiency
4. Code maintainability and documentation
5. User safety and ethical considerations
