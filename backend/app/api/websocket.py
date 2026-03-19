"""WebSocket handler for real-time frontend communication."""

import asyncio
import json
from typing import Dict, Set

from fastapi import WebSocket, WebSocketDisconnect

from ..core import BROADCAST_STREAMS, get_message_queue
from ..models import LogBroadcast, StateBroadcast


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)

    async def broadcast(self, message: Dict) -> None:
        """Broadcast message to all connections."""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        # Clean up disconnected
        self.active_connections -= disconnected

    async def send_to(self, websocket: WebSocket, message: Dict) -> None:
        """Send message to specific connection."""
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)


manager = ConnectionManager()


async def websocket_handler(websocket: WebSocket) -> None:
    """
    Handle WebSocket connections.

    Streams:
    - state:broadcast - State changes
    - log:broadcast - Thought logs
    - mindmap:broadcast - Mindmap updates
    """
    await manager.connect(websocket)

    try:
        # Get message queue
        queue = await get_message_queue()

        # Subscribe to broadcast streams
        subscribe_task = asyncio.create_task(
            _broadcast_listener(websocket, queue)
        )

        # Handle incoming messages from client
        receive_task = asyncio.create_task(
            _receive_handler(websocket)
        )

        # Wait for either task to complete
        done, pending = await asyncio.wait(
            [subscribe_task, receive_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        # Cancel pending tasks
        for task in pending:
            task.cancel()

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)


async def _broadcast_listener(websocket: WebSocket, queue) -> None:
    """Listen to Redis broadcasts and send to client."""
    async for message in queue.subscribe(list(BROADCAST_STREAMS)):
        try:
            data = message.get("data", {})

            # Format for frontend
            formatted = {
                "channel": message.get("stream"),
                "data": data,
            }

            await manager.send_to(websocket, formatted)
        except Exception as e:
            print(f"Broadcast listener error: {e}")
            break


async def _receive_handler(websocket: WebSocket) -> None:
    """Handle incoming messages from WebSocket client."""
    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                # Handle client messages if needed
                # Currently we only broadcast to frontend
                print(f"Received from client: {message}")
            except json.JSONDecodeError:
                print(f"Invalid JSON from client: {data}")

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Receive handler error: {e}")