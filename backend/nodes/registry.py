"""
Node Registry - Management of All 13 Node Classes

This module provides a centralized registry for managing all 13 node classes
from the AI-Q system, integrated into the Amauta wearable AI system.
"""

import logging
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
from .base import BaseNode, NodeTier, NodeStatus
from .foundation import MusaNode, HakimNode, SkaldNode, OracleNode
from .governance import JunziNode, YachayNode, SachemNode
from .elder import ArchonNode, AmautaNode, MzeeNode
from .core import GriotNode, RoninNode, TohungaNode

logger = logging.getLogger(__name__)


class NodeRegistry:
    """Central registry for managing all 13 node classes"""

    def __init__(self):
        self.nodes: Dict[str, BaseNode] = {}
        self.node_classes: Dict[str, Type[BaseNode]] = {
            # Foundation Tier: The Knowledge Keepers
            "musa": MusaNode,
            "hakim": HakimNode,
            "skald": SkaldNode,
            "oracle": OracleNode,
            # Governance Tier: The Wisdom Keepers
            "junzi": JunziNode,
            "yachay": YachayNode,
            "sachem": SachemNode,
            # Elder Tier: The Wisdom Guides
            "archon": ArchonNode,
            "amauta": AmautaNode,
            "mzee": MzeeNode,
            # Core Nodes
            "griot": GriotNode,
            "ronin": RoninNode,
            "tohunga": TohungaNode,
        }

        logger.info(f"Node registry initialized with {len(self.node_classes)} node classes")

    def get_available_classes(self) -> List[str]:
        """Get list of available node class names"""
        return list(self.node_classes.keys())

    def get_node_class(self, class_name: str) -> Optional[Type[BaseNode]]:
        """Get node class by name"""
        return self.node_classes.get(class_name.lower())

    def create_node(self, class_name: str, config: Optional[Dict[str, Any]] = None) -> Optional[BaseNode]:
        """Create a new node instance"""
        node_class = self.get_node_class(class_name)
        if not node_class:
            logger.error(f"Unknown node class: {class_name}")
            return None

        try:
            node = node_class(config or {})
            self.nodes[node.node_id] = node
            logger.info(f"Created {class_name} node with ID: {node.node_id}")
            return node
        except Exception as e:
            logger.error(f"Failed to create {class_name} node: {e}")
            return None

    def get_node(self, node_id: str) -> Optional[BaseNode]:
        """Get node by ID"""
        return self.nodes.get(node_id)

    def get_nodes_by_class(self, class_name: str) -> List[BaseNode]:
        """Get all nodes of a specific class"""
        return [node for node in self.nodes.values() if node.name.lower() == class_name.lower()]

    def get_nodes_by_tier(self, tier: NodeTier) -> List[BaseNode]:
        """Get all nodes of a specific tier"""
        return [node for node in self.nodes.values() if node.tier == tier]

    def get_active_nodes(self) -> List[BaseNode]:
        """Get all active nodes"""
        return [node for node in self.nodes.values() if node.status == NodeStatus.ACTIVE]

    async def start_node(self, node_id: str) -> bool:
        """Start a specific node"""
        node = self.get_node(node_id)
        if not node:
            logger.error(f"Node not found: {node_id}")
            return False

        try:
            success = await node.start()
            if success:
                logger.info(f"Started node: {node.name} ({node_id})")
            return success
        except Exception as e:
            logger.error(f"Failed to start node {node_id}: {e}")
            return False

    async def stop_node(self, node_id: str) -> bool:
        """Stop a specific node"""
        node = self.get_node(node_id)
        if not node:
            logger.error(f"Node not found: {node_id}")
            return False

        try:
            success = await node.stop()
            if success:
                logger.info(f"Stopped node: {node.name} ({node_id})")
            return success
        except Exception as e:
            logger.error(f"Failed to stop node {node_id}: {e}")
            return False

    async def start_all_nodes(self) -> Dict[str, bool]:
        """Start all nodes"""
        results = {}
        for node_id, node in self.nodes.items():
            try:
                success = await node.start()
                results[node_id] = success
                if success:
                    logger.info(f"Started {node.name} node")
                else:
                    logger.error(f"Failed to start {node.name} node")
            except Exception as e:
                logger.error(f"Error starting {node.name} node: {e}")
                results[node_id] = False

        return results

    async def stop_all_nodes(self) -> Dict[str, bool]:
        """Stop all nodes"""
        results = {}
        for node_id, node in self.nodes.items():
            try:
                success = await node.stop()
                results[node_id] = success
                if success:
                    logger.info(f"Stopped {node.name} node")
                else:
                    logger.error(f"Failed to stop {node.name} node")
            except Exception as e:
                logger.error(f"Error stopping {node.name} node: {e}")
                results[node_id] = False

        return results

    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Perform health check on all nodes"""
        results = {}
        for node_id, node in self.nodes.items():
            try:
                health = await node.health_check()
                results[node_id] = health
            except Exception as e:
                logger.error(f"Health check failed for {node.name} node: {e}")
                results[node_id] = {"error": str(e)}

        return results

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        total_nodes = len(self.nodes)
        active_nodes = len(self.get_active_nodes())

        tier_counts = {}
        for tier in NodeTier:
            tier_nodes = self.get_nodes_by_tier(tier)
            tier_counts[tier.value] = len(tier_nodes)

        return {
            "total_nodes": total_nodes,
            "active_nodes": active_nodes,
            "inactive_nodes": total_nodes - active_nodes,
            "tier_distribution": tier_counts,
            "node_classes": self.get_available_classes(),
            "last_update": datetime.utcnow().isoformat(),
        }

    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the registry"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            logger.info(f"Removing node: {node.name} ({node_id})")
            del self.nodes[node_id]
            return True
        return False

    def clear_registry(self):
        """Clear all nodes from the registry"""
        logger.info("Clearing node registry")
        self.nodes.clear()

    def get_node_info(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive information about a specific node"""
        node = self.get_node(node_id)
        if not node:
            return None

        return {
            "node_id": node.node_id,
            "name": node.name,
            "tier": node.tier.value,
            "status": node.status.value,
            "capabilities": [cap.dict() for cap in node.capabilities],
            "config": node.config,
            "metadata": node.metadata,
            "created_at": node.created_at.isoformat(),
            "last_heartbeat": node.last_heartbeat.isoformat() if node.last_heartbeat else None,
        }


# Global registry instance
node_registry = NodeRegistry()
