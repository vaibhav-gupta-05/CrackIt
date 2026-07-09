import hashlib
import re


def normalize_jd(jd_text: str) -> str:
    """
    Normalizes a job description to make caching robust against minor formatting changes.
    - Lowercases text
    - Removes all non-alphanumeric characters (except spaces)
    - Collapses multiple whitespace into single spaces
    """
    if not jd_text:
        return ""
        
    text = jd_text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def hash_jd(jd_text: str) -> str:
    """
    Returns a SHA-256 hash of the normalized job description.
    This serves as the primary key for the caching layer.
    """
    normalized = normalize_jd(jd_text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
