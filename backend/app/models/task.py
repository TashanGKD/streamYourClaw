"""Task models for the state engine."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task execution status."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class SubTask(BaseModel):
    """A subtask within a larger task."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    order: int = 0
    dependencies: List[str] = Field(default_factory=list)
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Task(BaseModel):
    """A task to be executed by the agent system."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    subtasks: List[SubTask] = Field(default_factory=list)
    current_subtask_index: int = 0
    retry_count: int = 0
    max_retries: int = 3
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

    def get_current_subtask(self) -> Optional[SubTask]:
        """Get the current subtask being processed."""
        if 0 <= self.current_subtask_index < len(self.subtasks):
            return self.subtasks[self.current_subtask_index]
        return None

    def advance_subtask(self) -> bool:
        """Move to the next subtask. Returns True if successful."""
        if self.current_subtask_index < len(self.subtasks) - 1:
            self.current_subtask_index += 1
            self.update_timestamp()
            return True
        return False

    def is_complete(self) -> bool:
        """Check if all subtasks are completed."""
        return all(st.status == TaskStatus.COMPLETED for st in self.subtasks)