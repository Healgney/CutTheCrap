# ICLR Video Highlight

把原始长视频转换为结构化剪辑结果：既判断哪些帧应进入高光成片，又为每个入选帧给出适配目标画幅
（`targetRatioWH`，常见 16:9 / 9:16）的构图区域 `[x, y, w]`，高度由画幅换算。

双目标：一个高光剪辑比赛，以及一篇 ICLR 论文。两者**不假设天然兼容**——见
[决策简报](docs/01-decision-brief.md)。

> **证据标注约定**（全仓库通用，沿用源文档）
> `[F]` 赛题附件已确认 · `[I]` 推断，可被证伪 · `[V]` 待核实，不替你补写
>
> 所有阈值均为**起始值待校准**，不是实测结论。不虚构 deadline、榜单数据、算力或实验结果。

---

## 当前决策状态（2026-09-04）

| 决策 | 结论 | 依据 |
|---|---|---|
| 时间基准 | 内部 deadline（09-11 / 09-16）**已推迟或未定**，按证据驱动排序，不按倒计时排 | 用户确认；harness 原文自述为占位日期 `[V]` |
| 策略 | **B · 论文主导**——先锁 thesis、数据与决定性实验，再把论文模型适配为参赛系统 | 用户选择 |
| 论文主线 | **数据 + 评测协议**：从专业短片反推 crop trajectory 的监督贡献 + 多参考评测协议 | 用户选择；决策简报 §06 |
| 联合学习 | 从 claim **降级**为受控发现，须由 Control D / E 支撑 | Hostile reviewer 判 Reject：输出签名与 STVG 同构 |
| 公开动作 | 条款澄清前**不做任何不可撤回的公开动作**：不 arXiv、不开源、不提交 OpenReview | 决策简报 §05 `[V]` |

**策略 B 的一个悬空前提：**B 的成立前提①是「条款确认宽松，或你接受放弃比赛」。
组委会问询尚未发出（清单见 [决策简报](docs/01-decision-brief.md) §05 与
[总览](docs/00-status-overview.md) 04）。数据线本身不触发公开披露，可以先推进；
但任何发布动作都要等条款回来。

### 关键路径（策略 B 下）

数据资产与评测资产，**不是架构**。简报的原话：「如果你选 B 却先去改架构，那是在错误的关键路径上。」

1. 阶段 0 合成对脚本 —— 不依赖任何未决答案，跑通就有抽取器第一个数字
2. Control C（croppability-blind）最小 pilot —— 决定联合性是 claim 还是工程细节
3. 从样例数据数三个数 —— 9:16 占比、高光帧稀疏度、GT 是稠密还是抽样标注 `[V]`
4. 读官方评测脚本，验证指标闭式 `F1 = 2S / (|P| + |G|)` 与「IoU > F1/2」决策规则
5. 论文评测数据从第 0 天独立建设（`eval/paper/`），含 Control D 反事实子集

---

## 目录

```
docs/                              # 全部决策与 spec
├── 00-status-overview.md          # 现状总览：idea / 流水线 / 架构 合并版（先读这份）
├── 01-decision-brief.md           # 双目标侧重决策简报（摘要版）
├── 01-decision-brief-full.html    # 完整版：决策矩阵、指标闭式、Hostile Reviewer、条款清单
├── 02-data-pipeline.md            # 数据流水线 spec：输出契约 + 七阶段 + 丢弃规则
├── 03-repo-selection.md           # repo 选型与三分支架构（⚠ 仍按旧主线写，待与新主线对齐）
└── harness/                       # 文献调研用的 prompt harness
    ├── ideahunt.md
    └── agentic-track.md

data_pipeline/
├── configs/
│   ├── sources_s1.yaml            # S1 来源清单（URL + 许可登记，不含视频）
│   └── thresholds.yaml            # 所有阈值集中管理，起始值待校准
├── stage0_synth/                  # 合成对生成 + 误差评测（永久回归集，非训练集）
├── stage1_pilot/                  # 真实对小批人工核 → yield rate
├── stage2_temporal/               # 音频指纹 + 互相关 + 斜率检验
├── stage3_spatial/                # NCC / 特征匹配，3-DoF 约束搜索
├── stage4_trajectory/             # 平滑 + 野点过滤
├── stage5_filter/                 # 丢弃规则 + 计数统计
├── stage6_export/                 # JSON 契约 + 可视化
├── labels/                        # 产出（url-only，不含视频本体）
└── reports/                       # yield rate、误差、丢弃分布、阈值校准记录

eval/
├── competition/                   # 官方指标复刻 + JSONL 校验（单 GT IoU-F1）
└── paper/                         # 多参考 / acceptable-set / 人类偏好

experiments/
└── control_c_croppability_blind/  # 决定联合学习 thesis 生死的那个消融
```

### 为什么 `eval/` 从第 0 天就分成两半

决策简报里唯一标记为「不可妥协」的一条：**论文永不依赖赛方测试集**。
评测数据与评测协议是唯一不能事后补做的资产——事后补做等于你已经用赛方测试集塑形了模型，
论文的独立性已被污染。代码、损失、阈值可以晚分叉，这两个不行。

两侧的评测口径本来就不同：比赛用单 GT 的 IoU-F1 `[F]`；论文必须做多参考 / acceptable-set /
人类偏好，因为构图是审美任务，合理解不唯一。

---

## 已知的三处许可地雷 `[V]`

同时做比赛（有工具合规条款）和论文（要可发布），这三个必须在选型时核实**当前**条款，
别等训练完才发现不能用。

| 组件 | 风险 | permissive 替代 |
|---|---|---|
| CoTracker3 | 历来 CC-BY-NC，非商用 | — |
| SuperPoint 权重 | 非商用（Magic Leap） | DISK / ALIKED |
| GAIC | 学术许可，需核实 | — |

## 待办：命名与文档缺口

- [ ] **三条 thesis 只有 T1 有名字**。流水线文档写「服务 T1（专业剪辑是可规模化取景监督源），
      是三 thesis 组装的脊柱」，T2 / T3 未定义。
- [x] **T1/T2/T3 撞名**已处理：数据来源梯队改称 S1 / S2 / S3；thesis 保留 T 前缀。
      `docs/02-data-pipeline.md` 内文尚未同步改。
- [ ] **三分支架构没有独立 spec**，只散在 `docs/03-repo-selection.md` 段落里，
      而流水线文档已经在引用它。
- [ ] **`docs/03-repo-selection.md` 仍按「联合学习」主线写**，需与新主线对齐。
