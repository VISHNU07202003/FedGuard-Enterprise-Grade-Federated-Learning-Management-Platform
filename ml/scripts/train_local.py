import argparse
import json
import time
import uuid
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path
from datetime import datetime

from ml.fedguard_ml.models.dense_autoencoder import DenseAutoencoder
from ml.fedguard_ml.models.transformer_autoencoder import TransformerAutoencoder
from ml.fedguard_ml.training.thresholds import calculate_threshold, save_threshold
from ml.fedguard_ml.privacy.config import PrivacyConfig
from ml.fedguard_ml.privacy.differential_privacy import FedGuardPrivacyEngine

ML_DIR = Path(__file__).resolve().parent.parent
PARTITIONS_DIR = ML_DIR / "data" / "partitions"
PROCESSED_DIR = ML_DIR / "data" / "processed"
RUNS_DIR = ML_DIR / "runs"

def get_model(model_name, input_dim):
    if model_name == "dense":
        return DenseAutoencoder(input_dim)
    elif model_name == "transformer":
        return TransformerAutoencoder(input_dim)
    else:
        raise ValueError(f"Unknown model: {model_name}")

def train():
    print("Starting local training...")
    parser = argparse.ArgumentParser(description="Local Training for FedGuard Phase 10")
    parser.add_argument("--model", type=str, choices=["dense", "transformer"], required=True)
    parser.add_argument("--client-id", type=str, default=None, help="E.g., client_001. If None, trains on central data.")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--track-mlflow", action="store_true", help="Enable MLflow tracking")
    
    # Privacy Arguments
    parser.add_argument("--privacy", action="store_true", help="Enable Differential Privacy")
    parser.add_argument("--dp-mode", type=str, default="opacus", choices=["none", "opacus", "update_noise"])
    parser.add_argument("--target-epsilon", type=float, default=None)
    parser.add_argument("--delta", type=float, default=1e-5)
    parser.add_argument("--noise-multiplier", type=float, default=1.0)
    parser.add_argument("--max-grad-norm", type=float, default=1.0)
    parser.add_argument("--secure-rng", action="store_true")
    
    args = parser.parse_args()
    
    privacy_config = PrivacyConfig(
        enabled=args.privacy,
        dp_mode=args.dp_mode,
        target_epsilon=args.target_epsilon,
        delta=args.delta,
        max_grad_norm=args.max_grad_norm,
        noise_multiplier=args.noise_multiplier,
        secure_rng=args.secure_rng
    )
    
    run_id = f"local_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{args.model}_{uuid.uuid4().hex[:6]}"
    run_path = RUNS_DIR / run_id
    run_path.mkdir(exist_ok=True, parents=True)
    
    # MLflow tracking
    tracker = None
    if args.track_mlflow:
        import os
        from ml.fedguard_ml.tracking.mlflow_tracker import FedGuardMLflowTracker
        
        tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "file:./mlruns")
        experiment_name = os.environ.get("MLFLOW_EXPERIMENT_NAME", "FedGuard")
        strict_mode = os.environ.get("MLFLOW_STRICT_MODE", "false").lower() == "true"
        
        tracker = FedGuardMLflowTracker(tracking_uri, experiment_name, strict_mode)
        
        mlflow_run_name = f"local_{args.model}_{args.client_id or 'central'}_seed42"
        tracker.start_run(
            run_name=mlflow_run_name,
            tags={
                "project": "FedGuard",
                "phase": "Phase 10",
                "training_type": "local",
                "model_type": f"{args.model}_autoencoder",
                "strategy": "local",
                "privacy": "enabled" if privacy_config.enabled else "disabled",
                "dp_library": privacy_config.dp_mode if privacy_config.enabled else "none",
                "client_id": args.client_id or "central",
                "fedguard_run_id": run_id
            }
        )
        
        tracker.log_params({
            "model_type": args.model,
            "local_epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": args.lr,
            "privacy_enabled": privacy_config.enabled,
            "dp_mode": privacy_config.dp_mode,
            "target_epsilon": privacy_config.target_epsilon,
            "delta": privacy_config.delta,
            "noise_multiplier": privacy_config.noise_multiplier,
            "max_grad_norm": privacy_config.max_grad_norm
        })
    
    # Load Data
    if args.client_id:
        client_dir = PARTITIONS_DIR / "iid" / args.client_id
        print(f"Loading data from {client_dir}")
        X_train = np.load(client_dir / "X_train.npy")
        y_train = np.load(client_dir / "y_train.npy")
    else:
        print(f"Loading centralized data from {PROCESSED_DIR}")
        X_train = np.load(PROCESSED_DIR / "X_train.npy")
        y_train = np.load(PROCESSED_DIR / "y_train.npy")
        
    normal_indices = (y_train == 0)
    X_train_normal = X_train[normal_indices]
    
    input_dim = X_train.shape[1]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    model = get_model(args.model, input_dim).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    criterion = nn.MSELoss()
    
    dataset = TensorDataset(torch.tensor(X_train_normal))
    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)
    
    # Privacy wrapping
    privacy_engine = FedGuardPrivacyEngine(privacy_config)
    if privacy_config.enabled and privacy_config.dp_mode == "opacus":
        print("Initializing Opacus PrivacyEngine...")
        model, optimizer, dataloader = privacy_engine.make_private(
            model=model,
            optimizer=optimizer,
            data_loader=dataloader,
            epochs=args.epochs
        )
    
    print(f"Training {args.model} autoencoder on {len(X_train_normal)} normal samples...")
    start_time = time.time()
    
    history = {"train_loss": []}
    
    model.train()
    for epoch in range(args.epochs):
        epoch_loss = 0.0
        for batch_x, in dataloader:
            batch_x = batch_x.to(device)
            
            optimizer.zero_grad()
            reconstructed = model(batch_x)
            loss = criterion(reconstructed, batch_x)
            
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item() * batch_x.size(0)
            
        epoch_loss /= len(X_train_normal)
        history["train_loss"].append(epoch_loss)
        print(f"Epoch {epoch+1}/{args.epochs} - Loss: {epoch_loss:.6f}")
        
    duration = time.time() - start_time
    
    # End of Training, grab privacy metrics
    privacy_spent = privacy_engine.get_privacy_spent()
    epsilon_spent = privacy_spent.get("epsilon_spent")
    
    # Validation step to find threshold using FULL validation set
    print("Calculating threshold using validation set...")
    # NOTE: In Opacus, evaluating the model might require removing the wrapper or setting eval()
    # Opacus wraps model with GradSampleModule. We can still call it in eval() mode.
    X_val = np.load(PROCESSED_DIR / "X_val.npy")
    y_val = np.load(PROCESSED_DIR / "y_val.npy")
    X_val_tensor = torch.tensor(X_val).to(device)
    
    model.eval()
    with torch.no_grad():
        val_recon = model(X_val_tensor)
        val_mse = torch.mean((X_val_tensor - val_recon)**2, dim=1).cpu().numpy()
        
    threshold = calculate_threshold(
        reconstruction_errors=None, 
        method="f1_optimal", 
        val_labels=y_val, 
        val_errors=val_mse
    )
    print(f"Optimal threshold set at: {threshold:.6f}")
    if epsilon_spent is not None:
        print(f"Epsilon spent: {epsilon_spent:.4f}")
    
    # Save artifacts
    # Unwrap model to save the original state dict without _module prefixes
    if privacy_config.enabled and privacy_config.dp_mode == "opacus":
        torch.save(model._module.state_dict(), run_path / "model.pt")
    else:
        torch.save(model.state_dict(), run_path / "model.pt")
        
    save_threshold(threshold, run_path / "threshold.json")
    
    config = {
        "model": args.model,
        "client_id": args.client_id,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "lr": args.lr,
        "input_dim": input_dim,
        "training_time": duration
    }
    with open(run_path / "config.json", "w") as f:
        json.dump(config, f, indent=2)
        
    with open(run_path / "metrics.json", "w") as f:
        json.dump(history, f, indent=2)
        
    if privacy_config.enabled:
        with open(run_path / "privacy_config.json", "w") as f:
            json.dump(privacy_config.to_dict(), f, indent=2)
        
        with open(run_path / "privacy_spent.json", "w") as f:
            json.dump(privacy_spent, f, indent=2)
            
        with open(run_path / "privacy_report.json", "w") as f:
            json.dump({
                "privacy_enabled": True,
                "dp_mode": privacy_config.dp_mode,
                "formal_accounting": privacy_spent.get("formal_accounting", False),
                "epsilon_spent": epsilon_spent,
                "delta": privacy_config.delta,
                "performance_tradeoff": "Formal DP may reduce model precision.",
                "limitations": "Model evaluated centrally. Secure Aggregation not used."
            }, f, indent=2)

    print(f"Run completed in {duration:.2f}s. Artifacts saved to {run_path}")

    if tracker:
        metrics = {
            "final_train_loss": history["train_loss"][-1],
            "training_time": duration,
            "threshold": threshold
        }
        if epsilon_spent is not None:
            metrics["epsilon_spent"] = epsilon_spent
            
        tracker.log_metrics(metrics)
        tracker.log_artifacts(str(run_path))
        
        metadata = tracker.get_metadata()
        with open(run_path / "mlflow_metadata.json", "w") as f:
            json.dump(metadata, f, indent=4)
        tracker.end_run()

if __name__ == "__main__":
    train()

