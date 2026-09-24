import pytest
import numpy as np
from ml.fedguard_ml.federation.update_validation import validate_update

def test_validate_valid_update():
    params = [np.array([1.0, 2.0]), np.array([[3.0]])]
    expected_shapes = [(2,), (1, 1)]
    result = validate_update(params, expected_shapes)
    assert result.valid is True
    assert result.reason is None

def test_validate_nan_update():
    params = [np.array([1.0, np.nan]), np.array([[3.0]])]
    expected_shapes = [(2,), (1, 1)]
    result = validate_update(params, expected_shapes)
    assert result.valid is False
    assert result.reason == "invalid_update_nan"

def test_validate_inf_update():
    params = [np.array([1.0, np.inf]), np.array([[3.0]])]
    expected_shapes = [(2,), (1, 1)]
    result = validate_update(params, expected_shapes)
    assert result.valid is False
    assert result.reason == "invalid_update_inf"

def test_validate_empty_update():
    params = []
    result = validate_update(params)
    assert result.valid is False
    assert result.reason == "empty_update"

def test_validate_shape_mismatch():
    params = [np.array([1.0, 2.0, 3.0]), np.array([[3.0]])]
    expected_shapes = [(2,), (1, 1)]
    result = validate_update(params, expected_shapes)
    assert result.valid is False
    assert result.reason == "shape_mismatch_layer_0"
    
def test_validate_layer_count_mismatch():
    params = [np.array([1.0, 2.0])]
    expected_shapes = [(2,), (1, 1)]
    result = validate_update(params, expected_shapes)
    assert result.valid is False
    assert result.reason == "layer_count_mismatch"
