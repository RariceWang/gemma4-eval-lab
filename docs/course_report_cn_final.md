# 面向本地部署的前沿大模型评测：Gemma 4 与 Qwen 3.5 的比较研究

## 摘要

随着大语言模型评测从经典静态 benchmark 排名转向更难、更强调污染控制、更多语言和更接近真实推理过程的前沿评测框架，课程项目如果仍然只依赖传统 benchmark，很难形成有说服力的结论。本文以本地可运行开源模型为对象，构建了一套由 `MMLU-Pro`、`MMLU-CF`、`MMLU-ProX-Lite`、`LiveBench Reasoning` 和 `SimpleQA` 组成的前沿评测流程，并同时记录得分、完成率、时延以及中间 thinking 文本长度。当前正式结果表明：在污染受控知识推理和高难知识推理任务上，`gemma4:26b` 强于 `gemma4:e4b`；但在多语言高级推理任务上，较大模型虽然在已完成样本上的得分更高，却更容易出现长时间不收敛，导致完成率下降。重任务案例进一步说明，`think=true` 并不天然等于更高的可用性。作为小参数量跨家族补充对照，`qwen3.5:9b` 可以在英文和中文 smoke 子集上完成任务，但在低资源语言与 factuality 上同样暴露出明显的长思考风险。综合来看，本地大模型评测不应只比较准确率，而应把完成率、时延与 thinking 行为一并纳入分析。

## 1. 引言

大语言模型的能力比较已经不再是“跑几个 benchmark 再列一张分数表”这么简单。经典 `MMLU` 等 benchmark 一度是大模型比较的核心工具，但随着模型能力提升和公开题库被反复使用，经典 benchmark 的区分度下降、训练-测试污染风险上升，已经越来越难真实反映模型的前沿能力。因此，当前更有代表性的评测趋势包括：使用更高难度的 benchmark 来拉开模型差异，使用污染受控或动态更新 benchmark 来降低数据泄漏影响，以及将多语言高级推理、长上下文理解和短事实问答重新纳入主评测框架。

在这样的背景下，本文希望把一个本地可执行的课程实验升级为更接近前沿研究风格的小型评测系统。与直接比较多个完全不同的模型不同，本文首先以 `Gemma 4` 同家族模型为主线，对比 `gemma4:e4b` 与 `gemma4:26b`，从而更好地控制架构家族变量，把重点放在参数规模、任务类型与本地运行行为的关系上。随后，本文进一步引入 `Qwen 3.5` 作为扩展对照，但不再把“能否安装”当作“能否纳入主实验”的充分条件，而是强调模型在当前机器上的实际可运行性。

围绕这一设置，本文关注三个问题。第一，较大模型在前沿 benchmark 上是否稳定优于较小模型。第二，这种优势究竟体现为更高得分，还是仅仅体现在部分 benchmark 上。第三，中间 thinking 文本究竟是更高质量推理的证据，还是会成为拖慢完成率与时延的主要来源。

## 2. 相关工作

前沿大模型评测的演化，主要体现在三个方向。第一，benchmark 难度提升。`MMLU-Pro` 相较经典 `MMLU` 引入了更复杂的问题和更多选项，从而提升区分度。第二，污染控制成为关键问题。`MMLU-CF` 通过 contamination-free 设计降低 benchmark 泄漏风险，`LiveBench` 则通过动态更新任务和自动客观评分避免静态 benchmark 过时。第三，多语言与长上下文评测的重要性明显提高。`MMLU-ProX` 直接关注高级推理在不同语言上的保持程度，`LongBench` 与 `LongBench v2` 则强调真实长上下文任务而不仅仅是简单检索。

在多语言推理方面，较早的 `MGSM` 和 `XCOPA` 已经表明，大模型在不同语言之间的推理能力并不稳定，尤其在低资源语言上更容易退化。更近一步的 `MMLU-ProX` 把高难度推理扩展到 29 种语言，因此为本文选择英文、中文和斯瓦希里语子集提供了直接依据。在 factuality 方面，`SimpleQA` 表明即使是较强模型，在短事实问答上仍然很难取得很高分数，因此它适合作为推理 benchmark 的补充，而不是可有可无的附加项。

与本文最直接相关的一条最新研究主线，是针对 reasoning model “过度思考”问题的分析与缓解。`Stop Overthinking` 综述系统整理了高效推理研究中的模型侧、输出侧和输入侧方法，指出 reasoning 输出过长已经成为当前大模型部署中的重要效率瓶颈[12]。`THOUGHTTERMINATOR` 则进一步强调，很多 reasoning 模型无法根据题目难度合理分配 token 预算，因此需要训练外的校准与截断机制来减少无效思考[13]。`Dynamic Early Exit in Reasoning Models` 提出在推理过程中监控过渡点并动态早停，说明“及时停止 thinking”本身已经成为一个独立研究问题[14]。`THINK-Bench` 从 benchmark 角度度量推理效率，指出大型 reasoning model 往往会在较简单题目上产生冗余思考[15]。最贴近本文实验现象的是 `Circular Reasoning`，该工作把 reasoning loop 明确区分为 `statement loops` 与 `numerical loops` 两类，并指出语义重复往往先于表面文本重复，是推理不收敛的核心症状[16]。本文对 think 循环的观察和分类，与这一研究方向高度一致。

本文不提出新的 benchmark，而是在课程项目尺度上回答一个更实际的问题：如何在单机本地部署条件下，用更符合前沿研究逻辑的 benchmark 重新组织模型比较实验，并从中得到既可复现又有研究价值的结论。

## 3. 方法

### 3.1 模型选择

本文主实验模型包括：

- `gemma4:e4b`
- `gemma4:26b`

扩展对照模型包括：

- `qwen3.5:9b`：作为小参数量跨家族扩展模型，已完成 smoke 级结果

这种设计使得本文同时具备两个层次的比较：

1. 同家族比较：`Gemma 4` 系列不同参数量
2. 跨家族补充：`Gemma E4B` 与 `Qwen 9B`

### 3.2 benchmark 设计

本文默认核心评测集包括：

1. `MMLU-Pro`
2. `MMLU-CF`
3. `MMLU-ProX-Lite`
4. `LiveBench Reasoning`
5. `SimpleQA`

其作用分别对应：

- 高难知识与推理
- 污染受控推理
- 多语言高级推理
- 动态推理 benchmark
- 短事实问答

### 3.3 推理与记录方式

所有 benchmark 样本都被统一转换成 JSONL 任务格式。正式实验统一采用：

- `temperature = 0.2`
- `top_p = 0.9`
- `think = true`
- 请求 `num_ctx = 262144`

runner 除了记录最终答案，还会流式记录：

- `latency_sec`
- `first_thinking_sec`
- `first_response_sec`
- `thinking_chars`
- `response_chars`
- `status`

在后续实验中，为避免单条任务卡住整轮实验，还引入了 `max_think_seconds` 上限，用于把极长 thinking 的任务结构化记为 `long_think`。

## 4. 实验设置

### 4.1 证据层级与样本量

为了避免把不同强度的证据混为一谈，本文将实验结果分为三个层级。

第一层级是正式主结果，用于支撑论文的主要结论，包括：

- `gemma4:e4b` 官方 pilot：`19` 条任务
- `gemma4:26b` 官方 calibration：`7` 条任务
- `gemma4:26b` safe pilot：`12` 条任务

因此，Gemma 主结论建立在一组已经完成的、相对稳定的正式实验之上。

第二层级是诊断实验，用于分析 think 循环及其与 `think=false` 的关系，包括：

- `gemma4:26b` think loop probe：`2` 条任务
- `qwen3.5:9b` think loop probe：`2` 条任务

这部分实验规模很小，但目标明确，主要用于诊断因果机制，而不是估计总体平均性能。

第三层级是探索性扩展结果，用于补充跨家族比较，包括：

- `qwen3.5:9b` smoke：`7` 条任务

因此，本文关于 `Qwen 9B` 的结论是“探索性扩展观察”，而不是与 Gemma 主结果同等强度的正式结论。对于这部分结果，本文会主动限制表述强度，避免过度推广。

当前已经完成的主实验包括：

- `gemma4:e4b` 官方 pilot
- `gemma4:26b` 官方 calibration
- `gemma4:26b` safe pilot
- `gemma4:26b` heavy case 对照

这些结果汇总在：

- `outputs/frontier_analysis_official_extended_20260409/`
- `outputs/frontier_analysis_heavy_compare_20260409/`
- `outputs/report_packet_20260409/`

同时，Qwen 扩展实验当前包括：

- `qwen3.5:9b` 的 smoke 对照  
  输出目录：`outputs/frontier_smoke_qwen35_9b_thinktrue_ctx256k_20260409/`  
  汇总目录：`outputs/frontier_analysis_qwen35_9b_smoke_20260409/` 与 `outputs/frontier_analysis_smoke_qwen_compare_20260409/`

## 5. 结果与分析

### 5.1 Gemma 主结果

表 1 给出了当前正式共享 benchmark 上 `gemma4:e4b` 与 `gemma4:26b` 的对照结果。

| Benchmark | E4B 得分 | E4B 完成率 | E4B 平均时延(s) | 26B 得分 | 26B 完成率 | 26B 平均时延(s) |
| --- | --- | --- | --- | --- | --- | --- |
| MMLU-CF | 1.0000 | 100.0% | 26.16 | 1.0000 | 100.0% | 35.48 |
| MMLU-Pro | 0.5000 | 100.0% | 54.20 | 0.8000 | 100.0% | 168.93 |
| MMLU-ProX-Lite (EN) | 0.5000 | 100.0% | 79.02 | 1.0000 | 66.7% | 347.87 |
| MMLU-ProX-Lite (ZH) | 1.0000 | 100.0% | 73.91 | 1.0000 | 66.7% | 415.19 |

从表 1 可以看出，`gemma4:26b` 的主要优势集中在高难知识推理与污染受控推理上：`MMLU-CF` 持平满分，`MMLU-Pro` 明显优于 `E4B`。但在多语言高级推理上，`26B` 的已完成样本得分虽然更高或持平，完成率却下降到 `66.7%`。因此，对本地前沿评测而言，仅报告得分是不够的，必须同时报告完成率。

### 5.2 heavy case 的意义

Gemma 26B 的 heavy case 更进一步说明了 thinking 的双刃剑特性。

| Task ID | Benchmark | think=false 状态 | think=false 时延(s) | think=true 状态 | think=true 时延(s) | think=true thinking 字符 |
| --- | --- | --- | --- | --- | --- | --- |
| mmlu_prox_lite_sw-70 | MMLU-ProX-Lite (SW) | ok | 2.06 | ok | 1813.74 | 35003 |
| livebench_reasoning-bd14ba82d1fe813d | LiveBench Reasoning | ok | 34.65 | long_think | 2371.41 | 32279 |
| simpleqa-0 | SimpleQA | ok | 1.85 | long_think | 867.49 | 23660 |

这说明在本地环境中，`think=true` 并不必然带来更高的可用性。它有时能够保留正确答案，但更多时候会把主要代价消耗在超长 thinking 阶段，而不是及时给出最终 response。

### 5.3 Qwen 9B 作为扩展对照

为了形成跨家族的小参数量比较，本文进一步比较了 `Qwen 9B` 与 `Gemma E4B` 在共享 smoke 任务上的表现。

| Task ID | Benchmark | E4B 状态 | E4B 得分 | E4B 时延(s) | Qwen 9B 状态 | Qwen 9B 得分 | Qwen 9B 时延(s) | Qwen 9B thinking 字符 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| livebench_reasoning-bd14ba82d1fe813d | LiveBench Reasoning | ok | 1.0 | 130.76 | ok | 1.0 | 334.02 | 6726 |
| mmlu_cf-0 | MMLU-CF | ok | 1.0 | 29.27 | ok | 1.0 | 50.62 | 1962 |
| mmlu_pro-70 | MMLU-Pro | ok | 1.0 | 40.69 | ok | 1.0 | 132.41 | 5427 |
| mmlu_prox_lite_en-70 | MMLU-ProX-Lite (EN) | ok | 1.0 | 30.39 | ok | 1.0 | 119.01 | 3997 |
| mmlu_prox_lite_sw-70 | MMLU-ProX-Lite (SW) | ok | 1.0 | 62.80 | long_think | - | - | - |
| mmlu_prox_lite_zh-70 | MMLU-ProX-Lite (ZH) | ok | 1.0 | 51.26 | ok | 1.0 | 368.62 | 10052 |
| simpleqa-0 | SimpleQA | ok | 0.0 | 26.70 | long_think | - | - | - |



### 5.4 非收敛样本与 think 循环分析

仅仅把失败样本记成 `long_think` 或 `interrupted` 还不够，因为不同失败样本的 thinking 形态并不相同。从当前记录中，可以辨认出两类主要非收敛模式。这一点与最新的 `Circular Reasoning` 工作高度一致：该研究将 reasoning loop 区分为 `statement loops` 和 `numerical loops`，并强调语义层面的重复往往先于表面文本重复[16]。本文的实验记录中，这两类现象都可以被清晰观察到。

第一类是“重复复核同一结论”的循环。这类样本已经在较早阶段得到稳定中间结论，但模型始终不进入最终回答。例如：

- `gemma4:26b / livebench_reasoning-bd14ba82d1fe813d`
  - 尾部 repeatedly 出现 `Wait, let me re-read the question...`
  - 反复核对 `Position 1 / Position 2 / journalist / police-officer / filmmaking`
  - 说明逻辑状态早已固定，但模型持续回放相同答案而不输出最终 `<solution>`
- `qwen3.5:9b / simpleqa-0`
  - thinking 尾部反复出现 `Okay, I'll output "Yann LeCun".`
  - 之后又继续 `Wait, I need to check if the answer is Yann LeCun`
  - 说明模型已经形成候选答案，但始终停留在“再确认一次”的循环中

  第二类是“重复重算或重复排除选项”的循环。这类样本主要出现在多选题或多语言推理题中，模型并不是没有思路，而是在不断重做已经完成过的计算或排除步骤。例如：

- `gemma4:26b / mmlu_prox_lite_en-71`
  - 多次重算 `30-10-2.5%`、`25-15-2%`、`15-15%` 与 `30%`
  - repeatedly 回到 `Option J` 再重新检查所有选项
- `gemma4:26b / mmlu_prox_lite_zh-71`
  - 同样反复重算折扣公式，重复比较 `30-10-2.5%` 与 `25-15-2%`
  - 已经得到 `Option J` 倾向，却继续回到前面重算
- `qwen3.5:9b / mmlu_prox_lite_sw-70`
  - 高频重复 `Vitendo visivyo salama, Msongo wa mawazo, Hofu, Nzito`
  - 反复把 `Vitendo salama` 判为错误，再重走同一排除链

  这说明当前本地 reasoning 模型的失败并不只是“慢”，而是存在可识别的非收敛机制：它们会在已经得到局部稳定答案后，继续对相同内容进行自我验证、重算或复核，从而把推理时间消耗在循环中，而不是输出最终响应。换言之，这类失败不应被简单理解为“模型需要更多时间”，而更接近当前前沿文献所讨论的 overthinking 或 circular reasoning 现象[12][13][16]。

  因此，本文对 `long_think` 或人工中断样本的表述不应写成笼统的“模型太慢”，而应更准确地写为：部分任务已经出现 think 循环或不收敛现象，主要表现为重复复核固定答案、重复计算相同公式，以及重复排除已排除过的选项。

### 5.5 think=false 诊断实验

为了进一步判断循环是否由 inference-time thinking 本身触发，本文对一组已经确认进入循环的样本进行了小型诊断实验，即在相同题目上关闭 `thinking` 后重新运行。

表 4 总结了这组诊断实验的核心结果。

| 模型 | 任务 | think=true 结果 | think=true 时延(s) | think=false 结果 | think=false 时延(s) | 解释 |
| --- | --- | --- | --- | --- | --- | --- |
| Gemma 26B | `mmlu_prox_lite_en-71` | `long_think` | 900.66 | 错误结束 | 97.50 | 关闭 thinking 后不再循环，但快速给出错误答案 |
| Gemma 26B | `mmlu_prox_lite_zh-71` | `long_think` | 900.18 | 错误结束 | 75.88 | 与英文样本一致，停止循环但未恢复正确性 |
| Qwen 9B | `mmlu_prox_lite_sw-70` | `interrupted`（think 循环） | 927.82 | 正确结束 | 11.54 | 关闭 thinking 后恢复正确完成 |
| Qwen 9B | `simpleqa-0` | `long_think` | 600.06 | 错误结束 | 1.01 | 关闭 thinking 后只是不再循环，并未提升 factuality |

对于 `gemma4:26b`，我们选取了两条在 `think=true` 下进入 `long_think` 的多语言折扣题：

- `mmlu_prox_lite_en-71`
- `mmlu_prox_lite_zh-71`

在 `think=false + 256k` 的诊断探针下，这两条题都不再循环，分别在约 `97.50s` 和 `75.88s` 内完成，但最终答案都错误，均输出 `A`。这说明对 Gemma 26B 而言，关闭 thinking 可以把“不收敛”转化为“快速结束”，但并不会恢复正确性。

对于 `qwen3.5:9b`，我们选取了两条最明显的循环样本：

- `mmlu_prox_lite_sw-70`
- `simpleqa-0`

诊断结果显示：

- `mmlu_prox_lite_sw-70`
  - `think=true`：约 `927.82s` 后仍未收敛
  - `think=false`：约 `11.54s` 正确完成
- `simpleqa-0`
  - `think=true`：约 `600.06s` 被记为 `long_think`
  - `think=false`：约 `1.01s` 快速返回错误答案 `Yann LeCun`

  因此，诊断实验支持一个更细的判断：关闭 thinking 的主要作用不是“普遍提升正确率”，而是“终止非收敛循环并迫使模型快速给出一个答案”。这个答案有时会恢复正确完成（如 `Qwen 9B / sw`），也可能只是更快地给出错误答案（如 `Gemma 26B / en71, zh71` 与 `Qwen 9B / SimpleQA`）。

  这说明在课程报告里，`think=true` 与 `think=false` 不应被写成简单的“开启推理”与“关闭推理”对比，而应被表述为一种能力-效率-收敛性三者之间的 trade-off：关闭 thinking 可以抑制循环，但也可能牺牲最终正确性。

### 5.6 总体结论

综合 Gemma 主结果、heavy case 和 `Qwen 9B` 扩展对照，本文得到三点更稳妥的结论：

1. 在污染受控推理和高难知识推理上，较大模型确实具有质量优势。
2. 这种优势不会自动迁移到多语言高级推理、低资源语言和 factuality 任务上。
3. 对本地部署场景而言，thinking 文本本身应被视为独立实验对象，而不能简单等同于“更好的推理”。

## 6. 结论

本文将一个课程层面的本地模型比较实验，重新组织为更符合当前前沿研究逻辑的评测流程。通过结合 `MMLU-Pro`、`MMLU-CF`、`MMLU-ProX-Lite`、`LiveBench Reasoning` 和 `SimpleQA`，并同时记录得分、完成率、时延和 thinking 行为，本文得到的结论明显比传统 benchmark 排名更细致。

主实验部分表明：`gemma4:26b` 在高难知识推理与污染受控推理上明显强于 `gemma4:e4b`，但代价是更高时延和更差的多语言稳定性。扩展实验部分进一步表明：`Qwen 9B` 虽然能够作为跨家族小参数量对照进入报告，但在低资源语言和短事实问答上同样存在长思考和不收敛问题。

因此，本文最核心的方法论结论是：本地大模型评测不应只围绕“谁得分更高”展开，而必须同时比较三类指标，即能力、完成率与推理成本。只有把这三者放在一起，课程项目才能真正接近前沿研究中的模型评测方式。

## 参考文献

[1] Hendrycks D, Burns C, Basart S, Zou A, Mazeika M, Song D, Steinhardt J. Measuring Massive Multitask Language Understanding[EB/OL]. arXiv:2009.03300, 2020. https://arxiv.org/abs/2009.03300

[2] Wang Y, Ma X, Zhang G, Ni Y, Chandra A, Guo S, Ren W, Arulraj A, He X, Jiang Z, Li T, Ku M, Wang K, Zhuang A, Fan R, Yue X, Chen W. MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark[EB/OL]. arXiv:2406.01574, 2024. https://arxiv.org/abs/2406.01574

[3] Zhao Q, Huang Y, Lv T, Cui L, Sun Q, Mao S, Zhang X, Xin Y, Yin Q, Li S, Wei F. MMLU-CF: A Contamination-free Multi-task Language Understanding Benchmark[EB/OL]. arXiv:2412.15194, 2024. https://arxiv.org/abs/2412.15194

[4] White C, Dooley S, Roberts M, Pal A, Feuer B, Jain S, Shwartz-Ziv R, Jain N, Saifullah K, Dey S, Shubh-Agrawal, Sandha S S, Naidu S, Hegde C, LeCun Y, Goldstein T, Neiswanger W, Goldblum M. LiveBench: A Challenging, Contamination-Limited LLM Benchmark[EB/OL]. arXiv:2406.19314, 2024. https://arxiv.org/abs/2406.19314

[5] Xuan W, Yang R, Qi H, Zeng Q, Xiao Y, Feng A, Liu D, Xing Y, Wang J, Gao F, Lu J, Jiang Y, Li H, Li X, Yu K, Dong R, Gu S, Li Y, Xie X, Juefei-Xu F, Khomh F, Yoshie O, Chen Q, Teodoro D, Liu N, Goebel R, Ma L, Marrese-Taylor E, Lu S, Iwasawa Y, Matsuo Y, Li I. MMLU-ProX: A Multilingual Benchmark for Advanced Large Language Model Evaluation[EB/OL]. arXiv:2503.10497, 2025. https://arxiv.org/abs/2503.10497

[6] Bai Y, Tu S, Zhang J, Peng H, Wang X, Lv X, Cao S, Xu J, Hou L, Dong Y, Tang J, Li J. LongBench v2: Towards Deeper Understanding and Reasoning on Realistic Long-context Multitasks[EB/OL]. arXiv:2412.15204, 2024. https://arxiv.org/abs/2412.15204

[7] OpenAI. Introducing SimpleQA[EB/OL]. 2024-10-30. https://openai.com/index/introducing-simpleqa/

[8] Google AI Edge Team. Bring state-of-the-art agentic skills to the edge with Gemma 4[EB/OL]. Google Developers Blog, 2026-04-02. https://developers.googleblog.com/bring-state-of-the-art-agentic-skills-to-the-edge-with-gemma-4/

[9] Shi F, Suzgun M, Freitag M, Wang X, Srivats S, Vosoughi S, Chung H W, Tay Y, Ruder S, Zhou D, Das D, Wei J. Language Models are Multilingual Chain-of-Thought Reasoners[EB/OL]. arXiv:2210.03057, 2022. https://arxiv.org/abs/2210.03057

[10] Ponti E M, Glavaš G, Majewska O, Liu Q, Vulić I, Korhonen A. XCOPA: A Multilingual Dataset for Causal Commonsense Reasoning[C]//Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP). 2020. https://aclanthology.org/2020.emnlp-main.185/

[11] Bai Y, Lv X, Zhang J, Lyu H, Tang J, Huang Z, Du Z, Liu X, Zeng A, Hou L, Dong Y, Tang J, Li J. LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding[EB/OL]. arXiv:2308.14508, 2023. https://arxiv.org/abs/2308.14508

[12] Sui Y, Chuang Y N, Wang G, Zhang J, Zhang T, Yuan J, Liu H, Wen A, Zhong S, Chen H, Hu X. Stop Overthinking: A Survey on Efficient Reasoning for Large Language Models[EB/OL]. arXiv:2503.16419, 2025. https://arxiv.org/abs/2503.16419

[13] Pu X, Saxon M, Hua W, Wang W Y. THOUGHTTERMINATOR: Benchmarking, Calibrating, and Mitigating Overthinking in Reasoning Models[EB/OL]. arXiv:2504.13367, 2025. https://arxiv.org/abs/2504.13367

[14] Yang C, Si Q, Duan Y, Zhu Z, Zhu C, Li Q, Lin Z, Cao L, Wang W. Dynamic Early Exit in Reasoning Models[EB/OL]. arXiv:2504.15895, 2025. https://arxiv.org/abs/2504.15895

[15] Li Z, Chang Y, Wu Y. THINK-Bench: Evaluating Thinking Efficiency and Chain-of-Thought Quality of Large Reasoning Models[EB/OL]. arXiv:2505.22113, 2025. https://arxiv.org/abs/2505.22113

[16] Duan Z, Pang L, Wei Z, Duan W, Tian Y, Xu S, Deng J, Yin Z, Cheng X. Circular Reasoning: Understanding Self-Reinforcing Loops in Large Reasoning Models[EB/OL]. arXiv:2601.05693, 2026. https://arxiv.org/abs/2601.05693
