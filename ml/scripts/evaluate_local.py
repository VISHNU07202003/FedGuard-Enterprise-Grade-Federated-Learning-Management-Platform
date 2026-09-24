import argparse
import json
import torch
import numpy as np
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

from ml.fedguard_ml.models.dense_autoencoder import DenseAutoencoder
from ml.fedguard_ml.models.transformer_autoencoder import TransformerAutoencoder
from ml.fedguard_ml.training.thresholds import load_threshold

ML_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ML_DIR / "data" / "processed"
RUNS_DIR = ML_DIR / "runs"

def get_model(model_name, input_dim):
    if model_name == "dense":
        return DenseAutoencoder(input_dim)
    elif model_name == "transformer":
        return TransformerAutoencoder(input_dim)
    else:
        raise ValueError(f"Unknown model: {model_name}")

def evaluate():
    parser = argparse.ArgumentParser(description="Evaluate a local FedGuard model")
    parser.add_argument("--run-id", type=str, required=True, help="Run ID folder name inside ml/runs/")
    args = parser.parse_args()
    
    run_path = RUNS_DIR / args.run_id
    if not run_path.exists():
        print(f"ERROR: Run path {run_path} does not exist.")
        return
        
    print(f"Loading configuration from {run_path}")
    with open(run_path / "config.json", "r") as f:
        config = json.load(f)
        
    input_dim = config["input_dim"]
    model_name = config["model"]
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = get_model(model_name, input_dim).to(device)
    model.load_state_dict(torch.load(run_path / "model.pt", map_location=device))
    model.eval()
    
    threshold = load_threshold(run_path / "threshold.json")
    print(f"Using threshold: {threshold:.6f}")
    
    print("Loading test data...")
    X_test = np.load(PROCESSED_DIR / "X_test.npy")
    y_test = np.load(PROCESSED_DIR / "y_test.npy")
    
    X_test_tensor = torch.tensor(X_test).to(device)
    
    print("Generating predictions...")
    with torch.no_grad():
        mse = model.get_reconstruction_error(X_test_tensor).cpu().numpy()
        
    # Anomaly detection: MSE > threshold => Anomaly (1), else Normal (0)
    y_pred = (mse > threshold).astype(int)
    
    # Metrics
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    auc = roc_auc_score(y_test, mse) # AUC uses continuous anomaly scores
    
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
    
    # Baseline: Majority Class (Normal is 0, Anomaly is 1)
    # The ToN-IoT dataset is heavily skewed to anomalies in this subset (160k vs 50k)
    majority_class = int(np.bincount(y_test.astype(int)).argmax())
    y_pred_maj = np.full_like(y_test, majority_class)
    
    # Baseline: Random Guess (50/50)
    np.random.seed(42)
    y_pred_rand = np.random.randint(0, 2, size=len(y_test))
    
    # Calculate baseline metrics
    acc_maj = accuracy_score(y_test, y_pred_maj)
    f1_maj = f1_score(y_test, y_pred_maj, zero_division=0)
    
    acc_rand = accuracy_score(y_test, y_pred_rand)
    f1_rand = f1_score(y_test, y_pred_rand, zero_division=0)
    
    report = {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "auc": auc,
        "false_positive_rate": fpr,
        "false_negative_rate": fnr,
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp)
        },
        "baselines": {
            "majority_class": {"accuracy": acc_maj, "f1": f1_maj},
            "random": {"accuracy": acc_rand, "f1": f1_rand}
        }
    }
    
    with open(run_path / "evaluation_report.json", "w") as f:
        json.dump(report, f, indent=2)
        
    md_content = f"""# Evaluation Report: {args.run_id}

## Model
- **Type:** {model_name}
- **Threshold:** {threshold:.6f}

## Metrics
- **Accuracy:** {acc:.4f}
- **Precision:** {prec:.4f}
- **Recall:** {rec:.4f}
- **F1 Score:** {f1:.4f}
- **AUC-ROC:** {auc:.4f}
- **False Positive Rate:** {fpr:.4f}
- **False Negative Rate:** {fnr:.4f}

## Baselines
- **Majority-Class Accuracy:** {acc_maj:.4f}
- **Majority-Class F1:** {f1_maj:.4f}
- **Random Accuracy:** {acc_rand:.4f}
- **Random F1:** {f1_rand:.4f}

## Confusion Matrix
| | Predicted Normal | Predicted Anomaly |
|-|------------------|-------------------|
| **Actual Normal** | {tn} | {fp} |
| **Actual Anomaly** | {fn} | {tp} |

"""
    with open(run_path / "evaluation_report.md", "w") as f:
        f.write(md_content)
        
    print("\nEvaluation Results:")
    print(f"Accuracy: {acc:.4f} (Maj: {acc_maj:.4f}, Rand: {acc_rand:.4f})")
    print(f"F1 Score: {f1:.4f} (Maj: {f1_maj:.4f}, Rand: {f1_rand:.4f})")
    print(f"AUC-ROC:  {auc:.4f}")
    print(f"\nReport saved to {run_path}/evaluation_report.md")

if __name__ == "__main__":
    evaluate()
