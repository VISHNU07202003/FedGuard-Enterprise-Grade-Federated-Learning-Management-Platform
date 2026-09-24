from fastapi import APIRouter

router = APIRouter()

@router.get("/events")
async def list_security_events():
    return []
