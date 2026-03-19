# streamYourClaw Design Document

## Project Overview

**streamYourClaw** is an open-source AI Agent live streaming system that enables real-time broadcasting of AI task execution on TikTok. A Supervisor Agent continuously monitors OpenClaw's execution results and orchestrates further tasks - running perpetually without stopping.

### Core Features

- **Perpetual Execution** - Supervisor Agent supervises OpenClaw's continuous task execution
- **Real-time Visualization** - Broadcast Agent thinking process via TikTok live
- **Community Driven** - All modules can be contributed via PR

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    User/Viewer Layer                      │
│          TikTok Live ← OBS ← Frontend Web                 │
└──────────────────────────────────────────────────────────┘
                            ↓ WebSocket/SSE
┌──────────────────────────────────────────────────────────┐
│                    Backend Service Layer                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │  FastAPI Application                              │   │
│  │  ├── API Gateway (REST + WebSocket)              │   │
│  │  ├── State Engine (Core Scheduler)               │   │
│  │  └── Agent Orchestrator                          │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
                            ↓ Redis Streams
┌──────────────────────────────────────────────────────────┐
│                    Agent Worker Layer                     │
│  ┌──────────────┐    ┌──────────────┐                   │
│  │  Supervisor  │ ←→ │   OpenClaw   │                   │
│  │   (Monitor)  │    │  (Executor)  │                   │
│  └──────────────┘    └──────────────┘                   │
└──────────────────────────────────────────────────────────┘
```

### Execution Loop (Perpetual)

```
User Input Task → Supervisor Decomposes → OpenClaw Executes → Supervisor Reviews
                        ↑                                        │
                        └────────── Decide to continue ─────────┘
```

---

## Directory Structure

```
streamYourClaw/
├── README.md                    # English documentation
├── README_CN.md                 # Chinese documentation
├── LICENSE                      # MIT License
├── CONTRIBUTING.md              # Contribution guide
├── pyproject.toml               # Python project config
├── docker-compose.yml           # Docker orchestration
│
├── docs/                        # Documentation
│   ├── architecture.md          # Architecture overview
│   ├── api.md                   # API documentation
│   └── contributing/            # Contribution guides
│       ├── videos.md            # How to contribute status videos
│       ├── agents.md            # How to contribute Agent modules
│       └── themes.md            # How to contribute themes
│
├── frontend/                    # Frontend (migrated from existing)
│   ├── index.html
│   ├── css/
│   │   ├── style.css
│   │   ├── mindmap.css
│   │   └── status.css
│   ├── js/
│   │   ├── app.js
│   │   ├── status.js
│   │   ├── video-status.js
│   │   ├── mindmap.js
│   │   └── thought-logger.js
│   └── assets/
│       ├── videos/              # Status video assets
│       │   ├── meta.json        # Video config (contributable)
│       │   └── *.mp4
│       └── images/
│
├── backend/                     # Backend service
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Configuration management
│   │   ├── api/                 # API routes
│   │   │   ├── __init__.py
│   │   │   ├── routes.py        # REST API
│   │   │   └── websocket.py     # WebSocket handler
│   │   ├── core/                # Core modules
│   │   │   ├── __init__.py
│   │   │   ├── state_engine.py  # State scheduling engine
│   │   │   ├── message_queue.py # Redis wrapper
│   │   │   └── events.py        # Event definitions
│   │   ├── agents/              # Agent modules (pluggable)
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # Agent base class
│   │   │   ├── supervisor.py    # Supervisor Agent
│   │   │   └── openclaw/        # OpenClaw integration (reserved)
│   │   │       ├── __init__.py
│   │   │       └── adapter.py
│   │   └── models/              # Data models
│   │       ├── __init__.py
│   │       ├── task.py
│   │       ├── state.py
│   │       └── message.py
│   ├── tests/
│   └── requirements.txt
│
├── sdk/                         # SDK for contributors
│   └── python/
│       ├── streamyourclaw/
│       │   ├── __init__.py
│       │   ├── agent.py         # Agent development SDK
│       │   ├── video.py         # Video contribution tools
│       │   └── state.py         # State definitions
│       └── examples/
│
└── scripts/                     # Utility scripts
    ├── start.sh
    └── dev.sh
```

---

## Core Module Design

### 3.1 State Engine

The heart of the backend, responsible for orchestrating the entire system.

```python
class StateEngine:
    """State Scheduling Engine - Core of perpetual execution"""

    # State flow
    IDLE → TASK_RECEIVED → DECOMPOSING → EXECUTING → REVIEWING → COMPLETED/RETRY
           ↑                                                                │
           └────────────────── Perpetual Loop ←────────────────────────────┘

    # Core methods
    - submit_task(task: str)           # Receive new task
    - dispatch_to_supervisor(task)     # Dispatch to supervisor
    - handle_agent_result(result)      # Handle agent result
    - update_frontend_state(state)     # Push state to frontend
    - broadcast_log(message)           # Broadcast log
```

### Redis Streams Structure

| Stream | Producer | Consumer | Purpose |
|--------|----------|----------|---------|
| `task:queue` | StateEngine | Supervisor | Task dispatch |
| `result:queue` | OpenClaw | Supervisor | Execution results |
| `review:queue` | Supervisor | StateEngine | Review results |
| `state:broadcast` | StateEngine | Frontend | State updates |
| `log:broadcast` | All | Frontend | Log stream |

---

### 3.2 Agent Module Architecture

```python
# backend/app/agents/base.py
class BaseAgent(ABC):
    """Agent base class - all agents must inherit"""

    @abstractmethod
    async def process(self, message: AgentMessage) -> AgentResponse:
        """Process message, return response"""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Declare agent capabilities"""
        pass


# backend/app/agents/supervisor.py
class SupervisorAgent(BaseAgent):
    """Supervisor Agent - Monitors OpenClaw execution"""

    capabilities = ["decompose", "review", "decide"]

    async def process(self, message):
        if message.type == "NEW_TASK":
            return await self.decompose_task(message)
        elif message.type == "EXECUTION_RESULT":
            return await self.review_result(message)

    async def decompose_task(self, task):
        """Decompose task into subtasks"""
        subtasks = await self.llm.decompose(task.content)
        return AgentResponse(
            type="SUBTASKS",
            subtasks=subtasks,
            next_action="EXECUTE"
        )

    async def review_result(self, result):
        """Review execution result, decide next step"""
        review = await self.llm.review(result)

        if review.success:
            return AgentResponse(
                type="REVIEW_PASSED",
                next_action="NEXT_SUBTASK" or "COMPLETE"
            )
        else:
            return AgentResponse(
                type="REVIEW_FAILED",
                feedback=review.feedback,
                next_action="RETRY"
            )


# backend/app/agents/openclaw/adapter.py
class OpenClawAdapter(BaseAgent):
    """OpenClaw adapter - reserved interface"""

    capabilities = ["code", "search", "browse", "execute"]

    async def process(self, message):
        # TODO: Integrate real OpenClaw
        # Currently returns mock result
        return AgentResponse(
            type="EXECUTION_RESULT",
            output="Mock execution result"
        )
```

---

### 3.3 Frontend Communication Layer

```python
# backend/app/api/websocket.py
@websocket.route("/ws")
async def websocket_handler(websocket):
    """WebSocket connection handler"""

    # Subscribe to Redis broadcasts
    pubsub = redis.pubsub()
    pubsub.subscribe("state:broadcast", "log:broadcast")

    async for message in pubsub.listen():
        if message["type"] == "message":
            await websocket.send_json({
                "channel": message["channel"],
                "data": json.loads(message["data"])
            })
```

**Frontend Message Format:**

```json
{
  "channel": "state:broadcast",
  "data": {
    "type": "STATE_CHANGE",
    "state": "EXECUTING",
    "agent": "OpenClaw",
    "timestamp": "2026-03-19T10:30:00Z"
  }
}

{
  "channel": "log:broadcast",
  "data": {
    "type": "THOUGHT",
    "agent": "Supervisor",
    "message": "Analyzing task requirements...",
    "level": "info"
  }
}
```

---

## Contribution Mechanism

### 4.1 Contribution Types

| Type | Location | Method | Review Criteria |
|------|----------|--------|-----------------|
| Status Videos | `frontend/assets/videos/` | Add mp4 + modify meta.json | Correct format, appropriate content |
| Agent Modules | `backend/app/agents/` | Create Agent dir + inherit BaseAgent | Tests pass, docs complete |
| Theme Styles | `frontend/css/themes/` | Add CSS variable override | Visually appealing, no conflicts |
| Task Templates | `backend/app/prompts/` | Add prompt template file | Valid template, clear description |

### 4.2 Video Contribution Example

Contributors simply:

1. Add video file to `frontend/assets/videos/`
2. Modify `meta.json`:

```json
{
  "states": {
    "thinking": {
      "videos": [
        { "file": "thinking_01.mp4", "weight": 1.0 },
        { "file": "thinking_coffee.mp4", "weight": 0.8 }  // New addition
      ]
    }
  }
}
```

3. Submit PR with title: `[Video] Add thinking_coffee.mp4 for thinking state`

### 4.3 Agent Contribution Example

```python
# backend/app/agents/my_agent/__init__.py
from app.agents.base import BaseAgent, AgentResponse

class MyCustomAgent(BaseAgent):
    """My custom Agent"""

    def get_capabilities(self):
        return ["custom_task"]

    async def process(self, message):
        # Implementation
        return AgentResponse(type="DONE", output="...")
```

Register in `agents/__init__.py`.

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | HTML5 + CSS3 + Vanilla JS | Live display page |
| Backend | Python + FastAPI | API & WebSocket server |
| Message Queue | Redis Streams | Agent communication |
| Agent Runtime | LLM (OpenAI/Claude/etc.) | AI reasoning |
| Deployment | Docker + docker-compose | Container orchestration |

---

## Development Phases

### Phase 1: Project Setup
- [ ] Create project structure
- [ ] Configure Python project (pyproject.toml)
- [ ] Setup Docker environment
- [ ] Migrate existing frontend code

### Phase 2: Backend Core
- [ ] Implement StateEngine
- [ ] Implement Redis Streams wrapper
- [ ] Create WebSocket API
- [ ] Define message models

### Phase 3: Agent System
- [ ] Implement BaseAgent class
- [ ] Implement SupervisorAgent (mock)
- [ ] Create OpenClaw adapter interface
- [ ] Build Agent registration system

### Phase 4: Frontend Integration
- [ ] Replace mock data with WebSocket
- [ ] Implement state synchronization
- [ ] Add error handling & reconnection

### Phase 5: Documentation & Polish
- [ ] Write README (EN + CN)
- [ ] Write CONTRIBUTING.md
- [ ] Create contribution guides for each module
- [ ] Add API documentation

---

## Version

- **Version**: v1.0
- **Created**: 2026-03-19
- **Status**: Design Approved