# API Documentation

This document describes the REST API and WebSocket interface for streamYourClaw.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. For production deployments, implement appropriate authentication middleware.

---

## REST API

### System Endpoints

#### GET /

Root endpoint returning API information.

**Response:**
```json
{
    "name": "streamYourClaw",
    "version": "0.1.0",
    "status": "running"
}
```

---

#### GET /api/health

Health check endpoint.

**Response:**
```json
{
    "status": "healthy",
    "engine": {
        "state": "IDLE",
        "current_task": null,
        "tasks_completed": 0,
        "tasks_failed": 0,
        "uptime": 3600.0,
        "running": true
    }
}
```

---

#### GET /api/status

Get full system status.

**Response:**
```json
{
    "state": "PROCESSING",
    "current_task": {
        "id": "task-uuid",
        "title": "Example Task",
        "description": "Task description",
        "status": "IN_PROGRESS",
        "subtasks": [...],
        "current_subtask_index": 0,
        "retry_count": 0
    },
    "tasks_completed": 5,
    "tasks_failed": 1,
    "uptime": 3600.0,
    "running": true
}
```

---

### Task Endpoints

#### POST /api/task

Submit a new task for execution.

**Request Body:**
```json
{
    "description": "Write a Python function to sort a list",
    "title": "Optional task title"
}
```

**Response:**
```json
{
    "task_id": "uuid-string",
    "title": "Optional task title",
    "status": "PENDING"
}
```

**Status Codes:**
- `200` - Task created successfully
- `400` - Missing required field (description)

---

#### GET /api/task/{task_id}

Get task details by ID.

**Path Parameters:**
- `task_id` (string) - The unique task identifier

**Response:**
```json
{
    "id": "task-uuid",
    "title": "Task Title",
    "description": "Task description",
    "status": "IN_PROGRESS",
    "priority": 0,
    "created_at": "2026-03-19T10:00:00Z",
    "updated_at": "2026-03-19T10:05:00Z",
    "subtasks": [
        {
            "id": "subtask-uuid",
            "title": "Subtask 1",
            "description": "Subtask description",
            "status": "COMPLETED",
            "order": 0,
            "result": "Result output"
        }
    ],
    "current_subtask_index": 1,
    "retry_count": 0,
    "max_retries": 3
}
```

**Status Codes:**
- `200` - Task found
- `404` - Task not found

---

#### GET /api/tasks

List recent tasks.

**Query Parameters:**
- `limit` (integer, optional) - Maximum number of tasks to return (default: 10)

**Response:**
```json
[
    {
        "id": "task-uuid-1",
        "title": "Task 1",
        "status": "COMPLETED",
        ...
    },
    {
        "id": "task-uuid-2",
        "title": "Task 2",
        "status": "IN_PROGRESS",
        ...
    }
]
```

---

### Agent Endpoints

#### GET /api/agents

List all registered agents.

**Response:**
```json
{
    "agents": {
        "Supervisor": {
            "name": "Supervisor",
            "version": "0.1.0",
            "capabilities": ["decompose", "review", "decide"]
        },
        "OpenClaw": {
            "name": "OpenClaw",
            "version": "0.1.0",
            "capabilities": ["code", "search", "browse", "execute"]
        }
    }
}
```

---

#### GET /api/agents/{agent_name}

Get details of a specific agent.

**Path Parameters:**
- `agent_name` (string) - The agent name

**Response:**
```json
{
    "name": "Supervisor",
    "version": "0.1.0",
    "description": "Supervises OpenClaw execution",
    "capabilities": ["decompose", "review", "decide", "feedback"]
}
```

**Status Codes:**
- `200` - Agent found
- `404` - Agent not found

---

## WebSocket API

### Connection

Connect to the WebSocket endpoint:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

### Message Format

All messages are JSON objects with the following structure:

```json
{
    "channel": "stream:name",
    "data": {
        // Message payload
    }
}
```

### Channels

#### state:broadcast

State changes from the engine.

**Message:**
```json
{
    "channel": "state:broadcast",
    "data": {
        "type": "STATE_CHANGE",
        "state": "EXECUTING",
        "agent": "OpenClaw",
        "task_id": "task-uuid",
        "message": "Executing subtask",
        "timestamp": "2026-03-19T10:00:00Z"
    }
}
```

**State Values:**
- `IDLE` - System idle
- `TASK_RECEIVED` - New task received
- `DECOMPOSING` - Supervisor decomposing task
- `EXECUTING` - OpenClaw executing subtask
- `REVIEWING` - Supervisor reviewing result
- `COMPLETED` - Task completed
- `RETRY` - Retrying subtask
- `ERROR` - Error occurred

---

#### log:broadcast

Thought logs from agents.

**Message:**
```json
{
    "channel": "log:broadcast",
    "data": {
        "type": "THOUGHT",
        "agent": "Supervisor",
        "message": "Analyzing task requirements...",
        "level": "thinking",
        "timestamp": "2026-03-19T10:00:00Z"
    }
}
```

**Log Levels:**
- `info` - General information
- `thinking` - Agent thinking process
- `success` - Success message
- `warning` - Warning message
- `error` - Error message
- `waiting` - Waiting state

---

#### mindmap:broadcast

Mindmap updates for visualization.

**Message:**
```json
{
    "channel": "mindmap:broadcast",
    "data": {
        "id": "task-uuid",
        "title": "Main Task",
        "status": "processing",
        "children": [
            {
                "id": "subtask-1",
                "title": "Subtask 1",
                "status": "completed",
                "children": []
            },
            {
                "id": "subtask-2",
                "title": "Subtask 2",
                "status": "processing",
                "children": []
            }
        ]
    }
}
```

**Node Status:**
- `pending` - Gray
- `processing` - Blue
- `completed` - Green
- `failed` - Red

---

### Client Usage Example

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    console.log('Connected to streamYourClaw');
};

ws.onmessage = (event) => {
    const { channel, data } = JSON.parse(event.data);

    switch (channel) {
        case 'state:broadcast':
            updateStateDisplay(data);
            break;
        case 'log:broadcast':
            appendLog(data);
            break;
        case 'mindmap:broadcast':
            updateMindmap(data);
            break;
    }
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = () => {
    console.log('Disconnected from streamYourClaw');
    // Implement reconnection logic
};
```

---

## Error Handling

### Error Response Format

```json
{
    "detail": "Error message description"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error |
| 503 | Service Unavailable - Redis connection issue |

---

## Rate Limiting

Currently, no rate limiting is implemented. For production use, implement rate limiting middleware.

---

## Versioning

The API is currently in v0.x (alpha). Breaking changes may occur. Once v1.0 is released, versioning will follow semantic versioning.