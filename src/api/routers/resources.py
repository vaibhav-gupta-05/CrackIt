import logging
from typing import List

from fastapi import APIRouter, HTTPException

from src.agents.graph import run_pipeline
from src.api.schemas import MatchRequest, MatchResponse, SearchRequest
from src.cache.hasher import hash_jd
from src.cache.store import CacheStore
from src.vectorstore.search import semantic_search

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resources", tags=["Resources"])
cache = CacheStore()


@router.post("/match", response_model=MatchResponse)
async def match_jd(request: MatchRequest):
    """
    Core pipeline: Takes a raw JD, checks cache. If miss, runs LangGraph
    to extract skills and match resources, then caches the result.
    """
    jd_text = request.jd_text
    if not jd_text or len(jd_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Job description is too short.")
        
    jd_hash = hash_jd(jd_text)
    
    # 1. Check Cache
    cached_state = cache.get(jd_hash)
    if cached_state:
        logger.info(f"Serving request {jd_hash} from cache.")
        cached_state["cache_hit"] = True
        return MatchResponse(**cached_state)
        
    # 2. Cache Miss -> Run LangGraph Pipeline
    logger.info(f"Cache miss for {jd_hash}. Triggering pipeline.")
    try:
        final_state = run_pipeline(jd_text)
        
        if final_state.get("error"):
            # Don't cache errors
            return MatchResponse(**final_state)
            
        # 3. Save to Cache
        cache.put(jd_hash, final_state)
        final_state["cache_hit"] = False
        
        return MatchResponse(**final_state)
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def direct_search(request: SearchRequest):
    """
    Direct semantic search bypassing the LangGraph JD parser.
    """
    try:
        results = semantic_search(request.skills, request.round_types)
        return {"status": "success", "results": results}
    except Exception as e:
        logger.error(f"Direct search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
