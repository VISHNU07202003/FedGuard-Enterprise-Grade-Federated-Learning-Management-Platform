from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from datetime import datetime, timezone

class WebSocketEvent(BaseModel):
    event: str
    version: int = 1
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    run_id: str
    round: Optional[int] = None
    client_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
