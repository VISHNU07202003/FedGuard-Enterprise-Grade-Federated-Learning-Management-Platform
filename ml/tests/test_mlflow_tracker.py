import pytest
import os
import json
from pathlib import Path
from ml.fedguard_ml.tracking.mlflow_tracker import FedGuardMLflowTracker
import mlflow

@pytest.fixture
def mock_tracking_uri(tmp_path):
    uri = f"sqlite:///{tmp_path}/mlflow.db"
    return uri

def test_mlflow_tracker_initialization(mock_tracking_uri):
    tracker = FedGuardMLflowTracker(mock_tracking_uri, "TestExperiment", strict_mode=True)
    assert tracker.is_enabled is True
    assert tracker.tracking_uri == mock_tracking_uri

def test_mlflow_tracker_logging(mock_tracking_uri, tmp_path):
    tracker = FedGuardMLflowTracker(mock_tracking_uri, "TestExperiment", strict_mode=True)
    
    tracker.start_run(run_name="test_run", tags={"test_tag": "value"})
    
    # Log param
    tracker.log_params({"learning_rate": 0.01})
    
    # Log metric
    tracker.log_metric("accuracy", 0.95, step=1)
    
    # Log artifact
    dummy_file = tmp_path / "dummy.txt"
    dummy_file.write_text("hello")
    tracker.log_artifact(str(dummy_file))
    
    metadata = tracker.get_metadata()
    assert metadata["mlflow_run_id"] is not None
    assert metadata["experiment_name"] == "TestExperiment"
    
    tracker.end_run()

def test_mlflow_tracker_fallback_when_disabled(monkeypatch):
    def mock_set_experiment(*args, **kwargs):
        raise Exception("Connection Refused")
    
    monkeypatch.setattr(mlflow, "set_experiment", mock_set_experiment)
    
    # If MLflow was missing, it should be disabled. We can simulate by messing with the URI
    tracker = FedGuardMLflowTracker("http://localhost:9999", "TestFail", strict_mode=False)
    # It should catch the connection error and disable itself if strict_mode is False
    assert tracker.is_enabled is False
    
    # These should not crash
    tracker.start_run("test")
    tracker.log_params({"x": 1})
    tracker.log_metric("y", 2)
    tracker.end_run()

def test_mlflow_tracker_strict_mode_crash(monkeypatch):
    def mock_set_experiment(*args, **kwargs):
        raise Exception("Connection Refused")
    
    monkeypatch.setattr(mlflow, "set_experiment", mock_set_experiment)

    with pytest.raises(Exception):
        tracker = FedGuardMLflowTracker("http://localhost:9999", "TestFail", strict_mode=True)
