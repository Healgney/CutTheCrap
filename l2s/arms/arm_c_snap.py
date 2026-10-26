#!/usr/bin/env python3
"""Arm C: snap arm A predictions to the nearest ASR sentence boundary.

Start -> nearest sentence start, end -> nearest sentence end, each within
+-WINDOW seconds; no candidate in the window leaves the boundary unchanged.
Scores, clip count and order are untouched. Spec: docs/07-server-handoff.md
(10-25 revision: sentence candidates only).

Usage:
  python l2s/arms/arm_c_snap.py --pred arm_a_seed1234.json --asr $L2S_ASR --out arm_c_seed1234.json
"""
import argparse
import bisect
import json
import os

WINDOW = 3.0


def nearest(sorted_ts, t):
    k = bisect.bisect_left(sorted_ts, t)
    best = None
    for c in sorted_ts[max(0, k - 1): k + 1]:
        if abs(c - t) <= WINDOW and (best is None or abs(c - t) < abs(best - t)):
            best = c
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", required=True, help="{vid: [[s, e, score], ...]} absolute seconds")
    ap.add_argument("--asr", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    preds = json.load(open(a.pred, encoding="utf-8"))
    out, n, snapped = {}, {"start": 0, "end": 0}, {"start": 0, "end": 0}
    for vid, segs in preds.items():
        p = os.path.join(a.asr, f"{vid}.json")
        sents = []
        if os.path.exists(p):
            sents = [(float(s["start"]), float(s["end"])) for s in json.load(open(p, encoding="utf-8")).get("segments", [])
                     if "start" in s and "end" in s]
        starts = sorted(s for s, _ in sents)
        ends = sorted(e for _, e in sents)
        res = []
        for s, e, sc in segs:
            ns, ne = nearest(starts, s), nearest(ends, e)
            n["start"] += 1
            n["end"] += 1
            snapped["start"] += ns is not None
            snapped["end"] += ne is not None
            res.append([ns if ns is not None else s, ne if ne is not None else e, sc])
        out[vid] = res
    json.dump(out, open(a.out, "w", encoding="utf-8"))
    stats = {side: {"snapped": snapped[side], "total": n[side], "rate": snapped[side] / max(n[side], 1)} for side in n}
    json.dump(stats, open(a.out.replace(".json", "_snap_stats.json"), "w"), indent=2)
    print(json.dumps(stats))


if __name__ == "__main__":
    main()
