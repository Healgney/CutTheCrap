# 臂 C / B 实验交接文档

> **目标读者：** 在 GPU 服务器上执行臂 C（回归 + 吸附）和臂 B（大模型零样本）实验的 agent  
> **执行方式：** 顺序执行，每个臂完成后提交报告并停下等审核  
> **前置条件：** P4 G0 已通过；clean test 的 ASR、候选文件和 GT 标注已就绪

---

## §0 执行规则（必读）

### 0.1 停下等人的情况

以下情况**必须停下**，在报告末尾写"等待审核"，不继续：

1. **依赖缺失或格式不符：** 原始预测文件不存在、格式无法解析、候选文件缺失超过 10%。
2. **臂 C 的吸附结果反常：** 吸附后的 bF1@1s 比吸附前**低**超过 0.05（说明候选点或吸附逻辑有问题）。
3. **臂 B 的模型推理失败率 > 20%：** 大模型输出无法解析或拒绝回答的比例过高。
4. **指标计算出现 NaN 或全 0：** 说明评测代码有 bug。
5. **任何需要改动 GT 或特征文件的操作。**

### 0.2 不需要问人的情况

1. **缺少少量视频（< 10%）：** 跳过，在报告里列出缺失 ID 和数量。
2. **候选文件格式需要适配：** 直接改 `load_candidates()` 函数，提交时在 commit message 里注明。
3. **大模型输出格式多样：** 用正则 + 启发式解析，失败的记为无效，报告解析成功率。
4. **评测指标的小调整：** 比如 soft-NMS 的 IoU 阈值、匹配算法，按常规值设定（0.5–0.7），报告里注明。

### 0.3 提交规范

- **一个臂一次提交：** 臂 C 的代码和报告提交一次，臂 B 的提交一次。
- **Commit message 格式：** `[P6 Arm-C] snap regression output to sent boundaries` / `[P6 Arm-B] zero-shot with Qwen2.5-8B on clean test`
- **报告位置：** `reports/P6/arm_c.md` 和 `reports/P6/arm_b.md`，同时输出 `arm_c_metrics.json` 和 `arm_b_metrics.json`
- **代码位置：** `l2s/arms/` 下，文件名 `arm_c_snap.py` 和 `arm_b_zeroshot.py`

---

## §1 臂 C：回归 + 吸附到句子边界

### 1.1 输入

| 项 | 路径 | 说明 |
|---|---|---|
| 臂 A 的原始预测 | 需要找或生成 | Repurpose-10K 仓库可能自带作者的预测结果；找不到就先复现臂 A（见 §1.7） |
| 句子候选 | `$L2S_ASR/{id}.json` | WhisperX 输出的 `segments[].start/end` |
| GT 标注 | `$REPURPOSE_SRC/data/test.json` | 原始划分（和 11.57 对比）和 clean test（主实验） |

### 1.2 算法

对臂 A 预测的每个 clip `(pred_start, pred_end, score)`：

1. **提取该视频的句子候选：**
   - 句首候选 = `[seg["start"] for seg in segments]`
   - 句尾候选 = `[seg["end"] for seg in segments]`
2. **吸附规则：**
   - `pred_start` 吸附到 ±3 秒内最近的句首候选；没有则保持原值
   - `pred_end` 吸附到 ±3 秒内最近的句尾候选；没有则保持原值
3. **保持原分数和原数量：** 吸附只改起止点，不改 `score`，不增删 clip
4. **输出格式和臂 A 一致：** 每个视频一个预测列表，每个 clip 包含 `(start, end, score)`

### 1.3 评测指标（和臂 A 对比）

评测脚本复用 `l2s/eval/evaluate.py`，输出以下指标并制表对比：

| 指标类别 | 具体指标 | 说明 |
|---|---|---|
| **边界精度（主指标）** | bF1 @ ±{0.5, 1, 2} s | 起点、终点各自单独看，落在 GT 边界 ±k 秒内算对 |
| | 句中切断率 | 起止点落在词内或离句边界 > 1 秒的比例（越低越好） |
| **片段匹配** | R / P / F1 @ IoU {0.5, 0.7, 0.9} | 一对一匹配，按最大 IoU 贪心配对 |
| **原指标** | `orig_tiou`（只算精度的平均 tIoU） | 和 11.57 对比用 |

**对比表格式（Markdown）：**

```markdown
| 指标 | 臂 A（回归） | 臂 C（回归 + 吸附） | Δ |
|---|---|---|---|
| bF1 起点 @1s | 0.xxx | 0.yyy | +0.zzz |
| bF1 终点 @1s | ... | ... | ... |
| 句中切断率 | ... | ... | −0.zzz |
| F1 @0.7 | ... | ... | ... |
| orig_tiou | 11.57 (reported) | ... | ... |
```

### 1.4 预期结果与判断

| 结果 | 含义 | 怎么办 |
|---|---|---|
| 臂 C 的 bF1@1s 比臂 A 高 0.10 以上 | 吸附本身就能显著提升边界精度 | ✅ 符合预期，继续做臂 D；臂 D 要打得更高才有意义 |
| 臂 C 的 bF1@1s 比臂 A 高 0.02–0.10 | 吸附有一点效果，但不强 | ✅ 臂 D 有空间 |
| 臂 C 和臂 A 几乎一样 | GT 本身就不在句边界上，或者臂 A 已经很接近句边界 | ⚠️ 报告后停下等审核 |
| 臂 C 比臂 A **更差** | 候选点或吸附逻辑有问题 | ❌ 报告后停下等审核 |

### 1.5 报告内容（`reports/P6/arm_c.md`）

```markdown
# 臂 C：回归 + 吸附到句子边界

**结论：** [一句话总结：吸附提升了 bF1@1s X 个点]

## 输入

- 臂 A 预测来源：[路径或说明]
- 评测划分：原始 test（和 11.57 对比）、clean test（主实验）
- 句子候选数量：[平均每视频 X 个句首、Y 个句尾]

## 算法

吸附窗口 ±3 秒；起点找句首、终点找句尾；未吸附比例 Z%

## 结果

### 原始 test（和 11.57 对比）

| 指标 | 臂 A | 臂 C | Δ |
|---|---|---|---|
| orig_tiou | 11.57 (reported) | ... | ... |
| ... | ... | ... | ... |

### clean test（主实验）

[主对比表]

## 观察

1. [吸附在哪些指标上有提升]
2. [句中切断率变化]
3. [任何反常现象]

等待审核
```

### 1.6 代码模板（`l2s/arms/arm_c_snap.py`）

```python
"""Arm C: snap regression output to nearest sentence boundaries.

Usage:
  python l2s/arms/arm_c_snap.py \
    --pred_a <path to arm A predictions> \
    --asr $L2S_ASR \
    --labels $REPURPOSE_SRC/data/test.json \
    --out reports/P6/arm_c_preds.json

Output format: same as arm A, {video_id: [(start, end, score), ...]}
"""
import argparse, json, os
import numpy as np

SNAP_WINDOW = 3.0  # seconds

def load_asr_sents(path):
    with open(path, encoding="utf-8") as f:
        asr = json.load(f)
    starts = [s["start"] for s in asr.get("segments", []) if "start" in s]
    ends = [s["end"] for s in asr.get("segments", []) if "end" in s]
    return np.sort(np.array(starts)), np.sort(np.array(ends))

def snap_to_nearest(t, cands, window):
    if len(cands) == 0:
        return t
    idx = np.searchsorted(cands, t)
    near = []
    if idx > 0:
        near.append(cands[idx - 1])
    if idx < len(cands):
        near.append(cands[idx])
    near = [c for c in near if abs(c - t) <= window]
    return min(near, key=lambda c: abs(c - t)) if near else t

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred_a", required=True)
    ap.add_argument("--asr", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    with open(a.pred_a, encoding="utf-8") as f:
        pred_a = json.load(f)  # {vid: [(s, e, score), ...]}
    with open(a.labels, encoding="utf-8") as f:
        gt = {e["youtube_id"]: e for e in json.load(f)}

    snapped = {}
    for vid, clips in pred_a.items():
        asr_p = os.path.join(a.asr, f"{vid}.json")
        if not os.path.exists(asr_p):
            snapped[vid] = clips  # keep original if no ASR
            continue
        starts_c, ends_c = load_asr_sents(asr_p)
        snapped[vid] = [
            (snap_to_nearest(s, starts_c, SNAP_WINDOW),
             snap_to_nearest(e, ends_c, SNAP_WINDOW),
             sc)
            for s, e, sc in clips
        ]

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(snapped, f, indent=2)
    print(f"Snapped predictions written to {a.out}")

if __name__ == "__main__":
    main()
```

### 1.7 如果找不到臂 A 的预测

Repurpose-10K 仓库可能自带作者的预测结果（通常在 `results/` 或 `output/` 下）。找不到就：

1. **先确认：** 在仓库里全局搜 `.json` 或 `.pkl`，看有没有包含 `(start, end, score)` 格式的文件。
2. **实在找不到：** 报告里写"臂 A 预测文件缺失，无法做臂 C"，停下等审核。不要尝试自己复现臂 A，那需要训练。

---

## §2 臂 B：大模型零样本

### 2.1 输入

| 项 | 路径 | 说明 |
|---|---|---|
| 转写 | `$L2S_ASR/{id}.json` | WhisperX 输出，只用 `segments[].text` 拼成全文 |
| 视频时长 | 从 GT 标注推断：`max(seg["end"] for seg in e["segments"])` | 大模型需要知道总时长 |
| GT 标注 | `$REPURPOSE_SRC/data/test.json` | clean test |

### 2.2 模型选择

**推荐优先级：**

1. **Qwen2.5-8B-Instruct**（首选，中英双语都强）
2. **Llama-3.3-8B-Instruct**（备选，纯英语视频用）
3. **Gemma-2-9B-It**（备选）

用 vLLM 跑推理，设置：
- `temperature=0`（确定性输出）
- `max_tokens=512`
- `top_p=1.0`

### 2.3 提示词模板

**System prompt（英语视频）：**

```
You are a video editor. Given a transcript and total duration, identify 2-4 interesting short clips suitable for social media. Each clip should be 15-90 seconds, self-contained (no dangling references), and start/end at sentence boundaries.

Output JSON only, no explanation:
[
  {"start": <seconds>, "end": <seconds>, "reason": "<one-line hook>"},
  ...
]
```

**User prompt：**

```
Transcript:
{transcript}

Total duration: {duration} seconds.

Identify 2-4 clips.
```

**非英语视频：** System prompt 改用该语言（比如法语视频用法语 prompt），或者在英语 prompt 后加一句 `The transcript is in {language}.`

### 2.4 输出解析

大模型输出可能包含：
- 纯 JSON 数组；
- Markdown 代码块 `` ```json ... ``` ``；
- 前后有解释文字；
- 时间格式多样：`"1:23"` / `83` / `"1m23s"`。

**解析策略：**

1. 先尝试整体 `json.loads()`；
2. 失败则提取第一个 `[...]` 或 `{...}` 块再解析；
3. 时间字段统一转成浮点秒数：`"1:23"` → 83.0；
4. 解析失败的样本记为无效，报告解析成功率。

### 2.5 评测指标（和臂 A 对比）

同臂 C，输出表格对比：

```markdown
| 指标 | 臂 A（回归） | 臂 B（大模型零样本） | Δ |
|---|---|---|---|
| bF1 起点 @1s | ... | ... | ... |
| 句中切断率 | ... | ... | ... |
| F1 @0.7 | ... | ... | ... |
| 解析成功率 | — | X% | — |
```

### 2.6 预期结果与判断

| 结果 | 含义 | 怎么办 |
|---|---|---|
| 臂 B 的 bF1@1s 比臂 A 低 0.15 以上 | "只看转写"明显不如多模态 | ✅ 符合预期，证明视觉和音频信号的价值 |
| 臂 B 和臂 A 接近或更高 | 转写信息已经够用，或者臂 A 的多模态融合没做好 | ⚠️ 报告后停下等审核 |
| 解析成功率 < 50% | 提示词或模型不适合 | ⚠️ 报告后停下等审核 |

### 2.7 报告内容（`reports/P6/arm_b.md`）

```markdown
# 臂 B：大模型零样本

**结论：** [一句话总结]

## 设置

- 模型：Qwen2.5-8B-Instruct / vLLM / temperature=0
- 输入：只用转写全文 + 总时长
- 输出：每视频 2–4 个 clip

## 结果

### clean test

| 指标 | 臂 A | 臂 B | Δ |
|---|---|---|---|
| ... | ... | ... | ... |

解析成功率：X%（Y 个视频中有 Z 个输出无法解析）

## 观察

1. [臂 B 在哪些方面明显弱于臂 A]
2. [边界精度 vs 片段选择准确性]
3. [非英语视频的表现]

等待审核
```

### 2.8 代码模板（`l2s/arms/arm_b_zeroshot.py`）

```python
"""Arm B: zero-shot clip extraction with text LLM.

Usage:
  python l2s/arms/arm_b_zeroshot.py \
    --asr $L2S_ASR \
    --labels $REPURPOSE_SRC/data/test.json \
    --ids eval/paper/splits/test_clean_ids.txt \
    --model Qwen/Qwen2.5-8B-Instruct \
    --out reports/P6/arm_b_preds.json

Requires: vllm (`pip install vllm`)
"""
import argparse, json, os, re
from vllm import LLM, SamplingParams

SYSTEM = """You are a video editor. Given a transcript and total duration, identify 2-4 interesting short clips suitable for social media. Each clip should be 15-90 seconds, self-contained (no dangling references), and start/end at sentence boundaries.

Output JSON only, no explanation:
[
  {"start": <seconds>, "end": <seconds>, "reason": "<one-line hook>"},
  ...
]"""

def load_transcript(path):
    with open(path, encoding="utf-8") as f:
        asr = json.load(f)
    text = " ".join(s.get("text", "") for s in asr.get("segments", []))
    return text.strip()

def parse_time(s):
    """Convert '1:23' or 83 or '1m23s' to float seconds."""
    if isinstance(s, (int, float)):
        return float(s)
    s = str(s).strip()
    # mm:ss or hh:mm:ss
    if ":" in s:
        parts = list(map(float, s.split(":")))
        return parts[-1] + (parts[-2] if len(parts) > 1 else 0) * 60 + (parts[-3] if len(parts) > 2 else 0) * 3600
    # 1m23s
    m = re.match(r"(\d+)m(\d+)s", s)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))
    return float(s)

def parse_output(text):
    try:
        return json.loads(text)
    except:
        # extract first [...] or {...}
        m = re.search(r'(\[.*\]|\{.*\})', text, re.DOTALL)
        if m:
            return json.loads(m.group(1))
    raise ValueError("Cannot parse LLM output")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asr", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--ids", required=True)
    ap.add_argument("--model", default="Qwen/Qwen2.5-8B-Instruct")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    with open(a.ids, encoding="utf-8-sig") as f:
        ids = [l.strip() for l in f if l.strip()]
    with open(a.labels, encoding="utf-8") as f:
        gt = {e["youtube_id"]: e for e in json.load(f) if e["youtube_id"] in ids}

    llm = LLM(model=a.model, tensor_parallel_size=1)
    sampling = SamplingParams(temperature=0, max_tokens=512, top_p=1.0)

    prompts = []
    for vid in ids:
        if vid not in gt:
            continue
        asr_p = os.path.join(a.asr, f"{vid}.json")
        if not os.path.exists(asr_p):
            continue
        text = load_transcript(asr_p)
        dur = max((s["end"] for s in gt[vid]["segments"]), default=0)
        prompts.append({
            "vid": vid,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": f"Transcript:\n{text}\n\nTotal duration: {dur} seconds.\n\nIdentify 2-4 clips."}
            ]
        })

    outputs = llm.chat(
        messages=[p["messages"] for p in prompts],
        sampling_params=sampling,
        use_tqdm=True
    )

    preds, failed = {}, 0
    for p, out in zip(prompts, outputs):
        try:
            raw = out.outputs[0].text
            clips = parse_output(raw)
            if not isinstance(clips, list):
                clips = [clips]
            preds[p["vid"]] = [
                (parse_time(c["start"]), parse_time(c["end"]), 1.0)
                for c in clips if "start" in c and "end" in c
            ]
        except:
            failed += 1
            preds[p["vid"]] = []

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(preds, f, indent=2)
    print(f"Success rate: {len(prompts) - failed}/{len(prompts)} ({100*(len(prompts)-failed)/len(prompts):.1f}%)")
    print(f"Predictions written to {a.out}")

if __name__ == "__main__":
    main()
```

---

## §3 时间估算

| 任务 | 预计耗时 | 瓶颈 |
|---|---|---|
| 臂 C 代码 + 跑通 | 30–60 分钟 | 找臂 A 预测文件 |
| 臂 C 评测 + 报告 | 15 分钟 | — |
| 臂 B 代码 + 跑通 | 1 小时 | vLLM 环境、提示词调试 |
| 臂 B 推理（clean test 约 600 视频） | 1–2 小时 | GPU（单卡 A6000 / A100） |
| 臂 B 评测 + 报告 | 15 分钟 | — |
| **总计** | **3–5 小时** | — |

---

## §4 依赖环境

| 环境 | 需求 | 安装 |
|---|---|---|
| `repurpose` | 臂 C 和评测 | 已有（P5 建过） |
| `vllm` | 臂 B | `pip install vllm` |
| 模型权重 | Qwen2.5-8B-Instruct | HuggingFace 自动下载，或提前 `huggingface-cli download Qwen/Qwen2.5-8B-Instruct` |

如果 vLLM 装不上（CUDA 版本不匹配等），可以改用 `transformers` + `torch`，但推理会慢 5–10 倍。

---

## §5 下一步

臂 C 和臂 B 做完后，结合 P4 的可达上限，可以看到：

1. **臂 C（吸附）能到什么水平** → 决定臂 D 要打多高才有意义
2. **臂 B（只看转写）能到什么水平** → 证明视觉和音频信号的价值
3. **句子候选的理论天花板** → 决定 D+ 的微调是不是必需

这三个数出来之后，就能开始训练臂 A / D / D+，目标是 G2 主表（11-02）。

---

**审核点：**
- 臂 C 完成后提交并等审核
- 臂 B 完成后提交并等审核
- 任何异常情况立即报告并停下
