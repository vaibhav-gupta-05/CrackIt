import logging
import uuid
from typing import Dict, List

from ddgs import DDGS

from src.vectorstore.schema import PrepResource, SearchResult

logger = logging.getLogger(__name__)


def semantic_search(skills: List[str], round_types: List[str], top_k: int = 2, company: str = "Unknown") -> List[Dict]:
    """
    Performs a real-time web search using DuckDuckGo to find the best, most relevant
    prep resources for the extracted skills.
    
    Iterates through each skill individually. If a company is specified, attempts
    to find company-specific resources first, then falls back to generic.
    
    Args:
        skills: List of extracted skill keywords (e.g., ["Java", "OOP", "Git"])
        round_types: List of predicted interview round types (unused for now, kept for API compat)
        top_k: Number of resources to fetch per skill
        company: Company name for company-specific resource search
    """
    if not skills:
        return []

    all_results = []
    seen_urls = set()
    
    # Cap at 5 skills to avoid rate limiting
    core_skills = skills[:5]
    has_company = company and company.lower() not in ("unknown", "")
    
    try:
        with DDGS() as ddgs:
            for skill in core_skills:
                found_for_skill = False
                
                # Build query list: company-specific first, then generic fallback
                queries = []
                if has_company:
                    queries.append(f"{company} {skill} interview prep site:youtube.com OR site:geeksforgeeks.org")
                queries.append(f"{skill} interview prep tutorial site:youtube.com OR site:geeksforgeeks.org")
                
                for query_text in queries:
                    if found_for_skill:
                        break
                        
                    logger.debug(f"DDG search: '{query_text}'")
                    ddg_results = list(ddgs.text(query_text, max_results=top_k))
                    
                    for item in ddg_results:
                        url = item.get("href", "")
                        if not url or url in seen_urls:
                            continue
                            
                        seen_urls.add(url)
                        found_for_skill = True
                        
                        # Determine platform
                        platform = "web"
                        if "youtube.com" in url or "youtu.be" in url:
                            platform = "youtube"
                        elif "geeksforgeeks.org" in url:
                            platform = "gfg"
                        elif "leetcode.com" in url:
                            platform = "leetcode"
                        
                        resource = PrepResource(
                            id=f"live_{uuid.uuid4().hex[:8]}",
                            title=item.get("title", "Resource"),
                            description=item.get("body", "No description available."),
                            url=url,
                            platform=platform,
                            topic=skill,
                            round_type="technical",
                            difficulty="all",
                            tags=skill
                        )
                        
                        search_result = SearchResult(resource=resource)
                        all_results.append(search_result.model_dump())
                    
    except Exception as e:
        logger.error(f"Live DDG search failed: {e}")
    
    logger.info(f"Live web search returned {len(all_results)} unique resources.")
    return all_results
