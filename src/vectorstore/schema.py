from typing import List, Optional

from pydantic import BaseModel, Field


class PrepResource(BaseModel):
    """
    Structured representation of a preparation resource
    found via live web search.
    """
    id: str = Field(..., description="Unique identifier (e.g., 'live_a1b2c3d4')")
    title: str = Field(..., description="Display title of the resource")
    description: str = Field(..., description="Short description or snippet from the search result")
    url: str = Field(..., description="Direct link to the resource")
    
    # Metadata
    platform: str = Field(..., description="Source platform (e.g., 'youtube', 'leetcode', 'gfg')")
    topic: str = Field(..., description="Primary topic / skill this resource covers")
    round_type: str = Field(..., description="Interview round (e.g., 'coding', 'hr', 'technical')")
    difficulty: str = Field(..., description="Difficulty level ('easy', 'medium', 'hard', 'all')")
    tags: str = Field(..., description="Comma-separated keyword tags")


class SearchResult(BaseModel):
    """
    Wrapper around a PrepResource returned by the search pipeline.
    """
    resource: PrepResource
