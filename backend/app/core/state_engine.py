"""State Engine - Core orchestrator for the agent system."""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..config import settings
from ..models import (
    AgentMessage,
    AgentState,
    AgentResponse,
    LogBroadcast,
    LogLevel,
    MindmapNode,
    StateBroadcast,
    SubTask,
    SystemState,
    Task,
    TaskStatus,
)
from .events import EventType, StreamName
from .message_queue import MessageQueue, get_message_queue


class StateEngine:
    """
    State Engine - The core orchestrator for streamYourClaw.

    Responsible for:
    - Managing task lifecycle
    - Coordinating between agents
    - Broadcasting state to frontend
    - Maintaining perpetual execution loop
    """

    def __init__(self, queue: Optional[MessageQueue] = None):
        self.queue = queue
        self.state = SystemState.IDLE
        self.current_task: Optional[Task] = None
        self.task_history: List[Task] = []
        self.max_history = 100

        # Stats
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.start_time: Optional[datetime] = None

        # Control
        self._running = False
        self._tasks: List[asyncio.Task] = []

    async def start(self) -> None:
        """Start the state engine."""
        if self._running:
            return

        if self.queue is None:
            self.queue = await get_message_queue()

        self._running = True
        self.start_time = datetime.utcnow()
        self.state = SystemState.IDLE

        # Start background tasks
        self._tasks = [
            asyncio.create_task(self._review_consumer()),
            asyncio.create_task(self._heartbeat()),
        ]

        await self._broadcast_log("System", "State Engine started", LogLevel.SUCCESS)
        await self._broadcast_state(AgentState.IDLE)

    async def stop(self) -> None:
        """Stop the state engine."""
        self._running = False

        # Cancel background tasks
        for task in self._tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        self.state = SystemState.SHUTDOWN
        await self._broadcast_log("System", "State Engine stopped", LogLevel.WARNING)

    async def submit_task(self, task_description: str, title: Optional[str] = None) -> Task:
        """
        Submit a new task to the engine.

        Args:
            task_description: Description of the task to execute
            title: Optional title for the task

        Returns:
            The created Task object
        """
        task = Task(
            title=title or f"Task {len(self.task_history) + 1}",
            description=task_description,
        )

        self.current_task = task
        self.state = SystemState.PROCESSING

        await self._broadcast_log(
            "System",
            f"New task received: {task.title}",
            LogLevel.INFO,
        )
        await self._broadcast_state(AgentState.TASK_RECEIVED)

        # Dispatch to supervisor for decomposition
        await self._dispatch_to_supervisor(task)

        return task

    async def _dispatch_to_supervisor(self, task: Task) -> None:
        """Dispatch task to supervisor agent for decomposition."""
        message = AgentMessage(
            type="NEW_TASK",
            source="StateEngine",
            target="Supervisor",
            content={
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
            },
        )

        await self.queue.publish(
            StreamName.TASK_QUEUE,
            message.model_dump(),
        )

        await self._broadcast_state(AgentState.DECOMPOSING)
        await self._broadcast_log(
            "Supervisor",
            "Analyzing task and decomposing into subtasks...",
            LogLevel.THINKING,
        )

    async def _dispatch_subtask_to_openclaw(self, subtask: SubTask) -> None:
        """Dispatch a subtask to OpenClaw for execution."""
        message = AgentMessage(
            type="EXECUTE",
            source="StateEngine",
            target="OpenClaw",
            content={
                "task_id": self.current_task.id if self.current_task else None,
                "subtask_id": subtask.id,
                "title": subtask.title,
                "description": subtask.description,
            },
        )

        await self.queue.publish(StreamName.TASK_QUEUE, message.model_dump())
        await self._broadcast_state(AgentState.EXECUTING)
        await self._broadcast_log(
            "OpenClaw",
            f"Executing: {subtask.title}",
            LogLevel.INFO,
        )

    async def _review_consumer(self) -> None:
        """Consumer for review results from supervisor."""
        async for message in self.queue.subscribe([StreamName.REVIEW_QUEUE]):
            if not self._running:
                break

            try:
                await self._handle_review_result(message["data"])
            except Exception as e:
                await self._broadcast_log(
                    "System",
                    f"Error processing review: {str(e)}",
                    LogLevel.ERROR,
                )

    async def _handle_review_result(self, data: Dict[str, Any]) -> None:
        """Handle review result from supervisor."""
        if not self.current_task:
            return

        result_type = data.get("type")

        if result_type == "SUBTASKS":
            # Task decomposed, start execution
            subtasks_data = data.get("subtasks", [])
            self.current_task.subtasks = [
                SubTask(**st) if isinstance(st, dict) else st
                for st in subtasks_data
            ]

            await self._update_mindmap()
            await self._broadcast_log(
                "Supervisor",
                f"Task decomposed into {len(self.current_task.subtasks)} subtasks",
                LogLevel.SUCCESS,
            )

            # Start first subtask
            if self.current_task.subtasks:
                first_subtask = self.current_task.subtasks[0]
                first_subtask.status = TaskStatus.IN_PROGRESS
                await self._dispatch_subtask_to_openclaw(first_subtask)

        elif result_type == "REVIEW_PASSED":
            # Subtask completed successfully
            current_subtask = self.current_task.get_current_subtask()
            if current_subtask:
                current_subtask.status = TaskStatus.COMPLETED
                current_subtask.result = data.get("output", "")

            await self._broadcast_log(
                "Supervisor",
                "Review passed!",
                LogLevel.SUCCESS,
            )

            # Check if more subtasks
            if self.current_task.advance_subtask():
                next_subtask = self.current_task.get_current_subtask()
                if next_subtask:
                    next_subtask.status = TaskStatus.IN_PROGRESS
                    await self._dispatch_subtask_to_openclaw(next_subtask)
            else:
                # Task complete
                await self._complete_task()

        elif result_type == "REVIEW_FAILED":
            # Subtask failed, check retry count
            self.current_task.retry_count += 1
            feedback = data.get("feedback", "No feedback provided")

            await self._broadcast_log(
                "Supervisor",
                f"Review failed: {feedback}",
                LogLevel.WARNING,
            )

            if self.current_task.retry_count < self.current_task.max_retries:
                # Retry current subtask
                current_subtask = self.current_task.get_current_subtask()
                if current_subtask:
                    current_subtask.status = TaskStatus.PENDING
                    await self._broadcast_log(
                        "System",
                        f"Retrying... ({self.current_task.retry_count}/{self.current_task.max_retries})",
                        LogLevel.INFO,
                    )
                    await self._dispatch_subtask_to_openclaw(current_subtask)
            else:
                # Max retries exceeded
                await self._fail_task(feedback)

        await self._update_mindmap()

    async def _complete_task(self) -> None:
        """Mark current task as complete and prepare for next."""
        if self.current_task:
            self.current_task.status = TaskStatus.COMPLETED
            self.tasks_completed += 1

            await self._broadcast_log(
                "System",
                f"Task completed: {self.current_task.title}",
                LogLevel.SUCCESS,
            )
            await self._broadcast_state(AgentState.COMPLETED)

            # Archive task
            self.task_history.append(self.current_task)
            if len(self.task_history) > self.max_history:
                self.task_history = self.task_history[-self.max_history :]

        self.current_task = None
        self.state = SystemState.IDLE
        await self._broadcast_state(AgentState.IDLE)

    async def _fail_task(self, error: str) -> None:
        """Mark current task as failed."""
        if self.current_task:
            self.current_task.status = TaskStatus.FAILED
            self.current_task.error = error
            self.tasks_failed += 1

            await self._broadcast_log(
                "System",
                f"Task failed: {error}",
                LogLevel.ERROR,
            )
            await self._broadcast_state(AgentState.ERROR)

            self.task_history.append(self.current_task)

        self.current_task = None
        self.state = SystemState.IDLE

    async def _heartbeat(self) -> None:
        """Periodic heartbeat for health monitoring."""
        while self._running:
            await asyncio.sleep(30)
            if self._running:
                await self.queue.publish(
                    StreamName.STATE_BROADCAST,
                    {
                        "type": "HEARTBEAT",
                        "state": self.state.value,
                        "tasks_completed": self.tasks_completed,
                        "tasks_failed": self.tasks_failed,
                    },
                )

    async def _broadcast_state(self, agent_state: AgentState) -> None:
        """Broadcast state change to frontend."""
        broadcast = StateBroadcast(
            state=agent_state,
            agent="System" if agent_state in [AgentState.IDLE, AgentState.ERROR] else "Supervisor",
            task_id=self.current_task.id if self.current_task else None,
        )
        await self.queue.publish(
            StreamName.STATE_BROADCAST,
            broadcast.model_dump(),
        )

    async def _broadcast_log(
        self,
        agent: str,
        message: str,
        level: LogLevel = LogLevel.INFO,
    ) -> None:
        """Broadcast thought log to frontend."""
        broadcast = LogBroadcast(
            agent=agent,
            message=message,
            level=level,
        )
        await self.queue.publish(
            StreamName.LOG_BROADCAST,
            broadcast.model_dump(),
        )

    async def _update_mindmap(self) -> None:
        """Update mindmap visualization."""
        if not self.current_task:
            return

        # Build mindmap from task
        root = MindmapNode(
            id=self.current_task.id,
            title=self.current_task.title,
            status=self.current_task.status.value.lower(),
            children=[
                MindmapNode(
                    id=st.id,
                    title=st.title,
                    status=st.status.value.lower(),
                )
                for st in self.current_task.subtasks
            ],
        )

        await self.queue.publish(
            StreamName.MINDMAP_BROADCAST,
            root.model_dump(),
        )

    def get_status(self) -> Dict[str, Any]:
        """Get current engine status."""
        uptime = 0.0
        if self.start_time:
            uptime = (datetime.utcnow() - self.start_time).total_seconds()

        return {
            "state": self.state.value,
            "current_task": self.current_task.model_dump() if self.current_task else None,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "uptime": uptime,
            "running": self._running,
        }


# Singleton instance
_engine: Optional[StateEngine] = None


async def get_state_engine() -> StateEngine:
    """Get the singleton state engine instance."""
    global _engine
    if _engine is None:
        _engine = StateEngine()
    return _engine