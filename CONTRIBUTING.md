# Contributing to streamYourClaw

Thank you for your interest in contributing to streamYourClaw! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
  - [Contributing Status Videos](#contributing-status-videos)
  - [Contributing Agent Modules](#contributing-agent-modules)
  - [Contributing Themes](#contributing-themes)
  - [Contributing Code](#contributing-code)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/streamYourClaw.git`
3. Install dependencies: `pip install -e ".[dev]"`
4. Create a branch: `git checkout -b my-contribution`

## How to Contribute

### Contributing Status Videos

Status videos are displayed in the frontend to show the current state of the agent. You can contribute new videos to enhance the visual experience.

#### Video Requirements

| Property | Requirement |
|----------|-------------|
| Format | MP4 (H.264 codec) |
| Resolution | 400x400 or 600x600 pixels (square) |
| Duration | 3-10 seconds (loop-friendly) |
| File size | < 5 MB |
| Frame rate | 30 FPS recommended |

#### Steps to Contribute

1. Add your video file to `frontend/assets/videos/`
2. Update `frontend/assets/videos/meta.json`:

```json
{
  "states": {
    "thinking": {
      "name": "Thinking",
      "videos": [
        { "file": "thinking_01.mp4", "weight": 1.0 },
        { "file": "YOUR_VIDEO.mp4", "weight": 0.8 }
      ],
      "indicatorColor": "#d29922"
    }
  }
}
```

3. Commit with message: `[Video] Add YOUR_VIDEO.mp4 for thinking state`
4. Submit a Pull Request

#### Available States

- `typing` - Agent is inputting text
- `waiting` - Agent is waiting for results
- `thinking` - Agent is processing/thinking

### Contributing Agent Modules

You can create new agents to extend streamYourClaw's capabilities.

#### Steps to Create an Agent

1. Create a new directory in `backend/app/agents/your_agent/`
2. Create `__init__.py` with your agent class:

```python
# backend/app/agents/your_agent/__init__.py
from ..base import BaseAgent, AgentResponse
from ..models import AgentMessage

class YourAgent(BaseAgent):
    """Your custom agent description."""

    name = "YourAgent"
    version = "0.1.0"
    description = "What your agent does"

    def get_capabilities(self):
        return ["capability_1", "capability_2"]

    async def process(self, message: AgentMessage) -> AgentResponse:
        # Your implementation
        return AgentResponse(
            type="YOUR_RESPONSE_TYPE",
            output="Result"
        )
```

3. Register in `backend/app/agents/__init__.py`:

```python
from .your_agent import YourAgent

def register_default_agents():
    AgentRegistry.register(SupervisorAgent())
    AgentRegistry.register(OpenClawAdapter())
    AgentRegistry.register(YourAgent())  # Add this
```

4. Add tests in `backend/tests/test_your_agent.py`
5. Update documentation

#### Agent Interface

All agents must:

- Inherit from `BaseAgent`
- Implement `process(message) -> AgentResponse`
- Implement `get_capabilities() -> List[str]`
- Handle the message types they subscribe to

### Contributing Themes

Create custom visual themes for the frontend.

1. Create a CSS file in `frontend/css/themes/`:

```css
/* frontend/css/themes/dark-purple.css */
:root {
    --bg-primary: #1a1a2e;
    --bg-secondary: #16213e;
    --accent-blue: #7b2cbf;
    --accent-green: #00ff88;
}
```

2. Update `index.html` to include the theme option
3. Submit your PR

### Contributing Code

For bug fixes and features:

1. Check existing issues or create a new one
2. Fork and create a branch
3. Write code following the existing style
4. Add tests for new functionality
5. Update documentation
6. Submit PR

## Development Setup

### Prerequisites

- Python 3.10+
- Redis (for message queue)
- Node.js (optional, for frontend development)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Start Redis (Docker)
docker run -d -p 6379:6379 redis:alpine

# Run server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
# Use any static file server, e.g.:
python -m http.server 8080
# Or with VSCode Live Server extension
```

### Running Tests

```bash
pytest backend/tests -v
```

## Pull Request Process

1. **Title Format**: Use prefixes for clarity
   - `[Video]` for video contributions
   - `[Agent]` for new agents
   - `[Theme]` for theme contributions
   - `[Fix]` for bug fixes
   - `[Feature]` for new features

2. **Description**: Include
   - What changes you made
   - Why you made them
   - How to test

3. **Checklist**:
   - [ ] Code follows project style
   - [ ] Tests pass
   - [ ] Documentation updated
   - [ ] Commit messages are clear

4. **Review**: Wait for maintainers to review your PR

## Questions?

Open an issue with the `question` label or join our discussions.

Thank you for contributing!