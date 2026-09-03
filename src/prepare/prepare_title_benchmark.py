#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prepare CroUDC benchmark data from the NSK harvester JSONL.

Main principles
---------------
- Primary input: title, optionally Hrčak abstract.
- NSK professional subject headings are NOT used in the primary track.
- Temporal split only.
- Retrieval candidates for a test document must come from older training records.
- Raw UDC labels are preserved.

Outputs
-------
prepared/
  train.jsonl
  val.jsonl
  test.jsonl
  future.jsonl
  label_stats.csv
  split_stats.json
"""

from __future__ import annotations
import argparse, csv, json, re
from collections import Counter
from pathlib import Path

BASIC_UDC_RE = re.compile(r"^\d+(?:\.\d+)*$")


def read_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def write_jsonl(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def clean_text(x):
    return re.sub(r"\s+", " ", (x or "")).strip()


def usable_text(r, track):
    title = clean_text(r.get("title_primary") or r.get("title_line") or "")
    abstract = clean_text(r.get("hrcak_abstract") or "")
    if track == "title":
        return title
    if track == "title_abstract":
        return (title + "\n" + abstract).strip()
    raise ValueError(track)


def valid_labels(r):
    xs = r.get("udc") or []
    return [clean_text(x) for x in xs if clean_text(x)]


def basic_or_compound(u):
    return "basic" if BASIC_UDC_RE.fullmatch(u) else "compound"


def normalize_record(r, track):
    labels = valid_labels(r)
    text = usable_text(r, track)
    return {
        "record_id": r.get("record_id"),
        "year": r.get("year"),
        "text": text,
        "title": clean_text(r.get("title_primary") or r.get("title_line") or ""),
        "abstract": clean_text(r.get("hrcak_abstract") or ""),
        "labels": labels,
        "label_types": [basic_or_compound(u) for u in labels],
        "journal": clean_text(r.get("journal_title") or ""),
        "issn": clean_text(r.get("issn") or ""),
        "source_record": r,
    }


def infer_default_splits(year_counts):
    years = sorted(y for y, n in year_counts.items() if n > 0)
    if len(years) < 4:
        raise ValueError("Need at least 4 populated years for temporal train/val/test/future splits.")
    future = years[-1]
    test = years[-2]
    val = years[-3]
    train_max = years[-4]
    return train_max, val, test, future


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="croudc_records.jsonl")
    ap.add_argument("--out", default="prepared")
    ap.add_argument("--track", choices=["title", "title_abstract"], default="title")
    ap.add_argument("--train-max-year", type=int)
    ap.add_argument("--val-year", type=int)
    ap.add_argument("--test-year", type=int)
    ap.add_argument("--future-year", type=int)
    ap.add_argument("--require-abstract", action="store_true")
    ap.add_argument("--min-label-count-train", type=int, default=1)
    args = ap.parse_args()

    rows = []
    for raw in read_jsonl(args.input):
        try:
            int(raw.get("year"))
        except Exception:
            continue
        r = normalize_record(raw, args.track)
        if not r["record_id"] or not r["text"] or not r["labels"]:
            continue
        if args.require_abstract and not r["abstract"]:
            continue
        rows.append(r)

    yc = Counter(r["year"] for r in rows)
    if not yc:
        raise SystemExit("No usable records.")

    if all(v is not None for v in [args.train_max_year, args.val_year, args.test_year, args.future_year]):
        train_max, val_year, test_year, future_year = (
            args.train_max_year, args.val_year, args.test_year, args.future_year
        )
    else:
        train_max, val_year, test_year, future_year = infer_default_splits(yc)

    if not (train_max < val_year < test_year < future_year):
        raise SystemExit("Need train_max_year < val_year < test_year < future_year.")

    train = [r for r in rows if r["year"] <= train_max]
    val = [r for r in rows if r["year"] == val_year]
    test = [r for r in rows if r["year"] == test_year]
    future = [r for r in rows if r["year"] == future_year]

    train_lc = Counter(u for r in train for u in r["labels"])
    keep = {u for u, c in train_lc.items() if c >= args.min_label_count_train}
    for split in [train, val, test, future]:
        for r in split:
            r["labels_seen_train"] = [u for u in r["labels"] if u in keep]
            r["labels_unseen_train"] = [u for u in r["labels"] if u not in keep]

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    write_jsonl(out / "train.jsonl", train)
    write_jsonl(out / "val.jsonl", val)
    write_jsonl(out / "test.jsonl", test)
    write_jsonl(out / "future.jsonl", future)

    with open(out / "label_stats.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["udc", "train_count"])
        for u, c in train_lc.most_common():
            w.writerow([u, c])

    stats = {
        "track": args.track,
        "train_max_year": train_max,
        "val_year": val_year,
        "test_year": test_year,
        "future_year": future_year,
        "n_train": len(train),
        "n_val": len(val),
        "n_test": len(test),
        "n_future": len(future),
        "n_train_labels": len(train_lc),
        "year_counts_usable": dict(sorted(yc.items())),
        "unseen_label_fraction_test": (
            sum(len(r["labels_unseen_train"]) for r in test) /
            max(1, sum(len(r["labels"]) for r in test))
        ),
        "unseen_label_fraction_future": (
            sum(len(r["labels_unseen_train"]) for r in future) /
            max(1, sum(len(r["labels"]) for r in future))
        ),
    }
    (out / "split_stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
