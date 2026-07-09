import logging
from typing import List

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from config import get_settings
from src.agents.state import PipelineState

logger = logging.getLogger(__name__)


class JDExtractionOutput(BaseModel):
    """Structured output schema expected from the LLM."""
    job_title: str = Field(description="The primary job title")
    company: str = Field(description="The hiring company name, if available, else 'Unknown'")
    extracted_skills: List[str] = Field(description="List of technical and soft skills required (must be single keywords, e.g., 'Java', 'Python', 'OOP')")
    experience_level: str = Field(description="One of: Junior, Mid-Level, Senior, Lead, Unknown")
    round_types: List[str] = Field(
        description="Predicted interview rounds needed to prepare for this role. "
                    "Choose from: coding, aptitude, technical, hr, system_design"
    )


def get_llm() -> ChatOpenAI:
    """
    Instantiates the LLM client. 
    Uses the ChatOpenAI client but configured to point to Grok/Groq API.
    """
    settings = get_settings()
    if not settings.has_grok_key:
        raise ValueError("GROK_API_KEY is not set in the environment.")
        
    return ChatOpenAI(
        api_key=settings.grok_api_key,
        base_url=settings.grok_base_url,
        model=settings.grok_model_name,
        temperature=0.1,  # Low temperature for extraction tasks
        max_retries=3,
        model_kwargs={"response_format": {"type": "json_object"}}
    )


def parse_jd_node(state: PipelineState) -> PipelineState:
    """
    LangGraph Node: Parses the raw Job Description text to extract structured insights.
    """
    logger.info("Executing JD Parser Node...")
    raw_jd = state.get("raw_jd", "")
    
    if not raw_jd:
        state["error"] = "No raw Job Description provided."
        return state

    try:
        llm = get_llm()
        parser = JsonOutputParser(pydantic_object=JDExtractionOutput)
        
        prompt = PromptTemplate(
            template="""You are an expert technical recruiter and career coach.
Your task is to analyze the following Job Description (JD) and extract key structured information.

Job Description:
{raw_jd}

Extract the exact job title, company name, required skills (both technical and soft), 
the expected experience level, and predict the types of interview rounds a candidate will face.

CRITICAL: For 'extracted_skills', you MUST extract single, concise keywords only (e.g., "Java", "OOP", "Git"). Do NOT extract full sentences or long phrases.

{format_instructions}
""",
            input_variables=["raw_jd"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        
        chain = prompt | llm | parser
        result_dict = chain.invoke({"raw_jd": raw_jd})
        result = JDExtractionOutput(**result_dict)
        
        # Update state with extracted data
        state["job_title"] = result.job_title
        state["company"] = result.company
        state["extracted_skills"] = result.extracted_skills
        state["experience_level"] = result.experience_level
        state["round_types"] = result.round_types
        
        logger.info(f"Successfully extracted {len(result.extracted_skills)} skills for {result.job_title}.")
        
    except Exception as e:
        logger.error(f"Failed to parse JD: {e}")
        state["error"] = f"JD Parsing failed: {str(e)}"
        
    return state
