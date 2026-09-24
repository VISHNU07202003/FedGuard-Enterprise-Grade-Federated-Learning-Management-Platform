import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AuditLog

async def log_audit_event(
    db: AsyncSession,
    actor: str,
    action: str,
    resource_type: str,
    resource_id: str = None,
    result: str = "success",
    metadata: dict = None
):
    metadata_str = json.dumps(metadata) if metadata else None
    audit_log = AuditLog(
        actor=actor,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        result=result,
        metadata=metadata_str
    )
    db.add(audit_log)
    await db.commit()