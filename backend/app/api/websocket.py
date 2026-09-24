from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import manager
from app.schemas.websocket import WebSocketEvent
from app.services.training_event_service import training_event_service
import asyncio
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/training/{run_id}")
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    await manager.connect(run_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Can handle incoming messages like pings/heartbeats here
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(run_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket error for run {run_id}: {e}")
        manager.disconnect(run_id, websocket)

@router.post("/api/v1/training/runs/{run_id}/events/test")
async def emit_test_event(run_id: str, event: dict):
    """
    Test endpoint for Phase 7A. Broadcasts a custom event to connected WebSockets.
    """
    await training_event_service.emit_event(
        event_type=event.get("event", "test.event"),
        run_id=run_id,
        round_num=event.get("round"),
        client_id=event.get("client_id"),
        payload=event.get("payload", {})
    )
    return {"status": "event_emitted", "run_id": run_id}
