from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from sqlalchemy.future import select
from sqlalchemy import func
from app.schemas.dashboard import DashboardSummaryResponse, EdgeSimulationSummary
from app.db.models import Client, TrainingRun, TrainingRound, RoundClient

router = APIRouter()

@router.get("/", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """
    Returns the dashboard summary queried from the database.
    """
    # KPI Metrics
    total_clients = (await db.execute(select(func.count(Client.client_id)))).scalar() or 0
    active_runs = (await db.execute(select(func.count(TrainingRun.run_id)).where(TrainingRun.status == "running"))).scalar() or 0
    
    # Current Run
    latest_run = (await db.execute(select(TrainingRun).order_by(TrainingRun.created_at.desc()).limit(1))).scalars().first()
    
    current_run_data = None
    model_perf = []
    edge_summary = EdgeSimulationSummary()
    
    if latest_run:
        rounds = (await db.execute(select(TrainingRound).where(TrainingRound.run_id == latest_run.run_id).order_by(TrainingRound.round_number.asc()))).scalars().all()
        for r in rounds:
            model_perf.append({
                "round": r.round_number,
                "accuracy": r.global_accuracy or 0.0,
                "loss": r.val_loss or 0.0,
                "f1": r.global_f1 or 0.0
            })
            
        current_run_data = {
            "run_id": latest_run.run_id,
            "status": latest_run.status,
            "current_round": max([r.round_number for r in rounds]) if rounds else 0,
            "total_rounds": latest_run.num_rounds or 0,
            "active_clients": latest_run.num_clients or 0,
            "accuracy": model_perf[-1]["accuracy"] if model_perf else 0.0,
            "privacy_enabled": False,
            "dp_mode": "none"
        }
        
        # Edge simulation
        edge_clients = (await db.execute(select(Client).where(Client.device_type != None))).scalars().all()
        if edge_clients:
            edge_summary.enabled = True
            edge_summary.active_edge_clients = len(edge_clients)
            
            # Aggregate edge metrics from RoundClient for latest run
            edge_rcs = (await db.execute(select(RoundClient).where(RoundClient.run_id == latest_run.run_id).where(RoundClient.network_latency_ms != None))).scalars().all()
            if edge_rcs:
                edge_summary.average_latency_ms = sum([r.network_latency_ms for r in edge_rcs if r.network_latency_ms]) / len(edge_rcs) if edge_rcs else 0
                edge_summary.edge_stragglers = len([r for r in edge_rcs if r.is_straggler])
                
            edge_summary.battery_limited_clients = len([c for c in edge_clients if c.battery_powered])
            edge_summary.slowest_device_profile = "raspberry_pi_4" # mock

    return {
        "system_status": {"status": "healthy", "message": "All systems operational"},
        "kpi_metrics": {
            "total_clients": total_clients,
            "active_training_runs": active_runs,
            "anomalies_detected_24h": 0,
            "system_health_score": 100
        },
        "current_training_run": current_run_data,
        "client_health_summary": {
            "online": total_clients,
            "offline": 0,
            "training": active_runs,
            "error": 0
        },
        "model_performance_series": model_perf,
        "recent_security_events": [],
        "recent_experiments": [],
        "service_health": [],
        "edge_simulation": edge_summary
    }
