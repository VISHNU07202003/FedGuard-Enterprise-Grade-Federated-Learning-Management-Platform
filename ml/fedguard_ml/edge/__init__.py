"""Edge device simulation package for FedGuard federated learning."""

from ml.fedguard_ml.edge.device_profile import DeviceProfile, PRESET_PROFILES, assign_profiles
from ml.fedguard_ml.edge.edge_simulator import EdgeSimulator, EdgeRoundResult
from ml.fedguard_ml.edge.config import EdgeSimulationConfig, load_edge_config

__all__ = [
    "DeviceProfile",
    "PRESET_PROFILES",
    "assign_profiles",
    "EdgeSimulator",
    "EdgeRoundResult",
    "EdgeSimulationConfig",
    "load_edge_config",
]
