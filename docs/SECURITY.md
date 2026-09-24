# FedGuard Security

## Overview
FedGuard implements Application-Level security separating **Application Users** (dashboard operators) and **Federated Clients** (training nodes).

## Role-Based Access Control (RBAC)
Dashboard users are assigned one of three roles:
- **Admin**: Can ingest runs, start/stop runs, quarantine clients.
- **Researcher**: Can create experiments and start runs.
- **Viewer**: Read-only access to metrics, topology, and dashboards.

## Audit Logging
All critical mutation actions are logged in the \udit_logs\ PostgreSQL table. This includes:
- Logins
- Run Ingestions
- Client Quarantine actions

## Federated Identity
The groundwork for Client API Keys has been added (\client_api_keys\ table). Future phases will strictly validate these keys before accepting FL updates.

