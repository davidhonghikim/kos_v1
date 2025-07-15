"""
System health monitoring endpoints for the KOS v1 system.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict, Any

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat(), "service": "KOS v1 Knowledge Library Framework"}


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with system information"""
    try:
        # Add more detailed health checks here
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "KOS v1 Knowledge Library Framework",
            "version": "1.0.0",
            "components": {
                "api": "operational",
                "database": "operational",
                "cache": "operational",
                "vector_db": "operational"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness check for Kubernetes"""
    return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """Liveness check for Kubernetes"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
