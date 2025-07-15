import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
from contextlib import asynccontextmanager

# Import routers
from backend.routes import auth, agents, plugins, vault, health, dicom, media, rag, nodes
from backend.middleware.auth import AuthMiddleware
from backend.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting KOS v1 Knowledge Library Framework...")
    yield
    # Shutdown
    logger.info("Shutting down KOS v1 Knowledge Library Framework...")


app = FastAPI(
    title="KOS v1 Knowledge Library Framework",
    description="Universal knowledge management and agent orchestration ecosystem with transformer-class resident system",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(agents.router, prefix="/agents", tags=["Agents"])
app.include_router(plugins.router, prefix="/plugins", tags=["Plugins"])
app.include_router(vault.router, prefix="/vault", tags=["Vault"])
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(dicom.router, prefix="/dicom", tags=["DICOM"])
app.include_router(media.router, prefix="/media", tags=["Media"])
app.include_router(rag.router, prefix="/rag", tags=["RAG"])
app.include_router(nodes.router, prefix="/nodes", tags=["Nodes"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "KOS v1 Knowledge Library Framework",
        "version": "1.0.0",
        "status": "operational",
        "features": [
            "Complete 13-class node system",
            "Multi-agent AI support",
            "Medical-grade features",
            "Plugin architecture",
            "Encrypted vault system",
            "Real-time health monitoring",
            "Transformer-class resident system",
            "Spark identity management",
            "Cortex runtime engine",
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "KOS v1 Knowledge Library Framework", "version": "1.0.0", "node_classes": 13}


@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "api": "KOS v1 Knowledge Library Framework API",
        "version": "1.0.0",
        "endpoints": ["/auth", "/agents", "/plugins", "/vault", "/health", "/dicom", "/media", "/rag", "/nodes"],
        "node_system": {
            "total_classes": 13,
            "tiers": ["foundation", "governance", "elder", "core"],
            "foundation_nodes": ["Musa", "Hakim", "Skald", "Oracle"],
            "governance_nodes": ["Junzi", "Yachay", "Sachem"],
            "elder_nodes": ["Archon", "Amauta", "Mzee"],
            "core_nodes": ["Griot", "Ronin", "Tohunga"],
        },
        "transformer_system": {
            "spark_enabled": True,
            "cortex_mode": "full",
            "vault_shards": True,
            "lego_integration": True,
        },
    }


if __name__ == "__main__":
    host = os.getenv("KOS_HOST", "0.0.0.0")
    port = int(os.getenv("KOS_PORT", "8000"))

    logger.info(f"Starting KOS v1 Knowledge Library Framework on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
