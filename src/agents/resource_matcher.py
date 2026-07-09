import logging

from src.agents.state import PipelineState
from src.vectorstore.search import semantic_search

logger = logging.getLogger(__name__)


def match_resources_node(state: PipelineState) -> PipelineState:
    """
    LangGraph Node: Takes the extracted skills and round types,
    performs a live web search, and returns the best matching
    preparation resources.
    """
    logger.info("Executing Resource Matcher Node...")
    
    # If there was an error in a previous node, pass it through
    if state.get("error"):
        logger.warning("Error found in state, skipping resource matching.")
        return state

    skills = state.get("extracted_skills", [])
    round_types = state.get("round_types", [])
    
    if not skills:
        state["error"] = "No skills extracted to match against."
        return state

    try:
        company = state.get("company", "Unknown")
        matched_results = semantic_search(skills, round_types, top_k=2, company=company)
        
        state["matched_resources"] = matched_results
        logger.info(f"Successfully matched {len(matched_results)} resources.")
        
    except Exception as e:
        logger.error(f"Failed to match resources: {e}")
        state["error"] = f"Resource matching failed: {str(e)}"
        
    return state
