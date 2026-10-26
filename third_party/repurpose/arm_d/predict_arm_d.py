#!/usr/bin/env python3
"""Arm D / D+ prediction export, same output format as arm_a/predict_arm_a.py:
  <out>_d.json, <out>_dplus.json        {vid: [[start, end, score], ...]} absolute seconds
  <out>_d_chunks.json, <out>_dplus_chunks.json

Usage (from third_party/repurpose):
  python arm_d/predict_arm_d.py --config_path arm_d/config_arm_d.yaml \
    --resume arm_d/ckpt_.../best.pth --out arm_d/preds/arm_d_seed1234
"""
import argparse
import json
import os
import sys

import torch
import yaml
from torch.utils.data import DataLoader

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from model_d import ArmD, PropTest, collate_test  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config_path", required=True)
    ap.add_argument("--resume", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--split", default="test_clean")
    ap.add_argument("--amp", action="store_true")
    a = ap.parse_args()
    cfg = yaml.load(open(a.config_path), Loader=yaml.FullLoader)
    ds_cfg = dict(cfg["sel_dataset"])
    ds_cfg["label_path"] = os.path.join(os.path.dirname(ds_cfg["label_path"]), f"{a.split}.json")
    ds = PropTest(prop_dir=os.path.join(cfg["prop_dir"], a.split), **ds_cfg)
    loader = DataLoader(ds, batch_size=1, shuffle=False, collate_fn=collate_test, num_workers=4)

    model = ArmD(**cfg["model"]).to("cuda")
    model.load_state_dict(torch.load(a.resume, map_location="cuda")["model"])
    model.eval()

    res = {"d": ([], {}), "dplus": ([], {})}
    with torch.no_grad():
        for entry, batch in zip(ds.label, loader):
            for k in ("visual_feats", "audio_feats", "text_feats", "masks"):
                batch[k] = batch[k].to("cuda")
            for name, refine in (("d", False), ("dplus", True)):
                with torch.autocast("cuda", dtype=torch.bfloat16, enabled=a.amp):
                    p = model.inference(batch, cfg["test_cfg"], refine=refine)[0]
                off = entry["timeRange"][0]
                segs = [[float(s[0]) + off, float(s[1]) + off, float(sc)]
                        for s, sc in zip(p["segments"].tolist(), p["scores"].tolist())]
                chunks, per_vid = res[name]
                chunks.append({"video_id": entry["youtube_id"], "chunk_start": off,
                               "duration": entry["timeRange"][1] - entry["timeRange"][0], "segments": segs})
                per_vid.setdefault(entry["youtube_id"], []).extend(segs)

    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    for name, (chunks, per_vid) in res.items():
        json.dump(chunks, open(f"{a.out}_{name}_chunks.json", "w"))
        json.dump(per_vid, open(f"{a.out}_{name}.json", "w"))
        print(f"wrote {a.out}_{name}.json: {len(per_vid)} videos, {sum(len(v) for v in per_vid.values())} segments")


if __name__ == "__main__":
    main()
