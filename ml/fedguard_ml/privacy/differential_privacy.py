from typing import Tuple, Dict, Any
import torch
from torch.utils.data import DataLoader
from opacus import PrivacyEngine
from ml.fedguard_ml.privacy.config import PrivacyConfig
from opacus.validators import ModuleValidator
import logging

logger = logging.getLogger(__name__)

class FedGuardPrivacyEngine:
    def __init__(self, config: PrivacyConfig):
        self.config = config
        self.privacy_engine = None

    def make_private(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        data_loader: DataLoader,
        epochs: int = 1
    ) -> Tuple[torch.nn.Module, torch.optim.Optimizer, DataLoader]:
        """
        Wraps the model, optimizer, and dataloader with Opacus.
        """
        if not self.config.enabled or self.config.dp_mode != "opacus":
            return model, optimizer, data_loader

        # Validate and fix model for Opacus compatibility
        errors = ModuleValidator.validate(model, strict=False)
        if len(errors) > 0:
            logger.warning(f"Opacus compatibility warnings/errors: {errors}")
            model = ModuleValidator.fix(model)

        self.privacy_engine = PrivacyEngine(secure_mode=self.config.secure_rng)

        if self.config.target_epsilon is not None:
            # Mode B: Target Epsilon
            logger.info(f"Using DP Mode B: Target Epsilon = {self.config.target_epsilon}, Delta = {self.config.delta}, Epochs = {epochs}")
            model, optimizer, data_loader = self.privacy_engine.make_private_with_epsilon(
                module=model,
                optimizer=optimizer,
                data_loader=data_loader,
                epochs=epochs,
                target_epsilon=self.config.target_epsilon,
                target_delta=self.config.delta,
                max_grad_norm=self.config.max_grad_norm,
            )
        else:
            # Mode A: Fixed Noise Multiplier
            logger.info(f"Using DP Mode A: Noise Multiplier = {self.config.noise_multiplier}, Delta = {self.config.delta}")
            model, optimizer, data_loader = self.privacy_engine.make_private(
                module=model,
                optimizer=optimizer,
                data_loader=data_loader,
                noise_multiplier=self.config.noise_multiplier,
                max_grad_norm=self.config.max_grad_norm,
            )

        return model, optimizer, data_loader

    def get_privacy_spent(self) -> Dict[str, Any]:
        """
        Returns the formal privacy accounting values.
        """
        if not self.config.enabled or self.privacy_engine is None:
            return {}

        try:
            epsilon = self.privacy_engine.get_epsilon(self.config.delta)
        except Exception as e:
            logger.warning(f"Failed to calculate epsilon: {e}")
            epsilon = None
            
        noise_mult = self.config.noise_multiplier
        if self.config.target_epsilon is not None and self.privacy_engine.accountant is not None:
             noise_mult = self.privacy_engine.optimizer.noise_multiplier if hasattr(self.privacy_engine, 'optimizer') and self.privacy_engine.optimizer else noise_mult
            
        return {
            "epsilon_spent": epsilon,
            "delta": self.config.delta,
            "accountant": "rdp",
            "noise_multiplier": noise_mult,
            "max_grad_norm": self.config.max_grad_norm,
            "formal_accounting": True
        }
