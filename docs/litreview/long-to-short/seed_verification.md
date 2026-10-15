# 种子论文核实（2026-10-15）

方法：arXiv 官方 API（`export.arxiv.org/api/query?id_list=...`）核对 ID/标题/作者/日期/comment；无 arXiv ID 的用 WebSearch 找 CVF / NeurIPS 官方页。
Semantic Scholar 匿名 API 对批量请求返回 429，仅 Repurpose-10K 一篇经 S2 交叉确认（paperId c2b36fe4…，venue 字段只写 arXiv.org）。
标注：`[F]` 在一手来源页面确认 · `[V]` 待核实。

| # | harness 给的名称 | 核实结果 | 状态 |
|---|---|---|---|
| 1 | Repurpose-10K, arXiv 2412.08879 | ID 存在。标题 **Video Repurposing from User Generated Content: A Large-scale Dataset and Benchmark**；Yongliang Wu 等 (+11)；v1 2024-12-12；comment: AAAI2025。**"Repurpose-10K" 这一数据集名未在元数据中见到，待读全文确认** | ID/标题/venue `[F]`；数据集名 `[V]` |
| 2 | HIVE, arXiv 2507.02790 | ID 存在。标题 **From Long Videos to Engaging Clips: A Human-Inspired Video Editing Framework with Multimodal Narrative Understanding**；Xiangfeng Wang 等 (+11)；2025-07-03；**EMNLP 2025 Industry Track**。"HIVE" 缩写与 "DramaAD" 待读全文确认 | ID/标题/venue `[F]`；缩写 `[V]` |
| 3 | Mr.HiSum, NeurIPS 2023 D&B | Sul, Han, Lee；31,892 视频，每视频聚合 5 万+用户的 Most Replayed 标签；官方页 https://proceedings.neurips.cc/paper_files/paper/2023/hash/7f880e3a325b06e3601af1384a653038-Abstract.html | `[F]`（来自官方 proceedings 页摘要）|
| 4 | SVHighlights, arXiv 2606.06926 | ID 存在。**SVHighlights: Towards Extremely Long Sport Video Highlight Detection**；Donggyu Lee 等 (+4)；2026-06-05；**KDD 2026 Datasets and Benchmarks Track**；项目页 leedongkyu2019.github.io/SVHighlights | `[F]` |
| 5 | TVHighlights, CVPR 2026 | 无 arXiv ID。CVF 页：**TVHighlights: LLM-Guided Human-Free Collaborative Training for Video Highlight Detection in Movies and TV Dramas**，Qi Qiu 等，CVPR 2026 pp. 9773–9783；1,721 视频，标签来自社区行为；方法 LTV-HD。https://openaccess.thecvf.com/content/CVPR2026/html/Qiu_TVHighlights_LLM-Guided_Human-Free_Collaborative_Training_for_Video_Highlight_Detection_in_CVPR_2026_paper.html。**领域是电影/电视剧，非播客语音** | `[F]` 元数据；数据集许可 `[V]` |
| 6 | Vidi, arXiv 2504.15681 | ID 存在。**Vidi: Large Multimodal Models for Video Understanding and Editing**，Vidi Team (+23)，v1 2025-04-22（当前 v3） | `[F]` |
| 7 | Vidi2, arXiv 2511.19529 | ID 存在，但**当前标题是 Vidi2.5: Large Multimodal Models for Video Understanding and Creation**（v2 2026-01-20；v1 2025-11-24，v1 标题是否为 Vidi2 待核）。引用时需注明标题变更 | ID `[F]`；"Vidi2" 命名 `[V]` |
| 8 | TimeLens, arXiv 2512.14698 | ID 存在。**TimeLens: Rethinking Video Temporal Grounding with Multimodal LLMs**，v2 2026-03-26 | `[F]`；venue `[V]` |
| 9 | Aha, arXiv 2509.16421 | ID 存在。**AHA — Predicting What Matters Next: Online Highlight Detection Without Looking Ahead**；Aiden Chang, Celso De Melo, Stephanie Lukin 等；**NeurIPS 2025** | `[F]` |
| 10 | Timeline-Bench, arXiv 2609.35143 | ID 存在。**Timeline-Bench: Evaluating Agents on Realistic Video-Editing Tasks, from Raw Footage to Final Cut**；Gunin Gupta 等 (+3)；2026-09-28 v1；**preprint, under review**（非已发表） | `[F]` |
| 11 | VlogReward, ICML 2026 | **更正（2026-10-15，Agent B 发现、我用 arxiv.org/abs 页面复核）**：arXiv 2607.22632 存在，标题 **VlogReward: Learning Multi-Dimensional Evaluation for Vlog Editing**，提交 2026-06-19，venue ICML 2026。我最初只搜到幻灯片，结论有误。Agent B 读了 arXiv HTML 的 1、3、4 与附录 A/B，认为其基准缺少独立人类一致性数字，不建议列 core。 | ID/标题 `[F]`；人类一致性结论 `[V]` |
| 12 | Otani et al. CVPR 2019, arXiv 1903.11328 | ID 存在。**Rethinking the Evaluation of Video Summaries**；Mayu Otani, Yuta Nakashima, Esa Rahtu, Janne Heikkilä；CVPR'19 poster | `[F]` |

## 对 harness 的修正建议
- #2：venue 应写 EMNLP 2025 Industry Track；#4：KDD 2026 D&B；#9：NeurIPS 2025。
- #7：标题已改为 Vidi2.5。
- #5 TVHighlights 与 HIVE 的 "DramaAD" 偏短剧/影视，对"语音为主"主域是次要域证据。
- #11 ID 已更正；是否 core 由 Agent B 的评估（缺独立人类相关数字）决定。
