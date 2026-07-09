from typing import List, Optional, TypedDict


class PipelineState(TypedDict):
    """
    The central state object passed between nodes in the LangGraph orchestration.
    It serves as the single source of truth for a single job processing run.
    """
    
    # --- Input ---
    raw_jd: str
    
    # --- Extracted Data (from JD Parser Node) ---
    job_title: Optional[str]
    company: Optional[str]
    extracted_skills: List[str]
    experience_level: Optional[str]
    round_types: List[str]
    
    # --- Output Data (from Matcher Node) ---
    matched_resources: List[dict]
    
    # --- Metadata / Routing ---
    cache_hit: bool
    error: Optional[str]
