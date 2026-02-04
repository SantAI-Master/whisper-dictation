# src/server.py
"""Web server for status dashboard."""
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Set, Callable, Optional
import asyncio
import json


app = FastAPI(title="Whisper Dictation")

# WebSocket connections for live updates
connections: Set[WebSocket] = set()

# Callback for mode changes (set by main.py)
_on_mode_change: Optional[Callable[[str], None]] = None
_get_mode: Optional[Callable[[], str]] = None

# Shared state
state = {
    "status": "idle",
    "format_mode": "single-line",
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


def set_mode_callback(on_change: Callable[[str], None], get_mode: Callable[[], str]):
    """Set callbacks for mode changes."""
    global _on_mode_change, _get_mode
    _on_mode_change = on_change
    _get_mode = get_mode
    # Initialize state with current mode
    state["format_mode"] = get_mode()


def update_mode(mode: str):
    """Update the format mode in state and broadcast."""
    state["format_mode"] = mode
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(broadcast_state())
    except RuntimeError:
        pass


@app.post("/api/mode")
async def set_mode(mode: str):
    """Set the format mode."""
    if mode not in ("single-line", "document"):
        return {"error": "Invalid mode. Use 'single-line' or 'document'"}
    if _on_mode_change:
        _on_mode_change(mode)
    state["format_mode"] = mode
    await broadcast_state()
    return {"mode": mode}


@app.get("/api/mode")
async def get_mode():
    """Get the current format mode."""
    return {"mode": state["format_mode"]}


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
