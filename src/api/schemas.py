from typing import List, Optional

from pydantic import BaseModel, HttpUrl

from src.scraper.models import JobListing, ScrapeConfig


# --- Job Endpoints ---

class ScrapeRequest(BaseModel):
    source_name: str
    config: ScrapeConfig


class ScrapeResponse(BaseModel):
    status: str
    message: str
    jobs_found: int
    jobs: List[JobListing]


# --- Resource Endpoints ---

class MatchRequest(BaseModel):
    jd_text: str


class MatchResponse(BaseModel):
    job_title: Optional[str]
    company: Optional[str]
    extracted_skills: List[str]
    experience_level: Optional[str]
    round_types: List[str]
    matched_resources: List[dict]
    cache_hit: bool
    error: Optional[str]


class SearchRequest(BaseModel):
    skills: List[str]
    round_types: List[str]
