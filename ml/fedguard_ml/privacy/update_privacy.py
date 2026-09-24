import torch
import numpy as np
from typing import List
from ml.fedguard_ml.privacy.config import PrivacyConfig
import logging

logger = logging.getLogger(__name__)

def apply_update_perturbation(
    client_params: List[np.ndarray], 
    global_params: List[np.ndarray], 
    config: PrivacyConfig
) -> List[np.ndarray]:
    """
    Experimental update perturbation for custom simulation loop.
    DO NOT claim this as formal Differential Privacy.
    """
    if not config.enabled or config.dp_mode != "update_noise":
        return client_params

    perturbed_params = []
    
    logger.info(f"Applying experimental update perturbation (Clipping: {config.update_clipping_norm}, Noise Std: {config.update_noise_std})")
    
    for client_p, global_p in zip(client_params, global_params):
        # Calculate delta (update)
        update = client_p - global_p
        
        # Clip update norm
        norm = np.linalg.norm(update)
        if norm > config.update_clipping_norm:
            update = update * (config.update_clipping_norm / (norm + 1e-10))
            
        # Add Gaussian noise
        if config.update_noise_std > 0:
            noise = np.random.normal(0, config.update_noise_std, update.shape)
            update = update + noise
            
        # Reconstruct client parameters
        perturbed_p = global_p + update
        perturbed_params.append(perturbed_p)
        
    return perturbed_params
