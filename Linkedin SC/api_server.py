from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
import os
from linkedin_feed_scraper import LinkedInFeedScraper
from linkedin_scraper import LinkedInScraper

app = FastAPI(title="LinkedIn Scraper Control API")

class RunRequest(BaseModel):
    mode: str = "feed"  # feed | keywords
    max_posts: int = 25
    scroll_attempts: int = 8
    keywords: str | None = None
    dry_run: bool = True

@app.post("/run")
async def run_scrape(req: RunRequest):
    if req.mode == "feed":
        scraper = LinkedInFeedScraper()
        res = await scraper.run_feed_scraper(max_posts=req.max_posts, scroll_attempts=req.scroll_attempts)
        return {"status": "ok", "count": len(res)}
    elif req.mode == "keywords":
        # Configure keywords via env for existing scraper usage
        if req.keywords:
            os.environ['SEARCH_KEYWORDS'] = req.keywords
        scraper = LinkedInScraper()
        # Dry-run means do not save or send messages; here it just runs parse without side effects
        if req.dry_run:
            os.environ['ACTIONS_DRY_RUN'] = 'true'
        await scraper.main()
        return {"status": "ok"}
    else:
        return {"status": "error", "message": "unknown mode"}
