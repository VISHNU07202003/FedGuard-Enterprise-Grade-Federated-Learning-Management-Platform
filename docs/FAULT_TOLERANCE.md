# Fault Tolerance in FedGuard

In a true distributed learning system, endpoints will drop out, experience latency spikes, or return corrupt tensors. FedGuard mitigates this through comprehensive failure isolation mechanics.

## Detected Failure Modes
FedGuard categorizes failures into distinct statuses:
1. **Dropout**: A client intentionally ignores the round invitation.
2. **Timeout**: A client takes longer than the server is willing to wait.
3. **Failure (Exception)**: A client throws an unhandled error locally.
4. **Straggler**: A client successfully returns, but their duration significantly exceeded the `straggler_threshold_seconds`. They are logged, but their updates are still applied.
5. **Rejected**: A client returned a mathematically broken tensor (`NaN`, `Inf`, empty size, or mismatched dimensions). Their update is actively destroyed before `aggregate_fit`.
6. **Battery Low**: An edge client is skipped for a round because its simulated battery level fell below 20%.
7. **Edge Unavailable**: A probabilistic availability check failed for a given edge profile type.

## Validation Strategy
The `update_validation.py` script loops through every NumPy layer submitted by the client checking `np.isnan().any()` and `np.isinf().any()`. If a client violates these rules, the simulation emits a `client.rejected` event payload containing the exact layer index fault, protecting the global weights from catastrophic gradient explosion.

## Partial Participation
Instead of failing a round, FedGuard allows `partial_success` if `clients_completed >= min_completed_clients`. The backend records a `completion_rate` reflecting the ratio.

## MLflow Lineage
The tracker natively stores these metrics:
`clients_failed`, `clients_rejected`, `clients_timed_out`, `straggler_count`, `completion_rate`.
This allows operators to build regression charts tracking client reliability across experiment time!
