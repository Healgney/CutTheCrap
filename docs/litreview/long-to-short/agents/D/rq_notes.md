# Agent D RQ notes (RQ2 main, RQ5 secondary)

Tags: [F] confirmed from a primary source I opened; [I] my inference (falsifiable); [V] to verify. Row ids refer to rows.tsv.

## (a) Has anyone explicitly debiased Most Replayed / danmaku / view-count labels in video highlight or summarization? (RQ2 novelty core)

Short answer: [F] Only ad hoc, position-at-the-start fixes exist; no paper found applies propensity weighting, a causal/counterfactual adjustment, or adjustment for title/thumbnail, channel popularity or candidate-tool selection to highlight labels. Queries tried are in search_log.md (A.1-A.19). Absence of evidence only: arXiv phrase search was patchy and Semantic Scholar was not used. [V] re-run on Semantic Scholar before claiming novelty in the paper.

Closest 1-3 (most recent first):
1. **Rhapsody, D14 (arXiv 2505.19429, 2025)** [F, sections 2.1-2.2, App A]. 13,364 podcast episodes, labels = top-K (K=20, score>0.5) of the YouTube replay graph. States the graphs "exhibit biases towards the first segment, likely as users frequently replay the beginning of the content without finishing it"; 75% of episodes had a ground-truth highlight at segment 1; fix: copy segment 2's value into segment 1 (avg highlights/episode 5.86 -> 5.20). Other measures: view availability (~50k+), channel/playlist filtering, threshold to avoid flat graphs. Difference from us: one hard-coded bin, applied to labels only; no model of why the start spikes (reach/retention vs replay), nothing for title/thumbnail/channel/duration or tool-selection; segments are 1/100 of the episode (about 16 s for a 27 min episode), not boundary-aligned clips; no human check that the corrected label is better.
2. **TripleSumm / MoSu, D13 (arXiv 2603.01169, 2026)** [F, App B.2 via HTML extraction]. Calls the early spike "YouTube Most Replayed Bias", attributes it to early viewer attention/buffering, warns a model could "learn position rather than content", and sets the first 5 s of ground truth to 0. Same limits as Rhapsody (fixed 5 s window, 120-501 s videos, no estimation, no other confound). Provides the only V/T/A ablation on replay labels.
3. **Sahu and Pandey, D17 (arXiv 2607.01400, 2026)** [F]. Not a label fix but an evaluation-side control: regress both curves on [1, t, t^2] (stricter 7-df spline) and correlate residuals; a probe at r=0.47 under the quadratic control drops to 0.14 under the spline control. Lists "intro/onset effects, chapter markers, seek-back behavior" as replay biases. N=48, preprint. Closest to a statistical treatment of position, but only tests a hypothesis (brain-response drive), does not produce debiased training labels.

Acknowledged-but-not-treated: Mr.HiSum D12 (self-fulfilling bias, partial replays) [F]; Aha D16 ("imperfect proxy ... may introduce biases by amplifying content designed for high engagement", calibration/debiasing left as future work) [F]; YTMR500 D15 (popularity gate >=30k views, noisy labels, humans at chance agreement) [F]. HIVE, SVHighlights, Repurpose-10K (seeds) do not analyse label bias [F, fetched HTML]; note Repurpose-10K clips come from LLM-tool candidates that users then pick and refine [F], a candidate-selection structure whose effect is unmeasured [I].

Where debiasing does exist (recommendation/search, not highlights): position bias (D01-D04), duration bias in watch time (D06, Kuaishou), clickbait / title-cover direct effect (D07, incl. the Tiktok micro-video dataset), popularity confounding (D09), selection bias (D08), survey (D10). [F for D01-D07]

Danmaku: [F] Ping and Chen 2017 (D18) is the only comment-density highlight paper found with a correction (lag calibration). No position/popularity debiasing of comment density found.

## (b) Which click-model / counterfactual-LTR methods transfer to "replay heat / clip views as weak labels", and what they assume

Mapping (my framing [I]): a replay value at time t is roughly P(viewer reaches t) x P(replays | reached, content at t); the reach term plays the role of the examination propensity, but YouTube exposes only the normalised replay curve, not retention. A clip-view-count label is exposure x click x watch, where exposure depends on channel, title/thumbnail, duration and recommender.

| Method | What it corrects | Needs / assumptions [F] | Fit to our setting [I] |
|---|---|---|---|
| IPS-weighted ERM, Propensity SVM-Rank (D01) | position/presentation bias in clicks | position-based model: examination depends only on rank; propensity >0 for every relevant item; unbiased even with click noise (noise is order-preserving); propensity known up to a constant; swap intervention or other estimate | Needs a reach/retention model per time bin; examination-independent-of-relevance fails for seek-back after intros/chapters and for UI-driven replays |
| Regression-EM / factor model P(c)=P(e|k)P(r|x) (D02) | position bias from regular logs, no randomization | position effect separable from content features; relevance function shared across positions; EM converges (about 10 iterations) | Most practical: fit heat(t) = position-tower(t, duration) x content-tower(x_t); Sahu's [1,t,t^2] control is the crude version. Needs many videos so positions vary across content |
| Intervention harvesting / AllPairs (D03) | propensity estimation from logs of >=2 rankers | same document appears at different ranks across rankers; query distribution independent of ranker (Pr(Q|f)=Pr(Q)) | Analogue needs the same content at different timestamps (re-uploads, different edits, recap segments) under quasi-random assignment; not available on public heatmaps |
| Dual Learning Algorithm (D04) | joint propensity + relevance | PBM; documents observed at multiple positions; list-wise softmax loss | Option if we build a two-tower model; same identifiability limits as D02 |
| Click models (UBM/DBN, cascade) | extract relevance from sessions | repeated query-doc sessions; user browsing hypothesis | Needs session-level playback logs; public heatmaps are aggregates, so inapplicable without platform access [I] |
| Duration deconfounding D2Q (D06) | duration affects exposure and watch time | backdoor adjustment: stratify by duration quantile, predict within-group quantile | Directly usable: normalise clip views/completion within duration (and channel-size) strata; SnapUGC's NAWP is a hand-built version (D20) |
| Counterfactual clickbait CR (D07) | direct effect of title/cover (exposure features) on clicks | exposure features separable from content features; post-click satisfaction signal for evaluation; tested on Tiktok micro-video captions | Use for the title/thumbnail effect on clip views: train with title+thumbnail as exposure branch and subtract at inference; need a completion/like proxy to validate |
| Popularity deconfounding PDA (D09) [abstract only] | item popularity confounds exposure and interaction | popularity observable per item; some popularity is real quality | Channel subscriber count as covariate; keep some of it, as the paper argues |
| Selection-bias IPS (D08) [abstract only] | recommender-induced missingness | propensities known/estimable | Frame for "only tool-proposed candidates can be selected"; need the candidate-generation probability |

Caution [F, D05]: on the one large real search log with expert labels, standard ULTR (IPS, two-tower, DLA, RegressionEM) gave no or marginal ranking gains despite strong estimated position bias; the authors list unobserved confounding between position and context as a reason. [I] Any debiasing claim we make needs a human-labelled evaluation set (self-containedness-aware clip judgments), not just agreement with replay.

## (c) SnapUGC / VQualA 2025 engagement challenge: what it actually is

- Source dataset (D20, ECCV 2024) [F]: ~90,000 Snapchat Spotlight videos, 10-60 s, only videos with >2,000 views; labels from >2,000 viewers each, no creator or viewer identity. Targets: NAWP (average watch percentage normalised by duration-dependent linear bounds f_max(d)=0.556d+5.64, top 3% AWT treated as max) and ECR (P(watch >5 s)). Paper states metrics depend on the platform recommender. Duration input did not help NAWP (0.696 -> 0.689 SRCC).
- Challenge (D21, ICCVW 2025) [F]: target = ECR only; 120,651 videos (106,192 train / 6,000 val / 8,459 test), 5-60 s, title/description provided; labels are a normalised ranking of true ECR (privacy). Metrics SROCC, PLCC, "Final" (report does not define; winner paper defines 0.6 SROCC + 0.4 PLCC [F, D22]; report's baseline row is internally inconsistent: text 0.660/0.657 vs table 0.657/0.665 [F]). 97 participants, 15 valid test submissions; baseline (Li et al., D20) 0.660.
- Results [F]: ECNU-SJTU VQA 0.710 (SROCC 0.707 / PLCC 0.714), IMCL-DAMO 0.698, HKUST-Cardiff-MI-BAAI 0.680 (visual only, CLIP + rectifiers), MCCE 0.667, EasyVQA 0.667 (CLIP first-5-s frames + BERT title + BEATs audio), Rochester 0.449 (frozen reward model on 16 frames), brucelyu17 0.441 (XGBoost on Sentence-BERT title/caption + music category; text-only). Report has no ablations.
- Winner (D22) [F]: 3x VideoLLaMA2.1-7B-AV (frames + audio + title/description, MLP regression head) + 1x Qwen2.5-VL-7B; no ASR; VideoLLaMA2 (0.695) > Qwen2.5-VL (0.664) is a cross-backbone comparison, not an audio ablation; actual ablations only on frames (5 vs 8: 0.690 vs 0.695), data fraction (60% vs 100%), regression strategy (token 0.664 vs feature 0.676).
- Original ablation (D20) [F], NAWP SRCC: VQA 0.625; +YAMNet top-5 sound labels 0.636; +title/description 0.651; +captions 0.657; +intermediate visual features 0.689; +transcripts: no gain; +aesthetic 0.696; +visual emotion 0.690 (dropped).
- What it says for us [I]: (i) the task is hook retention of a whole short video, not selecting a span inside a long video; (ii) content-only prediction reaches ~0.70 SRCC, so content carries real but limited signal; (iii) text-only is far behind (0.441 vs 0.710) in this setting, with titles/music metadata still informative; (iv) ASR transcripts did not help in D20 (only ~30% of videos had useful transcripts per the paper [F]), which is a warning for transcript-only pipelines on short UGC but not on speech-first long video.
- Confound check: SnapUGC deliberately excludes creator information [F], so channel confounding is removed by design on the input side; labels still come from recommender-allocated Spotlight exposure [F: paper acknowledges recommender dependence]. Contrast: SMP 2025 (D23, view-based labels with uploader features) shows uploader profile removal raises MAPE 0.1754 -> 0.3010 vs 0.1818 without video embedding [F].

## (d) Known bias analyses of Mr.HiSum's Most Replayed labels

From the Mr.HiSum paper itself [F, main text; supplement not read]:
- Construction: 100 normalised scores per video, 6 s per bin for a 600 s video, aligned to 1 fps features; only videos with >=50,000 views (so heatmap is public and "not biased towards just a few users"); deleted videos, >300 s videos and the music category excluded (music has audio-dependent replay changes); 31,892 videos, 121-300 s, views 50k-290M.
- Validity evidence: cross-dataset transfer (training on Mr.HiSum beats in-domain on TVSum/SumMe F1) and a user study (25 videos, 30 annotators, 6 votes/clip): 64.8% agree, 19.6% disagree, 15.6% 3:3.
- Self-stated limitations: (1) unclear how partial rewatches are counted, YouTube does not document replay counting; authors argue only adjacent bins are affected; (2) self-fulfilling bias: the heatmap UI appears after >=50,000 views, so later viewers may replay because the UI says others did; cannot be measured or removed because YouTube does not release stats for the first 50,000 viewers; the authors judge the effect "not significant" without evidence.
- Not analysed in the main text [F, keyword search of full text for bias/popular/thumbnail/beginning/intro]: start-of-video spike, position/retention confound, title/thumbnail, channel, duration, genre effects beyond category difficulty.

External evidence about the same label type: start-of-video spike and first-segment dominance (D14, D13) [F]; onset-replay artifact on music and sensitivity of content-replay correlation to position control (D17) [F]; near-chance predictability from video-only features and chance-level human agreement on 10-shot task (D15) [F]; replay as imperfect proxy that can amplify engagement-designed content (D16) [F]; split-half reliability of heatmaps 0.82 (D17) [F].

## RQ5 contributions from my clusters (quantified ablations only)

- SnapUGC incremental feature ablation (D20) [F]: sound labels +0.011 SRCC, title/description +0.015, captions +0.006, intermediate visual features +0.032, transcripts no gain, aesthetic +0.007 (NAWP SRCC, cumulative; not a leave-one-out).
- TripleSumm (D13) [F, qualitative only]: V+T+A beats every pair and single modality on MoSu (tau 0.351, rho 0.472); single-modality ordering V > A > T slightly; numbers not extracted reliably [V].
- MVP (D23) [F]: leave-one-out MAPE: no user profile +0.1256, no video embedding +0.0064, no text +0.0056, no metadata +0.0028, no time +0.0004.
- VQualA (D21/D22) [F]: no audio-on/off or text-on/off ablation anywhere in the report or winner paper; winning "audio helps" claim is confounded with backbone.
- Rhapsody (D14): text+HuBERT reaches best hit rate 0.490, but the text-only vs +audio fine-tuned numbers were not extracted [V].
- Comments/danmaku: no quantified gain over transcript-only found in my clusters [V].

## Still unresolved

1. [V] Whether any 2024-2026 paper applies IPS/causal debiasing to replay or danmaku labels (not found; re-run with Semantic Scholar/Google Scholar; check the CHI 2025 Most Replayed paper D19, whose full text was inaccessible).
2. [I] Whether the replay curve's start spike is reach-driven or replay-driven cannot be separated with public heatmaps; needs retention curves (platform-side) or a model that treats time as position.
3. [V] Mr.HiSum supplement and GitHub metadata.csv contents (may include category/view counts that would enable a channel/popularity audit).
4. [V] Whether IMCL-DAMO and MCCE have papers with ablations (not found).
5. [V] Leads not opened: Otani et al. BMVC 2020 (position prior in moment retrieval), Towards Debiasing Temporal Sentence Grounding (2111.04321), Deconfounded VMR (SIGIR 2021), mixture-based position+trust bias correction (2108.08538), DVR/AlignPxtr duration-bias papers, Twitch implicit-crowdsourcing highlights (1910.12201).

## Update after deep reading (D01, D13, D16, D20, D21) and forward-citation re-check

- RQ2 novelty re-check [F for what was screened, V for coverage]: forward citations of Mr.HiSum (about 35 via Semantic Scholar; 9 abstracts read, others title-screened), Rhapsody (1), Aha (3), TripleSumm (2), SVHighlights (0) contain no paper that debiases, reweights or causally adjusts Most Replayed, comment or view-count labels. Details and blind spots in search_log.md section E. The S2 search endpoint stayed rate-limited, so keyword search there was not completed.
- TripleSumm (D13) is ICLR 2026 (GitHub README), code MIT, MoSu features on Hugging Face under cc-by-4.0. Its only replay-bias handling is zeroing the first 5 s (App B.2); no evidence or sensitivity for that choice. Modality ablation (Tab. 4a) on MoSu tau: V 0.298, T 0.267, A 0.271, V+T+A 0.351; pair assignment unrecoverable [V].
- Aha (D16) trains the relevance head with the video title as query and only acknowledges replay-label bias (clickbait) with MultiVENT-G fine-tuning left as future work; no audio, no ASR.
- SnapUGC/VQualA (D20/D21): cold-start framing; labels are aggregated feed statistics with >2,000-view filter, ECR = P(watch>5 s), challenge ECR = rank-normalised; no ablations in the challenge report; winner's audio claim is cross-backbone only (D22).
- Joachims 2017 (D01): the deep note lists the exact conditions for unbiasedness; ips_transferability.md maps them to what is observable in our weak-label sources. Conclusion: standard IPS, swap interventions, intervention harvesting, click models are not usable on public replay/clip-view data; usable are covariate/stratification adjustments, position-tower regression, exposure-branch counterfactual inference, and human-labelled validation.
- CHI 2025 Most Replayed paper (D19): authors Minsun Kim, Dawon Lee, Junyong Noh; only the abstract was obtainable (ACM 403; no arXiv). Bias handling there is [V].
