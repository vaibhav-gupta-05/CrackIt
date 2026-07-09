import hashlib
import logging
from typing import Dict, List, Optional
from urllib.parse import urljoin

from playwright.async_api import ElementHandle, Page

from src.scraper.models import ScrapeConfig

logger = logging.getLogger(__name__)


async def extract_text_safely(element: ElementHandle, selector: str) -> str:
    """Safely extracts text from a child element, returning empty string if not found."""
    try:
        child = await element.query_selector(selector)
        if child:
            text = await child.inner_text()
            return text.strip()
    except Exception as e:
        logger.debug(f"Failed to extract text for selector '{selector}': {e}")
    return ""


async def extract_attribute_safely(element: ElementHandle, selector: str, attribute: str) -> str:
    """Safely extracts an attribute (like href) from a child element."""
    try:
        child = await element.query_selector(selector)
        if child:
            attr = await child.get_attribute(attribute)
            return attr.strip() if attr else ""
    except Exception as e:
        logger.debug(f"Failed to extract attribute '{attribute}' for selector '{selector}': {e}")
    return ""


def generate_job_id(title: str, company: str, location: str) -> str:
    """Generates a stable unique ID based on core job attributes."""
    raw = f"{title}-{company}-{location}".lower().strip()
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]


async def extract_job_cards(page: Page, config: ScrapeConfig, base_url_str: str) -> List[Dict]:
    """
    Finds all job cards on the current page using the configured list item selector,
    and extracts basic metadata (title, company, location, link) from each card.
    Returns a list of dictionaries (not full JobListing models yet, as they lack description).
    """
    logger.debug(f"Extracting job cards using selector '{config.list_item_selector}'")
    
    # Wait for the main container to load
    try:
        await page.wait_for_selector(config.list_item_selector, timeout=5000)
    except Exception:
        logger.warning(f"Timeout waiting for job cards '{config.list_item_selector}'. Page might be empty or blocked.")
        return []

    cards = await page.query_selector_all(config.list_item_selector)
    logger.info(f"Found {len(cards)} job cards on current page.")
    
    jobs_data = []
    for card in cards:
        title = await extract_text_safely(card, config.list_title_selector)
        company = await extract_text_safely(card, config.list_company_selector)
        location = await extract_text_safely(card, config.list_location_selector)
        
        # Link extraction needs special care as it might be relative
        raw_link = await extract_attribute_safely(card, config.list_link_selector, "href")
        full_link = ""
        if raw_link:
            full_link = urljoin(base_url_str, raw_link)
            
        if not title:
            continue # Skip invalid cards
            
        job_id = generate_job_id(title, company, location)
            
        jobs_data.append({
            "id": job_id,
            "title": title,
            "company": company or "Unknown Company",
            "location": location or "Unknown Location",
            "apply_url": full_link,
        })
        
    return jobs_data


async def extract_job_description(page: Page, config: ScrapeConfig) -> str:
    """
    Extracts the full text description from a job detail page.
    """
    logger.debug(f"Extracting description using selector '{config.detail_description_selector}'")
    try:
        await page.wait_for_selector(config.detail_description_selector, timeout=5000)
        element = await page.query_selector(config.detail_description_selector)
        if element:
            text = await element.inner_text()
            return text.strip()
    except Exception as e:
        logger.warning(f"Failed to extract description: {e}")
        
    return "Description could not be extracted."
