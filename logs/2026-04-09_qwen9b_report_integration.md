# Qwen 9B 报告接入记录 2026-04-09

## 本轮完成事项

1. 将 `qwen3.5:9b` 从“计划中的补充模型”推进为“已完成 smoke 的扩展对照模型”
2. 完成并整理以下产物：
   - `outputs/frontier_smoke_qwen35_9b_thinktrue_ctx256k_20260409/`
   - `outputs/frontier_analysis_qwen35_9b_smoke_20260409/`
   - `outputs/frontier_analysis_smoke_qwen_compare_20260409/`
   - `outputs/report_packet_20260409/table_qwen9b_e4b_shared_smoke.md`
3. 将结果同步写回：
   - `docs/course_report_cn_draft.md`
   - `docs/qwen_comparison_plan.md`

## 当前最稳妥的结论

### 关于 `Qwen 27B`

- 不再继续补跑
- 只作为“本地资源受限下不可行的大参数尝试”写入课程报告

### 关于 `Qwen 9B`

- 可以进入课程报告作为小参数量跨家族对照
- 当前 smoke 结果显示：
  - 英文/中文任务可完成
  - `LiveBench` 可完成
  - `sw` 出现语义死循环
  - `SimpleQA` 被记为 `long_think`

## 对课程报告的作用

到这一步，中文报告中关于 Qwen 的写法已经从：

- “未来可以加入 Qwen”

推进为：

- “大参数 Qwen 试跑失败，已被排除”
- “小参数量 Qwen 9B 已有实际结果，可作为扩展对照”
