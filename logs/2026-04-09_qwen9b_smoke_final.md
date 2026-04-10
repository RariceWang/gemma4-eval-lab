# Qwen 9B Smoke 完整记录 2026-04-09

## 执行配置

- 模型：`qwen3.5:9b`
- 数据集：`datasets/frontier/frontier_smoke.jsonl`
- 设置：
  - `think=true`
  - `num_ctx=262144`
  - 后续补跑阶段加入 `max_think_seconds=600`

输出目录：

- `outputs/frontier_smoke_qwen35_9b_thinktrue_ctx256k_20260409/`

配套汇总：

- `outputs/frontier_analysis_qwen35_9b_smoke_20260409/`
- `outputs/frontier_analysis_smoke_qwen_compare_20260409/`

## 最终结果

### 已完成并正确的任务

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
- `livebench_reasoning-bd14ba82d1fe813d`
  - `score = 1.0`
  - `latency_sec ≈ 334.02`
  - `thinking_chars ≈ 6726`

### 未完成任务

- `mmlu_prox_lite_sw-70`
  - `status = interrupted`
  - `latency_sec ≈ 927.82`
  - `thinking_chars ≈ 20173`
  - 判断：已出现语义死循环
- `simpleqa-0`
  - `status = long_think`
  - `latency_sec ≈ 600.06`
  - `thinking_chars ≈ 11690`
  - 判断：长时间候选答案反复比较，未及时收敛

## 当前结论

1. `Qwen 9B` 明显比 `Qwen 27B` 更适合当前机器。
2. 在 `MMLU-Pro`、`MMLU-CF`、`MMLU-ProX-Lite en/zh` 与 `LiveBench` 的 smoke 样本上，`Qwen 9B` 当前都能给出正确结果。
3. 但它在 `sw` 和 `SimpleQA` 上同样暴露出明显的 thinking 风险。
4. 因而 `Qwen 9B` 可以进入课程报告作为“小参数量跨家族对照”，但不能被表述为“稳定优于 Gemma E4B”的模型。

## 对课程报告的意义

当前最稳妥的写法是：

- `Qwen 27B`：由于本地运行代价过高，被排除出主实验
- `Qwen 9B`：作为可运行的小参数量扩展模型，展示出“英文/中文可用，但低资源语言和 factuality 仍有长思考问题”的特征

这使得课程报告可以从“Gemma 内部比较”升级为：

1. `Gemma 4` 主结果
2. `Qwen 9B` 扩展对照
3. `Qwen 27B` 作为资源受限下的失败尝试
