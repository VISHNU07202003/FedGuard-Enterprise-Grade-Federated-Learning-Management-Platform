"""Prometheus metrics definition for the Federation ML simulation."""
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# ==========================================
# Federation Metrics
# ==========================================
FEDERATION_RUNS = Counter(
    "fedguard_federation_runs_total",
    "Total federation training runs started",
    ["strategy", "model_type", "partition_type"]
)
FEDERATION_ROUNDS = Counter(
    "fedguard_federation_rounds_total",
    "Total federation training rounds executed",
    ["strategy", "model_type"]
)
CLIENTS_SELECTED = Counter(
    "fedguard_federation_clients_selected",
    "Total clients selected across rounds",
    ["strategy", "model_type"]
)
CLIENTS_COMPLETED = Counter(
    "fedguard_federation_clients_completed",
    "Total clients that completed training",
    ["strategy", "model_type"]
)
CLIENTS_FAILED = Counter(
    "fedguard_federation_clients_failed",
    "Total clients that failed with errors",
    ["strategy", "model_type"]
)
CLIENTS_REJECTED = Counter(
    "fedguard_federation_clients_rejected",
    "Total clients rejected (e.g. invalid tensors)",
    ["strategy", "model_type"]
)
CLIENTS_TIMED_OUT = Counter(
    "fedguard_federation_clients_timed_out",
    "Total clients that timed out",
    ["strategy", "model_type"]
)
ROUND_DURATION = Histogram(
    "fedguard_federation_round_duration_seconds",
    "Duration of federation rounds",
    ["strategy", "model_type"]
)
COMPLETION_RATE = Gauge(
    "fedguard_federation_completion_rate",
    "Ratio of completed to selected clients in the latest round",
    ["strategy", "model_type"]
)

# ==========================================
# Fault-Tolerance Metrics
# ==========================================
FAULT_DROPOUTS = Counter(
    "fedguard_fault_dropouts_total",
    "Total client dropouts",
    ["fault_type", "strategy", "model_type"]
)
FAULT_REJECTIONS = Counter(
    "fedguard_fault_rejections_total",
    "Total client rejections",
    ["fault_type", "strategy", "model_type"]
)
FAULT_TIMEOUTS = Counter(
    "fedguard_fault_timeouts_total",
    "Total client timeouts",
    ["fault_type", "strategy", "model_type"]
)
FAULT_STRAGGLERS = Counter(
    "fedguard_fault_stragglers_total",
    "Total straggling clients",
    ["fault_type", "strategy", "model_type"]
)
FAULT_PARTIAL_ROUNDS = Counter(
    "fedguard_fault_partial_rounds_total",
    "Rounds completed with partial success",
    ["fault_type", "strategy", "model_type"]
)
FAULT_FAILED_ROUNDS = Counter(
    "fedguard_fault_failed_rounds_total",
    "Rounds that failed completely",
    ["fault_type", "strategy", "model_type"]
)

# ==========================================
# Privacy Metrics
# ==========================================
PRIVACY_RUNS = Counter(
    "fedguard_privacy_runs_total",
    "Total privacy-enabled training runs",
    ["dp_mode", "model_type", "strategy"]
)
PRIVACY_EPSILON = Gauge(
    "fedguard_privacy_epsilon_spent",
    "Privacy budget (epsilon) spent by the end of the run",
    ["dp_mode", "model_type", "strategy"]
)
PRIVACY_NOISE = Gauge(
    "fedguard_privacy_noise_multiplier",
    "Noise multiplier applied",
    ["dp_mode", "model_type", "strategy"]
)
PRIVACY_GRAD_NORM = Gauge(
    "fedguard_privacy_max_grad_norm",
    "Max gradient norm for clipping",
    ["dp_mode", "model_type", "strategy"]
)

# ==========================================
# Edge Simulation Metrics
# ==========================================
EDGE_RUNS = Counter(
    "fedguard_edge_simulation_runs_total",
    "Total edge-simulated runs",
    ["device_type", "cpu_class"]
)
EDGE_LATENCY = Gauge(
    "fedguard_edge_average_latency_ms",
    "Average edge network latency in ms",
    ["device_type", "cpu_class"]
)
EDGE_AVAILABILITY = Gauge(
    "fedguard_edge_availability_rate",
    "Edge availability rate",
    ["device_type", "cpu_class"]
)
EDGE_BATTERY_SKIPS = Counter(
    "fedguard_edge_battery_skips_total",
    "Total edge clients skipped due to low battery",
    ["device_type", "cpu_class"]
)
EDGE_STRAGGLERS = Counter(
    "fedguard_edge_stragglers_total",
    "Total edge stragglers",
    ["device_type", "cpu_class"]
)

def start_metrics_server(port: int = 9101):
    """Start the Prometheus HTTP metrics server."""
    start_http_server(port)
    print(f"Metrics server started on port {port}")
