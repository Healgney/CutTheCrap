# 服务器实验交接：CVPR 2027「边界是离散决策」

> 写于 2026-10-15。研究设计见 [`06-cvpr2027-plan.md`](06-cvpr2027-plan.md)，数据来源与获取工具见 [`08-data-preparation.md`](08-data-preparation.md)，本文只写**怎么在 GPU 服务器上做**。
> 读者有两类：服务器上的 Claude Code（执行）和你本人（审关卡）。每个阶段都写明输入、输出、验收标准和"停下来问人"的条件。
> 标注沿用仓库约定：`[F]` 已确认 · `[I]` 推断 · `[V]` 待核实。所有阈值都是**起始值**，改动要写进报告。

---

## 0. 给服务器 agent 的工作规则

1. **只做本文写到的阶段，按顺序做。** 每个阶段结束后提交报告并停下，等人审核通过再进入下一阶段。§3 标了"可并行"的除外。
2. **遇到以下情况立刻停下问人，不要自行绕过：**
   - YouTube 要求登录验证或大面积 403/429（需要人提供 cookies）；
   - 需要任何账号、token、密钥（HuggingFace、GitHub、AWS）；
   - 结果与本文预期偏差很大（各阶段写了预期区间）；
   - 想改动本文的设计（候选定义、指标、数据划分、超参）。
3. **不碰的东西：** 不上传视频或特征到任何公开位置；不改 `eval/paper/splits/` 里的划分文件；不在 clean test 上调参（调参只用 clean val）。
4. **数字只报实测值。** 跑不出来就写"未完成 + 原因"，不估算、不补写。

## 1. 已确定的事实（交接时已核实）

| 项 | 内容 |
|---|---|
| 数据 | Repurpose-10K 标注：`github.com/yongliang-wu/Repurpose` 的 `data/{train,val,test}.json`。只有标注，视频要自己下载，特征要自己抽 [F] |
| 划分泄漏 | 已在本地审计，见 [`eval/paper/splits/AUDIT.md`](../eval/paper/splits/AUDIT.md)。clean test 677 个视频 / 6,438 个 clip；clean val 657 / 5,987 [F] |
| 原始特征 [F] | 1 fps，每秒一个向量：CLIP ViT-B/32（512 维）、PANNs（2048 维）、WhisperX 句子经 all-MiniLM-L6-v2 编码（384 维）。一个句子跨多个秒时，向量复制到每一秒；没有语音的秒用 `[empty]` 的编码 |
| 原始指标是 precision [F] | `utils/metrics.py: calculate_tiou` 算的是"预测片段中与任一 GT 的 IoU ≥ 阈值的比例"，**不含召回**。预测数量由 `max_seg_per_min: 0.3` 控制（约每 10 分钟 3 个），而数据里实际是每 10 分钟 5.3 个。这一点要写进论文的评测修正 |
| 原始结果 | 论文报告平均 tIoU 11.57（tIoU@0.5 = 24.94） |
| 边界粒度 | GT 起止精确到 0.01 秒；原模型在整数秒网格上回归偏移量 |

## 2. 环境与目录

### 2.1 你本人先做（agent 不做）

1. 在 GitHub 建私有仓库，把本仓库推上去；服务器 clone 同一个仓库。
2. 准备 HuggingFace token（`pyannote` 说话人分离要用，第一轮可跳过）。
3. 若 §3 P1 探测被拦，从你自己的浏览器导出 YouTube cookies，放到服务器的 `$COOKIES` 路径。cookies 是账号凭据，**由你本人放置，agent 只引用路径**。

### 2.2 路径变量（在服务器 `~/.l2s_env` 里定义，所有脚本只读这些变量）

```bash
export L2S_REPO=...        # 本仓库在服务器上的路径
export L2S_DATA=...        # 大文件根目录（按需计费的存储）
export L2S_VIDEOS=$L2S_DATA/videos      # {youtube_id}.mp4，360p
export L2S_AUDIO=$L2S_DATA/audio        # {youtube_id}.flac，16 kHz 单声道
export L2S_ASR=$L2S_DATA/asr            # {youtube_id}.json，WhisperX 词级输出
export L2S_FEATS=$L2S_DATA/features     # clip/ pann/ text/ 三个子目录，{youtube_id}.npy
export L2S_CKPT=$L2S_DATA/checkpoints
export REPURPOSE_SRC=$L2S_DATA/Repurpose   # 原仓库 clone，只读
export COOKIES=                         # 需要时由你填
```

### 2.3 仓库内的代码位置

```
l2s/                       # 本项目新代码，全部在这里
├── download/              # P1–P2
├── asr/                   # P3
├── candidates/            # P4 候选切点
├── features/              # P5
└── arms/                  # P7 各臂
third_party/repurpose/     # 从原仓库复制的代码（MIT，保留 LICENSE），各臂在副本上改
eval/paper/                # P6 评测（独立于任何模型）
reports/<阶段>/            # 每阶段的 summary.md + metrics.json + 小图，入库
```

视频、音频、特征、checkpoint **一律不入库**（`.gitignore` 已覆盖 mp4/wav/features/checkpoints；新增 `*.npy` 规则）。

### 2.4 conda 环境（分开装，避免依赖冲突）

| 环境 | 用途 | 关键依赖 |
|---|---|---|
| `l2s-base` | 下载、候选、评测、数据处理 | python 3.10、yt-dlp（最新版）、ffmpeg、numpy、pandas |
| `l2s-asr` | WhisperX | whisperx（按其 README 的 torch 版本）、silero-vad |
| `l2s-feat` | CLIP / PANNs / MiniLM / TransNetV2 | video_features、panns_inference、sentence-transformers、transnetv2 |
| `repurpose` | 臂 A / C / D / D+ 训练 | 原仓库 requirements：python 3.9、torch 2.0.1 |

**验收：** 每个环境写一行版本号到 `reports/P0/env.md`（`pip freeze` 存全量）。

---

## 3. 阶段与关卡

日期对齐 `06` 的时间线；正文截止 11-16，Enrollment 11-10。

### P1 下载探测（10-15 → 10-16，约 30 分钟）

- 从 `eval/paper/splits/test_clean_ids.txt` 随机取 20 个（seed=0），下载命令：

```bash
yt-dlp -f "bv*[height<=360]+ba/b[height<=360]" -S "vcodec:h264,res:360" --merge-output-format mp4 \
  --write-auto-subs --sub-langs "en.*" --sub-format json3 \
  -o "$L2S_VIDEOS/%(id)s.%(ext)s" --sleep-requests 1 --retries 3 \
  -a probe_ids.txt  ${COOKIES:+--cookies "$COOKIES"}
```

- **输出：** `reports/P1/probe.md`：成功数、失败数、每个失败的错误类别（已删除 / 私有 / 地区限制 / 要求登录 / 限流）。
- **停下问人：** 出现"Sign in to confirm you're not a bot"或 429 → 等你放 cookies。
- **预期：** 失效（删除、私有）约 5–20% 属正常 [I]。

### P2 全量下载（P1 通过后开始，后台跑，持续数天）

- **范围：全部 8,399 个视频**（覆盖原始划分，才能和 11.57 对比）。按优先级分批：**clean test → clean val → 原始 test/val 剩余 → train**。
- 每个视频下载后立即导出音频：`ffmpeg -i X.mp4 -ac 1 -ar 16000 -c:a flac $L2S_AUDIO/X.flac`（FLAC 无损，体积约为 WAV 的一半）。
- 视频优先 H.264（上面的 `-S` 参数）：AV1/VP9 在 CPU 上解码慢数倍，而 P5 抽帧的瓶颈就是解码。
- 维护 `reports/P2/status.csv`：`youtube_id, split, status, duration_s, error`，每天提交一次。
- **验收：** clean test 完成率 ≥ 80% 才能做 G0；低于 80% 停下问人。

### P3 ASR（可与 P2 并行，下载完一批跑一批）

- WhisperX `large-v3`，开 word-level alignment，语言自动检测；记录检测到的语言（非英语视频的比例本身是一个数据统计）。
- 输出 `$L2S_ASR/{id}.json`：segments（句子）+ words（逐词起止）。
- 第一轮**不做说话人分离**（需要 HF token，留到 P7 之后）。
- **验收：** 随机抽 5 个视频，把转写与 YouTube 自动字幕的逐词时间做对比，报告中位时间差。超过 0.5 秒停下问人。

### P4 候选切点 + **G0 关卡**（目标 10-17，用已完成 ASR 的 clean test 视频，至少 200 个）

**候选点定义（v1）：**

| 类型 | 定义 | 可作为 |
|---|---|---|
| `sent` | WhisperX 句子边界：句首时间、句尾时间 | 起点用句首，终点用句尾 |
| `pause` | 相邻两词间隔 ≥ 0.3 秒，取间隔中点 | 起点、终点 |
| `shot` | TransNetV2 镜头切换时间 | 起点、终点 |
| `union` | 以上三类合并，0.2 秒内的点去重 | 起点、终点 |

**G0 要算的数（全部写进 `reports/P4/g0.json` 和 `summary.md`）：**

1. **覆盖率：** GT 起点（终点）到最近的同类候选点的距离 ≤ 0.5 / 1 / 2 秒的比例。分类型、分起点/终点报告。
2. **候选密度：** 每分钟候选点数。
3. **随机对照（必须有）：** 在同一视频里按同样密度均匀撒随机点，算同样的覆盖率。候选点很密时，覆盖率高没有意义，要看比随机高多少。
4. **GT 句中率：** GT 起点（终点）落在某个词内部，或离最近句子边界 > 1 秒的比例。这个数说明真人是不是按句子切。

**通过标准（起始值）：** `union` 在 ±1 秒的覆盖率 ≥ 80%，且随机对照 ≤ 50%。

> **10-25 修订（事后修订，论文中须如实说明）：** 上面的原判据有设计缺陷。候选密度为 λ 个/秒时，同密度随机点在 ±tol 内的期望覆盖率是 `1 − exp(−2·tol·λ)`；union 密度约 37 个/分钟，所以 ±1 s 随机对照必然约为 0.70，"随机 ≤ 0.5"永远不可能成立。新判据：
> - 主指标为 **lift = 实测覆盖率 − 同密度随机期望**，按候选类型和起点/终点分别报告；
> - 候选集改为 **sent-first**：主候选只用句子边界；shot 不再作为候选，降级为特征；pause 仅作辅助；
> - 通过条件：`sent` 的起点和终点在 ±0.5 s 上 lift ≥ 0.25、在 ±1 s 上 lift ≥ 0.15；
> - 同时报告**可达上限**：把 GT 吸附到最近的 sent 候选后得到的 bF1 和 tIoU，这是臂 D 的理论天花板；
> - 结果按**语言**分组（英语 / 非英语）。
> 首轮结果见 `docs/P4-结论与判据修正.md`：sent 的 lift 为 +0.42/+0.37（±0.5 s）、+0.34/+0.30（±1 s）。
**结果交给人判定**，agent 不自行决定 go/no-go。

### P5 特征抽取（10-17 → 10-21，复现原文设置）

- 严格按 §1 的原始特征：CLIP ViT-B/32 1 fps、PANNs Cnn14 每秒 2048 维、WhisperX 句子 → all-MiniLM-L6-v2。
- 每个视频存**全长**特征 `{id}.npy`，形状 `[秒数, 维度]`。原 dataloader 会按 `timeRange` 切片。
- **验收：** 三种特征长度差 ≤ 2 秒；抽 3 个视频画 CLIP 特征相邻秒余弦相似度曲线，应在镜头切换处出现低谷。

### P6 评测台 `eval/paper/`（10-17 → 10-21，可与 P5 并行，不依赖任何模型）

统一输入格式：`predictions/{arm}/{split}.json` = `{youtube_id: {"chunk_start": s, "segments": [[st, ed, score], ...]}}`。

| 指标 | 定义 |
|---|---|
| `orig_tiou` | 原仓库 `calculate_tiou`，逐字复制，用于和 11.57 对比 |
| `R/P/F1@{0.5,0.7,0.9}` | 一对一匹配（贪心按 IoU）后的召回、精度、F1 |
| 两种预测预算 | (a) 原设置 `max_seg_per_min=0.3`；(b) 预测数 = 该块 GT 数（oracle 预算）。**所有臂两种都报** |
| `bF1@{0.5,1,2,5}s` | 起点、终点分别在容忍窗内匹配的 F1（边界精度） |
| `midsent_rate` | 预测起止点落在词内部或离句子边界 > 1 秒的比例 |
| `random` 基线 | 每个块按 GT 时长分布随机放同样数量的片段，10 次取均值 ± 标准差 |

- **验收：** 用 GT 当预测时，`orig_tiou=1`、`F1=1`、`midsent_rate` 等于 P4 里的 GT 句中率；random 基线结果入库。

### P7 四个臂 + **G1 / G2 关卡**

**G1（目标 10-24）：臂 A 复现。**
- 在原始划分上训练 → 原始 test 上报 `orig_tiou`，与 11.57 对比；再在 train → clean val 选模型 → clean test 报全部指标。
- 原配置训练，3 个种子（1234、1、2）。
- **预期：** 由于部分视频已失效，结果可能和 11.57 差 ±1.5；差得更多就停下问人。

**各臂定义（同一组特征、同一编码器、同样训练轮数）：**

| 臂 | 做法 |
|---|---|
| **A** 连续回归 | 原模型不改 |
| **C** 回归 + 吸附 | A 的预测起止点吸附到 ±3 秒内最近的 `sent` 候选点（10-25 起由 union 改为 sent，与臂 D 用同一候选集）；没有候选点就不动。**这是最关键的对照** |
| **D** 候选选择 | 保留原编码器；把回归头换成两个逐秒头：起点分数、终点分数（训练目标为离 GT 起止最近的候选点）。解码：枚举候选起点 × 候选终点、时长 15–90 秒的组合，分数 = 起点分 + 终点分 + 区间内显著性均值，再 soft-NMS，预算同 P6 |
| **D+** 候选 + 微调 | D 之后再回归 ±1 秒内的残差 |
| **B** 大模型时间戳（可选） | 纯文本 LLM（Qwen3-8B 一类，48 GB 卡可跑）零样本：输入带时间戳的转写，输出 K 个 `[start, end]`。只在算力和时间允许时做 |

**G2（目标 11-02）：主表** `reports/P7/main_table.md`：所有臂 × 两种预算 × 全部指标，3 种子均值 ± 标准差，外加 random 基线。
**判定交给人：** D 在 `bF1@1s`、`F1@0.7` 和 `midsent_rate` 上显著优于 C → 按原主张写；D ≈ C → 改写为分析型论文（见 `06` §4）。

> **10-27 修订（依据 `docs/P6/fix.md`，在看到臂 D 结果之前写定）：**
> P6 显示瓶颈首先是定位：臂 A 的 F1@0.7 与随机相同；即使在 IoU≥0.5 的匹配对上，边界误差中位数也约 10 秒。逐秒打起止分的旧版臂 D 解决不了这个问题，改为**句子区间提议**：
>
> | 臂 | 做法 |
> |---|---|
> | **D** 句子区间提议 | 提议 = 同一块内所有（第 i 句句首，第 j 句句尾）组合，时长 15–90 秒。提议特征 = 起点处插值特征 ⊕ 终点处插值特征 ⊕ 区间内均值池化 ⊕ 时长嵌入 ⊕ 边界特征（是否与镜头切换重合、前后停顿长度、音频能量变化）。编码器沿用原 MMCTransformer。训练：与某个 GT 的 IoU≥0.7 的提议为正例，每个 GT 至少保留 IoU 最高的 1 个提议；BCE + 排序损失。解码：分数排序 → soft-NMS → 与 A 相同的预算 |
> | **D+** | D 之后在 ±1 秒内回归起止残差 |
>
> **G2 判据（事先写定）**，D+ 与 C 比较，3 个种子均值，clean test 的 601 个视频：
> 1. **边界：** IoU≥0.5 匹配对中，起点和终点误差 ≤1 秒的比例都 ≥ C 的 2 倍（C 为 8.9% / 9.7%）；
> 2. **定位：** F1@0.5 不低于臂 A（0.150），且 F1@0.7 高于随机（0.050）超过 3 个标准差；
> 3. **可读性：** 句中切断率 ≤ GT 自身水平（0.36 / 0.46）。
>
> 满足 1+2+3：方法论文。只满足 1+3：论文以评测为主，方法作第二贡献。都不满足：改投。

### P8 人评素材准备（10-29 → 11-02，评分由你和实验室同学做）

- 从 clean test 抽 150 对：同一视频、主题重叠（IoU > 0.3）的 D 输出与 C 输出各一个，A/B 顺序随机，种子固定。
- 用 ffmpeg 渲染成 mp4（只在服务器本地或内网使用，不公开）。
- 导出 `reports/P8/pairs.csv`：`pair_id, youtube_id, clip_a, clip_b, which_is_D`（`which_is_D` 列单独存一份，不给评分者看）。
- 评分界面另外交接；评分问题：哪个更能单独看懂？哪个开头和结尾更自然？整体更想看哪个？

---

## 4. 报告格式（每个阶段都一样）

`reports/<阶段>/summary.md` 第一行写结论（通过 / 未通过 / 需要人判断），然后是关键数字表，最后是异常与疑问。数字同时写进 `metrics.json`。提交信息格式：`[P4] G0 coverage on 214 clean-test videos`。提交后在 summary 末尾写"等待审核"并停止。

## 5. 时间线速查

| 日期 | 服务器侧 | 关卡 |
|---|---|---|
| 10-15 → 10-16 | P0 环境、P1 探测、P2 开始 | P1 是否被拦 |
| 10-16 → 10-17 | P3 ASR（clean test 优先）、P4 候选 | **G0** |
| 10-17 → 10-21 | P5 特征、P6 评测台 | 评测台验收 |
| 10-22 → 10-24 | P7 臂 A 复现 | **G1** |
| 10-25 → 11-02 | P7 臂 C、D、D+（B 可选），P8 人评素材 | **G2** |
| 11-03 → 11-06 | 人评；补消融 | **G3** |
| 11-10 / 11-16 | — | Enrollment / 提交 |

## 6. 仍需你本人确认的事项 [V]

1. AWS 额度批下来后，P7 是否迁移到 AWS？迁移时只需重设 §2.2 的路径变量。
2. Repurpose-10K 数据许可未写明；论文只发布划分文件与 ID，不发视频和特征。
3. 比赛组委会问询（见 `00-status-overview.md` §04）仍未发出。
