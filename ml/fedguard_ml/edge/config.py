"""Edge simulation configuration loader and validator."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class EdgeSimulationConfig:
    """Top-level configuration for edge-device simulation."""

    enabled: bool = False
    seed: int = 42
    profiles: dict[str, str] | None = None  # client_id -> preset name
    battery_drain_per_round: float = 8.0
    battery_low_threshold: float = 20.0
    straggler_latency_threshold_ms: float = 500.0

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "seed": self.seed,
            "profiles": self.profiles,
            "battery_drain_per_round": self.battery_drain_per_round,
            "battery_low_threshold": self.battery_low_threshold,
            "straggler_latency_threshold_ms": self.straggler_latency_threshold_ms,
        }


def load_edge_config(path: Optional[str] = None) -> EdgeSimulationConfig:
    """Load edge simulation config from a JSON file.

    If *path* is ``None``, returns a default config with ``enabled=False``.
    """
    if path is None:
        return EdgeSimulationConfig(enabled=False)

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Edge config file not found: {p}")

    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)

    return EdgeSimulationConfig(
        enabled=data.get("enabled", True),
        seed=data.get("seed", 42),
        profiles=data.get("profiles"),
        battery_drain_per_round=data.get("battery_drain_per_round", 8.0),
        battery_low_threshold=data.get("battery_low_threshold", 20.0),
        straggler_latency_threshold_ms=data.get("straggler_latency_threshold_ms", 500.0),
    )
