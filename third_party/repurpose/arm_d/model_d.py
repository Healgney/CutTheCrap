"""Arm D / D+: sentence-span proposal scoring on top of the arm A encoder.

The MMCTransformer encoder and its per-second auxiliary losses (uni/multi focal,
KL) are kept unchanged from arm A; only the boundary head differs. Arm A
regresses (left, right) offsets per second; arm D scores precomputed
sentence-span proposals (arm_d/build_proposals.py), and D+ additionally
regresses a residual of at most +-RESID_MAX seconds on each proposal boundary.
"""
import os
import sys

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dataset.RepurposeClip import RepurposeClip, RepurposeClipTest, collate_fn, collate_fn_test  # noqa: E402
from models.MMCTransformer import MMCTransformer  # noqa: E402
from models.losses import sigmoid_focal_loss, kl_divergence_loss  # noqa: E402

RESID_MAX = 1.0
POS_LO, POS_HI = 0.3, 0.7   # soft target ramps from 0 at IoU 0.3 to 1 at IoU 0.7
N_EXTRA = 5


# ---------------------------------------------------------------- data

def _load_props(prop_dir, idx):
    z = np.load(os.path.join(prop_dir, f"{idx}.npz"))
    return {k: torch.from_numpy(z[k]) for k in z.files}


class PropTrain(RepurposeClip):
    def __init__(self, prop_dir, **kw):
        super().__init__(**kw)
        self.prop_dir = prop_dir

    def __getitem__(self, idx):
        d = super().__getitem__(idx)
        d["props"] = _load_props(self.prop_dir, idx)
        return d


class PropTest(RepurposeClipTest):
    def __init__(self, prop_dir, **kw):
        super().__init__(**kw)
        self.prop_dir = prop_dir

    def __getitem__(self, idx):
        d = super().__getitem__(idx)
        d["props"] = _load_props(self.prop_dir, idx)
        return d


def collate_train(batch):
    out = collate_fn(batch)
    out["props"] = [b["props"] for b in batch]
    return out


def collate_test(batch):
    out = collate_fn_test(batch)
    out["props"] = [b["props"] for b in batch]
    return out


# ---------------------------------------------------------------- model

class Encoder(MMCTransformer):
    """MMCTransformer whose forward also returns the fused per-second features."""

    def forward(self, batch):
        masks = batch["masks"]
        vis = self.vis_encoder(batch["visual_feats"], masks)
        aud = self.aud_encoder(batch["audio_feats"], masks)
        txt = self.text_encoder(batch["text_feats"], masks)
        for layer in self.vis_text_croos_att:
            vis = layer(vis, txt, masks)
        for layer in self.aud_text_croos_att:
            aud = layer(aud, txt, masks)
        for layer in self.vis_aud_cross_att:
            vis = layer(vis, aud, masks)
        for layer in self.aud_vis_cross_att:
            aud = layer(aud, vis, masks)
        feats = self.feature_map(torch.cat((vis, aud), dim=2))
        aux = (masks, self.cls_head(feats), self.vis_cls_head(vis), self.aud_cls_head(aud))
        return feats, aux


def mlp(i, h, o):
    return nn.Sequential(nn.Linear(i, h), nn.GELU(), nn.Linear(h, h), nn.GELU(), nn.Linear(h, o))


class ArmD(nn.Module):
    def __init__(self, **model_cfg):
        super().__init__()
        self.enc = Encoder(**model_cfg)
        d = model_cfg["d_model"]
        self.extra_proj = nn.Linear(N_EXTRA, 64)
        self.scorer = mlp(3 * d + 64, 512, 1)
        self.resid = mlp(3 * d + 64, 256, 2)

    @staticmethod
    def _interp(Fm, t):
        T = Fm.shape[0]
        t = t.clamp(0, T - 1)
        lo = t.floor().long().clamp(0, T - 1)
        hi = (lo + 1).clamp(max=T - 1)
        w = (t - lo.float()).unsqueeze(1)
        return Fm[lo] * (1 - w) + Fm[hi] * w

    def prop_features(self, Fm, p):
        """Fm [T, d] features of one chunk; p proposal dict. Returns [P, 3d+64]."""
        T = Fm.shape[0]
        S, E = p["S"].to(Fm.device).float(), p["E"].to(Fm.device).float()
        C = torch.cat([Fm.new_zeros(1, Fm.shape[1]), Fm.float().cumsum(0)], 0)
        s_idx = S.floor().long().clamp(0, T - 1)
        e_idx = torch.maximum(E.ceil().long(), s_idx + 1).clamp(max=T)
        mean = (C[e_idx] - C[s_idx]) / (e_idx - s_idx).unsqueeze(1).float()
        x = torch.cat([self._interp(Fm, S), self._interp(Fm, E), mean.to(Fm.dtype),
                       self.extra_proj(p["extra"].to(Fm.device).to(Fm.dtype))], 1)
        return x

    def forward(self, batch):
        feats, aux = self.enc(batch)
        logits, resid = [], []
        for b, p in enumerate(batch["props"]):
            L = int(batch["duration"][b])
            if len(p["S"]) == 0:
                logits.append(feats.new_zeros(0))
                resid.append(feats.new_zeros(0, 2))
                continue
            x = self.prop_features(feats[b, :L], p)
            logits.append(self.scorer(x).squeeze(1))
            resid.append(RESID_MAX * torch.tanh(self.resid(x)))
        return logits, resid, aux

    def losses(self, logits, resid, aux, batch):
        # per-second auxiliary losses, identical to arm A minus its offset regression
        masks, cls, vcls, acls = aux
        gt = batch["labels"].unsqueeze(-1)
        m = masks.transpose(1, 2).contiguous()
        uni = ((sigmoid_focal_loss(vcls, gt) + sigmoid_focal_loss(acls, gt)) * m).sum()
        mul = (sigmoid_focal_loss(cls, gt) * m).sum()
        kl = kl_divergence_loss(vcls, cls, m) + kl_divergence_loss(acls, cls, m)
        aux_l = {"uni_focal_loss": uni, "mul_focal_loss": mul, "kl_loss": kl}
        prop_l, res_l, n = cls.new_zeros((), dtype=torch.float32), cls.new_zeros((), dtype=torch.float32), 0
        for lg, rs, p in zip(logits, resid, batch["props"]):
            if len(lg) == 0:
                continue
            iou = p["iou"].to(lg.device)
            tgt = ((iou - POS_LO) / (POS_HI - POS_LO)).clamp(0, 1)
            tgt = torch.where(p["force"].to(lg.device), tgt.clamp(min=0.5), tgt)
            pos = tgt > 0
            w = torch.where(pos, 0.5 / pos.sum().clamp(min=1), 0.5 / (~pos).sum().clamp(min=1))
            prop_l = prop_l + (F.binary_cross_entropy_with_logits(lg.float(), tgt, reduction="none") * w).sum()
            sel = iou >= 0.5
            if sel.any():
                target = torch.stack([p["ds"], p["de"]], 1).to(lg.device)[sel].clamp(-RESID_MAX, RESID_MAX)
                res_l = res_l + F.smooth_l1_loss(rs[sel].float(), target, beta=0.25)
            n += 1
        n = max(n, 1)
        return {"uni_focal_loss": aux_l["uni_focal_loss"], "mul_focal_loss": aux_l["mul_focal_loss"],
                "kl_loss": aux_l["kl_loss"], "prop_loss": prop_l / n, "resid_loss": res_l / n}

    @torch.no_grad()
    def inference(self, batch, test_cfg, refine):
        """Returns per chunk {'segments': [K, 2] tensor, 'scores': [K]} in chunk seconds."""
        from models.softnms import soft_nms_intervals_cpu
        logits, resid, _ = self.forward(batch)
        out = []
        for b, (lg, rs, p) in enumerate(zip(logits, resid, batch["props"])):
            vlen = int(batch["duration"][b])
            k = int(np.ceil((vlen // 60) * test_cfg["max_seg_per_min"]))
            if len(lg) == 0 or k == 0:
                out.append({"segments": torch.zeros(0, 2), "scores": torch.zeros(0)})
                continue
            S, E = p["S"].float(), p["E"].float()
            if refine:
                r = rs.float().cpu()
                S, E = S + r[:, 0], E + r[:, 1]
                S, E = S.clamp(0, vlen), torch.maximum(E.clamp(0, vlen), S + 1.0)
            sc = lg.float().sigmoid().cpu()
            top = sc.argsort(descending=True)[: test_cfg.get("pre_nms_topk", 1000)]
            segs, sc = torch.stack([S, E], 1)[top], sc[top]
            keep = soft_nms_intervals_cpu(sc, segs, sigma=test_cfg["nms_sigma"],
                                          thresh=test_cfg["min_score"], max_seg_num=k)
            out.append({"segments": segs[keep], "scores": sc[keep]})
        return out
