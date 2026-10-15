# A13 Video2GIF, A15 LIGHTOR, A16 Fu et al. 2017 -- reading notes (older behaviour/user-clip label papers)

Read via pdftotext on the copies WebFetch stored in tool-results (A13, A15) and ar5iv HTML (A16). Sections: abstract, intro, dataset/labelling, metrics, main results; not every table read.

## A13 Video2GIF (arXiv 1605.04850, CVPR 2016)
- [F] Dataset (Table 1): 121,647 animated GIFs; mean GIF duration 5.8 s; 84,754 videos; total video duration 7,379 h; mean video 5.2 min; only 432 videos are CC-BY; experiments use 100,699 GIFs / 70,456 videos; test set 357 videos; ~65K train / rest validation videos.
- [F] Source GIF sites: GIFSoup, Make-a-GIF, Imgflip etc. (user-generated GIFs with a link to the YouTube source). Alignment by perceptual hash (DCT-based) per frame, Hamming-distance matching of GIF frames to video frames; non-GIF segments of the same video serve as negatives; >500K positive/negative segment pairs.
- [F] Model: Robust Deep RankNet with C3D features and an adaptive Huber rank loss to cope with noisy web data. Metrics: normalised meaningful summary duration (nMSD, lower better) and mAP.
- [F] GIFs have no sound: the text states a GIF is "short, entirely visual with no sound"; hence no audio/speech modelling.
- [F] Mr.HiSum (A05) remarks that a large part of the dataset is no longer available because GIFSoup is down. Repo: github.com/gyglim/video2gif_dataset (footnote).
- [V] Best-row nMSD/mAP numbers not isolated (Table 2 variants all around 44% nMSD / 16% mAP).

## A15 LIGHTOR (arXiv 1910.12201)
- [F] Two modules: Highlight Initializer predicts approximate highlight position from timestamped chat (message number, message length, message similarity in sliding windows; trained on a few labelled videos); Highlight Extractor refines start/end iteratively from viewers' play/seek behaviour (a "red dot" prior is shown; Type I/II/III dot-position cases; weighted aggregation, outlier removal).
- [F] The authors explicitly model the delay between a highlight and the chat reaction (Figure 2a) and state that a naive regression/LSTM fails to capture it.
- [F] Data: Dota2: 60 Twitch videos (0.5-2 h) labelled by experienced players with start/end; LoL: 173 videos from the NALCS dataset (labels from a YouTube channel's highlight collections). Evaluation recruits hundreds of MTurk workers to generate interaction data.
- [F] Metrics: Chat Precision@K; Video Precision@K (start): a start is correct if it lies in [s-10, e]; (end): in [s, e+10]. Compared with chat-LSTM trained on LoL; LIGHTOR trained on 1 video generalises LoL -> Dota2.
- [F] Reproducibility repo: github.com/sfu-db/Lightor_Exp. Venue not stated on the arXiv PDF (cs.DB) [V].
- [I] Relevance: shows that even with behaviour signals, boundaries need a separate refinement stage and a tolerant metric (10 s); chat/danmaku are lagged signals.

## A16 Fu et al. EMNLP 2017 (arXiv 1707.08559)
- [F] Dataset: League of Legends championships (NALCS English 218 videos, LMS Traditional Chinese 103 videos = 321) from Twitch; chat + video; labels = community highlight videos from a single YouTube channel (Onivia) (5-7 min highlights); frames of the highlight video are matched to the full match with a 48-d colour-grid template matching over 60-frame windows; clip transitions found from low matching score; each clip start/end located in the full video.
- [F] Observation: the action of interest often occurs in the later part of a highlight clip while the early part sets the stage; positives restricted to the last 25% of frames in some settings; evaluation uses all clip frames.
- [F] Test results (F-score, Table 3): chat-only L-Char-LSTM 43.2 (NALCS) / 39.7 (LMS); video-only V-CNN-LSTM 72.2 / 69.2; joint lv-LSTM 74.7 / 70.0. Text: vision-only is more accurate than language-only; adding chat helps a little. Character-level LSTM beats word-level by 22.3% on dev; best chat window = 7 s.
- [V] Dataset described as "will be released"; availability not checked.
