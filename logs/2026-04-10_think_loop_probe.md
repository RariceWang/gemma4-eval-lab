# Think 循环诊断实验 2026-04-10

## 实验目的

验证一类关键问题：

> 已经进入 think 循环的样本，是否在关闭 `thinking` 后能够恢复正常完成？

这类实验不追求规模，而追求诊断性，因此只选用已知会出现循环的代表样本。

## 实验设置

### 1. Gemma 26B 诊断探针

- 模型：`gemma4:26b`
- 数据集：`datasets/frontier/gemma26b_think_loop_probe.jsonl`
- 配置：
  - `think=false`
  - `num_ctx=262144`

对应原始循环样本：

- `mmlu_prox_lite_en-71`
- `mmlu_prox_lite_zh-71`

输出目录：

- `outputs/gemma26b_think_loop_probe_thinkfalse_ctx256k_20260410/`

### 2. Qwen 9B 诊断探针

- 模型：`qwen3.5:9b`
- 数据集：`datasets/frontier/qwen9b_think_loop_probe.jsonl`
- 配置：
  - `think=false`
  - `num_ctx=262144`

对应原始循环样本：

- `mmlu_prox_lite_sw-70`
- `simpleqa-0`

输出目录：

- `outputs/qwen9b_think_loop_probe_thinkfalse_20260410/`

## 结果

### Gemma 26B

- `mmlu_prox_lite_en-71`
  - 原始 `think=true`：`long_think`，约 `900.66s`
  - 诊断 `think=false`：`ok`，约 `97.50s`
  - 得分：`0.0`
  - 输出：`A`
- `mmlu_prox_lite_zh-71`
  - 原始 `think=true`：`long_think`，约 `900.18s`
  - 诊断 `think=false`：`ok`，约 `75.88s`
  - 得分：`0.0`
  - 输出：`A`

结论：

- 关闭 thinking 后，Gemma 26B 不再循环
- 但它没有得到正确答案，而是快速给出错误答案

### Qwen 9B

- `mmlu_prox_lite_sw-70`
  - 原始 `think=true`：`interrupted`，约 `927.82s`
  - 诊断 `think=false`：`ok`，约 `11.54s`
  - 得分：`1.0`
  - 输出：`I`
- `simpleqa-0`
  - 原始 `think=true`：`long_think`，约 `600.06s`
  - 诊断 `think=false`：`ok`，约 `1.01s`
  - 得分：`0.0`
  - 输出：`Yann LeCun`

结论：

- 关闭 thinking 后，Qwen 9B 同样不再循环
- 在 `sw` 多选题上，关闭 thinking 反而恢复了正确完成
- 但在 `SimpleQA` 上，它只是快速给出错误答案

## 总结

这组诊断实验说明：

1. think 循环并不等于“模型不会做”
2. 对部分任务，关闭 thinking 可以把“不收敛”转化为“快速完成”
3. 但这种恢复并不保证正确率
4. 因此，thinking 的收益和风险应被分开报告：
   - 风险：可能导致不收敛循环
   - 收益：有时有助于更难题的最终正确性
   - 代价：可能把错误答案前的犹豫无限放大
