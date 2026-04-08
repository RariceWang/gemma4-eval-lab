#!/usr/bin/env python3
"""Probe streamed Ollama generation to measure first-token latency and chunk cadence."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stream-probe a single benchmark task via Ollama.")
    parser.add_argument("--dataset", required=True, help="Path to task jsonl file.")
    parser.add_argument("--model", required=True, help="Ollama model name.")
    parser.add_argument("--task-id", required=True, help="Task id from the dataset.")
    parser.add_argument("--timeout", type=int, default=600, help="Socket timeout in seconds.")
    parser.add_argument("--num-ctx", type=int, default=8192, dest="num_ctx", help="Context window.")
    parser.add_argument("--temperature", type=float, default=0.2, help="Sampling temperature.")
    parser.add_argument("--top-p", type=float, default=0.9, dest="top_p", help="Top-p value.")
    parser.add_argument("--think", choices=["true", "false"], default="true", help="Whether to enable thinking.")
    parser.add_argument("--out", help="Optional JSON output path.")
    return parser.parse_args()


def load_task(dataset_path: Path, task_id: str) -> dict[str, Any]:
    with dataset_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row["id"] == task_id:
                return row
    raise SystemExit(f"Task id not found: {task_id}")


def main() -> int:
    args = parse_args()
    task = load_task(Path(args.dataset), args.task_id)

    payload = {
        "model": args.model,
        "prompt": task["prompt"],
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

    started = time.perf_counter()
    first_token_at: float | None = None
    first_thinking_sec: float | None = None
    chunks: list[dict[str, Any]] = []
    full_text: list[str] = []
    full_thinking: list[str] = []
    error_message = ""

    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            while True:
                line = response.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                event = json.loads(line.decode("utf-8"))
                now = time.perf_counter()
                piece = event.get("response", "")
                thought = event.get("thinking", "")
                if thought and first_thinking_sec is None:
                    first_thinking_sec = now - started
                if piece and first_token_at is None:
                    first_token_at = now - started
                if piece:
                    full_text.append(piece)
                if thought:
                    full_thinking.append(thought)
                chunks.append(
                    {
                        "t_sec": round(now - started, 4),
                        "chars": len(piece),
                        "thinking_chars": len(thought),
                        "done": bool(event.get("done", False)),
                        "preview": piece[:80],
                        "thinking_preview": thought[:80],
                    }
                )
                if event.get("done", False):
                    break
    except (TimeoutError, urllib.error.URLError, OSError) as exc:
        error_message = str(exc)

    total_time = time.perf_counter() - started
    result = {
        "model": args.model,
        "task_id": task["id"],
        "benchmark": task.get("benchmark", ""),
        "think_enabled": args.think == "true",
        "num_ctx": args.num_ctx,
        "timeout": args.timeout,
        "first_thinking_sec": round(first_thinking_sec, 4) if first_thinking_sec is not None else None,
        "first_token_sec": round(first_token_at, 4) if first_token_at is not None else None,
        "total_time_sec": round(total_time, 4),
        "chunk_count": len(chunks),
        "response_chars": sum(chunk["chars"] for chunk in chunks),
        "thinking_chars": sum(chunk["thinking_chars"] for chunk in chunks),
        "error": error_message,
        "chunks": chunks,
        "final_thinking_preview": "".join(full_thinking)[:1000],
        "final_text_preview": "".join(full_text)[:1000],
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Saved probe log to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
