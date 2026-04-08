# Pilot Eval 日志 2026-04-08

## 执行概览

今天完成了两轮新的前沿评测：

1. `gemma4:e4b` 的完整核心 pilot
2. `gemma4:26b` 的最小校准集

另外，原先设计的 `datasets/frontier/frontier_pilot_26b_safe.jsonl` 在实际执行中仍然过重，已被判定为不适合当前机器作为默认执行方案，因此保留配置但不作为主结果来源。

## 任务集

- `datasets/frontier/frontier_pilot_e4b.jsonl`
  - 19 条任务
  - 覆盖 `MMLU-Pro`、`MMLU-CF`、`MMLU-ProX-Lite(en/zh/sw)`、`LiveBench Reasoning`、`SimpleQA`
- `datasets/frontier/frontier_calibration_26b.jsonl`
  - 7 条任务
  - 覆盖 `MMLU-Pro`、`MMLU-CF`、`MMLU-ProX-Lite(en/zh)`

## `gemma4:e4b` 核心结果

来自 `outputs/frontier_pilot_e4b_20260408/summary.csv`：

- `MMLU-CF`：`4/4`，平均时延约 `22.86s`
- `MMLU-Pro`：`2/4`，平均时延约 `37.18s`
- `MMLU-ProX-Lite en`：`2/2`，平均时延约 `65.65s`
- `MMLU-ProX-Lite zh`：`2/2`，平均时延约 `62.03s`
- `MMLU-ProX-Lite sw`：`2/2`，平均时延约 `91.98s`
- `LiveBench Reasoning`：`1/1`，时延约 `122.46s`
- `SimpleQA`：`1/4`，平均时延约 `14.27s`

## `gemma4:26b` 校准结果

来自 `outputs/frontier_calibration_26b_20260408/summary.csv`：

- `MMLU-CF`：`4/4`，平均时延约 `20.00s`
- `MMLU-Pro`：`1/1`，时延约 `56.86s`
- `MMLU-ProX-Lite en`：`1/1`，时延约 `89.92s`
- `MMLU-ProX-Lite zh`：`1/1`，时延约 `109.43s`

## 关键发现

1. `e4b` 是当前机器上更合适的主力 benchmark 模型。
2. `26b` 并非单纯“更慢但更强”，而是对 benchmark 类型非常敏感。
3. `MMLU-CF` 是当前本地环境下最稳定、最适合拉开样本量的前沿 benchmark。
4. `SimpleQA` 揭示了 `e4b` 的事实性短板，和其推理类 benchmark 表现形成明显反差。
5. `sw` 在多语言高级推理上的时延成本最高，说明低资源语言可能触发更高推理负担。

## 工程修正

- `benchmark_runner.py` 已支持增量写出 `raw_outputs.jsonl`
- 长跑中断时不再丢失全部结果
- 新增 `scripts/analyze_frontier_results.py` 用于聚合多个 run 的结果

## 输出位置

- `outputs/frontier_pilot_e4b_20260408/`
- `outputs/frontier_calibration_26b_20260408/`
- `outputs/frontier_analysis_20260408/`
