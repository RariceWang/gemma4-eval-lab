# 调研笔记

## 1. 选题筛选结果

最初候选方向有 4 类：

- 生成内容艺术性评估
- 生成模型安全性评估
- 多语言生成能力对比
- 大模型一系列版本性能对比

最终选择：

**以 Gemma 4 系列为对象，做“系列版本性能对比”，并把任务重点放在多语言推理与开放式生成。**

原因：

1. 本机已安装 `gemma4:e4b`、`gemma4:26b`、`gemma4:31b`，可直接本地复现实验。
2. 同系列模型更容易控制变量，适合写课程报告里的“公平比较”。
3. 多语言推理和开放式生成能自然形成至少 3 组对比数据，且指标清晰。

## 2. 模型选择依据

### Gemma 4

根据 Google Developers Blog 在 2026-04-02 发布的文章 *Bring state-of-the-art agentic skills to the edge with Gemma 4*，Gemma 4 是一个面向本地与边缘部署的开放模型系列，强调多语言支持、代理能力和本地运行能力。

本机 `ollama show` 结果显示：

- `gemma4:e4b`：8.0B，131072 context
- `gemma4:26b`：25.8B，262144 context
- `gemma4:31b`：31.3B，262144 context

这 3 个版本构成了适合课程实验的“同家族多尺度比较对象”。但结合本机 24G 内存约束，默认实际执行版本调整为：

- `gemma4:e4b`
- `gemma4:26b`

`gemma4:31b` 只作为可选扩展项保留在方案中。

## 3. 评测任务选择依据

### MGSM

`Language Models are Multilingual Chain-of-Thought Reasoners` 提出 MGSM，核心价值在于比较模型跨语言数学推理能力，并特别适合做 `Exact Match` 类型的可重复实验。

适合本项目的原因：

- 题目短，成本低
- 输出标准答案明确
- 可以观察低资源语言退化

### XCOPA

`XCOPA: A Multilingual Dataset for Causal Commonsense Reasoning` 是经典跨语言常识推理基准，适合用二选一准确率做稳定对比。

适合本项目的原因：

- 任务形式简单
- 便于统一提示模板
- 与数学推理形成互补

### 开放式生成

仅有客观题会让报告偏“刷题式评测”，不够体现生成模型的实际应用场景。因此补充：

- 中文摘要
- 英文学术改写
- 中文提纲生成

这组任务更贴近课程报告写作、信息压缩和结构化表达场景。

## 4. 预期分析点

- 小模型是否在中文和低资源语言上更容易退化
- 参数规模增长是否带来稳定的推理增益
- 大模型是否只在开放式生成中明显占优
- 延迟增加是否足以抵消质量提升

## 5. 参考来源

1. Google Developers Blog, *Bring state-of-the-art agentic skills to the edge with Gemma 4*, 2026-04-02
   [https://developers.googleblog.com/bring-state-of-the-art-agentic-skills-to-the-edge-with-gemma-4/](https://developers.googleblog.com/bring-state-of-the-art-agentic-skills-to-the-edge-with-gemma-4/)
2. Google AI for Developers, *Gemma models overview*
   [https://ai.google.dev/gemma/docs](https://ai.google.dev/gemma/docs)
3. Shi et al., *Language Models are Multilingual Chain-of-Thought Reasoners*
   [https://huggingface.co/papers/2210.03057](https://huggingface.co/papers/2210.03057)
4. Ponti et al., *XCOPA: A Multilingual Dataset for Causal Commonsense Reasoning*
   [https://aclanthology.org/2020.emnlp-main.185/](https://aclanthology.org/2020.emnlp-main.185/)
