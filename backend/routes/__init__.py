"""
Routes package for Amauta Wearable AI Node

This package contains all API route modules for the backend.
"""

from . import nodes, auth, agents, plugins, vault, health, dicom, media, rag

__all__ = ["nodes", "auth", "agents", "plugins", "vault", "health", "dicom", "media", "rag"]
