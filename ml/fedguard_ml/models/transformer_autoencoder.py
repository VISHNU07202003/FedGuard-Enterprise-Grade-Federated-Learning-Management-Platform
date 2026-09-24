import torch
import torch.nn as nn

class TransformerAutoencoder(nn.Module):
    def __init__(self, input_dim: int, d_model: int = 32, nhead: int = 4, num_layers: int = 2):
        super().__init__()
        
        self.d_model = d_model
        
        # Project input feature to d_model space
        self.input_projection = nn.Linear(input_dim, d_model)
        
        # Transformer Encoder
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, dim_feedforward=64, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # We'll use a bottleneck to compress
        self.bottleneck = nn.Sequential(
            nn.Linear(d_model, 16),
            nn.ReLU(),
            nn.Linear(16, d_model),
            nn.ReLU()
        )
        
        # Transformer Decoder (just another encoder layer for symmetry in reconstruction)
        decoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, dim_feedforward=64, batch_first=True)
        self.transformer_decoder = nn.TransformerEncoder(decoder_layer, num_layers=num_layers)
        
        # Project back to original features
        self.output_projection = nn.Linear(d_model, input_dim)
        
    def forward(self, x):
        # x is (batch, features). We pretend it's a sequence of length 1: (batch, 1, features)
        x_seq = x.unsqueeze(1)
        
        projected = self.input_projection(x_seq)
        
        encoded = self.transformer_encoder(projected)
        
        latent = self.bottleneck(encoded)
        
        decoded = self.transformer_decoder(latent)
        
        reconstruction = self.output_projection(decoded)
        
        # squeeze sequence dim back out
        return reconstruction.squeeze(1)
        
    def get_reconstruction_error(self, x):
        """Returns the per-sample reconstruction error (MSE)"""
        with torch.no_grad():
            reconstruction = self(x)
            mse = torch.mean((x - reconstruction) ** 2, dim=1)
        return mse
