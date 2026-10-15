# Agent B search log（簇 3 边界相关 + 簇 6 评测方法学；2026-10-15）

工具说明：WebSearch / WebFetch（Claude Code 内置）；Bash curl（arxiv.org/html、ar5iv、api.openalex.org、export.arxiv.org、api.semanticscholar.org）。未使用 Undermind / Elicit / Asta（需登录）。未下载 PDF；WebFetch 直接取 arxiv.org/pdf/1903.11328 返回二进制，已改用 ar5iv 文本。
WebFetch 返回的是小模型摘要，凡用于数字的页面都已用 curl 取 HTML 文本二次核对（Otani、TimeLens、Timeline-Bench、MEDit-Bench、Vidi、Time-R1、QVHighlights、How Should、VlogReward、Stiennon、MT-Bench）。

## 一、种子直读
| 目标 | 工具 | 结果 |
|---|---|---|
| Otani 2019 abs / 全文 | WebFetch arxiv.org/abs/1903.11328；WebFetch ar5iv.labs.arxiv.org/html/1903.11328；curl 同 URL 取原文核对 Table 1/2 | 命中，full-text |
| TimeLens abs / 全文 | WebFetch abs；curl arxiv.org/html/2512.14698v2 → sed 去标签 → grep | 命中；WebFetch 对该 HTML 的摘要不完整，改 curl |
| Timeline-Bench | curl arxiv.org/abs/2609.35143（命中）；arxiv.org/html/2609.35143 返回 abs 页；arxiv.org/html/2609.35143v1 命中全文 | 命中；v2 为 404 |
| Vidi / VUE-TR | curl arxiv.org/html/2504.15681 | 命中 |
| VlogReward | WebSearch "VlogReward ICML 2026 reward model vlog video editing human preference"；WebFetch icml.cc/virtual/2026/poster/61914；OpenAlex works?search=VlogReward | **brief 称 arXiv 未找到，但 OpenAlex 命中 arXiv:2607.22632（abs 页与 HTML 可访问，2026-06-19 提交）**；已读 sections |

## 二、簇 3（时刻检索/边界）query
1. WebSearch "Time-R1 post-training large vision language model temporal video grounding RL IoU reward arXiv" → Time-R1 (2503.13377)；curl html v3 读 sections。
2. WebSearch "boundary refinement video moment retrieval candidate boundaries snapping vs direct timestamp regression ablation" → CMIN、BMRN、ClipTBP(2604.27591)、FlashMMR；**未找到**直接对比"候选切点选择 vs 连续回归"的消融（搜索结果自己也如此陈述）。
3. WebSearch "temporal grounding precise boundary high IoU threshold 0.9 metric limitation video LLM timestamp error seconds" → 命中 "How Should Video LLMs Output Time?"(2604.08966)、DisTime、TSGV survey；**未找到**报告 IoU@0.9 的 MLLM 时刻检索论文（TimeLens/Time-R1 均止于 0.7）。
4. WebSearch "DisTime distribution-based time representation ..." → DisTime ICCV 2025 (2505.24329)。
5. WebSearch "TRACE causal event modeling ..." → TRACE (2410.05643, ICLR 2025)（仅作提及，未入表）。
6. WebSearch "video LLM temporal grounding select from candidate segment proposals instead of generating timestamps ..." → MeCo (2503.09027)、HawkEye、BAM-DETR (2312.00083)、TimeRefine (2412.09601)、StepVTG、Foresee-to-Ground (2605.21973)。
7. WebSearch "Moment-DETR QVHighlights ..." → 2107.09609；ar5iv 读 sections。
8. WebSearch "Kinetics-GEBD ... Rel.Dis" → GEBD (2101.10511)；协议细节来自派生论文的搜索摘要，标 [V]。
9. WebSearch "VidChapters-7M ... tolerance" → 2309.13952、Chapter-Llama 2504.00072；指标细节标 [V]。
10. WebSearch "video highlight clip start end boundary alignment sentence boundaries speech cut points evaluation human perceived boundary quality" → 仅得到工程/专利类线索（snap to word edge、VAD/silence cut cost）；**未找到**评估"clip 起止点人类感知质量"的学术工作。专利/博客不作证据。
11. arXiv API 查 TimeLens 前向引用：search_query=all:TimeLens / "TimeLens-Bench" / "TimeLens-100K" / abs:TimeLens → 命中 Kwai Keye-VL-2.0 (2606.10651)、CAPD (2609.34581)。
12. 其余 abs 页（WebFetch）：2312.00083、2503.09027、2604.27591、2109.08039、2101.10511、2309.13952、2512.16906（误命中：是 VIVA 而非 VlogReward）。
13. arXiv API id_list 批量取摘要：2607.23951、2607.17423、2606.05758、2606.06294、2609.39883、2607.25300 命中；之后同类请求多次返回空（疑限流），改用 WebFetch。

## 三、簇 6（评测方法学）query
1. WebSearch 'Otani "Rethinking the Evaluation of Video Summaries" cited alternative evaluation ...' → 只返回 Otani 本文；改用 OpenAlex 前向引用。
2. OpenAlex：filter=doi:10.48550/arxiv.1903.11328 → W2967219836，被引 169；filter=cites:W2967219836 取标题，按关键词筛 → Margin MCC (ACM MM 2023)、GF-measure (TETCI 2024)、VISIOCITY (2007.14560 / 2101.10514)、Multiple Pairwise Ranking Networks (ICCV 2021)、Multi-Annotation Attention (CVPRW 2023)、A Framework for Evaluating Video Summary Approaches (2022) 等。
3. WebSearch 'Margin MCC ...' / '"Multi-Reference Evaluation ... Granule-Aware F-Measure"' → 搜索引擎未索引；改 OpenAlex 取摘要（abstract_inverted_index）。**这两篇均无 arXiv 版本（未找到）**。
4. OpenAlex referenced_works of W2967219836 → 后向：SumMe(Gygli 2014)、TVSum(Song 2015)、Zhang 2016 LSTM、DR-DSN、Kendall/DPP 等；另见 VideoSET (2014, 文本化摘要评测)。
5. Semantic Scholar /citations?fields=title,year,externalIds：第一次 429，间隔 5 秒后重试成功；共 ≥60 条 TimeLens 引用（见 rq_notes 前向列表）。OpenAlex 对 TimeLens 的 cited_by_count=0（索引滞后）。
6. WebSearch "LLM-as-a-judge evaluating video highlight or video summarization clip selection agreement ..." → VideoJudge (2509.21451)、QEVA (2604.24052)、positional bias in multi-video summarization (2606.04596) 等；**未找到**专门验证"高光/选段 MLLM judge vs 人类"的论文。
7. arXiv/ar5iv/WebFetch 读 sections：Stiennon 2009.01325、MT-Bench 2306.05685、Chatbot Arena 2403.04132；abs-only：G-Eval 2303.16634、SummEval 2007.12626、VideoScore 2406.15252、VideoReward 2501.13918、Wang 2305.17926、Shi 2406.07791、AutoCalibrate 2309.13308、PPI 2301.09633。
8. Timeline-Bench 的 "editor-calibrated judge"：全文 Sec 3.3 与 App D 直读（见 notes/B22.md）。

## 四、明确"未找到"清单
- 对"连续时间戳回归 vs 在候选切点（句末/说话人轮次/镜头切/停顿）上选择"做同骨干、同数据消融的论文：未找到（上述 query 2/3/6 + survey 全文检索）。
- 报告 IoU@0.9 或"边界误差秒数"的 MLLM 时刻检索论文：未找到（仅 VidChapters 经搜索摘要提及 0.9，标 [V]；GEBD 用绝对距离 0.2–1 s）。
- 评估 clip 起止点"人类感知质量"的学术协议：未找到。
- Margin MCC / GF-measure 的 arXiv 版本：未找到（仅 DOI）。
- 对 Otani 2019 提出"替代评测"的后续工作，在 OpenAlex 169 篇引用中仅筛出：VISIOCITY、Margin MCC、GF-measure、Multiple Pairwise Ranking、MEDit-Bench（经 Semantic Scholar/搜索发现，非 OpenAlex 篇目）。
