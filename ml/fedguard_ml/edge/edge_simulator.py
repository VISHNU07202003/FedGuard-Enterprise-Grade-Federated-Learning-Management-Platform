"""Simulate realistic edge-device constraints during federated training rounds."""

from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass, field
from typing import Optional

from ml.fedguard_ml.edge.device_profile import DeviceProfile

logger = logging.getLogger(__name__)

BATTERY_LOW_THRESHOLD = 20.0  # percent
BATTERY_DRAIN_PER_ROUND = 8.0  # percent drained per participation


@dataclass
class EdgeRoundResult:
    """Telemetry captured for one client in one round."""

    client_id: str
    device_type: str
    cpu_class: str
    memory_mb: int
    network_latency_ms: float
    bandwidth_mbps: float
    battery_level: Optional[float]
    available: bool
    availability_reason: str  # "ok", "battery_low", "unavailable", "failure"
    simulated_training_time: float  # seconds
    simulated_communication_time: float  # seconds
    total_client_time: float  # seconds

    def to_dict(self) -> dict:
        return {
            "client_id": self.client_id,
            "device_type": self.device_type,
            "cpu_class": self.cpu_class,
            "memory_mb": self.memory_mb,
            "network_latency_ms": self.network_latency_ms,
            "bandwidth_mbps": self.bandwidth_mbps,
            "battery_level": self.battery_level,
            "available": self.available,
            "availability_reason": self.availability_reason,
            "simulated_training_time": self.simulated_training_time,
            "simulated_communication_time": self.simulated_communication_time,
            "total_client_time": self.total_client_time,
        }


class EdgeSimulator:
    """
    Wraps per-round edge-device behaviour: availability checks,
    latency injection, training-speed scaling, and battery drain.
    """

    def __init__(self, profiles: dict[str, DeviceProfile], seed: int = 42):
        self.profiles = profiles
        self.rng = random.Random(seed)

    # ------------------------------------------------------------------
    # Availability
    # ------------------------------------------------------------------

    def check_availability(self, client_id: str) -> tuple[bool, str]:
        """Return (is_available, reason)."""
        profile = self.profiles[client_id]

        # Battery check first
        if profile.battery_powered and profile.battery_level is not None:
            if profile.battery_level < BATTERY_LOW_THRESHOLD:
                return False, "battery_low"

        # Probabilistic availability
        if self.rng.random() > profile.availability_probability:
            return False, "unavailable"

        return True, "ok"

    # ------------------------------------------------------------------
    # Latency & communication delay
    # ------------------------------------------------------------------

    def simulate_latency(self, client_id: str) -> float:
        """
        Return simulated network latency in **seconds**.
        Adds a small jitter (±20 %) around the profile value.
        Capped at 0.5 s so tests stay fast.
        """
        profile = self.profiles[client_id]
        base_ms = profile.network_latency_ms
        jitter = self.rng.uniform(-0.2, 0.2) * base_ms
        latency_s = max(0.001, (base_ms + jitter) / 1000.0)
        return min(latency_s, 0.5)  # cap for tests

    def simulate_communication_delay(self, client_id: str, model_size_bytes: int = 500_000) -> float:
        """Estimate upload/download delay from bandwidth. Returns seconds."""
        profile = self.profiles[client_id]
        bw_bytes_per_sec = (profile.bandwidth_mbps * 1_000_000) / 8
        if bw_bytes_per_sec <= 0:
            return 0.5
        delay = model_size_bytes / bw_bytes_per_sec
        return min(delay, 0.5)  # cap

    # ------------------------------------------------------------------
    # Training speed
    # ------------------------------------------------------------------

    def adjust_training_time(self, client_id: str, base_time: float) -> float:
        """Scale actual training duration by the device speed multiplier."""
        profile = self.profiles[client_id]
        return base_time / max(profile.training_speed_multiplier, 0.1)

    # ------------------------------------------------------------------
    # Battery drain
    # ------------------------------------------------------------------

    def drain_battery(self, client_id: str) -> None:
        """Reduce battery after a round of participation."""
        profile = self.profiles[client_id]
        if profile.battery_powered and profile.battery_level is not None:
            drain = BATTERY_DRAIN_PER_ROUND + self.rng.uniform(-2, 2)
            profile.battery_level = max(0.0, profile.battery_level - drain)

    # ------------------------------------------------------------------
    # Full round helper
    # ------------------------------------------------------------------

    def run_round_for_client(
        self,
        client_id: str,
        actual_training_time: float,
        model_size_bytes: int = 500_000,
    ) -> EdgeRoundResult:
        """
        Execute all edge simulation steps for one client in one round
        and return the telemetry record.
        """
        profile = self.profiles[client_id]
        available, reason = self.check_availability(client_id)

        if not available:
            return EdgeRoundResult(
                client_id=client_id,
                device_type=profile.device_type,
                cpu_class=profile.cpu_class,
                memory_mb=profile.memory_mb,
                network_latency_ms=profile.network_latency_ms,
                bandwidth_mbps=profile.bandwidth_mbps,
                battery_level=profile.battery_level,
                available=False,
                availability_reason=reason,
                simulated_training_time=0.0,
                simulated_communication_time=0.0,
                total_client_time=0.0,
            )

        latency = self.simulate_latency(client_id)
        comm_delay = self.simulate_communication_delay(client_id, model_size_bytes)
        adjusted_time = self.adjust_training_time(client_id, actual_training_time)

        self.drain_battery(client_id)

        total = latency + adjusted_time + comm_delay

        return EdgeRoundResult(
            client_id=client_id,
            device_type=profile.device_type,
            cpu_class=profile.cpu_class,
            memory_mb=profile.memory_mb,
            network_latency_ms=profile.network_latency_ms,
            bandwidth_mbps=profile.bandwidth_mbps,
            battery_level=profile.battery_level,
            available=True,
            availability_reason="ok",
            simulated_training_time=round(adjusted_time, 4),
            simulated_communication_time=round(latency + comm_delay, 4),
            total_client_time=round(total, 4),
        )
