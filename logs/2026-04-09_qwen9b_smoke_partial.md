# Qwen 9B Smoke 阶段记录 2026-04-09

## 执行目的

在确认 `Qwen 27B` 不适合作为当前机器上的正式主实验模型后，补跑小参数量 `qwen3.5:9b`，观察它是否能够作为 `gemma4:e4b` 的跨家族对照模型。

## 执行配置

- 模型：`qwen3.5:9b`
- 数据集：`datasets/frontier/frontier_smoke.jsonl`
- 配置：
  - `think=true`
  - `num_ctx=262144`
  - `timeout=900`

输出目录：

- `outputs/frontier_smoke_qwen35_9b_thinktrue_ctx256k_20260409/`

配套汇总：

- `outputs/frontier_analysis_qwen35_9b_smoke_partial_20260409/`

## 当前结果

已正式完成的样本：

- `mmlu_pro-70`
  - `score = 1.0`
  - `latency_sec ≈ 132.41`
  - `thinking_chars ≈ 5427`
- `mmlu_cf-0`
  - `score = 1.0`
  - `latency_sec ≈ 50.62`
  - `thinking_chars ≈ 1962`
- `mmlu_prox_lite_en-70`
  - `score = 1.0`
  - `latency_sec ≈ 119.01`
  - `thinking_chars ≈ 3997`
- `mmlu_prox_lite_zh-70`
  - `score = 1.0`
  - `latency_sec ≈ 368.62`
  - `thinking_chars ≈ 10052`

被人工中断的样本：

- `mmlu_prox_lite_sw-70`
  - `status = interrupted`
  - `latency_sec ≈ 927.82`
  - `thinking_chars ≈ 20173`
  - `first_response_sec = None`

## 对 `sw` thinking 的判断

从 `raw_outputs.jsonl` 和 `stream_events.jsonl` 可见，`mmlu_prox_lite_sw-70` 在较长时间内反复重走同一套排除逻辑，已经表现出明显的“语义死循环”特征。

主要证据：

1. 在 `927s` 内始终没有最终 response。
2. thinking 中高频重复：
   - `Vitendo visivyo salama, Msongo wa mawazo, Hofu, Nzito`
   - `Msongo wa mawazo, Hofu`
3. 尾部仍在重复类似：
   - `Vitendo salama ... Incorrect`
   - 对已排除选项的再次复核

因此，这条题不应视为普通“慢推理”，而应视为已经进入不收敛循环。

## 当前结论

1. `qwen3.5:9b` 明显比 `qwen3.5:27b` 更可运行。
2. 在英文与中文 smoke 子集上，`Qwen 9B` 当前表现是可用的。
3. 但在 `sw` 题上，它同样暴露出与 `Gemma 26B` 相似的长 thinking 风险。
4. 因此，`Qwen 9B` 可以进入课程报告作为“小参数量跨家族对照”，但需要明确说明其在低资源语言上的稳定性问题。
