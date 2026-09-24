# FedGuard Phase 10 Results

## Differential Privacy Achieved
FedGuard now integrates Opacus for Local Differential Privacy (DP-SGD) during federated client training. This reduces the risk of exposing individual client data during federated training.

## Verification Commands

To run a simulated federated DP experiment:
\\\ash
python ml/scripts/run_simulation.py --strategy fedavg --model dense --num-clients 3 --rounds 2 --privacy --dp-mode opacus --noise-multiplier 1.0 --max-grad-norm 1.0 --delta 1e-5
\\\`n
To ingest the results into PostgreSQL for the dashboard:
\\\ash
# Adjust run_path to your actual output folder
python backend/scripts/ingest_federation_run.py --run-path ml/federation/runs/sim_20260913_...
\\\`n
## Artifacts Generated
Each DP run outputs the following files:
- \privacy_config.json\: Parameters used (delta, noise multiplier).
- \privacy_spent.json\: Formal accounting of the epsilon budget spent.
- \privacy_report.json\: Human-readable summary of privacy guarantees and limitations.

## Frontend UI
The Dashboard, Training Runs table, and Training Run Detail pages now display badges and cards highlighting the active Privacy Preserving Training mode, along with the precise Epsilon spent.
