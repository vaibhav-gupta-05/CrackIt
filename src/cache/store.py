import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Optional

from config import get_settings

logger = logging.getLogger(__name__)


class CacheStore:
    """
    SQLite-backed caching layer.
    Stores LangGraph pipeline results keyed by the hashed JD text.
    Ensures zero-latency responses for previously processed job descriptions.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.db_path = self.settings.cache_db_path
        self._init_db()

    def _init_db(self):
        """Initializes the SQLite schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jd_cache (
                    jd_hash TEXT PRIMARY KEY,
                    pipeline_state JSON NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    hit_count INTEGER DEFAULT 0
                )
            """)
            # Index for TTL cleanup
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON jd_cache(created_at)")
            conn.commit()
            
    def get(self, jd_hash: str, ttl_days: int = 7) -> Optional[Dict]:
        """
        Retrieves a cached pipeline state if it exists and hasn't expired.
        Increments the hit counter on successful retrieval.
        """
        expiry_threshold = datetime.utcnow() - timedelta(days=ttl_days)
        
        with sqlite3.connect(self.db_path) as conn:
            # We want to return rows as dicts for easier parsing
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT pipeline_state, created_at FROM jd_cache WHERE jd_hash = ?",
                (jd_hash,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
                
            # Check TTL
            created_at = datetime.fromisoformat(row["created_at"])
            if created_at < expiry_threshold:
                logger.info(f"Cache miss (expired) for {jd_hash}")
                return None
                
            # Update hit count asynchronously (fire and forget)
            cursor.execute(
                "UPDATE jd_cache SET hit_count = hit_count + 1 WHERE jd_hash = ?",
                (jd_hash,)
            )
            conn.commit()
            
            logger.info(f"Cache hit for {jd_hash}")
            return json.loads(row["pipeline_state"])
            
    def put(self, jd_hash: str, pipeline_state: Dict) -> None:
        """
        Stores the complete pipeline state in the cache.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            state_json = json.dumps(pipeline_state)
            
            cursor.execute("""
                INSERT INTO jd_cache (jd_hash, pipeline_state, created_at, hit_count)
                VALUES (?, ?, ?, 0)
                ON CONFLICT(jd_hash) DO UPDATE SET
                    pipeline_state = excluded.pipeline_state,
                    created_at = excluded.created_at
            """, (jd_hash, state_json, now))
            conn.commit()
            logger.info(f"Cached results for {jd_hash}")
            
    def invalidate_expired(self, ttl_days: int = 7) -> int:
        """
        Deletes entries older than ttl_days. Returns number of deleted rows.
        """
        expiry_threshold = (datetime.utcnow() - timedelta(days=ttl_days)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM jd_cache WHERE created_at < ?", (expiry_threshold,))
            deleted = cursor.rowcount
            conn.commit()
            if deleted > 0:
                logger.info(f"Invalidated {deleted} expired cache entries.")
            return deleted
