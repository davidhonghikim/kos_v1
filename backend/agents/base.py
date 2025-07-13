from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all Amauta agents"""

    name: str = "BaseAgent"
    description: str = "Base agent class"
    capabilities: list = []

    def __init__(self):
        self.is_active = True
        self.metadata = {}

    @abstractmethod
    async def execute(self, task_type: str, payload: Dict[str, Any], model: Optional[str] = None) -> Dict[str, Any]:
        """Execute agent task - must be implemented by subclasses"""
        pass

    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities"""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "is_active": self.is_active,
        }

    def set_metadata(self, key: str, value: Any):
        """Set agent metadata"""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get agent metadata"""
        return self.metadata.get(key, default)

    def activate(self):
        """Activate the agent"""
        self.is_active = True
        logger.info(f"Agent {self.name} activated")

    def deactivate(self):
        """Deactivate the agent"""
        self.is_active = False
        logger.info(f"Agent {self.name} deactivated")

    def health_check(self) -> Dict[str, Any]:
        """Health check for the agent"""
        return {
            "name": self.name,
            "status": "healthy" if self.is_active else "inactive",
            "capabilities": len(self.capabilities),
            "metadata_keys": len(self.metadata),
        }
