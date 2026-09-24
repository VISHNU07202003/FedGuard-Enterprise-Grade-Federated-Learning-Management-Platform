"""Edge device profiles for realistic federated-client simulation."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class DeviceProfile:
    """Hardware and network characteristics of a simulated edge device."""

    device_type: str
    organization_name: str
    cpu_class: str  # "low", "medium", "high"
    memory_mb: int
    network_latency_ms: float
    bandwidth_mbps: float
    availability_probability: float  # 0.0 – 1.0
    battery_powered: bool
    battery_level: Optional[float]  # 0–100 or None
    data_volume_multiplier: float  # 1.0 = baseline
    training_speed_multiplier: float  # <1 = slower than baseline
    failure_probability: float  # 0.0 – 1.0

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Preset profiles
# ---------------------------------------------------------------------------

PRESET_PROFILES: dict[str, DeviceProfile] = {
    "industrial_gateway": DeviceProfile(
        device_type="industrial_gateway",
        organization_name="Smart Factory A",
        cpu_class="high",
        memory_mb=4096,
        network_latency_ms=50,
        bandwidth_mbps=100,
        availability_probability=0.95,
        battery_powered=False,
        battery_level=None,
        data_volume_multiplier=1.5,
        training_speed_multiplier=1.0,
        failure_probability=0.02,
    ),
    "smart_factory_sensor": DeviceProfile(
        device_type="smart_factory_sensor",
        organization_name="Smart Factory B",
        cpu_class="low",
        memory_mb=512,
        network_latency_ms=200,
        bandwidth_mbps=10,
        availability_probability=0.80,
        battery_powered=True,
        battery_level=75.0,
        data_volume_multiplier=0.6,
        training_speed_multiplier=0.5,
        failure_probability=0.08,
    ),
    "building_controller": DeviceProfile(
        device_type="building_controller",
        organization_name="Building Mgmt Co",
        cpu_class="medium",
        memory_mb=2048,
        network_latency_ms=120,
        bandwidth_mbps=25,
        availability_probability=0.92,
        battery_powered=False,
        battery_level=None,
        data_volume_multiplier=1.3,
        training_speed_multiplier=0.8,
        failure_probability=0.03,
    ),
    "edge_cluster": DeviceProfile(
        device_type="edge_cluster",
        organization_name="Cloud Edge Region",
        cpu_class="high",
        memory_mb=8192,
        network_latency_ms=30,
        bandwidth_mbps=500,
        availability_probability=0.99,
        battery_powered=False,
        battery_level=None,
        data_volume_multiplier=2.0,
        training_speed_multiplier=1.2,
        failure_probability=0.01,
    ),
    "low_power_iot_node": DeviceProfile(
        device_type="low_power_iot_node",
        organization_name="IoT Deployment X",
        cpu_class="low",
        memory_mb=256,
        network_latency_ms=350,
        bandwidth_mbps=5,
        availability_probability=0.70,
        battery_powered=True,
        battery_level=60.0,
        data_volume_multiplier=0.3,
        training_speed_multiplier=0.3,
        failure_probability=0.12,
    ),
    "mobile_edge_node": DeviceProfile(
        device_type="mobile_edge_node",
        organization_name="Mobile Fleet",
        cpu_class="medium",
        memory_mb=1024,
        network_latency_ms=180,
        bandwidth_mbps=15,
        availability_probability=0.75,
        battery_powered=True,
        battery_level=55.0,
        data_volume_multiplier=0.8,
        training_speed_multiplier=0.6,
        failure_probability=0.06,
    ),
}


def assign_profiles(
    num_clients: int,
    config_path: Optional[str] = None,
    seed: int = 42,
) -> dict[str, DeviceProfile]:
    """
    Return a mapping ``{client_id: DeviceProfile}`` for *num_clients*.

    If *config_path* is provided, it should point to a JSON file with a
    ``profiles`` key mapping client IDs to preset profile names.  Any
    client not listed in the config is assigned a random preset
    deterministically via *seed*.
    """
    rng = random.Random(seed)
    preset_names = list(PRESET_PROFILES.keys())
    result: dict[str, DeviceProfile] = {}

    explicit_map: dict[str, str] = {}
    if config_path:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        explicit_map = cfg.get("profiles", {})

    for i in range(num_clients):
        cid = f"client_{i:03d}"
        if cid in explicit_map:
            profile_name = explicit_map[cid]
        else:
            profile_name = rng.choice(preset_names)

        base = PRESET_PROFILES[profile_name]
        # Create a copy so per-client mutation (e.g. battery drain) is safe
        profile = DeviceProfile(**asdict(base))
        # Personalise the org name per client
        profile.organization_name = f"{base.organization_name} — {cid}"
        result[cid] = profile

    return result
