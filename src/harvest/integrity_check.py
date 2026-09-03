#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
from collections import Counter
from pathlib import Path


def read_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                pass


def main():
    ap = argparse.ArgumentParser(
        description="CroUDC integrity check: failed IDs minus successfully parsed IDs."
    )
    ap.add_argument("--records", default=r"data_nsk\processed\croudc_records.jsonl")
    ap.add_argument("--failures", default=r"data_nsk\reports\parse_failures.jsonl")
    ap.add_argument("--out", default=r"data_nsk\reports\integrity_check")
    args = ap.parse_args()

    records_path = Path(args.records)
    failures_path = Path(args.failures)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if not records_path.exists():
        raise SystemExit(f"Missing records file: {records_path}")
    if not failures_path.exists():
        raise SystemExit(f"Missing failures file: {failures_path}")

    success_ids = set()
    success_counter = Counter()
    for row in read_jsonl(records_path):
        rid = str(row.get("record_id") or "").strip().upper()
        if rid:
            success_ids.add(rid)
            success_counter[rid] += 1

    failure_counter = Counter()
    failure_rows_by_id = {}
    total_failure_rows = 0
    for row in read_jsonl(failures_path):
        total_failure_rows += 1
        rid = str(row.get("record_id") or "").strip().upper()
        if rid:
            failure_counter[rid] += 1
            failure_rows_by_id.setdefault(rid, row)

    failed_ids = set(failure_counter)
    failed_only = failed_ids - success_ids
    overlap = failed_ids & success_ids
    success_only = success_ids - failed_ids

    with (out / "failed_only_ids.txt").open("w", encoding="utf-8") as f:
        for rid in sorted(failed_only):
            f.write(rid + "\n")

    with (out / "failed_only_records.jsonl").open("w", encoding="utf-8") as f:
        for rid in sorted(failed_only):
            row = dict(failure_rows_by_id[rid])
            row["failure_occurrences"] = failure_counter[rid]
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    failed_only_occurrences = sum(failure_counter[rid] for rid in failed_only)
    overlap_occurrences = sum(failure_counter[rid] for rid in overlap)

    report = {
        "success_rows": sum(success_counter.values()),
        "unique_success_ids": len(success_ids),
        "failure_rows": total_failure_rows,
        "unique_failure_ids": len(failed_ids),
        "unique_failed_ids_also_successfully_parsed": len(overlap),
        "unique_failed_only_ids": len(failed_only),
        "unique_success_only_ids": len(success_only),
        "failure_rows_belonging_to_already_successful_ids": overlap_occurrences,
        "failure_rows_belonging_to_failed_only_ids": failed_only_occurrences,
        "failed_only_fraction_of_unique_failure_ids": (
            len(failed_only) / len(failed_ids) if failed_ids else 0.0
        ),
        "failed_only_fraction_relative_to_success_corpus": (
            len(failed_only) / len(success_ids) if success_ids else 0.0
        ),
    }

    (out / "integrity_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
