import argparse
import flwr as fl
from pathlib import Path
import json
import uuid
import httpx
import threading
import asyncio
from datetime import datetime
import numpy as np
import time
import random

from ml.fedguard_ml.federation.client_app import client_fn
from ml.fedguard_ml.federation.strategy import get_evaluate_fn
from ml.fedguard_ml.federation.update_validation import validate_update
from ml.fedguard_ml.models.dense_autoencoder import DenseAutoencoder
from ml.fedguard_ml.models.transformer_autoencoder import TransformerAutoencoder
from ml.fedguard_ml.federation.serialization import get_parameters

ML_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ML_DIR / "data" / "processed"
RUNS_DIR = ML_DIR / "federation" / "runs"

def _fire_event(run_id, event, round_num, client_id, payload):
    url = f"http://localhost:8000/api/v1/training/runs/{run_id}/events/test"
    data = {"event": event, "run_id": run_id, "round": round_num, "client_id": client_id, "payload": payload or {}}
    try:
        httpx.post(url, json=data, timeout=1.0)
    except Exception:
        pass

def emit_event(run_id, event, round_num=None, client_id=None, payload=None):
    threading.Thread(target=_fire_event, args=(run_id, event, round_num, client_id, payload), daemon=True).start()

def main():
    parser = argparse.ArgumentParser(description="Run FedGuard Flower Simulation")
    parser.add_argument("--strategy", type=str, default="fedavg", choices=["fedavg", "fedprox"])
    parser.add_argument("--model", type=str, default="dense", choices=["dense", "transformer"])
    parser.add_argument("--num-clients", type=int, default=10)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--proximal-mu", type=float, default=0.01)
    parser.add_argument("--track-mlflow", action="store_true", help="Enable MLflow tracking")
    parser.add_argument("--no-track-mlflow", action="store_false", dest="track_mlflow")
    parser.set_defaults(track_mlflow=False)
    
    # Fault Tolerance Args
    parser.add_argument("--fault-tolerance", action="store_true", help="Enable fault tolerance tracking")
    parser.add_argument("--fault-seed", type=int, default=42, help="Seed for deterministic fault injection")
    parser.add_argument("--dropout-rate", type=float, default=0.0, help="Probability of client dropout (0-1)")
    parser.add_argument("--straggler-threshold-seconds", type=float, default=10.0, help="Threshold to mark as straggler")
    parser.add_argument("--min-completed-clients", type=int, default=1, help="Minimum clients to aggregate")

    # Observability
    parser.add_argument("--metrics", action="store_true", help="Enable Prometheus metrics server")
    parser.add_argument("--metrics-port", type=int, default=9101, help="Prometheus metrics server port")
    
    # Specific Invalid Updates
    parser.add_argument("--inject-nan-update", type=str, nargs="*", default=[], help="List of client IDs to return NaN")
    parser.add_argument("--inject-inf-update", type=str, nargs="*", default=[], help="List of client IDs to return Inf")
    parser.add_argument("--inject-empty-update", type=str, nargs="*", default=[], help="List of client IDs to return empty")
    parser.add_argument("--inject-shape-mismatch", type=str, nargs="*", default=[], help="List of client IDs to return mismatched shape")
    parser.add_argument("--inject-slow-client", type=str, nargs="*", default=[], help="List of client IDs to artificially delay")
    parser.add_argument("--inject-client-failure", type=str, nargs="*", default=[], help="List of client IDs to throw an exception")
    parser.add_argument("--inject-client-timeout", type=str, nargs="*", default=[], help="List of client IDs to simulate timeout")
    
    # Privacy Arguments
    parser.add_argument("--privacy", action="store_true", help="Enable Differential Privacy")
    parser.add_argument("--dp-mode", type=str, default="opacus", choices=["none", "opacus", "update_noise"])
    parser.add_argument("--target-epsilon", type=float, default=None)
    parser.add_argument("--delta", type=float, default=1e-5)
    parser.add_argument("--noise-multiplier", type=float, default=1.0)
    parser.add_argument("--max-grad-norm", type=float, default=1.0)
    parser.add_argument("--secure-rng", action="store_true")
    parser.add_argument("--update-clipping-norm", type=float, default=1.0)
    parser.add_argument("--update-noise-std", type=float, default=0.0)

    # Edge Device Simulation Args
    parser.add_argument("--edge-simulation", action="store_true", help="Enable edge device simulation")
    parser.add_argument("--edge-config", type=str, default=None, help="Path to edge simulation config JSON")
    parser.add_argument("--partition", type=str, default="iid", help="Data partition type")

    args = parser.parse_args()

    from ml.fedguard_ml.edge import assign_profiles, EdgeSimulator
    from ml.fedguard_ml.observability.prometheus_metrics import (
        start_metrics_server, FEDERATION_RUNS, PRIVACY_RUNS
    )
    from ml.fedguard_ml.privacy.config import PrivacyConfig
    
    if args.metrics:
        start_metrics_server(args.metrics_port)
        FEDERATION_RUNS.labels(strategy=args.strategy, model_type=args.model, partition_type=args.partition).inc()
        if args.privacy:
            PRIVACY_RUNS.labels(dp_mode=args.dp_mode, model_type=args.model, strategy=args.strategy).inc()

    # Load Privacy Config
    privacy_config = PrivacyConfig(
        enabled=args.privacy,
        dp_mode=args.dp_mode,
        target_epsilon=args.target_epsilon,
        delta=args.delta,
        max_grad_norm=args.max_grad_norm,
        noise_multiplier=args.noise_multiplier,
        secure_rng=args.secure_rng,
        update_clipping_norm=args.update_clipping_norm,
        update_noise_std=args.update_noise_std
    )

    # Edge device simulation
    edge_simulator = None
    edge_profiles = None
    if args.edge_simulation:
        from ml.fedguard_ml.edge.device_profile import assign_profiles
        from ml.fedguard_ml.edge.edge_simulator import EdgeSimulator
        edge_profiles = assign_profiles(
            num_clients=args.num_clients,
            config_path=args.edge_config,
            seed=args.fault_seed,
        )
        edge_simulator = EdgeSimulator(edge_profiles, seed=args.fault_seed)
        print(f"Edge simulation enabled with {len(edge_profiles)} device profiles.")
        for cid, p in edge_profiles.items():
            print(f"  {cid}: {p.device_type} ({p.cpu_class} CPU, {p.memory_mb}MB, {p.network_latency_ms}ms latency)")

    # Create run directory
    run_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{args.strategy}_{args.model}_{uuid.uuid4().hex[:6]}"
    run_path = RUNS_DIR / run_id
    run_path.mkdir(parents=True, exist_ok=True)
    
    # MLflow tracking
    tracker = None
    if args.track_mlflow:
        import os
        from ml.fedguard_ml.tracking.mlflow_tracker import FedGuardMLflowTracker
        
        tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "file:./mlruns")
        experiment_name = os.environ.get("MLFLOW_EXPERIMENT_NAME", "FedGuard")
        strict_mode = os.environ.get("MLFLOW_STRICT_MODE", "false").lower() == "true"
        
        tracker = FedGuardMLflowTracker(tracking_uri, experiment_name, strict_mode)
        
        mlflow_run_name = f"{args.strategy}_{args.model}_iid_clients{args.num_clients}_rounds{args.rounds}_seed42"
        tracker.start_run(
            run_name=mlflow_run_name,
            tags={
                "project": "FedGuard",
                "phase": "Phase 10",
                "training_type": "federated",
                "model_type": f"{args.model}_autoencoder",
                "strategy": args.strategy,
                "num_clients": args.num_clients,
                "fedguard_run_id": run_id,
                "fault_tolerance_enabled": args.fault_tolerance,
                "privacy": "enabled" if args.privacy else "disabled",
                "dp_library": args.dp_mode if args.privacy else "none",
            }
        )
        
        tracker.log_params({
            "model_type": args.model,
            "training_type": "federated",
            "strategy": args.strategy,
            "num_clients": args.num_clients,
            "num_rounds": args.rounds,
            "dropout_rate": args.dropout_rate,
            "straggler_threshold": args.straggler_threshold_seconds,
            "privacy_enabled": args.privacy,
            "dp_mode": args.dp_mode,
            "target_epsilon": args.target_epsilon,
            "delta": args.delta,
            "noise_multiplier": args.noise_multiplier,
            "max_grad_norm": args.max_grad_norm,

            "fault_seed": args.fault_seed
        })
        if args.strategy == "fedprox":
            tracker.log_params({"proximal_mu": args.proximal_mu})
        if args.edge_simulation:
            tracker.log_params({
                "edge_simulation_enabled": True,
                "edge_config": args.edge_config or "auto",
                "device_profile_count": len(edge_profiles) if edge_profiles else 0,
            })

    # Save config
    config = vars(args)
    with open(run_path / "config.json", "w") as f:
        json.dump(config, f, indent=2)

    # Initial global model parameters
    input_dim = np.load(PROCESSED_DIR / "X_train.npy").shape[1]
    if args.model == "dense":
        initial_model = DenseAutoencoder(input_dim)
    else:
        initial_model = TransformerAutoencoder(input_dim)
        
    initial_parameters = fl.common.ndarrays_to_parameters(get_parameters(initial_model))

    def fit_config_fn(server_round: int):
        return {
            "local_epochs": 3,
            "batch_size": 256,
            "lr": 1e-3,
            "proximal_mu": args.proximal_mu if args.strategy == "fedprox" else 0.0
        }

    evaluate_fn = get_evaluate_fn(args.model, input_dim, PROCESSED_DIR, run_path)

    if args.strategy == "fedavg":
        strategy = fl.server.strategy.FedAvg(
            fraction_fit=1.0,
            fraction_evaluate=1.0,
            min_fit_clients=args.num_clients,
            min_evaluate_clients=args.num_clients,
            min_available_clients=args.num_clients,
            evaluate_fn=evaluate_fn,
            on_fit_config_fn=fit_config_fn,
            initial_parameters=initial_parameters,
        )
    elif args.strategy == "fedprox":
        strategy = fl.server.strategy.FedProx(
            fraction_fit=1.0,
            fraction_evaluate=1.0,
            min_fit_clients=args.num_clients,
            min_evaluate_clients=args.num_clients,
            min_available_clients=args.num_clients,
            evaluate_fn=evaluate_fn,
            on_fit_config_fn=fit_config_fn,
            initial_parameters=initial_parameters,
            proximal_mu=args.proximal_mu,
        )
    else:
        raise ValueError(f"Unknown strategy: {args.strategy}")

    # Custom simulation loop to bypass Ray (since Ray is failing on Windows)
    parameters = initial_parameters
    emit_event(run_id, "training.started", payload={"status": "started"})
    
    if args.fault_tolerance:
        random.seed(args.fault_seed)
        
    all_round_metrics = {}
    
    # Cache clients to preserve PrivacyEngine state across rounds
    clients = {str(cid): client_fn(str(cid), privacy_config=privacy_config) for cid in range(1, args.num_clients + 1)}
    
    for server_round in range(1, args.rounds + 1):
        print(f"\n--- Round {server_round} ---")
        emit_event(run_id, "round.start", round_num=server_round, payload={
            "strategy": args.strategy,
            "num_clients": args.num_clients
        })
        
        fit_ins = fl.common.FitIns(parameters, fit_config_fn(server_round))
        
        results = []
        clients_selected = args.num_clients
        clients_completed = 0
        clients_failed = 0
        clients_rejected = 0
        clients_timed_out = 0
        straggler_count = 0
        
        client_metrics = []
        edge_round_results = []
        
        for cid in range(1, args.num_clients + 1):
            client_id = f"client_{cid:03d}"
            c_metric = {
                "client_id": client_id,
                "status": "completed",
                "failure_reason": None,
                "is_straggler": False,
                "update_valid": True,
                "rejected_reason": None,
                "duration": 0.0
            }
            
            # Dropout
            if args.fault_tolerance and random.random() < args.dropout_rate:
                print(f"{client_id} dropped out.")
                c_metric["status"] = "dropout"
                client_metrics.append(c_metric)
                continue

            # Edge device availability check
            if edge_simulator and client_id in edge_simulator.profiles:
                avail, reason = edge_simulator.check_availability(client_id)
                if not avail:
                    print(f"{client_id} unavailable: {reason}")
                    c_metric["status"] = "dropout"
                    c_metric["failure_reason"] = f"edge:{reason}"
                    edge_result = edge_simulator.run_round_for_client(client_id, 0.0)
                    edge_round_results.append(edge_result)
                    emit_event(run_id, "edge.device_unavailable", round_num=server_round, client_id=client_id, payload={
                        "device_type": edge_simulator.profiles[client_id].device_type,
                        "reason": reason,
                        "battery_level": edge_simulator.profiles[client_id].battery_level
                    })
                    client_metrics.append(c_metric)
                    continue
                    
            emit_event(run_id, "client.training", round_num=server_round, client_id=client_id)
            client = clients[str(cid)]
            print(f"Training {client_id}...")
            
            start_time = time.time()
            
            try:
                # Inject timeout
                if client_id in args.inject_client_timeout:
                    time.sleep(0.1) # Simulate delay without real long wait
                    clients_timed_out += 1
                    emit_event(run_id, "client.timeout", round_num=server_round, client_id=client_id)
                    print(f"{client_id} timed out.")
                    c_metric["status"] = "timeout"
                    c_metric["duration"] = time.time() - start_time
                    client_metrics.append(c_metric)
                    continue
                    
                # Inject failure
                if client_id in args.inject_client_failure:
                    raise RuntimeError("Injected failure")
                    
                # Inject slow client
                if client_id in args.inject_slow_client:
                    time.sleep(0.1) # small delay for test
                    duration = args.straggler_threshold_seconds + 1.0 # Force straggler status
                else:
                    duration = 0.05
                    
                fit_res = client.fit(fit_ins)
                c_metric["duration"] = duration
                
                # Check straggler
                if duration > args.straggler_threshold_seconds:
                    straggler_count += 1
                    c_metric["is_straggler"] = True
                    emit_event(run_id, "client.straggler", round_num=server_round, client_id=client_id)
                    print(f"{client_id} is a straggler.")
                    
                # Fault injections for updates
                ndarrays = fl.common.parameters_to_ndarrays(fit_res.parameters)
                
                if client_id in args.inject_nan_update:
                    ndarrays[0][0] = np.nan
                elif client_id in args.inject_inf_update:
                    ndarrays[0][0] = np.inf
                elif client_id in args.inject_empty_update:
                    ndarrays = []
                elif client_id in args.inject_shape_mismatch:
                    ndarrays[0] = np.zeros((1, 1))
                
                # Validation
                expected_shapes = [w.shape for w in fl.common.parameters_to_ndarrays(parameters)]
                val_result = validate_update(ndarrays, expected_shapes)
                
                if not val_result.valid:
                    clients_rejected += 1
                    c_metric["status"] = "rejected"
                    c_metric["update_valid"] = False
                    c_metric["rejected_reason"] = val_result.reason
                    emit_event(run_id, "client.rejected", round_num=server_round, client_id=client_id, payload={"reason": val_result.reason})
                    print(f"{client_id} rejected: {val_result.reason}")
                    client_metrics.append(c_metric)
                    continue
                
                fit_res.parameters = fl.common.ndarrays_to_parameters(ndarrays)
                
                emit_event(run_id, "client.completed", round_num=server_round, client_id=client_id)
                clients_completed += 1
                
                # Record edge telemetry for this successful client
                if edge_simulator and client_id in edge_simulator.profiles:
                    edge_result = edge_simulator.run_round_for_client(client_id, duration)
                    edge_round_results.append(edge_result)
                    c_metric["simulated_training_time"] = edge_result.simulated_training_time
                    c_metric["simulated_communication_time"] = edge_result.simulated_communication_time
                
                client_metrics.append(c_metric)
                
                class MockClientProxy(fl.server.client_proxy.ClientProxy):
                    def __init__(self, cid): super().__init__(cid)
                    def get_properties(self, ins, timeout, group_id): return None
                    def get_parameters(self, ins, timeout, group_id): return None
                    def fit(self, ins, timeout, group_id): return None
                    def evaluate(self, ins, timeout, group_id): return None
                    def reconnect(self, ins, timeout, group_id): return None
                    
                mock_proxy = MockClientProxy(str(cid))
                results.append((mock_proxy, fit_res))
                
            except Exception as e:
                clients_failed += 1
                c_metric["status"] = "failed"
                c_metric["failure_reason"] = str(e)
                c_metric["duration"] = time.time() - start_time
                client_metrics.append(c_metric)
                emit_event(run_id, "client.failed", round_num=server_round, client_id=client_id, payload={"error": str(e)})
                print(f"{client_id} failed: {e}")
                continue
            
        # Determine round status
        completion_rate = clients_completed / clients_selected if clients_selected > 0 else 0
        if clients_completed == 0 or clients_completed < args.min_completed_clients:
            round_status = "failed"
        elif clients_completed < clients_selected:
            round_status = "partial_success"
        else:
            round_status = "success"
            
        # Log fault metrics
        round_fault_metrics = {
            "round": server_round,
            "clients_selected": clients_selected,
            "clients_completed": clients_completed,
            "clients_failed": clients_failed,
            "clients_rejected": clients_rejected,
            "clients_timed_out": clients_timed_out,
            "straggler_count": straggler_count,
            "completion_rate": completion_rate,
            "dropout_rate": args.dropout_rate,
            "round_status": round_status,
            "client_metrics": client_metrics
        }
        
        # Add edge round summary
        if edge_simulator and edge_round_results:
            available_results = [r for r in edge_round_results if r.available]
            unavailable_results = [r for r in edge_round_results if not r.available]
            battery_skipped = [r for r in unavailable_results if r.availability_reason == "battery_low"]
            avg_latency = sum(r.network_latency_ms for r in edge_round_results) / len(edge_round_results) if edge_round_results else 0
            avg_bw = sum(r.bandwidth_mbps for r in edge_round_results) / len(edge_round_results) if edge_round_results else 0
            
            round_fault_metrics["edge_summary"] = {
                "average_latency_ms": round(avg_latency, 2),
                "average_bandwidth_mbps": round(avg_bw, 2),
                "battery_skipped_clients": len(battery_skipped),
                "availability_rate": round(len(available_results) / len(edge_round_results), 4) if edge_round_results else 1.0,
                "edge_straggler_count": sum(1 for r in available_results if r.total_client_time > args.straggler_threshold_seconds),
                "edge_client_results": [r.to_dict() for r in edge_round_results]
            }
            
        if args.metrics:
            from ml.fedguard_ml.observability.prometheus_metrics import (
                FEDERATION_ROUNDS, CLIENTS_SELECTED, CLIENTS_COMPLETED,
                CLIENTS_FAILED, CLIENTS_REJECTED, CLIENTS_TIMED_OUT,
                COMPLETION_RATE, FAULT_STRAGGLERS, FAULT_DROPOUTS, FAULT_PARTIAL_ROUNDS, FAULT_FAILED_ROUNDS
            )
            FEDERATION_ROUNDS.labels(strategy=args.strategy, model_type=args.model).inc()
            CLIENTS_SELECTED.labels(strategy=args.strategy, model_type=args.model).inc(clients_selected)
            CLIENTS_COMPLETED.labels(strategy=args.strategy, model_type=args.model).inc(clients_completed)
            CLIENTS_FAILED.labels(strategy=args.strategy, model_type=args.model).inc(clients_failed)
            CLIENTS_REJECTED.labels(strategy=args.strategy, model_type=args.model).inc(clients_rejected)
            CLIENTS_TIMED_OUT.labels(strategy=args.strategy, model_type=args.model).inc(clients_timed_out)
            COMPLETION_RATE.labels(strategy=args.strategy, model_type=args.model).set(completion_rate)
            
            if straggler_count > 0:
                FAULT_STRAGGLERS.labels(fault_type="straggler", strategy=args.strategy, model_type=args.model).inc(straggler_count)
            if (clients_selected - clients_completed - clients_failed - clients_rejected) > 0:
                dropouts = (clients_selected - clients_completed - clients_failed - clients_rejected)
                FAULT_DROPOUTS.labels(fault_type="dropout", strategy=args.strategy, model_type=args.model).inc(dropouts)
                
            if round_status == "partial_success":
                FAULT_PARTIAL_ROUNDS.labels(fault_type="partial_round", strategy=args.strategy, model_type=args.model).inc()
            elif round_status == "failed":
                FAULT_FAILED_ROUNDS.labels(fault_type="failed_round", strategy=args.strategy, model_type=args.model).inc()

        all_round_metrics[server_round] = round_fault_metrics
        
        if round_status == "failed":
            print(f"Round {server_round} failed. Not enough clients completed.")
            emit_event(run_id, "round.failed", round_num=server_round)
            continue
        elif round_status == "partial_success":
            emit_event(run_id, "round.partial", round_num=server_round)
            
        # 3. Aggregate fit
        emit_event(run_id, "aggregation.started", round_num=server_round)
        aggregated_parameters, metrics_aggregated = strategy.aggregate_fit(server_round, results, [])
        if aggregated_parameters is not None:
            parameters = aggregated_parameters
        emit_event(run_id, "aggregation.completed", round_num=server_round)
            
        # 4. Centralized evaluation
        if evaluate_fn is not None:
            loss, metrics = evaluate_fn(server_round, fl.common.parameters_to_ndarrays(parameters), {})
            print(f"Round {server_round} evaluation - loss: {loss}, metrics: {metrics}")
            emit_event(run_id, "metrics.updated", round_num=server_round, payload={
                "accuracy": metrics.get("accuracy"),
                "f1": metrics.get("f1"),
                "loss": loss
            })
            
    # Save fault metrics
    with open(run_path / "fault_metrics.json", "w") as f:
        json.dump({"run_id": run_id, "rounds": [all_round_metrics[r] for r in sorted(all_round_metrics.keys())]}, f, indent=2)

    # Save edge metrics
    if edge_simulator and edge_profiles:
        edge_data = {
            "run_id": run_id,
            "edge_simulation_enabled": True,
            "seed": args.fault_seed,
            "profiles": {cid: p.to_dict() for cid, p in edge_profiles.items()},
        }
        with open(run_path / "edge_metrics.json", "w") as f:
            json.dump(edge_data, f, indent=2)
            
        with open(run_path / "edge_config.json", "w") as f:
            json.dump({"enabled": True, "seed": args.fault_seed}, f, indent=2)
            
        edge_report = {
            "run_id": run_id,
            "edge_simulation": "enabled",
            "device_profile_count": len(edge_profiles),
            "summary": "Simulated heterogeneous edge-device behavior."
        }
        with open(run_path / "edge_report.json", "w") as f:
            json.dump(edge_report, f, indent=2)
            
        with open(run_path / "edge_report.md", "w") as f:
            f.write(f"# Edge Simulation Report\n\nRun ID: {run_id}\n\nFedGuard simulates heterogeneous edge-device behavior for federated-learning experiments.\n\nTotal device profiles: {len(edge_profiles)}\n")
            
        print(f"Edge metrics saved to {run_path / 'edge_metrics.json'}")
        
    if privacy_config.enabled:
        with open(run_path / "privacy_config.json", "w") as f:
            json.dump(privacy_config.to_dict(), f, indent=2)
            
        # Get privacy spent from first client (since they all do the same amount of work in IID config)
        first_client = clients.get("1")
        if first_client and hasattr(first_client, "numpy_client") and first_client.numpy_client.privacy_engine:
            privacy_spent = first_client.numpy_client.privacy_engine.get_privacy_spent()
        else:
            privacy_spent = {}
            
        with open(run_path / "privacy_spent.json", "w") as f:
            json.dump(privacy_spent, f, indent=2)
            
        with open(run_path / "privacy_report.json", "w") as f:
            json.dump({
                "privacy_enabled": True,
                "dp_mode": privacy_config.dp_mode,
                "formal_accounting": privacy_spent.get("formal_accounting", False),
                "epsilon_spent": privacy_spent.get("epsilon_spent"),
                "delta": privacy_config.delta,
                "performance_tradeoff": "Formal DP reduces model precision; clipping restricts influence.",
                "limitations": "Model evaluated centrally. Secure Aggregation not used due to simulation loop constraints."
            }, f, indent=2)
            
        if tracker and privacy_spent.get("epsilon_spent") is not None:
            tracker.log_metrics({"final_epsilon_spent": privacy_spent["epsilon_spent"]})

    emit_event(run_id, "training.completed", payload={"status": "completed"})
        
    print(f"\nSimulation finished. Results saved to {run_path}")

    if tracker:
        metrics_file = run_path / "round_metrics.json"
        if metrics_file.exists():
            with open(metrics_file, "r") as f:
                saved_metrics = json.load(f)
            
            rounds_data = saved_metrics.get("rounds", {})
            last_round = 0
            for round_str, r_metrics in rounds_data.items():
                r_num = int(round_str)
                last_round = max(last_round, r_num)
                orig = r_metrics.get("original", {})
                tracker.log_metrics({
                    "round_val_loss": r_metrics.get("loss"),
                    "global_accuracy": orig.get("accuracy"),
                    "global_precision": orig.get("precision"),
                    "global_recall": orig.get("recall"),
                    "global_f1": orig.get("f1"),
                    "global_roc_auc": orig.get("roc_auc"),
                    "global_pr_auc": orig.get("pr_auc")
                }, step=r_num)
                
                # Log fault metrics
                if r_num in all_round_metrics:
                    fm = all_round_metrics[r_num]
                    metrics_to_log = {
                        "clients_selected": fm["clients_selected"],
                        "clients_completed": fm["clients_completed"],
                        "clients_failed": fm["clients_failed"],
                        "clients_rejected": fm["clients_rejected"],
                        "clients_timed_out": fm["clients_timed_out"],
                        "straggler_count": fm["straggler_count"],
                        "completion_rate": fm["completion_rate"]
                    }
                    if "edge_summary" in fm:
                        edge_summary = fm["edge_summary"]
                        metrics_to_log.update({
                            "round_average_latency_ms": edge_summary.get("average_latency_ms"),
                            "round_availability_rate": edge_summary.get("availability_rate"),
                            "round_edge_straggler_count": edge_summary.get("edge_straggler_count")
                        })
                    tracker.log_metrics(metrics_to_log, step=r_num)
                
            if str(last_round) in rounds_data:
                final_orig = rounds_data[str(last_round)].get("original", {})
                tracker.log_metrics({
                    "final_accuracy": final_orig.get("accuracy"),
                    "final_precision": final_orig.get("precision"),
                    "final_recall": final_orig.get("recall"),
                    "final_f1": final_orig.get("f1"),
                    "final_roc_auc": final_orig.get("roc_auc"),
                    "final_pr_auc": final_orig.get("pr_auc"),
                    "final_false_positive_rate": final_orig.get("fpr"),
                    "final_false_negative_rate": final_orig.get("fnr")
                })
                
            # Log aggregate edge metrics for the run
            if args.edge_simulation and all_round_metrics:
                valid_edge_summaries = [fm["edge_summary"] for fm in all_round_metrics.values() if "edge_summary" in fm]
                if valid_edge_summaries:
                    tracker.log_metrics({
                        "average_latency_ms": sum(s.get("average_latency_ms", 0) for s in valid_edge_summaries) / len(valid_edge_summaries),
                        "average_bandwidth_mbps": sum(s.get("average_bandwidth_mbps", 0) for s in valid_edge_summaries) / len(valid_edge_summaries),
                        "availability_rate": sum(s.get("availability_rate", 0) for s in valid_edge_summaries) / len(valid_edge_summaries),
                        "battery_skipped_clients": sum(s.get("battery_skipped_clients", 0) for s in valid_edge_summaries),
                        "edge_straggler_count": sum(s.get("edge_straggler_count", 0) for s in valid_edge_summaries)
                    })
        
        # Log artifacts
        tracker.log_artifacts(str(run_path))
        
        # Save metadata
        metadata = tracker.get_metadata()
        with open(run_path / "mlflow_metadata.json", "w") as f:
            json.dump(metadata, f, indent=4)
            
        tracker.end_run()

if __name__ == "__main__":
    main()
