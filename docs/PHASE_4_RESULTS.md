# Phase 4 Results: Local ML Pipeline

## Overview
Phase 4 successfully established the baseline local machine learning pipeline for FedGuard before introducing federated learning. 

## What was Implemented
1. **Dataset Inspection:** `inspect_dataset.py` rigorously analyzed the raw ToN-IoT Network Traffic dataset without assumptions, producing JSON and Markdown reports detailing class distribution and schema.
2. **Preprocessing:** `preprocessing.py` built an sklearn-compatible `ToNIoTPreprocessor` that safely drops leaky features, imputes missing values (including Zeek's `"-"`), label encodes categoricals, and standard scales numericals while preventing data leakage from the test set.
3. **Partitioning:** `partition_dataset.py` generates 10-client splits under three conditions:
   - **IID:** Uniform random split.
   - **Label-Skew:** Sorted by label before splitting.
   - **Quantity-Skew:** Dirichlet distribution for unequal sample sizes.
4. **Models:** 
   - `DenseAutoencoder` (baseline)
   - `TransformerAutoencoder` (self-attention based)
5. **Training & Evaluation:** `train_local.py` trains the autoencoder solely on `label=0` (normal) traffic. `evaluate_local.py` tests on the 15% holdout test set using a dynamically calculated 95th-percentile anomaly threshold.

## How to Run
```bash
# 1. Inspection
python ml/scripts/inspect_dataset.py

# 2. Preprocessing
python ml/scripts/prepare_dataset.py

# 3. Partitioning
python ml/scripts/partition_dataset.py

# 4. Local Training
python ml/scripts/train_local.py --model dense
python ml/scripts/train_local.py --model transformer

# 5. Evaluation
python ml/scripts/evaluate_local.py --run-id <run_id>
```

## Known Limitations
- The current Transformer autoencoder is a minimal prototype (length=1 sequence) for tabular data. A more advanced tabular transformer (like FT-Transformer) or creating sequences out of time-windows could improve AUC.
- Categorical variables are `LabelEncoded`. One-hot encoding or learned embeddings would prevent ordinal misinterpretation.
- F1-scores on the Dense model are currently low due to minimal tuning (5 epochs, small architecture). The goal of Phase 4 is pipeline validation, not SOTA accuracy. Tuning will occur in later phases.
