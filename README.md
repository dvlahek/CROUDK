# CroUDC

**CroUDC: A Temporal Benchmark for Retrieval-Augmented Universal Decimal Classification from the Croatian National Bibliography**

CroUDC studies title-based Universal Decimal Classification (UDC) recommendation from professionally catalogued records of the Croatian National Bibliography, Series B.

This repository is currently a **development/reproducibility snapshot** for the Information Processing & Management manuscript. The predictive architecture is frozen, while bounded reviewer controls, the hierarchy-aware extension and the final 2023–2024 partial-volume holdout are still pending.

## Current result

The strongest frozen system is a candidate-level stacker that reranks the union of candidates from:

1. TF-IDF + SGD;
2. BERTić;
3. sparse historical retrieval.

Historical retrieval is restricted to the 2008–2019 training corpus for every 2020–2022 query.

| Year | Top-1 | Hit@5 | nDCG@5 |
|---|---:|---:|---:|
| 2021 | 0.2097 | 0.4466 | 0.2728 |
| 2022 | 0.1945 | 0.4440 | 0.2554 |

Calibrated selective prediction identifies a substantially stronger high-confidence subset. Aggregate results are provided under `results/`.

## Temporal protocol

```text
2008–2019  training + fixed historical retrieval index
2020       model selection, fusion learning, OOF calibration
2021       temporal development evaluation
2022       temporal development evaluation
2023–2024  untouched partial-volume holdout
```

The 2021 and 2022 sets are explicitly **temporal development evaluations**, not untouched final test sets, because their results were inspected during architecture development.

## Repository contents

```text
configs/      frozen configurations
src/          harvesting, preparation, models and evaluation
scripts/      reproduction wrappers
metadata/     aggregate corpus and audit metadata
results/      small aggregate result files
docs/         dataset, licensing and reproducibility documentation
data/         no redistributed record-level benchmark yet
```

## Data availability

The record-level CroUDC dataset is **not redistributed here at present**. Reconstruction code is provided while the final data-sharing arrangement with the National and University Library in Zagreb is being resolved.

The full proprietary UDC Master Reference File is not included.

See `docs/DATASET_CARD.md`, `docs/UDC_LICENSING.md`, and `docs/REPRODUCIBILITY.md`.

## Installation

Python 3.11+ is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

BERTić training requires PyTorch and Hugging Face Transformers and is most practical with a CUDA-capable GPU.

## Development status

The current repository intentionally excludes the final 2023–2024 holdout results and the official UDC hierarchy layer until those analyses are frozen.

## Licence

No code licence is granted by this development snapshot yet. A final code licence will be selected before the archival/publication release. Rights in the source bibliographic records and UDC resources are separate from the source-code licence.
