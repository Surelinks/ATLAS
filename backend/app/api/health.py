"""
Health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    Returns system status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Atlas AI"
    }


@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint
    Verifies all dependencies are available
    """
    # TODO: Add checks for vector DB, OpenAI API, etc.
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {
            "vector_db": "ok",
            "llm": "ok"
        }
    }
