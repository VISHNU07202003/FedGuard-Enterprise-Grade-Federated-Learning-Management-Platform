from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class PrivacyConfig:
    enabled: bool = False
    dp_mode: str = "none"  # none | opacus | update_noise
    target_epsilon: Optional[float] = None
    delta: float = 1e-5
    max_grad_norm: float = 1.0
    noise_multiplier: float = 1.0
    secure_rng: bool = False
    update_clipping_norm: float = 1.0
    update_noise_std: float = 0.0

    def to_dict(self):
        return asdict(self)
