"""OpsOracle Utils Package - Utilities"""

from backend.utils.pdf_generator import PDFGenerator
from backend.utils.embeddings import EmbeddingsUtil
from backend.utils.logging_config import setup_logging

pdf_generator = PDFGenerator()
embeddings_util = EmbeddingsUtil()

__all__ = ["pdf_generator", "embeddings_util", "setup_logging"]
