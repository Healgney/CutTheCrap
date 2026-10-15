# Can click-model / counterfactual-LTR debiasing be moved to "replay heat or clip views as weak labels"? Observables, availability, verdict

Tags: [F] taken from a paper I read (row/deep note id in brackets); [I] my inference, falsifiable; [V] unverified. This note covers the weak-label sources in our setting: (A) YouTube-style Most Replayed heatmap, (B) public view/like counts of user-made clips, (C) timestamped comments/danmaku/chat, (D) platform-internal logs (only if a partner supplies them).

## 0. What each debiasing method needs

| Method | Observables it needs [F] | Unbiasedness / validity condition [F] |
|---|---|---|
| IPS-weighted ERM, Propensity SVM-Rank (D01) | per-instance: the shown ranking (position of each item), click log, and a propensity for every CLICKED item = P(item examined | position, context) | unbiased iff propensity > 0 for every relevant item; examination depends only on rank (position-based model) and not on relevance; propensity known up to a constant; click noise tolerated if eps+ > eps- |
| Swap / RandPair / RandTopN randomisation (D01 5.3, D02 4.2) | ability to intervene on traffic and log clicks per swapped position | randomised assignment, CTR ratio proportional to propensity; costs user experience (D02 Tab. 1) |
| Regression-EM / factor model (D02) | logs of (query, doc, position, click) with doc-level features x_{q,d}; many impressions at varying positions | P(click)=P(E|position) P(R|x); relevance function shared across positions; clicked doc assumed relevant |
| Intervention Harvesting, AllPairs (D03) | click logs from >=2 rankers where the SAME (query, doc) appears at different ranks | assignment of query to ranker independent of the query/user distribution, Pr(Q|f)=Pr(Q); position-based model |
| Dual Learning Algorithm (D04) | click logs with positions; no interventions; features for ranker and propensity | PBM; items observed at multiple positions to identify the two towers; softmax list-wise loss |
| Click models UBM/DBN/cascade (D04 baselines, D01 5.4) | repeated sessions of the same query-doc pair with click/skip sequences | specific browsing hypotheses; same query seen many times (D01 intro) |
| Duration deconfounding D2Q (D06) | per-sample watch time AND video duration for every impression, including impressions with near-zero watch time | duration is the only confounder of exposure and watch time on the backdoor path; quantile groups large enough |
| Counterfactual de-clickbait CR (D07) | per-item exposure features (title/cover/caption) separate from content features; click logs; a post-click signal (like/finish) for evaluation | exposure features have a direct effect on click that is not mediated by content; the two feature sets are separable |
| Popularity deconfounding PDA (D09, abstract only) | item popularity, user-item interactions | popularity confounds exposure and interaction; partly real quality [V details] |
| IPS for MNAR feedback (D08, abstract only) | selection/exposure propensities | propensities known or estimable [V details] |

## 1. What we can and cannot observe

| Quantity | (A) Most Replayed heatmap | (B) Clip view counts | (C) Comment/danmaku/chat timestamps | (D) Platform logs |
|---|---|---|---|---|
| Impressions / exposure | No [F: only normalised replay scores, D12] | No public impressions or CTR [I] | No viewer-exposure log [I]; live chat sometimes carries concurrent viewers [V] | Yes |
| Position in a list shown to the viewer | Not applicable: the "position" is the timeline second; viewer path (where they started/sought) not given | Rank on a search/recommendation page unknown [I] | n/a | Yes |
| Retention / reach probability per second (the natural propensity for replay) | No: only replay frequency relative to the video, normalised to [0,1] per video, 100 bins [F, D12 4.2] | No | Partial proxy: comment volume decays with time [I] | Yes (watch-time curves) |
| Number of viewers behind the label | Not given; public only above ~50k views [F, D12 4.1] | Views public | Comment counts public; viewers not | Yes |
| Replay counting rule | Undocumented (partial rewatches) [F, D12 6] | n/a | n/a | Yes |
| Whether viewers saw the heatmap UI | Cannot be separated: UI appears after >=50k views; no stats for first 50k [F, D12 6] | n/a | n/a | Possible |
| Duration | Yes | Yes | Yes | Yes |
| Channel size, upload date | Yes (public) [I] | Yes (public) [I] | Yes | Yes |
| Title, thumbnail | Yes | Yes | Yes | Yes |
| Multiple rankers/versions showing the same content at different positions | Possibly: re-uploads, different edits of the same moment [I] | Many clips of the same source moment by different creators/channels with different titles [I] | - | A/B logs |
| Post-click satisfaction (like ratio, watch-through) | Not at second level | Likes/comments public; watch-through usually not public [I] | - | Yes |

## 2. Method-by-method verdict for our setting

1. **Standard IPS / Propensity SVM-Rank on heatmap labels (A)** - NOT directly applicable. [I] It needs a propensity for each "relevant" second, i.e. the probability that a viewer reaches or replays that second regardless of its content; the platform exposes neither retention nor per-viewer paths. The label is itself a replay-frequency ratio, not a click on a shown item. Even the closest analogue, "examination depends only on position", fails around chapter markers, seek-back and intro effects (the onset spike documented in D13/D14/D17 [F]).
2. **Swap / RandPair interventions** - UNAVAILABLE without a platform partnership. [I] We cannot reorder what viewers see; D02/D03 show these require traffic control.
3. **Intervention Harvesting (D03)** - UNAVAILABLE as published (needs multi-ranker logs with Pr(Q|f)=Pr(Q)). [I] Conceptual analogue worth testing: the same source moment re-cut by several channels (different start offsets, titles, thumbnails) as a quasi-intervention on "position within the clip" and on exposure features. Assignment is not random (creators choose), so condition (1) of D03 is violated; this would be observational adjustment, not harvesting.
4. **Regression-EM / two-tower position tower (D02, D04)** - PARTIALLY applicable. [I] heat(video, t) ~ f_position(t, duration, chapter flag) x g_content(x_t) can be fitted from many videos because content varies while position basis is shared; D17 uses an OLS [1,t,t^2] basis (spline robustness check) as a crude version [F]. Identifiability requires content features not to be a function of position (not true: intros, outros, ads are positionally structured), so the fitted position curve absorbs real "intros are boring". The Baidu-ULTR study cautions that position variability coming from confounded context can break such methods [F, D05 7.2] and that gains on click likelihood did not translate to ranking gains [F, D05 6.3]. Needs a human-labelled evaluation set.
5. **Click models (UBM/DBN/cascade)** - UNAVAILABLE. [I] Require repeated session-level click/skip sequences; public replay is an aggregate.
6. **Duration deconfounding (D06)** - AVAILABLE in a simplified form for (B) and for heatmap lengths. [I] We have duration and views per clip; stratifying clip views or completion by duration quantile is feasible; the backdoor argument rests on duration being the main confounder of exposure, which is not true for clips (channel size, title/thumbnail dominate, see D23 [F]). Impressions-with-zero-watch (needed to avoid survivorship) are not observed publicly; only clips that got views exist [I].
7. **Counterfactual de-clickbait CR (D07)** - PARTIALLY available for (B). [I] We have exposure features (title, thumbnail text/image) and content features (audio, transcript, frames) for each clip, and views/likes; the method needs a click-like target and a like-like post-click signal: views per channel-adjusted baseline vs like or comment ratio could play these roles, but both are exposure-contaminated. Evaluation on Tiktok micro-video captions exists [F]; transfer to clip views untested.
8. **Popularity/channel adjustment (D09, D23)** - AVAILABLE as covariate adjustment. [I] Subscriber count, channel median views, upload age are public; D23 shows uploader features explain far more than video content in a view-based label (MAPE 0.1754 -> 0.3010 without user profile; -> 0.1818 without video embedding) [F], so any claim from clip views must be channel-stratified or evaluated with leave-channel-out splits.
9. **Label surgery on the onset (D13, D14)** - AVAILABLE and already used. [F] zero the first 5 s (D13) or copy bin 2 into bin 1 (D14). These are heuristic masks, not estimates; sensitivity to window size is not reported [F by absence].
10. **Doubly-robust / other ULTR variants, trust-bias correction** - not read; listed as leads only [V].

## 3. Consequences for the RQ2 plan [I]
- The only methods that can be run on public data are (i) a position/duration/channel regression adjustment, (ii) stratified or rank-normalised labels (as SnapUGC does with NAWP/rank-normalised ECR [F, D20/D21]), (iii) leave-channel-out evaluation, and (iv) the title/thumbnail "exposure branch" idea. None gives the unbiasedness guarantee of D01; they are bias reduction under stated covariates.
- A faithful IPS/DLA study needs platform-side logs (D). Without them, claims about debiasing should be framed as covariate adjustment validated against human clip judgments, not as unbiased learning.
- Validate against humans: D12 reports only 64.8% agreement of Most Replayed with majority human votes on 5-10 s clips [F]; D05 shows click-likelihood gains may not help ranking [F]. A debiasing claim should show improved agreement with a held-out human preference set.
- Title-as-input leakage: Aha conditions on the video title (D16 [F]); with replay labels this lets the model learn title-to-segment associations, an exposure shortcut that D07 targets [I].
