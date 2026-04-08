# Thinking Probe 日志 2026-04-08

## 目的

验证 `gemma4:26b` 在重任务上的超时究竟更像：

1. 上下文窗口设置问题
2. 共享内存/资源崩溃
3. `thinking` 阶段过长

## 关键实验

### 实验 1：同一任务，不同 `num_ctx`

任务：

- `mmlu_prox_lite_sw-70`

设置：

- `think=true`
- `num_ctx=8192`
- `timeout=240`

结果：

- `first_token_sec = null`
- `chunk_count = 0`
- `error = timed out`

对应文件：

- `outputs/probes/26b_sw_ctx8192_probe.json`

设置：

- `think=true`
- `num_ctx=2048`
- `timeout=240`

结果：

- `first_token_sec = null`
- `chunk_count = 0`
- `error = timed out`

对应文件：

- `outputs/probes/26b_sw_ctx2048_probe.json`

结论：

- 仅仅缩小 `num_ctx` 并没有解决问题
- “上下文窗口太小导致死循环”缺少证据支持

### 实验 2：同一任务，`think=true` vs `think=false`

任务：

- `mmlu_prox_lite_sw-70`

`think=true` 的前 12 个流式事件显示：

- 约 `12.5s` 开始出现流式输出
- 输出在 `thinking` 字段
- `response` 字段仍为空

`think=false` 的前 2 个流式事件显示：

- 约 `10.06s` 直接输出最终答案 `I`
- 没有 `thinking` 字段内容

结论：

- 模型并非“完全卡死”
- 在 `think=true` 下，它很快进入 thinking 流，但正式答案迟迟不出现
- 在 `think=false` 下，同题可以快速给出最终答案

### 实验 3：完整重任务集，`think=false`

任务集：

- `mmlu_prox_lite_sw-70`
- `livebench_reasoning-bd14ba82d1fe813d`
- `simpleqa-0`

设置：

- `think=false`
- `timeout=180`

结果：

- `mmlu_prox_lite_sw-70`：正确，约 `2.06s`
- `livebench_reasoning`：正确，约 `34.65s`
- `simpleqa-0`：错误，约 `1.85s`

结论：

- 之前 `26b` 在这些重任务上的超时，主因是 thinking 阶段过长
- 关闭 thinking 后，至少在当前 3 条重任务上，时延显著下降
- 因此后续报告中必须把 `think=true` 与 `think=false` 视作两个不同实验条件

## 当前判断

最合理的解释是：

1. `gemma4:26b` 能跑这些任务
2. `think=true` 时重任务会被 reasoning 阶段主导
3. 之前的 `300s` 超时更像是“thinking 太长”，而不是共享内存爆掉
4. `num_ctx` 调整不是主要矛盾
