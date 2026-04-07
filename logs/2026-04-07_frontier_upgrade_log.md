# 前沿升级日志 2026-04-07

## 背景

用户要求：

- 忽略原本 3 页左右篇幅限制
- 调研当前 LLM 前沿研究
- 用前沿 benchmark 完善实验方法
- 在 lab 中真正使用这些数据集进行 eval

## 调研结论

当前 LLM 评测前沿重点集中在：

1. 更高难度的知识与推理 benchmark
2. benchmark contamination 控制
3. 多语言高级推理
4. 长上下文真实推理
5. 事实性与可验证性

## 新 benchmark 选择

纳入核心套件：

- `MMLU-Pro`
- `MMLU-CF`
- `MMLU-ProX-Lite`
- `LiveBench Reasoning`
- `SimpleQA`

保留扩展：

- `LongBench-v2`

## 方法升级

- 新增 `frontier_suite.json`
- 新增 benchmark 构造脚本
- runner 升级为支持多种解析与评分模式
- 默认实验从手工题改为官方 benchmark 子集

## 资源约束

- 继续默认仅评测 `gemma4:e4b` 与 `gemma4:26b`
- `gemma4:31b` 仍作为禁用默认项
- `LongBench-v2` 不纳入默认 smoke 执行
