# Report Packet 记录 2026-04-09

## 本轮目标

将当前前沿评测的正式结果与 heavy 风险结果整理成可直接用于课程报告的主表、案例表和作图数据，减少后续人工抄录和二次整理。

## 新增脚本

- `scripts/build_report_packet.py`

作用：

1. 从正式主表中生成报告级 Markdown/CSV 表格
2. 从 heavy 对照中生成案例表
3. 生成共享 benchmark 的质量/完成率/时延作图数据
4. 自动输出简短报告摘要

## 生成结果

输出目录：

- `outputs/report_packet_20260409/`

内容包括：

- `table_model_overview.*`
- `table_benchmark_overview.*`
- `table_official_all_rows.*`
- `table_official_shared_benchmarks.*`
- `table_heavy_case_studies.*`
- `figure_shared_quality_latency.csv`
- `summary.md`

## 目前最有价值的表

### 1. 正式共享 benchmark 对照主表

文件：

- `outputs/report_packet_20260409/table_official_shared_benchmarks.md`

它直接展示：

- `E4B` 与 `26B` 在共享 benchmark 上的得分差异
- 完成率差异
- 平均时延差异
- 平均 thinking 长度差异

这张表已经足够支撑结果分析部分的核心叙述。

### 2. Heavy 风险案例表

文件：

- `outputs/report_packet_20260409/table_heavy_case_studies.md`

它直接展示：

- 相同 task 在 `think=false` 与 `think=true` 下的状态差异
- 时延放大倍数
- `think=true` 的 thinking 规模

这张表适合放在结果分析或讨论部分，说明 `thinking` 的收益和成本分离。

### 3. 共享 benchmark 作图数据

文件：

- `outputs/report_packet_20260409/figure_shared_quality_latency.csv`

适合直接用于：

- 柱状图：score / completion_rate
- 折线图或条形图：latency_sec

## 当前状态

到这一步，项目已经从“实验跑完”推进到了“结果可直接写报告”。

后续若继续推进，最顺的路径是：

1. 直接基于 `report_packet_20260409` 写报告正文
2. 或继续补生成图表文件本身（例如 SVG/PNG/PDF）
