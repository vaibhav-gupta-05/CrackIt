import asyncio
import logging
from typing import List

from urllib.parse import urlparse

from config import get_settings
from src.scraper.browser import BrowserManager
from src.scraper.extractors import extract_job_cards, extract_job_description
from src.scraper.models import JobListing, ScrapeConfig
from src.scraper.url_builder import build_search_url

logger = logging.getLogger(__name__)


class JobScraper:
    """
    Orchestrates the job scraping workflow.
    Handles pagination, rate limiting, and tying together the browser lifecycle
    with the extraction logic based on the provided generic ScrapeConfig.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    async def scrape(self, config: ScrapeConfig, source_name: str = "custom") -> List[JobListing]:
        """
        Executes the full scraping run for a given configuration.
        
        Workflow:
        1. Iterate through search result pages (pagination).
        2. Extract basic job cards (title, company, URL).
        3. For each job card, navigate to the detail page.
        4. Extract the full job description.
        5. Return a list of validated JobListing objects.
        """
        logger.info(f"Starting scrape run for {source_name} targeting {config.base_url}")
        
        all_jobs: List[JobListing] = []
        base_url_str = str(config.base_url)
        parsed_base = urlparse(base_url_str)
        site_root = f"{parsed_base.scheme}://{parsed_base.netloc}"

        async with BrowserManager() as browser_manager:
            
            # Step 1 & 2: Get all job cards across all pages
            job_cards_data = []
            for page_num in range(1, config.max_pages + 1):
                page_url = build_search_url(config, page_num)
                logger.info(f"Scraping list page {page_num}: {page_url}")
                
                page = await browser_manager.new_page()
                try:
                    await page.goto(page_url, wait_until="networkidle")
                    # Rate limiting delay
                    await asyncio.sleep(self.settings.scraper_delay_ms / 1000.0)
                    
                    cards = await extract_job_cards(page, config, site_root)
                    job_cards_data.extend(cards)
                    
                    if not cards:
                        logger.info(f"No cards found on page {page_num}. Stopping pagination.")
                        break
                        
                except Exception as e:
                    logger.error(f"Error scraping list page {page_url}: {e}")
                finally:
                    await page.close()

            logger.info(f"Extracted {len(job_cards_data)} total job cards. Fetching descriptions...")

            # Step 3 & 4: Fetch detailed descriptions for each job card
            for card in job_cards_data:
                if not card.get("apply_url"):
                    logger.warning(f"Skipping job '{card.get('title')}' - no apply URL found.")
                    continue
                    
                detail_url = card["apply_url"]
                logger.debug(f"Fetching description from {detail_url}")
                
                page = await browser_manager.new_page()
                try:
                    await page.goto(detail_url, wait_until="networkidle")
                    await asyncio.sleep(self.settings.scraper_delay_ms / 1000.0)
                    
                    description = await extract_job_description(page, config)
                    
                    # Step 5: Construct the final model
                    listing = JobListing(
                        id=card["id"],
                        title=card["title"],
                        company=card["company"],
                        location=card["location"],
                        description=description,
                        apply_url=detail_url,
                        source=source_name
                    )
                    all_jobs.append(listing)
                    
                except Exception as e:
                    logger.error(f"Error extracting detail page {detail_url}: {e}")
                finally:
                    await page.close()

        logger.info(f"Scrape complete. Returning {len(all_jobs)} full job listings.")
        return all_jobs
