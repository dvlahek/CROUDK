# Reproducibility

This repository is an **interim reproducibility snapshot**. The predictive architecture is frozen, while bounded post-freeze reviewer controls and the UDC hierarchy analysis are still pending.

## What is frozen now

1. title-only temporal benchmark definition;
2. TF-IDF + SGD baseline configuration;
3. sparse historical retrieval configuration;
4. BERTić baseline configuration used by the frozen fusion system;
5. candidate-level stacking configuration;
6. OOF isotonic calibration procedure;
7. 2021/2022 development evaluation protocol;
8. source-clustered bootstrap audit.

The full executable pipeline will be expanded in this repository as the remaining post-freeze controls are completed.

## Holdout protection

The reserved 2023-2024 partial public volumes must remain outside all tuning decisions. The final holdout evaluation will be documented and added only after the hierarchy-aware protocol, normalization policy and reported metrics are frozen.
