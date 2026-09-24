from pydantic import BaseModel
from typing import List, Optional

class KPIMetrics(BaseModel):
    total_clients: int
    active_training_runs: int
    anomalies_detected_24h: int
    system_health_score: int

class SystemStatus(BaseModel):
    status: str
    message: str

class ClientHealthSummary(BaseModel):
    online: int
    offline: int
    training: int
    error: int

class MetricPoint(BaseModel):
    round: int
    accuracy: float
    loss: float
    f1: float

class CurrentTrainingRun(BaseModel):
    run_id: str
    status: str
    current_round: int
    total_rounds: int
    active_clients: int
    accuracy: float
    privacy_enabled: Optional[bool] = False
    dp_mode: Optional[str] = "none"

class EdgeSimulationSummary(BaseModel):
    enabled: bool = False
    active_edge_clients: int = 0
    average_latency_ms: Optional[float] = None
    availability_rate: Optional[float] = None
    battery_limited_clients: int = 0
    slowest_device_profile: Optional[str] = None
    edge_stragglers: int = 0

class DashboardSummaryResponse(BaseModel):
    system_status: SystemStatus
    kpi_metrics: KPIMetrics
    current_training_run: Optional[CurrentTrainingRun]
    client_health_summary: ClientHealthSummary
    model_performance_series: List[MetricPoint]
    recent_security_events: List[dict]
    recent_experiments: List[dict]
    service_health: List[dict]
    edge_simulation: Optional[EdgeSimulationSummary] = None
