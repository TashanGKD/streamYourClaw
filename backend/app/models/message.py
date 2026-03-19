"""Message models for inter-agent communication."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Message types for agent communication."""

    # Task related
    NEW_TASK = "NEW_TASK"
    SUBTASKS = "SUBTASKS"
    EXECUTE = "EXECUTE"
    EXECUTION_RESULT = "EXECUTION_RESULT"

    # Review related
    REVIEW_PASSED = "REVIEW_PASSED"
    REVIEW_FAILED = "REVIEW_FAILED"

    # State related
    STATE_CHANGE = "STATE_CHANGE"
    THOUGHT = "THOUGHT"

    # Control
    HEARTBEAT = "HEARTBEAT"
    ERROR = "ERROR"


class AgentState(str, Enum):
    """Agent execution states."""

    IDLE = "IDLE"
    TASK_RECEIVED = "TASK_RECEIVED"
    DECOMPOSING = "DECOMPOSING"
    EXECUTING = "EXECUTING"
    REVIEWING = "REVIEWING"
    COMPLETED = "COMPLETED"
    RETRY = "RETRY"
    ERROR = "ERROR"


class LogLevel(str, Enum):
    """Log levels for thought broadcasting."""

    INFO = "info"
    THINKING = "thinking"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    WAITING = "waiting"


class AgentMessage(BaseModel):
    """Base message format for inter-agent communication."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: MessageType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str  # Agent name that sent this message
    target: Optional[str] = None  # Target agent (None for broadcast)
    content: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = None  # For request-response correlation

    class Config:
        use_enum_values = True


class AgentResponse(BaseModel):
    """Response from agent processing."""

    type: MessageType
    output: Optional[str] = None
    subtasks: Optional[List[Dict[str, Any]]] = None
    feedback: Optional[str] = None
    next_action: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class StateBroadcast(BaseModel):
    """State change broadcast to frontend."""

    type: str = "STATE_CHANGE"
    state: AgentState
    agent: str
    task_id: Optional[str] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class LogBroadcast(BaseModel):
    """Log/thought broadcast to frontend."""

    type: str = "THOUGHT"
    agent: str
    message: str
    level: LogLevel = LogLevel.INFO
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True