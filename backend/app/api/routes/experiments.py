from fastapi import APIRouter, Depends
from app.api.deps import RequireRole, get_current_active_user
from app.db.models import UserModel

router = APIRouter()

@router.get("/")
async def list_experiments(current_user: UserModel = Depends(get_current_active_user)):
    return []

@router.get("/{experiment_id}")
async def get_experiment(experiment_id: str, current_user: UserModel = Depends(get_current_active_user)):
    return {"experiment_id": experiment_id}

@router.post("/", dependencies=[Depends(RequireRole(["admin", "researcher"]))])
async def create_experiment():
    # Example of audit logging would go here
    return {"status": "created"}
