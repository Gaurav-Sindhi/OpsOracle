"""
OpsOracle Backend - FastAPI Application Entry Point
Reorganized for professional architecture
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

# Import configuration
from backend.config import Config

# Import routers
from backend.routers import incidents, metrics, remediation, postmortem

# Initialize logger
logger.add(Config.LOG_FILE, rotation="500 MB", retention="10 days")

# Startup event
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic"""
    # Startup
    try:
        Config.validate()
        logger.info("✅ OpsOracle Backend Started Successfully")
    except Exception as e:
        logger.error(f"❌ Configuration Error: {str(e)}")
        sys.exit(1)
    
    yield
    
    # Shutdown
    logger.info("🛑 OpsOracle Backend Shutting Down")

# Create FastAPI app
app = FastAPI(
    title="OpsOracle",
    description="AI-Powered Incident Response System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ HEALTH CHECK ============
@app.get("/")
def health_check():
    """Health check endpoint"""
    from datetime import datetime
    return {
        "status": "ok",
        "service": "OpsOracle",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# ============ INCLUDE ROUTERS ============
app.include_router(incidents.router)
app.include_router(metrics.router)
app.include_router(remediation.router)
app.include_router(postmortem.router)

# ============ STARTUP ============
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=Config.API_HOST,
        port=Config.API_PORT,
        log_level=Config.LOG_LEVEL.lower()
    )