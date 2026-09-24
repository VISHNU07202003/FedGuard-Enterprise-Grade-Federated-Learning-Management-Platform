from app.schemas.websocket import WebSocketEvent
from app.services.websocket_manager import manager
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings

class TrainingEventService:
    @staticmethod
    async def emit_event(
        event_type: str, 
        run_id: str, 
        round_num: Optional[int] = None, 
        client_id: Optional[str] = None, 
        payload: Dict[str, Any] = None
    ):
        if payload is None:
            payload = {}
            
        event = WebSocketEvent(
            event=event_type,
            run_id=run_id,
            round=round_num,
            client_id=client_id,
            payload=payload
        )
        await manager.broadcast(run_id, event)
        
    @staticmethod
    async def emit_event_http(
        event_type: str, 
        run_id: str, 
        round_num: Optional[int] = None, 
        client_id: Optional[str] = None, 
        payload: Dict[str, Any] = None
    ):
        """Used by external python scripts (like the federated simulation) to push events via HTTP if they don't have direct access to the manager."""
        if payload is None:
            payload = {}
        
        url = f"http://localhost:8000/api/v1/training/runs/{run_id}/events/test"
        
        data = {
            "event": event_type,
            "run_id": run_id,
            "round": round_num,
            "client_id": client_id,
            "payload": payload
        }
        
        async with httpx.AsyncClient() as client:
            try:
                await client.post(url, json=data, timeout=2.0)
            except Exception:
                pass # Swallow error if backend is not running

training_event_service = TrainingEventService()
