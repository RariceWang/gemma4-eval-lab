# Think 循环分析 2026-04-10

## 分析对象

本次分析聚焦所有已被记录为：

- `long_think`
- `interrupted`

且保留了较长 thinking 文本的任务。

涉及样本：

1. `gemma4:26b / livebench_reasoning-bd14ba82d1fe813d`
2. `gemma4:26b / simpleqa-0`
3. `gemma4:26b / mmlu_prox_lite_en-71`
4. `gemma4:26b / mmlu_prox_lite_zh-71`
5. `qwen3.5:9b / mmlu_prox_lite_sw-70`
6. `qwen3.5:9b / simpleqa-0`

## 观察到的两类循环

### 1. 重复复核同一结论

代表样本：

- `gemma4:26b / livebench_reasoning-bd14ba82d1fe813d`
- `qwen3.5:9b / simpleqa-0`

表现：

- 已经得到稳定中间答案
- 但不断回到：
  - “再读一遍问题”
  - “再确认一次候选答案”
  - “我将输出某个答案”

典型重复：

- `gemma4:26b / livebench_reasoning`
  - 高频重复 `Wait, let me re-read the question`
- `qwen3.5:9b / simpleqa-0`
  - 高频重复 `Okay, I'll output "Yann LeCun".`

解读：

- 这类任务的核心问题不是“不会做”
- 而是模型已经有答案倾向，但迟迟不进入最终 response

### 2. 重复重算或重复排除选项

代表样本：

- `gemma4:26b / mmlu_prox_lite_en-71`
- `gemma4:26b / mmlu_prox_lite_zh-71`
- `qwen3.5:9b / mmlu_prox_lite_sw-70`

表现：

- 反复重算相同折扣公式
- 反复比较已经比较过的选项
- 反复重走同一条排除链

典型重复：

- `gemma4:26b / mmlu_prox_lite_en-71`
  - 多次重算 `30-10-2.5%`、`25-15-2%`、`15-15%`
- `gemma4:26b / mmlu_prox_lite_zh-71`
  - 多次重复 `30-10-2(1/2)%` 相关计算
- `qwen3.5:9b / mmlu_prox_lite_sw-70`
  - 高频重复 `Vitendo visivyo salama, Msongo wa mawazo, Hofu, Nzito`

解读：

- 这类任务已经得到局部稳定答案
- 但模型通过不断重算和重排除，把推理时间消耗在循环中

## 当前最稳妥的判断

这些样本不应简单表述为“模型太慢”，而应更准确地写成：

1. 模型在部分任务上进入了非收敛 think 循环。
2. 循环的主要形式包括：
   - 重复复核固定答案
   - 重复重算相同公式
   - 重复排除已排除过的选项
3. 因而 `thinking_chars` 的增加并不等价于更高质量的推理结果。
