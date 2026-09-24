"""Prometheus metrics definition for the backend."""
from prometheus_client import Counter, Histogram, Gauge

# ==========================================
# API Metrics
# ==========================================
API_REQUESTS = Counter(
    "fedguard_api_requests_total",
    "Total API requests",
    ["method", "route", "status_code"]
)
API_DURATION = Histogram(
    "fedguard_api_request_duration_seconds",
    "API request duration",
    ["method", "route", "status_code"]
)
API_ERRORS = Counter(
    "fedguard_api_errors_total",
    "Total API errors",
    ["method", "route", "status_code"]
)
API_ACTIVE_REQUESTS = Gauge(
    "fedguard_api_active_requests",
    "Number of active API requests",
    ["method", "route"]
)

# ==========================================
# Database Metrics
# ==========================================
DB_READY = Gauge(
    "fedguard_db_ready",
    "Database connection readiness (1=ready, 0=not ready)"
)
DB_DURATION = Histogram(
    "fedguard_db_query_duration_seconds",
    "Database query duration",
    ["operation"]
)
DB_ERRORS = Counter(
    "fedguard_db_errors_total",
    "Total database errors",
    ["operation"]
)

# ==========================================
# WebSocket Metrics
# ==========================================
WS_ACTIVE_CONNECTIONS = Gauge(
    "fedguard_ws_active_connections",
    "Number of active WebSocket connections"
)
WS_MESSAGES_SENT = Counter(
    "fedguard_ws_messages_sent_total",
    "Total WebSocket messages sent",
    ["event_type"]
)
WS_DISCONNECTS = Counter(
    "fedguard_ws_disconnects_total",
    "Total WebSocket disconnections"
)
WS_EVENT_EMIT_DURATION = Histogram(
    "fedguard_ws_event_emit_duration_seconds",
    "Duration to emit WS events",
    ["event_type"]
)

# ==========================================
# Copilot Metrics
# ==========================================
COPILOT_REQUESTS = Counter(
    "fedguard_copilot_requests_total",
    "Total Copilot requests",
    ["mode", "result"]
)
COPILOT_DURATION = Histogram(
    "fedguard_copilot_response_duration_seconds",
    "Copilot response duration",
    ["mode"]
)
COPILOT_GUARDRAIL_BLOCKS = Counter(
    "fedguard_copilot_guardrail_blocks_total",
    "Total Copilot responses blocked by guardrails",
    ["mode"]
)

# ==========================================
# Auth/Security Metrics
# ==========================================
AUTH_LOGINS = Counter(
    "fedguard_auth_logins_total",
    "Total successful logins",
    ["role"]
)
AUTH_LOGIN_FAILURES = Counter(
    "fedguard_auth_login_failures_total",
    "Total login failures"
)
RBAC_DENIALS = Counter(
    "fedguard_rbac_denials_total",
    "Total RBAC access denials",
    ["role"]
)
SECURITY_EVENTS = Counter(
    "fedguard_security_events_total",
    "Total security events logged",
    ["event_type", "severity"]
)
