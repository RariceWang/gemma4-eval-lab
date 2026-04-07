# Gemma 4 Series Eval Lab

一个面向课程作业的独立实验项目，用于比较 Gemma 4 系列模型在本地环境中的生成与推理表现，并保留完整研究与执行日志。

## 当前选题

题目暂定为：

**Gemma 4 系列本地可运行版本在多语言推理与开放式生成任务中的性能对比**

这个方向对应作业要求中的“大模型一系列版本性能对比”，同时兼顾实际可运行性：

- 本机已安装 3 个 Gemma 4 版本，可直接在本地复现实验。
- 可以自然形成至少 3 组对比数据。
- 3 页左右的报告结构清晰，容易写出“模型差异 + 任务差异 + 资源代价”的分析。

## 计划中的三组对比数据

1. 多语言数学推理：MGSM 风格子任务，指标为 `Exact Match`
2. 多语言常识推理：XCOPA 风格子任务，指标为 `Accuracy`
3. 开放式生成质量：摘要、改写、提纲生成，指标为人工打分

补充记录：

- 延迟与响应时间
- 输出长度
- 失败率

## 项目结构

```text
gemma4-eval-lab/
├── configs/
├── datasets/
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
- `31b` 在 24G 内存机器上不建议直接跑本地批量评测

运行一个最小试验：

```bash
python3 scripts/benchmark_runner.py \
  --dataset datasets/pilot/tasks.jsonl \
  --models gemma4:e4b gemma4:26b \
  --out outputs/pilot_run \
  --limit 3
```

运行完成后会生成：

- `outputs/.../raw_outputs.jsonl`
- `outputs/.../summary.csv`
- `outputs/.../metadata.json`

## 日志约定

- 研究与选题过程写入 `logs/`
- 实验方案写入 `docs/`
- 模型执行原始结果写入 `outputs/`

## 当前状态

- 已完成调研与题目收敛
- 已完成实验方案初稿
- 已完成最小评测脚本
- 已完成双模型冒烟测试
- 待执行：GitHub 远端创建与首次推送
