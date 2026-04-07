# Frontier Smoke Eval 日志 2026-04-07

## 运行命令

```bash
python3 scripts/build_frontier_suite.py \
  --suite frontier_smoke \
  --out datasets/frontier/frontier_smoke.jsonl

python3 scripts/benchmark_runner.py \
  --dataset datasets/frontier/frontier_smoke.jsonl \
  --models gemma4:e4b gemma4:26b \
  --out outputs/frontier_smoke_20260407
```

## 运行范围

本次 smoke eval 共覆盖 7 条任务：

1. `MMLU-Pro`
2. `MMLU-CF`
3. `MMLU-ProX-Lite` English
4. `MMLU-ProX-Lite` Chinese
5. `MMLU-ProX-Lite` Swahili
6. `LiveBench Reasoning`
7. `SimpleQA`

## 结果摘要

### `gemma4:e4b`

- `MMLU-Pro`：正确，约 `32.11s`
- `MMLU-CF`：正确，约 `18.10s`
- `MMLU-ProX-Lite en`：正确，约 `25.87s`
- `MMLU-ProX-Lite zh`：正确，约 `38.05s`
- `MMLU-ProX-Lite sw`：正确，约 `47.32s`
- `LiveBench Reasoning`：正确，约 `134.36s`
- `SimpleQA`：错误，输出 `Judea Pearl`，标准答案为 `Michio Sugeno`

### `gemma4:26b`

- `MMLU-Pro`：正确，约 `63.94s`
- `MMLU-CF`：正确，约 `23.91s`
- `MMLU-ProX-Lite en`：正确，约 `73.88s`
- `MMLU-ProX-Lite zh`：正确，约 `115.50s`
- `MMLU-ProX-Lite sw`：超时，`300s`
- `LiveBench Reasoning`：超时，`300s`
- `SimpleQA`：超时，`300s`

## 关键观察

1. `26b` 不一定比 `e4b` 更适合作为默认本地 benchmark 模型。
2. 在当前 24G 内存与本地推理设置下，`26b` 的时延明显放大，且在更复杂任务上直接碰到可用性边界。
3. `e4b` 在这轮前沿 smoke 中对 6 个 benchmark 任务给出了有效响应，只在 `SimpleQA` 上答错。
4. 多语言高级推理会显著增加推理耗时，尤其是 `sw`。
5. `LiveBench` 这类更接近真实推理交互的 benchmark，对本地中等模型非常不友好。

## 方法修正

在执行 smoke eval 后，修正了 runner 中一个统计问题：

- 超时与执行错误不再记为 `0.0` 分
- 现在统一记为 `score = null`
- `summary.csv` 中 `scored_count` 只统计实际返回结果的样本

## 当前结论

如果目标是：

- **跑通更多前沿 benchmark**：优先 `gemma4:e4b`
- **观察更大模型上限**：可局部尝试 `gemma4:26b`
- **默认长期批量评测**：暂不建议把 `gemma4:26b` 设为唯一主力模型
