from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.db.models import Client, UserModel
from app.api.deps import RequireRole, get_current_active_user

router = APIRouter()

@router.get("/")
async def list_clients(db: AsyncSession = Depends(get_db), current_user: UserModel = Depends(get_current_active_user)):
    result = await db.execute(select(Client).order_by(Client.client_id.asc()))
    return result.scalars().all()

@router.get("/{client_id}")
async def get_client(client_id: str, db: AsyncSession = Depends(get_db), current_user: UserModel = Depends(get_current_active_user)):
    result = await db.execute(select(Client).where(Client.client_id == client_id))
    return result.scalars().first()

@router.post("/{client_id}/quarantine", dependencies=[Depends(RequireRole(["admin"]))])
async def quarantine_client(client_id: str, db: AsyncSession = Depends(get_db)):
    return {"status": "quarantined", "client_id": client_id}
