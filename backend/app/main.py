"""Main FastAPI application for streamYourClaw."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api import api_router, websocket_handler
from .agents import register_default_agents
from .config import settings
from .core import get_message_queue, get_state_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}...")

    # Initialize message queue
    queue = await get_message_queue()
    print("Message queue connected")

    # Register agents
    register_default_agents()
    print("Agents registered")

    # Start state engine
    engine = await get_state_engine()
    await engine.start()
    print("State engine started")

    yield

    # Shutdown
    print("Shutting down...")
    await engine.stop()
    await queue.disconnect()
    print("Goodbye!")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Open-source AI Agent live streaming system for TikTok",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time updates."""
    await websocket_handler(websocket)


# Serve frontend static files
frontend_path = Path(settings.frontend_path)
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )