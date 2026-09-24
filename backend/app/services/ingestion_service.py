import json
import uuid
import datetime
from pathlib import Path
from typing import Dict, Any

from app.db.models import TrainingRun, TrainingRound, GlobalMetric, ModelVersion, RoundClient, Client
from sqlalchemy.ext.asyncio import AsyncSession

async def ingest_federation_run(session: AsyncSession, run_path: Path):
    """
    Ingests a Phase 5 federated run output folder into the database.
    """
    if not run_path.exists():
        raise ValueError(f"Run path does not exist: {run_path}")
        
    config_file = run_path / "config.json"
    metrics_file = run_path / "round_metrics.json"
    
    if not config_file.exists() or not metrics_file.exists():
        raise ValueError("Missing config.json or round_metrics.json in run directory")
        
    with open(config_file, "r") as f:
        config = json.load(f)
        
    with open(metrics_file, "r") as f:
        metrics = json.load(f)
        
    # Extract run_id from directory name
    run_id = run_path.name
    
    # Read MLflow metadata if available
    mlflow_metadata = {}
    mlflow_file = run_path / "mlflow_metadata.json"
    if mlflow_file.exists():
        with open(mlflow_file, "r") as f:
            mlflow_metadata = json.load(f)
    
    # 1. Create TrainingRun
    training_run = TrainingRun(
        run_id=run_id,
        experiment_id=None,
        model_type=config.get("model", "unknown"),
        strategy=config.get("strategy", "unknown"),
        status="completed",
        num_clients=config.get("num_clients", 0),
        num_rounds=config.get("rounds", 0),
        started_at=datetime.datetime.utcnow(), # Approximate if not in config
        completed_at=datetime.datetime.utcnow(),
        artifact_path=str(run_path),
        mlflow_run_id=mlflow_metadata.get("mlflow_run_id"),
        mlflow_experiment_id=mlflow_metadata.get("mlflow_experiment_id"),
        mlflow_tracking_uri=mlflow_metadata.get("tracking_uri")
    )
    session.add(training_run)
    await session.flush()
    
    # Read fault metrics if available
    fault_metrics = {}
    fault_file = run_path / "fault_metrics.json"
    if fault_file.exists():
        with open(fault_file, "r") as f:
            fm_data = json.load(f)
            # Map round number to its fault metrics
            for rm in fm_data.get("rounds", []):
                fault_metrics[rm["round"]] = rm

    # Read edge metrics if available
    edge_metrics = {}
    edge_file = run_path / "edge_metrics.json"
    if edge_file.exists():
        with open(edge_file, "r") as f:
            edge_metrics = json.load(f)

    # 2. Parse rounds
    rounds_data = metrics.get("rounds", {})
    last_round_metrics = None
    
    for round_str, round_data in rounds_data.items():
        round_number = int(round_str)
        orig_metrics = round_data.get("original", {})
        
        fm = fault_metrics.get(round_number, {})
        
        training_round = TrainingRound(
            run_id=run_id,
            round_number=round_number,
            train_loss=None, # Client loss not currently tracked globally
            val_loss=round_data.get("loss"),
            global_accuracy=orig_metrics.get("accuracy"),
            global_precision=orig_metrics.get("precision"),
            global_recall=orig_metrics.get("recall"),
            global_f1=orig_metrics.get("f1"),
            global_roc_auc=orig_metrics.get("roc_auc"),
            global_pr_auc=orig_metrics.get("pr_auc"),
            clients_selected=fm.get("clients_selected", 0),
            clients_completed=fm.get("clients_completed", 0),
            clients_failed=fm.get("clients_failed", 0),
            clients_rejected=fm.get("clients_rejected", 0),
            clients_timed_out=fm.get("clients_timed_out", 0),
            straggler_count=fm.get("straggler_count", 0),
            dropout_rate=fm.get("dropout_rate", 0.0),
            completion_rate=fm.get("completion_rate", 1.0),
            round_status=fm.get("round_status", "success")
        )
        session.add(training_round)
        last_round_metrics = orig_metrics
        
        # Add client metrics for this round
        for c_metric in fm.get("client_metrics", []):
            # Check if client exists
            client_id = c_metric["client_id"]
            
            # Simple upsert logic for Client is skipped for brevity (assuming clients exist or will be populated by another process)
            # Let's just create RoundClient records
            # Actually, to prevent FK errors, we must make sure Client exists.
            from sqlalchemy.future import select
            client_exists = await session.execute(select(Client).where(Client.client_id == client_id))
            if not client_exists.scalars().first():
                # Extract edge client profile if it exists
                profile = edge_metrics.get("profiles", {}).get(client_id, {})
                new_client = Client(
                    client_id=client_id, 
                    organization_name=f"Org {client_id}",
                    device_type=profile.get("device_type"),
                    cpu_class=profile.get("cpu_class"),
                    memory_mb=profile.get("memory_mb"),
                    bandwidth_mbps=profile.get("bandwidth_mbps"),
                    battery_powered=profile.get("battery_powered")
                )
                session.add(new_client)
                await session.flush()
                
            # Find edge telemetry for this client in this round
            edge_telemetry = {}
            edge_summary = fm.get("edge_summary", {})
            for ecr in edge_summary.get("edge_client_results", []):
                if ecr.get("client_id") == client_id:
                    edge_telemetry = ecr
                    break
                
            rc = RoundClient(
                run_id=run_id,
                round_number=round_number,
                client_id=client_id,
                status=c_metric.get("status"),
                failure_reason=c_metric.get("failure_reason"),
                is_straggler=c_metric.get("is_straggler", False),
                update_valid=c_metric.get("update_valid", True),
                rejected_reason=c_metric.get("rejected_reason"),
                client_duration_seconds=c_metric.get("duration"),
                network_latency_ms=edge_telemetry.get("network_latency_ms"),
                edge_bandwidth_mbps=edge_telemetry.get("bandwidth_mbps"),
                battery_level=edge_telemetry.get("battery_level"),
                availability_reason=edge_telemetry.get("availability_reason"),
                simulated_training_time=c_metric.get("simulated_training_time"),
                simulated_communication_time=c_metric.get("simulated_communication_time")
            )
            session.add(rc)
            
    # 3. Create GlobalMetric for the final round
    if last_round_metrics:
        global_metric = GlobalMetric(
            run_id=run_id,
            accuracy=last_round_metrics.get("accuracy"),
            precision=last_round_metrics.get("precision"),
            recall=last_round_metrics.get("recall"),
            f1=last_round_metrics.get("f1"),
            roc_auc=last_round_metrics.get("roc_auc"),
            pr_auc=last_round_metrics.get("pr_auc"),
            false_positive_rate=last_round_metrics.get("fpr"),
            false_negative_rate=last_round_metrics.get("fnr"),
            threshold=last_round_metrics.get("threshold"),
            threshold_source=last_round_metrics.get("threshold_source"),
            confusion_matrix_json=last_round_metrics.get("confusion_matrix")
        )
        session.add(global_metric)
        
    # 4. Model Version
    model_version = ModelVersion(
        model_version=f"{run_id}_final",
        run_id=run_id,
        model_type=config.get("model", "unknown"),
        strategy=config.get("strategy", "unknown"),
        checkpoint_path=str(run_path / "global_model.pt"),
        f1=last_round_metrics.get("f1") if last_round_metrics else None,
        roc_auc=last_round_metrics.get("roc_auc") if last_round_metrics else None,
        pr_auc=last_round_metrics.get("pr_auc") if last_round_metrics else None,
        mlflow_run_id=mlflow_metadata.get("mlflow_run_id")
    )
    session.add(model_version)
    
    # 5. Privacy Config
    from app.db.models import PrivacyConfigModel
    privacy_file = run_path / "privacy_config.json"
    if privacy_file.exists():
        with open(privacy_file, "r") as f:
            p_conf = json.load(f)
            
        spent_file = run_path / "privacy_spent.json"
        e_spent = None
        if spent_file.exists():
            with open(spent_file, "r") as f:
                spent_data = json.load(f)
                e_spent = spent_data.get("epsilon_spent")
                
        p_model = PrivacyConfigModel(
            run_id=run_id,
            enabled=p_conf.get("enabled", False),
            dp_mode=p_conf.get("dp_mode", "none"),
            target_epsilon=p_conf.get("target_epsilon"),
            epsilon_spent=e_spent,
            delta=p_conf.get("delta"),
            noise_multiplier=p_conf.get("noise_multiplier"),
            max_grad_norm=p_conf.get("max_grad_norm"),
            secure_rng=p_conf.get("secure_rng", False)
        )
        session.add(p_model)
    
    await session.commit()
    return training_run
