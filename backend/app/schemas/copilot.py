from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class CopilotContext(BaseModel):
    run_id: Optional[str] = None
    experiment_id: Optional[str] = None
    page: Optional[str] = None
    round_number: Optional[int] = None
    security_event_id: Optional[str] = None
    action: Optional[str] = None # explain_run, compare_experiments, etc.

class CopilotRequest(BaseModel):
    message: str
    context: CopilotContext = Field(default_factory=CopilotContext)

class CopilotSource(BaseModel):
    type: str
    id: str

class CopilotResponse(BaseModel):
    answer: str
    mode: str
    grounded: bool = True
    sources: List[CopilotSource] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    created_at: str
