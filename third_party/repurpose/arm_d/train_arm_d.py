#!/usr/bin/env python3
"""Arm D / D+ training. Same data, batching, optimizer, schedule, epochs and
checkpoint selection (avg orig tIoU on the sel split) as arm_a/train_arm_a.py;
only the boundary head and its losses differ (arm_d/model_d.py).

Usage (from third_party/repurpose):
  python arm_d/train_arm_d.py --config_path arm_d/config_arm_d.yaml --seed 1234 --amp
"""
import argparse
import os
import sys
import time

import torch
import yaml
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import LambdaLR, CosineAnnealingLR

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "arm_a"))
from train_arm_a import LengthBucketBatchSampler, seed_everything, load_config  # noqa: E402
from utils.metrics import calculate_tiou  # noqa: E402
from model_d import ArmD, PropTrain, PropTest, collate_train, collate_test  # noqa: E402

W = {"uni_focal_loss": 0.1, "mul_focal_loss": 0.3, "kl_loss": 0.1}   # arm A weights, per batch item
W_PROP, W_RESID = 1.0, 0.5                                           # per chunk (already averaged)


def to_cuda(batch):
    for k in ("visual_feats", "audio_feats", "text_feats", "masks", "labels", "segments"):
        if k in batch:
            batch[k] = batch[k].to("cuda")
    return batch


@torch.no_grad()
def evaluate_tiou(model, loader, test_cfg, amp, refine):
    model.eval()
    th = [0.5, 0.6, 0.7, 0.8, 0.9]
    per = []
    for batch in loader:
        batch = to_cuda(batch)
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=amp):
            preds = model.inference(batch, test_cfg, refine=refine)
        for i, p in enumerate(preds):
            per.append(calculate_tiou(batch["gt_segments"][i], p["segments"].float().tolist(), th))
    t = {x: sum(c[x] for c in per) / len(per) for x in th}
    return sum(t.values()) / len(t), t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config_path", required=True)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--amp", action="store_true")
    ap.add_argument("--epochs", type=int, default=None, help="override (smoke tests only)")
    ap.add_argument("--limit", type=int, default=None, help="use first N train chunks (smoke tests only)")
    args = ap.parse_args()
    cfg = load_config(args.config_path)
    seed = args.seed if args.seed is not None else cfg["train"]["seed"]
    seed_everything(seed)

    ckpt_dir = time.strftime(f"arm_d/ckpt_seed{seed}_%Y%m%d_%H%M%S")
    os.makedirs(ckpt_dir, exist_ok=True)
    with open(os.path.join(ckpt_dir, "config.yaml"), "w") as f:
        yaml.dump(cfg, f)
    log_path = os.path.join(ckpt_dir, "train_log.txt")

    def log(msg):
        print(msg, flush=True)
        with open(log_path, "a") as f:
            f.write(msg + "\n")

    train_ds = PropTrain(prop_dir=os.path.join(cfg["prop_dir"], "train"), **cfg["train_dataset"])
    sel_ds = PropTest(prop_dir=os.path.join(cfg["prop_dir"], "sel"), **cfg["sel_dataset"])
    if args.limit:
        train_ds.label = train_ds.label[: args.limit]
    log(f"arm D training, seed={seed}, dir={ckpt_dir}; train chunks {len(train_ds)}, sel chunks {len(sel_ds)}")

    model = ArmD(**cfg["model"]).to("cuda")
    tc = cfg["train"]
    epochs = args.epochs or tc["epochs"]
    lengths = [int(e["timeRangeOffset"][1]) - int(e["timeRangeOffset"][0]) + 1 for e in train_ds.label]
    sampler = LengthBucketBatchSampler(lengths, ref_batch=tc["batch_size"], ref_len=1800, seed=seed)
    train_loader = DataLoader(train_ds, batch_sampler=sampler, collate_fn=collate_train,
                              num_workers=tc.get("num_workers", 4))
    sel_loader = DataLoader(sel_ds, batch_size=1, shuffle=False, collate_fn=collate_test,
                            num_workers=tc.get("num_workers", 4))

    opt = torch.optim.Adam(model.parameters(), lr=tc["lr"], weight_decay=tc["weight_decay"])
    n_it = len(train_loader)
    warm = tc["warmup_epochs"] * n_it
    warm_s = LambdaLR(opt, lr_lambda=lambda s: (s + 1) / warm if (s + 1) <= warm else 1)
    cos_s = CosineAnnealingLR(opt, T_max=epochs * n_it)

    best, best_ep, step = -1.0, -1, 0
    for ep in range(epochs):
        model.train()
        tot = {k: 0.0 for k in ("total", "mul", "prop", "resid")}
        t0 = time.time()
        for batch in train_loader:
            batch = to_cuda(batch)
            bs = len(batch["video_id"])
            with torch.autocast("cuda", dtype=torch.bfloat16, enabled=args.amp):
                logits, resid, aux = model(batch)
                L = model.losses(logits, resid, aux, batch)
            loss = sum(W[k] * L[k] for k in W) / bs + W_PROP * L["prop_loss"] + W_RESID * L["resid_loss"]
            opt.zero_grad()
            loss.backward()
            opt.step()
            (warm_s if step < warm else cos_s).step()
            step += 1
            tot["total"] += loss.item()
            tot["mul"] += L["mul_focal_loss"].item() / bs
            tot["prop"] += L["prop_loss"].item()
            tot["resid"] += L["resid_loss"].item()
        log(f"Epoch {ep+1}/{epochs} ({time.time()-t0:.1f}s) " +
            ", ".join(f"{k} {v/n_it:.4f}" for k, v in tot.items()))
        state = {"model": model.state_dict(), "epoch": ep, "seed": seed}
        torch.save(state, os.path.join(ckpt_dir, "last.pth"))
        avg, t = evaluate_tiou(model, sel_loader, cfg["test_cfg"], args.amp, refine=True)
        mark = ""
        if avg > best:
            best, best_ep = avg, ep
            torch.save(state, os.path.join(ckpt_dir, "best.pth"))
            mark = "  <- best"
        log(f"  sel tIoU (D+): {t}, avg {avg:.4f} (best {best:.4f} @ epoch {best_ep}){mark}")
    log(f"DONE seed={seed}, best avg tIoU {best:.4f} @ epoch {best_ep}, best.pth saved")


if __name__ == "__main__":
    main()
