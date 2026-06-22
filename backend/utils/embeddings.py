"""Embeddings Utility - Handle embeddings and vectors"""

from sentence_transformers import SentenceTransformer
import numpy as np
from loguru import logger

class EmbeddingsUtil:
    """Embeddings utility for RAG"""
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("✅ Embeddings Util initialized")
    
    def encode(self, text: str) -> np.ndarray:
        """Encode text to embedding"""
        return self.model.encode(text)
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity"""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-10)