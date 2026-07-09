from urllib.parse import urlencode, urlparse, urlunparse

from src.scraper.models import ScrapeConfig


def build_search_url(config: ScrapeConfig, page: int = 1) -> str:
    """
    Constructs the full target URL by safely encoding query parameters
    and handling pagination logic based on the provided configuration.
    
    Args:
        config: The configuration defining base URL and params.
        page: The current page number (1-indexed).
        
    Returns:
        A fully qualified and URL-encoded string.
    """
    # Create a mutable copy of the params
    params = config.query_params.copy()
    
    # Handle pagination
    if config.pagination_param and page > 1:
        # e.g., if page=2 and multiplier=10, start=10 (for 0-indexed APIs like Indeed)
        # e.g., if page=2 and multiplier=1, page=2
        val = (page - 1) * config.pagination_multiplier
        if config.pagination_multiplier == 1:
            val = page
        params[config.pagination_param] = str(val)
        
    # Safely encode the parameters
    query_string = urlencode(params)
    
    # Parse the base URL (HttpUrl converts to string implicitly, but let's be safe)
    parsed_url = urlparse(str(config.base_url))
    
    # Reconstruct the URL with the new query string
    # Replace the query part entirely
    new_url_parts = list(parsed_url)
    new_url_parts[4] = query_string  # Index 4 is the query component
    
    return urlunparse(new_url_parts)
