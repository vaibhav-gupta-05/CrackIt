import logging
from typing import List

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from src.agents.jd_parser import get_llm

logger = logging.getLogger(__name__)


class ResourceTags(BaseModel):
    topic: str = Field(description="Primary topic (e.g., 'system_design', 'arrays', 'behavioral', 'react')")
    round_type: str = Field(description="Interview round this helps with ('coding', 'system_design', 'hr', 'technical')")
    difficulty: str = Field(description="Difficulty level ('easy', 'medium', 'hard', 'all')")
    tags: List[str] = Field(description="Up to 5 highly relevant keyword tags")


def tag_resource(title: str, description: str) -> ResourceTags:
    """
    Offline Utility: Uses the LLM to automatically generate rich tags
    and metadata for a given prep resource to optimize vector DB retrieval.
    """
    try:
        llm = get_llm()
        parser = JsonOutputParser(pydantic_object=ResourceTags)
        
        prompt = PromptTemplate(
            template="""Analyze the following preparation resource and categorize it.

Title: {title}
Description: {description}

Categorize the resource strictly into these fields.
{format_instructions}
""",
            input_variables=["title", "description"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        
        chain = prompt | llm | parser
        result_dict = chain.invoke({"title": title, "description": description})
        return ResourceTags(**result_dict)
        
    except Exception as e:
        logger.error(f"Failed to tag resource '{title}': {e}")
        # Fallback
        return ResourceTags(
            topic="general", 
            round_type="technical", 
            difficulty="all", 
            tags=[title.lower().replace(" ", "_")]
        )
