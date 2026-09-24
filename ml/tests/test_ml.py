import pytest
import numpy as np
import torch
from ml.fedguard_ml.data.preprocessing import ToNIoTPreprocessor
from ml.fedguard_ml.models.dense_autoencoder import DenseAutoencoder
from ml.fedguard_ml.models.transformer_autoencoder import TransformerAutoencoder
from ml.fedguard_ml.training.thresholds import calculate_threshold
from ml.fedguard_ml.data.partitioning import create_iid_partitions

def test_preprocessing():
    import pandas as pd
    
    # Mock data
    df = pd.DataFrame({
        "src_ip": ["192.168.1.1", "10.0.0.1", "192.168.1.1"],
        "src_port": [80, 443, 8080],
        "label": [0, 1, 0],
        "type": ["normal", "dos", "normal"]
    })
    
    preprocessor = ToNIoTPreprocessor()
    X, y = preprocessor.fit_transform(df)
    
    assert "src_ip" not in preprocessor.feature_names
    assert "type" not in preprocessor.feature_names
    assert "label" not in preprocessor.feature_names
    
    assert X.shape[1] == 1 # Only src_port remains as feature
    assert len(X) == 3
    
def test_partitioning():
    X = np.random.rand(100, 10)
    y = np.random.randint(0, 2, 100)
    
    parts = create_iid_partitions(X, y, num_clients=10, seed=42)
    assert len(parts) == 10
    
def test_dense_autoencoder():
    model = DenseAutoencoder(input_dim=10)
    x = torch.randn(32, 10)
    recon = model(x)
    assert recon.shape == (32, 10)
    
def test_transformer_autoencoder():
    model = TransformerAutoencoder(input_dim=10)
    x = torch.randn(32, 10)
    recon = model(x)
    assert recon.shape == (32, 10)
    
def test_thresholds():
    errors = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 1.0, 2.0])
    t = calculate_threshold(errors, method="percentile", percentile=50)
    assert np.isclose(t, 0.4)
