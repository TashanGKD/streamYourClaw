# Architecture Overview

This document provides a detailed overview of streamYourClaw's architecture.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           User Interface                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │   TikTok Live   │  │      OBS        │  │   Frontend Web      │ │
│  │   (Viewers)     │←─│   (Streaming)   │←─│   (Display)         │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ WebSocket/SSE
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Backend Service                              │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                     FastAPI Application                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │ │
│  │  │ API Routes  │  │  WebSocket  │  │  Static Files        │   │ │
│  │  │ (REST API)  │  │  Handler    │  │  (Frontend Serving)  │   │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘   │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                │                                     │
│                                ▼                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                       Core Layer                               │ │
│  │  ┌─────────────────┐  ┌─────────────────────────────────────┐ │ │
│  │  │  State Engine   │  │     Message Queue (Redis Streams)   │ │ │
│  │  │  (Orchestrator) │  │  ┌───────────┐ ┌──────────────────┐ │ │ │
│  │  └─────────────────┘  │  │  task:*   │ │  result:*        │ │ │ │
│  │                       │  │  review:* │ │  state:broadcast │ │ │ │
│  │                       │  │  log:*    │ │  mindmap:*       │ │ │ │
│  │                       │  └───────────┘ └──────────────────┘ │ │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          Agent Layer                                 │
│  ┌───────────────────────┐       ┌───────────────────────┐          │
│  │    Supervisor Agent   │       │    OpenClaw Adapter   │          │
│  │  ┌─────────────────┐  │       │  ┌─────────────────┐  │          │
│  │  │ Task Decomposer │  │       │  │  Execute Tasks  │  │          │
│  │  │ Result Reviewer │  │       │  │  (Mock/Real)    │  │          │
│  │  │ Decision Maker  │  │       │  └─────────────────┘  │          │
│  │  └─────────────────┘  │       └───────────────────────┘          │
│  └───────────────────────┘                                           │
└─────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. State Engine

The central orchestrator that manages the entire system lifecycle.

**Responsibilities:**
- Task lifecycle management
- State transitions and broadcasting
- Agent coordination
- Error handling and recovery

**State Flow:**

```
IDLE → TASK_RECEIVED → DECOMPOSING → EXECUTING → REVIEWING
  ↑                                                      │
  └──────────────── COMPLETE/RETRY ←────────────────────┘
```

### 2. Message Queue (Redis Streams)

Provides asynchronous communication between components.

**Stream Types:**

| Stream | Direction | Purpose |
|--------|-----------|---------|
| `task:queue` | Engine → Agents | Task dispatch |
| `result:queue` | OpenClaw → Supervisor | Execution results |
| `review:queue` | Supervisor → Engine | Review decisions |
| `state:broadcast` | Engine → Frontend | State changes |
| `log:broadcast` | All → Frontend | Thought logs |
| `mindmap:broadcast` | Engine → Frontend | Mindmap updates |

### 3. Agent System

Pluggable agent architecture for extensibility.

**Agent Interface:**

```python
class BaseAgent(ABC):
    @abstractmethod
    async def process(message: AgentMessage) -> AgentResponse

    @abstractmethod
    def get_capabilities() -> List[str]
```

**Built-in Agents:**

| Agent | Capabilities | Role |
|-------|--------------|------|
| Supervisor | decompose, review, decide | Orchestration |
| OpenClaw | code, search, browse, execute | Task execution |

### 4. Frontend

Real-time visualization layer.

**Components:**
- Mindmap visualization
- Status video player
- Thought log stream
- WebSocket client

## Data Flow

### Task Execution Flow

```
1. User submits task
   │
   ▼
2. State Engine receives task
   │
   ├──► Broadcast: TASK_RECEIVED
   │
   ▼
3. Dispatch to Supervisor
   │
   ├──► Broadcast: DECOMPOSING
   │
   ▼
4. Supervisor decomposes task
   │
   ├──► Publish: SUBTASKS to review:queue
   │
   ▼
5. State Engine receives subtasks
   │
   ├──► Broadcast: EXECUTING
   │
   ▼
6. Dispatch subtask to OpenClaw
   │
   ▼
7. OpenClaw executes and returns result
   │
   ▼
8. Supervisor reviews result
   │
   ├──► If pass: NEXT_SUBTASK or COMPLETE
   │
   └──► If fail: RETRY with feedback
   │
   ▼
9. Loop until all subtasks complete
   │
   ▼
10. Task complete, return to IDLE
```

## Message Models

### AgentMessage

```python
class AgentMessage:
    id: str              # Unique message ID
    type: MessageType    # NEW_TASK, EXECUTE, etc.
    source: str          # Sender agent name
    target: str          # Target agent (None for broadcast)
    content: dict        # Message payload
    correlation_id: str  # For request-response correlation
```

### AgentResponse

```python
class AgentResponse:
    type: str            # Response type
    output: str          # Result output
    subtasks: List       # For task decomposition
    feedback: str        # For review failures
    next_action: str     # EXECUTE, RETRY, COMPLETE
```

## Configuration

Configuration is managed via environment variables:

```python
class Settings:
    # Application
    app_name: str
    debug: bool

    # Redis
    redis_url: str
    redis_stream_prefix: str

    # Agents
    supervisor_model: str
    openclaw_adapter: str  # "mock" or "real"

    # LLM
    llm_api_key: str
    llm_base_url: str
```

## Extension Points

### Adding a New Agent

1. Create agent class inheriting `BaseAgent`
2. Implement `process()` and `get_capabilities()`
3. Register in `AgentRegistry`

### Adding a New Message Type

1. Add type to `MessageType` enum
2. Define handling logic in relevant agent
3. Update documentation

### Custom State Handlers

1. Extend `StateEngine` class
2. Override relevant methods
3. Register custom handlers