# 数据准备：来源、获取工具与产出格式

> 写于 2026-10-23。本文是 CVPR 2027 这条线**数据侧的唯一依据**；执行顺序与关卡见 [`07-server-handoff.md`](07-server-handoff.md)，研究设计见 [`06-cvpr2027-plan.md`](06-cvpr2027-plan.md)。
> 标注沿用仓库约定：`[F]` 已确认 · `[I]` 推断 · `[V]` 待核实。工具许可一列是代码许可，模型权重另行核实。

---

## 0. 总览

| 数据集 | 用途 | 来源 | 规模 | 优先级 |
|---|---|---|---|---|
| **D1 Repurpose-10K** | 训练、调参、主评测 | 公开标注 + YouTube 原视频 | 8,399 视频 / 约 3,800 h / 120,942 clip | 必做 |
| **D2 官方切片配对集（自建）** | 跨来源零样本评测 | 播客频道的官方完整版 ↔ 官方切片 | 目标 60–100 个完整版 | G0 通过后做 |
| **D3 人评集** | 不依赖 GT 的证据 | 从 D1 clean test 的模型输出中抽样 | 150 对 × 3 人 | P8 阶段 |
| D4 SVHighlights 子集 | 可选：非语音域泛化 | 公开数据集 | 视时间而定 | 有余力再做 |

**发布原则（所有数据集通用）：** 只发布 YouTube ID、时间戳、划分文件和我们导出的标注，不发布视频、音频和特征。每个来源都登记到 §6 的来源登记表。

---

## 1. D1 Repurpose-10K

### 1.1 来源

| 项 | 内容 |
|---|---|
| 标注 | `github.com/yongliang-wu/Repurpose` 的 `data/{train,val,test}.json`，代码 MIT，数据集许可未写明 [V] |
| 原视频 | YouTube，按 `youtube_id` 下载 |
| 字段 | `youtube_id`、`timeRange`（≤30 分钟一块）、`segments`（绝对时间）、`timeRangeOffset`、`segmentsOffset`（块内相对时间）、`coverage` |
| 划分 | 原始划分有泄漏；clean 划分见 [`eval/paper/splits/`](../eval/paper/splits/AUDIT.md) [F] |

### 1.2 获取步骤

| # | 步骤 | 工具 | 产出 |
|---|---|---|---|
| 1 | 下载视频，360p，优先 H.264 | yt-dlp | `$L2S_VIDEOS/{id}.mp4` |
| 2 | 同时抓 YouTube 自动字幕（备用，用于 ASR 对照） | yt-dlp `--write-auto-subs --sub-format json3` | `{id}.en.json3` |
| 3 | 导出音频 | ffmpeg | `$L2S_AUDIO/{id}.flac`，16 kHz 单声道 |
| 4 | 语音转写 + 词级对齐 | WhisperX large-v3 | `$L2S_ASR/{id}.json` |
| 5 | 抽特征（严格复现原文） | video_features（CLIP ViT-B/32，1 fps）、panns_inference（Cnn14）、sentence-transformers（all-MiniLM-L6-v2） | `$L2S_FEATS/{clip,pann,text}/{id}.npy`，形状 `[秒数, 维度]` |
| 6 | 候选切点 | WhisperX 句子/词时间、silero-vad、TransNetV2 | `$L2S_DATA/candidates/{id}.json` |

下载顺序：clean test → clean val → 原始 test/val 剩余 → train。

命令模板：

```bash
yt-dlp -f "bv*[height<=360]+ba/b[height<=360]" -S "vcodec:h264,res:360" \
  --merge-output-format mp4 --write-auto-subs --sub-langs "en.*" --sub-format json3 \
  -o "$L2S_VIDEOS/%(id)s.%(ext)s" --sleep-requests 1 --retries 3 \
  --download-archive "$L2S_DATA/archive.txt" -a ids.txt ${COOKIES:+--cookies "$COOKIES"}

ffmpeg -n -i "$L2S_VIDEOS/$ID.mp4" -vn -ac 1 -ar 16000 -c:a flac "$L2S_AUDIO/$ID.flac"
```

`--download-archive` 让中断后可以续传，不会重复下载。

### 1.3 已知问题与处理

| 问题 | 处理 |
|---|---|
| 视频失效（删除、私有、地区限制） | 记入 `status.csv`；论文报告实际可用数量，并在原始划分和 clean 划分上都注明 |
| 划分泄漏 | 主表用 clean 划分 |
| clip 中位时长 36 s，论文写约 60 s | 以数据为准，论文中说明 |
| GT 来自 OpusClip 候选 | 用 D2 回应，见 §2 |
| 非英语视频 | 用 WhisperX 的语言检测结果统计比例；第一轮全部保留，在报告里分语言给结果 |

---

## 2. D2 官方切片配对集（自建，仅评测）

### 2.1 为什么要它

D1 的标签是"用户接受并修剪了 OpusClip 的候选"。如果 OpusClip 本来就按句子切，臂 D 赢可能只是在模仿同一个工具。D2 的标签来自频道自己的剪辑师，和 OpusClip 无关，而且同样是长语音领域，正好回应这条攻击。

### 2.2 来源选择标准

1. **频道类型：** 播客、访谈、圆桌、讲座。英语为主。
2. **同一创作方同时发布完整版和切片：** 可以是同一频道，也可以是官方的 "Clips" 子频道。
3. **切片要求：** 时长 15–90 秒；是**连续的一段**，不是多段拼接。
4. **每个完整版至少有 3 个切片**，否则评测意义不大。
5. **只要官方发布的切片。** 粉丝搬运号不算，标签来源必须可说明。

目标规模：15–20 个频道，每个频道 4–6 期，共 60–100 期完整版。

### 2.3 获取步骤

| # | 步骤 | 工具 | 产出 |
|---|---|---|---|
| 1 | **人工**列出候选频道（完整版频道 + 切片频道的 URL） | 浏览器 | `data/d2/channels.yaml` |
| 2 | 列出频道上传列表（不下载视频） | `yt-dlp --flat-playlist --print "%(id)s\t%(title)s\t%(duration)s\t%(upload_date)s"` | `uploads.tsv` |
| 3 | 抓取切片的简介，找指向完整版的链接 | `yt-dlp --skip-download --print description` | 候选配对 `pairs_candidates.tsv` |
| 4 | 按"简介链接 > 标题相似度 + 发布时间在完整版之后 14 天内"配对 | 脚本 | 每个切片最多 3 个候选完整版 |
| 5 | 只下载配对上的视频和音频 | yt-dlp、ffmpeg | 同 D1 的目录结构 |
| 6 | **粗对齐：** 音频指纹找切片在完整版中的大致位置 | Chromaprint（`fpcalc -raw`） | 每个切片一个粗偏移 + 置信度 |
| 7 | **精对齐：** 在粗位置 ±10 秒内，用 log-mel 包络做互相关，精确到 10 ms | librosa + scipy | 起止时间 |
| 8 | **校验：** 切片的开头 5 秒和结尾 5 秒分别对齐，两者算出的偏移之差 ≤ 0.1 秒（说明没有变速和中间剪接） | 脚本 | 通过 / 丢弃 + 原因 |
| 9 | 人工抽检 20%：并排看切片和完整版对应时间段的起止 | 浏览器或 mpv | 抽检记录 |
| 10 | 导出成 Repurpose-10K 同格式 | 脚本 | `data/d2/test.json` |

### 2.4 丢弃规则（每条都计数，写进报告）

| 条件 | 含义 |
|---|---|
| 粗对齐置信度低 | 切片可能不来自这期完整版 |
| 开头和结尾的偏移差 > 0.1 秒 | 变速，或中间被剪掉了一段（拼接切片） |
| 切片开头或结尾有完整版里没有的音频（片头音乐、配音） | 用互相关峰值逐秒检测；只裁掉首尾的非源音频，裁后仍需 ≥ 15 秒 |
| 时长不在 15–90 秒 | 和 D1 的任务定义保持一致 |

### 2.5 产出格式

与 D1 完全相同的 JSON 字段，评测台不用改。完整版超过 30 分钟时，按 D1 的方式切成 ≤30 分钟的块；跨块的切片归到重叠更多的块里，并计数。

### 2.6 评测时必须注意

D2 的 GT **不完整**：频道只切了一部分精彩内容，没被切的不代表不好。所以在 D2 上：

- 主报：召回（预算 = GT 数）和匹配上的 clip 的 bF1、句中切断率；
- 精度只作参考，并在论文里说明原因。

### 2.7 验收

- 对齐误差：人工抽检中，起止误差 ≤ 0.2 秒的比例 ≥ 95%；
- 产出：至少 60 期完整版、300 个切片；
- 报告：`reports/D2/summary.md`，包含频道列表、配对数、各丢弃原因的计数和抽检结果。

---

## 3. D3 人评集

| 项 | 内容 |
|---|---|
| 来源 | D1 clean test 上臂 D 与臂 C 的输出 |
| 抽样 | 150 对：同一视频、两者 IoU > 0.3（说的是同一件事），A/B 顺序随机，种子固定 |
| 渲染 | ffmpeg 截取片段为 mp4，仅在内网使用 |
| 评分者 | 你和实验室同学，3 人，每人约 2–3 小时 |
| 问题 | 哪个更能单独看懂？哪个开头和结尾更自然？整体更想看哪个？ |
| 产出 | `reports/P8/pairs.csv`；答案键单独存放，不给评分者看 |

---

## 4. D4 SVHighlights 子集（可选）

| 项 | 内容 |
|---|---|
| 来源 | 数据集卡 `huggingface.co/datasets/idong1004/SVHighlights`，数据 CC BY-NC 4.0，代码 Apache-2.0 [F] |
| 获取 | 先读数据集卡，确认视频是否以 YouTube ID 形式提供 [V]；再用 yt-dlp 下载 |
| 规模 | 全量 320 个、平均 2 小时，太大；取 2–3 种运动、每种 10 个 |
| 价值 | 体育没有语音候选，只能用镜头切换候选，可以检验臂 D 是不是只对语音有效 |
| 触发条件 | G2 通过且离截稿还有 ≥ 10 天 |

---

## 5. 工具清单

| 工具 | 用途 | 代码许可 | 备注 |
|---|---|---|---|
| yt-dlp | 下载视频、字幕、频道列表 | Unlicense | 用最新版；YouTube 经常改接口 |
| ffmpeg | 解码、抽音频、截片段 | LGPL / GPL | 需支持 H.264 |
| Chromaprint `fpcalc` | 音频指纹粗对齐 | LGPL-2.1 | D2 用 |
| librosa + scipy | log-mel 包络与互相关精对齐 | ISC / BSD-3 | D2 用 |
| WhisperX | 转写 + 词级时间戳 | BSD-2 | 模型 large-v3 |
| silero-vad | 停顿检测 | MIT | |
| TransNetV2 | 镜头切换 | MIT | |
| video_features | CLIP ViT-B/32 帧特征 | [V] | 复现原文必须用同一模型 |
| panns_inference | PANNs Cnn14 音频特征 | MIT | |
| sentence-transformers | all-MiniLM-L6-v2 文本特征 | Apache-2.0 | |
| pyannote-audio | 说话人分离（可选） | MIT，权重需 HF 授权 | 第一轮不用 |

---

## 6. 来源登记表

每个来源一行，存 `data/sources_l2s.yaml`，比赛披露和论文的数据说明都从这里出。

```yaml
- id: d1_repurpose10k
  url: https://github.com/yongliang-wu/Repurpose
  content: annotations only; videos from YouTube
  license_annotations: unspecified   # [V]
  license_videos: YouTube ToS, third-party content
  release_plan: ids + timestamps + our split files
- id: d2_official_clips
  url: data/d2/channels.yaml
  content: channel-published full episodes and clips
  license_videos: YouTube ToS, third-party content
  release_plan: ids + aligned timestamps + alignment code
```

---

## 7. 目录与状态追踪

```
$L2S_DATA/
├── videos/  audio/  asr/  candidates/
├── features/{clip,pann,text}/
├── d2/      # D2 的原始视频与对齐中间产物
└── archive.txt
<repo>/
├── data/sources_l2s.yaml
├── data/d2/{channels.yaml, test.json}
└── reports/{P1,P2,D2,...}/   # summary.md + metrics.json + status.csv
```

每个数据集维护一份 `status.csv`：`youtube_id, dataset, split, download, asr, features, candidates, error`。每天提交一次，审核看这个文件就知道卡在哪一步。
