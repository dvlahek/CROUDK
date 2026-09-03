# CroUDC dataset card

## Scope

CroUDC is a temporal research benchmark derived from publicly accessible Croatian National Bibliography, Series B (HNB Niz B) records.

Current harvest snapshot:

- 154,210 unique bibliographic records;
- 153,823 with at least one UDC assignment;
- 66,611 multi-label records;
- 232,093 UDC assignments;
- 808 distinct raw UDC strings in the full harvested snapshot.

The primary benchmark is title-only.

## Temporal protocol

- 2008-2019: supervised training and fixed historical retrieval index
- 2020: model selection, fusion learning, OOF calibration
- 2021: temporal development evaluation
- 2022: temporal development evaluation
- 2023-2024: untouched partial-volume holdout

The 2021 and 2022 sets are explicitly **development temporal evaluations**, not untouched final test sets, because their results were inspected during architecture development.

## CroUDC-Core

The current primary target vocabulary contains 254 UDC labels with at least 10 occurrences in the 2008-2019 training period.

Rare and unseen labels are not conceptually removed from CroUDC. They belong to the LongTail/Open setting.

## Redistribution

Record-level files are intentionally absent from this repository pending the final NSK data-sharing decision. Aggregate statistics, code and small non-record-level result files may be released separately.

## Important limitations

Bibliography year is the HNB volume year and should not automatically be equated with original article publication year. The 2023-2024 public coverage is partial.
