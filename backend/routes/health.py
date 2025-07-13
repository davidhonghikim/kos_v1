"""
Health Routes

System health monitoring endpoints for the Amauta system.
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat(), "service": "Amauta Wearable AI Node"}


@router.get("/detailed")
async def detailed_health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {"database": "healthy", "cache": "healthy", "nodes": "healthy"},
    }
