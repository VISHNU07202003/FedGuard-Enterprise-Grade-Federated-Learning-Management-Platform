# FedGuard Secure Aggregation Strategy

## Overview
Secure Aggregation (SecAgg) allows the central server to aggregate client model updates without ever seeing the individual updates. This prevents the server from reverse-engineering client data from raw gradients.

## Flower SecAgg+ limitations on Windows
Flower provides a powerful built-in SecAgg+ protocol using the SuperLink/SuperNode architecture. However, because FedGuard uses a custom sequential simulation loop to bypass Ray multiprocessing bugs on Windows (AssignProcessToJobObject failed), we cannot natively run Flower's asynchronous SecAgg+ protocol in our simulation.

## Alternative Approaches
Currently, FedGuard relies on Local Differential Privacy (LDP) via Opacus and experimental update perturbation to protect data at the client level before it reaches the server. In a production environment with physically distributed nodes (e.g. Linux containers), Flower's SecAgg+ could be deployed to provide Cryptographic Secure Aggregation.
