import json
import pytest
from pathlib import Path
from ml.fedguard_ml.edge.device_profile import PRESET_PROFILES, assign_profiles
from ml.fedguard_ml.edge.edge_simulator import EdgeSimulator, BATTERY_LOW_THRESHOLD

def test_preset_profiles_exist():
    assert len(PRESET_PROFILES) >= 6
    assert "industrial_gateway" in PRESET_PROFILES
    assert "mobile_edge_node" in PRESET_PROFILES

def test_assign_profiles_deterministic():
    profiles_1 = assign_profiles(5, seed=42)
    profiles_2 = assign_profiles(5, seed=42)
    assert profiles_1.keys() == profiles_2.keys()
    for cid in profiles_1:
        assert profiles_1[cid].device_type == profiles_2[cid].device_type
        
    profiles_3 = assign_profiles(5, seed=99)
    # Different seed should likely produce a different assignment
    different = any(profiles_1[cid].device_type != profiles_3[cid].device_type for cid in profiles_1)
    assert different

def test_assign_profiles_with_config(tmp_path):
    config = {
        "enabled": True,
        "profiles": {
            "client_000": "industrial_gateway",
            "client_002": "mobile_edge_node"
        }
    }
    config_path = tmp_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f)
        
    profiles = assign_profiles(3, str(config_path), seed=42)
    assert profiles["client_000"].device_type == "industrial_gateway"
    assert profiles["client_002"].device_type == "mobile_edge_node"
    # client_001 is randomly assigned
    assert profiles["client_001"].device_type in PRESET_PROFILES

def test_edge_simulator_latency():
    profiles = assign_profiles(1, seed=42)
    cid = "client_000"
    sim = EdgeSimulator(profiles, seed=42)
    
    latency = sim.simulate_latency(cid)
    assert latency > 0
    assert latency <= 0.5  # Should be capped

def test_battery_low_skip():
    profiles = assign_profiles(1, seed=42)
    cid = "client_000"
    
    # Force battery config
    profiles[cid].battery_powered = True
    profiles[cid].battery_level = BATTERY_LOW_THRESHOLD - 1.0
    profiles[cid].availability_probability = 1.0  # Force available if not for battery
    
    sim = EdgeSimulator(profiles, seed=42)
    available, reason = sim.check_availability(cid)
    
    assert not available
    assert reason == "battery_low"

def test_run_round_for_client():
    profiles = assign_profiles(1, seed=42)
    cid = "client_000"
    
    # Ensure client is available and has battery
    profiles[cid].availability_probability = 1.0
    profiles[cid].battery_powered = True
    profiles[cid].battery_level = 100.0
    
    sim = EdgeSimulator(profiles, seed=42)
    
    initial_battery = profiles[cid].battery_level
    result = sim.run_round_for_client(cid, actual_training_time=0.1)
    
    assert result.available
    assert result.availability_reason == "ok"
    assert result.client_id == cid
    assert profiles[cid].battery_level < initial_battery
