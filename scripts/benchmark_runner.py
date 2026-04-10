#!/usr/bin/env python3
"""Run local evaluations against Ollama and persist full streamed logs."""

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
    parser.add_argument("--timeout", type=int, default=900, help="Socket timeout in seconds.")
    parser.add_argument("--limit", type=int, default=0, help="Optional limit on task count.")
    parser.add_argument("--temperature", type=float, default=0.2, help="Sampling temperature.")
    parser.add_argument("--top-p", type=float, default=0.9, dest="top_p", help="Top-p value.")
    parser.add_argument("--num-ctx", type=int, default=262144, dest="num_ctx", help="Context window limit.")
    parser.add_argument("--think", choices=["true", "false"], default="true", help="Whether to enable thinking.")
    parser.add_argument("--resume", action="store_true", help="Resume from existing output directory if present.")
    parser.add_argument(
        "--max-think-seconds",
        type=float,
        default=0,
        help="If >0, record task as long_think when thinking continues beyond this threshold before any final response.",
    )
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


def call_ollama_stream(
    model: str,
    prompt: str,
    timeout: int,
    temperature: float,
    top_p: float,
    num_ctx: int,
    think: bool,
    max_think_seconds: float,
    chunk_logger,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "think": think,
        "options": {
            "temperature": temperature,
            "top_p": top_p,
            "num_ctx": num_ctx,
        },
    }
    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    started = time.perf_counter()
    first_thinking_sec: float | None = None
    first_response_sec: float | None = None
    thinking_parts: list[str] = []
    response_parts: list[str] = []
    chunk_count = 0
    done_reason = ""

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            while True:
                line = response.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                event = json.loads(line.decode("utf-8"))
                now = time.perf_counter()
                thought = event.get("thinking", "")
                piece = event.get("response", "")
                if thought:
                    if first_thinking_sec is None:
                        first_thinking_sec = now - started
                    thinking_parts.append(thought)
                if piece:
                    if first_response_sec is None:
                        first_response_sec = now - started
                    response_parts.append(piece)
                if chunk_logger is not None:
                    chunk_logger(
                        {
                            "t_sec": round(now - started, 4),
                            "thinking": thought,
                            "response": piece,
                            "done": bool(event.get("done", False)),
                        }
                    )
                chunk_count += 1
                if (
                    max_think_seconds > 0
                    and first_response_sec is None
                    and first_thinking_sec is not None
                    and (now - started) >= max_think_seconds
                ):
                    done_reason = "long_think"
                    break
                if event.get("done", False):
                    done_reason = event.get("done_reason", "")
                    break
    except KeyboardInterrupt:
        done_reason = "interrupted"

    total_time = time.perf_counter() - started
    return {
        "thinking": "".join(thinking_parts),
        "response": "".join(response_parts).strip(),
        "first_thinking_sec": round(first_thinking_sec, 4) if first_thinking_sec is not None else None,
        "first_response_sec": round(first_response_sec, 4) if first_response_sec is not None else None,
        "chunk_count": chunk_count,
        "done_reason": done_reason,
        "total_time_sec": round(total_time, 4),
    }


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
        if not text:
            return ""
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


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_existing_results(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


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
                "mean_first_thinking_sec",
                "mean_first_response_sec",
                "mean_prompt_chars",
                "mean_thinking_chars",
                "mean_response_chars",
                "error_count",
            ]
        )
        for (model, benchmark, group), items in sorted(grouped.items()):
            scored = [item["score"] for item in items if item["score"] is not None]
            latencies = [item["latency_sec"] for item in items if item["latency_sec"] is not None]
            first_thinking = [item["first_thinking_sec"] for item in items if item["first_thinking_sec"] is not None]
            first_response = [item["first_response_sec"] for item in items if item["first_response_sec"] is not None]
            prompt_chars = [item["prompt_chars"] for item in items]
            thinking_chars = [item["thinking_chars"] for item in items]
            response_chars = [item["response_chars"] for item in items]
            errors = sum(1 for item in items if item["status"] != "ok")
            writer.writerow(
                [
                    model,
                    benchmark,
                    group,
                    len(items),
                    len(scored),
                    round(sum(scored) / len(scored), 4) if scored else "",
                    round(sum(latencies) / len(latencies), 4) if latencies else "",
                    round(sum(first_thinking) / len(first_thinking), 4) if first_thinking else "",
                    round(sum(first_response) / len(first_response), 4) if first_response else "",
                    round(sum(prompt_chars) / len(prompt_chars), 2) if prompt_chars else "",
                    round(sum(thinking_chars) / len(thinking_chars), 2) if thinking_chars else "",
                    round(sum(response_chars) / len(response_chars), 2) if response_chars else "",
                    errors,
                ]
            )


def make_completed_key(model: str, task_id: str) -> str:
    return f"{model}::{task_id}"


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
            "think": args.think == "true",
            "temperature": args.temperature,
            "top_p": args.top_p,
            "num_ctx": args.num_ctx,
            "timeout": args.timeout,
        },
    }

    metadata_path = out_dir / "metadata.json"
    raw_path = out_dir / "raw_outputs.jsonl"
    summary_path = out_dir / "summary.csv"
    stream_path = out_dir / "stream_events.jsonl"

    existing_results = load_existing_results(raw_path) if args.resume else []
    results: list[dict[str, Any]] = list(existing_results)
    completed = {make_completed_key(row["model"], row["task_id"]) for row in existing_results}

    if args.resume:
        run_meta["resumed_at"] = datetime.now().isoformat(timespec="seconds")
        run_meta["existing_result_count"] = len(existing_results)
        if not stream_path.exists():
            stream_path.write_text("", encoding="utf-8")
    else:
        metadata_path.write_text(json.dumps(run_meta, ensure_ascii=False, indent=2), encoding="utf-8")
        raw_path.write_text("", encoding="utf-8")
        stream_path.write_text("", encoding="utf-8")

    metadata_path.write_text(json.dumps(run_meta, ensure_ascii=False, indent=2), encoding="utf-8")

    stop_requested = False

    for model in args.models:
        for task in tasks:
            if make_completed_key(model, task.task_id) in completed:
                print(
                    f"[skip] model={model} benchmark={task.benchmark} task={task.task_id}",
                    file=sys.stderr,
                )
                continue
            started = time.perf_counter()
            status = "ok"
            error_message = ""
            stream_result = {
                "thinking": "",
                "response": "",
                "first_thinking_sec": None,
                "first_response_sec": None,
                "chunk_count": 0,
                "done_reason": "",
                "total_time_sec": None,
            }
            parsed_response = ""
            append_jsonl(
                stream_path,
                {
                    "event": "task_started",
                    "model": model,
                    "task_id": task.task_id,
                    "benchmark": task.benchmark,
                    "t_wall": datetime.now().isoformat(timespec="seconds"),
                },
            )
            try:
                def log_chunk(payload: dict[str, Any]) -> None:
                    append_jsonl(
                        stream_path,
                        {
                            "event": "chunk",
                            "model": model,
                            "task_id": task.task_id,
                            "benchmark": task.benchmark,
                            **payload,
                        },
                    )

                payload = {
                    "model": model,
                    "prompt": task.prompt,
                    "stream": True,
                    "think": args.think == "true",
                    "options": {
                        "temperature": args.temperature,
                        "top_p": args.top_p,
                        "num_ctx": args.num_ctx,
                    },
                }
                request = urllib.request.Request(
                    OLLAMA_URL,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )

                stream_result = call_ollama_stream(
                    model=model,
                    prompt=task.prompt,
                    timeout=args.timeout,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    num_ctx=args.num_ctx,
                    think=args.think == "true",
                    max_think_seconds=args.max_think_seconds,
                    chunk_logger=log_chunk,
                )
                if stream_result["done_reason"] == "long_think":
                    status = "long_think"
                    error_message = "long_think"
                elif stream_result["done_reason"] == "interrupted":
                    status = "interrupted"
                    error_message = "interrupted"
                    stop_requested = True
                parsed_response = parse_response(stream_result["response"], task.response_parser)
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
                "think_enabled": args.think == "true",
                "metric": task.metric,
                "response_parser": task.response_parser,
                "prompt": task.prompt,
                "reference": task.reference,
                "thinking": stream_result["thinking"],
                "response": stream_result["response"],
                "parsed_response": parsed_response,
                "score": score,
                "status": status,
                "error": error_message,
                "latency_sec": latency,
                "first_thinking_sec": stream_result["first_thinking_sec"],
                "first_response_sec": stream_result["first_response_sec"],
                "chunk_count": stream_result["chunk_count"],
                "done_reason": stream_result["done_reason"],
                "prompt_chars": len(task.prompt),
                "thinking_chars": len(stream_result["thinking"]),
                "response_chars": len(stream_result["response"]),
            }
            results.append(record)
            append_jsonl(raw_path, record)
            append_jsonl(
                stream_path,
                {
                    "event": "task_finished",
                    "model": model,
                    "task_id": task.task_id,
                    "benchmark": task.benchmark,
                    "status": status,
                    "score": score,
                    "latency_sec": latency,
                    "t_wall": datetime.now().isoformat(timespec="seconds"),
                },
            )
            print(
                f"[{status}] model={model} benchmark={task.benchmark} "
                f"task={task.task_id} latency={latency:.2f}s",
                file=sys.stderr,
            )
            if stop_requested:
                break
        if stop_requested:
            break

    write_summary(summary_path, results)

    print(f"Saved metadata to {metadata_path}")
    print(f"Saved raw results to {raw_path}")
    print(f"Saved summary to {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
