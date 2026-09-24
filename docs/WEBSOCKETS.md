# WebSocket Infrastructure

This document outlines the real-time WebSocket architecture for FedGuard Phase 7.

## Endpoint
- **URL**: `/ws/training/{run_id}`
- **Protocol**: WebSocket

## Event Schema
All events sent from the server adhere to the following schema:
```json
{
  "event": "training.started",
  "version": 1,
  "timestamp": "2026-09-13T21:00:00Z",
  "run_id": "run-018",
  "round": 3,
  "client_id": "client_004",
  "payload": {
    "status": "started"
  }
}
```

### Supported Event Types
- `training.started`
- `round.started`
- `client.training`
- `client.completed`
- `client.failed`
- `aggregation.started`
- `aggregation.completed`
- `metrics.updated`
- `training.completed`
- `error`

## Reconnect Behavior
The frontend uses the `useTrainingWebSocket` React hook. It automatically attempts to reconnect using a backoff timer (defaulting to 5 seconds) when a connection drops.

## Limitations
- State is managed strictly in memory on a single backend instance (`ConnectionManager`). Scaling to multiple backend nodes will require Redis Pub/Sub integration.
- Connection is currently unauthenticated.
