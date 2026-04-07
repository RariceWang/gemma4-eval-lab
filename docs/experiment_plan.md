# 实验方案

## 1. 研究问题

**Gemma 4 系列本地可运行版本在前沿 benchmark 上的知识推理、污染受控评测、多语言高级推理、动态推理与事实性表现是否存在稳定差异？如果存在，这些差异体现在哪些 benchmark 与语言维度？**

## 2. 研究假设

- `H1`：`gemma4:26b` 在多数前沿客观 benchmark 上整体优于 `gemma4:e4b`
- `H2`：模型规模越小，在低资源语言上的性能下降越明显
- `H3`：污染受控与动态 benchmark 会拉低两者绝对分数，但保留相对差异
- `H4`：`gemma4:26b` 的质量增益将伴随明显时延代价

## 3. 模型选择

选择理由：

- 同一模型家族，控制变量更容易
- 本地已可运行，不依赖闭源 API
- 版本差异明确，适合做系列评测

默认本地模型列表：

| 模型 | 参数规模 | 上下文长度 | 预期定位 |
|---|---:|---:|---|
| `gemma4:e4b` | 8.0B | 131072 | 低成本、速度优先 |
| `gemma4:26b` | 25.8B | 262144 | 中档平衡 |

可选扩展模型：

| 模型 | 参数规模 | 上下文长度 | 说明 |
|---|---:|---:|---|
| `gemma4:31b` | 31.3B | 262144 | 能力优先，但 24G 内存机器不建议默认启用 |

## 4. 实验任务与前沿 benchmark

### 4.1 高难知识与推理：`MMLU-Pro`

- 数据来源：`TIGER-Lab/MMLU-Pro`
- 语言：英文
- 指标：`Exact Match`
- 输出约束：只返回选项字母
- 选择理由：区分度高于经典 `MMLU`

### 4.2 污染受控知识推理：`MMLU-CF`

- 数据来源：`microsoft/MMLU-CF`
- 语言：英文
- 指标：`Accuracy`
- 实际实现：四选一字母匹配
- 选择理由：显式控制 benchmark contamination

### 4.3 多语言高级推理：`MMLU-ProX-Lite`

- 数据来源：`li-lab/MMLU-ProX-Lite`
- 语言：`en` / `zh` / `sw`
- 指标：`Exact Match`
- 输出约束：只返回选项字母
- 选择理由：比较高级推理能力是否跨语言保持

### 4.4 动态推理：`LiveBench Reasoning`

- 数据来源：`livebench/reasoning`
- 语言：英文
- 指标：`Exact Match`
- 输出约束：按 benchmark 要求输出 `<solution>...</solution>`
- 选择理由：动态更新、自动评分、污染风险更低

### 4.5 短事实问答：`SimpleQA`

- 数据来源：`OpenEvals/SimpleQA`
- 语言：英文
- 指标：近似 `SimpleQA Match`
- 输出约束：只返回简短事实答案
- 选择理由：专门评测 factuality

### 4.6 可选扩展：`LongBench-v2`

- 数据来源：`zai-org/LongBench-v2`
- 语言：英文
- 指标：多选准确率
- 说明：默认不做全量执行，仅保留接口与扩展方案

## 5. 参数设置

为了保证公平性，默认统一使用：

- `temperature = 0.2`
- `top_p = 0.9`
- `num_ctx = 8192`
- 单轮推理，不做多次采样投票
- 默认优先 direct answer，不启用 self-consistency

控制原则：

- 同类任务使用统一提示模板
- 所有 benchmark 子集通过脚本自动拉取
- 所有样本保留来源信息与行号
- 默认先跑 `frontier_smoke`，再跑 `frontier_pilot`

## 6. 评估指标

### 客观指标

- `Exact Match`
- `Accuracy`
- 平均响应时延
- 失败率
- prompt 长度
- 输出长度

### 近似客观指标

- `SimpleQA Match`

## 7. 数据组织方式

至少形成 4 组对比数据：

1. **模型维度对比**：`e4b` 与 `26b`
2. **benchmark 维度对比**：`MMLU-Pro` / `MMLU-CF` / `LiveBench` / `SimpleQA`
3. **语言维度对比**：`MMLU-ProX-Lite` 上的 `en` / `zh` / `sw`
4. **效率维度对比**：延迟与质量的权衡

## 8. 实验执行流程

1. 运行环境检查并记录
2. 构建 `frontier_smoke`
3. 运行 `frontier_smoke`
4. 统计客观指标
5. 构建并运行 `frontier_pilot`
6. 汇总为表格与图表
7. 如有资源，再执行 `LongBench-v2` 扩展
8. 写报告

## 9. 风险与应对

- 风险：本地长任务耗时过长或内存不足
  - 应对：先跑子集，再扩展全量
- 风险：`31b` 超出本机舒适运行范围
  - 应对：默认不启用 `31b`，仅作为扩展实验
- 风险：`SimpleQA` 本地评分与官方评分不完全一致
  - 应对：显式标注为近似评分
- 风险：`LongBench-v2` 上下文过长
  - 应对：作为单独扩展执行
- 风险：动态 benchmark 后续还会变化
  - 应对：记录拉取日期与数据来源
