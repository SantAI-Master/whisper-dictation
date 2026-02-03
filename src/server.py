# src/server.py
"""Web server for status dashboard."""
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Set
import asyncio
import json


app = FastAPI(title="Whisper Dictation")

# WebSocket connections for live updates
connections: Set[WebSocket] = set()

# Shared state
state = {
    "status": "idle",
    "history": [],  # List of recent transcriptions
}


@app.get("/")
async def index():
    """Serve the dashboard."""
    return FileResponse("static/index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for live status updates."""
    await websocket.accept()
    connections.add(websocket)

    # Send current state
    await websocket.send_json(state)

    try:
        while True:
            # Keep connection alive, handle client messages if needed
            await websocket.receive_text()
    except Exception:
        pass
    finally:
        connections.discard(websocket)


async def broadcast_state():
    """Send current state to all connected clients."""
    if connections:
        message = json.dumps(state)
        await asyncio.gather(
            *[ws.send_text(message) for ws in connections],
            return_exceptions=True,
        )


def update_status(status: str):
    """Update status and broadcast to clients."""
    state["status"] = status
    # Run broadcast in the event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(broadcast_state())
    except RuntimeError:
        pass


def add_transcription(text: str):
    """Add a transcription to history and broadcast."""
    from datetime import datetime
    state["history"].insert(0, {
        "text": text,
        "timestamp": datetime.now().isoformat(),
    })
    # Keep only last 50
    state["history"] = state["history"][:50]
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(broadcast_state())
    except RuntimeError:
        pass


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
