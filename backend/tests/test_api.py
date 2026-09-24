import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_current_active_user
from app.db.models import UserModel

def mock_active_user():
    return UserModel(email="admin@fedguard.dev", role="admin")

app.dependency_overrides[get_current_active_user] = mock_active_user

client = TestClient(app)

requires_db = pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"),
    reason="TEST_DATABASE_URL not configured (Requires a real database for integration testing)"
)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200

@requires_db
def test_dashboard():
    response = client.get("/api/v1/dashboard/")
    assert response.status_code == 200
    data = response.json()
    assert "kpi_metrics" in data

@requires_db
def test_clients():
    response = client.get("/api/v1/clients/")
    assert response.status_code == 200

@requires_db
def test_experiments():
    response = client.get("/api/v1/experiments/")
    assert response.status_code == 200

@requires_db
def test_training_runs():
    response = client.get("/api/v1/training/runs")
    assert response.status_code == 200
