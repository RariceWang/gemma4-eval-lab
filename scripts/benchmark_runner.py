#!/usr/bin/env python3
"""Run local evaluations against Ollama and persist raw logs."""

from __future__ import annotations

import argparse
import csv
import json
import re
import string
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


@dataclass
class Task:
    task_id: str
    benchmark: str
    group: str
    language: str
    metric: str
    response_parser: str
    prompt: str
    reference: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Gemma 4 evaluation tasks via Ollama.")
    parser.add_argument("--dataset", required=True, help="Path to jsonl dataset.")
    parser.add_argument("--models", nargs="+", required=True, help="Model IDs to run.")
    parser.add_argument("--out", required=True, help="Output directory.")
    parser.add_argument("--timeout", type=int, default=300, help="Per request timeout in seconds.")
    parser.add_argument("--limit", type=int, default=0, help="Optional limit on task count.")
    parser.add_argument("--temperature", type=float, default=0.2, help="Sampling temperature.")
    parser.add_argument("--top-p", type=float, default=0.9, dest="top_p", help="Top-p value.")
    parser.add_argument("--num-ctx", type=int, default=8192, dest="num_ctx", help="Context window limit.")
    return parser.parse_args()


def load_tasks(path: Path, limit: int) -> list[Task]:
    tasks: list[Task] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            tasks.append(
                Task(
                    task_id=data["id"],
                    benchmark=data.get("benchmark", data.get("group", "custom")),
                    group=data["group"],
                    language=data["language"],
                    metric=data["metric"],
                    response_parser=data.get("response_parser", "raw_text"),
                    prompt=data["prompt"],
                    reference=data.get("reference", ""),
                )
            )
    if limit > 0:
        return tasks[:limit]
    return tasks


def call_ollama(
    model: str,
    prompt: str,
    timeout: int,
    temperature: float,
    top_p: float,
    num_ctx: int,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": top_p,
            "num_ctx": num_ctx,
        },
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_text(text: str) -> str:
    return " ".join(text.strip().lower().split())


def normalize_simpleqa(text: str) -> str:
    lowered = normalize_text(text)
    table = str.maketrans("", "", string.punctuation)
    return lowered.translate(table)


def parse_response(text: str, response_parser: str) -> str:
    text = text.strip()
    if response_parser == "choice_letter":
        match = re.search(r"\b([A-J])\b", text.upper())
        return match.group(1) if match else text
    if response_parser == "solution_tag":
        match = re.search(r"<solution>\s*(.*?)\s*</solution>", text, flags=re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else text
    if response_parser == "short_answer":
        first_line = text.splitlines()[0].strip()
        return re.sub(r"^(answer|final answer)\s*:\s*", "", first_line, flags=re.IGNORECASE)
    return text


def score_result(metric: str, parsed_response: str, reference: str) -> float | None:
    if not reference:
        return None
    if metric == "exact_match":
        return float(normalize_text(parsed_response) == normalize_text(reference))
    if metric == "simpleqa_match":
        pred = normalize_simpleqa(parsed_response)
        gold = normalize_simpleqa(reference)
        return float(pred == gold or gold in pred)
    return None


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_summary(path: Path, rows: list[dict[str, Any]]) -> None:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["model"], row["benchmark"], row["group"])].append(row)

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "model",
                "benchmark",
                "group",
                "task_count",
                "scored_count",
                "mean_score",
                "mean_latency_sec",
                "mean_prompt_chars",
                "mean_response_chars",
                "error_count",
            ]
        )
        for (model, benchmark, group), items in sorted(grouped.items()):
            scored = [item["score"] for item in items if item["score"] is not None]
            latencies = [item["latency_sec"] for item in items if item["latency_sec"] is not None]
            prompt_chars = [item["prompt_chars"] for item in items]
            response_chars = [item["response_chars"] for item in items]
            errors = sum(1 for item in items if item["status"] != "ok")
            mean_score = round(sum(scored) / len(scored), 4) if scored else ""
            mean_latency = round(sum(latencies) / len(latencies), 4) if latencies else ""
            mean_prompt_chars = round(sum(prompt_chars) / len(prompt_chars), 2) if prompt_chars else ""
            mean_response_chars = round(sum(response_chars) / len(response_chars), 2) if response_chars else ""
            writer.writerow(
                [
                    model,
                    benchmark,
                    group,
                    len(items),
                    len(scored),
                    mean_score,
                    mean_latency,
                    mean_prompt_chars,
                    mean_response_chars,
                    errors,
                ]
            )


def main() -> int:
    args = parse_args()
    dataset_path = Path(args.dataset)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    tasks = load_tasks(dataset_path, args.limit)
    run_meta = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "dataset": str(dataset_path),
        "models": args.models,
        "task_count": len(tasks),
        "options": {
            "temperature": args.temperature,
            "top_p": args.top_p,
            "num_ctx": args.num_ctx,
            "timeout": args.timeout,
        },
    }

    metadata_path = out_dir / "metadata.json"
    raw_path = out_dir / "raw_outputs.jsonl"
    summary_path = out_dir / "summary.csv"

    metadata_path.write_text(json.dumps(run_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    raw_path.write_text("", encoding="utf-8")

    results: list[dict[str, Any]] = []
    for model in args.models:
        for task in tasks:
            started = time.perf_counter()
            status = "ok"
            error_message = ""
            response_text = ""
            parsed_response = ""
            try:
                response = call_ollama(
                    model=model,
                    prompt=task.prompt,
                    timeout=args.timeout,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    num_ctx=args.num_ctx,
                )
                response_text = response.get("response", "").strip()
                parsed_response = parse_response(response_text, task.response_parser)
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
                status = "error"
                error_message = str(exc)

            latency = round(time.perf_counter() - started, 4)
            score = score_result(task.metric, parsed_response, task.reference) if status == "ok" else None
            record = {
                "model": model,
                "task_id": task.task_id,
                "benchmark": task.benchmark,
                "group": task.group,
                "language": task.language,
                "metric": task.metric,
                "response_parser": task.response_parser,
                "reference": task.reference,
                "response": response_text,
                "parsed_response": parsed_response,
                "score": score,
                "status": status,
                "error": error_message,
                "latency_sec": latency,
                "prompt_chars": len(task.prompt),
                "response_chars": len(response_text),
            }
            results.append(record)
            append_jsonl(raw_path, record)
            print(
                f"[{status}] model={model} benchmark={task.benchmark} "
                f"task={task.task_id} latency={latency:.2f}s",
                file=sys.stderr,
            )

    write_summary(summary_path, results)

    print(f"Saved metadata to {metadata_path}")
    print(f"Saved raw results to {raw_path}")
    print(f"Saved summary to {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
