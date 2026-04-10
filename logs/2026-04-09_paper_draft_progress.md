# 论文草稿推进记录 2026-04-09

## 本轮新增内容

### 1. 课程论文草稿

- `docs/course_paper_draft.md`

当前已包含完整章节：

- `Abstract`
- `Introduction`
- `Related Work`
- `Method`
- `Experiment`
- `Results`
- `Conclusion`
- `References`

### 2. 图表脚本与图表产物

新增脚本：

- `scripts/render_report_figures.py`

生成图表：

- `outputs/report_packet_20260409/figure_shared_quality.png`
- `outputs/report_packet_20260409/figure_shared_latency.png`
- `outputs/report_packet_20260409/figure_heavy_cases.png`

### 3. 参考文献库

- `docs/course_paper_refs.bib`

可用于后续：

- LaTeX/BibTeX
- Word/Zotero 手工导入参考
- 正文引用清单校对

## 当前论文材料关系

### 正文主稿

- `docs/course_paper_draft.md`

### 报告主表与作图数据

- `outputs/report_packet_20260409/`

### 研究与结果日志

- `logs/2026-04-09_heavy_compare_findings.md`
- `logs/2026-04-09_pilot26b_safe_final.md`
- `logs/2026-04-09_report_packet.md`

## 当前状态

到这一步，仓库里已经具备一套相对完整的课程论文素材链：

1. 前沿调研
2. 正式实验输出
3. 论文主表
4. 图表文件
5. 正文草稿
6. 参考文献库

## 后续最顺的推进方向

1. 继续把 `docs/course_paper_draft.md` 压缩润色成最终提交版
2. 根据课程格式要求调整标题、页数、图表编号和参考文献样式
3. 如有需要，再补极少量对照实验来增强 `Results` 中的论证
