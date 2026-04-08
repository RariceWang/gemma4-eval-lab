# Streaming Thinking 日志 2026-04-08

## 目的

将正式实验切换到统一配置：

- `think=true`
- `num_ctx=262144`

并确保原始结果中保留：

- 输入 prompt
- thinking 内容
- 最终 response

## 现象

在手动 `ollama` 交互中，`gemma4:26b` 对 `mmlu_prox_lite_sw-70` 会长时间处于 `Thinking...` 状态，随后才给出最终答案 `I`。

使用流式 API 观察可知：

- `thinking` 内容会先持续流出
- 正式答案在 `response` 字段中更晚出现

## 方法调整

1. `benchmark_runner.py` 改为流式拉取
2. 每条样本记录以下字段：
   - `prompt`
   - `thinking`
   - `response`
   - `first_thinking_sec`
   - `first_response_sec`
3. 所有正式实验统一使用 `think=true`
4. 所有正式实验统一使用 `num_ctx=262144`
5. 特别重的任务使用更高超时上限

## 结论

此前的超时主要与 thinking 阶段过长有关，因此后续正式实验统一保留 `think=true` 的完整日志记录。
