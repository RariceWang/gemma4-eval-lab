#!/usr/bin/env python3
"""Aggregate one or more benchmark_runner outputs into compact CSV reports."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate frontier eval outputs.")
    parser.add_argument("--runs", nargs="+", required=True, help="Output run directories")
    parser.add_argument("--out", required=True, help="Output directory for aggregated reports")
    return parser.parse_args()


def load_run_meta(run_dir: str) -> dict[str, Any]:
    path = Path(run_dir) / "metadata.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def think_mode_label(value: Any) -> str:
    if value is True:
        return "think_true"
    if value is False:
        return "think_false"
    return "unknown"


def load_rows(run_dirs: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run_dir in run_dirs:
        meta = load_run_meta(run_dir)
        default_think = meta.get("options", {}).get("think")
        path = Path(run_dir) / "raw_outputs.jsonl"
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                record = json.loads(line)
                record["run_dir"] = run_dir
                record["run_name"] = Path(run_dir).name
                record["dataset"] = meta.get("dataset", "")
                record["think_enabled"] = record.get("think_enabled", default_think)
                record["think_mode"] = think_mode_label(record["think_enabled"])
                rows.append(record)
    return rows


def mean(values: list[float]) -> str:
    if not values:
        return ""
    return f"{sum(values) / len(values):.4f}"


def rate(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return ""
    return f"{numerator / denominator:.4f}"


def write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def task_level_rows(rows: list[dict[str, Any]]) -> list[list[str]]:
    out_rows: list[list[str]] = []
    for row in sorted(
        rows,
        key=lambda item: (
            str(item.get("model", "")),
            str(item.get("think_mode", "")),
            str(item.get("benchmark", "")),
            str(item.get("task_id", "")),
        ),
    ):
        first_thinking = row.get("first_thinking_sec")
        first_response = row.get("first_response_sec")
        latency = row.get("latency_sec")
        think_to_response_gap = (
            round(first_response - first_thinking, 4)
            if first_response is not None and first_thinking is not None
            else ""
        )
        thinking_tail = (
            round(latency - first_thinking, 4)
            if latency is not None and first_thinking is not None
            else ""
        )
        out_rows.append(
            [
                row.get("run_name", ""),
                row.get("dataset", ""),
                row.get("model", ""),
                row.get("think_mode", ""),
                row.get("task_id", ""),
                row.get("benchmark", ""),
                row.get("group", ""),
                row.get("language", ""),
                row.get("status", ""),
                str(row.get("score", "")) if row.get("score") is not None else "",
                str(latency) if latency is not None else "",
                str(first_thinking) if first_thinking is not None else "",
                str(first_response) if first_response is not None else "",
                str(think_to_response_gap),
                str(thinking_tail),
                str(row.get("prompt_chars", "")),
                str(row.get("thinking_chars", "")),
                str(row.get("response_chars", "")),
                row.get("parsed_response", ""),
                row.get("error", ""),
            ]
        )
    return out_rows


def aggregate(rows: list[dict[str, Any]], keys: list[str]) -> list[list[str]]:
    grouped: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row[key] for key in keys)].append(row)

    out_rows: list[list[str]] = []
    for group_key, items in sorted(grouped.items()):
        successes = [item for item in items if item["status"] == "ok"]
        long_think_count = sum(1 for item in items if item["status"] == "long_think")
        error_count = sum(1 for item in items if item["status"] == "error")
        scored = [item["score"] for item in items if item["score"] is not None]
        latencies = [item["latency_sec"] for item in items]
        first_thinking = [item["first_thinking_sec"] for item in items if item.get("first_thinking_sec") is not None]
        first_response = [item["first_response_sec"] for item in items if item.get("first_response_sec") is not None]
        think_to_response_gap = [
            item["first_response_sec"] - item["first_thinking_sec"]
            for item in items
            if item.get("first_thinking_sec") is not None and item.get("first_response_sec") is not None
        ]
        thinking_tail = [
            item["latency_sec"] - item["first_thinking_sec"]
            for item in items
            if item.get("latency_sec") is not None and item.get("first_thinking_sec") is not None
        ]
        out_rows.append(
            [
                *[str(part) for part in group_key],
                str(len(items)),
                str(len(successes)),
                rate(len(successes), len(items)),
                str(long_think_count),
                rate(long_think_count, len(items)),
                str(error_count),
                rate(error_count, len(items)),
                str(len(scored)),
                mean(scored),
                mean(latencies),
                mean(first_thinking),
                mean(first_response),
                mean(think_to_response_gap),
                mean(thinking_tail),
                mean([item["prompt_chars"] for item in items]),
                mean([item.get("thinking_chars", 0) for item in items]),
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
            "think_mode",
            "benchmark",
            "task_count",
            "success_count",
            "success_rate",
            "long_think_count",
            "long_think_rate",
            "error_count",
            "error_rate",
            "scored_count",
            "mean_score",
            "mean_latency_sec",
            "mean_first_thinking_sec",
            "mean_first_response_sec",
            "mean_think_to_response_gap_sec",
            "mean_thinking_tail_sec",
            "mean_prompt_chars",
            "mean_thinking_chars",
            "mean_response_chars",
        ],
        aggregate(rows, ["model", "think_mode", "benchmark"]),
    )

    write_csv(
        out_dir / "by_model_language.csv",
        [
            "model",
            "think_mode",
            "language",
            "task_count",
            "success_count",
            "success_rate",
            "long_think_count",
            "long_think_rate",
            "error_count",
            "error_rate",
            "scored_count",
            "mean_score",
            "mean_latency_sec",
            "mean_first_thinking_sec",
            "mean_first_response_sec",
            "mean_think_to_response_gap_sec",
            "mean_thinking_tail_sec",
            "mean_prompt_chars",
            "mean_thinking_chars",
            "mean_response_chars",
        ],
        aggregate(rows, ["model", "think_mode", "language"]),
    )

    write_csv(
        out_dir / "by_model_group.csv",
        [
            "model",
            "think_mode",
            "group",
            "task_count",
            "success_count",
            "success_rate",
            "long_think_count",
            "long_think_rate",
            "error_count",
            "error_rate",
            "scored_count",
            "mean_score",
            "mean_latency_sec",
            "mean_first_thinking_sec",
            "mean_first_response_sec",
            "mean_think_to_response_gap_sec",
            "mean_thinking_tail_sec",
            "mean_prompt_chars",
            "mean_thinking_chars",
            "mean_response_chars",
        ],
        aggregate(rows, ["model", "think_mode", "group"]),
    )

    write_csv(
        out_dir / "by_model_think.csv",
        [
            "model",
            "think_mode",
            "task_count",
            "success_count",
            "success_rate",
            "long_think_count",
            "long_think_rate",
            "error_count",
            "error_rate",
            "scored_count",
            "mean_score",
            "mean_latency_sec",
            "mean_first_thinking_sec",
            "mean_first_response_sec",
            "mean_think_to_response_gap_sec",
            "mean_thinking_tail_sec",
            "mean_prompt_chars",
            "mean_thinking_chars",
            "mean_response_chars",
        ],
        aggregate(rows, ["model", "think_mode"]),
    )

    write_csv(
        out_dir / "task_level.csv",
        [
            "run_name",
            "dataset",
            "model",
            "think_mode",
            "task_id",
            "benchmark",
            "group",
            "language",
            "status",
            "score",
            "latency_sec",
            "first_thinking_sec",
            "first_response_sec",
            "think_to_response_gap_sec",
            "thinking_tail_sec",
            "prompt_chars",
            "thinking_chars",
            "response_chars",
            "parsed_response",
            "error",
        ],
        task_level_rows(rows),
    )

    print(f"Saved aggregate reports to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
