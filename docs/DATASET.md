# ToN-IoT Dataset Overview

**Source:** UNSW ToN-IoT Dataset (Network Traffic subset)
**Subset:** `Train_Test_Network.csv`

## Schema Summary
The network dataset contains 211,043 samples and 44 columns capturing realistic benign and malicious IoT network traffic. 

**Label:** 
- `label` (0 = normal, 1 = anomaly)
- `type` (detailed attack category: dos, ddos, ransomware, etc.)

## Preprocessing Pipeline
To prevent data leakage and dimensionality explosion, the following preprocessing steps are applied in `ml/fedguard_ml/data/preprocessing.py`:

1. **Deduplication:** Dropped exact duplicate rows.
2. **Column Removal:** Dropped leaky/high-cardinality columns (`src_ip`, `dst_ip`, `type`, `http_uri`, etc.).
3. **Missing Values:** Imputed with column median (numerical) and mode (categorical). Zeek's default `"-"` values are treated as missing.
4. **Encoding:** `LabelEncoder` applied to categorical string features.
5. **Scaling:** `StandardScaler` applied to all numerical features to normalize inputs for the neural networks.
6. **Data Type:** Output cast to `np.float32` for PyTorch efficiency.

## Split Strategy
Data is split into:
- 70% Train
- 15% Validation (used for anomaly thresholding)
- 15% Test (used for final evaluation)

Splits are stratified by the `label` to ensure realistic proportions of normal and attack traffic across all splits.

## Limitations
- Due to categorical label encoding instead of one-hot encoding, categorical relationships may be incorrectly interpreted as ordinal. A future iteration should introduce embedding layers for categorical variables.
- We rely on local `LabelEncoder` state. In true federated settings, the mapping must be globally agreed upon or distributed.
