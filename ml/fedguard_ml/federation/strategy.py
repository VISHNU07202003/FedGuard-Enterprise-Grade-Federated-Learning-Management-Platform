import flwr as fl
from typing import Callable, Dict, List, Optional, Tuple
import numpy as np
import torch
import json
from pathlib import Path

from ml.fedguard_ml.federation.serialization import set_parameters
from ml.fedguard_ml.models.dense_autoencoder import DenseAutoencoder
from ml.fedguard_ml.models.transformer_autoencoder import TransformerAutoencoder
from ml.fedguard_ml.training.thresholds import calculate_threshold
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, precision_score, recall_score, average_precision_score, confusion_matrix

def get_evaluate_fn(model_name: str, input_dim: int, test_data_path: Path, run_path: Path) -> Callable:
    # Load global test set (has both normal and anomalies)
    X_test = np.load(test_data_path / "X_test.npy")
    y_test = np.load(test_data_path / "y_test.npy")
    
    # Load global val set (has both normal and anomalies globally, but we will filter)
    X_val = np.load(test_data_path / "X_val.npy")
    y_val = np.load(test_data_path / "y_val.npy")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    if model_name == "dense":
        model = DenseAutoencoder(input_dim).to(device)
    else:
        model = TransformerAutoencoder(input_dim).to(device)
        
    def evaluate(
        server_round: int,
        parameters: fl.common.NDArrays,
        config: Dict[str, fl.common.Scalar],
    ) -> Optional[Tuple[float, Dict[str, fl.common.Scalar]]]:
        
        set_parameters(model, parameters)
        model.eval()
        
        # 1. Compute threshold on NORMAL validation samples ONLY
        val_normal_mask = (y_val == 0)
        X_val_normal = torch.tensor(X_val[val_normal_mask]).to(device)
        
        with torch.no_grad():
            val_recon = model(X_val_normal)
            val_mse = torch.mean((X_val_normal - val_recon)**2, dim=1).cpu().numpy()
            
            # Use 95th percentile of normal validation errors
            threshold = float(np.percentile(val_mse, 95))
            
            # Evaluate on full test set
            X_test_t = torch.tensor(X_test).to(device)
            test_recon = model(X_test_t)
            test_mse = torch.mean((X_test_t - test_recon)**2, dim=1).cpu().numpy()
            test_loss = float(np.mean(test_mse))
            
        y_pred = (test_mse > threshold).astype(int)
        
        def compute_metrics(y_true, y_p, mse):
            acc = float(accuracy_score(y_true, y_p))
            prec = float(precision_score(y_true, y_p, zero_division=0))
            rec = float(recall_score(y_true, y_p, zero_division=0))
            f1 = float(f1_score(y_true, y_p, zero_division=0))
            auc = float(roc_auc_score(y_true, mse))
            pr_auc = float(average_precision_score(y_true, mse))
            
            cm = confusion_matrix(y_true, y_p).tolist()
            tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]
            fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
            fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0
            
            # Majority baseline
            y_maj = np.ones_like(y_true) # Anomalies are the majority
            maj_prec = float(precision_score(y_true, y_maj, zero_division=0))
            maj_rec = float(recall_score(y_true, y_maj, zero_division=0))
            maj_f1 = float(f1_score(y_true, y_maj, zero_division=0))
            
            return {
                "accuracy": acc, "precision": prec, "recall": rec, "f1": f1,
                "roc_auc": auc, "pr_auc": pr_auc, "fpr": fpr, "fnr": fnr,
                "confusion_matrix": cm, "majority_precision": maj_prec,
                "majority_recall": maj_rec, "majority_f1": maj_f1,
                "threshold": threshold, "threshold_source": "validation_normal"
            }
            
        metrics_original = compute_metrics(y_test, y_pred, test_mse)
        
        # Balanced diagnostic evaluation
        normal_idx = np.where(y_test == 0)[0]
        anomaly_idx = np.where(y_test == 1)[0]
        min_class_count = min(len(normal_idx), len(anomaly_idx))
        
        np.random.seed(42)
        bal_normal_idx = np.random.choice(normal_idx, min_class_count, replace=False)
        bal_anomaly_idx = np.random.choice(anomaly_idx, min_class_count, replace=False)
        balanced_idx = np.concatenate([bal_normal_idx, bal_anomaly_idx])
        
        y_test_bal = y_test[balanced_idx]
        y_pred_bal = y_pred[balanced_idx]
        test_mse_bal = test_mse[balanced_idx]
        
        metrics_balanced = compute_metrics(y_test_bal, y_pred_bal, test_mse_bal)
        
        metrics = metrics_original # Return original for Flower dashboard/history
        
        # Save metrics for this round
        metrics_file = run_path / "round_metrics.json"
        if metrics_file.exists():
            with open(metrics_file, "r") as f:
                history = json.load(f)
        else:
            history = {"rounds": {}}
            
        history["rounds"][server_round] = {
            "loss": test_loss,
            "original": metrics_original,
            "balanced_diagnostic": metrics_balanced
        }
        
        with open(metrics_file, "w") as f:
            json.dump(history, f, indent=2)
            
        csv_file = run_path / "round_metrics.csv"
        import csv
        with open(csv_file, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["round", "loss", "accuracy", "precision", "recall", "f1", "roc_auc", "pr_auc", "threshold"])
            for r, m in history["rounds"].items():
                orig = m["original"]
                writer.writerow([r, m["loss"], orig["accuracy"], orig["precision"], orig["recall"], orig["f1"], orig["roc_auc"], orig["pr_auc"], orig["threshold"]])
            
        # Save model checkpoint
        torch.save(model.state_dict(), run_path / f"global_model_round_{server_round}.pt")
        torch.save(model.state_dict(), run_path / "global_model.pt")
            
        # Flower expects dict of scalar metrics
        flower_metrics = {k: v for k, v in metrics_original.items() if isinstance(v, (int, float, bool))}
        return test_loss, flower_metrics

    return evaluate
