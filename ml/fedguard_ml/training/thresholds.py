import numpy as np
import torch
import json
from pathlib import Path

def calculate_threshold(reconstruction_errors, method="percentile", percentile=95.0, factor=3.0, val_labels=None, val_errors=None):
    """
    Calculate an anomaly detection threshold based on reconstruction errors.
    """
    if method == "percentile":
        return float(np.percentile(reconstruction_errors, percentile))
    elif method == "std_dev":
        mean = np.mean(reconstruction_errors)
        std = np.std(reconstruction_errors)
        return float(mean + (factor * std))
    elif method == "max":
        return float(np.max(reconstruction_errors))
    elif method == "f1_optimal":
        if val_labels is None or val_errors is None:
            raise ValueError("f1_optimal requires validation labels and validation errors.")
        from sklearn.metrics import f1_score
        best_f1 = 0
        best_threshold = 0
        # Sweep from min to max error in 100 steps
        min_err = np.min(val_errors)
        max_err = np.max(val_errors)
        for t in np.linspace(min_err, max_err, 100):
            preds = (val_errors > t).astype(int)
            f1 = f1_score(val_labels, preds, zero_division=0)
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = t
        return float(best_threshold)
    else:
        raise ValueError(f"Unknown threshold method: {method}")

def save_threshold(threshold_val, path):
    with open(path, "w") as f:
        json.dump({"threshold": threshold_val}, f, indent=2)

def load_threshold(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data["threshold"]
