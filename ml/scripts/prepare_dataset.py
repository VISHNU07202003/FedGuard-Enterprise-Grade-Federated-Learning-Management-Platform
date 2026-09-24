import pandas as pd
import numpy as np
import json
from pathlib import Path
from sklearn.model_selection import train_test_split
from ml.fedguard_ml.data.preprocessing import ToNIoTPreprocessor

# Paths
ML_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ML_DIR / "data"
RAW_FILE = DATA_DIR / "Train_Test_Network.csv"
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_DIR.mkdir(exist_ok=True, parents=True)

def prepare():
    print(f"Loading raw dataset from {RAW_FILE}...")
    df = pd.read_csv(RAW_FILE)
    
    print("Splitting into train/val/test (70/15/15)...")
    # Stratify by label to maintain normal/anomaly ratio
    train_df, temp_df = train_test_split(df, test_size=0.3, stratify=df['label'], random_state=42)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, stratify=temp_df['label'], random_state=42)
    
    print(f"Train size: {len(train_df)}")
    print(f"Val size: {len(val_df)}")
    print(f"Test size: {len(test_df)}")
    
    print("Fitting preprocessor on training data...")
    preprocessor = ToNIoTPreprocessor()
    X_train, y_train = preprocessor.fit_transform(train_df)
    
    print("Transforming validation and test data...")
    X_val, y_val = preprocessor.transform(val_df)
    X_test, y_test = preprocessor.transform(test_df)
    
    print("Saving processed arrays to disk...")
    np.save(PROCESSED_DIR / "X_train.npy", X_train)
    np.save(PROCESSED_DIR / "y_train.npy", y_train)
    np.save(PROCESSED_DIR / "X_val.npy", X_val)
    np.save(PROCESSED_DIR / "y_val.npy", y_val)
    np.save(PROCESSED_DIR / "X_test.npy", X_test)
    np.save(PROCESSED_DIR / "y_test.npy", y_test)
    
    print("Saving preprocessor state...")
    preprocessor.save(PROCESSED_DIR / "preprocessor.joblib")
    
    # Save metadata
    metadata = {
        "num_features": X_train.shape[1],
        "feature_names": preprocessor.feature_names,
        "train_samples": len(X_train),
        "val_samples": len(X_val),
        "test_samples": len(X_test)
    }
    
    with open(PROCESSED_DIR / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
        
    print("Preparation complete.")

if __name__ == "__main__":
    prepare()
