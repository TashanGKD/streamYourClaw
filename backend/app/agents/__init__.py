"""Agents module for streamYourClaw."""

from .base import AgentRegistry, BaseAgent
from .openclaw import OpenClawAdapter
from .supervisor import SupervisorAgent

__all__ = [
    "AgentRegistry",
    "BaseAgent",
    "OpenClawAdapter",
    "SupervisorAgent",
]


def register_default_agents() -> None:
    """Register the default agents."""
    AgentRegistry.register(SupervisorAgent())
    AgentRegistry.register(OpenClawAdapter())