from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field, HttpUrl


class JobListing(BaseModel):
    """
    Structured representation of a scraped job listing.
    """
    id: str = Field(..., description="Unique identifier (e.g., job ID from the URL or site)")
    title: str = Field(..., description="Job title (e.g., 'Senior Python Developer')")
    company: str = Field(..., description="Hiring company name")
    location: str = Field(..., description="Job location or 'Remote'")
    description: str = Field(..., description="Full text of the job description")
    apply_url: str = Field(..., description="URL to apply or view the original posting")
    source: str = Field(..., description="Platform scraped from (e.g., 'indeed', 'custom')")
    scraped_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of scrape")


class ScrapeConfig(BaseModel):
    """
    Configuration for scraping a specific job board or URL.
    This allows the scraper to be completely generic and driven by config rather
    than hardcoding fragile site-specific logic.
    """
    base_url: HttpUrl = Field(..., description="The base URL of the search page")
    query_params: Dict[str, str] = Field(
        default_factory=dict, 
        description="Query parameters to append (e.g., {'q': 'python', 'l': 'remote'})"
    )
    
    # CSS Selectors for the list view
    list_item_selector: str = Field(..., description="CSS selector for the individual job card container")
    list_title_selector: str = Field(..., description="CSS selector inside the card for the job title")
    list_company_selector: str = Field(..., description="CSS selector inside the card for the company name")
    list_location_selector: str = Field(..., description="CSS selector inside the card for the location")
    list_link_selector: str = Field(..., description="CSS selector inside the card for the job link (href)")
    
    # CSS Selectors for the detail view
    detail_description_selector: str = Field(..., description="CSS selector for the full job description text on the detail page")
    
    max_pages: int = Field(default=1, description="Maximum number of pages to scrape")
    pagination_param: Optional[str] = Field(None, description="Query parameter name for pagination (e.g., 'page' or 'start')")
    pagination_multiplier: int = Field(default=1, description="Multiplier for pagination (e.g., 10 for start=0, 10, 20)")
