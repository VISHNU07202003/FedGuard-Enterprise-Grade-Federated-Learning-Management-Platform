# Observability in FedGuard

FedGuard uses Prometheus for time-series metrics collection and Grafana for visual dashboards.

## What Prometheus Monitors
Prometheus scrapes the `/metrics` endpoints across our microservices (FastAPI backend, ML edge simulation servers). It monitors operational system health, including:
- **API Performance:** Latencies, request rates, status codes.
- **WebSocket Activity:** Active connections, emit latencies.
- **Federation Pipeline Health:** Round pass/fail rates, edge dropouts, and stragglers.
- **Privacy Budgeting:** DP-SGD noise and epsilon consumption.

## What is NOT monitored
Prometheus does NOT store:
- User emails, JWT tokens, IP addresses, or secrets.
- Full LLM query prompts (for Copilot).
- High-cardinality values like individual `client_id`s in massive runs, except for specific edge simulation demographics.
- Raw model tensors or datasets.

## MLflow vs Prometheus
**MLflow:** Experiment tracking, model lineage, hyperparameter comparisons across epochs.
**Prometheus/Grafana:** Live system health, API responsiveness, active hardware faults, security monitoring.

## Local Docker Setup
To run the full stack:
```bash
docker compose up -d
```
- **Backend Metrics:** `http://localhost:8000/metrics`
- **Prometheus:** `http://localhost:9090`
- **Grafana:** `http://localhost:3000` (Default: `admin`/`admin`)
