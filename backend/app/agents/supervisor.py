"""Supervisor Agent - Monitors and orchestrates OpenClaw execution."""

import json
from typing import Any, Dict, List, Optional

from ..models import AgentMessage, AgentResponse, SubTask, TaskStatus
from .base import BaseAgent


class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent - The monitoring and orchestration agent.

    Responsibilities:
    - Decompose tasks into subtasks
    - Review OpenClaw execution results
    - Decide next actions (continue, retry, fail)
    - Provide feedback for failed executions
    """

    name = "Supervisor"
    version = "0.1.0"
    description = "Supervises OpenClaw execution and orchestrates task flow"

    # Mock LLM responses for demo mode
    MOCK_DECOMPOSITIONS = {
        "default": [
            {"title": "Analyze requirements", "description": "Understand and analyze the task requirements"},
            {"title": "Plan approach", "description": "Create a plan for executing the task"},
            {"title": "Execute plan", "description": "Carry out the planned steps"},
            {"title": "Verify results", "description": "Verify the execution results meet requirements"},
        ],
        "code": [
            {"title": "Understand requirements", "description": "Parse and understand coding requirements"},
            {"title": "Design solution", "description": "Design the code architecture"},
            {"title": "Write code", "description": "Implement the solution"},
            {"title": "Test and debug", "description": "Test the code and fix any issues"},
        ],
        "research": [
            {"title": "Define research scope", "description": "Clarify what needs to be researched"},
            {"title": "Gather information", "description": "Search and collect relevant data"},
            {"title": "Analyze findings", "description": "Analyze and synthesize the information"},
            {"title": "Summarize results", "description": "Create a summary of findings"},
        ],
    }

    def __init__(self, llm_client: Optional[Any] = None, demo_mode: bool = True):
        """
        Initialize Supervisor Agent.

        Args:
            llm_client: Optional LLM client for real AI processing
            demo_mode: If True, use mock responses; if False, use real LLM
        """
        self.llm_client = llm_client
        self.demo_mode = demo_mode

    def get_capabilities(self) -> List[str]:
        """Return supervisor capabilities."""
        return ["decompose", "review", "decide", "feedback"]

    async def process(self, message: AgentMessage) -> AgentResponse:
        """
        Process incoming messages.

        Handles:
        - NEW_TASK: Decompose into subtasks
        - EXECUTION_RESULT: Review and decide next action
        """
        if message.type == "NEW_TASK":
            return await self._handle_new_task(message)
        elif message.type == "EXECUTION_RESULT":
            return await self._handle_execution_result(message)
        else:
            return AgentResponse(
                type="ERROR",
                output=f"Unknown message type: {message.type}",
                metadata={"error": True},
            )

    async def _handle_new_task(self, message: AgentMessage) -> AgentResponse:
        """Handle a new task by decomposing it into subtasks."""
        content = message.content
        task_id = content.get("task_id")
        title = content.get("title", "")
        description = content.get("description", "")

        # Determine task type for decomposition
        task_type = self._detect_task_type(description)

        # Get subtasks
        if self.demo_mode:
            subtasks_data = self.MOCK_DECOMPOSITIONS.get(
                task_type,
                self.MOCK_DECOMPOSITIONS["default"],
            )
        else:
            subtasks_data = await self._llm_decompose(description)

        # Create SubTask objects
        subtasks = []
        for i, st_data in enumerate(subtasks_data):
            subtask = SubTask(
                title=st_data["title"],
                description=st_data.get("description", ""),
                status=TaskStatus.PENDING,
                order=i,
            )
            subtasks.append(subtask.model_dump())

        return AgentResponse(
            type="SUBTASKS",
            subtasks=subtasks,
            metadata={
                "task_id": task_id,
                "task_type": task_type,
                "original_title": title,
            },
        )

    async def _handle_execution_result(self, message: AgentMessage) -> AgentResponse:
        """Review execution result and decide next action."""
        content = message.content
        subtask_id = content.get("subtask_id")
        output = content.get("output", "")
        success = content.get("success", True)

        if self.demo_mode:
            # Mock review - 80% pass rate
            import random
            passed = random.random() < 0.8

            if passed or not success:
                return AgentResponse(
                    type="REVIEW_PASSED",
                    output="Execution completed successfully",
                    metadata={"subtask_id": subtask_id},
                )
            else:
                return AgentResponse(
                    type="REVIEW_FAILED",
                    feedback="The execution did not meet quality standards. Please review and retry.",
                    metadata={"subtask_id": subtask_id},
                )
        else:
            return await self._llm_review(output, subtask_id)

    def _detect_task_type(self, description: str) -> str:
        """Detect the type of task from description."""
        description_lower = description.lower()

        code_keywords = ["code", "function", "script", "program", "implement", "debug", "fix"]
        research_keywords = ["research", "find", "search", "analyze", "investigate", "study"]

        for kw in code_keywords:
            if kw in description_lower:
                return "code"

        for kw in research_keywords:
            if kw in description_lower:
                return "research"

        return "default"

    async def _llm_decompose(self, description: str) -> List[Dict[str, str]]:
        """
        Use LLM to decompose task into subtasks.

        Override this method to integrate with real LLM.
        """
        if self.llm_client is None:
            # Fallback to mock
            return self.MOCK_DECOMPOSITIONS["default"]

        # TODO: Implement real LLM call
        # prompt = f"Decompose this task into subtasks: {description}"
        # response = await self.llm_client.generate(prompt)
        # return self._parse_subtasks(response)

        return self.MOCK_DECOMPOSITIONS["default"]

    async def _llm_review(self, output: str, subtask_id: str) -> AgentResponse:
        """
        Use LLM to review execution result.

        Override this method to integrate with real LLM.
        """
        if self.llm_client is None:
            # Fallback to pass
            return AgentResponse(
                type="REVIEW_PASSED",
                output="Execution reviewed and accepted",
                metadata={"subtask_id": subtask_id},
            )

        # TODO: Implement real LLM review
        return AgentResponse(
            type="REVIEW_PASSED",
            output="Execution reviewed and accepted",
            metadata={"subtask_id": subtask_id},
        )