# streamYourClaw

<div align="center">

**Open-source AI Agent Live Streaming System for TikTok**

A Supervisor Agent continuously monitors OpenClaw's execution and orchestrates tasks - running perpetually without stopping.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[English](#overview) | [中文文档](README_CN.md)

</div>

---

## Overview

streamYourClaw enables real-time broadcasting of AI agent task execution on TikTok. The system features:

- **Perpetual Execution** - A Supervisor Agent oversees OpenClaw's continuous task execution, never stopping
- **Real-time Visualization** - Broadcast the AI's thinking process via TikTok live streaming
- **Community Driven** - All modules can be contributed via Pull Requests
- **Pluggable Architecture** - Easy to extend with new agents, themes, and content

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Viewer Layer                          │
│          TikTok Live ← OBS ← Frontend Web               │
└─────────────────────────────────────────────────────────┘
                         ↓ WebSocket
┌─────────────────────────────────────────────────────────┐
│                   Backend Service                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │  FastAPI Application                             │   │
│  │  ├── State Engine (Core Scheduler)              │   │
│  │  ├── Agent Orchestrator                         │   │
│  │  └── WebSocket Gateway                          │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                         ↓ Redis Streams
┌─────────────────────────────────────────────────────────┐
│                   Agent Workers                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │  Supervisor  │ ←─────→ │   OpenClaw   │             │
│  │   (Monitor)  │         │  (Executor)  │             │
│  └──────────────┘         └──────────────┘             │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Redis server
- (Optional) Docker & Docker Compose

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/streamYourClaw.git
cd streamYourClaw

# Install dependencies
pip install -e ".[dev]"

# Start Redis (using Docker)
docker run -d -p 6379:6379 redis:alpine

# Start the backend server
cd backend
uvicorn app.main:app --reload --port 8000
```

### Access the Frontend

Open your browser and navigate to `http://localhost:8000`

### TikTok Live Streaming Setup

1. Open OBS Studio
2. Add a "Browser" source
3. Set URL to `http://localhost:8000`
4. Set resolution to 1080x1920 (9:16 vertical)
5. Start streaming to TikTok

## Project Structure

```
streamYourClaw/
├── frontend/              # Web frontend (HTML/CSS/JS)
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── assets/
│       └── videos/        # Status video assets
│           └── meta.json  # Video configuration
│
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── api/          # REST & WebSocket endpoints
│   │   ├── core/         # State Engine, Message Queue
│   │   ├── agents/       # Agent modules (pluggable)
│   │   └── models/       # Data models
│   └── tests/
│
├── sdk/                   # SDK for contributors
│   └── python/
│
├── docs/                  # Documentation
│   └── contributing/      # Contribution guides
│
└── scripts/               # Utility scripts
```

## Features

### State Engine

The core orchestrator that manages:
- Task lifecycle and execution flow
- Inter-agent communication via Redis Streams
- Real-time state broadcasting to frontend

### Supervisor Agent

An AI agent that:
- Decomposes tasks into subtasks
- Reviews OpenClaw's execution results
- Decides next actions (continue, retry, fail)
- Provides feedback for improvements

### OpenClaw Integration

Reserved interface for connecting to OpenClaw:
- Currently operates in mock mode for demonstration
- Ready for real OpenClaw integration

### Visual Components

- **Mindmap**: Displays task hierarchy and progress
- **Status Videos**: Shows agent state with animated videos
- **Thought Log**: Real-time stream of agent thoughts

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

| What | How |
|------|-----|
| Status Videos | Add MP4 to `frontend/assets/videos/`, update `meta.json` |
| Agent Modules | Create agent in `backend/app/agents/`, inherit `BaseAgent` |
| Themes | Add CSS to `frontend/css/themes/` |
| Code | Fork → Branch → PR |

Detailed guides:
- [Contributing Videos](docs/contributing/videos.md)
- [Contributing Agents](docs/contributing/agents.md)
- [Contributing Themes](docs/contributing/themes.md)

## API Reference

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/` | API info |
| GET | `/api/health` | Health check |
| GET | `/api/status` | System status |
| POST | `/api/task` | Submit new task |
| GET | `/api/task/{id}` | Get task by ID |
| GET | `/api/tasks` | List recent tasks |
| GET | `/api/agents` | List registered agents |

### WebSocket

Connect to `/ws` for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Handle state:broadcast, log:broadcast, mindmap:broadcast
};
```

## Configuration

Environment variables (`.env`):

```bash
# Application
APP_NAME=streamYourClaw
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8000

# Redis
REDIS_URL=redis://localhost:6379/0

# LLM (for Supervisor)
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://api.openai.com/v1
SUPERVISOR_MODEL=gpt-4
```

## Docker Deployment

```bash
# Using Docker Compose
docker-compose up -d

# Or build manually
docker build -t streamyourclaw .
docker run -p 8000:8000 streamyourclaw
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Inspired by AI agent visualization needs
- Community contributions welcome

---

<div align="center">

Made with ❤️ by the streamYourClaw community

</div>