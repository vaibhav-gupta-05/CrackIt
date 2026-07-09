"""
Seed Script: Populate ChromaDB with Initial Resources
=====================================================
Reads a CSV of resources, uses the LLM to tag them automatically,
and saves them into the local ChromaDB vector store.
"""

import csv
import logging
import os
import sys
import uuid
from pathlib import Path

# Add project root to Python path so we can import src
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import get_settings
from src.agents.resource_tagger import tag_resource
from src.vectorstore.client import get_vector_client
from src.vectorstore.schema import PrepResource

# Ensure logging is configured
get_settings().configure_logging()
logger = logging.getLogger(__name__)


def generate_stable_id(title: str, url: str) -> str:
    """Creates a stable ID so re-running this script updates instead of duplicates."""
    import hashlib
    raw = f"{title}-{url}".lower().strip()
    return f"res_{hashlib.md5(raw.encode('utf-8')).hexdigest()[:10]}"


def run_seed():
    settings = get_settings()
    csv_path = Path(settings.seed_resources_path)
    
    if not csv_path.exists():
        logger.error(f"Seed file not found at {csv_path}")
        return

    logger.info("Initializing Vector Database Client...")
    client = get_vector_client()
    
    resources_to_upsert = []
    
    logger.info(f"Reading seed file: {csv_path}")
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get("title", "")
            description = row.get("description", "")
            url = row.get("url", "")
            platform = row.get("platform", "unknown")
            
            logger.info(f"Tagging resource via LLM: {title}")
            # Call the LLM to generate rich metadata tags
            tags = tag_resource(title, description)
            
            res_id = generate_stable_id(title, url)
            
            resource = PrepResource(
                id=res_id,
                title=title,
                description=description,
                url=url,
                platform=platform,
                topic=tags.topic,
                round_type=tags.round_type,
                difficulty=tags.difficulty,
                tags=",".join(tags.tags)
            )
            resources_to_upsert.append(resource)
            logger.info(f"  -> Tagged as [{tags.round_type}] Topic: {tags.topic}")

    if resources_to_upsert:
        client.upsert_resources(resources_to_upsert)
        logger.info(f"Successfully seeded {len(resources_to_upsert)} resources into ChromaDB.")
    else:
        logger.warning("No valid resources found to seed.")


if __name__ == "__main__":
    try:
        run_seed()
    except Exception as e:
        logger.critical(f"Seed script failed: {e}", exc_info=True)
