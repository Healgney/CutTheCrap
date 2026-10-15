# 合并检索日志（四个检索 agent 的原始日志，按簇分段）

> 工具：WebSearch / WebFetch / arXiv API / OpenAlex / GitHub API；Semantic Scholar 匿名 API 多数请求 429。Undermind / Elicit / Asta 需登录，未使用。

---
## Agent A
# Agent A search log (clusters 1 and 2) -- date 2026-10-15

Tools used: WebSearch (standard/extended), WebFetch, curl via Bash (arXiv abs/HTML/ar5iv, OpenAlex API, Crossref API, GitHub API/raw, Hugging Face API, CVF open access), pdftotext on PDFs.
Not used: Undermind / Elicit / Asta (login required, per brief). Google Scholar not available.
Tool limits hit: Semantic Scholar Graph API returned HTTP 429 on 5 attempts (spaced 4-20 s) -> snowball via OpenAlex and reference-list parsing instead. arXiv export API returned results at first, then HTTP 429 -> switched to arxiv.org/abs meta tags. WebFetch could not parse PDFs (returns compressed streams); where a PDF was unavoidable I ran pdftotext on the copy WebFetch had already saved in tool-results (Mr.HiSum, Video2GIF, LIGHTOR) and, for TVHighlights (CVF 403 for WebFetch, no HTML version), curled the PDF to the scratchpad, extracted text and deleted the PDF. These are the only PDF copies; nothing stored in the repo.
Seeds taken as given (not re-verified): Repurpose-10K, HIVE, Mr.HiSum, SVHighlights, TVHighlights, Vidi, Vidi2.5.

## Queries and outcomes (WebSearch unless noted)
1. "long video to short clips automatic highlight extraction podcast interview LLM transcript self-contained clips arXiv" -> RankCut (IUI'26), commercial tools (Sieve, PlayPlay, OpenClip/AutoShorts GitHub). No new arXiv paper. Product blogs kept only as [V] leads.
2. "\"Repurpose-10K\" video long-to-short benchmark" -> only the paper itself, AAAI page, GitHub, aggregator reviews (not used as evidence).
3. "livestream highlight detection chat messages Twitch dataset highlight clips" -> LIGHTOR (1910.12201), York PhD thesis (Ringer 2022), Stanford CS231n HiLAiT (student project, not used), Ping&Chen pointer.
4. "Shah IUI 2026 transcript-based rough cut ..." -> RankCut metadata (Hamburg page fetched, F for abstract).
5. "KLive dataset live streaming highlight detection" -> KLive paper (2407.12002), ContentCTR (2306.14392), KuaiLive-M3 (2607.24862), patents (ignored).
6. "time-sync comments danmaku video highlight extraction dataset deep learning" -> Ping&Chen 1708.02210 (+GitHub), Lv et al. AAAI'16 (DOI verified via Crossref), SmartBullets (ignored), DanmakuTPPBench (2505.18411; not highlight task -> not included).
7. Twitch user clips query ("Twitch clips user-created clips dataset highlight detection ...") -> no Twitch-clip-supervised dataset found; PHD-GIFs/ECCV'20 Rochan (2007.09598), Ringer 2018 unsupervised (1807.09715, not included), KAIST thesis (not opened).
8. "YouTube Most Replayed heatmap video highlight detection paper arXiv" -> Mr.HiSum only; no other peer-reviewed Most-Replayed dataset found. Patent "Determining video highlights and chaptering" (ignored).
9. Video2GIF query -> arXiv 1605.04850 (PDF parsed locally via tool-results copy).
10. extended: "benchmark for automatically generating short-form clips from long videos podcasts interviews ..." -> Pennec et al. 2512.11399 (movie clip selection, IWSDS'26), CineBench 2604.10456, CLIP-CC-Bench (irrelevant), Chapter-Llama (cluster 3/4 lead). No podcast clip benchmark.
11. "LLM transcript highlight selection long video standalone OR self-contained ... hook title" -> RankCut, Pexo/Jupitrr/MuAPI/AutoShorts product pages (vendor claims about hook/payoff/complete-thought criteria; [V] only, not rows).
12. "AntPivot ... AntHighlight" -> 2206.04888 (+repo, OpenI data page).
13. "Fu 2017 Video highlight prediction using audience chat reactions" -> D17-1102 / 1707.08559.
14. "multimodal LLM agent highlight clip generation from hour-long livestream VOD ... dataset clips published by creators" -> Vidi2.5, HIVE, pharmacy clips paper (2601.05059), ContentCTR, KLive, Videogenic (2211.12493, not read), Less is More (1903.00859). No creator-published-clips dataset beyond Repurpose-10K.
15. OpusClip virality-score query -> help.opus.pro page fetched (vendor statement: Hook, Flow, Value, Trend; score 0-99; Pro/Starter). Third-party reviews ignored.
16. "CapCut long video to shorts ... Vidi" -> no primary source tying CapCut to Vidi; Vidi repo README documents a Highlight demo mode. TikTok Smart Split/Vidi claim is press-only (not used).
17. Danmaku highlight 2024-2025 queries (2) -> nothing newer than Ping&Chen 2017 for danmaku highlight; DanmakuTPPBench is a TPP benchmark.
18. Sun et al. ECCV'14 and Badamdorj ICCV'21 title queries -> confirmed metadata; ECCV'14 data/code repo aliensunmin/DomainSpecificHighlight listed by search result [V].
19. PodReels query -> arXiv 2311.05867 (read), Adobe Research news (marketing, not used).
20. "MultiSeg dataset temporal segmentation long livestream" -> LiveSeg / MultiLive (WACV 2023); the "MultiSeg 1,000 videos 78 min" row in Repurpose-10K Table 1 does not match MultiLive (11,285 videos, 1.3 h) [V].
21. extended: "highlight short-form clips benchmark talk show interview lecture 2026 ..." -> no new paper; confirms gap.

arXiv API queries (export.arxiv.org, before 429): abs:"Repurpose-10K"; abs:"video repurposing"; abs:"long-to-short" AND abs:video; abs:"long-form" AND abs:"short-form" AND abs:video AND abs:clip (-> Lotus, SVHighlights); abs:podcast AND abs:"short clips" (-> VoiceGiraffe 2605.27976, not relevant); abs:"short video" AND abs:"long video" AND abs:highlight AND abs:LLM (survey 2409.18938, not relevant); ti:TVHighlights / abs:TVHighlights (0 hits: TVHighlights has no arXiv version I could find).
OpenAlex: search queries "long-to-short video repurposing clips", "automatic video editing long video to short highlight clips LLM", "short-form clip extraction from long-form video podcast interview", "viral clip selection transcript large language model" (from 2024-06) -> Lotus, HIVE, PodReels, pharmacy paper, LLM popularity predictors (ACL Findings 2025, lead for cluster 8), "Social Media Content Generation: AI-Based System for Automated Viral Short-Form Video Creation" (ICITEICS 2025; low-quality system paper, not included).

## Snowball
- Repurpose-10K backward (parsed the reference list of arXiv HTML v2): PodReels (A10), Sun 2014 (A20), QVHighlights (A19), Truong 2021 (CHI makeup tutorials, irrelevant), UnAV/AVE-type TEL datasets (irrelevant), MultiSeg row (see above). Forward: OpenAlex `cites:` -> 2 works (Number it, CVPR 2025; HarmonySet, CVPR 2025) -- not relevant; Semantic Scholar blocked (429). OpenAlex coverage of arXiv-only citers is poor, so the forward list is likely incomplete [V].
- HIVE backward (reference list read): FunClip (github.com/modelscope/FunClip) and AI-Youtube-Shorts-Generator (github.com/SamurAIGPT/AI-Youtube-Shorts-Generator) named as prior ASR+LLM clip tools (open-source repos, no papers -> recorded as [V] leads, not rows); Lotus (A11), Hu et al. 2023 / Argaw et al. 2022 (AVE editing dataset, movies; not included), Pardo et al. 2021. Forward: OpenAlex `cites:` = 0 works; no other citers found.
- Vidi family: forward not pursued beyond README; Vidi2.5 text cites Vidi (1) and benchmark papers only.
- Extra forward/backward from newly found items: PodReels -> Adobe Clip Maker (marketing); KLive -> AntPivot, PHD-GIFs; SVHighlights -> Mr.HiSum, TimeChat/TRACE/VTG-LLM (cluster 3).

## Explicit "not found" statements
- Industrial systems (OpusClip, CapCut/TikTok Smart Split, Vizard, Descript, Clips.ai, Adobe Clip Maker, Eklipse, Sieve): no peer-reviewed paper found for any of them (queries 1, 11, 14, 15, 16). Only vendor docs/blogs; OpusClip's help page is the single first-party description of its scoring; kept as row A25 with F restricted to what the vendor states.
- Twitch "Clips" (viewer-created clips) as a supervised highlight dataset: not found (query 7; KAIST thesis title only seen in search snippet).
- Open dataset of official podcast/interview full episodes <-> official shorts: not found (queries 1, 10, 14, 21).
- YouTube Most Replayed beyond Mr.HiSum: not found (query 8).
- Bilibili danmaku highlight datasets after 2017: not found (query 17).
- Venue for AntPivot, Vidi, KLive (ICME 2024?), LIGHTOR: not confirmed -> [V] in rows.
- A modality ablation for TVHighlights, Mr.HiSum, Video2GIF: none exists in the sections read.

---
## Agent B
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

---
## Agent C
# Search log -- Agent C (clusters 4 and 5; RQ1 primary, RQ5 secondary)
Date: 2026-10-15. Tools: WebSearch (general web), WebFetch (arxiv.org/abs, arxiv.org/html, ar5iv.labs.arxiv.org, aclanthology.org, trec/nist pages), arXiv API (export.arxiv.org), OpenAlex API (api.openalex.org: search, cites: filter). Not used: Undermind / Elicit / Asta (need login); Semantic Scholar API (not needed). No PDFs downloaded; PDF-only pages (TREC 2021 overview PDF, Maskey and Hirschberg 2005, TruNet PDF) could not be parsed by WebFetch, so were read via ar5iv or left abstract-only.
Tool problems: arXiv API returned HTTP 429 after ~35 queries (from about the "Dense X Retrieval" query onward); switched to OpenAlex + WebSearch. WebFetch returns small-model summaries, so numbers marked [F] come from those summaries of the primary page text and should be spot-checked before final citation.

## A. Podcast / spoken-content NLP (cluster 4)
| # | query | tool | outcome |
|---|---|---|---|
| 1 | TREC Podcasts Track overview summarization segment retrieval | WebSearch | found TREC 2020 overview (2103.15953) -> C01 |
| 2 | podcast summarization TREC / podcast segment retrieval | arXiv API | Spotify TREC-2020 (2104.03343), CUED (2012.02535), baseline analysis (2008.10648), PodSumm (2009.10315), 2011.04132, 2011.08291 -- only CUED noted in C01 notes; others not included (summarization-only, not relevant to clips) |
| 3 | TREC 2021 Podcasts Track overview (x3 variants, incl. reranking/audio/entertaining) | arXiv API, WebSearch, WebFetch (pages.nist.gov, trec.nist.gov/data/podcast2021.html, trecpodcasts.github.io) | 2021 overview PDF exists (trec.nist.gov/pubs/trec30/papers/Overview-Pod.pdf) but unreadable by tool; task page read -> C02 (partly [V]). podcastsdataset.byspotify.com DNS failed. TU Wien 2021 participant paper (TU_Vienna-DL-Pod.pdf) located, not read |
| 4 | podcast trailer preview generation | arXiv API | 2505.23908 -> C03 |
| 5 | podcast highlights detection | arXiv API | Rhapsody 2505.19429 -> C04; 2103.02585 (extraneous content/ads in podcasts, EACL 2021, abstract only, not included) |
| 6 | podcast episode segments chapter generation | arXiv API | PODTILE 2410.16148 -> C05; 2110.07096 (intro identification), 2307.13394 (TextTiling+summarisation) not included |
| 7 | podcast audio features entertaining segment reranking; interesting moments podcast audio engagement | arXiv API | nothing relevant |
| 8 | topic segmentation spoken transcripts; lecture video segmentation transcripts topic; dialogue topic segmentation | arXiv API | YTSeg 2402.17633 (via WebSearch) -> C06; TreeSeg 2407.12028, 2609.34425 (Cue-Grounded, Sep 2026), 2512.17083 (granularity-aware eval), 2012.07589 read abstracts only, not included |
| 9 | multimodal topic segmentation podcast | OpenAlex | Ghinassi et al. ICMR 2023 -> C07 (abstract-only via WebSearch snippet) |
| 10 | podcast summarization segment audio features | OpenAlex | Vaiani et al. SAC 2022 -> C08 (abstract-only); "100,000 Podcasts" COLING 2020 (DOI 10.18653/v1/2020.coling-main.519) noted, not read |
| 11 | Maskey Hirschberg speech summarization features | WebSearch, WebFetch(PDF failed) | C09 abstract-only |
| 12 | speech summarization prosodic features ablation extractive | OpenAlex | Murray, Renals, Carletta Interspeech 2005 (DOI 10.21437/interspeech.2005-59, meeting extractive summarization with prosody, abstract via WebSearch only) -- not in rows; voicemail summarization 2005 (Koumpis/Renals) not read |
| 13 | quotable quote detection; memorable quote extraction; quotability sentence spoken content prediction; pull quote detection | arXiv API, OpenAlex | Pull quotes (Bohn and Ling, COLING 2020) -> C13; RA-MTR (2502.12124, inspirational quote extraction from long text, abstract only, not included); Danescu-Niculescu-Mizil "You had me at hello" (arXiv 1203.6360, memorability of movie quotes; cited 105; not read, not included). **No dataset or model for quotable/clip-worthy sentence detection in SPOKEN content found.** |
| 14 | laughter detection audio / speech / segmentation; humor detection multimodal laughter; audience laughter punchline detection stand-up; ur-funny | arXiv API, OpenAlex | UR-FUNNY -> C10; Alnajjar 2211.01889 -> C11; FunnyNet-W -> C12; seen but not included: SMILE 2312.09818 (Findings NAACL 2024, laugh reasoning), StandUp4AI 2505.18903 (330+ h, 7 languages, laughter-labeled), TIC-TALK 2603.21803, MTLLFM 2605.25409 (CVPR 2026 workshop), PunchBench 2412.11906, Video2Reaction 2607.06875, MultiLinguahah 2605.06309, Gillick et al. Interspeech 2021 laughter detector (abstract via WebSearch) |
| 15 | applause laughter TED talks audience reaction prediction | OpenAlex | "Audience Response Prediction from Textual Context" 2206.10967 (abstract only), "Please Clap" NAACL 2018, Rhetorical devices for applause ICWSM 2017: not read, not included |
| 16 | lecture highlight detection speech prosody | OpenAlex, WebSearch | "Lecture Video Highlights Detection from Speech" EUSIPCO 2024 (104 speakers, VGG+transformer 78.2% acc / 78.8% UAR; abstract via WebSearch) -- not included |
| 17 | turn-taking prediction voice activity projection; end of turn detection pause prosody; prosodic boundary detection | OpenAlex, arXiv API | VAP (Ekstedt and Skantze, Interspeech 2022, DOI 10.21437/interspeech.2022-10955), wav2vec2 prosodic boundary detection 2209.15032; **no paper found that uses pause/turn cues to choose clip start/end of a highlight** (not read in depth; RQ3 is other agents' remit) |
| 18 | emphasis detection speech prosody summarization / acoustic prosodic features extractive speech summarization | arXiv API | nothing relevant (arXiv weak for pre-2010 speech work) |

## B. Self-containedness / coherence / coreference (cluster 5, RQ1)
| # | query | tool | outcome |
|---|---|---|---|
| 19 | self-contained extractive summary sentence selection dangling anaphora context-independent sentences | WebSearch | Durrett et al. 2016 (1603.08887) -> C21; older rule-based anaphora-in-summarization work (Paice 1990, Steinberger) mentioned by sources but not retrieved; "Can Anaphora Resolution Improve Extractive Query-Focused MDS" (IEEE Access 2023) seen, not read |
| 20 | Decontextualization making sentences stand-alone; ...LLM; propositions retrieval granularity | arXiv API, OpenAlex | Choi et al. 2102.05169 -> C14; Kane and Schubert 2310.06254 (few-shot LLM decontextualization, abstract only), Molecular Facts 2406.20079 (EMNLP Findings 2024: decontextuality vs minimality, abstract only), DnDScore 2412.13175, Dense X Retrieval 2312.06648 (propositions "self-contained"; abstract only) -- not rows |
| 21 | cites: Decontextualization (OpenAlex W3128754101, 54 citing works) | OpenAlex | QaDecontext 2305.14772 -> C16; PropSegmEnt, Text-based NP Enrichment, RARR etc. are text-QA/fact-check uses; "Audio-Based Tools for Decontextualisation Detection" (2026) is about misinformation, different sense -- not relevant |
| 22 | standalone excerpt comprehensibility out of context | arXiv API | 2412.19966 -> C15; 1803.08983 "Automated Evaluation of Out-of-Context Errors" (Huber, Niehues, Waibel LREC 2018: inserted ASR/MT errors in TEDTalk, abstract read; about error detection, not excerpt self-containedness; not included) |
| 23 | dangling anaphora extractive summarization coreference | arXiv API | 2608.04569 -> C20; extractive-faithfulness query via WebSearch -> 2209.03549 -> C17 |
| 24 | summary coherence evaluation metric discourse; BooookScore coherence; SNaC | arXiv API, OpenAlex, WebSearch | BooookScore -> C19; SNaC -> C18; DiscoScore 2201.11176, summary coherence measures toolbox 2209.06517, PDD 2402.10175, "Learning to extract coherent summary via RL" 1804.07036 seen, abstracts not read |
| 25 | coreference: Maverick, LingMess, CorPipe, spoken/dialogue coreference CODI-CRAC | OpenAlex, WebSearch, WebFetch | Maverick -> C22; Xu and Choi 2109.00185 -> C23; LingMess (2205.12644, EACL 2023, abstract only), CorPipe (2209.07278, 2311.14391), CorefDS 2106.08556 (SIGDIAL 2021, abstract only) noted not rows |
| 26 | coherence extractive summary pronoun antecedent missing neural | arXiv API | nothing beyond above |

## C. Video / clip side (to answer RQ1 (a))
| # | query | tool | outcome |
|---|---|---|---|
| 27 | self-contained clip context independent understandable (video) ; standalone short clips from long videos LLM transcript; short-form clip extraction from long podcast LLM; viral clip selection transcript hook; video excerpt out-of-context understanding | arXiv API | TruNet 1910.05899 -> C25; otherwise irrelevant (CLIP, video generation) |
| 28 | "self-contained" clips long-form video podcast highlight selection LLM "without context" evaluation | WebSearch (extended) | 2505.23908 (C03); PodReels (C24); Lotus 2502.07096 (Barua et al., IUI 2025, abstract only; cited by C03 for the "self-contained, easy to understand without context" principle -- belongs to cluster 1); CLIP-CC-Bench 2608.04302 (selects ~90 s clips required to be understandable without outside context, as a selection rule only; snippet only [V]); 2512.11399 (key-moment extraction for MovieSum; no standalone notion) |
| 29 | video moment standalone / self-contained / context-independent clip comprehensibility metric | WebSearch | Only vendor help pages (Munch "coherence score", Pexo, OpenClip, Videotto, ClipSpeed): scores like "narrative completeness", "topic completeness", "stand on their own" with no published formula or validation -- not evidence |
| 30 | arXiv "self-containedness" score segment transcript LLM judge clip viral | WebSearch (extended) | LemmaBench 2602.24173: LLM judge of "self-containedness" of math lemmas, 75.5-96.5% of lemmas it vetted were judged self-contained by human mathematicians (from search snippet [V]); not video |
| 31 | hook-aware highlight clip extraction podcast interview transcript LLM engagement context dangling/standalone shorts | WebSearch (extended) | same trio (C03, C24, C04); 2505.23268 "Unsupervised Transcript-assisted Video Summarization and Highlight Detection" (Mr.HiSum eval; multimodal vs visual-only: Spearman 0.0636 vs 0.0348, MAP50 59.26 vs 55.97/57.38; not about standalone-ness; cluster 2) |
| 32 | OpenAlex cites: Spotify preview paper (W4412886861), Rhapsody (W4414763360), Bridging Context Gaps (W4405955376), TREC 2020 overview (W3147642179) | OpenAlex | Preview paper: 2 citing works (podcast semantic search; ACL industry front matter); Rhapsody and Bridging: 0 in OpenAlex (too recent or not indexed); TREC 2020: 8 (MQAG, grounded podcast summarization ACL 2022, noise-robust spoken retrieval, ...) -- nothing on clip selection |

## Explicit "not found" statements
- **Definition + measurement of self-containedness of a video/audio clip**: not found with queries 27-31 (arXiv API, WebSearch extended x3, OpenAlex). The nearest are C03 (implicit via prompt + human Yes/No) and C24 (design principle only).
- **Quotable / clip-worthy sentence detection on spoken content**: not found (query 13).
- **Laughter / applause as a feature in highlight or summarization of podcasts with an ablation**: not found; humor detection ablations exist only on sitcom/TED (C10-C12), and Rhapsody (C04) uses generic HuBERT/DVA not laughter.
- **Pause/prosody cues used for clip-boundary choice**: not found beyond topic-segmentation abstract claim (C07) and VAP turn-taking (not read).
- **TREC Podcasts 2021 participant-level audio gains**: not retrieved ([V]).

# Addendum (deep-read phase, 2026-10-15): final RQ1 "not found" confirmation and tool notes
Tools in this phase: Bash curl (own text dumps of arxiv.org/html, ar5iv, GitHub raw/API, TREC PDF via pdftotext in the scratchpad; nothing saved in the project), arXiv API (restored after earlier HTTP 429; slow), OpenAlex (title lookups worked; free-text multi-word searches returned empty in this phase, probably a throttle), WebSearch (one query worked; WebFetch hit a session limit mid-phase, so later reading was done by own curl text dumps). Two papers (C07, C08) sit behind Cloudflare bot challenges (dl.acm.org, qmro.qmul.ac.uk, iris.polito.it): not bypassed; kept abstract-only.

| # | query | tool | outcome |
|---|---|---|---|
| 33 | "self-contained clip" ; standalone excerpt podcast ; context-independent segment spoken ; dangling reference spoken transcript clip ; teaser self-contained podcast ; quotable podcast clip ; clip understandability without context ; self-contained segment video highlight ; short video clip standalone comprehensible long video transcript ; context sufficiency video moment | arXiv API (all: field, 6 results each) | Nothing new. Hits were PodReels (2311.05867), TruNet (1910.05899), podcast summarization baselines, the 2026 referential-dangling preprint (2608.04569), and irrelevant CLIP/5G papers. arXiv all: search matches single words loosely, so absence here is weak evidence |
| 34 | self-contained clip podcast ; standalone clips from long-form video selection ; clip selection context-independent understandable ; short-form repurposing self-contained coherence ; podcast clip recommendation highlight standalone ; video highlight completeness semantic integrity clip boundary ; teaser trailer self-contained spoiler context podcast ; excerpt out-of-context comprehension spoken conversation ; quotable moment detection speech ; viral clip detection podcast transcript | OpenAlex works?search | returned no rows in this phase (throttle or query parsing); not counted as evidence of absence. Earlier OpenAlex queries (log #13, #20-26, #32) did work |
| 35 | "self-contained" clip podcast video repurposing short-form "understood without" context LLM selection evaluation 2025 2026 | WebSearch (standard) | Only Repurpose-10K (seed, AAAI 2025) as academic hit plus vendor blogs. Practitioner claims (clip tools pick well only ~30-60% of the time; models find self-contained moments but not performers) are untraced opinion, not evidence |
| 36 | Seed check by grep of own text dumps for self-contain / standalone / context-independent / dangling / complete / coheren | Bash grep on arxiv.org/html of Repurpose-10K (2412.08879), HIVE (2507.02790), Vidi (2504.15681), Vidi2.5 (2511.19529) | Repurpose-10K: clips described as "each clip encapsulating a self-contained sub-topic"; human study (Table 2) rates "engagement level" and "completeness level" 1-5 by 10 participants on 462 clips per group (random: E 1.623, C 1.508; professional editors: E 3.938, C 3.738; Repurpose-10K annotations: E 3.868, C 3.418; avg lengths 59.55 / 53.27 / 58.66 s); no definition of completeness or agreement seen in the text hits. HIVE: coherence of the edited video via a "smoothness" metric and scene-level segmentation "semantic completeness" (line-level grep only). Vidi/Vidi2.5: no standalone notion in hits (only coherent editing plans). These seeds belong to cluster 1; I only grepped them |

## Final status of RQ1 "not found"
No paper found (queries 27-36) that (i) defines self-containedness of a video or audio clip, (ii) decomposes it into dangling reference / missing setup / unanswered question / joke without setup, and (iii) validates an automatic score against human judgements on spoken clips. Nearest partial precedents: Spotify previews (C03; binary human item), Repurpose-10K (seed; 1-5 "completeness" rating, undefined), PodReels (design principle), TruNet (IoU-based integral story), text-side C14/C15/C16/C17/C18/C19/C20.

---
## Agent D
# Agent D search log (clusters 7 and 8)

Date of run: 2026-10-15. Tools: Bash+curl to arXiv API (export.arxiv.org, relevance sort; rate-limited with HTTP 429 after ~35 calls, then switched), OpenAlex API (api.openalex.org/works?search=..., note: `search=` is full-text-ish and noisy), WebSearch (US-only), WebFetch on arxiv.org/abs, arxiv.org/html, proceedings.neurips.cc, aclanthology.org, frontiersin.org, github.com, research.google. Semantic Scholar was NOT used. Undermind / Elicit / Asta not used (login required).

PDF note: WebFetch could not parse PDFs; the harness auto-saved the binary into its tool-results cache, and I ran `pdftotext` on those cached copies (Mr.HiSum, Joachims 2017, Agarwal 2019, Ai 2018, Wang 2018, Zhan 2022, Wang 2021 clickbait, Hager 2024). No PDF was deliberately downloaded into the project. Text copies live only in the scratchpad.

## A. Queries on "explicit debiasing of Most Replayed / danmaku / view-count labels in highlight or clip selection" (RQ2 novelty core)
| # | Query | Tool | Result |
|---|---|---|---|
| 1 | all:"Most Replayed" | arXiv API | 5 hits: Duico 2023 (2309.06102), TripleSumm (2603.01169), HierSum (2504.18689), Rhapsody (2505.19429), Sahu 2026 (2607.01400). Kept all but HierSum (HierSum text has no bias discussion beyond ">50k views more accurate") |
| 2 | all:"replay" AND all:"highlight" AND all:bias AND all:video | arXiv API | 0 hits |
| 3 | all:"unbiased" AND all:"video highlight" | arXiv API | 0 hits |
| 4 | all:"position bias" AND all:"video highlight" | arXiv API | 0 hits |
| 5 | all:"popularity bias" AND all:"video highlight" | arXiv API | 0 hits |
| 6 | all:"debias" AND all:"video moment" AND all:highlight | arXiv API | 0 hits |
| 7 | all:"audience retention" AND all:video AND all:highlight | arXiv API | 0 hits |
| 8 | all:"viewer engagement" AND all:"video summarization" AND all:bias | arXiv API | 0 hits |
| 9 | all:"weak supervision" AND all:"highlight detection" AND all:"view counts" | arXiv API | 0 hits |
| 10 | all:"noisy" AND all:"user behavior" AND all:"highlight detection" AND all:label | arXiv API | 0 hits |
| 11 | all:"replay" AND all:heatmap AND all:YouTube | arXiv API | 1 hit: Sahu 2026 |
| 12 | all:"Mr.HiSum" / all:"Mr. HiSum" | arXiv API | HierSum, TRINITY (2608.29577), TSMD (2609.39051), Aha. TRINITY page checked: no bias discussion of Mr.HiSum labels (frames saliency as perspective-dependent; benchmark for personal-style) |
| 13 | all:danmaku AND all:highlight; all:"time-sync comments" AND all:highlight | arXiv API | Ping and Chen 2017 (1708.02210) only |
| 14 | "video highlight detection most replayed label bias debiasing position bias popularity channel thumbnail confound" | WebSearch extended | Surfaced the TripleSumm (App B.2) and Aha statements; no paper doing propensity/IPS/causal debiasing of replay labels. Search summary claimed several things not in sources (e.g. generic recsys results); I only used items I then verified by fetching |
| 15 | danmaku OR "time-sync comments" video highlight detection bias comment density position bias debiasing | WebSearch standard | Only Ping and Chen 2017; lag calibration is the only correction found |
| 16 | "Most Replayed" spike first seconds bias | WebSearch standard | No new source (the spike statement was located by fetching TripleSumm and Rhapsody) |
| 17 | debiasing replay statistics video highlight; time-sync comments highlight extraction video; danmaku video highlight detection; bullet comments video highlight bias; highlight detection implicit user feedback bias noisy labels video; video highlight dataset selection bias creator-selected clips; causal video highlight detection debiasing; replay graph podcast highlight YouTube; Mr. HiSum most replayed label noise; highlight detection most replayed supervision limitation proxy engagement | OpenAlex | Found older time-sync comment highlight papers (Video Highlight Shot Extraction with Time-Sync Comment 2015 DOI 10.1145/2757513.2757516; Reading the Videos AAAI 2016; Bridging Video Content and Comments AAAI 2017) - titles only, not opened, lead for danmaku density (cluster 2 owner); CHI 2025 Most Replayed paper (title/DOI confirmed). Nothing on debiasing |
| 18 | Direct read of seeds for bias handling: HIVE (2507.02790), SVHighlights (2606.06926), Repurpose-10K (2412.08879) | WebFetch (HTML) | None of the three analyses or corrects label bias. HIVE labels = viewer study + expert edits; SVHighlights labels = official highlight videos (view filter >10k only); Repurpose-10K: LLM repurposing tools propose candidate clips and users pick/refine, but selection effect is not analysed |
| 19 | Generating Highlight Videos of a User-Specified Length using Most Replayed Data (CHI 2025) | WebSearch, WebFetch | ACM page returned 403; only third-party abstract snippet. Bias handling NOT verified [V] |

## B. Queries for click models / counterfactual LTR / popularity bias (cluster 7)
| # | Query | Tool | Result |
|---|---|---|---|
| 20 | all:"counterfactual learning to rank" AND all:"position bias" AND all:propensity | arXiv API | 8 hits (e.g. 2005.10615, 2108.08538 mixture-based correction for position and trust bias, 2008.10242 affine corrections) - listed as leads, not read |
| 21 | all:"duration bias" AND all:"watch time" | arXiv API | D2Q 2206.06003 (read), 2406.07932 counterfactual watch time, 2208.05190 DVR, 2308.08120, 2504.07575, 2503.06920 AlignPxtr (leads, not read) |
| 22 | all:clickbait AND all:counterfactual AND all:recommendation | arXiv API | 2009.09945 (read) |
| 23 | unbiased learning to rank position bias | OpenAlex | Wang 2018 WSDM (DOI 10.1145/3159652.3159732), Joachims 2017, Unbiased LambdaMART (1809.05818, lead, not included), Doubly Robust ULTR (TOIS 2022, lead) |
| 24 | Direct abs fetch: 1812.05161, 1804.05938, 2404.02543, 2207.03051, 2105.06067, 2010.03240, 1602.05352, 2009.09945 | WebFetch | verified titles/authors/dates |
| 25 | video summarization view count popularity bias; popularity bias micro-video highlight | OpenAlex | popularity-bias surveys (UMUAI 2024 DOI 10.1007/s11257-024-09406-0, lead), Alleviating Video-length Effect for Micro-video Recommendation (TOIS 2023, lead) |
| 26 | uncovering hidden challenges in query-based video moment retrieval; temporal grounding dataset bias moment prior debiasing | OpenAlex | Otani et al. BMVC 2020 (DOI 10.5244/c.34.84) and "Towards Debiasing Temporal Sentence Grounding in Video" (2111.04321), "Deconfounded Video Moment Retrieval with Causal Intervention" (SIGIR 2021, DOI 10.1145/3404835.3462823): relevant for position-prior bias in annotation but NOT opened -> leads [V] for the cluster 3/6 owners |
| 27 | click model video watch behavior skip replay implicit feedback | OpenAlex | SWaT (WSDM-adjacent, DOI 10.1145/3690624.3709415) and "Relative Advantage Debiasing for Watch-Time Prediction" (AAAI 2026) - leads, not opened |
| NOT DONE | Classic click-model papers (Craswell 2008 cascade, Chapelle and Zhang 2009 DBN, Dupret and Piwowarski UBM, Chuklin et al. book) | - | No arXiv versions; not retrieved. Their ideas are cited inside Ai 2018 / Wang 2018 / Joachims 2017 (which I read) |

## C. Queries for cluster 8 (short-video engagement / popularity)
| # | Query | Tool | Result |
|---|---|---|---|
| 28 | all:VQualA; all:SnapUGC; all:"VQualA" AND engagement; all:"short video" AND all:"engagement prediction" | arXiv API | 2509.02969 (challenge report), 2508.02516 (winner), 2410.00289 (SnapUGC); other VQualA 2025 hits are face-IQA/SR-IQA/LMM-comparison tracks (irrelevant) |
| 29 | all:"engagement" AND all:Snapchat AND all:video | arXiv API | SnapUGC; 2607.28895 LLM-Based Generative Retrieval for Snapchat (recsys, not relevant) |
| 30 | all:"video popularity prediction" AND all:multimodal | arXiv API | 2003.12724 (2020 micro-video MVED, lead), 2507.00950 MVP (read) |
| 31 | "short video engagement prediction content"; "video popularity prediction thumbnail title confound causal"; "YouTube video views thumbnail title effect causal experiment"; "causal inference popularity prediction social media content creator confounding" | OpenAlex | Found Douyin hooks null-result paper (read), LLM popularity (ACL Findings, abstract), IMCL-DAMO not on arXiv; MMF-QE (ICCVW DOI 10.1109/iccvw69036.2025.00366) exists but no accessible text -> not included; SmartEdit (ICME 2025) lead; "Catchy or Sketchy? thumbnail-title congruence" (SSRN 2026) lead, social-science, not opened |
| 32 | MMF-QE ...; IMCL-DAMO ... | WebSearch | Not found as arXiv; only DOI-level confirmation of MMF-QE. IMCL-DAMO method taken from the challenge report's table only |
| 33 | all:"Twitch" AND all:clips; livestream highlight chat viewer clip creation bias; Twitch clips popularity prediction | arXiv API, OpenAlex | 1910.12201 (Implicit crowdsourcing highlights from recorded live videos, ICDE 2020 DOI 10.1109/ICDE48307.2020.00176: cluster 2 lead) and 2026 LLM Twitch clip summarisation (DOI 10.1145/3789624.3789641: lead). No bias analysis of clip-creation selection found |

## D. Explicit "not found" statements
- Propensity/IPS/counterfactual debiasing applied to Most Replayed, danmaku density or clip view count labels in the highlight/summarization/clip-extraction literature: NOT FOUND with queries 1-19 (arXiv API, OpenAlex, WebSearch). Absence is not proof; arXiv API phrase search was patchy (many AND-phrase queries returned 0), so queries should be re-run with Semantic Scholar once the rate limit allows.
- Title/thumbnail effect and channel-popularity adjustment in highlight/clip label construction: NOT FOUND (only Rhapsody's channel/playlist filtering and Aha/Mr.HiSum view-count thresholds, which are filters, not adjustments).
- Candidate-tool selection bias (clips can only be chosen among tool-proposed candidates): NOT FOUND as an analysed bias. Repurpose-10K's pipeline has this structure but does not analyse it.
- Danmaku: only 2017 lag-calibration; no density position bias paper found.
- Mr.HiSum labels: bias analysis exists only inside the original paper (limitations paragraph) plus indirect treatments in TripleSumm, Rhapsody, Sahu 2026, Aha.

## E. Deep-read phase additions (RQ2 novelty re-check, forward citations; run after the coordinator's request)

Tools this phase: Semantic Scholar Graph API (citations endpoint worked intermittently with >=9-15 s spacing and retries; the /paper/search endpoint was 429 almost every time), OpenAlex (free daily budget exhausted mid-session: "Insufficient budget", resets at midnight UTC, so later OpenAlex lookups failed), Crossref API, GitHub API/raw README, arXiv HTML (read locally via curl + tag stripping), WebFetch (hit a session limit once, then recovered).

| # | Query / action | Tool | Result |
|---|---|---|---|
| 34 | Forward citations of Mr.HiSum (S2 id via DOI 10.52202/075280-1764), about 35 citing papers returned by S2 with titles/abstracts keyword-screened (debias, propensity, counterfactual, causal, confound, noisy label, calibrat, replay, danmaku, popularity, thumbnail, clickbait) | Semantic Scholar | Citing titles include LOGA, TSMD, SGWIB, MCHD, TRINITY, HABSS, Language-guided personalized summarization, SVHighlights, FSDD joint MR/HD, keyframe extraction, HAVEN, PivotSketch, Video plot segmentation, Twitch clip LLM summarisation, TripleSumm, HiVid, Sounding Highlights, TSTN, MediaPot, SummDiff, SD-MVSum, Aha, Spatial-Perceptual highlight model, domain-adaptive summarisation, AViLA, Unsupervised Transcript-assisted summarisation, HierSum, CHI 2025 Most Replayed paper, Video Summarization with LLMs, E.T. Bench, Sportoonizer, Localizing Events with Multimodal Queries, language-guided self-supervised summarisation, Non-Event Oriented Video Assessments. I read the abstracts of 9 of them (TSMD, SGWIB, Language-guided, PivotSketch, Twitch LLM clips, HiVid, Sounding Highlights, SummDiff, Transcript-assisted; TRINITY and TripleSumm were read earlier): NONE addresses debiasing, propensity, causal adjustment or calibration of Most Replayed / comment / view-count labels. (Abstract not available from S2 for LOGA, MCHD, Video plot segmentation, Non-Event Oriented: titles only [V].) Keyword hits were false positives (SGWIB "bias" = information-bottleneck context; PivotSketch "calibrat" = streaming control). |
| 35 | Forward citations of Rhapsody (ARXIV:2505.19429) | Semantic Scholar | 1 citing paper: "Benchmarking NLP Paradigms for Livestream Transcript Highlight Detection" (2025) - abstract not retrieved [V]; title suggests transcript-based highlight detection benchmark (cluster 4 lead); no debiasing in title |
| 36 | Forward citations of Aha (ARXIV:2509.16421) | Semantic Scholar | 3: SGWIB, TRINITY, Non-Event Oriented Video Assessments in Long-Form Robot Videos; none about label debiasing |
| 37 | Forward citations of TripleSumm (ARXIV:2603.01169) | Semantic Scholar | 2: TSMD, SGWIB; neither about label bias (TSMD: modality-missingness and loss misalignment with peak-driven highlights) |
| 38 | Forward citations of SVHighlights (ARXIV:2606.06926) | Semantic Scholar | 0 returned (new paper) |
| 39 | Forward citations via OpenAlex (cites: filter) for Mr.HiSum / Rhapsody / TripleSumm / Aha / SVHighlights | OpenAlex | Mr.HiSum 7 (subset of #34: Twitch LLM, Sounding Highlights, keyframe extraction, HABSS, Test-Time Counterfactual Calibration for Hallucination-Resistant Temporal Grounding, MCHD, LOGA); others 0. The "Counterfactual Calibration" hit concerns hallucination in temporal grounding, not label bias (title-level screen only [V]) |
| 40 | CHI 2025 paper "Generating Highlight Videos of a User-Specified Length using Most Replayed Data": Crossref (authors Minsun Kim, Dawon Lee, Junyong Noh; licence CC BY-NC-ND 4.0), Semantic Scholar (abstract; DBLP conf/chi/KimLN25; openAccessPdf points to publisher DOI), ACM DL pdf via curl (403 Cloudflare challenge), arXiv API title query (no arXiv version found), web search for author/project page (no result) | Crossref, S2, curl, arXiv | Abstract only. Full text NOT read. Abstract does not mention bias handling (it only says Most Replayed Data gauges the most engaging parts and an editing path is optimised). Whether the full paper treats the initial spike or other biases is [V]. |
| 41 | S2 /paper/search queries ("debiasing most replayed video highlight", "inverse propensity weighting video highlight detection engagement labels", "position bias replay statistics video", "danmaku highlight detection bias", "clip popularity prediction long video podcast highlights views") | Semantic Scholar | Only the third returned (irrelevant results); the rest 429 after retries. Not a negative finding; to be re-run [V] |

Conclusion of the re-check: still NOT FOUND - no paper applying propensity/IPS/causal debiasing to Most Replayed, danmaku or view-count labels for highlight/summary/clip selection, among the forward citations of the five anchor papers (Mr.HiSum fully screened; others small) and the earlier keyword searches. Remaining blind spots: papers that do not cite these anchors; S2 search endpoint; CHI 2025 full text.
