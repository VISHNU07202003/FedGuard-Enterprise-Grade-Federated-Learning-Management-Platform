# FedGuard

**Privacy-Preserving Federated Anomaly Detection Platform**

> Multiple simulated organizations train a shared anomaly detection model collaboratively without sharing raw training data.

---

## Architecture

```text
+--------------------------------------------------+
|                  React Frontend                  |
|               TypeScript + Vite                  |
|               Tailwind + shadcn/ui               |
+------------------------+-------------------------+
                         |
                  REST / WebSocket
                         |
+------------------------v-------------------------+
|                    FastAPI                       |
|            API / Auth / Validation               |
|                 Control Plane                    |
+---------+------------------------------+---------+
          |                              |
+---------v---------+          +---------v---------+
|    PostgreSQL     |          |      Redis        |
+-------------------+          +-------------------+

+--------------------------------------------------+
|                 Federated Layer                  |
|                 Flower + PyTorch                 |
|                 FedAvg / FedProx                 |
+--------------------------------------------------+

+--------------------------------------------------+
|                  AI Assistant                    |
|                 Amazon Bedrock                   |
|                Guardrails + RAG                  |
+--------------------------------------------------+

+--------------------------------------------------+
|                     MLOps                        |
|                     MLflow                       |
|              Prometheus + Grafana                |
+--------------------------------------------------+
```

## Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React, TypeScript, Vite, Tailwind CSS, shadcn/ui, Motion, Recharts, Lucide |
| **Backend** | Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy, PostgreSQL, Redis |
| **Federated Learning** | Flower, PyTorch, FedAvg, FedProx |
| **ML** | Transformer Autoencoder, Dense Autoencoder |
| **Dataset** | ToN-IoT (Network Traffic subset) |
| **MLOps** | MLflow |
| **AI** | Amazon Bedrock, Bedrock Guardrails, RAG |
| **Observability** | Prometheus, Grafana |
| **Infrastructure** | Docker, Docker Compose, GitHub Actions |

## Key Features

- **Federated Learning**  Collaborative model training across distributed clients
- **Privacy Preservation**  Differential privacy, secure aggregation
- **Anomaly Detection**  Transformer autoencoder for IoT/IIoT network traffic
- **Non-IID Data**  Label skew, quantity skew, feature skew partitioning
- **AI Copilot**  Bedrock-powered assistant for experiment analysis (with guardrails)
- **Real-Time Monitoring**  WebSocket-based live training updates
- **MLOps**  MLflow experiment tracking and model registry
- ✅ **Phase 10:** Privacy-Preserving Features (DP-SGD & Opacus)
- ✅ **Phase 11:** Security & Authentication (JWT & RBAC)
- ✅ **Phase 12:** AWS Bedrock AI Copilot
- ✅ **Phase 13A:** Edge Device Simulation
- ✅ **Phase 13B:** Observability (Prometheus & Grafana)
- ✅ **Phase 14:** AWS Cloud Readiness & Cost-Safe Deployment

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.12+ (for local backend development)

### Run with Docker

```bash
# Clone the repository
git clone <repo-url>
cd fedguard

# Create environment file
cp .env.example .env

# Start all services
docker compose up --build
```

### Access

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Health | http://localhost:8000/health |
| API Docs | http://localhost:8000/docs |

## Project Structure

```text
fedguard/
 frontend/          # React + TypeScript + Vite
 backend/           # FastAPI + SQLAlchemy
 federation/        # Flower federation layer
 ml/                # PyTorch models + preprocessing
 privacy/           # Differential privacy + secure aggregation
 security/          # Auth + threat detection
 monitoring/        # Prometheus + Grafana configs
 experiments/       # Experiment configs + results
 infrastructure/    # Cloud deployment configs
 tests/             # Integration tests
 docs/              # Documentation
 docker-compose.yml
 .env.example
 README.md
```

## Development Phases

| Phase | Description | Status |
|-------|------------|--------|
| 1 | Repository Foundation |  In Progress |
| 2 | UI Design System |  Planned |
| 3 | Dashboard |  Planned |
| 4 | Data + ML Pipeline |  Planned |
| 5 | Federated Learning |  Planned |
| 6 | Backend Integration |  Planned |
| 7 | WebSockets |  Planned |
| 8 | MLflow |  Planned |
| 9 | Fault Tolerance |  Planned |
| 10 | Privacy |  Planned |
| 11 | Security |  Planned |
| 12 | Bedrock AI Copilot |  Planned |
| 13 | Observability |  Planned |
| 14 | Final Docker |  Planned |
| 15 | AWS Deployment |  Planned |
| 16 | Final Polish |  Planned |

## License

This project is developed for academic and portfolio purposes.

## Disclaimer

FedGuard is a demonstration platform. Security features are experimental. Do not deploy to production without a thorough security review. All performance metrics shown are from actual experiments  none are fabricated.
