#!/usr/bin/env python3
"""Arm D: build sentence-span proposals for every chunk of the arm A label files.

A proposal is (start of ASR sentence i, end of ASR sentence j), j >= i, with
duration in [MIN_DUR, MAX_DUR] seconds. Times are chunk-relative, on the same
grid as the RepurposeClip datasets (feature row k = second k of the chunk).
Spec: docs/07-server-handoff.md, 10-27 revision.

Per chunk, writes <out>/<split>/<idx>.npz with
  S, E          proposal start / end (s)
  extra         [P, 5]: log duration, pause before start, pause after end,
                shot cut within 0.5 s of start, shot cut within 0.5 s of end
  iou           [P] max IoU with any GT segment (train/sel only)
  ds, de        [P] GT start/end minus proposal start/end for the argmax GT
  force         [P] bool, best proposal of each GT (if its IoU >= 0.3)
and prints proposal recall (fraction of GT segments whose best proposal
reaches IoU 0.5 / 0.7), which is the ceiling for arm D.

Usage (from third_party/repurpose):
  python arm_d/build_proposals.py --labels-dir arm_a/labels \
    --asr-dir ~/l2s_cache/asr --cands-dir ~/l2s_cache/candidates \
    --feat-dir ~/l2s_cache/features/clip --out-dir ~/l2s_cache/arm_d_props
"""
import argparse
import json
import os

import numpy as np

MIN_DUR, MAX_DUR = 15.0, 90.0
GAP_CAP = 5.0
SHOT_TOL = 0.5


def feat_rows(path):
    with open(path, "rb") as f:
        ver = np.lib.format.read_magic(f)
        shape, _, _ = np.lib.format._read_array_header(f, ver)
    return shape[0]


def chunk_len(entry, rows):
    """Sequence length the RepurposeClip datasets will produce for this chunk."""
    t0, t1 = entry["timeRange"]
    n_labels = int(t1 - t0) + 1
    n_feats = rows if t0 == 0 else max(0, min(int(t1), rows) - int(t0))
    return min(n_feats, n_labels)


def iou_matrix(S, E, G):
    inter = np.clip(np.minimum(E[:, None], G[None, :, 1]) - np.maximum(S[:, None], G[None, :, 0]), 0, None)
    union = (E - S)[:, None] + (G[:, 1] - G[:, 0])[None, :] - inter
    return inter / np.maximum(union, 1e-6)


def build_chunk(entry, asr, shots, L):
    t0 = float(entry["timeRange"][0])
    sents = [(s["start"] - t0, s["end"] - t0) for s in asr.get("segments", [])
             if "start" in s and "end" in s]
    sents = sorted((s, e) for s, e in sents if s >= 0 and e <= L - 1e-3 and e > s)
    if not sents:
        return None
    ss = np.array([s for s, _ in sents], dtype=np.float32)
    ee = np.array([e for _, e in sents], dtype=np.float32)
    ee = np.maximum.accumulate(ee)  # guard against rare overlapping segments
    n = len(ss)
    prev_gap = np.full(n, GAP_CAP, np.float32)
    prev_gap[1:] = np.clip(ss[1:] - ee[:-1], 0, GAP_CAP)
    next_gap = np.full(n, GAP_CAP, np.float32)
    next_gap[:-1] = np.clip(ss[1:] - ee[:-1], 0, GAP_CAP)

    I, J = [], []
    for i in range(n):
        lo = np.searchsorted(ee, ss[i] + MIN_DUR, side="left")
        hi = np.searchsorted(ee, ss[i] + MAX_DUR, side="right")
        lo = max(lo, i)
        if hi > lo:
            I.append(np.full(hi - lo, i))
            J.append(np.arange(lo, hi))
    if not I:
        return None
    I = np.concatenate(I)
    J = np.concatenate(J)
    S, E = ss[I], ee[J]

    sh = np.sort(np.asarray([t - t0 for t in shots if 0 <= t - t0 <= L], dtype=np.float32))

    def near_shot(t):
        if len(sh) == 0:
            return np.zeros(len(t), np.float32)
        k = np.searchsorted(sh, t)
        lo = sh[np.clip(k - 1, 0, len(sh) - 1)]
        hi = sh[np.clip(k, 0, len(sh) - 1)]
        d = np.minimum(np.abs(lo - t), np.abs(hi - t))
        return (d <= SHOT_TOL).astype(np.float32)

    extra = np.stack([np.log(E - S), prev_gap[I], next_gap[J], near_shot(S), near_shot(E)], 1).astype(np.float32)
    out = {"S": S, "E": E, "extra": extra}

    G = np.asarray(entry.get("segmentsOffset", []), dtype=np.float32).reshape(-1, 2)
    if len(G):
        M = iou_matrix(S, E, G)
        arg = M.argmax(1)
        out["iou"] = M.max(1).astype(np.float32)
        out["ds"] = (G[arg, 0] - S).astype(np.float32)
        out["de"] = (G[arg, 1] - E).astype(np.float32)
        force = np.zeros(len(S), bool)
        best = M.argmax(0)
        force[best[M[best, np.arange(len(G))] >= 0.3]] = True
        out["force"] = force
        out["gt_best"] = M.max(0).astype(np.float32)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels-dir", required=True)
    ap.add_argument("--asr-dir", required=True)
    ap.add_argument("--cands-dir", required=True)
    ap.add_argument("--feat-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--splits", default="train,sel,test_clean")
    a = ap.parse_args()

    for split in a.splits.split(","):
        labels = json.load(open(os.path.join(a.labels_dir, f"{split}.json"), encoding="utf-8"))
        od = os.path.join(a.out_dir, split)
        os.makedirs(od, exist_ok=True)
        n_props, empty, gt_best = [], 0, []
        cache = {}
        for idx, e in enumerate(labels):
            vid = e["youtube_id"]
            if vid not in cache:
                ap_ = os.path.join(a.asr_dir, f"{vid}.json")
                asr = json.load(open(ap_, encoding="utf-8")) if os.path.exists(ap_) else {}
                cp = os.path.join(a.cands_dir, f"{vid}.json")
                shots = json.load(open(cp, encoding="utf-8")).get("points", {}).get("shot", []) if os.path.exists(cp) else []
                cache = {vid: (asr, shots)}
            asr, shots = cache[vid]
            L = chunk_len(e, feat_rows(os.path.join(a.feat_dir, f"{vid}.npy")))
            out = build_chunk(e, asr, shots, L)
            if out is None:
                empty += 1
                out = {"S": np.zeros(0, np.float32), "E": np.zeros(0, np.float32),
                       "extra": np.zeros((0, 5), np.float32)}
            np.savez(os.path.join(od, f"{idx}.npz"), **out)
            n_props.append(len(out["S"]))
            if "gt_best" in out:
                gt_best.extend(out["gt_best"].tolist())
            elif len(e.get("segmentsOffset", [])):
                gt_best.extend([0.0] * len(e["segmentsOffset"]))
        gb = np.asarray(gt_best)
        msg = (f"{split}: {len(labels)} chunks, proposals/chunk median {int(np.median(n_props))} "
               f"max {max(n_props)}, empty {empty}")
        if len(gb):
            msg += (f"; proposal recall over {len(gb)} GT: IoU>=0.5 {np.mean(gb >= 0.5):.3f}, "
                    f">=0.7 {np.mean(gb >= 0.7):.3f}, >=0.9 {np.mean(gb >= 0.9):.3f}")
        print(msg, flush=True)


if __name__ == "__main__":
    main()
