# Heavy Compare Findings 2026-04-09

## 已完成事项

1. 阅读并串联了以下既有文档与日志：
   - `README.md`
   - `docs/experiment_plan.md`
   - `docs/frontier_methodology.md`
   - `logs/2026-04-08_official_runs.md`
   - `logs/2026-04-08_interim_readable_findings.md`
   - `logs/2026-04-09_heavy_suite_status.md`
2. 将误写到 `USTC_CG_26` 的 `thinking_formatted.md` 移回本项目：
   - `outputs/frontier_heavy_26b_thinktrue_ctx256k_20260408/thinking_formatted.md`
3. 升级 `scripts/analyze_frontier_results.py`：
   - 汇总时显式区分 `think_true` / `think_false`
   - 新增 `long_think_count`、`error_count`
   - 新增 `mean_first_thinking_sec`、`mean_first_response_sec`
   - 新增 `mean_think_to_response_gap_sec`、`mean_thinking_tail_sec`
   - 新增 `task_level.csv` 便于逐题分析

## 新生成结果

### 1. 正式实验新汇总

- `outputs/frontier_analysis_official_20260409/by_model_benchmark.csv`
- `outputs/frontier_analysis_official_20260409/by_model_group.csv`
- `outputs/frontier_analysis_official_20260409/by_model_language.csv`
- `outputs/frontier_analysis_official_20260409/by_model_think.csv`
- `outputs/frontier_analysis_official_20260409/task_level.csv`

### 2. `26b` 重任务对照汇总

- `outputs/frontier_analysis_heavy_compare_20260409/by_model_benchmark.csv`
- `outputs/frontier_analysis_heavy_compare_20260409/by_model_group.csv`
- `outputs/frontier_analysis_heavy_compare_20260409/by_model_language.csv`
- `outputs/frontier_analysis_heavy_compare_20260409/by_model_think.csv`
- `outputs/frontier_analysis_heavy_compare_20260409/task_level.csv`

## 核心发现

### 1. 正式 `think=true` 基线

- `gemma4:26b` 在已完成的正式校准集上保持满分：
  - `MMLU-CF`：`1.0000`
  - `MMLU-Pro`：`1.0000`
  - `MMLU-ProX-Lite zh`：`1.0000`
- 但 `26b` 的 thinking 展开明显更长：
  - `MMLU-CF`：`mean_thinking_chars ≈ 1227`
  - `MMLU-Pro`：`mean_thinking_chars ≈ 2554`
  - `MMLU-ProX-Lite zh`：`mean_thinking_chars ≈ 5620`
- `gemma4:e4b` 的正式 pilot 仍体现“更稳但不一定更强”的格局：
  - `LiveBench Reasoning`：`1.0000`
  - `SimpleQA`：`0.2500`
  - `MMLU-Pro`：`0.5000`

### 2. `26b` 重任务上 `think=false` 明显更可控

来自 `outputs/frontier_analysis_heavy_compare_20260409/by_model_think.csv`：

- `think_false`
  - `task_count = 3`
  - `success_count = 3`
  - `mean_score = 0.6667`
  - `mean_latency_sec = 12.8570`
- `think_true`
  - `task_count = 3`
  - `success_count = 1`
  - `long_think_count = 2`
  - `mean_latency_sec = 1684.2125`
  - `mean_thinking_chars = 30314`

### 3. `think=true` 的收益高度不稳定

- `mmlu_prox_lite_sw-70`
  - `think_false`：`2.0646s`，正确
  - `think_true`：`1813.7390s`，正确
  - 结论：质量无增益，但时延扩大约 `878x`
- `livebench_reasoning-bd14ba82d1fe813d`
  - `think_false`：`34.6529s`，正确
  - `think_true`：`2371.4120s`，`long_think`
  - 结论：`think=true` 在该题上直接破坏了任务完成性
- `simpleqa-0`
  - `think_false`：`1.8536s`，错误
  - `think_true`：`867.4866s`，`long_think`
  - 结论：超长 thinking 也没有换来事实性收益

### 4. 当前最稳妥的报告表述

可以将重任务结论写为：

1. `26b + think=true` 能产生大量与题目相关的推理文本。
2. 这些推理文本在重任务上并不稳定转化为任务完成率提升。
3. 对本地部署而言，`think=true` 更适合作为“推理过程观察对象”，而不是默认执行配置。
4. 对重任务的主结果，应把“是否完成任务”和“thinking 是否展开”分开汇报。

## 下一步建议

1. 将 `frontier_analysis_official_20260409` 作为正式主表来源。
2. 将 `frontier_analysis_heavy_compare_20260409` 作为 heavy 阶段对照证据。
3. 后续如果还要补 `26b` 重任务，优先做：
   - 有上限的 `think=true` 探针
   - 少量 task 级 case study
4. 不建议继续无上限地跑完整 `frontier_heavy_26b` 的 `think=true` 批量实验。
