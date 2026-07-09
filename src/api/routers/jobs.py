import logging

import bs4
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.api.schemas import ScrapeRequest, ScrapeResponse
from src.scraper.engine import JobScraper

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/scrape", response_model=ScrapeResponse)
async def run_scraper(request: ScrapeRequest):
    """
    Triggers the Playwright scraper based on the provided configuration.
    """
    logger.info(f"Received scrape request for {request.source_name}")
    try:
        scraper = JobScraper()
        jobs = await scraper.scrape(config=request.config, source_name=request.source_name)
        
        return ScrapeResponse(
            status="success",
            message="Scraping completed successfully.",
            jobs_found=len(jobs),
            jobs=jobs
        )
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class URLRequest(BaseModel):
    url: str


@router.post("/scrape_url")
async def scrape_single_url(req: URLRequest):
    """
    Fetches the text content of a single URL using lightweight httpx (no browser needed).
    Falls back to Playwright only if httpx fails (e.g., JS-rendered pages).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # Fast path: simple HTTP GET (works for Greenhouse, Lever, Workday, etc.)
        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
            resp = await client.get(req.url)
            resp.raise_for_status()
            
            soup = bs4.BeautifulSoup(resp.text, "html.parser")
            
            # Remove script/style tags for cleaner text
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            
            text = soup.get_text(separator="\n", strip=True)
            
            if len(text) > 50:
                return {"text": text}
            
            # If text is too short, the page might be JS-rendered — fall through
            logger.warning(f"httpx returned only {len(text)} chars for {req.url}, trying Playwright fallback.")
    
    except Exception as e:
        logger.warning(f"httpx fetch failed for {req.url}: {e}. Trying Playwright fallback.")
    
    # Slow fallback: Playwright for JS-heavy pages
    try:
        from src.scraper.browser import BrowserManager
        
        async with BrowserManager() as manager:
            html = await manager.fetch_html(req.url)
            soup = bs4.BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            return {"text": text}
    except Exception as e:
        logger.error(f"Both httpx and Playwright failed for {req.url}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
