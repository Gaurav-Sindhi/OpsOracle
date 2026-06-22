"""Logging Configuration"""

from loguru import logger
import sys
from backend.config import Config

def setup_logging():
    """Setup logging configuration"""
    logger.remove()  # Remove default handler
    
    # Console handler
    logger.add(
        sys.stderr,
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=Config.LOG_LEVEL
    )
    
    # File handler
    logger.add(
        Config.LOG_FILE,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=Config.LOG_LEVEL,
        rotation="500 MB",
        retention="10 days"
    )
    
    return logger