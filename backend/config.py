"""OpsOracle Configuration Management - Updated for Claude API"""

import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    """Central configuration for OpsOracle"""
    
    # AWS Configuration
    AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # Claude API (Anthropic) - UPDATED
    CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    LLM_MODEL = "claude-3-5-sonnet-20241022"
    
    # Pinecone (Optional - for production RAG)
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp")
    PINECONE_INDEX = "opsops-incidents"
    
    # FastAPI
    API_HOST = os.getenv("FASTAPI_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("FASTAPI_PORT", 8000))
    
    # Streamlit
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", 8501))
    
    # Database
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "opsops_db")
    
    # Feature Flags
    ENABLE_AUTO_REMEDIATION = os.getenv("ENABLE_AUTO_REMEDIATION", "True").lower() == "true"
    AUTO_REMEDIATION_LEVEL = int(os.getenv("AUTO_REMEDIATION_LEVEL", 1))
    ENABLE_PREDICTION = os.getenv("ENABLE_PREDICTION", "True").lower() == "true"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/opsops.log")
    
    # ML Model paths
    MODEL_PATH = "ml_models/anomaly_detector.pkl"
    SCALER_PATH = "ml_models/scaler.pkl"
    
    # Thresholds
    ANOMALY_THRESHOLD = 0.7
    PREDICTION_CONFIDENCE_THRESHOLD = 0.8
    BLAST_RADIUS_THRESHOLD = 0.5
    
    # RAG Configuration
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    TOP_K_RESULTS = 3
    
    # Remediation Timeouts
    REMEDIATION_TIMEOUT_SECONDS = 60
    LOG_FETCH_TIMEOUT_SECONDS = 30
    
    @staticmethod
    def validate():
        """Validate that all required configs are set"""
        required = [
            "CLAUDE_API_KEY",
            "AWS_ACCESS_KEY",
            "AWS_SECRET_KEY",
        ]
        missing = [key for key in required if not getattr(Config, key, None)]
        if missing:
            raise ValueError(f"Missing required config: {missing}")
        return True

if __name__ == "__main__":
    Config.validate()
    print("✅ Configuration loaded successfully (Claude API enabled)")