# 26B Safe Pilot 阶段记录 2026-04-09

## 本轮目的

按当前正式前沿评测口径，补跑：

- 数据集：`datasets/frontier/frontier_pilot_26b_safe.jsonl`
- 模型：`gemma4:26b`
- 配置：
  - `think=true`
  - `num_ctx=262144`
  - `timeout=1800`
  - 流式记录 `prompt + thinking + response`

输出目录：

- `outputs/frontier_pilot_26b_safe_thinktrue_ctx256k_20260409/`

## 当前阶段结果

本轮在人工中断前，已正式完成 `9/12` 条任务。

已完成任务分布：

- `MMLU-Pro`：`4/4`
- `MMLU-CF`：`4/4`
- `MMLU-ProX-Lite en`：`1/2`

尚未完成：

- `MMLU-ProX-Lite en`：`1` 条
- `MMLU-ProX-Lite zh`：`2` 条

## 已完成部分的可用结果

来自 `outputs/frontier_analysis_pilot26b_safe_partial_20260409/by_model_benchmark.csv`：

- `MMLU-Pro`
  - `task_count = 4`
  - `mean_score = 0.7500`
  - `mean_latency_sec = 190.1249`
  - `mean_thinking_chars = 6352`
- `MMLU-CF`
  - `task_count = 4`
  - `mean_score = 1.0000`
  - `mean_latency_sec = 37.9764`
  - `mean_thinking_chars = 1307`
- `MMLU-ProX-Lite en`
  - `task_count = 1`
  - `mean_score = 1.0000`
  - `mean_latency_sec = 72.4896`
  - `mean_thinking_chars = 2312`

## 新出现的风险信号

当前 run 中，`mmlu_prox_lite_en-71` 出现了与 heavy 阶段相似的长时间 thinking 现象：

- `task_id`: `mmlu_prox_lite_en-71`
- 已记录 `chunk_count ≈ 4294`
- `first_t_sec ≈ 6.2663`
- `latest_t_sec ≈ 752.9742`
- `thinking_chars_so_far ≈ 11084`
- `response_chars_so_far = 0`

解读：

1. `26b + think=true + 256k` 的不稳定性并不只出现在最重的 `sw / LiveBench / SimpleQA` 上。
2. 即便在 `safe pilot` 中，个别多语言高级推理题也可能进入超长 thinking 而迟迟不给最终答案。
3. 因而 `pilot_26b_safe` 虽然整体比 heavy 阶段稳，但仍不能假设其所有题都能在合理时间内自然收敛。

## 工程改进

本轮中断暴露出 runner 的一个缺口：人工停止长跑时，当前任务不会被结构化记录。

已修复：

- `scripts/benchmark_runner.py` 现在会在 `KeyboardInterrupt` 下：
  - 保留当前任务已累计的 `thinking / response`
  - 将该任务标记为 `interrupted`
  - 继续写出本轮 summary

这能保证后续前沿长跑在被人工中断时仍然保持结果可分析。

## 当前建议

1. 将本轮已完成的 `9` 条样本视为“阶段性正式结果”。
2. 将 `mmlu_prox_lite_en-71` 记为新的长思考风险样本。
3. 后续若继续补齐剩余 `3` 条，优先使用：
   - 相同 `think=true` 主配置
   - 但配合显式人工监控或有限的中断策略
4. 当前不建议无监控地继续整批放跑 `26b` 的 `think=true` 多语言题。
