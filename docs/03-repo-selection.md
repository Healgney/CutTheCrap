这两个都需要给你能直接落地的东西——repo 要确认现在还在维护、许可清楚。我先联网核实一批，再写 pipeline 文档。

核实几个关键的：那个统一的可复现库、图像构图的 GAIC、以及音频对齐工具。

核实完了。先给结论，再上文档。

## 一个必须先讲清的事实

**没有任何一个 repo 能同时匹配你的任务**——query-free、画幅条件、联合高光+逐帧 3-DoF 构图，这个组合目前没有开源实现。这不是坏消息：它正好说明你的贡献空间是真的。

所以正确的做法不是"找一个 repo 改"，而是**一个主干 + 各模块借件**。下面按你上一轮定的三分支架构给。

## 一、主干（决策头 + 评测框架，最该 fork 的）

**[line/lighthouse](https://github.com/line/lighthouse)** —— 这是我的首选主干。

- 它是一个**统一、可复现**的 moment retrieval + highlight detection 库，内置 7 个模型（QD-DETR、CG-DETR、UniVTG、Moment-DETR 等）、特征抽取、训练/评测 harness。
- **还在活跃维护**（README 挂到 ICASSP 2026）——这在这个方向很少见，大多数论文 repo 发完就死。
- 为什么是它：**harness 是最贵的、两个目标都要用的部分**（可复现评测正是论文要的，稳定提交正是比赛要的）。它的 DETR 决策头就是你"联合决策头"最近的起点。
- 改造点：把文本 query 输入位置换成 `targetRatioWH` 条件；时间头保留；**空间头它没有，你自己加**。

如果不想 fork 整个库，单模型基线可用 [wjun0830/QD-DETR](https://github.com/wjun0830/QD-DETR)、[showlab/UniVTG](https://github.com/showlab/univtg)（UniVTG 尤其贴合，因为它本来就统一了 interval/curve/point 三种时间标注）。

## 二、几何分支（空间构图，需自己组装）

没有现成的，用这几个拼——**这套组装本身可以写进 method**：

| 用途 | Repo | 说明 |
|---|---|---|
| 主体框 + 跟踪（一体） | [IDEA-Research/Grounded-SAM-2](https://github.com/idea-research/grounded-sam-2) | Grounding DINO + SAM2，文本或框 prompt 直接出可跟踪的主体，几何分支最省事的入口 |
| 分割/跟踪底座 | [facebookresearch/sam2](https://github.com/facebookresearch/sam2) | SAM 2.1，需要更底层控制时用 |
| 点级跟踪（做平滑轨迹） | [facebookresearch/co-tracker](https://github.com/facebookresearch/co-tracker) | CoTracker3。**许可注意**：历来是 CC-BY-NC（非商用），比赛/商用前必须核实当前条款 `[V]` |
| 构图美学打分 + 定宽高比裁切 | [HuiZeng/Grid-Anchor-based-Image-Cropping-Pytorch](https://github.com/HuiZeng/Grid-Anchor-based-Image-Cropping-Pytorch) | GAIC，能对指定宽高比输出候选裁切并打分——正好对上你"3-DoF 稠密枚举"的想法。学术许可，需核实 `[V]` |

## 三、语义分支（VLM + LoRA/DPO，训练框架成熟）

| Repo | 说明 |
|---|---|
| [hiyouga/LLaMA-Factory](https://github.com/hiyouga/LlamaFactory) | 支持 Qwen2-VL 的 SFT + **DPO** + LoRA/QLoRA，配方现成。你上一轮想要的"偏好优化"直接有 |
| [modelscope/ms-swift](https://github.com/modelscope/ms-swift) | 同类，DeepSpeed/FSDP 分布式更全，长视频多帧场景更稳 |
| [zjysteven/lmms-finetune](https://github.com/zjysteven/lmms-finetune) | 最小代码库，想读懂/魔改微调逻辑时比前两个清楚 |

底座模型建议 Qwen2.5-VL（2B/7B Apache-2.0，许可对论文和比赛都友好，但大尺寸需核实 `[V]`）。

## 四、这些是基线，不是主干（别在上面改）

**[google/mediapipe AutoFlip](https://opensource.googleblog.com/2020/02/autoflip-open-source-framework-for.html)**、[bmezaris/RetargetVid](https://github.com/bmezaris/RetargetVid)、[Autocrop-vertical](https://github.com/kamilstanuch/Autocrop-vertical) —— 这三个是经典/启发式视频重构图。它们的价值是：

1. **必比的 baseline**——审稿人一定问"你比 AutoFlip 好多少"，RetargetVid 还自带数据集和评测
2. AutoFlip 的三阶段（场景检测→内容分析→重构图）**解码逻辑**可以参考
3. 它们都**不学习**、都**无高光选择**——正好反衬你的贡献

一句话总结：**fork Lighthouse 当主干和评测台，几何分支用 Grounded-SAM-2 + GAIC 拼，语义分支用 LLaMA-Factory 微调 Qwen2.5-VL，AutoFlip/RetargetVid 只当基线。**

---

现在写数据 pipeline 文档。

文档已保存到 [data-pipeline-crop-trajectory.md](Downloads/data-pipeline-crop-trajectory.md)。它是按「能直接放进代码仓当 spec 用」写的——markdown 便于版本化、GitHub 直接渲染、和代码放一起。涵盖：

- **输出契约**（先定死，字段和比赛 `[x,y,w]` + `targetRatioWH` 对齐，额外带 `conf` 供 PU/加权训练）
- **来源三梯队**表（T1 天然双画幅 / T2 全景虚拟机位 / T3 仅时间监督）+ 为什么不能单押 T1
- **6 个阶段**：阶段 0 合成对自检（含 FFmpeg 命令）、阶段 2 音频优先对齐（含 fpcalc）、阶段 3 的 3-DoF 约束搜索（含 NCC 代码）、阶段 4 轨迹平滑、阶段 5 丢弃规则表、阶段 6 导出
- **PU 陷阱**的数据层处理 + 偏好对如何喂 DPO
- **要盯的数**（yield rate 是决定 T1 生死的那个）、**合规发布**、目录结构、`thresholds.yaml` 示例、里程碑通过标准

三处诚实标注保持一致：所有阈值都写明是**起始值待校准**、不是实测；许可风险全标 `[V]`；yield rate 明确写"现在完全未知"。

---

**两个提醒**，都关系到你别在错的地方投入：

1. **repo 里有两个真实的许可地雷**——CoTracker 历来是非商用（CC-BY-NC），SuperPoint 权重非商用。你同时在做比赛（有工具合规条款）和论文（要可发布），这两个必须在选型时就核实当前条款，别等训练完才发现不能用。permissive 替代我在文档 §5 写了（DISK/ALIKED）。

2. 文档末尾「附」里挂了一个**未决前提**：GT 是稠密标注还是抽样标注 `[V]`。它同时决定几何分支逐帧还是逐段、以及 pipeline 导出要不要下采样对齐比赛粒度——这个从样例数据里数一下就知道，我建议你早于任何架构编码去确认它。

需要的话，下一步我可以：把阶段 0 的脚本真正写出来（合成对生成 + NCC 轨迹恢复 + 误差评测，跑通就有抽取器第一个数）；或者把这两轮的架构结论和 repo 选型并进那份 HTML 简报。你说哪个。