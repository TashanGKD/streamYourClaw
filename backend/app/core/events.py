"""Event definitions for the state engine."""

from enum import Enum


class StreamName(str, Enum):
    """Redis stream names for different message types."""

    # Task streams
    TASK_QUEUE = "task:queue"          # Tasks from engine to supervisor
    RESULT_QUEUE = "result:queue"      # Results from openclaw to supervisor

    # Review stream
    REVIEW_QUEUE = "review:queue"      # Review results from supervisor to engine

    # Broadcast streams (fanout to frontend)
    STATE_BROADCAST = "state:broadcast"  # State changes
    LOG_BROADCAST = "log:broadcast"      # Thought logs
    MINDMAP_BROADCAST = "mindmap:broadcast"  # Mindmap updates


class EventType(str, Enum):
    """Event types for internal dispatching."""

    # Task lifecycle
    TASK_SUBMITTED = "TASK_SUBMITTED"
    TASK_STARTED = "TASK_STARTED"
    TASK_DECOMPOSED = "TASK_DECOMPOSED"
    TASK_SUBTASK_COMPLETE = "TASK_SUBTASK_COMPLETE"
    TASK_COMPLETE = "TASK_COMPLETE"
    TASK_FAILED = "TASK_FAILED"
    TASK_RETRY = "TASK_RETRY"

    # Agent events
    AGENT_STATE_CHANGE = "AGENT_STATE_CHANGE"
    AGENT_THOUGHT = "AGENT_THOUGHT"
    AGENT_ERROR = "AGENT_ERROR"

    # System events
    SYSTEM_START = "SYSTEM_START"
    SYSTEM_SHUTDOWN = "SYSTEM_SHUTDOWN"
    SYSTEM_ERROR = "SYSTEM_ERROR"


# Stream groups for subscription
AGENT_STREAMS = [
    StreamName.TASK_QUEUE,
    StreamName.RESULT_QUEUE,
    StreamName.REVIEW_QUEUE,
]

BROADCAST_STREAMS = [
    StreamName.STATE_BROADCAST,
    StreamName.LOG_BROADCAST,
    StreamName.MINDMAP_BROADCAST,
]