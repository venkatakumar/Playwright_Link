"""
Example script demonstrating how to use the LinkedIn scraper
with custom configurations and OpenAI integration
"""
import asyncio
import os
from linkedin_scraper import LinkedInScraper, generate_content_ideas
from utils import setup_logging, validate_environment_variables


async def run_custom_scraper():
    """
    Example of running the scraper with custom settings
    """
    # Set up logging
    logger = setup_logging("INFO")
    
    # Validate environment
    missing_vars = validate_environment_variables()
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        return
    
    # Create scraper with custom settings
    scraper = LinkedInScraper()
    
    # Override some settings if needed
    scraper.max_posts = 25  # Limit for testing
    scraper.headless = True  # Run in background
    
    try:
        # Run the scraper
        await scraper.main()
        
        # Optional: Generate content ideas if OpenAI key is available
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and scraper.scraped_posts:
            logger.info("Generating content ideas with OpenAI...")
            ideas = await generate_content_ideas(scraper.scraped_posts, openai_key)
            
            if ideas:
                logger.info("Generated content ideas:")
                for i, idea in enumerate(ideas, 1):
                    logger.info(f"{i}. {idea}")
        
    except Exception as e:
        logger.error(f"Scraper failed: {str(e)}")


async def run_targeted_search():
    """
    Example of searching for specific topics
    """
    # Override search keywords for this run
    os.environ['SEARCH_KEYWORDS'] = 'python programming,software development,tech career'
    os.environ['MAX_POSTS'] = '30'
    
    scraper = LinkedInScraper()
    await scraper.main()


if __name__ == "__main__":
    # Choose which example to run
    print("LinkedIn Scraper Examples")
    print("1. Run custom scraper")
    print("2. Run targeted search")
    
    choice = input("Enter choice (1 or 2): ")
    
    if choice == "1":
        asyncio.run(run_custom_scraper())
    elif choice == "2":
        asyncio.run(run_targeted_search())
    else:
        print("Invalid choice")
