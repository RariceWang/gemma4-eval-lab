# Gemma 4 Frontier Eval Lab

一个面向课程作业与前沿 benchmark 调研的独立实验项目，用于比较 Gemma 4 系列模型在本地环境中的推理、事实性、多语言与污染受控 benchmark 表现，并保留完整研究与执行日志。

## 当前选题

题目暂定为：

**Gemma 4 系列本地可运行版本在前沿 LLM benchmark 上的能力与效率对比**

这个方向仍然属于“大模型一系列版本性能对比”，但方法已经升级为前沿评测版：

- 使用官方 benchmark 子集而不是只用手工题
- 显式纳入 benchmark contamination 问题
- 增加多语言高级推理与事实性评测
- 为长上下文扩展预留接口

## 当前前沿评测套件

默认核心套件：

1. `MMLU-Pro`
2. `MMLU-CF`
3. `MMLU-ProX-Lite`
4. `LiveBench Reasoning`
5. `SimpleQA`

可选扩展：

6. `LongBench-v2`

补充记录指标：

- 延迟与响应时间
- prompt 长度
- 输出长度
- 失败率
- 不同 benchmark 的稳健性差异

## 项目结构

```text
gemma4-eval-lab/
├── configs/
├── datasets/
│   ├── frontier/
│   └── pilot/
├── docs/
├── logs/
├── outputs/
└── scripts/
```

## 快速开始

先确认本地 `ollama` 服务可用，并且已拉取以下模型：

- `gemma4:e4b`
- `gemma4:26b`

可选扩展模型：

- `gemma4:31b`

说明：

- 默认实验只使用 `e4b` 与 `26b`
- 官方实验统一使用 `think=true`
- 默认上下文窗口统一设为 `256k`（`num_ctx=262144`）
- 特别重的任务单独提高超时上限
- `31b` 在 24G 内存机器上不建议直接跑本地批量评测

先构建前沿 benchmark 小样本任务集：

```bash
python3 scripts/build_frontier_suite.py \
  --suite frontier_smoke \
  --out datasets/frontier/frontier_smoke.jsonl
```

再运行小样本评测：

```bash
python3 scripts/benchmark_runner.py \
  --dataset datasets/frontier/frontier_smoke.jsonl \
  --models gemma4:e4b gemma4:26b \
  --out outputs/frontier_smoke_run \
  --think true \
  --num-ctx 262144 \
  --timeout 900
```

运行完成后会生成：

- `outputs/.../raw_outputs.jsonl`
- `outputs/.../summary.csv`
- `outputs/.../metadata.json`

可用的任务集：

- `datasets/frontier/frontier_smoke.jsonl`
- `datasets/frontier/frontier_pilot_e4b.jsonl`
- `datasets/frontier/frontier_calibration_26b.jsonl`
- `datasets/frontier/frontier_heavy_26b.jsonl`
- `datasets/frontier/long_context_extension.jsonl`

## 核心文档

- `docs/frontier_research_survey.md`
- `docs/frontier_methodology.md`
- `docs/experiment_plan.md`

## 日志约定

- 研究与选题过程写入 `logs/`
- 实验方案写入 `docs/`
- benchmark 执行原始结果写入 `outputs/`

## 当前状态

- 已完成初始课题收敛
- 已完成前沿 benchmark 调研
- 已完成 Hugging Face dataset viewer API 接入设计
- 已完成最小前沿评测脚手架
- 已完成本地双模型基础冒烟测试
- 已完成统一设置下的 `gemma4:26b` 正式校准集
- 已完成统一设置下的 `gemma4:e4b` 正式 pilot
- 所有正式运行现已记录 `prompt + thinking + response`

## 最新发现

截至 2026-04-08：

- 正式实验统一采用 `think=true` 与 `num_ctx=262144`
- `gemma4:26b` 在官方校准集上对 `MMLU-CF / MMLU-Pro / MMLU-ProX-Lite` 均跑通
- `gemma4:e4b` 在正式 pilot 上对 `MMLU-CF`、多语言推理和 `LiveBench` 表现稳定，但在 `SimpleQA` 上仍然偏弱
- `26b` 的 thinking 内容明显更长，尤其在更难题与中文题上更明显
- `e4b` 实际生效上下文上限为 `131072`，`26b` 则可实际跑到 `262144`
