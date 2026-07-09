import logging

from langgraph.graph import END, StateGraph

from src.agents.jd_parser import parse_jd_node
from src.agents.resource_matcher import match_resources_node
from src.agents.state import PipelineState

logger = logging.getLogger(__name__)


def build_graph() -> StateGraph:
    """
    Constructs the LangGraph state machine for processing a Job Description.
    
    Flow:
    START -> parse_jd -> match_resources -> END
    """
    builder = StateGraph(PipelineState)
    
    # Add nodes
    builder.add_node("parse_jd", parse_jd_node)
    builder.add_node("match_resources", match_resources_node)
    
    # Define edges (linear flow for now, can be cyclical if human-in-loop added later)
    builder.set_entry_point("parse_jd")
    builder.add_edge("parse_jd", "match_resources")
    builder.add_edge("match_resources", END)
    
    # Compile the graph
    return builder.compile()


# A global instance of the compiled graph ready for execution
pipeline_graph = build_graph()

def run_pipeline(raw_jd: str) -> dict:
    """
    Convenience function to execute the graph with a raw JD.
    """
    logger.info("Triggering LangGraph pipeline...")
    
    initial_state = PipelineState(
        raw_jd=raw_jd,
        job_title=None,
        company=None,
        extracted_skills=[],
        experience_level=None,
        round_types=[],
        matched_resources=[],
        cache_hit=False,
        error=None
    )
    
    # Execute the graph
    final_state = pipeline_graph.invoke(initial_state)
    return final_state
