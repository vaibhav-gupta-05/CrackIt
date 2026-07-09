import logging
from typing import List

import chromadb
from chromadb.utils import embedding_functions

from config import get_settings
from src.vectorstore.schema import PrepResource

logger = logging.getLogger(__name__)

COLLECTION_NAME = "prep_resources"


class VectorStoreClient:
    """
    Wrapper around local ChromaDB.
    Handles connection, embedding function configuration, and core CRUD.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStoreClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        settings = get_settings()
        logger.info(f"Initializing ChromaDB client at {settings.chroma_persist_dir}")
        
        # Uses local SQLite engine for ChromaDB
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        
        # 100% Free, local embeddings using sentence-transformers
        # all-MiniLM-L6-v2 is fast, lightweight (~90MB), and excellent for semantic matching
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"} # Cosine similarity is best for text
        )

    def upsert_resources(self, resources: List[PrepResource]) -> None:
        """
        Batch adds or updates resources in the vector database.
        """
        if not resources:
            return

        ids = [r.id for r in resources]
        documents = [r.description for r in resources]
        
        # ChromaDB metadata must be flat dictionaries of strings/ints/floats/bools
        metadatas = [
            {
                "title": r.title,
                "url": r.url,
                "platform": r.platform,
                "topic": r.topic,
                "round_type": r.round_type,
                "difficulty": r.difficulty,
                "tags": r.tags
            }
            for r in resources
        ]

        logger.info(f"Upserting {len(resources)} resources into ChromaDB...")
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        logger.info("Upsert complete.")

    def delete_all(self):
        """Utility for clearing the database during development."""
        try:
            self.client.delete_collection(COLLECTION_NAME)
            self._initialize()
        except Exception:
            pass


def get_vector_client() -> VectorStoreClient:
    """Singleton accessor for the VectorStoreClient."""
    return VectorStoreClient()
