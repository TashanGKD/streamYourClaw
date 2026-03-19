"""State models for the state engine."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class SystemState(str, Enum):
    """Overall system state."""

    IDLE = "IDLE"
    PROCESSING = "PROCESSING"
    WAITING_AGENT = "WAITING_AGENT"
    ERROR = "ERROR"
    SHUTDOWN = "SHUTDOWN"


class AgentInfo(BaseModel):
    """Information about a registered agent."""

    name: str
    capabilities: List[str]
    status: str = "idle"
    last_heartbeat: Optional[datetime] = None
    current_task: Optional[str] = None


class SystemStatus(BaseModel):
    """Full system status for monitoring."""

    state: SystemState = SystemState.IDLE
    current_task_id: Optional[str] = None
    active_agents: List[str] = Field(default_factory=list)
    registered_agents: Dict[str, AgentInfo] = Field(default_factory=dict)
    queue_length: int = 0
    uptime: float = 0.0
    tasks_completed: int = 0
    tasks_failed: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class MindmapNode(BaseModel):
    """A node in the mindmap visualization."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    status: str = "pending"  # pending, processing, completed, failed
    children: List["MindmapNode"] = Field(default_factory=list)

    class Config:
        use_enum_values = True


# Allow self-referencing model
MindmapNode.model_rebuild()


class ThoughtLog(BaseModel):
    """A thought log entry."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent: str
    message: str
    level: str = "info"  # info, thinking, success, warning, error, waiting

    class Config:
        use_enum_values = True