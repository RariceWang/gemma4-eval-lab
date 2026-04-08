# 官方实验日志 2026-04-08

## 统一设置

本轮之后，正式实验统一采用：

- `think=true`
- `num_ctx=262144`
- 较高超时上限
- 流式记录 `prompt + thinking + response`

## 已完成运行

### 1. `gemma4:26b` 官方校准集

输出目录：

- `outputs/frontier_calibration_26b_thinktrue_ctx256k_20260408/`

主要结果：

- `MMLU-CF`：`4/4`，平均时延约 `32.98s`
- `MMLU-Pro`：`1/1`，时延约 `84.17s`
- `MMLU-ProX-Lite en`：`1/1`，时延约 `70.47s`
- `MMLU-ProX-Lite zh`：`1/1`，时延约 `158.18s`

thinking 相关现象：

- `MMLU-CF` 平均 `first_thinking_sec` 约 `6.23s`
- `MMLU-CF` 平均 `first_response_sec` 约 `32.71s`
- `MMLU-ProX-Lite zh` thinking 文本约 `5620` 字符，显著高于同轮其他任务

### 2. `gemma4:e4b` 官方 pilot

输出目录：

- `outputs/frontier_pilot_e4b_thinktrue_ctx256k_20260408/`

主要结果：

- `MMLU-CF`：`4/4`，平均时延约 `26.16s`
- `MMLU-Pro`：`2/4`，平均时延约 `54.20s`
- `MMLU-ProX-Lite en`：`1/2`，平均时延约 `79.02s`
- `MMLU-ProX-Lite zh`：`2/2`，平均时延约 `73.91s`
- `MMLU-ProX-Lite sw`：`2/2`，平均时延约 `77.22s`
- `LiveBench Reasoning`：`1/1`，时延约 `130.76s`
- `SimpleQA`：`1/4`，平均时延约 `15.03s`

thinking 相关现象：

- `LiveBench` 平均 `first_thinking_sec` 约 `3.05s`
- `LiveBench` 平均 `first_response_sec` 约 `81.85s`
- `MMLU-Pro` 平均 thinking 文本约 `3478` 字符
- `SimpleQA` 平均 thinking 文本约 `908` 字符

## 额外观察

在运行 `e4b` 时，`ollama ps` 显示实际 context 为 `131072`，说明虽然请求值设为 `262144`，模型实际仍受自身上限约束；`26b` 则可实际使用 `262144`。

## 当前结论

1. 统一设置后的正式实验链路已经稳定。
2. `26b` 的 thinking 长度与最终答案出现时间明显高于 `e4b`。
3. `26b` 在知识推理与污染受控 benchmark 上表现更强，但代价是更长的等待时间。
4. `e4b` 在多语言推理与 `LiveBench` 上保持了较好的可用性，但事实性仍然是明显短板。
