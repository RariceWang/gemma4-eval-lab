# Qwen 对照扩展方案

## 1. 当前目标

在现有 `Gemma 4` 主实验基础上，加入 `Qwen 3.5` 系列模型，形成：

1. 同家族比较：`Gemma 4` 不同参数量
2. 跨家族比较：`Gemma 4` vs `Qwen 3.5`

这样可以让课程报告从“系列内部性能比较”进一步升级为“不同开放模型家族在前沿 benchmark 上的本地部署比较”。

## 2. 当前本地状态

截至 `2026-04-09`：

- 已安装：`qwen3.5:27b`
- 已安装：`qwen3.5:9b`

本地 `ollama show qwen3.5:27b` 显示：

- `architecture = qwen35`
- `parameters = 27.8B`
- `context length = 262144`
- `quantization = Q4_K_M`
- 支持 `thinking`

理论上它适合作为 `gemma4:26b` 的同级对照模型，但当前机器上的实际试跑结果并不支持把它作为正式主实验对象。

## 3. 推荐对照组合

### 3.1 当前最优先

- `gemma4:e4b` vs `qwen3.5:9b`
- `gemma4:26b` vs `qwen3.5:27b`

原因：

1. 参数规模最接近
2. 都支持本地运行
3. 便于讨论“家族差异”和“参数规模差异”两个维度

### 3.2 可选扩展

- `gemma4:31b` vs `qwen3.5:35b-A3B`

说明：

- 这一组更接近大参数上沿对比
- 但当前机器资源风险更高，不建议作为课程报告主结果

## 4. 建议实验层级

### 4.1 当前试跑结论

已对 `qwen3.5:27b` 尝试运行：

- `datasets/frontier/frontier_calibration_26b.jsonl`

得到的关键信号是：

- `mmlu_pro-70` 耗时约 `3187.98s` 且答错
- `mmlu_cf-0` 在开头阶段被人工中断

结论：

- `qwen3.5:27b` 在当前机器上的 `think=true + 256k` 前沿正式配置下不可行
- 因此不再继续补 `Qwen 27B` 的正式结果

### 4.2 下一步：小参数量对照

补充 `qwen3.5:9b` 后，运行：

- `datasets/frontier/frontier_pilot_e4b.jsonl`
  或
- `datasets/frontier/frontier_smoke.jsonl`

目的：

- 与 `gemma4:e4b` 建立同量级对照
- 检查 `Qwen 9B` 是否在 factuality、completion rate 或多语言稳定性上优于 `Gemma E4B`

当前阶段性结果：

- `mmlu_pro-70`：正确，约 `132.41s`
- `mmlu_cf-0`：正确，约 `50.62s`
- `mmlu_prox_lite_en-70`：正确，约 `119.01s`
- `mmlu_prox_lite_zh-70`：正确，约 `368.62s`
- `livebench_reasoning-bd14ba82d1fe813d`：正确，约 `334.02s`
- `mmlu_prox_lite_sw-70`：人工中断，约 `927.82s`
- `simpleqa-0`：`long_think`，约 `600.06s`

结论：

- `Qwen 9B` 明显比 `Qwen 27B` 更适合当前机器
- 但它在 `sw` 和 `SimpleQA` 上同样会出现长时间不收敛的 thinking 风险

### 4.3 是否补大参数 Qwen

当前建议：

- 不再继续补 `qwen3.5:27b`
- 只有在更强硬件条件下，才考虑重开大参数 Qwen 的正式前沿实验

## 5. 建议执行命令

### 已安装的 `qwen3.5:9b`

当前已完成一轮 smoke，输出目录：

- `outputs/frontier_smoke_qwen35_9b_thinktrue_ctx256k_20260409/`

若后续需要重跑，建议命令：

```bash
python3 scripts/benchmark_runner.py \
  --dataset datasets/frontier/frontier_smoke.jsonl \
  --models qwen3.5:9b \
  --out outputs/frontier_smoke_qwen35_9b_thinktrue_ctx256k_20260409 \
  --think true \
  --num-ctx 262144 \
  --timeout 900
```

## 6. 当前建议

1. 不再继续补 `qwen3.5:27b`
2. 后续若要加入 Qwen，对照优先级改为 `qwen3.5:9b`
3. `Qwen 9B` 当前已经具备写入课程报告“扩展实验”部分的基本证据
4. 课程报告正文优先写成：
   - 已完成主结果：`Gemma 4`
   - 已尝试但放弃的大参数 Qwen：`Qwen 27B`
   - 后续补强方向：小参数量 `Qwen 9B`
