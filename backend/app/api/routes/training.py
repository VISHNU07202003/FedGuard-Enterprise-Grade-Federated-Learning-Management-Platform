from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.db.models import TrainingRun, TrainingRound, GlobalMetric
from typing import List

router = APIRouter()

@router.get("/runs")
async def list_runs(db: AsyncSession = Depends(get_db)):
    from app.db.models import PrivacyConfigModel
    # Use outer join to include privacy if available
    result = await db.execute(
        select(TrainingRun, PrivacyConfigModel)
        .outerjoin(PrivacyConfigModel, TrainingRun.run_id == PrivacyConfigModel.run_id)
        .order_by(TrainingRun.created_at.desc())
    )
    rows = result.all()
    # Serialize to list of dicts
    out = []
    for run, priv in rows:
        r_dict = {c.name: getattr(run, c.name) for c in run.__table__.columns}
        if priv and priv.enabled:
            r_dict["privacy_enabled"] = True
            r_dict["dp_mode"] = priv.dp_mode
        else:
            r_dict["privacy_enabled"] = False
        out.append(r_dict)
    return out

@router.get("/runs/{run_id}")
async def get_run(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TrainingRun).where(TrainingRun.run_id == run_id))
    run = result.scalars().first()
    if not run:
        from app.core.exceptions import NotFoundError
        raise NotFoundError(message=f"Training run {run_id} not found")
        
    from app.db.models import RoundClient
    edge_check = await db.execute(select(RoundClient).where(RoundClient.run_id == run_id).where(RoundClient.network_latency_ms != None).limit(1))
    has_edge = edge_check.scalars().first() is not None
    
    r_dict = {c.name: getattr(run, c.name) for c in run.__table__.columns}
    r_dict["edge_simulation_enabled"] = has_edge
    return r_dict

@router.get("/runs/{run_id}/edge")
async def get_run_edge_metrics(run_id: str, db: AsyncSession = Depends(get_db)):
    from app.db.models import RoundClient
    result = await db.execute(select(RoundClient).where(RoundClient.run_id == run_id).where(RoundClient.network_latency_ms != None).order_by(RoundClient.round_number.asc()))
    clients = result.scalars().all()
    
    rounds_data = {}
    for c in clients:
        if c.round_number not in rounds_data:
            rounds_data[c.round_number] = []
        rounds_data[c.round_number].append({
            "client_id": c.client_id,
            "network_latency_ms": c.network_latency_ms,
            "edge_bandwidth_mbps": c.edge_bandwidth_mbps,
            "battery_level": c.battery_level,
            "availability_reason": c.availability_reason,
            "simulated_training_time": c.simulated_training_time,
            "simulated_communication_time": c.simulated_communication_time
        })
    
    return rounds_data

@router.get("/runs/{run_id}/rounds")
async def get_run_rounds(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TrainingRound).where(TrainingRound.run_id == run_id).order_by(TrainingRound.round_number.asc()))
    return result.scalars().all()

@router.get("/runs/{run_id}/metrics")
async def get_run_metrics(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GlobalMetric).where(GlobalMetric.run_id == run_id))
    metric = result.scalars().first()
    if not metric:
        from app.core.exceptions import NotFoundError
        raise NotFoundError(message="Metrics not found")
    return metric

@router.get("/runs/{run_id}/privacy")
async def get_run_privacy(run_id: str, db: AsyncSession = Depends(get_db)):
    from app.db.models import PrivacyConfigModel
    result = await db.execute(select(PrivacyConfigModel).where(PrivacyConfigModel.run_id == run_id))
    privacy = result.scalars().first()
    if not privacy:
        return {"enabled": False}
    return privacy
from app.db.models import UserModel
from app.api.deps import RequireRole, get_current_active_user

@router.post('/runs/ingest', dependencies=[Depends(RequireRole(['admin']))])
async def ingest_run():
    return {'status': 'ingested'}

@router.post('/runs/{run_id}/pause', dependencies=[Depends(RequireRole(['admin', 'researcher']))])
async def pause_run(run_id: str):
    return {'status': 'paused', 'run_id': run_id}

@router.post('/runs/{run_id}/stop', dependencies=[Depends(RequireRole(['admin', 'researcher']))])
async def stop_run(run_id: str):
    return {'status': 'stopped', 'run_id': run_id}
