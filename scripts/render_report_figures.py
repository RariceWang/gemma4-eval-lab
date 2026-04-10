#!/usr/bin/env python3
"""Render report-ready figures from the generated report packet tables."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render report figures from report_packet tables.")
    parser.add_argument("--packet-dir", required=True, help="Directory produced by build_report_packet.py")
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def to_float(text: str) -> float:
    text = text.strip()
    if text.endswith("%"):
        return float(text[:-1]) / 100.0
    return float(text)


def configure_matplotlib() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 180,
            "savefig.dpi": 220,
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "legend.fontsize": 9,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
        }
    )


def render_shared_quality(path: Path) -> None:
    rows = read_csv(path / "table_official_shared_benchmarks.csv")
    benchmarks = [row["Benchmark"] for row in rows]
    e4b_scores = [to_float(row["E4B 得分"]) for row in rows]
    b26_scores = [to_float(row["26B 得分"]) for row in rows]
    e4b_completion = [to_float(row["E4B 完成率"]) for row in rows]
    b26_completion = [to_float(row["26B 完成率"]) for row in rows]

    x = np.arange(len(benchmarks))
    width = 0.36

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    score_ax, completion_ax = axes

    score_ax.bar(x - width / 2, e4b_scores, width, label="Gemma 4 E4B", color="#3465a4")
    score_ax.bar(x + width / 2, b26_scores, width, label="Gemma 4 26B", color="#cc4e00")
    score_ax.set_title("Figure 1a. Shared Benchmark Scores")
    score_ax.set_ylabel("Score")
    score_ax.set_xticks(x)
    score_ax.set_xticklabels(benchmarks, rotation=20, ha="right")
    score_ax.set_ylim(0, 1.1)
    score_ax.grid(axis="y", linestyle="--", alpha=0.35)
    score_ax.legend(frameon=False, loc="upper left")

    completion_ax.bar(x - width / 2, e4b_completion, width, label="Gemma 4 E4B", color="#3465a4")
    completion_ax.bar(x + width / 2, b26_completion, width, label="Gemma 4 26B", color="#cc4e00")
    completion_ax.set_title("Figure 1b. Shared Benchmark Completion Rates")
    completion_ax.set_ylabel("Completion Rate")
    completion_ax.set_xticks(x)
    completion_ax.set_xticklabels(benchmarks, rotation=20, ha="right")
    completion_ax.set_ylim(0, 1.1)
    completion_ax.grid(axis="y", linestyle="--", alpha=0.35)

    fig.savefig(path / "figure_shared_quality.png", bbox_inches="tight")
    plt.close(fig)


def render_shared_latency(path: Path) -> None:
    rows = read_csv(path / "table_official_shared_benchmarks.csv")
    benchmarks = [row["Benchmark"] for row in rows]
    e4b_latency = [to_float(row["E4B 平均时延(s)"]) for row in rows]
    b26_latency = [to_float(row["26B 平均时延(s)"]) for row in rows]

    x = np.arange(len(benchmarks))
    width = 0.36

    fig, ax = plt.subplots(figsize=(8.8, 4.5), constrained_layout=True)
    ax.bar(x - width / 2, e4b_latency, width, label="Gemma 4 E4B", color="#3465a4")
    ax.bar(x + width / 2, b26_latency, width, label="Gemma 4 26B", color="#cc4e00")
    ax.set_title("Figure 2. Shared Benchmark Latency (log scale)")
    ax.set_ylabel("Latency (seconds, log scale)")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(benchmarks, rotation=20, ha="right")
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.legend(frameon=False, loc="upper left")

    fig.savefig(path / "figure_shared_latency.png", bbox_inches="tight")
    plt.close(fig)


def render_heavy_cases(path: Path) -> None:
    rows = read_csv(path / "table_heavy_case_studies.csv")
    cases = [row["Benchmark"] for row in rows]
    false_latency = [to_float(row["think=false 时延(s)"]) for row in rows]
    true_latency = [to_float(row["think=true 时延(s)"]) for row in rows]
    true_thinking = [to_float(row["think=true thinking 字符"]) for row in rows]

    x = np.arange(len(cases))
    width = 0.36

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    latency_ax, thinking_ax = axes

    latency_ax.bar(x - width / 2, false_latency, width, label="think=false", color="#4e9a06")
    latency_ax.bar(x + width / 2, true_latency, width, label="think=true", color="#cc4e00")
    latency_ax.set_title("Figure 3a. Heavy-Task Latency")
    latency_ax.set_ylabel("Latency (seconds, log scale)")
    latency_ax.set_yscale("log")
    latency_ax.set_xticks(x)
    latency_ax.set_xticklabels(cases, rotation=18, ha="right")
    latency_ax.grid(axis="y", linestyle="--", alpha=0.35)
    latency_ax.legend(frameon=False, loc="upper left")

    thinking_ax.bar(x, true_thinking, width=0.52, color="#75507b")
    thinking_ax.set_title("Figure 3b. think=true Thinking Length")
    thinking_ax.set_ylabel("Thinking characters")
    thinking_ax.set_xticks(x)
    thinking_ax.set_xticklabels(cases, rotation=18, ha="right")
    thinking_ax.grid(axis="y", linestyle="--", alpha=0.35)

    fig.savefig(path / "figure_heavy_cases.png", bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    args = parse_args()
    packet_dir = Path(args.packet_dir)
    configure_matplotlib()
    render_shared_quality(packet_dir)
    render_shared_latency(packet_dir)
    render_heavy_cases(packet_dir)
    print(f"Saved figures to {packet_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
