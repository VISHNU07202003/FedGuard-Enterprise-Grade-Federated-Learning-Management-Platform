from fastapi import WebSocket
from typing import Dict, List
import logging
from app.schemas.websocket import WebSocketEvent

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # run_id -> list of WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, run_id: str, websocket: WebSocket):
        await websocket.accept()
        if run_id not in self.active_connections:
            self.active_connections[run_id] = []
        self.active_connections[run_id].append(websocket)
        logger.info(f"WebSocket connected for run {run_id}. Total: {len(self.active_connections[run_id])}")
        from app.observability.metrics import WS_ACTIVE_CONNECTIONS
        WS_ACTIVE_CONNECTIONS.inc()

    def disconnect(self, run_id: str, websocket: WebSocket):
        if run_id in self.active_connections and websocket in self.active_connections[run_id]:
            self.active_connections[run_id].remove(websocket)
            if not self.active_connections[run_id]:
                del self.active_connections[run_id]
            logger.info(f"WebSocket disconnected from run {run_id}.")
            from app.observability.metrics import WS_ACTIVE_CONNECTIONS, WS_DISCONNECTS
            WS_ACTIVE_CONNECTIONS.dec()
            WS_DISCONNECTS.inc()

    async def broadcast(self, run_id: str, event: WebSocketEvent):
        import time
        from app.observability.metrics import WS_MESSAGES_SENT, WS_EVENT_EMIT_DURATION
        
        start = time.time()
        if run_id in self.active_connections:
            event_json = event.model_dump_json()
            disconnected = []
            for connection in self.active_connections[run_id]:
                try:
                    await connection.send_text(event_json)
                    WS_MESSAGES_SENT.labels(event_type=event.event).inc()
                except Exception as e:
                    logger.warning(f"Error sending event to websocket: {e}")
                    disconnected.append(connection)
            
            for d in disconnected:
                self.disconnect(run_id, d)
        
        WS_EVENT_EMIT_DURATION.labels(event_type=event.event).observe(time.time() - start)

    async def send_error(self, websocket: WebSocket, code: str, message: str, run_id: str):
        error_event = WebSocketEvent(
            event="error",
            run_id=run_id,
            payload={"code": code, "message": message}
        )
        try:
            await websocket.send_text(error_event.model_dump_json())
        except Exception:
            pass

manager = ConnectionManager()
