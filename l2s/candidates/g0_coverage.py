"""G0 gate: do human-refined GT clip boundaries land on candidate cut points?

Reports, per candidate type (sent / pause / shot / union) and per boundary side
(start / end), the fraction of GT boundaries within +-0.5 / 1 / 2 s of a candidate,
against a density-matched uniform-random control. Also reports the GT mid-sentence
rate. Spec: docs/07-server-handoff.md, P4.

Sentence and pause candidates are recomputed here from the WhisperX output so the
definition is fixed by this script. Shot candidates are read from the candidates
file via load_shots(); adapt that one function if the schema differs.

Usage:
  python l2s/candidates/g0_coverage.py \
    --labels $REPURPOSE_SRC/data/test.json \
    --ids eval/paper/splits/test_clean_ids.txt \
    --asr $L2S_ASR --cands $L2S_DATA/candidates --out reports/P4
"""
import argparse
import json
import os
from collections import defaultdict

import numpy as np

TOLS = (0.5, 1.0, 2.0)
PAUSE_MIN = 0.3   # gap between words that counts as a pause (s)
DEDUP = 0.2       # union candidates closer than this are merged (s)
WORD_MARGIN = 0.05
SENT_FAR = 1.0    # boundary farther than this from any sentence edge = mid-sentence
N_RANDOM = 10


def load_asr(path):
    with open(path, encoding="utf-8") as f:
        asr = json.load(f)
    sents, words = [], []
    for seg in asr.get("segments", []):
        if "start" in seg and "end" in seg:
            sents.append((float(seg["start"]), float(seg["end"])))
        for w in seg.get("words", []):
            if "start" in w and "end" in w:  # WhisperX leaves numerals unaligned
                words.append((float(w["start"]), float(w["end"])))
    words.sort()
    return sents, words, asr.get("language", "unknown")


def load_shots(path):
    """Return a list of shot-cut times (s). Adapt to the candidates file schema."""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        c = json.load(f)
    if isinstance(c, dict):
        for key in ("shot", "shots", "shot_cuts"):
            if key in c:
                return [float(x["t"] if isinstance(x, dict) else x) for x in c[key]]
        if "candidates" in c:
            c = c["candidates"]
    if isinstance(c, list) and c and isinstance(c[0], dict):
        tkey = "t" if "t" in c[0] else "time"
        kkey = "type" if "type" in c[0] else "kind"
        return [float(x[tkey]) for x in c if x.get(kkey) == "shot"]
    raise ValueError(f"Unknown candidates schema in {path}: adapt load_shots()")


def candidates(sents, words, shots):
    starts = {"sent": [s for s, _ in sents], "pause": [], "shot": list(shots)}
    ends = {"sent": [e for _, e in sents], "pause": [], "shot": list(shots)}
    for (_, e0), (s1, _) in zip(words, words[1:]):
        if s1 - e0 >= PAUSE_MIN:
            mid = (e0 + s1) / 2
            starts["pause"].append(mid)
            ends["pause"].append(mid)
    for side in (starts, ends):
        allp = np.sort(np.array(side["sent"] + side["pause"] + side["shot"]))
        keep = [t for i, t in enumerate(allp) if i == 0 or t - allp[i - 1] > DEDUP]
        side["union"] = keep
        for k in side:
            side[k] = np.sort(np.asarray(side[k], dtype=float))
    return starts, ends


def nearest_dist(points, cands):
    if len(cands) == 0:
        return np.full(len(points), np.inf)
    idx = np.searchsorted(cands, points)
    lo = cands[np.clip(idx - 1, 0, len(cands) - 1)]
    hi = cands[np.clip(idx, 0, len(cands) - 1)]
    return np.minimum(np.abs(points - lo), np.abs(points - hi))


def mid_sentence(t, sents, words):
    for ws, we in words:
        if ws + WORD_MARGIN < t < we - WORD_MARGIN:
            return True
    if not sents:
        return False
    edges = np.array([x for s in sents for x in s])
    return bool(np.min(np.abs(edges - t)) > SENT_FAR)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", required=True)
    ap.add_argument("--ids", required=True)
    ap.add_argument("--asr", required=True)
    ap.add_argument("--cands", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)

    with open(a.ids, encoding="utf-8-sig") as f:
        ids = {l.strip() for l in f if l.strip()}
    with open(a.labels, encoding="utf-8") as f:
        labels = [e for e in json.load(f) if e["youtube_id"] in ids]

    dists = defaultdict(list)       # (side, type) -> distances
    rand = defaultdict(list)        # (side, tol) -> random coverage per chunk
    midsent = {"start": [], "end": []}
    density, langs, used, skipped = [], defaultdict(int), set(), defaultdict(int)

    for e in labels:
        vid = e["youtube_id"]
        asr_p = os.path.join(a.asr, f"{vid}.json")
        if not os.path.exists(asr_p):
            skipped["no_asr"] += 1
            continue
        sents, words, lang = load_asr(asr_p)
        shots = load_shots(os.path.join(a.cands, f"{vid}.json"))
        t0, t1 = map(float, e["timeRange"])
        starts, ends = candidates(sents, words, shots)
        if vid not in used:
            langs[lang] += 1
            used.add(vid)
        segs = np.array(e["segments"], dtype=float)  # absolute seconds
        for side, col, cand in (("start", 0, starts), ("end", 1, ends)):
            pts = segs[:, col]
            for k, c in cand.items():
                c = c[(c >= t0 - 2) & (c <= t1 + 2)]
                dists[(side, k)].extend(nearest_dist(pts, c).tolist())
            cu = cand["union"]
            n = int(((cu >= t0) & (cu <= t1)).sum())
            for _ in range(N_RANDOM):
                r = np.sort(rng.uniform(t0, t1, n))
                d = nearest_dist(pts, r)
                for tol in TOLS:
                    rand[(side, tol)].append(float((d <= tol).mean()))
            midsent[side].extend(mid_sentence(t, sents, words) for t in pts)
        dur_min = max((t1 - t0) / 60, 1e-6)
        density.append(int(((starts["union"] >= t0) & (starts["union"] <= t1)).sum()) / dur_min)

    res = {"n_chunks": len(labels) - sum(skipped.values()), "n_videos": len(used),
           "skipped": dict(skipped), "languages": dict(langs),
           "union_candidates_per_min": {"mean": float(np.mean(density)), "median": float(np.median(density))},
           "coverage": {}, "random_coverage": {}, "gt_midsentence_rate": {}}
    for (side, k), d in sorted(dists.items()):
        d = np.asarray(d)
        res["coverage"][f"{side}/{k}"] = {f"{tol}s": float((d <= tol).mean()) for tol in TOLS}
    for side in ("start", "end"):
        res["random_coverage"][side] = {f"{tol}s": float(np.mean(rand[(side, tol)])) for tol in TOLS}
        res["gt_midsentence_rate"][side] = float(np.mean(midsent[side]))

    cu1 = min(res["coverage"]["start/union"]["1.0s"], res["coverage"]["end/union"]["1.0s"])
    rd1 = max(res["random_coverage"]["start"]["1.0s"], res["random_coverage"]["end"]["1.0s"])
    res["gate"] = {"union_cov_1s_min": cu1, "random_cov_1s_max": rd1,
                   "meets_start_values": bool(cu1 >= 0.8 and rd1 <= 0.5)}

    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "g0.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)

    lines = ["# G0 候选覆盖率", "",
             f"结论：需要人判断（起始阈值{'满足' if res['gate']['meets_start_values'] else '未满足'}：union ±1 s 覆盖率 {cu1:.3f}，随机对照 {rd1:.3f}）", "",
             f"块数 {res['n_chunks']}，视频数 {res['n_videos']}，跳过 {dict(skipped)}；union 候选密度中位 {res['union_candidates_per_min']['median']:.1f} 个/分钟", "",
             "| 边界/类型 | ±0.5 s | ±1 s | ±2 s |", "|---|---|---|---|"]
    for key, v in res["coverage"].items():
        lines.append(f"| {key} | {v['0.5s']:.3f} | {v['1.0s']:.3f} | {v['2.0s']:.3f} |")
    for side, v in res["random_coverage"].items():
        lines.append(f"| {side}/random（同密度） | {v['0.5s']:.3f} | {v['1.0s']:.3f} | {v['2.0s']:.3f} |")
    lines += ["", f"GT 句中率：起点 {res['gt_midsentence_rate']['start']:.3f}，终点 {res['gt_midsentence_rate']['end']:.3f}",
              "", f"语言分布（视频数）：{dict(langs)}", "", "等待审核"]
    with open(os.path.join(a.out, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
