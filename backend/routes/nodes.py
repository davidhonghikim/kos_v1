"""
Node Management API Routes

This module provides REST API endpoints for managing all 13 node classes
in the Amauta Wearable AI Node system.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from backend.nodes.registry import node_registry
from backend.nodes.base import NodeTier, NodeStatus

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for API requests/responses
class NodeCreateRequest(BaseModel):
    class_name: str
    config: Dict[str, Any] = {}


class NodeResponse(BaseModel):
    node_id: str
    name: str
    tier: str
    status: str
    capabilities: List[Dict[str, Any]]
    config: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: str
    last_heartbeat: Optional[str] = None


class SystemStatusResponse(BaseModel):
    total_nodes: int
    active_nodes: int
    inactive_nodes: int
    tier_distribution: Dict[str, int]
    node_classes: List[str]
    last_update: str


@router.get("/classes", response_model=List[str])
async def get_available_classes():
    """Get list of available node classes"""
    return node_registry.get_available_classes()


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get overall system status"""
    return node_registry.get_system_status()


@router.post("/create", response_model=NodeResponse)
async def create_node(request: NodeCreateRequest):
    """Create a new node instance"""
    node = node_registry.create_node(request.class_name, request.config)
    if not node:
        raise HTTPException(status_code=400, detail=f"Failed to create {request.class_name} node")

    return NodeResponse(
        node_id=node.node_id,
        name=node.name,
        tier=node.tier.value,
        status=node.status.value,
        capabilities=[cap.dict() for cap in node.capabilities],
        config=node.config,
        metadata=node.metadata,
        created_at=node.created_at.isoformat(),
        last_heartbeat=node.last_heartbeat.isoformat() if node.last_heartbeat else None,
    )


@router.get("/{node_id}", response_model=NodeResponse)
async def get_node(node_id: str):
    """Get node information by ID"""
    node_info = node_registry.get_node_info(node_id)
    if not node_info:
        raise HTTPException(status_code=404, detail="Node not found")

    return NodeResponse(**node_info)


@router.get("/class/{class_name}", response_model=List[NodeResponse])
async def get_nodes_by_class(class_name: str):
    """Get all nodes of a specific class"""
    nodes = node_registry.get_nodes_by_class(class_name)
    return [
        NodeResponse(
            node_id=node.node_id,
            name=node.name,
            tier=node.tier.value,
            status=node.status.value,
            capabilities=[cap.dict() for cap in node.capabilities],
            config=node.config,
            metadata=node.metadata,
            created_at=node.created_at.isoformat(),
            last_heartbeat=node.last_heartbeat.isoformat() if node.last_heartbeat else None,
        )
        for node in nodes
    ]


@router.get("/tier/{tier}", response_model=List[NodeResponse])
async def get_nodes_by_tier(tier: str):
    """Get all nodes of a specific tier"""
    try:
        node_tier = NodeTier(tier)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {tier}")

    nodes = node_registry.get_nodes_by_tier(node_tier)
    return [
        NodeResponse(
            node_id=node.node_id,
            name=node.name,
            tier=node.tier.value,
            status=node.status.value,
            capabilities=[cap.dict() for cap in node.capabilities],
            config=node.config,
            metadata=node.metadata,
            created_at=node.created_at.isoformat(),
            last_heartbeat=node.last_heartbeat.isoformat() if node.last_heartbeat else None,
        )
        for node in nodes
    ]


@router.post("/{node_id}/start")
async def start_node(node_id: str):
    """Start a specific node"""
    success = await node_registry.start_node(node_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to start node")

    return {"message": "Node started successfully"}


@router.post("/{node_id}/stop")
async def stop_node(node_id: str):
    """Stop a specific node"""
    success = await node_registry.stop_node(node_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to stop node")

    return {"message": "Node stopped successfully"}


@router.post("/start-all")
async def start_all_nodes():
    """Start all nodes"""
    results = await node_registry.start_all_nodes()
    successful = sum(1 for success in results.values() if success)
    total = len(results)

    return {"message": f"Started {successful}/{total} nodes", "results": results}


@router.post("/stop-all")
async def stop_all_nodes():
    """Stop all nodes"""
    results = await node_registry.stop_all_nodes()
    successful = sum(1 for success in results.values() if success)
    total = len(results)

    return {"message": f"Stopped {successful}/{total} nodes", "results": results}


@router.get("/{node_id}/health")
async def get_node_health(node_id: str):
    """Get health status of a specific node"""
    node = node_registry.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    try:
        health = await node.health_check()
        return health
    except Exception as e:
        logger.error(f"Health check failed for node {node_id}: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/health/all")
async def get_all_nodes_health():
    """Get health status of all nodes"""
    health_results = await node_registry.health_check_all()
    return health_results


@router.delete("/{node_id}")
async def remove_node(node_id: str):
    """Remove a node from the registry"""
    success = node_registry.remove_node(node_id)
    if not success:
        raise HTTPException(status_code=404, detail="Node not found")

    return {"message": "Node removed successfully"}


@router.post("/{node_id}/capability/{capability_name}/execute")
async def execute_node_capability(node_id: str, capability_name: str, params: Dict[str, Any] = {}):
    """Execute a specific capability on a node"""
    node = node_registry.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    try:
        result = await node.execute_capability(capability_name, params)
        return result
    except Exception as e:
        logger.error(f"Capability execution failed: {e}")
        raise HTTPException(status_code=500, detail="Capability execution failed")


@router.get("/{node_id}/capabilities")
async def get_node_capabilities(node_id: str):
    """Get capabilities of a specific node"""
    node = node_registry.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    return {
        "node_id": node_id,
        "capabilities": [cap.dict() for cap in node.capabilities],
        "enabled_capabilities": [cap.dict() for cap in node.get_enabled_capabilities()],
    }
