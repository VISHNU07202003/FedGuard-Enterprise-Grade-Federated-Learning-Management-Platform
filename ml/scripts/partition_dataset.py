import numpy as np
from pathlib import Path
from ml.fedguard_ml.data.partitioning import (
    create_iid_partitions, 
    create_label_skew_partitions,
    create_quantity_skew_partitions,
    save_partitions
)

ML_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ML_DIR / "data" / "processed"
PARTITIONS_DIR = ML_DIR / "data" / "partitions"

def run_partitioning():
    print("Loading preprocessed training data...")
    X_train = np.load(PROCESSED_DIR / "X_train.npy")
    y_train = np.load(PROCESSED_DIR / "y_train.npy")
    
    num_clients = 10
    seed = 42
    
    print(f"Generating IID partitions for {num_clients} clients...")
    iid_parts = create_iid_partitions(X_train, y_train, num_clients, seed)
    save_partitions(X_train, y_train, iid_parts, PARTITIONS_DIR, "iid")
    
    print(f"Generating Label-Skew partitions for {num_clients} clients...")
    label_skew_parts = create_label_skew_partitions(X_train, y_train, num_clients, seed)
    save_partitions(X_train, y_train, label_skew_parts, PARTITIONS_DIR, "label_skew")
    
    print(f"Generating Quantity-Skew partitions for {num_clients} clients...")
    qty_skew_parts = create_quantity_skew_partitions(X_train, y_train, num_clients, seed)
    save_partitions(X_train, y_train, qty_skew_parts, PARTITIONS_DIR, "quantity_skew")
    
    print("Partitioning complete. Check ml/data/partitions/ for reports.")

if __name__ == "__main__":
    run_partitioning()
