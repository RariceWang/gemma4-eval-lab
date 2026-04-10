#!/usr/bin/env python3
"""Build report-ready tables and figure data from current frontier eval outputs."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


BENCHMARK_ORDER = [
    "mmlu_cf",
    "mmlu_pro",
    "mmlu_prox_lite_en",
    "mmlu_prox_lite_zh",
    "mmlu_prox_lite_sw",
    "livebench_reasoning",
    "simpleqa",
]

BENCHMARK_META = {
    "mmlu_cf": {
        "label": "MMLU-CF",
        "group_cn": "污染受控知识推理",
        "metric": "Accuracy",
        "note": "显式控制 benchmark contamination。",
    },
    "mmlu_pro": {
        "label": "MMLU-Pro",
        "group_cn": "高难知识与推理",
        "metric": "Exact Match",
        "note": "高难客观题，区分度高于经典 MMLU。",
    },
    "mmlu_prox_lite_en": {
        "label": "MMLU-ProX-Lite (EN)",
        "group_cn": "多语言高级推理",
        "metric": "Exact Match",
        "note": "英文多语言高级推理子集。",
    },
    "mmlu_prox_lite_zh": {
        "label": "MMLU-ProX-Lite (ZH)",
        "group_cn": "多语言高级推理",
        "metric": "Exact Match",
        "note": "中文多语言高级推理子集。",
    },
    "mmlu_prox_lite_sw": {
        "label": "MMLU-ProX-Lite (SW)",
        "group_cn": "多语言高级推理",
        "metric": "Exact Match",
        "note": "斯瓦希里语多语言高级推理子集。",
    },
    "livebench_reasoning": {
        "label": "LiveBench Reasoning",
        "group_cn": "动态推理",
        "metric": "Exact Match",
        "note": "动态更新 benchmark，污染风险更低。",
    },
    "simpleqa": {
        "label": "SimpleQA",
        "group_cn": "短事实问答",
        "metric": "SimpleQA Match",
        "note": "本地近似 factuality 评分。",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build report packet from frontier eval outputs.")
    parser.add_argument("--models-json", default="configs/models.json", help="Path to models.json.")
    parser.add_argument(
        "--official-dir",
        default="outputs/frontier_analysis_official_extended_20260409",
        help="Directory containing official extended analysis outputs.",
    )
    parser.add_argument(
        "--heavy-dir",
        default="outputs/frontier_analysis_heavy_compare_20260409",
        help="Directory containing heavy compare analysis outputs.",
    )
    parser.add_argument(
        "--e4b-raw",
        default="outputs/frontier_pilot_e4b_thinktrue_ctx256k_20260408/raw_outputs.jsonl",
        help="Raw output file for Gemma 4 E4B think=true runs used in smoke-level shared-task comparison.",
    )
    parser.add_argument(
        "--qwen9b-raw",
        default="outputs/frontier_smoke_qwen35_9b_thinktrue_ctx256k_20260409/raw_outputs.jsonl",
        help="Raw output file for Qwen 3.5 9B smoke runs.",
    )
    parser.add_argument("--out", required=True, help="Output directory for report-ready artifacts.")
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def to_markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    table = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        table.append("| " + " | ".join(row) + " |")
    return "\n".join(table) + "\n"


def fnum(text: str, digits: int = 4) -> str:
    if text == "":
        return "-"
    return f"{float(text):.{digits}f}"


def fpct(text: str) -> str:
    if text == "":
        return "-"
    return f"{float(text) * 100:.1f}%"


def benchmark_sort_key(name: str) -> tuple[int, str]:
    try:
        return (BENCHMARK_ORDER.index(name), name)
    except ValueError:
        return (len(BENCHMARK_ORDER), name)


def build_model_table(models_json: Path) -> tuple[list[str], list[list[str]]]:
    models = json.loads(models_json.read_text(encoding="utf-8"))
    rows: list[list[str]] = []
    for model in models:
        if not model.get("default_local", False):
            continue
        rows.append(
            [
                model["label"],
                model["id"],
                f"{model['params_b']}",
                str(model["context_length"]),
                model["quantization"],
                model["notes"],
            ]
        )
    header = ["模型", "Model ID", "参数规模(B)", "上下文长度", "量化", "说明"]
    return header, rows


def build_benchmark_table() -> tuple[list[str], list[list[str]]]:
    rows = []
    for benchmark in BENCHMARK_ORDER:
        meta = BENCHMARK_META.get(benchmark)
        if meta is None:
            continue
        rows.append([meta["label"], meta["group_cn"], meta["metric"], meta["note"]])
    header = ["Benchmark", "任务类型", "主指标", "备注"]
    return header, rows


def build_official_tables(official_rows: list[dict[str, str]]) -> dict[str, Any]:
    think_true_rows = [row for row in official_rows if row.get("think_mode") == "think_true"]
    by_key = {(row["model"], row["benchmark"]): row for row in think_true_rows}
    models = sorted({row["model"] for row in think_true_rows})
    model_labels = {
        "gemma4:e4b": "Gemma 4 E4B",
        "gemma4:26b": "Gemma 4 26B",
        "qwen3.5:9b": "Qwen 3.5 9B",
        "qwen3.5:27b": "Qwen 3.5 27B",
    }

    flattened_rows: list[list[str]] = []
    for row in sorted(think_true_rows, key=lambda item: (item["model"], benchmark_sort_key(item["benchmark"]))):
        meta = BENCHMARK_META.get(row["benchmark"], {})
        flattened_rows.append(
            [
                model_labels.get(row["model"], row["model"]),
                meta.get("label", row["benchmark"]),
                fpct(row["success_rate"]),
                fnum(row["mean_score"]),
                fnum(row["mean_latency_sec"], 2),
                fnum(row["mean_thinking_chars"], 0),
                row["long_think_count"],
            ]
        )

    shared = set.intersection(*(set(row["benchmark"] for row in think_true_rows if row["model"] == model) for model in models))
    shared_rows: list[list[str]] = []
    figure_rows: list[list[str]] = []
    summary_lines = ["# Report Summary", "", "## 共享 benchmark 对比", ""]
    for benchmark in sorted(shared, key=benchmark_sort_key):
        left = by_key[("gemma4:e4b", benchmark)]
        right = by_key[("gemma4:26b", benchmark)]
        meta = BENCHMARK_META.get(benchmark, {})
        shared_rows.append(
            [
                meta.get("label", benchmark),
                fnum(left["mean_score"]),
                fpct(left["success_rate"]),
                fnum(left["mean_latency_sec"], 2),
                fnum(left["mean_thinking_chars"], 0),
                fnum(right["mean_score"]),
                fpct(right["success_rate"]),
                fnum(right["mean_latency_sec"], 2),
                fnum(right["mean_thinking_chars"], 0),
            ]
        )
        figure_rows.append([meta.get("label", benchmark), "Gemma 4 E4B", "score", fnum(left["mean_score"])])
        figure_rows.append([meta.get("label", benchmark), "Gemma 4 E4B", "latency_sec", fnum(left["mean_latency_sec"], 4)])
        figure_rows.append([meta.get("label", benchmark), "Gemma 4 E4B", "completion_rate", fnum(left["success_rate"], 4)])
        figure_rows.append([meta.get("label", benchmark), "Gemma 4 26B", "score", fnum(right["mean_score"])])
        figure_rows.append([meta.get("label", benchmark), "Gemma 4 26B", "latency_sec", fnum(right["mean_latency_sec"], 4)])
        figure_rows.append([meta.get("label", benchmark), "Gemma 4 26B", "completion_rate", fnum(right["success_rate"], 4)])

        score_cmp = "更高" if float(right["mean_score"]) > float(left["mean_score"]) else ("持平" if float(right["mean_score"]) == float(left["mean_score"]) else "更低")
        completion_cmp = "更低" if float(right["success_rate"]) < float(left["success_rate"]) else ("持平" if float(right["success_rate"]) == float(left["success_rate"]) else "更高")
        latency_ratio = float(right["mean_latency_sec"]) / float(left["mean_latency_sec"])
        summary_lines.append(
            f"- {meta.get('label', benchmark)}: `26B` 得分{score_cmp}，完成率{completion_cmp}，平均时延约为 `E4B` 的 `{latency_ratio:.1f}x`。"
        )

    shared_header = [
        "Benchmark",
        "E4B 得分",
        "E4B 完成率",
        "E4B 平均时延(s)",
        "E4B 平均 thinking 字符",
        "26B 得分",
        "26B 完成率",
        "26B 平均时延(s)",
        "26B 平均 thinking 字符",
    ]
    flat_header = ["模型", "Benchmark", "完成率", "得分", "平均时延(s)", "平均 thinking 字符", "long_think 数"]
    figure_header = ["benchmark", "model", "metric", "value"]
    return {
        "flat_header": flat_header,
        "flat_rows": flattened_rows,
        "shared_header": shared_header,
        "shared_rows": shared_rows,
        "figure_header": figure_header,
        "figure_rows": figure_rows,
        "summary_text": "\n".join(summary_lines) + "\n",
    }


def build_heavy_case_table(heavy_task_rows: list[dict[str, str]]) -> tuple[list[str], list[list[str]], str]:
    grouped: dict[str, dict[str, dict[str, str]]] = {}
    for row in heavy_task_rows:
        grouped.setdefault(row["task_id"], {})[row["think_mode"]] = row

    header = [
        "Task ID",
        "Benchmark",
        "语言",
        "think=false 状态",
        "think=false 得分",
        "think=false 时延(s)",
        "think=true 状态",
        "think=true 得分",
        "think=true 时延(s)",
        "think=true thinking 字符",
    ]
    rows: list[list[str]] = []
    summary = ["## Heavy Case Study", ""]
    for task_id, item in sorted(grouped.items(), key=lambda kv: benchmark_sort_key(next(iter(kv[1].values()))["benchmark"])):
        false_row = item.get("think_false", {})
        true_row = item.get("think_true", {})
        benchmark = false_row.get("benchmark") or true_row.get("benchmark", "")
        label = BENCHMARK_META.get(benchmark, {}).get("label", benchmark)
        rows.append(
            [
                task_id,
                label,
                false_row.get("language") or true_row.get("language", ""),
                false_row.get("status", "-"),
                false_row.get("score", "-") or "-",
                fnum(false_row.get("latency_sec", ""), 2),
                true_row.get("status", "-"),
                true_row.get("score", "-") or "-",
                fnum(true_row.get("latency_sec", ""), 2),
                fnum(true_row.get("thinking_chars", ""), 0),
            ]
        )
        summary.append(
            f"- {label} / {task_id}: `think=false` 为 `{false_row.get('status', '-')}`，"
            f"`think=true` 为 `{true_row.get('status', '-')}`，后者 thinking 约 `{fnum(true_row.get('thinking_chars', ''), 0)}` 字。"
        )
    return header, rows, "\n".join(summary) + "\n"


def build_qwen_smoke_compare(
    e4b_rows: list[dict[str, Any]],
    qwen_rows: list[dict[str, Any]],
) -> tuple[list[str], list[list[str]], str]:
    e4b_by_id = {row["task_id"]: row for row in e4b_rows}
    shared_ids = sorted({row["task_id"] for row in qwen_rows if row["task_id"] in e4b_by_id})
    header = [
        "Task ID",
        "Benchmark",
        "E4B 状态",
        "E4B 得分",
        "E4B 时延(s)",
        "Qwen 9B 状态",
        "Qwen 9B 得分",
        "Qwen 9B 时延(s)",
        "Qwen 9B thinking 字符",
    ]
    rows: list[list[str]] = []
    summary_lines = ["## Qwen 9B vs E4B Shared-Task Comparison", ""]
    for task_id in shared_ids:
        left = e4b_by_id[task_id]
        right = next(row for row in qwen_rows if row["task_id"] == task_id)
        benchmark = right["benchmark"]
        label = BENCHMARK_META.get(benchmark, {}).get("label", benchmark)
        rows.append(
            [
                task_id,
                label,
                left["status"],
                "-" if left["score"] is None else str(left["score"]),
                f"{left['latency_sec']:.2f}",
                right["status"],
                "-" if right["score"] is None else str(right["score"]),
                f"{right['latency_sec']:.2f}",
                str(right["thinking_chars"]),
            ]
        )
        summary_lines.append(
            f"- {label} / {task_id}: `E4B` 为 `{left['status']}`、`Qwen 9B` 为 `{right['status']}`，"
            f"后者时延 `{right['latency_sec']:.2f}s`，thinking 约 `{right['thinking_chars']}` 字。"
        )
    return header, rows, "\n".join(summary_lines) + "\n"


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    official_rows = read_csv(Path(args.official_dir) / "by_model_benchmark.csv")
    heavy_task_rows = read_csv(Path(args.heavy_dir) / "task_level.csv")
    e4b_raw_rows = read_jsonl(Path(args.e4b_raw))
    qwen9b_raw_rows = read_jsonl(Path(args.qwen9b_raw))

    model_header, model_rows = build_model_table(Path(args.models_json))
    benchmark_header, benchmark_rows = build_benchmark_table()
    official = build_official_tables(official_rows)
    heavy_header, heavy_rows, heavy_summary = build_heavy_case_table(heavy_task_rows)
    qwen_header, qwen_rows, qwen_summary = build_qwen_smoke_compare(e4b_raw_rows, qwen9b_raw_rows)

    write_csv(out_dir / "table_model_overview.csv", model_header, model_rows)
    write_text(out_dir / "table_model_overview.md", to_markdown_table(model_header, model_rows))

    write_csv(out_dir / "table_benchmark_overview.csv", benchmark_header, benchmark_rows)
    write_text(out_dir / "table_benchmark_overview.md", to_markdown_table(benchmark_header, benchmark_rows))

    write_csv(out_dir / "table_official_all_rows.csv", official["flat_header"], official["flat_rows"])
    write_text(out_dir / "table_official_all_rows.md", to_markdown_table(official["flat_header"], official["flat_rows"]))

    write_csv(out_dir / "table_official_shared_benchmarks.csv", official["shared_header"], official["shared_rows"])
    write_text(out_dir / "table_official_shared_benchmarks.md", to_markdown_table(official["shared_header"], official["shared_rows"]))

    write_csv(out_dir / "table_heavy_case_studies.csv", heavy_header, heavy_rows)
    write_text(out_dir / "table_heavy_case_studies.md", to_markdown_table(heavy_header, heavy_rows))

    write_csv(out_dir / "table_qwen9b_e4b_shared_smoke.csv", qwen_header, qwen_rows)
    write_text(out_dir / "table_qwen9b_e4b_shared_smoke.md", to_markdown_table(qwen_header, qwen_rows))

    write_csv(out_dir / "figure_shared_quality_latency.csv", official["figure_header"], official["figure_rows"])

    summary_text = (
        "# Report Packet\n\n"
        "本目录汇总了当前可直接用于课程报告写作的主表与作图数据。\n\n"
        "## 内容\n\n"
        "- `table_model_overview.*`: 模型基本信息\n"
        "- `table_benchmark_overview.*`: benchmark 与指标说明\n"
        "- `table_official_all_rows.*`: 正式结果逐模型逐 benchmark 主表\n"
        "- `table_official_shared_benchmarks.*`: `E4B` 与 `26B` 在共享 benchmark 上的对照主表\n"
        "- `table_heavy_case_studies.*`: heavy 阶段 `think=false` vs `think=true` 案例表\n"
        "- `table_qwen9b_e4b_shared_smoke.*`: `Qwen 9B` 与 `E4B` 的共享 smoke 任务对照表\n"
        "- `figure_shared_quality_latency.csv`: 共享 benchmark 的得分/完成率/时延作图数据\n\n"
        f"{official['summary_text']}\n"
        f"{heavy_summary}\n"
        f"{qwen_summary}"
    )
    write_text(out_dir / "summary.md", summary_text)

    print(f"Saved report packet to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
