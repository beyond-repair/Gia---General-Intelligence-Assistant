from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from loguru import logger

class BaseAgent(ABC):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.context = {}
        logger.info(f"Initializing {self.__class__.__name__}")

    @abstractmethod
    async def execute(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main task"""
        pass

    async def cleanup(self):
        """Cleanup any resources used by the agent"""
        pass

    def update_context(self, new_context: Dict[str, Any]):
        """Update the agent's context with new information"""
        self.context.update(new_context)

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agent"""
        return {
            "agent_type": self.__class__.__name__,
            "context": self.context
        }