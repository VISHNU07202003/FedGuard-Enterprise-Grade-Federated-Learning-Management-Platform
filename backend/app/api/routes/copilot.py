from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.db.session import get_db
from app.db.models import UserModel
from app.api.deps import get_current_active_user, RequireRole
from app.schemas.copilot import CopilotRequest, CopilotResponse
from app.ai.copilot_service import process_chat
from app.services.audit_service import log_audit_event

router = APIRouter()

@router.post("/chat", response_model=CopilotResponse, dependencies=[Depends(RequireRole(["admin", "researcher", "viewer"]))])
async def copilot_chat(
    request: CopilotRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Interact with FedGuard Copilot.
    """
    from app.observability.metrics import COPILOT_REQUESTS, COPILOT_DURATION
    import time
    start_time = time.time()

    # Generate the response
    response = await process_chat(db, request)
    
    COPILOT_REQUESTS.labels(mode=response.mode, result="success" if response.grounded else "blocked").inc()
    COPILOT_DURATION.labels(mode=response.mode).observe(time.time() - start_time)

    # Audit log the interaction
    await log_audit_event(
        db=db,
        actor=current_user.email,
        action=f"copilot.{request.context.action or 'chat'}",
        resource_type="copilot_context",
        resource_id=request.context.run_id or request.context.experiment_id or "general",
        result="blocked" if not response.grounded else "success",
        metadata={"mode": response.mode}
    )
    
    return response