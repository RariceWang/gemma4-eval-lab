# Qwen 27B 试跑记录 2026-04-09

## 目的

评估 `qwen3.5:27b` 是否可以作为 `gemma4:26b` 的跨家族同级对照模型，纳入当前课程报告的正式前沿实验。

## 执行配置

- 模型：`qwen3.5:27b`
- 数据集：`datasets/frontier/frontier_calibration_26b.jsonl`
- 配置：
  - `think=true`
  - `num_ctx=262144`
  - `timeout=1800`

输出目录：

- `outputs/frontier_calibration_qwen35_27b_thinktrue_ctx256k_20260409/`

## 当前结果

### `mmlu_pro-70`

- 状态：`ok`
- 得分：`0.0`
- 时长：约 `3187.98s`
- `first_thinking_sec ≈ 62.9955`
- `thinking_chars ≈ 383`

解读：

- 该题虽然最终结束，但耗时已经远超当前课程实验的合理范围
- 而且最终答案错误，说明超长 thinking 并没有换来正确结果

### `mmlu_cf-0`

- 状态：`interrupted`
- 时长：约 `21.05s`

解读：

- 在首题已经暴露出极高代价后，本轮未继续完整跑完

## 结论

`qwen3.5:27b` 在当前机器上的 `think=true + 256k` 前沿正式配置下不适合作为课程报告主实验模型。

因此：

1. 不再继续补 `Qwen 27B`
2. 若后续仍希望加入 Qwen，对照重点应转向小参数量 `qwen3.5:9b`
