# 面向本地部署的前沿大模型评测：Gemma 4 与 Qwen 3.5 的课程报告草稿

## Abstract

近年来，大语言模型评测已经从经典静态 benchmark 排名，转向更难、更强调污染控制、更多语言、更接近真实推理过程的前沿评测框架。为了让课程项目与当前研究趋势对齐，本文基于本地可运行的开源模型，构建了一套由 `MMLU-Pro`、`MMLU-CF`、`MMLU-ProX-Lite`、`LiveBench Reasoning` 和 `SimpleQA` 组成的前沿评测流程，并记录准确率、完成率、时延以及中间 thinking 文本长度等指标。当前已完成的正式结果表明：在污染受控知识推理和高难知识推理任务上，`gemma4:26b` 明显强于 `gemma4:e4b`；但在多语言高级推理任务上，较大模型虽然在已完成样本上的得分更高，却更容易出现长时间不收敛，导致完成率下降。重任务案例进一步说明，`think=true` 虽然能够产生大量与题目相关的推理文本，但这些中间推理并不必然转化为更高的任务完成率。除 Gemma 4 系列外，本文原本计划补充 `Qwen 3.5` 作为跨家族对照，但 `qwen3.5:27b` 的试跑结果表明它在当前机器上的正式前沿配置下代价过高，因此后续更合理的扩展方向是补充小参数量 `qwen3.5:9b`，而不是继续硬跑更大的 Qwen 模型。

## Introduction

课程层面的模型比较实验，通常容易落入“跑几个经典 benchmark，再列一张分数表”的模式。然而到 2025 至 2026 年，这种做法已经难以反映当前大模型能力的真实差异。经典 `MMLU` 一类 benchmark 已经逐渐饱和，公开测试题的训练污染问题也越来越严重，同时，英语之外的高级推理能力、动态更新 benchmark 的鲁棒性，以及短事实问答中的 factuality 问题，都已经成为前沿研究重点。因此，如果课程项目仍然停留在简单的静态 benchmark 排名上，就很难形成有说服力的结论。

本文的目标，是把一个本地可执行的课程实验，升级为一个更接近前沿研究风格的小型评测系统。与直接比较多个异构模型不同，本文首先以 `Gemma 4` 同家族模型为核心对象，对比 `gemma4:e4b` 与 `gemma4:26b` 在统一本地推理配置下的表现。这样做的好处是可以更好地控制模型家族差异，把焦点放在参数规模、推理过程和任务类型之间的关系上。随后，在课程允许扩展模型范围的前提下，本文原本希望引入 `Qwen 3.5` 作为跨家族对照。当前已经确认 `qwen3.5:27b` 在本地环境中安装完成，但试跑显示它并不适合当前机器上的正式主实验；因此，后续真正值得补充的是小参数量 `qwen3.5:9b`，因为它在量级上最接近 `gemma4:e4b`，更适合作为公平对照。

围绕这一实验框架，本文试图回答三个问题。第一，在前沿 benchmark 上，较大模型是否稳定优于较小模型。第二，这种优势究竟体现为更高的得分，还是仅体现为某些 benchmark 上的局部收益。第三，在本地部署场景中，中间 thinking 文本究竟是高质量推理的证据，还是会成为拖慢完成率和时延的主要因素。

## Related Work

### 经典大模型评测与其局限

`MMLU` 曾经是多任务语言理解评测的代表 benchmark，它覆盖 57 个学科任务，并为模型提供了统一的知识与推理评价框架。然而随着模型能力提升和公开题库反复使用，经典 `MMLU` 的区分度逐渐下降，也更容易受到训练-测试污染的影响。因此，越来越多的研究开始转向更难、更鲁棒的 benchmark 设计。

### 更高难度与更强区分度的 benchmark

`MMLU-Pro` 就是在这一背景下提出的。它通过筛除较容易题目、增加推理复杂度，并将选项数从 4 个提高到 10 个，从而显著提升了 benchmark 的区分度。相关研究报告表明，与原始 `MMLU` 相比，`MMLU-Pro` 会让模型分数下降 `16%` 到 `33%`，同时减少 prompt 敏感性。因此，在当前的大模型课程项目中，使用 `MMLU-Pro` 比继续依赖传统 `MMLU` 更符合前沿评测逻辑。

### 污染控制与动态 benchmark

训练-测试污染是当前 LLM 评测最核心的问题之一。`MMLU-CF` 针对这一问题提出 contamination-free 评测思路，通过更严格的数据构造与闭源测试划分，使得分数更接近真实泛化能力。与之互补的是 `LiveBench`，它通过持续引入新题、强调自动客观评分，进一步降低静态 benchmark 过时和泄漏的风险。对于本项目而言，这两类 benchmark 的意义在于：即使模型在传统公开题库上表现很好，也未必能在污染受控或动态更新 benchmark 上保持同样优势。

### 多语言高级推理与长上下文评测

在多语言方向，早期的 `MGSM` 和 `XCOPA` 已经表明，大模型跨语言推理能力并不稳定，尤其在低资源语言上更容易退化。更近一步的 `MMLU-ProX` 直接把 `MMLU-Pro` 扩展到 29 种语言，使得研究者能够比较不同语言下高级推理能力是否同步保持。其报告指出，高资源语言与低资源语言之间可能存在显著性能差距，这也是本文引入 `MMLU-ProX-Lite` 英文、中文与斯瓦希里语子集的直接动机。

在长上下文方向，`LongBench` 与 `LongBench v2` 则说明，长上下文评测已经不再只是“捞针”式检索，而是强调真实长文档、多文档与复杂任务中的推理能力。虽然本项目受限于本地资源，没有将 `LongBench v2` 纳入默认正式结果，但其结论对于理解“长 thinking 是否可能带来真实推理收益”仍然具有参考价值。

### factuality 与短事实问答

`SimpleQA` 把注意力重新拉回到短事实问答这一高信号场景。相比开放式生成任务，短事实问答更容易验证，也更适合观察模型是否出现稳定幻觉。OpenAI 在其介绍中指出，即使是较强的模型，在 `SimpleQA` 上也很难取得很高分数。因此，把 `SimpleQA` 和推理 benchmark 放在同一个实验框架里，可以避免只看推理分数而忽略 factuality 弱点。

### 本文的位置

本文并不提出新的 benchmark，而是试图回答一个更实际的问题：在单机本地部署条件下，如何用当前前沿 benchmark 重新组织课程实验，并从中得到仍然有研究价值的结论。本文的贡献主要体现在方法设计和经验观察上，而不是 benchmark 创新本身。

## Method

### 模型选择

当前主实验模型包括：

- `gemma4:e4b`
- `gemma4:26b`

扩展对照模型包括：

- `qwen3.5:27b`：本地已安装，但试跑显示在当前机器上的正式前沿配置下代价过高，因此不纳入最终主实验
- `qwen3.5:9b`：计划补充的小参数量 Qwen，对应 `gemma4:e4b` 的同量级对照

这样设计的原因有两点。第一，Gemma 4 系列内部比较可以控制家族变量，便于观察参数规模带来的变化。第二，跨家族引入 Qwen 可以让结论不局限于单一模型家族。但在当前机器条件下，这种扩展必须建立在“能稳定跑完”的前提上，因此更现实的路线是优先补充 `Qwen 9B`，而不是继续扩张到 `Qwen 27B`。

### benchmark 设计

本文默认核心评测集包括：

1. `MMLU-Pro`
2. `MMLU-CF`
3. `MMLU-ProX-Lite`
4. `LiveBench Reasoning`
5. `SimpleQA`

其中：

- `MMLU-Pro` 对应高难知识与推理
- `MMLU-CF` 对应污染受控推理
- `MMLU-ProX-Lite` 对应多语言高级推理
- `LiveBench Reasoning` 对应动态推理 benchmark
- `SimpleQA` 对应短事实问答

### 推理与评分流程

所有 benchmark 样本都会被统一转换成 JSONL 任务格式，包含 `benchmark`、`group`、`language`、`prompt`、`reference`、`metric` 和 `response_parser` 等字段。多选题任务统一使用选项字母匹配，`LiveBench Reasoning` 提取 `<solution>` 标签，`SimpleQA` 使用本地近似匹配规则进行评分。

在推理设置上，正式实验统一采用：

- `temperature = 0.2`
- `top_p = 0.9`
- `think = true`
- 请求 `num_ctx = 262144`

runner 会流式记录：

- `latency_sec`
- `first_thinking_sec`
- `first_response_sec`
- `thinking_chars`
- `response_chars`
- `status`

后续为了避免单条任务卡死整轮实验，还加入了 `max_think_seconds` 上限，使得过长推理会被结构化记为 `long_think`。

## Experiment

### 已完成实验

当前已经完成的正式实验主要包括：

- `gemma4:e4b` 的官方 pilot
- `gemma4:26b` 的官方 calibration
- `gemma4:26b` 的 safe pilot
- `gemma4:26b` 的 heavy case 对照

这些结果已经汇总为：

- `outputs/frontier_analysis_official_extended_20260409/`
- `outputs/frontier_analysis_heavy_compare_20260409/`
- `outputs/report_packet_20260409/`

### 当前 Qwen 扩展状态

截至 `2026-04-09`，本地已确认存在：

- `qwen3.5:27b`

本地 `ollama show qwen3.5:27b` 显示：

- 参数规模：`27.8B`
- 上下文长度：`262144`
- 量化：`Q4_K_M`
- 支持 `thinking`

理论上这使得它适合作为 `gemma4:26b` 的跨家族对照模型，因此我们曾经启动一轮与 `gemma4:26b` 同口径的正式校准集：

- 数据集：`datasets/frontier/frontier_calibration_26b.jsonl`
- 配置：`think=true + num_ctx=262144`
- 输出目录：`outputs/frontier_calibration_qwen35_27b_thinktrue_ctx256k_20260409/`

但试跑结果表明，该模型在当前机器上不适合作为课程报告主实验：

- `mmlu_pro-70` 耗时约 `3187.98s`，且最终答错
- 随后的 `mmlu_cf-0` 尚未形成正式结果就被人工中断

因此，本文后续不继续补 `Qwen 27B` 的正式结果，而把它作为“本地中大参数跨家族模型在当前机器上不可行”的工程性证据。

此外，当前已经开始补充：

- `qwen3.5:9b`

并已在 `frontier_smoke` 上得到一轮完整 smoke 结果，作为 `gemma4:e4b` 的跨家族小参数量对照。

## Results

### 当前 Gemma 主结果

当前正式主结果表明：

1. `gemma4:26b` 在 `MMLU-CF` 上表现最稳定，扩展正式结果中达到 `1.0000`
2. `gemma4:26b` 在 `MMLU-Pro` 上优于 `gemma4:e4b`，得分分别为 `0.8000` 和 `0.5000`
3. `gemma4:26b` 在 `MMLU-ProX-Lite` 的英文和中文子集上，已完成样本得分不低于 `gemma4:e4b`，但完成率只有 `66.7%`
4. `gemma4:e4b` 的最大优势不在绝对得分，而在完成率和运行稳定性

### heavy case 的结论

在 `26B` 的 heavy case 对照中，可以看到更明显的风险：

- `MMLU-ProX-Lite (SW)`：`think=false` 仅需 `2.06s`，`think=true` 却扩展到 `1813.74s`
- `LiveBench Reasoning`：`think=false` 能正常完成，`think=true` 被记为 `long_think`
- `SimpleQA`：`think=true` 产生大量 thinking 文本，但仍未能在合理时间内完成任务

这说明在本地场景中，较大模型的 thinking 能力并不天然等于更高的可用性。

### 当前对 Qwen 的意义

引入 `Qwen 3.5` 的价值，不在于简单替换 Gemma，而在于回答一个更强的问题：当前观察到的“高质量但高风险”的模式，是 `Gemma 4 26B` 的家族特征，还是更普遍的大参数推理模型现象。

不过当前试跑也说明，这个问题不能通过任意选择一个大参数 Qwen 来强行回答。对于本课程项目而言，更重要的是得到能在本地稳定复现的比较结果。因此，`Qwen` 的现实意义不再是“继续补 `27B`”，而是“优先补一个能稳定完成实验的小参数量版本”，也就是 `qwen3.5:9b`。

从当前 `qwen3.5:9b` 的 smoke 结果看，它已经能够在 `MMLU-Pro`、`MMLU-CF`、`MMLU-ProX-Lite en`、`MMLU-ProX-Lite zh` 和 `LiveBench` 上完整给出正确答案，说明它确实比 `Qwen 27B` 更适合作为课程报告中的实际扩展对照对象。但与此同时，它在 `MMLU-ProX-Lite sw` 上出现了语义死循环，在 `SimpleQA` 上也被结构化记为 `long_think`。这表明“低资源语言和 factuality 场景中的长思考风险”并不只属于 Gemma 系列，也可能是当前本地 reasoning 模型的更普遍问题。

如果与 `gemma4:e4b` 的同题 smoke 结果相比，`Qwen 9B` 目前呈现出一种更尖锐的特征：在英文和中文 smoke 子集上，它能够完成并答对所有已完成样本，但平均时延明显高于 `E4B`；而在低资源语言和短事实问答上，它反而更容易进入无法及时收敛的 thinking 状态。换言之，`Qwen 9B` 并不是一个“更强的小模型”，而更像是一个“在部分任务上更激进、但稳定性更弱”的小参数量 reasoning 模型。

## Conclusion

本文当前已经建立了一条较完整的中文课程报告路线：以前沿 benchmark 为主线，以本地可复现 runner 为基础，以能力、时延、完成率和 thinking 行为为联合指标，对 Gemma 4 系列进行系统比较。现有结果表明，较大模型在高难知识推理与污染受控推理上确实更强，但其收益并不稳定地迁移到多语言高级推理和重任务上；相反，长时间 thinking 常常成为本地场景中的主要瓶颈。

接下来的最重要扩展，是继续把 `qwen3.5:9b` 作为小参数量跨家族对照模型，补充到现有 Gemma 主实验框架中。相比之下，`qwen3.5:27b` 已经通过试跑证明不适合作为当前机器上的正式主实验对象。因此，最终课程报告更现实的升级方向是：“Gemma 4 主结果 + Qwen 3.5 小参数量补充对照”，而不是继续扩张到难以稳定完成的大参数 Qwen 模型。

## References

当前参考文献主库见：

- `docs/course_paper_refs.bib`

正文引用对应的核心来源包括：

1. `MMLU`
2. `MMLU-Pro`
3. `MMLU-CF`
4. `MMLU-ProX`
5. `LiveBench`
6. `LongBench v2`
7. `SimpleQA`
8. `Gemma 4` 官方博客
9. `MGSM`
10. `XCOPA`
