# 26B Safe Pilot 完整记录 2026-04-09

## 本轮执行

完成了 `gemma4:26b` 在 `frontier_pilot_26b_safe` 上的正式口径补跑：

- 数据集：`datasets/frontier/frontier_pilot_26b_safe.jsonl`
- 模型：`gemma4:26b`
- 配置：
  - `think=true`
  - `num_ctx=262144`
  - `timeout=1800`
  - 补跑阶段加入 `max_think_seconds=900`

输出目录：

- `outputs/frontier_pilot_26b_safe_thinktrue_ctx256k_20260409/`

配套汇总：

- `outputs/frontier_analysis_pilot26b_safe_20260409/`
- `outputs/frontier_analysis_pilot26b_compare_20260409/`
- `outputs/frontier_analysis_official_extended_20260409/`

## Safe Pilot 结果

### 1. `MMLU-Pro`

- `task_count = 4`
- `success_count = 4`
- `mean_score = 0.7500`
- `mean_latency_sec = 190.1249`
- `mean_thinking_chars = 6352`

逐题观察：

- `mmlu_pro-70`：`127.6570s`
- `mmlu_pro-71`：`273.2825s`
- `mmlu_pro-72`：`280.9873s`
- `mmlu_pro-73`：`78.5727s`，答错

结论：

- `26b + think=true` 在 `MMLU-Pro` 上比 `e4b` 更强
- 但单位题目时延明显更高

### 2. `MMLU-CF`

- `task_count = 4`
- `success_count = 4`
- `mean_score = 1.0000`
- `mean_latency_sec = 37.9764`
- `mean_thinking_chars = 1307`

结论：

- `26b` 在污染受控 benchmark 上延续了稳定优势
- 这一组是当前 `26b think=true` 下最稳的正式结果

### 3. `MMLU-ProX-Lite en`

- `task_count = 2`
- `success_count = 1`
- `long_think_count = 1`
- `success_rate = 0.5000`
- `mean_latency_sec = 486.5749`

关键样本：

- `mmlu_prox_lite_en-70`：`72.4896s`，正确
- `mmlu_prox_lite_en-71`：`900.6601s`，`long_think`

### 4. `MMLU-ProX-Lite zh`

- `task_count = 2`
- `success_count = 1`
- `long_think_count = 1`
- `success_rate = 0.5000`
- `mean_latency_sec = 543.6957`

关键样本：

- `mmlu_prox_lite_zh-70`：`187.2124s`，正确
- `mmlu_prox_lite_zh-71`：`900.1790s`，`long_think`

## 与 `think=false` 的直接对照

来自 `outputs/frontier_analysis_pilot26b_compare_20260409/`：

- `MMLU-Pro`
  - `think_false`：`mean_score = 0.7500`，`mean_latency_sec = 3.9649`
  - `think_true`：`mean_score = 0.7500`，`mean_latency_sec = 190.1249`
  - 结论：质量无提升，时延扩大约 `48x`
- `MMLU-CF`
  - `think_false`：`mean_score = 0.7500`
  - `think_true`：`mean_score = 1.0000`
  - 结论：这里出现了明确质量收益，但代价是从 `0.7951s` 升到 `37.9764s`
- `MMLU-ProX-Lite en`
  - `think_false`：`2/2` 完成，`mean_score = 0.5000`
  - `think_true`：`1/2` 完成，`1/2` 为 `long_think`
  - 结论：`think=true` 在多语言题上带来完成性风险
- `MMLU-ProX-Lite zh`
  - `think_false`：`2/2` 完成，`mean_score = 0.5000`
  - `think_true`：`1/2` 完成，`1/2` 为 `long_think`
  - 结论：同样表现出完成率下降

## 扩展后的正式结论

来自 `outputs/frontier_analysis_official_extended_20260409/by_model_benchmark.csv`：

### `gemma4:26b`

- `MMLU-CF`：`8` 条全完成，`mean_score = 1.0000`
- `MMLU-Pro`：`5` 条全完成，`mean_score = 0.8000`
- `MMLU-ProX-Lite en`：`3` 条中 `2` 条完成，`1` 条 `long_think`
- `MMLU-ProX-Lite zh`：`3` 条中 `2` 条完成，`1` 条 `long_think`

### 对比 `gemma4:e4b`

- `26b` 仍在知识推理和污染受控 benchmark 上更强
- `e4b` 在多语言高级推理上的完成性更稳
- `26b` 的主要问题不是早期起思慢，而是起思后长期停留在 thinking 阶段

## 当前最稳妥的表述

1. `26b + think=true + 256k` 在 `MMLU-CF` 和部分 `MMLU-Pro` 题上提供了可见质量收益。
2. 这种收益并不普遍，尤其在 `MMLU-ProX-Lite` 的英文和中文题上会出现明显的长时间不收敛。
3. 对当前本地环境而言，`26b + think=true` 更适合作为“高质量但高风险”的正式配置，而不是全题默认稳态配置。
4. 在报告里应同时呈现：
   - 正确率/得分
   - 完成率
   - `long_think` 比例
   - thinking 长度与最终响应时延

## 下一步建议

1. 将 `outputs/frontier_analysis_official_extended_20260409/` 作为后续正式主表来源。
2. 将 `outputs/frontier_analysis_heavy_compare_20260409/` 作为 `26b` 重任务风险证据。
3. 后续若继续推进前沿评测，优先补：
   - 面向报告的图表整理
   - 对 `long_think` 任务的 task-level case study
4. 不建议再扩大 `26b think=true` 的多语言批量任务规模，除非继续采用显式上限控制。
