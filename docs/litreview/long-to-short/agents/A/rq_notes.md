# Agent A -- RQ notes (clusters 1 and 2; primary RQ2, RQ3; secondary RQ5; side-notes RQ1/RQ4)

Tags: [F] confirmed in a primary source I opened (section-level reading unless the row says abstract-only) / [I] my inference, falsifiable / [V] needs verification.
Row ids refer to rows.tsv; notes/ has the section-level facts.

## Direct answers to the four special questions

### (a) Datasets whose labels come from behaviour / pairs of official-or-user clips, with scale and licence
| dataset | label source | scale | domain | availability / licence |
|---|---|---|---|---|
| Repurpose-10K (A01) | OpusClip users: tool proposes topic clips -> like/post -> creator re-trims start/end [F] | 120,925 clips, 8,398 videos (11,210 after splitting), 4,539.94 h, avg 32 min [F] | YouTube long UGC (interviews/vlogs/livestreams per README; share not measured [V]) | JSON splits on GitHub; videos via yt-dlp; code MIT; dataset licence not stated [V] |
| SVHighlights (A06) | official full broadcast <-> official highlight video, PSNR alignment [F] | 320 videos, 640.18 h | sports | URLs + features + labels; licence [V] |
| TVHighlights (A07) | reuse frequency of clips in short-form platform videos traced by fingerprint; test by human vote [F] | 1,721 videos (1,368 train / 353 test), 15 genres | movies/TV | "will release" [V] |
| Video2GIF (A13) | user-made GIF <-> source video via frame hash [F] | 121,647 GIFs, 84,754 videos, 7,379 h | web video, GIFs 5.8 s, silent | repo exists; only 432 videos CC-BY; GIFSoup defunct (Mr.HiSum statement) [F] |
| Fu 2017 (A16) | community highlight video <-> full LoL match [F] | 321 matches | esports | "will be released" [V] |
| Sun 2014 (A20) | raw <-> edited YouTube pairs [F abstract] | ~700 min | personal videos in 6 domains | repo [V] |
| Mr.HiSum (A05) | YouTube Most Replayed (>=50k viewers) [F] | 31,892 videos, 1,788 h, 2-5 min | YouTube-8M | CC BY 4.0 + YouTube ToS [F README] |
| KLive (A08) | long-view-through-rate of live rooms [F] | 17,897 rooms, 19,334 h | live streaming | not actually public [V] |
| PHD-GIFs (A14) | per-user GIFs | 81,056/7,595 videos (second-hand) [V] | YouTube | [V] |
- [I] I found **no** dataset of spoken-word long videos (podcast / talk show / lecture) paired with *official* creator-published clips of those same videos with open licence. Repurpose-10K is the closest (user-curated clips on OpusClip), but its interview/podcast share is not reported.
- [I] No dataset I read combines clip labels with engagement outcomes of the clips (views/retention of the published short); SVHighlights, TVHighlights and Video2GIF only use the *fact of selection/reuse*; Mr.HiSum and KLive use *viewing* behaviour of the long video itself.

### (b) Repurpose-10K and HIVE: task, inputs, outputs, labels, metrics, boundaries, self-containedness
- Repurpose-10K [F, A01 notes]: input untrimmed video (>=30 min, avg 32 min) as 1-s segments (CLIP/PANNs/WhisperX+MiniLM); output ~60 s clips via per-second classification + offset regression, soft-NMS, 3 clips per 10 min; labels = OpusClip users' like/post + manual start/end refinement; metric = tIoU 0.5-0.9 (avg best 11.57, tIoU@0.9 only 1.57); human study (10 raters) of Engagement/Completeness gives labels 3.87/3.42 vs pro editors 3.94/3.74 vs random 1.51/1.62. Boundaries = creators' manual trims, not snapped to linguistic units. Self-containedness: only as a stated design intent ("self-contained sub-topic", "complete narrative") and the Completeness rating; no automatic metric.
- HIVE/DramaAD [F, A02 notes]: input = ~10-episode short-drama storyline (20-30 min) turned into scene narration; output = edited videos (highlight scenes + chosen opening/ending scenes + pruning); no labels (prompted LLMs); references = 522 pro-edited ads; metrics Diversity/Smoothness/Engagement/VEI/Hook/Suspense from human viewers; boundaries are scene-level with an explicit LLM opening/ending selection; self-containedness appears only as a prompt rule ("avoid starting with scenes that rely heavily on prior plot context") and the Smoothness metric (interruption count) -- no measurement of context-independence.

### (c) Vidi / Vidi2.5 on clip extraction
- [F] Vidi is temporal retrieval given a query (VUE-TR; overall IoU-AUC 39.6 Vidi-1.5 vs Gemini-2.5-Pro 15.2); Vidi2.5 adds STG/QA and reports VUE-TR-V2 IoU-AUC 49.62 vs Gemini 3 Pro 37.58 / GPT-5 17.15. "Highlight segments + titles" is a one-paragraph qualitative demo (Fig. 8) and a demo mode in the repo. No benchmark, human study or baseline for clip extraction; no engagement or self-containedness evaluation. [I] So Vidi is not a measured competitor on our task, but its TR strength (long video, audio queries) makes it a plausible backbone/baseline.

### (d) Does prior work already do "long speech video -> independent, watchable short clips"? Closest 1-3 and differences
1. **PodReels (A10, DIS 2024)** -- same domain (hour-long video podcasts) and same output length (15-45 s). Formative study names self-containedness explicitly ("clear context", unresolved referents "here"/"them") and hook styles; sentence is the unit; GPT-4 returns sentence IDs; user adjusts context windows. Differences: human-in-the-loop prompt tool, no learned model, no benchmark/dataset, no engagement labels, no automatic self-containedness or boundary metric, evaluated by criterion-adherence (76.7% of clips right on >=3 criteria) and a 10-person user study. [F]
2. **AntPivot / AntHighlight (A09, arXiv 2022)** -- long speech streams (avg ~47 min), segments defined as "integral topic and complete content", boundaries on utterances, DP decoding, boundary F1 (+-5 s). Differences: finance livestream only, segments ~212 s, human editorial labels (no behaviour), no hook/title, no cross-clip ranking by engagement, no explicit self-containedness test. [F]
3. **Repurpose-10K (A01)** -- long UGC -> 60 s clips with real creator behaviour. Differences: no self-containedness definition/metric beyond a rating, no sentence/turn-aware boundaries, no title, weak performance (11.57 avg tIoU), single-tool candidate bias [I]. Plus HIVE (A02) as the industrial pipeline with an explicit boundary stage but in short drama; Lotus/RankCut (A11/A12) are authoring-tool papers.
- [I] Net: nobody I found (a) *defines or measures* self-containedness of a clip for long speech video, (b) combines it with an engagement label and a boundary-quality criterion in one benchmark, or (c) evaluates against creator-published clips of podcasts/interviews with open data. The novelty risk is in the *idea* (PodReels/Repurpose-10K) rather than a ready-made method; the benchmark/measurement angle appears open as of Oct 2026 within the sources I could reach (search was not exhaustive: Google Scholar / S2 citation graph were unavailable, see search_log).

## RQ2 -- natural supervision and its biases (cluster 2 + 1)
Signals seen: Most Replayed (A05), implicit view-time on live rooms (A08), user-made GIFs / community highlight videos / raw-vs-edited pairs (A13, A16, A20), official highlight videos (A06), short-video reuse count (A07), creator like/post + re-trim (A01), duration as proxy (A21), chat/danmaku (A15, A16, A17, A18), personal GIF history (A14).
Biases explicitly discussed by authors [F]: Mr.HiSum self-fulfilling replay bias (UI shown only after 50k views), unclear partial-replay counting; LIGHTOR and Ping&Chen reaction lag of chat/danmaku and noise; Fu 2017 positives should concentrate on the *end* of a clip because the action comes late; Video2GIF web-label noise (robust Huber rank loss); SVHighlights label agreement varies by sport (alpha 0.22-0.72); PHD-GIFs user-specific taste.
Biases NOT discussed anywhere I read [I]: position/exposure bias of impression-based labels (KLive LVTR); candidate-generator selection bias (Repurpose-10K: the clips are chosen from OpusClip's own proposals); popularity/channel bias (Repurpose avg 18.9M views per video; Mr.HiSum >=50k views filter); title/thumbnail effect on clip choice; seek-bar UI effects on replay (intro replays, scrub-backs); platform-specific length effects. None of the papers I read at section level (A01, A02, A05-A10, A13, A15, A16, A22; the abstract-only ones were not checked) applies propensity weighting, click-model or LTR-style debiasing; they cope with noise via robust losses (Huber rank loss, noisy-label cleaning in TVHighlights, border-aware pairwise loss in KLive) or majority vote. This is an open gap for RQ2.

## RQ3 -- boundary as structured prediction
- Continuous regression of offsets: Repurpose-10K (A01, IoU regression head), Vidi (A03/A04, timestamp tokens in text; AUC-IoU), UMT/Moment-DETR baselines in A01/A06 (very low tIoU / HIT@K on long videos). [F]
- Selection among candidate cuts: AntPivot (utterance boundaries + DP, Boundary F1) [F]; HIVE (scene-level candidates from shot->scene merging, LLM picks opening/ending; random boundary selection drops Hook 0.71 -> 0.28) [F]; PodReels (sentence units + context-window expansion) [F]; SVHighlights TF-Selector merges shots whose ASR sentence spans a cut (<1 s word gap) to avoid mid-sentence segmentation [F]; TVHighlights shows per-clip scoring + selection beats MLLM direct moment retrieval (AP 47.42 vs 36.62) [F].
- Boundary-specific metrics seen: AntPivot Boundary F1 (+-5 s), LIGHTOR start/end precision (10 s tolerance), SVHighlights window-F1 (appendix); HIVE Smoothness (interruptions) and Hook/Suspense rates. I found **no** metric that checks whether a cut falls mid-sentence/mid-turn or leaves a dangling reference [I].
- LIGHTOR (A15) refines boundaries from viewer interaction; Fu 2017 (A16) notes the salient action sits late in the clip so context should precede it. [F]

## RQ5 -- quantified modality evidence in my clusters (everything else is unablated)
| paper | comparison | number | caveat |
|---|---|---|---|
| Repurpose-10K (A01) | A 9.66, V 9.52, C(caption/ASR text) 9.59; A+V 10.31; A+V+C 10.75; full 11.57 | caption adds +0.44 on top of A+V | tIoU tiny; features are generic (CLIP/PANNs/MiniLM) |
| AntPivot (A09) | text S 67.2 AP@0.5; +speaker 67.8; +mel P 67.3; all 68.9 | speaker > prosody | finance livestream, mel embedding only |
| SVHighlights (A06) | caption 15.00 HIT@1; +audio volume 16.25; +transcript 21.25; all 26.56 | transcript +6.25; volume alone small, helps with transcript | sports, 'audio volume' only, LLM scoring |
| KLive (A08) | w/o text (ASR+comments) -2.01% tau; w/o visual -4.72% | visual dominant | ASR and comments not separated; no acoustic features |
| Fu 2017 (A16) | chat 43.2, video 72.2, both 74.7 (F) | chat adds +2.5 | LoL esports 2017 |
| HIVE (A02) | ASR-only vs scene-narration: VEI 0.54 -> 1.14 (-> 4.01 with staged editing) | confounded with segmentation | short drama |
| Pharmacy (A22) | transcript-only LLM vs full-video Gemini: 3-4x faster, similar clip metrics | no quality ablation by modality | proprietary |
| Mr.HiSum (A05), Video2GIF (A13) | visual only (music category removed in Mr.HiSum because replay depends on audio) [F] | - | no audio evidence |
| TVHighlights (A07) | no modality ablation in main paper [F] | - | |
| Vidi (A03) | audio-query accuracy < vision-query accuracy for all models [F statement] | - | retrieval, not selection |
- [I] No paper in these clusters ablates laughter, applause, prosody, or visual reactions separately for clip selection; "audio" is volume (SVHighlights), mel pattern (AntPivot) or PANNs (Repurpose). The strongest consistent signal is that **transcript/text carries most of the gain for talk-like content** while generic audio adds little.

## Unresolved / not found (with tags)
1. [V] Whether Repurpose-10K contains a large share of interviews/podcasts and what the clip length distribution looks like (Fig. 2 not numerically read; check data/*.json).
2. [V] Release status/licence of TVHighlights, KLive, Fu 2017 data; project page/licence of SVHighlights.
3. [V] Venue of AntPivot (arXiv only?), HIVE code (none found), OpusClip/CapCut internals (vendor docs: OpusClip help centre lists Hook/Flow/Value/Trend [F as vendor statement]; no algorithm or validation published; CapCut docs describe highlight detection only in marketing terms).
4. [V] Forward citation snowball for Repurpose-10K/HIVE is incomplete: Semantic Scholar returned HTTP 429; OpenAlex lists only 2 citers for Repurpose-10K (neither relevant) and 0 for HIVE; arXiv full-text citation search is unavailable. Missing recent citers are plausible.
5. [I] Adjacent leads handed to other agents: LiveSeg/MultiLive (WACV 2023, livestream topic segmentation; cluster 4/5), "Large Language Models Are Natural Video Popularity Predictors" (ACL Findings 2025; cluster 8), ContentCTR (arXiv 2306.14392; frame-level live CTR; cluster 7/8), KuaiLive-M3 (arXiv 2607.24862; multi-feedback live dataset; cluster 7/8), Minimal Clips Maximum Salience (arXiv 2512.11399; movies; cluster 3/6).

## Addendum after deep reading (phase 2; details in deep/*.md and row_updates.tsv)
Corrections to the earlier notes:
1. [F] PodReels (A10): the GPT-4 clip-extraction prompt contains NO self-containedness instruction (only length, speakers, style, keywords); context-independence is handled by humans in the refine step. Its "tagline" (<10 words) is the only hook-title analogue and is never evaluated. Abstract says 59% of time / 44% of mental demand; Discussion says -41% mental demand / -56% time (inconsistent). Evaluation set = 4 episodes (~45 min), 168 + 30 clips.
2. [F, computed from released JSON] Repurpose-10K (A01): clip median is ~36 s (98% in 15-90 s), not ~60 s; 5.3 clips per 10 min (paper's inference k = 3 per 10 min); selected clips cover ~30% of chunk time; chunks <=30 min; 807 YouTube ids appear in more than one split (404 in both train and test) -> chunk-level split leakage; JSON timeRange hours 3,803 vs paper 4,539.94.
3. [F] TVHighlights (A07): videos are short (train avg 50.6 s, test avg 134.9 s; raw 248.8 s), supplement says dataset not yet released; no modality ablation. It is NOT a long-video resource.
4. [F] HIVE (A02): the "clarity" rule about not opening on context-dependent scenes is also in the End2End baselines' prompts, so the large ablation effect of random boundaries (Hook 0.71 -> 0.28) is about boundary choice itself, not the clarity wording; HF repo holds 2,603 raw videos / 501 edits vs 2,582 / 522 in the text.
5. [F] SVHighlights (A06): dataset licence is CC BY-NC 4.0 on HF, code Apache-2.0, code+data released 2026-05; project page claims +3.12 HIT@1 whereas arXiv v2 says +2.50.
6. [F] Lotus (A11) and RankCut (A12) were read to sections level (PDF text): Lotus formative analysis of 20 YouTube long (17.9 min) -> Short (47.5 s) pairs: 13 highlight-type, 7 summary-type, 13 add new audio; its automatic baseline lacked hooks/conclusions. RankCut snaps all boundaries to sentence timecodes by construction ("timecode fidelity" 100%) and reports ROUGE/QA on MeetingBank only; no clip-level or engagement evaluation.
Threat update: PodReels remains the nearest neighbour for concept/domain (High for idea novelty, Low for method); AntPivot remains the nearest for boundary formulation; Repurpose-10K remains the nearest for data but its statistics/splits need cleaning before reuse; TVHighlights drops to Low-Medium for our setting (short videos).
