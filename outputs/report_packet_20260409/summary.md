# Report Packet

本目录汇总了当前可直接用于课程报告写作的主表与作图数据。

## 内容

- `table_model_overview.*`: 模型基本信息
- `table_benchmark_overview.*`: benchmark 与指标说明
- `table_official_all_rows.*`: 正式结果逐模型逐 benchmark 主表
- `table_official_shared_benchmarks.*`: `E4B` 与 `26B` 在共享 benchmark 上的对照主表
- `table_heavy_case_studies.*`: heavy 阶段 `think=false` vs `think=true` 案例表
- `table_qwen9b_e4b_shared_smoke.*`: `Qwen 9B` 与 `E4B` 的共享 smoke 任务对照表
- `figure_shared_quality_latency.csv`: 共享 benchmark 的得分/完成率/时延作图数据

# Report Summary

## 共享 benchmark 对比

- MMLU-CF: `26B` 得分持平，完成率持平，平均时延约为 `E4B` 的 `1.4x`。
- MMLU-Pro: `26B` 得分更高，完成率持平，平均时延约为 `E4B` 的 `3.1x`。
- MMLU-ProX-Lite (EN): `26B` 得分更高，完成率更低，平均时延约为 `E4B` 的 `4.4x`。
- MMLU-ProX-Lite (ZH): `26B` 得分持平，完成率更低，平均时延约为 `E4B` 的 `5.6x`。

## Heavy Case Study

- MMLU-ProX-Lite (SW) / mmlu_prox_lite_sw-70: `think=false` 为 `ok`，`think=true` 为 `ok`，后者 thinking 约 `35003` 字。
- LiveBench Reasoning / livebench_reasoning-bd14ba82d1fe813d: `think=false` 为 `ok`，`think=true` 为 `long_think`，后者 thinking 约 `32279` 字。
- SimpleQA / simpleqa-0: `think=false` 为 `ok`，`think=true` 为 `long_think`，后者 thinking 约 `23660` 字。

## Qwen 9B vs E4B Shared-Task Comparison

- LiveBench Reasoning / livebench_reasoning-bd14ba82d1fe813d: `E4B` 为 `ok`、`Qwen 9B` 为 `ok`，后者时延 `334.02s`，thinking 约 `6726` 字。
- MMLU-CF / mmlu_cf-0: `E4B` 为 `ok`、`Qwen 9B` 为 `ok`，后者时延 `50.62s`，thinking 约 `1962` 字。
- MMLU-Pro / mmlu_pro-70: `E4B` 为 `ok`、`Qwen 9B` 为 `ok`，后者时延 `132.41s`，thinking 约 `5427` 字。
- MMLU-ProX-Lite (EN) / mmlu_prox_lite_en-70: `E4B` 为 `ok`、`Qwen 9B` 为 `ok`，后者时延 `119.01s`，thinking 约 `3997` 字。
- MMLU-ProX-Lite (SW) / mmlu_prox_lite_sw-70: `E4B` 为 `ok`、`Qwen 9B` 为 `long_think`，后者时延 `927.82s`，thinking 约 `20173` 字。
- MMLU-ProX-Lite (ZH) / mmlu_prox_lite_zh-70: `E4B` 为 `ok`、`Qwen 9B` 为 `ok`，后者时延 `368.62s`，thinking 约 `10052` 字。
- SimpleQA / simpleqa-0: `E4B` 为 `ok`、`Qwen 9B` 为 `long_think`，后者时延 `600.06s`，thinking 约 `11690` 字。
