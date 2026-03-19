# Contributing Agent Modules

This guide explains how to create and contribute new Agent modules to streamYourClaw.

## Overview

Agents are the core processing units in streamYourClaw. Each agent handles specific types of tasks and communicates via Redis Streams.

## Agent Architecture

```
┌─────────────────────────────────────────┐
│              State Engine                │
└─────────────────────────────────────────┘
                    │
          Redis Streams (messages)
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼───┐      ┌────▼───┐      ┌────▼───┐
│Supervisor│    │OpenClaw│    │YourAgent│
└─────────┘    └────────┘    └─────────┘
```

## Creating a New Agent

### 1. Directory Structure

```
backend/app/agents/your_agent/
├── __init__.py       # Agent class definition
├── prompts.py        # LLM prompts (if using LLM)
└── utils.py          # Helper functions (optional)
```

### 2. Basic Agent Template

```python
# backend/app/agents/your_agent/__init__.py

from typing import List

from ..base import BaseAgent, AgentResponse
from ..models import AgentMessage


class YourAgent(BaseAgent):
    """
    YourAgent - Brief description of what it does.

    Handles: LIST_MESSAGE_TYPES
    Capabilities: capability_1, capability_2
    """

    name = "YourAgent"
    version = "0.1.0"
    description = "Detailed description of your agent's purpose"

    def __init__(self, config: dict = None):
        """Initialize your agent with optional configuration."""
        self.config = config or {}
        # Setup any needed resources

    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this agent provides."""
        return [
            "capability_1",  # e.g., "code_analysis"
            "capability_2",  # e.g., "data_processing"
        ]

    async def process(self, message: AgentMessage) -> AgentResponse:
        """
        Process an incoming message.

        Args:
            message: The message to process

        Returns:
            AgentResponse with the result
        """
        message_type = message.type

        if message_type == "YOUR_MESSAGE_TYPE":
            return await self._handle_your_type(message)
        elif message_type == "ANOTHER_TYPE":
            return await self._handle_another_type(message)
        else:
            return AgentResponse(
                type="ERROR",
                output=f"Unknown message type: {message_type}",
                metadata={"error": True}
            )

    async def _handle_your_type(self, message: AgentMessage) -> AgentResponse:
        """Handle YOUR_MESSAGE_TYPE messages."""
        # Your processing logic here
        content = message.content

        # Process the content...
        result = "Your processing result"

        return AgentResponse(
            type="YOUR_RESPONSE_TYPE",
            output=result,
            metadata={
                "processed": True,
                "source_message": message.id
            }
        )

    async def on_start(self) -> None:
        """Called when agent starts. Initialize resources."""
        # Setup connections, load models, etc.
        pass

    async def on_stop(self) -> None:
        """Called when agent stops. Cleanup resources."""
        # Close connections, save state, etc.
        pass
```

### 3. Register Your Agent

Update `backend/app/agents/__init__.py`:

```python
from .your_agent import YourAgent

def register_default_agents() -> None:
    """Register the default agents."""
    AgentRegistry.register(SupervisorAgent())
    AgentRegistry.register(OpenClawAdapter())
    AgentRegistry.register(YourAgent())  # Add your agent
```

## Message Types

### Incoming Messages

Your agent can receive these message types:

| Type | Description | Content |
|------|-------------|---------|
| `NEW_TASK` | New task to process | `{task_id, title, description}` |
| `EXECUTE` | Execute a subtask | `{task_id, subtask_id, title, description}` |
| `EXECUTION_RESULT` | Result from execution | `{subtask_id, output, success}` |

### Response Types

Your agent can return these response types:

| Type | Description | Fields |
|------|-------------|--------|
| `SUBTASKS` | Task decomposition | `subtasks: List[SubTask]` |
| `EXECUTION_RESULT` | Execution output | `output: str` |
| `REVIEW_PASSED` | Review success | `output: str` |
| `REVIEW_FAILED` | Review failure | `feedback: str` |
| `ERROR` | Error occurred | `output: str` |

## Using LLM in Your Agent

```python
from openai import AsyncOpenAI

class LLMAgent(BaseAgent):
    def __init__(self, api_key: str = None):
        self.client = AsyncOpenAI(api_key=api_key)

    async def _process_with_llm(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
```

## Testing Your Agent

Create tests in `backend/tests/test_your_agent.py`:

```python
import pytest
from app.agents.your_agent import YourAgent
from app.models import AgentMessage


@pytest.fixture
def agent():
    return YourAgent()


@pytest.mark.asyncio
async def test_agent_capabilities(agent):
    capabilities = agent.get_capabilities()
    assert "capability_1" in capabilities


@pytest.mark.asyncio
async def test_process_message(agent):
    message = AgentMessage(
        type="YOUR_MESSAGE_TYPE",
        source="test",
        content={"test": "data"}
    )
    response = await agent.process(message)
    assert response.type == "YOUR_RESPONSE_TYPE"
```

## Best Practices

1. **Single Responsibility**: Each agent should handle one type of task well
2. **Error Handling**: Always return meaningful error responses
3. **Async Operations**: Use async for I/O operations
4. **Logging**: Log important events for debugging
5. **Documentation**: Document your agent's purpose and API

## Example: Research Agent

```python
class ResearchAgent(BaseAgent):
    """Agent that performs web research."""

    name = "ResearchAgent"
    description = "Performs web searches and summarizes findings"

    def get_capabilities(self):
        return ["search", "summarize", "cite"]

    async def process(self, message: AgentMessage) -> AgentResponse:
        if message.type == "EXECUTE":
            query = message.content.get("description")
            results = await self._search(query)
            summary = await self._summarize(results)
            return AgentResponse(
                type="EXECUTION_RESULT",
                output=summary,
                metadata={"sources": results["sources"]}
            )
```

## PR Checklist

- [ ] Agent class inherits from `BaseAgent`
- [ ] All abstract methods implemented
- [ ] Agent registered in `__init__.py`
- [ ] Unit tests added
- [ ] Documentation updated
- [ ] Example usage provided