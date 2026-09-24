# FedGuard — Privacy-Preserving Federated Anomaly Detection Platform
## Antigravity Implementation Specification

> **Purpose:** Build a portfolio-grade, production-style federated machine learning platform that demonstrates Software Engineering, Distributed Systems, ML Engineering, Privacy/Security, MLOps, Cloud, and modern frontend engineering.
>
> **Important:** This is not a notebook-only academic demo. Build it as a complete software product with a polished interface, clean architecture, automated testing, observability, fault tolerance, documentation, and reproducible experiments.

---

# 1. Product Overview

## Product Name

**FedGuard**

## Product Description

FedGuard is a privacy-preserving federated anomaly detection platform.

Multiple simulated organizations/devices train a shared anomaly-detection model collaboratively without sending their raw training data to the central coordinator.

The system should demonstrate:

- Federated learning
- Distributed systems
- Non-IID data
- Differential privacy
- Secure aggregation
- Client fault tolerance
- Model poisoning detection/defense
- Model evaluation
- Experiment tracking
- Model registry
- API development
- Real-time monitoring
- Dockerized services
- CI/CD
- Modern React UI
- Cloud-ready architecture

## Primary Demonstration Scenario

Use a realistic **IoT / industrial network anomaly detection** scenario.

Each federated client represents a different organization, factory, building, or edge deployment.

Example clients:

- Smart Factory A
- Smart Factory B
- Industrial Gateway
- Smart Building
- Edge Cluster
- Data Center
- Manufacturing Line
- Sensor Network

Each client owns a different local data distribution.

Raw data must remain local to the client.

The coordinator receives model updates rather than raw training data.

---

# 2. Core Engineering Principles

These rules must be followed throughout development.

## 2.1 Separation of Concerns

Frontend:
- Presentation
- User interaction
- Client-side state
- Visualization
- API consumption

FastAPI backend:
- API layer
- Authentication/authorization
- Input validation
- Business logic
- Database access
- Training controls
- WebSocket event streaming
- Audit logging

Federated layer:
- Client/server orchestration
- Training rounds
- Aggregation
- Client participation

ML layer:
- Preprocessing
- Model definition
- Training
- Evaluation
- Inference

Privacy layer:
- Differential privacy
- Secure aggregation configuration

Security layer:
- Client identity
- Authentication
- Authorization
- Threat detection
- Audit logs

MLOps:
- Experiments
- Metrics
- Model versions
- Artifacts

Observability:
- Metrics
- Health
- Alerts
- System telemetry

## 2.2 No Fake Claims

Never hard-code impressive metrics merely for screenshots.

All performance numbers shown in the UI, README, experiments, or resume must come from actual experiments.

Examples:

- accuracy
- F1
- AUC
- round duration
- communication overhead
- number of active clients
- dropout rate
- privacy budget
- model version

## 2.3 Reproducibility

Experiments must be reproducible.

Use:

- deterministic random seeds where practical
- versioned experiment configuration
- explicit dataset preprocessing
- recorded model configuration
- recorded software version
- MLflow experiment tracking

## 2.4 Security

Never:

- expose secrets in frontend code
- expose API keys in Git
- allow unrestricted SQL generation
- trust arbitrary client input
- store credentials in source code

Use environment variables and typed configuration.

---

# 3. Recommended Technology Stack

## Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- Motion for React
- TanStack Query
- Recharts
- Lucide icons

## Backend

- Python 3.12+
- FastAPI
- Pydantic v2
- SQLAlchemy
- PostgreSQL
- Redis
- WebSockets
- Pytest

## Federated Learning

- Flower
- PyTorch
- FedAvg
- FedProx
- Secure Aggregation
- Differential Privacy

## ML/MLOps

- PyTorch
- NumPy
- Pandas
- scikit-learn
- MLflow

## Infrastructure

- Docker
- Docker Compose
- GitHub Actions
- Prometheus
- Grafana

## Cloud

- AWS-ready architecture
- Docker-first deployment
- Keep cloud-specific code isolated

---

# 4. High-Level Architecture

```text
                         ┌──────────────────────────┐
                         │      React Frontend      │
                         │ TypeScript + Vite        │
                         │ Tailwind + shadcn/ui     │
                         │ Motion + Recharts        │
                         └────────────┬─────────────┘
                                      │
                           REST + WebSocket
                                      │
                         ┌────────────▼─────────────┐
                         │        FastAPI            │
                         │ API / Auth / Validation   │
                         │ Training Control          │
                         │ WebSocket Events          │
                         └──────────┬───────┬────────┘
                                    │       │
                     ┌──────────────┘       └───────────────┐
                     │                                      │
              ┌──────▼──────┐                        ┌──────▼──────┐
              │ PostgreSQL  │                        │    Redis     │
              │ Metadata    │                        │ Cache / Jobs │
              └─────────────┘                        └─────────────┘

                              Federated Layer

                     ┌─────────────────────────┐
                     │       Flower Layer      │
                     │ SuperLink / ServerApp   │
                     └────────────┬────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
        ┌─────▼─────┐       ┌─────▼─────┐       ┌─────▼─────┐
        │ SuperNode │       │ SuperNode │       │ SuperNode │
        │ Client A  │       │ Client B  │       │ Client C  │
        └─────┬─────┘       └─────┬─────┘       └─────┬─────┘
              │                   │                   │
          Local data          Local data          Local data
              │                   │                   │
          PyTorch             PyTorch             PyTorch
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                         Secure Aggregation
                                  │
                            Global Model
                                  │
                         ┌────────▼────────┐
                         │     MLflow      │
                         │ Experiments +   │
                         │ Model Registry  │
                         └─────────────────┘

                  Observability:
                Prometheus → Grafana
```

---

# 5. Frontend Product Design

## 5.1 Design Goal

The UI must look like a modern commercial ML platform.

Reference visual quality:

- Vercel-style clean layout
- Datadog-style observability
- modern security dashboard
- modern ML experiment tooling

Do NOT create a generic Bootstrap-style dashboard.

## 5.2 Visual Language

Use a refined dark-first interface.

Recommended palette:

- Background: deep neutral/near-black
- Panels: slightly lighter neutral
- Borders: subtle gray
- Primary: blue/indigo
- Success: emerald
- Warning: amber
- Error: red
- Text: white
- Secondary text: muted gray

Do not overuse glow or neon.

The design should feel professional.

## 5.3 Typography

Use a clean modern sans-serif UI font.

Recommended:

- Inter or equivalent system-friendly sans-serif

Hierarchy:

- Large page titles
- Medium card titles
- Compact metric labels
- Small metadata text

## 5.4 Motion Philosophy

Animations must communicate state, not distract.

Use:

- subtle page enter/exit animation
- card hover elevation
- button hover scale
- button press feedback
- smooth progress transitions
- animated number counters
- skeleton loaders
- toast transitions
- client node status pulses
- chart transitions
- modal enter/exit
- sidebar collapse animation

Avoid:

- excessive parallax
- constant bouncing
- long animations
- distracting transitions

Suggested timing:

- Hover: 120–180ms
- UI transition: 180–250ms
- Page transition: 200–300ms
- Modal: 200–250ms

Provide reduced-motion support.

---

# 6. Navigation

Sidebar:

```text
FedGuard

OVERVIEW
  Dashboard

TRAINING
  Training Runs
  Rounds

FEDERATION
  Clients
  Topology

MODELS
  Model Registry
  Experiments

SECURITY
  Privacy
  Threat Detection
  Audit Logs

OBSERVABILITY
  Metrics
  System Health

SYSTEM
  Settings
```

Requirements:

- active navigation indicator
- hover state
- keyboard support
- tooltip when collapsed
- smooth collapse/expand
- responsive mobile drawer
- icons from Lucide

---

# 7. Dashboard Page

## Hero Header

Example:

```text
FedGuard
Privacy-Preserving Federated ML Platform

System Operational
```

Show:

- active clients
- current training run
- security state
- model version

## KPI Cards

Display:

```text
Active Clients       47 / 50
Global Accuracy      94.7%
F1 Score             92.4%
AUC                   0.982
Privacy Budget        ε = 3.2
Training Round        18 / 50
Model Version         v18
```

Cards must support:

- hover effect
- click-through
- subtle animation
- mini trend indicator where meaningful
- tooltips for technical metrics

## Main Dashboard Sections

1. Training overview
2. Model performance
3. Client health
4. Security events
5. Recent experiments
6. Infrastructure health

---

# 8. Training Page

## Header

```text
Federated Training

Run #2026-018
Model: Transformer Autoencoder
Strategy: FedProx
Clients: 50

[ Pause Training ] [ Stop ]
```

Buttons require confirmation for destructive operations.

## Live Training Progress

Show:

```text
ROUND 18

████████████████████░░░░░░

72%

37 / 50 clients completed
```

Update live using WebSockets.

## Metrics

Display:

- training loss
- validation loss
- accuracy
- precision
- recall
- F1
- AUC
- training duration
- communication duration
- aggregation duration

Charts should support:

- tooltip
- legend
- time/round range
- smooth transitions

---

# 9. Clients Page

Table columns:

```text
Client
Organization
Status
Samples
Accuracy
F1
Last Seen
Round
Health
```

Features:

- search
- filtering
- sorting
- pagination
- client status badges
- click into client details

Status types:

```text
Training
Uploading
Waiting
Completed
Failed
Offline
Rejected
```

Use distinct accessible status indicators.

---

# 10. Federation Topology Page

Create a visual topology.

Central coordinator:

```text
                    ┌──────────────┐
                    │ Coordinator  │
                    └───────┬──────┘
                            │
              ──────────────┼─────────────
              │      │      │      │      │
              ●      ●      ●      ●      ●
```

Each client node has:

- status
- progress
- latency
- contribution state

Node animations:

- training = pulse
- uploading = rotating/progress ring
- waiting = subtle idle state
- completed = check animation
- failed = red state
- offline = muted/gray

Click a client to open a side panel.

---

# 11. Client Detail Panel

Display:

```text
Client #27

Organization
Industrial IoT Site B

Status
Training

Dataset
Industrial Network Telemetry

Samples
183,492

Local Accuracy
91.8%

Local F1
89.4%

Training Time
14.8s

Communication Time
2.1s

Privacy
Enabled

Contribution
Accepted

Last Update
4.2 seconds ago
```

Optional actions:

- inspect metrics
- disable client
- retry
- quarantine
- view audit events

---

# 12. Privacy Page

## Differential Privacy Card

Show:

```text
Differential Privacy

Enabled

ε = 3.2
δ = 1e-5

Noise Multiplier
1.15

Clipping Norm
1.0

Budget Consumed
64%
```

Include a privacy-budget visualization.

Explain technical concepts through hover tooltips.

## Secure Aggregation Card

Show:

```text
Secure Aggregation
Enabled

Individual client updates
Hidden

Server visibility
Aggregated updates only
```

Do not claim cryptographic properties that have not actually been implemented.

---

# 13. Threat Detection Page

## Threat Types

Support experimental detection/defense for:

- model poisoning
- malformed update
- abnormal gradient
- suspicious client behavior
- unauthorized client

Example UI:

```text
Security Events

Model poisoning attempt
Client #19
HIGH
BLOCKED

Abnormal gradient
Client #31
MEDIUM
REVIEW

Unauthorized client
Client #42
LOW
REJECTED
```

Each event must have:

- timestamp
- severity
- client
- event type
- status
- explanation
- action taken

---

# 14. Audit Logs

Table:

```text
Timestamp
Actor
Action
Resource
IP / Identifier
Result
```

Examples:

- training started
- training paused
- client registered
- client rejected
- model promoted
- experiment created
- security event detected

Audit logs must be append-oriented.

---

# 15. Experiment Page

Build an experiment creation flow.

## Form

Fields:

```text
Experiment Name
Dataset
Model
Federated Strategy
Number of Clients
Rounds
Client Participation
Differential Privacy
Secure Aggregation
Random Seed
```

## Experiment Comparison

Display:

```text
Method             F1       AUC      Time

Centralized        95.2%    .991     12m
FedAvg             ...
FedProx            ...
FedProx + DP       ...
```

Every value must be generated from actual experiments.

---

# 16. Model Registry

Models should be versioned.

Example:

```text
anomaly-transformer

v18
Production
F1 94.7%
AUC 0.982

[View] [Compare] [Promote]
```

Track:

- model name
- version
- experiment
- training run
- dataset version
- metrics
- artifact
- created time
- status
- deployment state

Do not allow arbitrary direct edits of historical model records.

---

# 17. Model Architecture

Initial model:

**Transformer Autoencoder**

Pipeline:

```text
Raw telemetry
       ↓
Data validation
       ↓
Normalization
       ↓
Windowing
       ↓
Transformer Encoder
       ↓
Latent Representation
       ↓
Decoder
       ↓
Reconstruction Error
       ↓
Anomaly Score
       ↓
Threshold
       ↓
Normal / Anomaly
```

Later comparison:

- Autoencoder
- LSTM Autoencoder
- Transformer Autoencoder

---

# 18. Dataset

Use a realistic cybersecurity/IoT anomaly-detection dataset suitable for experiments.

Features can include:

```text
packet_rate
connection_duration
bytes_sent
bytes_received
protocol
source_port
destination_port
error_rate
latency
cpu_usage
memory_usage
```

Potential labels:

```text
Normal
DoS
Probe
Botnet
Port Scan
Brute Force
```

The dataset must be validated and documented.

Document:

- source
- license
- feature definitions
- preprocessing
- train/test split
- known limitations

Do not redistribute restricted datasets.

---

# 19. Federated Data Distribution

Create multiple non-IID partitioning strategies.

## IID

Randomly distribute data equally.

## Label skew

Each client receives different anomaly-class proportions.

## Quantity skew

Clients have different dataset sizes.

## Feature skew

Clients have different distributions of continuous features.

## Realistic mixed non-IID

Combine:

- label skew
- quantity skew
- feature skew

Make distribution configurable.

---

# 20. Federated Strategies

Implement initially:

- FedAvg
- FedProx

Architecture must make adding future strategies easy.

Use a strategy interface/abstraction rather than hard-coding everything into one file.

Example conceptual interface:

```python
class FederatedStrategy:
    def aggregate(...)
    def validate_update(...)
    def handle_client_dropout(...)
```

---

# 21. Differential Privacy

Implement privacy as a modular layer.

Conceptually:

```text
Local model update
       ↓
Gradient/update clipping
       ↓
Noise injection
       ↓
Secure transport
       ↓
Aggregation
```

Configuration:

```text
enabled
epsilon target / budget
delta
noise multiplier
clipping norm
```

Record privacy configuration for every training run.

Do not invent formal privacy guarantees without calculating them correctly.

---

# 22. Secure Aggregation

Integrate the selected federated framework's secure-aggregation capabilities.

Do not implement cryptographic protocols from scratch unless there is a clear engineering reason.

Expose status in UI:

```text
Secure Aggregation
Enabled / Disabled
```

Record whether the run actually used it.

---

# 23. Fault Tolerance

The system must handle:

## Client timeout

```text
Client → timeout
      ↓
Retry
      ↓
Retry fails
      ↓
Mark unavailable
      ↓
Continue round
```

## Client disconnect

Training round should continue according to configurable participation rules.

## Invalid update

Reject update.

Do not let one malformed client crash the global round.

## Slow client

Track stragglers.

Expose:

- average client time
- p95 client time
- slowest clients

## Server failure

Provide clean startup/recovery behavior.

---

# 24. Adversarial Experiments

Implement experimental attacks.

## Model Poisoning

Allow configurable malicious clients.

Possible behavior:

- send abnormal gradient/update
- distort local weights

## Backdoor Experiment

Optional later phase.

## Defense

Compare defenses such as:

- FedAvg baseline
- trimmed mean
- coordinate-wise median
- Krum / similar robust strategy

All experimental defenses must be clearly documented as research/demo features.

---

# 25. Real-Time Communication

Use FastAPI WebSockets for live UI updates.

Events could include:

```text
training.started
training.round_started
client.connected
client.training
client.uploading
client.completed
client.failed
aggregation.started
aggregation.completed
security.alert
training.completed
```

Event schema should be versioned.

Example:

```json
{
  "event": "client.completed",
  "version": 1,
  "timestamp": "...",
  "run_id": "...",
  "round": 18,
  "client_id": "client-27"
}
```

Frontend should gracefully reconnect after WebSocket failure.

---

# 26. Backend API

Suggested routes:

```text
/api/v1/auth
/api/v1/dashboard
/api/v1/training
/api/v1/runs
/api/v1/rounds
/api/v1/clients
/api/v1/federation
/api/v1/models
/api/v1/experiments
/api/v1/privacy
/api/v1/security
/api/v1/audit
/api/v1/metrics
/api/v1/health
```

Use:

- Pydantic request models
- Pydantic response models
- proper HTTP status codes
- centralized exception handling
- structured error responses

Example:

```json
{
  "error": {
    "code": "CLIENT_NOT_FOUND",
    "message": "Client client-27 was not found."
  }
}
```

---

# 27. Database Schema

Core tables:

```text
users
roles

clients
client_sessions

experiments
training_runs
training_rounds
round_clients

client_metrics
global_metrics

models
model_versions

privacy_configs

security_events
audit_logs
```

Use proper:

- foreign keys
- indexes
- unique constraints
- timestamps
- soft-delete rules where appropriate

Use migrations.

Do not modify production schema manually.

---

# 28. Redis

Use Redis for:

- short-lived cache
- WebSocket/event coordination where needed
- background task state where appropriate
- rate limiting where appropriate

Do not make Redis the source of truth for persistent business data.

PostgreSQL remains the source of truth.

---

# 29. Background Jobs

Long-running training must not block FastAPI request threads.

Use an explicit job/orchestration layer.

Conceptually:

```text
POST /training/run
        ↓
Create Training Run
        ↓
Queue / Scheduler
        ↓
Federated Training
        ↓
Persist Metrics
        ↓
Emit WebSocket Events
        ↓
MLflow Logging
        ↓
Training Complete
```

---

# 30. Observability

Use Prometheus metrics.

Application metrics:

- request count
- request latency
- error count
- active WebSocket connections

Federated metrics:

- active clients
- completed clients
- dropout rate
- round duration
- aggregation duration
- communication duration

ML metrics:

- loss
- accuracy
- precision
- recall
- F1
- AUC

Infrastructure:

- CPU
- memory
- container health

Grafana should provide infrastructure and federation dashboards.

---

# 31. Frontend State Management

Use TanStack Query for server state.

Use local React state for:

- dialogs
- filters
- temporary UI state
- navigation state

Avoid introducing a global state library unless the application actually needs one.

Implement hooks such as:

```text
useTrainingRuns()
useTrainingRun()
useClients()
useClient()
useMetrics()
useModels()
useExperiments()
useSecurityEvents()
useWebSocket()
```

---

# 32. Component Architecture

Frontend:

```text
frontend/
└── src/
    ├── app/
    │   ├── router.tsx
    │   ├── providers.tsx
    │   └── layout.tsx
    │
    ├── components/
    │   ├── ui/
    │   ├── charts/
    │   ├── metrics/
    │   ├── federation/
    │   ├── training/
    │   ├── security/
    │   └── models/
    │
    ├── features/
    │   ├── dashboard/
    │   ├── training/
    │   ├── clients/
    │   ├── experiments/
    │   ├── models/
    │   ├── security/
    │   └── monitoring/
    │
    ├── hooks/
    ├── lib/
    ├── types/
    └── styles/
```

Keep reusable UI components separate from domain-specific features.

---

# 33. Backend Architecture

```text
backend/
└── app/
    ├── main.py
    │
    ├── api/
    │   ├── routes/
    │   │   ├── auth.py
    │   │   ├── training.py
    │   │   ├── clients.py
    │   │   ├── experiments.py
    │   │   ├── models.py
    │   │   ├── security.py
    │   │   └── metrics.py
    │   │
    │   └── websocket.py
    │
    ├── core/
    │   ├── config.py
    │   ├── security.py
    │   ├── logging.py
    │   └── exceptions.py
    │
    ├── db/
    │   ├── models.py
    │   ├── session.py
    │   ├── migrations/
    │   └── repositories/
    │
    ├── services/
    │   ├── training_service.py
    │   ├── client_service.py
    │   ├── experiment_service.py
    │   ├── model_service.py
    │   └── security_service.py
    │
    ├── federation/
    │   ├── server.py
    │   ├── strategy.py
    │   ├── orchestration.py
    │   └── events.py
    │
    ├── ml/
    │   ├── models/
    │   ├── preprocessing/
    │   ├── training/
    │   └── evaluation/
    │
    ├── privacy/
    │   ├── differential_privacy.py
    │   └── secure_aggregation.py
    │
    └── monitoring/
        ├── metrics.py
        └── prometheus.py
```

---

# 34. Project Repository

Final repository:

```text
fedguard/
├── frontend/
├── backend/
├── federation/
├── ml/
├── privacy/
├── security/
├── monitoring/
├── experiments/
├── infrastructure/
├── tests/
├── docs/
│
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── pyproject.toml
├── README.md
├── architecture.md
└── .github/
    └── workflows/
        └── ci.yml
```

---

# 35. Docker Compose

Local development should include:

```text
frontend
backend
postgres
redis
mlflow
flower-superlink
flower-supernode-1
flower-supernode-2
flower-supernode-3
prometheus
grafana
```

Target command:

```bash
docker compose up --build
```

A clean clone should be able to run using documented commands.

---

# 36. Configuration

Create:

```text
.env.example
```

Include placeholders for:

```text
DATABASE_URL=
REDIS_URL=

MLFLOW_TRACKING_URI=

FLOWER_CONFIG=

JWT_SECRET=
```

Never commit real credentials.

Use Pydantic Settings.

---

# 37. Authentication

Build application authentication separately from federated client identity.

Application users:

```text
User
 ↓
Login
 ↓
JWT/session
 ↓
React
 ↓
FastAPI
```

Federated client identity should use a separate mechanism.

Roles:

```text
Admin
Researcher
Viewer
```

Basic permissions:

Admin:
- manage clients
- manage training
- manage models
- security controls

Researcher:
- run experiments
- view training
- inspect metrics

Viewer:
- view dashboards
- view experiments
- no mutations

---

# 38. Testing Strategy

## Unit Testing

Test:

```text
model
preprocessing
aggregation
privacy
validation
security
services
```

## API Testing

Test:

```text
auth
training
clients
models
experiments
security
metrics
```

## Integration Testing

Test:

```text
client → federated server → aggregation
```

## Failure Testing

Explicitly test:

- client timeout
- client disconnect
- invalid update
- server restart
- database unavailable
- Redis unavailable
- WebSocket disconnect
- malformed request

## Frontend Testing

Test:

- dashboard rendering
- loading states
- empty states
- training controls
- filtering
- client detail
- experiment comparison
- security alerts

---

# 39. CI/CD

GitHub Actions pipeline:

```text
Push / Pull Request
        ↓
Lint
        ↓
Type Check
        ↓
Unit Tests
        ↓
Integration Tests
        ↓
Frontend Build
        ↓
Docker Build
        ↓
Security Scan
        ↓
Deploy-ready artifact
```

Do not allow merges when required tests fail.

---

# 40. Security Requirements

Implement:

- secret management through environment variables
- authentication
- authorization
- request validation
- rate limiting
- CORS configuration
- secure headers
- structured audit logging
- client identity validation
- safe error responses
- dependency security scanning

Do not expose stack traces to end users.

---

# 41. Accessibility

The UI must support:

- keyboard navigation
- visible focus states
- semantic buttons
- accessible dialogs
- ARIA labels where necessary
- color + icon/text for statuses
- reduced-motion preference
- adequate contrast

Do not communicate state using color alone.

---

# 42. Responsive Design

Desktop is primary.

Must also support:

- tablet
- mobile

Mobile behavior:

- sidebar becomes drawer
- tables become scrollable or cards
- multi-column KPI grids stack
- charts resize
- dialogs fit viewport

---

# 43. Empty / Loading / Error States

Every page needs all three.

Example:

Loading:

```text
Skeleton dashboard
```

Empty:

```text
No training runs yet.

Create your first federated experiment.
[Create Experiment]
```

Error:

```text
Unable to load training data.

[Retry]
```

Never show blank white pages.

---

# 44. Toast / Notification System

Use toasts for:

- training started
- training paused
- training stopped
- client rejected
- experiment created
- model promoted
- security event

Avoid toast spam.

---

# 45. Experiment Plan

The application must support generating real comparative experiments.

## Experiment 1

Centralized vs Federated

## Experiment 2

IID vs Non-IID

## Experiment 3

FedAvg vs FedProx

## Experiment 4

No DP vs Differential Privacy

## Experiment 5

No Secure Aggregation vs Secure Aggregation

## Experiment 6

Client Dropout

Run with:

```text
0%
10%
20%
30%
```

## Experiment 7

Poisoned Clients

Compare:

```text
normal federation
poisoned federation
robust aggregation
```

---

# 46. Metrics to Collect

For every training run:

```text
run_id
model_version
strategy
client_count
participating_clients
round_count

accuracy
precision
recall
f1
auc

training_loss
validation_loss

round_duration
training_duration
communication_duration
aggregation_duration

dropout_rate

privacy_enabled
epsilon
delta

secure_aggregation_enabled
```

---

# 47. Data and Model Versioning

Every result must be traceable to:

```text
Dataset Version
Model Version
Experiment
Training Run
Round
Strategy
Privacy Configuration
```

This creates reproducibility and provenance.

---

# 48. README Requirements

The README must include:

1. Product overview
2. Key features
3. Screenshots
4. Architecture diagram
5. Technology stack
6. Federated learning explanation
7. Privacy/security explanation
8. Experimental methodology
9. Actual experiment results
10. Installation
11. Docker instructions
12. API documentation
13. Testing
14. Limitations
15. Future work
16. Disclaimer

Do not use exaggerated claims such as "zero hallucinations" or "military-grade security."

---

# 49. Documentation

Create:

```text
docs/
├── ARCHITECTURE.md
├── API.md
├── FEDERATED_LEARNING.md
├── PRIVACY.md
├── SECURITY.md
├── EXPERIMENTS.md
├── DEPLOYMENT.md
├── TESTING.md
├── TROUBLESHOOTING.md
└── UI_DESIGN.md
```

---

# 50. Development Phases

## Phase 1 — Repository Foundation

Tasks:

- create repository
- frontend scaffold
- backend scaffold
- Docker setup
- PostgreSQL
- Redis
- environment configuration
- health endpoint
- initial CI

Definition of Done:

- clean clone
- one-command local startup
- health check works
- frontend loads
- backend loads

---

## Phase 2 — UI Design System

Build first:

- application shell
- sidebar
- top bar
- buttons
- cards
- badges
- dialogs
- tables
- charts
- tooltips
- toasts
- skeleton loaders

Implement:

- dark theme
- hover animations
- transitions
- focus states
- responsive behavior

Use mocked data at this phase.

Definition of Done:

Every major UI screen can be navigated with realistic mock data.

---

## Phase 3 — Dashboard

Implement:

- KPI cards
- performance charts
- training overview
- client health
- security events
- recent experiments
- system health

Definition of Done:

Dashboard looks production-ready with no backend dependency beyond mocked service layer.

---

## Phase 4 — ML Pipeline

Implement:

- dataset loader
- validation
- preprocessing
- partitioning
- Transformer Autoencoder
- local training
- local evaluation
- anomaly scoring

Definition of Done:

A standalone local client can train and evaluate successfully.

---

## Phase 5 — Federated Layer

Implement:

- Flower integration
- ServerApp
- ClientApp
- federation configuration
- FedAvg
- FedProx
- round metrics
- client participation

Definition of Done:

Multiple clients can train collaboratively and produce a global model.

---

## Phase 6 — Backend Integration

Connect:

- training service
- database
- training runs
- rounds
- metrics
- clients
- experiments
- model registry

Definition of Done:

Dashboard reflects actual federated-training state.

---

## Phase 7 — WebSockets

Implement:

- event publisher
- event schema
- WebSocket API
- frontend subscription
- reconnection
- live UI updates

Definition of Done:

Training progress is visible live without page refresh.

---

## Phase 8 — Privacy

Implement:

- differential privacy
- privacy configuration
- secure aggregation integration
- privacy metrics

Definition of Done:

Training can be run with privacy enabled or disabled and results clearly record which mode was used.

---

## Phase 9 — Fault Tolerance

Implement:

- timeouts
- retries
- client dropout
- invalid update handling
- straggler handling
- health checks

Definition of Done:

Individual client failures do not crash the federation.

---

## Phase 10 — Security

Implement:

- authentication
- role-based authorization
- client identity
- audit events
- rate limiting
- secure configuration
- poisoning experiments/defenses

Definition of Done:

Security-sensitive endpoints are protected and all major mutations are auditable.

---

## Phase 11 — MLOps

Implement:

- MLflow experiments
- metrics
- artifacts
- model versions
- model registry

Definition of Done:

Every experiment and model can be traced.

---

## Phase 12 — Observability

Implement:

- Prometheus
- Grafana
- API metrics
- federation metrics
- infrastructure health

Definition of Done:

System behavior can be diagnosed without reading application logs manually.

---

## Phase 13 — Testing

Build:

- unit tests
- API tests
- integration tests
- frontend tests
- failure tests

Target:

> Strong meaningful coverage, not a vanity percentage.

Focus especially on critical paths.

---

## Phase 14 — Experiments

Run actual benchmark suite:

- centralized
- FedAvg
- FedProx
- IID
- non-IID
- DP
- secure aggregation
- dropout
- poisoning

Automatically save results.

---

## Phase 15 — Cloud Deployment

Start from Docker.

Then deploy a practical AWS architecture.

Do not introduce unnecessary cloud complexity before local functionality is stable.

---

## Phase 16 — Final Polish

Perform:

- UI polish
- animation review
- accessibility review
- responsive review
- security review
- performance review
- documentation review
- README screenshots
- architecture diagram
- demo video

---

# 51. Definition of Done for the Entire Project

The project is complete only when:

- frontend and backend are cleanly separated
- application starts from documented commands
- federated learning runs successfully
- multiple clients participate
- non-IID experiments work
- FedAvg and FedProx work
- differential privacy works
- secure aggregation works
- client failures are handled
- malicious-client experiment exists
- models are tracked with MLflow
- metrics are stored
- WebSocket updates work
- dashboards show real data
- authentication exists
- important actions are audited
- automated tests pass
- CI passes
- Docker build works
- documentation is complete
- no secrets are committed
- no fake performance claims exist

---

# 52. Important Scope Control

Do NOT add these during the first MVP:

- autonomous vehicles
- traffic prediction
- reinforcement learning
- V2X
- digital twins
- computer vision
- LLM agents
- blockchain
- unnecessary microservices

The product should remain focused on:

**Federated Anomaly Detection + Privacy + Distributed Systems + Security + MLOps.**

---

# 53. Suggested MVP Cut Line

If the project starts becoming too large, stop at:

```text
React UI
+
FastAPI
+
PostgreSQL
+
Flower
+
PyTorch
+
FedAvg
+
FedProx
+
Non-IID data
+
Differential Privacy
+
Secure Aggregation
+
MLflow
+
Docker
+
WebSockets
+
Tests
```

Then add security/poisoning/monitoring/cloud as advanced phases.

---

# 54. Antigravity Execution Rules

When implementing:

1. Inspect the repository before creating files.
2. Do not overwrite existing user work without checking it first.
3. Create small, logical commits/steps.
4. Keep modules focused.
5. Use typed interfaces.
6. Avoid giant files.
7. Avoid duplicated business logic.
8. Write tests with each major feature.
9. Run the application frequently.
10. Run tests before moving to the next phase.
11. Update documentation as architecture changes.
12. Never invent metrics.
13. Never commit secrets.
14. Prefer simple architecture over premature microservices.
15. Keep the application runnable after every major phase.
16. Do not sacrifice accessibility for visual effects.
17. Animations must remain subtle and fast.
18. Use real API responses and real database records once backend integration begins.
19. Keep demo/mock data isolated from production data paths.
20. Clearly label experimental security features.

---

# 55. First Implementation Task

Start with **Phase 1 only**.

Create the initial repository architecture:

```text
fedguard/
├── frontend/
├── backend/
├── docs/
├── tests/
├── infrastructure/
├── experiments/
├── docker-compose.yml
├── .env.example
├── README.md
└── .github/workflows/ci.yml
```

Then:

1. Initialize React + TypeScript + Vite.
2. Initialize FastAPI.
3. Add PostgreSQL.
4. Add Redis.
5. Add Docker Compose.
6. Add health endpoints.
7. Add basic frontend shell.
8. Add environment configuration.
9. Add basic CI.
10. Verify one-command startup.

Do not implement the ML model yet.

The next phase begins only after the foundation is stable.

---

# 56. First UI Mock Data

Before backend integration, create realistic mock data.

Example:

```json
{
  "activeClients": 47,
  "totalClients": 50,
  "accuracy": 0.947,
  "f1": 0.924,
  "auc": 0.982,
  "privacyBudget": 3.2,
  "currentRound": 18,
  "totalRounds": 50
}
```

Clearly isolate this mock layer so it can later be replaced with API data.

---

# 57. Product Quality Goal

The final product should pass the following mental test:

> "If this GitHub repository were shown to a software engineering interviewer, it should look like a thoughtfully engineered distributed ML product rather than a classroom federated-learning assignment."

Prioritize:

**Architecture > correctness > reliability > testability > observability > polish.**

A beautiful dashboard is valuable, but the underlying engineering must be equally strong.

---

# 58. Final Portfolio Positioning

The final FedGuard portfolio story should be:

> Built a production-style privacy-preserving federated learning platform that coordinates distributed anomaly-detection training across heterogeneous clients while supporting differential privacy, secure aggregation, fault tolerance, experiment tracking, model versioning, real-time monitoring, and modern web-based operations.

Only make this claim after the corresponding functionality actually exists.

---

# 59. Final Resume-Relevant Technology List

Once implemented, potential resume technologies are:

```text
Python
PyTorch
Flower
FastAPI
React
TypeScript
PostgreSQL
Redis
Docker
MLflow
Prometheus
Grafana
WebSockets
GitHub Actions
Differential Privacy
Secure Aggregation
Federated Learning
FedAvg
FedProx
Distributed Systems
MLOps
REST APIs
```

Only list technologies that were genuinely used.

---

# 60. Start Here

**Immediate task for Antigravity:**

Implement **Phase 1 — Repository Foundation** and stop after verifying:

```bash
docker compose up --build
```

works successfully.

Then implement **Phase 2 — UI Design System** before introducing the ML pipeline.

The frontend should already look excellent before real training data is connected.

