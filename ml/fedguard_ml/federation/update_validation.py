import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Tuple

@dataclass
class UpdateValidationResult:
    valid: bool
    reason: Optional[str]
    parameter_count: int
    shapes_checked: int

def validate_update(parameters: List[np.ndarray], expected_shapes: Optional[List[Tuple[int, ...]]] = None) -> UpdateValidationResult:
    """
    Validates a client's model parameters update.
    Returns an UpdateValidationResult with details on the validity.
    """
    if not parameters:
        return UpdateValidationResult(valid=False, reason="empty_update", parameter_count=0, shapes_checked=0)
    
    total_params = 0
    shapes_checked = 0
    
    for idx, layer_weights in enumerate(parameters):
        if not isinstance(layer_weights, np.ndarray):
            return UpdateValidationResult(valid=False, reason=f"invalid_type_layer_{idx}", parameter_count=total_params, shapes_checked=shapes_checked)
            
        total_params += layer_weights.size
        shapes_checked += 1
        
        # Check for NaNs
        if np.isnan(layer_weights).any():
            return UpdateValidationResult(valid=False, reason="invalid_update_nan", parameter_count=total_params, shapes_checked=shapes_checked)
            
        # Check for Infs
        if np.isinf(layer_weights).any():
            return UpdateValidationResult(valid=False, reason="invalid_update_inf", parameter_count=total_params, shapes_checked=shapes_checked)
            
        # Check shape mismatch if expected shapes are provided
        if expected_shapes and idx < len(expected_shapes):
            if layer_weights.shape != expected_shapes[idx]:
                return UpdateValidationResult(valid=False, reason=f"shape_mismatch_layer_{idx}", parameter_count=total_params, shapes_checked=shapes_checked)

    if expected_shapes and len(parameters) != len(expected_shapes):
         return UpdateValidationResult(valid=False, reason="layer_count_mismatch", parameter_count=total_params, shapes_checked=shapes_checked)
         
    return UpdateValidationResult(valid=True, reason=None, parameter_count=total_params, shapes_checked=shapes_checked)
