# FedGuard Privacy Strategies

## Differential Privacy (Opacus)
FedGuard supports local differentially private SGD (DP-SGD) using Facebook's Opacus library. When a client trains locally, gradients are clipped to a maximum norm and random Gaussian noise is added before model updates are computed. This provides a formal mathematical guarantee ($\epsilon, \delta$) that an adversary cannot determine if a specific data record was present in the training set.

### Modes:
1. **Fixed Noise Mode**: Specify a noise multiplier directly.
2. **Target Epsilon Mode**: Specify a target privacy budget ($\epsilon$), and Opacus automatically calculates the required noise multiplier for the given epochs and dataset size.

## Trade-offs
Formal DP significantly reduces model precision. Heavy clipping restricts the influence of rare features (which are often the most important in intrusion detection). You will notice lower F1 scores and higher False Negative Rates when DP is enabled. There is a fundamental trade-off between privacy and utility.

## Limitations
- **Global Evaluation**: While client training is private, the global model is evaluated centrally on normal data in this simulation. In a real environment, evaluation would also be federated or synthetic.
- **Secure Aggregation**: Due to Windows multiprocessing constraints bypassing Ray, the Flower SuperLink/SuperNode SecAgg+ protocol is not actively executed in the simulation loop. Instead, data is protected via LDP before leaving the client.

