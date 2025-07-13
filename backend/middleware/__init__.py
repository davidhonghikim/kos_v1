"""
Middleware package for Amauta Wearable AI Node

This package contains middleware components for the backend.
"""

from .auth import AuthMiddleware

__all__ = ["AuthMiddleware"]
