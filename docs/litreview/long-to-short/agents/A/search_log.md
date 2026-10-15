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
