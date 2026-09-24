from fastapi import APIRouter, Depends
from app.db.models import UserModel
from app.api.deps import RequireRole, get_current_active_user

router = APIRouter()

@router.get("/")
async def list_models(current_user: UserModel = Depends(get_current_active_user)):
    return []

@router.get("/{model_version}")
async def get_model(model_version: str, current_user: UserModel = Depends(get_current_active_user)):
    return {"model_version": model_version}

@router.post("/{model_version}/promote", dependencies=[Depends(RequireRole(["admin"]))])
async def promote_model(model_version: str):
    return {"status": "promoted", "model_version": model_version}
