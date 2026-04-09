# 重任务阶段性状态 2026-04-09

## 已完成整理

重任务目录：

- `outputs/frontier_heavy_26b_thinktrue_ctx256k_20260408/`

当前已生成：

- `metadata.json`
- `raw_outputs.jsonl`
- `stream_events.jsonl`
- `summary.csv`
- `thinking_readable.md`

## 三条重任务当前状态

### 1. `mmlu_prox_lite_sw-70`

- 状态：`ok`
- 得分：`1.0`
- 总时长：约 `1813.74s`
- `first_thinking_sec ≈ 32.43s`
- `first_response_sec ≈ 1812.28s`
- `thinking_chars ≈ 35003`
- 最终答案：`I`

解读：

- thinking 在这条题上是“有效”的，因为最终给出了正确答案
- 但效率非常低，因为最终答案几乎在 30 分钟后才出现

### 2. `livebench_reasoning-bd14ba82d1fe813d`

- 状态：`long_think`
- 得分：无
- 已记录 thinking 时长：约 `2371.41s`
- `first_thinking_sec ≈ 36.75s`
- 尚未出现最终 response
- `thinking_chars ≈ 32279`

解读：

- 这条任务已按规则记为“长时间陷入 think”
- 从实时 thinking 内容看，它并非乱码，而是在不断重复校验同一组线索与答案
- 说明 thinking 有内容，但有效推进不足

### 3. `simpleqa-0`

- 状态：`long_think`
- 得分：无
- 已记录 thinking 时长：约 `867.49s`
- `first_thinking_sec ≈ 31.69s`
- 尚未出现最终 response
- `thinking_chars ≈ 23660`

解读：

- 这条也被记录为“长时间陷入 think”
- thinking 内容与问题相关，但没有及时收敛到最终答案

## 对 thinking 有效性的初步判断

### 有效的部分

- 在 `mmlu_prox_lite_sw-70` 上，thinking 最终导向了正确答案
- thinking 内容整体和任务强相关，不是随机噪声

### 无效的部分

- `LiveBench` 与 `SimpleQA` 都出现了长时间不收敛
- thinking 内容出现大量反复核对、重复表述、迟迟不进入最终响应
- 因而在重任务上，thinking 更像“高成本但不稳定的推理展开”

## 当前最稳妥的表述

可以在报告中写成：

1. `26b + think=true + 256k` 在复杂任务上能产生大量与任务相关的推理文本。
2. thinking 并不等价于高效求解，部分任务会出现长时间不收敛。
3. 对本地部署评测而言，应把 thinking 的“正确性收益”和“时间成本”分开报告。
