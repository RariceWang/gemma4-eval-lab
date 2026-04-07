#!/usr/bin/env python3
"""Build local JSONL tasks from frontier benchmark subsets via HF dataset viewer API."""

from __future__ import annotations

import argparse
import json
import ssl
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


API_ROWS = "https://datasets-server.huggingface.co/rows"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a local frontier benchmark task file.")
    parser.add_argument("--suite", required=True, help="Suite name from configs/frontier_suite.json")
    parser.add_argument("--config-path", default="configs/frontier_suite.json", help="Path to suite config JSON")
    parser.add_argument("--out", required=True, help="Output JSONL path")
    return parser.parse_args()


def fetch_rows(dataset: str, config: str, split: str, offset: int, length: int) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode(
        {
            "dataset": dataset,
            "config": config,
            "split": split,
            "offset": offset,
            "length": length,
        }
    )
    url = f"{API_ROWS}?{params}"
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(url, timeout=60, context=context) as response:
        data = json.load(response)
    return data["rows"]


def build_choice_prompt(question: str, options: list[str], answer_instruction: str) -> str:
    labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lines = [question.strip(), "", "Options:"]
    for index, option in enumerate(options):
        lines.append(f"{labels[index]}. {option}")
    lines.append("")
    lines.append(answer_instruction)
    return "\n".join(lines)


def adapt_mmlu_pro(spec: dict[str, Any], row: dict[str, Any], row_idx: int) -> dict[str, Any]:
    raw = row["row"]
    options = [option for option in raw["options"] if option]
    prompt = build_choice_prompt(raw["question"], options, "Reply with only the correct option letter.")
    return {
        "id": f"{spec['benchmark']}-{raw['question_id']}",
        "benchmark": spec["benchmark"],
        "group": spec["group"],
        "language": spec["language"],
        "metric": "exact_match",
        "response_parser": "choice_letter",
        "prompt": prompt,
        "reference": raw["answer"],
        "source": {
            "dataset": spec["dataset"],
            "config": spec["config"],
            "split": spec["split"],
            "row_idx": row_idx,
            "category": raw.get("category", ""),
            "src": raw.get("src", ""),
        },
    }


def adapt_mmlu_cf(spec: dict[str, Any], row: dict[str, Any], row_idx: int) -> dict[str, Any]:
    raw = row["row"]
    options = [raw["A"], raw["B"], raw["C"], raw["D"]]
    prompt = build_choice_prompt(raw["Question"], options, "Reply with only A, B, C, or D.")
    return {
        "id": f"{spec['benchmark']}-{row_idx}",
        "benchmark": spec["benchmark"],
        "group": spec["group"],
        "language": spec["language"],
        "metric": "exact_match",
        "response_parser": "choice_letter",
        "prompt": prompt,
        "reference": raw["Answer"],
        "source": {
            "dataset": spec["dataset"],
            "config": spec["config"],
            "split": spec["split"],
            "row_idx": row_idx,
        },
    }


def adapt_mmlu_prox_lite(spec: dict[str, Any], row: dict[str, Any], row_idx: int) -> dict[str, Any]:
    raw = row["row"]
    options = [raw.get(f"option_{index}") for index in range(10)]
    options = [option for option in options if option]
    prompt = build_choice_prompt(raw["question"], options, "Reply with only the correct option letter.")
    return {
        "id": f"{spec['benchmark']}-{raw['question_id']}",
        "benchmark": spec["benchmark"],
        "group": spec["group"],
        "language": spec["language"],
        "metric": "exact_match",
        "response_parser": "choice_letter",
        "prompt": prompt,
        "reference": raw["answer"],
        "source": {
            "dataset": spec["dataset"],
            "config": spec["config"],
            "split": spec["split"],
            "row_idx": row_idx,
            "category": raw.get("category", ""),
            "src": raw.get("src", ""),
        },
    }


def adapt_livebench_reasoning(spec: dict[str, Any], row: dict[str, Any], row_idx: int) -> dict[str, Any]:
    raw = row["row"]
    return {
        "id": f"{spec['benchmark']}-{raw['question_id'][:16]}",
        "benchmark": spec["benchmark"],
        "group": spec["group"],
        "language": spec["language"],
        "metric": "exact_match",
        "response_parser": "solution_tag",
        "prompt": raw["turns"][0].strip(),
        "reference": raw["ground_truth"],
        "source": {
            "dataset": spec["dataset"],
            "config": spec["config"],
            "split": spec["split"],
            "row_idx": row_idx,
            "task": raw.get("task", ""),
            "level": raw.get("level", ""),
        },
    }


def adapt_simpleqa(spec: dict[str, Any], row: dict[str, Any], row_idx: int) -> dict[str, Any]:
    raw = row["row"]
    metadata = raw.get("metadata", {})
    prompt = (
        "Answer the following factual question with a short phrase only.\n\n"
        f"Question: {raw['problem']}\n"
        "Answer:"
    )
    return {
        "id": f"{spec['benchmark']}-{row_idx}",
        "benchmark": spec["benchmark"],
        "group": spec["group"],
        "language": spec["language"],
        "metric": "simpleqa_match",
        "response_parser": "short_answer",
        "prompt": prompt,
        "reference": raw["answer"],
        "source": {
            "dataset": spec["dataset"],
            "config": spec["config"],
            "split": spec["split"],
            "row_idx": row_idx,
            "topic": metadata.get("topic", ""),
            "answer_type": metadata.get("answer_type", ""),
        },
    }


def adapt_longbench_v2(spec: dict[str, Any], row: dict[str, Any], row_idx: int) -> dict[str, Any]:
    raw = row["row"]
    prompt = (
        "Read the following long-context task and answer with only the correct option letter.\n\n"
        f"Context:\n{raw['context']}\n\n"
        f"Question:\n{raw['question']}\n\n"
        f"A. {raw['choice_A']}\n"
        f"B. {raw['choice_B']}\n"
        f"C. {raw['choice_C']}\n"
        f"D. {raw['choice_D']}\n\n"
        "Reply with only A, B, C, or D."
    )
    return {
        "id": f"{spec['benchmark']}-{raw['_id']}",
        "benchmark": spec["benchmark"],
        "group": spec["group"],
        "language": spec["language"],
        "metric": "exact_match",
        "response_parser": "choice_letter",
        "prompt": prompt,
        "reference": raw["answer"],
        "source": {
            "dataset": spec["dataset"],
            "config": spec["config"],
            "split": spec["split"],
            "row_idx": row_idx,
            "domain": raw.get("domain", ""),
            "sub_domain": raw.get("sub_domain", ""),
            "difficulty": raw.get("difficulty", ""),
            "length": raw.get("length", ""),
        },
    }


ADAPTERS = {
    "mmlu_pro": adapt_mmlu_pro,
    "mmlu_cf": adapt_mmlu_cf,
    "mmlu_prox_lite": adapt_mmlu_prox_lite,
    "livebench_reasoning": adapt_livebench_reasoning,
    "simpleqa": adapt_simpleqa,
    "longbench_v2": adapt_longbench_v2,
}


def main() -> int:
    args = parse_args()
    config_path = Path(args.config_path)
    suite_config = json.loads(config_path.read_text(encoding="utf-8"))
    specs = suite_config["suites"][args.suite]

    tasks: list[dict[str, Any]] = []
    for spec in specs:
        rows = fetch_rows(spec["dataset"], spec["config"], spec["split"], spec["offset"], spec["length"])
        adapter = ADAPTERS[spec["adapter"]]
        for row in rows:
            tasks.append(adapter(spec, row, row["row_idx"]))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        for task in tasks:
            handle.write(json.dumps(task, ensure_ascii=False) + "\n")

    print(f"Saved {len(tasks)} tasks to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
