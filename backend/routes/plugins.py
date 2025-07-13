"""
Plugins Routes

Plugin management endpoints for the Amauta system.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()


class PluginInfo(BaseModel):
    name: str
    version: str
    description: str
    enabled: bool


@router.get("/", response_model=List[PluginInfo])
async def get_plugins():
    """Get all available plugins"""
    return [PluginInfo(name="medical_viewer", version="1.0.0", description="Medical image viewer plugin", enabled=True)]


@router.post("/install/{plugin_name}")
async def install_plugin(plugin_name: str):
    """Install a plugin"""
    return {"message": f"Plugin {plugin_name} installed successfully"}
