# Frontier Lab 方法升级

## 1. 方法总览

升级后的 lab 不再是“几个手工题 + 一张表”，而是一个可持续扩展的本地 benchmark runner。方法上有 4 个关键变化：

1. **数据源升级**：改用官方 benchmark 数据集的小样本子集
2. **评分升级**：按 benchmark 类型使用不同解析与匹配策略
3. **实验设计升级**：把能力、稳健性、效率一起纳入
4. **复现升级**：统一通过 Hugging Face dataset viewer API 构造本地任务集
5. **日志升级**：runner 改为流式记录 `thinking + response`，并增量写出原始结果

## 2. 新实验问题

### 主问题

`gemma4:e4b` 与 `gemma4:26b` 在前沿 benchmark 上的能力差异是否稳定存在？

### 子问题

- 更大模型是否在污染受控 benchmark 上依然明显更强？
- 更大模型是否在多语言高级推理上更稳？
- 更大模型的延迟代价是否与质量提升成比例？
- 本地小模型在事实性任务上是否更容易失败？

## 3. benchmark 选择逻辑

### 核心套件

| Benchmark | 作用 | 选用理由 |
|---|---|---|
| `MMLU-Pro` | 高难知识与推理 | 比经典 MMLU 更难、更稳定 |
| `MMLU-CF` | 污染受控知识推理 | 体现前沿评测对 contamination 的重视 |
| `MMLU-ProX-Lite` | 多语言高级推理 | 直接检验高级能力跨语言保持程度 |
| `LiveBench Reasoning` | 动态、自动评分推理 | 更接近持续更新 benchmark |
| `SimpleQA` | 短事实问答 | 检验 factuality 与幻觉控制 |

### 扩展套件

| Benchmark | 作用 | 备注 |
|---|---|---|
| `LongBench-v2` | 长上下文真实推理 | 当前机器默认不全量执行 |

## 4. 统一任务表示

每一条 benchmark 样本都会被转换成统一 JSONL 任务格式，核心字段包括：

- `benchmark`
- `group`
- `language`
- `prompt`
- `reference`
- `metric`
- `response_parser`
- `source`

## 5. 评分策略

### 多选题

适用：

- `MMLU-Pro`
- `MMLU-CF`
- `MMLU-ProX-Lite`
- `LongBench-v2`

评分：

- 从模型输出中提取第一个合法选项字母
- 与标准答案做大小写无关匹配

### 标签化答案

适用：

- `LiveBench Reasoning`

评分：

- 优先提取 `<solution>...</solution>` 中的内容
- 做归一化精确匹配

### 短事实问答

适用：

- `SimpleQA`

评分：

- 对大小写、空格、部分标点做归一化
- 优先 exact match
- 同时记录 reference 是否被响应完整包含

说明：

- 这不是 `SimpleQA` 官方完整评分器
- 当前实现适合本地小样本 pilot，不适合作为最终论文级结论

### Thinking 记录

本项目的正式实验统一使用：

- `think=true`

原因：

- 这是 Gemma 4 系列的默认推理模式之一
- 重任务中的 thinking 内容本身也是实验对象
- 需要把 thinking 作为正式输出的一部分记录下来

## 6. 新增记录指标

除准确率外，新增：

- `latency_sec`
- `first_thinking_sec`
- `first_response_sec`
- `prompt_chars`
- `thinking_chars`
- `response_chars`
- `status`
- `parsed_response`

## 7. 执行策略

### 默认执行

- `gemma4:e4b`
- `gemma4:26b`

### 默认不执行

- `gemma4:31b`

### benchmark 默认层级

1. `frontier_smoke`
2. `frontier_pilot_e4b`
3. `frontier_calibration_26b`
4. `frontier_heavy_26b`
5. `long_context_extension`

## 8. 结果分析方式

结果至少从以下维度分析：

1. **模型维度**：`e4b` vs `26b`
2. **benchmark 维度**：不同 benchmark 上是否表现一致
3. **语言维度**：`en` / `zh` / `sw`
4. **效率维度**：能力增益是否值得延迟代价
5. **thinking 维度**：thinking 内容长度、thinking 起始时间、最终答案起始时间

## 9. 当前限制

- 仍以本地模型推理为主，无法覆盖真正的 frontier closed models
- `LongBench-v2` 的全量评测不适合当前机器
- `SimpleQA` 目前仅做近似本地评分
- `26b` 的稳定可用区间明显窄于 `e4b`
- `26b` 在重任务上的时延可能被 thinking 阶段主导
- 暂未接入正式统计显著性检验
