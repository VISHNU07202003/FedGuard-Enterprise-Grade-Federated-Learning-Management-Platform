from collections import OrderedDict
from typing import List
import torch
import numpy as np

def get_parameters(model: torch.nn.Module) -> List[np.ndarray]:
    """
    Extracts model parameters as a list of NumPy arrays.
    Only extracts trainable parameters to save bandwidth.
    """
    return [val.cpu().numpy() for _, val in model.state_dict().items()]

def set_parameters(model: torch.nn.Module, parameters: List[np.ndarray]):
    """
    Injects a list of NumPy arrays into the model as parameters.
    """
    params_dict = zip(model.state_dict().keys(), parameters)
    state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
    model.load_state_dict(state_dict, strict=True)
