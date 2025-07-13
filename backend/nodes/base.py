"""
Base Node Class for Amauta Wearable AI Node System

This implements the foundational node class that all 13 specialized
node classes inherit from, providing common functionality and interfaces.
"""

import logging
import uuid
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class NodeTier(Enum):
    """Node tiers in the hierarchy"""

    FOUNDATION = "foundation"  # Knowledge Keepers
    GOVERNANCE = "governance"  # Wisdom Keepers
    ELDER = "elder"  # Wisdom Guides
    CORE = "core"  # Core Infrastructure


class NodeStatus(Enum):
    """Node operational status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class NodeCapability(BaseModel):
    """Node capability definition"""

    name: str
    description: str
    version: str
    enabled: bool = True
    config: Dict[str, Any] = {}


class BaseNode(ABC):
    """Base class for all Amauta node types"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.node_id = str(uuid.uuid4())
        self.name = self.__class__.__name__
        self.tier = self._get_tier()
        self.status = NodeStatus.INACTIVE
        self.capabilities: List[NodeCapability] = []
        self.config = config or {}
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.last_heartbeat = None

        # Initialize node-specific capabilities
        self._initialize_capabilities()

        logger.info(f"Initialized {self.name} node (ID: {self.node_id})")

    @abstractmethod
    def _get_tier(self) -> NodeTier:
        """Return the tier this node belongs to"""
        pass

    @abstractmethod
    def _initialize_capabilities(self):
        """Initialize node-specific capabilities"""
        pass

    @abstractmethod
    async def start(self) -> bool:
        """Start the node"""
        pass

    @abstractmethod
    async def stop(self) -> bool:
        """Stop the node"""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        pass

    async def execute_capability(self, capability_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a specific capability"""
        capability = self._get_capability(capability_name)
        if not capability:
            return {"error": f"Capability '{capability_name}' not found"}

        if not capability.enabled:
            return {"error": f"Capability '{capability_name}' is disabled"}

        try:
            method_name = f"execute_{capability_name.lower().replace(' ', '_')}"
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                if callable(method):
                    if asyncio.iscoroutinefunction(method):
                        result = await method(params or {})
                    else:
                        result = method(params or {})
                    return {"success": True, "result": result}
                else:
                    return {"error": f"Method {method_name} is not callable"}
            else:
                return {"error": f"No implementation found for capability '{capability_name}'"}
        except Exception as e:
            logger.error(f"Error executing capability '{capability_name}': {e}")
            return {"error": str(e)}

    def _get_capability(self, name: str) -> Optional[NodeCapability]:
        """Get capability by name"""
        for capability in self.capabilities:
            if capability.name == name:
                return capability
        return None

    def add_capability(self, capability: NodeCapability):
        """Add a capability to the node"""
        self.capabilities.append(capability)
        logger.info(f"Added capability '{capability.name}' to {self.name}")

    def remove_capability(self, name: str) -> bool:
        """Remove a capability from the node"""
        for i, capability in enumerate(self.capabilities):
            if capability.name == name:
                del self.capabilities[i]
                logger.info(f"Removed capability '{name}' from {self.name}")
                return True
        return False

    def enable_capability(self, name: str) -> bool:
        """Enable a capability"""
        capability = self._get_capability(name)
        if capability:
            capability.enabled = True
            logger.info(f"Enabled capability '{name}' on {self.name}")
            return True
        return False

    def disable_capability(self, name: str) -> bool:
        """Disable a capability"""
        capability = self._get_capability(name)
        if capability:
            capability.enabled = False
            logger.info(f"Disabled capability '{name}' on {self.name}")
            return True
        return False

    def get_info(self) -> Dict[str, Any]:
        """Get comprehensive node information"""
        return {
            "node_id": self.node_id,
            "name": self.name,
            "tier": self.tier.value,
            "status": self.status.value,
            "capabilities": [cap.dict() for cap in self.capabilities],
            "config": self.config,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
        }

    def update_metadata(self, key: str, value: Any):
        """Update node metadata"""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get node metadata"""
        return self.metadata.get(key, default)

    async def heartbeat(self):
        """Update heartbeat timestamp"""
        self.last_heartbeat = datetime.utcnow()

    def is_healthy(self) -> bool:
        """Check if node is healthy"""
        return self.status == NodeStatus.ACTIVE

    def get_enabled_capabilities(self) -> List[NodeCapability]:
        """Get list of enabled capabilities"""
        return [cap for cap in self.capabilities if cap.enabled]

    def get_capability_names(self) -> List[str]:
        """Get list of capability names"""
        return [cap.name for cap in self.capabilities]
