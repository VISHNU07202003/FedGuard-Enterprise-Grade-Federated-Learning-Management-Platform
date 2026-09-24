import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_websocket_connection():
    run_id = "test-run-123"
    with client.websocket_connect(f"/ws/training/{run_id}") as websocket:
        # Test emitting an event
        response = client.post(
            f"/api/v1/training/runs/{run_id}/events/test",
            json={"event": "training.started", "payload": {"status": "started"}}
        )
        assert response.status_code == 200
        
        # Check if the websocket received the event
        data = websocket.receive_json()
        assert data["event"] == "training.started"
        assert data["run_id"] == run_id
        assert data["payload"]["status"] == "started"

def test_websocket_ping():
    run_id = "test-run-123"
    with client.websocket_connect(f"/ws/training/{run_id}") as websocket:
        websocket.send_text("ping")
        data = websocket.receive_text()
        assert data == "pong"
