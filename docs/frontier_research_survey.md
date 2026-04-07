# 前沿 LLM 评测调研

## 1. 结论先行

到 2025-2026，LLM 评测的主线已经从“单一静态 benchmark 排名”转向更难、更真实、更新更快的评测框架，核心趋势有 5 个：

1. **更强的区分度**：经典 MMLU 等基准逐渐饱和，研究转向更难的推理题，如 `MMLU-Pro`
2. **更严格的污染控制**：训练-测试污染已成为主问题，出现 `MMLU-CF`、`LiveBench`、`AntiLeak-Bench`
3. **更真实的长上下文任务**：长 context 不再只测“捞针”，而是测真实理解与推理，如 `LongBench-v2`
4. **更多语言与文化边界**：英语之外的高级推理成为重点，如 `MMLU-ProX`
5. **更强调事实性与可验证性**：短事实问答和可自动打分任务重新受到重视，如 `SimpleQA`

## 2. 为什么原始 lab 不够前沿

此前 lab 主要使用：

- MGSM 风格数学题
- XCOPA 风格常识题
- 少量人工开放式生成题

这些任务适合课程起步，但在前沿评测视角下有明显不足：

- benchmark 难度不足
- 对污染问题没有显式控制
- 缺少短事实问答与动态 benchmark
- 没有覆盖长上下文能力
- 多语言评测还停留在基础难度

## 3. 当前前沿 benchmark 的代表方向

### 3.1 更难的知识与推理 benchmark

`MMLU-Pro` 相比原始 MMLU 引入更复杂的推理题，并把选项数从 4 扩展到 10，提升了区分度与提示稳定性。

### 3.2 污染受控 benchmark

`MMLU-CF` 的核心出发点是 benchmark contamination，会导致评测分数虚高。`LiveBench` 进一步采用动态更新与自动客观评分，降低静态 benchmark 过时风险。

### 3.3 多语言高级推理

`MMLU-ProX` 把 `MMLU-Pro` 扩展到 29 种语言，直接检验高级推理能力在不同语言上的保持程度。

### 3.4 长上下文真实推理

`LongBench-v2` 不再只是长上下文检索，而是使用真实长文档、多文档、长对话、代码仓库、结构化数据等任务。

### 3.5 事实性 benchmark

`SimpleQA` 聚焦短事实问答，强调问题可验证、答案简洁、评分稳定，是当前 factuality 评测中的高信号 benchmark。

## 4. 本项目最终选择

结合本机资源与可执行性，升级后的核心评测集为：

1. `MMLU-Pro`
2. `MMLU-CF`
3. `MMLU-ProX-Lite`
4. `LiveBench Reasoning`
5. `SimpleQA`

可选扩展：

6. `LongBench-v2`

## 5. 对 lab 方法的影响

- 从手工题目转为官方 benchmark 子集
- 从单一 `exact match` 转为按 benchmark 类型定制评分
- 从静态课程实验转为“可更新 benchmark 套件”
- 从只关注能力，扩展到能力-效率联合分析

## 6. 参考来源

1. MMLU-Pro paper page
   [https://huggingface.co/papers/2406.01574](https://huggingface.co/papers/2406.01574)
2. MMLU-Pro official dataset
   [https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro](https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro)
3. MMLU-CF paper page
   [https://huggingface.co/papers/2412.15194](https://huggingface.co/papers/2412.15194)
4. MMLU-CF official dataset
   [https://huggingface.co/datasets/microsoft/MMLU-CF](https://huggingface.co/datasets/microsoft/MMLU-CF)
5. MMLU-ProX paper page
   [https://huggingface.co/papers/2503.10497](https://huggingface.co/papers/2503.10497)
6. MMLU-ProX-Lite dataset
   [https://huggingface.co/datasets/li-lab/MMLU-ProX-Lite](https://huggingface.co/datasets/li-lab/MMLU-ProX-Lite)
7. LiveBench paper page
   [https://huggingface.co/papers/2406.19314](https://huggingface.co/papers/2406.19314)
8. LiveBench reasoning dataset
   [https://huggingface.co/datasets/livebench/reasoning](https://huggingface.co/datasets/livebench/reasoning)
9. LongBench v2 paper page
   [https://huggingface.co/papers/2412.15204](https://huggingface.co/papers/2412.15204)
10. LongBench-v2 dataset
   [https://huggingface.co/datasets/zai-org/LongBench-v2](https://huggingface.co/datasets/zai-org/LongBench-v2)
11. Introducing SimpleQA
   [https://openai.com/index/introducing-simpleqa/](https://openai.com/index/introducing-simpleqa/)
12. OpenEvals SimpleQA dataset
   [https://huggingface.co/datasets/OpenEvals/SimpleQA](https://huggingface.co/datasets/OpenEvals/SimpleQA)
