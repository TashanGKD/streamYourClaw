"""Base Agent class for streamYourClaw."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..models import AgentMessage, AgentResponse


class BaseAgent(ABC):
    """
    Base class for all agents in streamYourClaw.

    All agents must inherit from this class and implement
    the process() method and get_capabilities() method.
    """

    name: str = "BaseAgent"
    version: str = "0.1.0"
    description: str = "Base agent class"

    @abstractmethod
    async def process(self, message: AgentMessage) -> AgentResponse:
        """
        Process an incoming message and return a response.

        Args:
            message: The incoming message to process

        Returns:
            AgentResponse with the result of processing
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Return a list of capabilities this agent provides.

        Returns:
            List of capability strings
        """
        pass

    async def on_start(self) -> None:
        """Called when the agent starts. Override for initialization."""
        pass

    async def on_stop(self) -> None:
        """Called when the agent stops. Override for cleanup."""
        pass

    async def health_check(self) -> Dict[str, Any]:
        """
        Return health status of the agent.

        Returns:
            Dict with health information
        """
        return {
            "name": self.name,
            "version": self.version,
            "status": "healthy",
            "capabilities": self.get_capabilities(),
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name})>"


class AgentRegistry:
    """Registry for all available agents."""

    _agents: Dict[str, BaseAgent] = {}

    @classmethod
    def register(cls, agent: BaseAgent) -> None:
        """Register an agent."""
        cls._agents[agent.name] = agent

    @classmethod
    def unregister(cls, name: str) -> None:
        """Unregister an agent by name."""
        if name in cls._agents:
            del cls._agents[name]

    @classmethod
    def get(cls, name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        return cls._agents.get(name)

    @classmethod
    def get_all(cls) -> Dict[str, BaseAgent]:
        """Get all registered agents."""
        return cls._agents.copy()

    @classmethod
    def list_capabilities(cls) -> Dict[str, List[str]]:
        """List all agents and their capabilities."""
        return {
            name: agent.get_capabilities()
            for name, agent in cls._agents.items()
        }