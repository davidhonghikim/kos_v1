"""
Agents Routes

AI agent management endpoints for the Amauta system.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List

router = APIRouter()


class AgentInfo(BaseModel):
    name: str
    status: str
    capabilities: List[str]


@router.get("/", response_model=List[AgentInfo])
async def get_agents():
    """Get all available agents"""
    return [
        AgentInfo(name="Skald", status="active", capabilities=["content_creation", "storytelling"]),
        AgentInfo(name="Musa", status="active", capabilities=["security", "authentication"]),
    ]


@router.get("/{agent_name}")
async def get_agent(agent_name: str):
    """Get specific agent information"""
    return {"name": agent_name, "status": "active", "capabilities": ["capability1", "capability2"]}
