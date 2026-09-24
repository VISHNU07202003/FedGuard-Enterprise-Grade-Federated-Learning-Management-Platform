import flwr as fl
import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path
import json

from ml.fedguard_ml.models.dense_autoencoder import DenseAutoencoder
from ml.fedguard_ml.models.transformer_autoencoder import TransformerAutoencoder
from ml.fedguard_ml.federation.serialization import get_parameters, set_parameters

from ml.fedguard_ml.privacy.differential_privacy import FedGuardPrivacyEngine
from ml.fedguard_ml.privacy.config import PrivacyConfig
from ml.fedguard_ml.privacy.update_privacy import apply_update_perturbation

def get_model(model_name: str, input_dim: int) -> nn.Module:
    if model_name == "dense":
        return DenseAutoencoder(input_dim)
    elif model_name == "transformer":
        return TransformerAutoencoder(input_dim)
    else:
        raise ValueError(f"Unknown model: {model_name}")

class FedGuardClient(fl.client.NumPyClient):
    def __init__(self, cid: str, data_dir: Path, model_name: str, batch_size: int, local_epochs: int, lr: float, privacy_config=None):
        self.cid = cid
        self.data_dir = data_dir
        self.model_name = model_name
        self.batch_size = batch_size
        self.local_epochs = local_epochs
        self.lr = lr
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.privacy_config = privacy_config
        
        # Load local partition
        client_dir = self.data_dir / "iid" / f"client_{int(self.cid):03d}"
        
        # The partitioning guarantees client gets NORMAL data only for training
        self.X_train = np.load(client_dir / "X_train.npy")
        self.X_val = np.load(client_dir / "X_val.npy")
        
        self.input_dim = self.X_train.shape[1]
        self.model = get_model(self.model_name, self.input_dim).to(self.device)
        self.criterion = nn.MSELoss()
        
        # Initialize PrivacyEngine (stateful across rounds)
        self.privacy_engine = None
        if self.privacy_config and self.privacy_config.enabled and self.privacy_config.dp_mode == "opacus":
            self.privacy_engine = FedGuardPrivacyEngine(self.privacy_config)
            
            # Create dataloader and optimizer ONCE to be wrapped
            self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)
            dataset = TensorDataset(torch.tensor(self.X_train))
            self.dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
            
            self.model, self.optimizer, self.dataloader = self.privacy_engine.make_private(
                model=self.model,
                optimizer=self.optimizer,
                data_loader=self.dataloader,
                epochs=self.local_epochs # Initial estimate
            )
        else:
            self.optimizer = None
            self.dataloader = None

    def get_parameters(self, config):
        if hasattr(self.model, "_module"):
            return get_parameters(self.model._module)
        return get_parameters(self.model)

    def fit(self, parameters, config):
        # Unwrap for setting parameters
        if hasattr(self.model, "_module"):
            set_parameters(self.model._module, parameters)
        else:
            set_parameters(self.model, parameters)
            
        epochs = config.get("local_epochs", self.local_epochs)
        batch_size = config.get("batch_size", self.batch_size)
        lr = config.get("lr", self.lr)
        
        if self.privacy_engine:
            dataloader = self.dataloader
            optimizer = self.optimizer
        else:
            dataset = TensorDataset(torch.tensor(self.X_train))
            dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
            optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        
        self.model.train()
        total_loss = 0.0
        
        for epoch in range(epochs):
            epoch_loss = 0.0
            for batch_x, in dataloader:
                batch_x = batch_x.to(self.device)
                
                optimizer.zero_grad()
                recon = self.model(batch_x)
                loss = self.criterion(recon, batch_x)
                
                proximal_mu = config.get("proximal_mu", 0.0)
                if proximal_mu > 0:
                    proximal_term = 0.0
                    global_params = [torch.tensor(p).to(self.device) for p in parameters]
                    for local_p, global_p in zip(self.model.parameters(), global_params):
                        proximal_term += ((local_p - global_p) ** 2).sum()
                    loss += (proximal_mu / 2) * proximal_term

                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item() * batch_x.size(0)
            
            total_loss += epoch_loss / len(self.X_train)
            
        avg_train_loss = total_loss / epochs
        
        new_parameters = self.get_parameters(config)
        
        # Experimental update perturbation
        if self.privacy_config and self.privacy_config.enabled and self.privacy_config.dp_mode == "update_noise":
            new_parameters = apply_update_perturbation(new_parameters, parameters, self.privacy_config)
            
        metrics = {"train_loss": avg_train_loss}
        if self.privacy_engine:
            spent = self.privacy_engine.get_privacy_spent()
            if spent.get("epsilon_spent") is not None:
                metrics["epsilon_spent"] = spent["epsilon_spent"]
                
        return new_parameters, len(self.X_train), metrics

    def evaluate(self, parameters, config):
        if hasattr(self.model, "_module"):
            set_parameters(self.model._module, parameters)
        else:
            set_parameters(self.model, parameters)
        
        # Evaluate on local validation set (normal data)
        X_val_t = torch.tensor(self.X_val).to(self.device)
        self.model.eval()
        with torch.no_grad():
            recon = self.model(X_val_t)
            loss = self.criterion(recon, X_val_t).item()
            
        return float(loss), len(self.X_val), {"val_loss": float(loss)}

def client_fn(cid: str, privacy_config=None) -> fl.client.Client:
    """Creates a Flower client for the simulation."""
    ml_dir = Path(__file__).resolve().parent.parent.parent
    data_dir = ml_dir / "data" / "partitions"
    
    # Normally read from environment variables or context in a real deployment
    # For simulation, we can hardcode or pass via simulation context
    client = FedGuardClient(
        cid=cid,
        data_dir=data_dir,
        model_name="dense", # Can make this configurable
        batch_size=256,
        local_epochs=3,
        lr=1e-3,
        privacy_config=privacy_config
    )
    return client.to_client()
