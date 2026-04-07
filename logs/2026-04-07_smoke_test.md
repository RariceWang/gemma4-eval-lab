# 冒烟测试日志 2026-04-07

## 目的

- 验证本地 `ollama -> Python runner -> 文件输出` 链路可用
- 验证默认模型组合是否适合当前硬件

## 测试命令

```bash
python3 scripts/benchmark_runner.py \
  --dataset datasets/pilot/tasks.jsonl \
  --models gemma4:e4b gemma4:26b \
  --out outputs/pilot_smoke_20260407 \
  --limit 3
```

## 测试范围

- `math-en-001`
- `cs-en-001`
- `gen-zh-001`

## 结果摘要

| 模型 | 数学题 | 常识题 | 中文摘要 | 平均现象 |
|---|---|---|---|---|
| `gemma4:e4b` | 正确 | 正确 | 可用 | 速度快 |
| `gemma4:26b` | 正确 | 正确 | 可用 | 明显更慢 |

## 关键时延

- `gemma4:e4b`
  - 数学推理：约 5.01s
  - 常识推理：约 8.15s
  - 中文摘要：约 20.51s
- `gemma4:26b`
  - 数学推理：约 13.41s
  - 常识推理：约 6.93s
  - 中文摘要：约 36.62s

## 结论

1. 默认双模型评测链路可正常运行。
2. `e4b` 更适合快速批量实验，`26b` 更适合作为质量对照。
3. `31b` 在当前 24G 内存机器上不应作为默认实验对象。
