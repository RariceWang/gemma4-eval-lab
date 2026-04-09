# 阶段性结果整理 2026-04-08

## 1. 已完成的正式结果

### 1.1 `gemma4:26b` 官方校准集

数据来源：

- `outputs/frontier_calibration_26b_thinktrue_ctx256k_20260408/summary.csv`

可读结论：

- `MMLU-CF`：`4/4` 正确，平均时延约 `32.98s`
- `MMLU-Pro`：`1/1` 正确，时延约 `84.17s`
- `MMLU-ProX-Lite en`：`1/1` 正确，时延约 `70.47s`
- `MMLU-ProX-Lite zh`：`1/1` 正确，时延约 `158.18s`

thinking 特征：

- `MMLU-CF` 平均 `first_thinking_sec ≈ 6.23s`
- `MMLU-CF` 平均 `first_response_sec ≈ 32.71s`
- `MMLU-ProX-Lite zh` thinking 长度约 `5620` 字符

初步解读：

- `26b` 在知识推理与污染受控 benchmark 上表现强
- 但更难、更重的题会显著延长 thinking 阶段

### 1.2 `gemma4:e4b` 官方 pilot

数据来源：

- `outputs/frontier_pilot_e4b_thinktrue_ctx256k_20260408/summary.csv`

可读结论：

- `MMLU-CF`：`4/4`，平均时延约 `26.16s`
- `MMLU-Pro`：`2/4`，平均时延约 `54.20s`
- `MMLU-ProX-Lite en`：`1/2`，平均时延约 `79.02s`
- `MMLU-ProX-Lite zh`：`2/2`，平均时延约 `73.91s`
- `MMLU-ProX-Lite sw`：`2/2`，平均时延约 `77.22s`
- `LiveBench Reasoning`：`1/1`，时延约 `130.76s`
- `SimpleQA`：`1/4`，平均时延约 `15.03s`

thinking 特征：

- `LiveBench` 的 `first_thinking_sec ≈ 3.05s`
- `LiveBench` 的 `first_response_sec ≈ 81.85s`
- `SimpleQA` 平均 thinking 长度约 `908` 字符，但得分仍只有 `0.25`

初步解读：

- `e4b` 的整体可用性更稳
- 但事实性是明确短板

## 2. 正在进行中的正式重任务

数据来源：

- `outputs/frontier_heavy_26b_thinktrue_ctx256k_20260408/raw_outputs.jsonl`
- `outputs/frontier_heavy_26b_thinktrue_ctx256k_20260408/stream_events.jsonl`

### 2.1 已完成样本：`mmlu_prox_lite_sw-70`

结果：

- 正确
- 总时长约 `1813.74s`
- `first_thinking_sec ≈ 32.43s`
- `first_response_sec ≈ 1812.28s`
- `thinking_chars ≈ 35003`
- `response_chars = 28`

解读：

- 这不是“完全跑不动”
- 模型很早就进入 thinking
- 但最终答案直到将近 30 分钟才出现

### 2.2 进行中样本：`livebench_reasoning-bd14ba82d1fe813d`

当前从 `stream_events.jsonl` 可见：

- 已记录流式事件约 `4237` 条
- 最新 thinking 时间戳约 `1449.48s`
- 仍然只有 thinking，尚无最终 response 落盘

解读：

- `LiveBench` 在 `26b + think=true + 256k` 下属于极重任务
- 当前至少说明 thinking 一直在持续推进，而非进程崩溃

## 3. 对 thinking 有效性的初步判断

### 3.1 thinking 是有“效果”的

证据：

- `26b` 在校准集和重任务的已完成样本上都能给出正确答案
- 当前重任务中，thinking 内容极长且与题目直接相关，不是明显乱码或无关输出

### 3.2 thinking 的“效率”目前很差

证据：

- `mmlu_prox_lite_sw-70`：thinking 约 `35k` 字符，但为了得到一个单字母答案耗时约 `1814s`
- `LiveBench` 当前也已经超过 `1400s`，仍未出最终答案

### 3.3 当前更像“过度思考”而不是“高效推理”

理由：

- 在很多任务里，thinking 很早开始，但最终 response 极晚出现
- `first_thinking_sec` 和 `first_response_sec` 的差值非常大
- 说明主要时间花在中间推理展开，而不是输入装载或解码首 token

## 4. 当前最稳妥的结论表述

可以在报告中先写成：

1. `think=true` 的 Gemma 4 模型能在复杂任务上产生大量与任务相关的中间推理文本。
2. 这些中间推理并不必然转化为更高的单位时间收益。
3. 对 `26b` 而言，重任务上的主要瓶颈是超长 thinking 阶段，而不是显存或共享内存崩溃。
4. 在当前本地环境中，应将 thinking 的“质量收益”和“时间代价”分开分析。
