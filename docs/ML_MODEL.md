# ML Models for Anomaly Detection

## Dense Autoencoder (Baseline)
A simple feed-forward neural network autoencoder.
- **Encoder:** Input -> 64 -> 32 -> 16 (Latent)
- **Decoder:** 16 -> 32 -> 64 -> Input
- **Activation:** ReLU (no activation on final layer)

## Transformer Autoencoder (Primary)
A self-attention based model adapted for tabular data anomaly detection.
- **Input Projection:** Maps the flat feature vector into a sequence of length 1 with dimensionality `d_model` (default 32).
- **Transformer Encoder:** Applies multi-head self-attention.
- **Bottleneck:** Feed-forward layer compressing `d_model` to 16 and back to force loss of information (autoencoder bottleneck).
- **Transformer Decoder:** Symmetrical self-attention block reconstructing the features.
- **Output Projection:** Maps `d_model` back to original feature space.

## Anomaly Scoring & Thresholding
Models are trained **only on normal data** (label = 0). 
During validation/testing, the models attempt to reconstruct the input. 

**Anomaly Score:** Mean Squared Error (MSE) between the original input and the reconstruction.

**Threshold:** The threshold is calculated by running validation normal data through the model and finding the 95th percentile of the reconstruction error. Any sample with a reconstruction error higher than this threshold is classified as an anomaly (1).
