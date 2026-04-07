# 研究日志 2026-04-07

## 2026-04-07 16:59 CST

- 明确用户要求：先调研，再新建独立项目，不修改现有 `USTC_CG_26`
- 决定项目落地路径采用“两段式”：先在 `/tmp` 搭建，再移动到 `/Users/yixuwang/vsprojects/`

## 2026-04-07 17:00 CST

- 检查本地环境
- 发现 `ollama` 已安装，`gh` 未安装
- Python 版本为 `3.13.5`

## 2026-04-07 17:02 CST

- 枚举本地 Ollama 模型
- 当前可用模型：
  - `gemma4:e4b`
  - `gemma4:26b`
  - `gemma4:31b`

## 2026-04-07 17:05 CST

- 调研候选选题
- 初步比较后认为“Gemma 4 系列版本性能对比”最稳妥
- 原因：
  - 模型现成可跑
  - 不依赖闭源 API
  - 容易形成三组对比数据

## 2026-04-07 17:08 CST

- 查询 Gemma 4 官方资料
- 确认 Gemma 4 是面向本地/边缘部署的开放模型系列
- 记录官方来源用于后续写作和引用

## 2026-04-07 17:10 CST

- 确认使用 MGSM 风格题、XCOPA 风格题和开放式生成任务三类评测
- 决定正式报告聚焦：
  - 模型版本差异
  - 语言差异
  - 任务差异

## 结论

最终定题：

**Gemma 4 系列不同参数版本在多语言推理与开放式生成任务中的性能对比**

## 参考来源

1. Google Developers Blog
   [https://developers.googleblog.com/bring-state-of-the-art-agentic-skills-to-the-edge-with-gemma-4/](https://developers.googleblog.com/bring-state-of-the-art-agentic-skills-to-the-edge-with-gemma-4/)
2. Google AI for Developers
   [https://ai.google.dev/gemma/docs](https://ai.google.dev/gemma/docs)
3. MGSM 论文页面
   [https://huggingface.co/papers/2210.03057](https://huggingface.co/papers/2210.03057)
4. XCOPA 论文页面
   [https://aclanthology.org/2020.emnlp-main.185/](https://aclanthology.org/2020.emnlp-main.185/)
