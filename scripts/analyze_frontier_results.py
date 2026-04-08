#!/usr/bin/env python3
"""Aggregate one or more benchmark_runner outputs into compact CSV reports."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate frontier eval outputs.")
    parser.add_argument("--runs", nargs="+", required=True, help="Output run directories")
    parser.add_argument("--out", required=True, help="Output directory for aggregated reports")
    return parser.parse_args()


def load_rows(run_dirs: list[str]) -> list[dict]:
    rows: list[dict] = []
    for run_dir in run_dirs:
        path = Path(run_dir) / "raw_outputs.jsonl"
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                record = json.loads(line)
                record["run_dir"] = run_dir
                rows.append(record)
    return rows


def mean(values: list[float]) -> str:
    if not values:
        return ""
    return f"{sum(values) / len(values):.4f}"


def write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def aggregate(rows: list[dict], keys: list[str]) -> list[list[str]]:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row[key] for key in keys)].append(row)

    out_rows: list[list[str]] = []
    for group_key, items in sorted(grouped.items()):
        successes = [item for item in items if item["status"] == "ok"]
        scored = [item["score"] for item in items if item["score"] is not None]
        latencies = [item["latency_sec"] for item in items]
        out_rows.append(
            [
                *[str(part) for part in group_key],
                str(len(items)),
                str(len(successes)),
                mean(scored),
                mean(latencies),
                mean([item["prompt_chars"] for item in items]),
                mean([item["response_chars"] for item in items]),
            ]
        )
    return out_rows


def main() -> int:
    args = parse_args()
    rows = load_rows(args.runs)
    out_dir = Path(args.out)

    write_csv(
        out_dir / "by_model_benchmark.csv",
        [
            "model",
            "benchmark",
            "task_count",
            "success_count",
            "mean_score",
            "mean_latency_sec",
            "mean_prompt_chars",
            "mean_response_chars",
        ],
        aggregate(rows, ["model", "benchmark"]),
    )

    write_csv(
        out_dir / "by_model_language.csv",
        [
            "model",
            "language",
            "task_count",
            "success_count",
            "mean_score",
            "mean_latency_sec",
            "mean_prompt_chars",
            "mean_response_chars",
        ],
        aggregate(rows, ["model", "language"]),
    )

    write_csv(
        out_dir / "by_model_group.csv",
        [
            "model",
            "group",
            "task_count",
            "success_count",
            "mean_score",
            "mean_latency_sec",
            "mean_prompt_chars",
            "mean_response_chars",
        ],
        aggregate(rows, ["model", "group"]),
    )

    print(f"Saved aggregate reports to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
