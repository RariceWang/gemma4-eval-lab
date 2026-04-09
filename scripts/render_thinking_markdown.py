#!/usr/bin/env python3
"""Render raw thinking outputs and in-progress stream events into readable Markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render thinking traces as Markdown.")
    parser.add_argument("--out-dir", required=True, help="Benchmark run output directory")
    parser.add_argument("--output", help="Markdown output path; defaults to <out-dir>/thinking_readable.md")
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def fenced(text: str, lang: str = "text") -> str:
    return f"```{lang}\n{text.rstrip()}\n```"


def summarize_completed(rows: list[dict]) -> list[str]:
    lines = ["## 已完成任务", ""]
    if not rows:
        lines.extend(["暂无已完成任务。", ""])
        return lines

    for row in rows:
        lines.append(f"### {row['task_id']}")
        lines.append("")
        lines.append(f"- benchmark: `{row['benchmark']}`")
        lines.append(f"- score: `{row['score']}`")
        lines.append(f"- latency_sec: `{row['latency_sec']}`")
        lines.append(f"- first_thinking_sec: `{row['first_thinking_sec']}`")
        lines.append(f"- first_response_sec: `{row['first_response_sec']}`")
        lines.append(f"- thinking_chars: `{row['thinking_chars']}`")
        lines.append(f"- response_chars: `{row['response_chars']}`")
        lines.append("")
        lines.append("Prompt:")
        lines.append(fenced(row["prompt"]))
        lines.append("")
        lines.append("Thinking:")
        lines.append(fenced(row.get("thinking", "")))
        lines.append("")
        lines.append("Response:")
        lines.append(fenced(row.get("response", "")))
        lines.append("")
    return lines


def summarize_in_progress(events: list[dict], completed_task_ids: set[str]) -> list[str]:
    lines = ["## 进行中任务", ""]
    task_map: dict[str, list[dict]] = {}
    for event in events:
        task_id = event.get("task_id")
        if not task_id or task_id in completed_task_ids:
            continue
        task_map.setdefault(task_id, []).append(event)

    if not task_map:
        lines.extend(["暂无进行中任务。", ""])
        return lines

    for task_id, task_events in sorted(task_map.items()):
        chunks = [event for event in task_events if event.get("event") == "chunk"]
        thinking = "".join(event.get("thinking", "") for event in chunks)
        response = "".join(event.get("response", "") for event in chunks)
        last_t = chunks[-1].get("t_sec") if chunks else None
        benchmark = next((event.get("benchmark") for event in task_events if event.get("benchmark")), "")
        lines.append(f"### {task_id}")
        lines.append("")
        if benchmark:
            lines.append(f"- benchmark: `{benchmark}`")
        lines.append(f"- streamed_events: `{len(task_events)}`")
        lines.append(f"- chunk_events: `{len(chunks)}`")
        lines.append(f"- latest_t_sec: `{last_t}`")
        lines.append(f"- thinking_chars_so_far: `{len(thinking)}`")
        lines.append(f"- response_chars_so_far: `{len(response)}`")
        lines.append("")
        lines.append("Thinking So Far:")
        lines.append(fenced(thinking))
        lines.append("")
        if response:
            lines.append("Response So Far:")
            lines.append(fenced(response))
            lines.append("")
    return lines


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    raw_rows = read_jsonl(out_dir / "raw_outputs.jsonl")
    stream_rows = read_jsonl(out_dir / "stream_events.jsonl")

    output_path = Path(args.output) if args.output else out_dir / "thinking_readable.md"
    completed_ids = {row["task_id"] for row in raw_rows}

    lines = [
        "# Thinking Readable View",
        "",
        f"- output_dir: `{out_dir}`",
        f"- completed_tasks: `{len(raw_rows)}`",
        f"- stream_events: `{len(stream_rows)}`",
        "",
    ]
    lines.extend(summarize_completed(raw_rows))
    lines.extend(summarize_in_progress(stream_rows, completed_ids))

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved Markdown to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
