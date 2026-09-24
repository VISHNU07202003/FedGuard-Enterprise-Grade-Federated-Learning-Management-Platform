import torch
import torch.nn as nn

class DenseAutoencoder(nn.Module):
    def __init__(self, input_dim: int, latent_dim: int = 16):
        super().__init__()
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, latent_dim),
            nn.ReLU()
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Linear(64, input_dim)
            # Typically no activation on final layer for standardized inputs
        )
        
    def forward(self, x):
        latent = self.encoder(x)
        reconstruction = self.decoder(latent)
        return reconstruction
        
    def get_reconstruction_error(self, x):
        """Returns the per-sample reconstruction error (MSE)"""
        with torch.no_grad():
            reconstruction = self(x)
            # Mean over features
            mse = torch.mean((x - reconstruction) ** 2, dim=1)
        return mse
