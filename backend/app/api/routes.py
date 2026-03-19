"""REST API routes for streamYourClaw."""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from ..agents import AgentRegistry
from ..core import get_state_engine
from ..models import Task

router = APIRouter()


@router.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {
        "name": "streamYourClaw",
        "version": "0.1.0",
        "status": "running",
    }


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    engine = await get_state_engine()
    return {
        "status": "healthy",
        "engine": engine.get_status(),
    }


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """Get current system status."""
    engine = await get_state_engine()
    return engine.get_status()


@router.post("/task")
async def submit_task(task: Dict[str, str]) -> Dict[str, Any]:
    """
    Submit a new task for execution.

    Request body:
    {
        "description": "Task description",
        "title": "Optional task title"
    }
    """
    description = task.get("description")
    if not description:
        raise HTTPException(status_code=400, detail="description is required")

    title = task.get("title")

    engine = await get_state_engine()
    new_task = await engine.submit_task(description, title)

    return {
        "task_id": new_task.id,
        "title": new_task.title,
        "status": new_task.status.value,
    }


@router.get("/task/{task_id}")
async def get_task(task_id: str) -> Dict[str, Any]:
    """Get task by ID."""
    engine = await get_state_engine()

    # Check current task
    if engine.current_task and engine.current_task.id == task_id:
        return engine.current_task.model_dump()

    # Check history
    for task in engine.task_history:
        if task.id == task_id:
            return task.model_dump()

    raise HTTPException(status_code=404, detail="Task not found")


@router.get("/tasks")
async def list_tasks(limit: int = 10) -> List[Dict[str, Any]]:
    """List recent tasks."""
    engine = await get_state_engine()

    tasks = []
    if engine.current_task:
        tasks.append(engine.current_task.model_dump())

    for task in engine.task_history[-limit:]:
        tasks.append(task.model_dump())

    return tasks


@router.get("/agents")
async def list_agents() -> Dict[str, Any]:
    """List all registered agents."""
    return {
        "agents": {
            name: {
                "name": agent.name,
                "version": agent.version,
                "capabilities": agent.get_capabilities(),
            }
            for name, agent in AgentRegistry.get_all().items()
        }
    }


@router.get("/agents/{agent_name}")
async def get_agent(agent_name: str) -> Dict[str, Any]:
    """Get agent by name."""
    agent = AgentRegistry.get(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return {
        "name": agent.name,
        "version": agent.version,
        "description": agent.description,
        "capabilities": agent.get_capabilities(),
    }