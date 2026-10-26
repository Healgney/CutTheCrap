#!/usr/bin/env python3
"""P6 evaluation harness (independent of any model).

Metrics (spec: docs/07-server-handoff.md §P6 and its 10-27 revision):
  orig_tiou      verbatim copy of Repurpose calculate_tiou (precision-only),
                 averaged over tIoU thresholds {.5,.6,.7,.8,.9}.
  R/P/F1@t       one-to-one greedy tIoU matching at t in {0.5, 0.7, 0.9};
                 pooled (micro) counts over all videos.
  bF1@tol        boundary F1 at tol in {0.5, 1, 2} s; starts and ends matched
                 separately, one-to-one greedy by distance; pooled micro.
  cond_iou{t}    conditional boundary error: on the one-to-one IoU>=t matched
                 pairs (t in {0.5, 0.3}), median |start error|, |end error| and
                 the fraction within {0.5, 1, 2} s; plus the number of pairs.
  midsent_rate   fraction of predicted boundaries inside an ASR word or more
                 than 1 s from the nearest sentence edge (lower is better).
  Budgets        "orig"   = ceil(minutes * 0.3) per video; "oracle" = |GT|.
  random         per video, as many clips as the budget allows, durations
                 sampled from that video's GT durations, uniform placement;
                 every scalar metric reported as [mean, std] over N runs.

Rebuilt 2026-10-27 from the pre-P6 harness on EC2, adding the conditional
metrics and budget-following random baseline described in docs/P6/fix.md;
validated by reproducing fix.md's arm A / arm C / random numbers.

Input formats (auto-detected), ABSOLUTE video seconds:
  P1  {vid: [[start, end, score], ...]}
  P2  {vid: {"chunk_start": s, "segments": [[s, e, sc], ...]}}
  P3  [{"video_id": v, "chunk_start": s, "segments": [...]}, ...]

Usage:
  python l2s/eval/evaluate.py --pred preds.json \
      --gt eval/paper/splits/clean/test_clean.json \
      --ids eval/paper/splits/test_clean_covered_ids.txt \
      --asr $L2S_ASR --budgets orig,oracle --random 10 --out metrics.json
"""
import argparse
import json
import math
import os
import random
import statistics

TIOU_THRESHOLDS = [0.5, 0.6, 0.7, 0.8, 0.9]
F1_THRESHOLDS = [0.5, 0.7, 0.9]
BF1_TOLERANCES = [0.5, 1.0, 2.0]
COND_IOUS = [0.5, 0.3]
COND_TOLS = [0.5, 1.0, 2.0]
MAX_SEG_PER_MIN = 0.3
MIDSENT_SENT_WINDOW = 1.0


# --- verbatim from Repurpose-main/utils/metrics.py (calculate_tiou only) ---
def calculate_tiou(reference_segments, predicted_segments, tiou_thresholds=[0.5]):
    def calculate_iou(segment1, segment2):
        start_max = max(segment1[0], segment2[0])
        end_min = min(segment1[1], segment2[1])

        intersection = max(0, end_min - start_max)
        union = (segment1[1] - segment1[0]) + (segment2[1] - segment2[0]) - intersection

        return intersection / union if union != 0 else 0

    max_tiou_scores = [max([calculate_iou(predicted_segment, ref_segment) for ref_segment in reference_segments], default=0)
                       for predicted_segment in predicted_segments]

    precision_per_threshold = {}
    for threshold in tiou_thresholds:
        valid_predictions = sum(score >= threshold for score in max_tiou_scores)
        precision = valid_predictions / len(predicted_segments) if len(predicted_segments) > 0 else 0
        precision_per_threshold[threshold] = precision

    return precision_per_threshold
# --- end verbatim copy ---


def iou(s1, s2):
    inter = max(0.0, min(s1[1], s2[1]) - max(s1[0], s2[0]))
    union = (s1[1] - s1[0]) + (s2[1] - s2[0]) - inter
    return inter / union if union > 0 else 0.0


def load_predictions(path):
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    preds = {}
    if isinstance(raw, dict):
        for vid, v in raw.items():
            if isinstance(v, dict):
                cs = v.get("chunk_start", 0.0) or 0.0
                preds.setdefault(vid, []).extend(
                    (seg[0] + cs, seg[1] + cs, seg[2] if len(seg) >= 3 else 1.0) for seg in v.get("segments", []))
            else:
                preds[vid] = [(seg[0], seg[1], seg[2] if len(seg) >= 3 else 1.0) for seg in v]
    elif isinstance(raw, list):
        for entry in raw:
            cs = entry.get("chunk_start", 0.0) or 0.0
            preds.setdefault(entry["video_id"], []).extend(
                (seg[0] + cs, seg[1] + cs, seg[2] if len(seg) >= 3 else 1.0) for seg in entry.get("segments", []))
    else:
        raise ValueError(f"unsupported prediction format: {type(raw)}")
    return preds


def load_gt_chunks(path, ids):
    with open(path, encoding="utf-8") as f:
        entries = json.load(f)
    gt = {}
    for e in entries:
        vid = e["youtube_id"]
        if ids is not None and vid not in ids:
            continue
        t0, t1 = e["timeRange"]
        g = gt.setdefault(vid, {"segments": [], "span": [t1, t0], "chunks": 0})
        g["segments"].extend((s, en) for s, en in e["segments"])
        g["span"][0] = min(g["span"][0], t0)
        g["span"][1] = max(g["span"][1], t1)
        g["chunks"] += 1
    return gt


def apply_budget(segs, budget):
    if budget is None or len(segs) <= budget:
        return segs
    return sorted(segs, key=lambda x: x[2], reverse=True)[:budget]


def orig_budget(gt_entry):
    span_min = (gt_entry["span"][1] - gt_entry["span"][0]) / 60.0
    return max(1, math.ceil(span_min * MAX_SEG_PER_MIN))


def budget_for(gt_entry, budget):
    if budget == "orig":
        return orig_budget(gt_entry)
    if budget == "oracle":
        return len(gt_entry["segments"])
    return None


def greedy_iou_pairs(preds, gts, thr):
    """One-to-one matches [(pred_idx, gt_idx)] by descending IoU, IoU >= thr."""
    scores = []
    for i, p in enumerate(preds):
        for j, g in enumerate(gts):
            v = iou(p, g)
            if v >= thr:
                scores.append((v, i, j))
    scores.sort(reverse=True)
    used_p, used_g, pairs = set(), set(), []
    for v, i, j in scores:
        if i not in used_p and j not in used_g:
            used_p.add(i)
            used_g.add(j)
            pairs.append((i, j))
    return pairs


def greedy_boundary_pairs(p_times, g_times, tol):
    cands = []
    for i, p in enumerate(p_times):
        for j, g in enumerate(g_times):
            d = abs(p - g)
            if d <= tol:
                cands.append((d, i, j))
    cands.sort()
    used_p, used_g, matches = set(), set(), 0
    for d, i, j in cands:
        if i not in used_p and j not in used_g:
            used_p.add(i)
            used_g.add(j)
            matches += 1
    return matches


class SentenceIndex:
    """Same semantics as l2s/candidates/g0_coverage.py::mid_sentence."""

    WORD_MARGIN = 0.05
    SENT_FAR = MIDSENT_SENT_WINDOW

    def __init__(self, asr_path):
        with open(asr_path, encoding="utf-8") as f:
            asr = json.load(f)
        self.words, self.sents = [], []
        for seg in asr.get("segments", []):
            if "start" in seg and "end" in seg:
                self.sents.append((float(seg["start"]), float(seg["end"])))
            for w in seg.get("words", []) or []:
                if isinstance(w, dict) and "start" in w and "end" in w:
                    self.words.append((float(w["start"]), float(w["end"])))
        self.words.sort()
        self.edges = [x for s in self.sents for x in s]

    def is_midsent(self, t):
        for ws, we in self.words:
            if ws + self.WORD_MARGIN < t < we - self.WORD_MARGIN:
                return True
        if not self.sents:
            return False
        return min(abs(e - t) for e in self.edges) > self.SENT_FAR


_ASR_CACHE = {}


def sentence_index(asr_dir, vid):
    if vid not in _ASR_CACHE:
        p = os.path.join(asr_dir, f"{vid}.json")
        try:
            _ASR_CACHE[vid] = SentenceIndex(p) if os.path.exists(p) else None
        except (json.JSONDecodeError, OSError):
            _ASR_CACHE[vid] = None
    return _ASR_CACHE[vid]


def evaluate(preds, gt, asr_dir=None, budget="orig", random_runs=0, seed=1234):
    vid_pool = sorted(gt.keys())
    pred_vids = set(preds.keys())
    tp = {t: 0 for t in F1_THRESHOLDS}
    n_gt_total = n_pred_total = 0
    b_tp = {tol: {"start": 0, "end": 0} for tol in BF1_TOLERANCES}
    n_bounds = {"start": 0, "end": 0}
    per_chunk_tiou = []
    cond = {t: {"start": [], "end": []} for t in COND_IOUS}
    midsent = {"start": [0, 0], "end": [0, 0]}
    midsent_missing_asr = 0

    for vid in vid_pool:
        g_entry = gt[vid]
        g_segs = sorted(g_entry["segments"])
        p_segs = sorted(apply_budget(preds.get(vid, []), budget_for(g_entry, budget)))
        p_pairs = [(s, e) for s, e, _ in p_segs]
        n_gt_total += len(g_segs)
        n_pred_total += len(p_pairs)
        if g_segs:
            per_chunk_tiou.append(calculate_tiou(g_segs, p_pairs, TIOU_THRESHOLDS))
        for t in F1_THRESHOLDS:
            tp[t] += len(greedy_iou_pairs(p_pairs, g_segs, t))
        for t in COND_IOUS:
            for i, j in greedy_iou_pairs(p_pairs, g_segs, t):
                cond[t]["start"].append(abs(p_pairs[i][0] - g_segs[j][0]))
                cond[t]["end"].append(abs(p_pairs[i][1] - g_segs[j][1]))

        p_starts = [s for s, _, _ in p_segs]
        p_ends = [e for _, e, _ in p_segs]
        n_bounds["start"] += len(p_starts)
        n_bounds["end"] += len(p_ends)
        for tol in BF1_TOLERANCES:
            b_tp[tol]["start"] += greedy_boundary_pairs(p_starts, [s for s, _ in g_segs], tol)
            b_tp[tol]["end"] += greedy_boundary_pairs(p_ends, [e for _, e in g_segs], tol)

        if asr_dir:
            idx = sentence_index(asr_dir, vid)
            if idx is not None:
                for side, times in (("start", p_starts), ("end", p_ends)):
                    for t in times:
                        midsent[side][1] += 1
                        midsent[side][0] += idx.is_midsent(t)
            else:
                midsent_missing_asr += len(p_starts) + len(p_ends)

    m = {}
    for t in TIOU_THRESHOLDS:
        m[f"orig_tiou@{t}"] = sum(c[t] for c in per_chunk_tiou) / len(per_chunk_tiou) if per_chunk_tiou else 0.0
    m["orig_tiou_avg"] = sum(m[f"orig_tiou@{t}"] for t in TIOU_THRESHOLDS) / len(TIOU_THRESHOLDS)
    for t in F1_THRESHOLDS:
        r = tp[t] / n_gt_total if n_gt_total else 0.0
        p = tp[t] / n_pred_total if n_pred_total else 0.0
        m[f"R@{t}"], m[f"P@{t}"], m[f"F1@{t}"] = r, p, (2 * r * p / (r + p) if r + p else 0.0)
    for tol in BF1_TOLERANCES:
        tag = f"{tol:g}s"
        for side in ("start", "end"):
            hit = b_tp[tol][side]
            r = hit / n_gt_total if n_gt_total else 0.0
            p = hit / n_bounds[side] if n_bounds[side] else 0.0
            m[f"bF1_{side}@{tag}"] = 2 * r * p / (r + p) if r + p else 0.0
            m[f"bP_{side}@{tag}"], m[f"bR_{side}@{tag}"] = p, r
    for t in COND_IOUS:
        tag = f"cond_iou{t:g}"
        m[f"{tag}_n_pairs"] = len(cond[t]["start"])
        for side in ("start", "end"):
            errs = cond[t][side]
            m[f"{tag}_{side}_median"] = statistics.median(errs) if errs else float("nan")
            for tol in COND_TOLS:
                m[f"{tag}_{side}_within{tol:g}s"] = (sum(e <= tol for e in errs) / len(errs)) if errs else float("nan")
    if asr_dir:
        for side in ("start", "end"):
            bad, total = midsent[side]
            m[f"midsent_{side}"] = bad / total if total else float("nan")
        m["midsent_missing_asr_boundaries"] = midsent_missing_asr
    m["n_videos"] = len(vid_pool)
    m["n_gt_segments"] = n_gt_total
    m["n_pred_segments"] = n_pred_total
    m["n_pred_videos_missing"] = len([v for v in vid_pool if v not in pred_vids])
    if random_runs:
        m["random"] = random_baseline(gt, asr_dir, budget, runs=random_runs, seed=seed)
    return m


def random_baseline(gt, asr_dir, budget, runs=10, seed=1234):
    runs_m = []
    for run in range(runs):
        rng = random.Random(seed + run)
        pred = {}
        for vid, g in gt.items():
            t0, t1 = g["span"]
            durs = [e - s for s, e in g["segments"]] or [30.0]
            n = budget_for(g, budget) or len(g["segments"])
            clips = []
            for _ in range(n):
                d = min(rng.choice(durs), t1 - t0)
                s = rng.uniform(t0, max(t0, t1 - d))
                clips.append((s, s + d, rng.random()))
            pred[vid] = clips
        runs_m.append(evaluate(pred, gt, asr_dir=asr_dir, budget=budget))
    out = {}
    for k, v in runs_m[0].items():
        if isinstance(v, (int, float)):
            xs = [r[k] for r in runs_m if not (isinstance(r[k], float) and math.isnan(r[k]))]
            if xs:
                mean = sum(xs) / len(xs)
                std = statistics.stdev(xs) if len(xs) > 1 else 0.0
                out[k] = [mean, std]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred")
    ap.add_argument("--pred-as-gt", action="store_true")
    ap.add_argument("--gt", required=True)
    ap.add_argument("--ids", default=None)
    ap.add_argument("--asr", default=None)
    ap.add_argument("--budgets", default="orig,oracle", help="comma list: orig, oracle, none")
    ap.add_argument("--random", type=int, default=0)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    ids = None
    if args.ids:
        with open(args.ids, encoding="utf-8-sig") as f:
            ids = {line.strip() for line in f if line.strip()}
    gt = load_gt_chunks(args.gt, ids)
    if args.pred_as_gt:
        preds = {vid: [[s, e, 1.0] for s, e in g["segments"]] for vid, g in gt.items()}
    else:
        if not args.pred:
            ap.error("--pred or --pred-as-gt required")
        preds = load_predictions(args.pred)
        if ids:
            preds = {v: s for v, s in preds.items() if v in ids}

    results = {"gt_file": args.gt, "pred_file": args.pred, "budgets": {}}
    for b in args.budgets.split(","):
        b = b.strip()
        results["budgets"][b] = evaluate(preds, gt, asr_dir=args.asr, budget=None if b == "none" else b,
                                         random_runs=args.random)
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    print(json.dumps(results["budgets"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
