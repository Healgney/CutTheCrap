# Agent B：RQ3 / RQ4 笔记（簇 3 边界相关 + 簇 6 评测方法学）
标注：[F]=一手来源已确认；[I]=推断（可被证伪）；[V]=待核实。论文 id 见 rows.tsv，细节见 notes/。

---
## RQ3 边界即结构化预测

### 最近邻（3 篇）及与我们方向的差异
1. **B05 How Should Video LLMs Output Time?**（最近：唯一受控消融）。比较文本数字 / 专用时间 token / 连续分布头；三者都是"自由生成连续时间"，backbone ≤8B，视频 30–150 秒（Charades/QVH/YouCook2）。我们要问的是"在句末/说话人轮次/镜头切候选集上选择"，该文**没有此臂**。区别：无语音、无长视频、无候选切点。[F]
2. **B02 TimeLens**。最强 tIoU-RLVR 配方，并证明标注噪声（Charades-STA 20.6% 违反唯一性、34.9% 标注精度问题）会改变模型排名；仍是单 query 单片段、短视频、IoU≤0.7、连续文本时间戳。区别：query-conditioned grounding，不是无 query 的"选 K 个自包含 clip"。[F]
3. **B01 Vidi / VUE-TR**。长至 >1 小时、多时间范围、IoU-AUC 阈值扫描；训练数据用"场景切 + 字幕标点"分出 5–30 秒单元，但模型输出仍是自由生成的时间戳。区别：query 驱动；无 engagement/自包含目标。[F]

### (a) 边界精度有无专门指标/方法；连续回归 vs 候选切点有无直接消融
**专门指标**（MLLM 时刻检索主流并不用）：
- **Margin MCC**（ACM MM 2023）：指出"带容忍窗的 F1 会被预测数量很多的随机模型充高"，提出机会校正的 MCC 变体，期望随机分数为 0，对过/欠分割稳健。仅读摘要。[F: 摘要]
- **GEBD**（ICCV 2021）：F1@Rel.Dis 阈值 0.05–0.5（步长 0.05），对多位标注者取最佳匹配；标注者一致性另用绝对距离 0.2–1.0 s 的 F1。协议细节来自派生论文的搜索摘要。[V]
- **VidChapters-7M**：chapter 起点的 recall/precision@时间距离或 IoU，IoU 阈值含 0.9（来自搜索摘要）。[V]
- **MEDit-Bench**（B21）：cut 级 greedy 匹配 F1@{0.3,0.5,0.7} + 并集 R@θ；reward 中用 tIoU 加权软 TP，对边界连续。人类 leave-one-out R@0.7 仅 0.033、F1@0.7 0.109。[F]
- **VUE-TR**：IoU/P/R 对阈值 [0,1] 扫描取 AUC，支持多段范围并集。[F]
- **OMTG**（ICML 2026）：Count Accuracy + Effective Temporal F1；**TimeLens2**：temporal Wasserstein-1 reward，对不重叠的预测也有梯度。仅摘要。[F: 摘要]
- 主流 MLLM 只报 R1@{0.3,0.5,0.7} + mIoU（TimeLens、Time-R1）；**未见 IoU@0.9 或以秒计的边界误差**。[F]
- Time-R1 自述：IoU reward 使预测落入容忍带 ε，目的就是不必精确对齐，即 IoU 训练/评测对亚秒级偏差不敏感。[F]

**专门方法**：BAM-DETR（把"中心+长度"改成"内部锚点推边界"，摘要）；TimeRefine（粗预测 + 迭代偏移修正，WACV 2026，搜索摘要 +3.6/+5.0 mIoU）[V]；DRIFT（base 预测 + flow-matching 残差，称文本 token 接口不适合精确边界，摘要）；DisTime（单 token → bin 分布 → 连续时间，摘要）；TimeLens2 数据流水线含 boundary refinement 步骤（摘要）；TimePLE（2607.23951，区间联合分布，摘要）。

**回归 vs 候选切点的直接消融：未找到**（query 见 search_log）。最接近的间接证据：
1. TSGV 综述（2109.08039）：proposal/anchor 与 proposal-free/regression 方法族在不同数据集上各自胜出，混杂了架构、特征、训练等因素，无隔离对比。[F]
2. QVHighlights（B06）：DETR 式回归在 R1@0.5 上比 span 基线 XML+ 高 6.2 点（52.89 vs 46.69），但 mAP@0.75 低 5.3 点（29.40 vs 34.67）：回归在严格 IoU 处更弱，但这是整架构差异。[F]
3. B05：同骨干下连续分布头 > 文本数字（0.5B 连续 mIoU 43.4 > 8B 文本 27.5），说明输出接口本身对精度影响巨大。[F]
4. 候选式先例：MeCo（结构 token → 视频段，摘要）、Grounding with Confidence（生成候选 → 置信度选择，摘要）、Vidi 训练数据按场景/标点分段。工程文档中的 "snap to nearest word edge ≤0.5 s"（博客类，不作证据，仅作线索）。[F/V]
5. Otani 2019：摘要任务里"分段方式"对分数的影响大于重要性打分，[I] 暗示若候选切点集固定，评测应把"切点质量"与"排序质量"拆开报告。

**结论 [I]**：我们"在语义候选切点（句末/轮次/镜头切/停顿）上选择 + 小幅连续精修"的路线在文献中没有被消融过，既是空白也是风险：审稿人会要求同骨干比较 连续回归 / 文本时间戳 / 候选选择 / 候选+微调 四个臂。

### RQ3 仍未解决
- [V] Margin MCC 全文、GEBD 与 VidChapters 的指标细节需读原文。
- [I] 没有证据显示"句子/说话人轮次边界"相对任意回归边界有人类感知优势；也没找到评估 clip 起止点人类感知质量的学术协议（只有工程/专利线索）。
- [I] TimeLens 止于 IoU 0.7，MEDit 人类 R@0.7=0.033：多答案场景下高 IoU 阈值几乎不可达，应使用容忍窗口 F1 / 边界误差分布。
- [V] TimeRefine、DisTime、DRIFT、TimePLE、BAM-DETR 的消融数字未读。

---
## RQ4 多解评测

### 最近邻（3 篇）及差异
1. **B21 MEDit-Bench**：多参考（3 编辑 × 3 message）、cut 级 F1、严格阈值、LLM judge 失败的实证。区别：视觉-only、message 条件而非 engagement/自包含、1–3 分钟成片、无语音/ASR。[F]
2. **B22 Timeline-Bench**：人类校准 LLM judge 的完整配方与可靠性边界。区别：评 agent 的完整成片，不是长视频选 clip。[F]
3. **B17 Otani 2019**：指出单参考 F1 的"随机≈SOTA"与分段主导问题。区别：2019 摘要任务，非 clip 选择，评的是帧重要性。[F]

### (b) "多个答案都可接受"的现有评测协议清单（带与人类对齐的数字）
| 协议 | 代表 | 与人类对齐/验证的数字 | 备注 |
|---|---|---|---|
| 多参考 + avg/max F1 | SumMe/TVSum（Otani 批判） | TVSum avg F1：人类 leave-one-out 0.54 vs 随机 0.57–0.58；SumMe：人类 0.31 vs 随机 0.19（max 0.54 vs 0.41）[F] | 必须报随机/均匀基线 |
| 重要性分数与每位标注者的秩相关 | Otani τ/ρ | TVSum 人类 τ=0.177/ρ=0.204，方法 0.02–0.04（绝对值低因主观性）[F] | MEDit 零样本 MEDitor 在 TVSum 上 0.193/0.219 超人类 [F] |
| 参考间一致性作难度上限 | MEDit Table 2 | cross-annotator F1 0.42、cross-message 0.15；人类 R@0.7=0.033 [F] | |
| 建模参考分歧的多参考指标 | GF-measure（TETCI 2024）、VISIOCITY | 摘要称含相关与用户研究，数字未读 [V] | |
| 集合级召回/匹配 | VUE-TR 并集 IoU/P/R；OMTG EtF1+C-Acc；QVHighlights 多 moment mAP；MEDit cut-F1 | 评测本身不报人类相关；QVH 报标注者间 IoU>0.9（约 90% query）[F] | 与人类对齐未验证 |
| 成对人类偏好 | Timeline-Bench（43 剪辑师，2582 判断）；MEDit（90 对，1620 评价）；Stiennon；Chatbot Arena | Timeline-Bench 单判断 Krippendorff α=0.103、系统级 Spearman-Brown 可靠性 0.84；Stiennon 标注者–研究者 77%、人–人 73%；Arena crowd–expert 72–83%、expert–expert 79.4%/89.8% [F] | 须报人–人上限 |
| LLM-as-judge pairwise | MT-Bench（GPT-4 vs 人 66%/85%，人–人 63%/81%）；MEDit（失败） | MEDit：位置摆幅 55.6%→20.2%（35.4pp）；judge 判 AI 赢 62.1%，人类却 56.7% 偏好人类 [F] | 须双序评估；自我增强偏差 |
| 人类校准 judge 面板 | Timeline-Bench quality test | 系统级 ρ=r=0.93；单 edit κ=0.15（单个人类 κ=0.14）；每任务 ρ=0.32 [F] | 只可排序系统，不可评单件 |
| 学习型 reward model | Stiennon RM；VlogReward；VideoScore / VideoReward | Stiennon：RM–标注者 62.4%/66.5% vs 人–人 66.9%；VlogReward 仅在构造排序上 comparison acc 73.5%，**无独立人类相关** [F]；VideoScore Spearman 77.1（摘要）[F: 摘要]；VideoReward 去平局准确率约 72.9/73.6（表格列对应 GenAI-Bench / VideoGen-RewardBench 待核）[V] | VlogReward 不可当"已验证" |
| 偏差校准 | Wang 2023（平衡位置、多证据、人在回路）；Shi 2025（15 个 judge，>150k 实例，位置偏差随 judge/任务而变）；AutoCalibrate；PPI（Angelopoulos 2023，用少量人类标注给 judge 估计出置信区间） | 摘要级 [V] | 未入 rows.tsv，仅提及 |

### (c) Otani 2019 的核心结论与数字（详见 notes/B17.md）
- 随机摘要 F1 ≈ 已发表 SOTA：TVSum avg 随机 0.57/0.58 vs 方法 0.58–0.64；SumMe max 随机 0.41 vs 方法 0.41–0.45；TVSum 上随机甚至 ≥ 人类 leave-one-out（0.57 vs 0.54）。[F]
- 分段方法主导分数；背包偏好短片段；"均值"而非"求和"计分大幅抬高 TVSum F1。[F]
- 替代评测：对重要性分数与每位标注者排序算 Kendall τ / Spearman ρ 并平均，加 accumulative correlation curve；TVSum 方法 τ=0.020–0.042，人类 0.177。[F]
- 前向引用 169 篇（OpenAlex）中提出替代评测者：VISIOCITY（多参考+框架）、Margin MCC（边界）、GF-measure（多参考分歧）；Otani 组后续：MEDit-Bench、MeCo。后向引用：SumMe、TVSum、dppLSTM、DR-DSN、DPP、VideoSET 等经典。[F]

### (d) Timeline-Bench 的"editor-calibrated judge"（详见 notes/B22.md）
- 做法：3 个跨厂商 MLLM judge 对 edit 与 reference 分别打分 → 各 judge 在 919 视频上 z-score → 面板均值 → 通过 = 分差 ≥ 按 collection 拟合的"平局边距"；边距使通过率逼近但不超过人类 win-or-tie 率；报告用 leave-one-agent-out 边距。[F]
- 校准后一致性：16 agent 层面 ρ=r=0.93（平均差 3.0 点，最大 7.2）；单 edit κ=0.15；任务层面 ρ=0.32；校准与验证用同一批人类票（作者自陈局限）。[F]
- **VlogReward 更正**：arXiv:2607.22632 存在（2026-06-19 提交），不是"仅幻灯片"；但其 benchmark 的真值是 AI 辅助打分 + 合成降质，没有独立人类相关数字，保持"未验证"。[F]

### RQ4 仍未解决
- [I] 没找到专门针对"长视频选 clip（高光/摘录）"的 MLLM judge 与人类一致性验证；最近的是 MEDit（失败）与 Timeline-Bench（仅系统级）。
- [I] 没有同时满足"集合级（K 个 clip 的覆盖/冗余/排序）+ 多参考 + 人类偏好"的协议。
- [V] Margin MCC / GF-measure / VISIOCITY 的计算与人类相关数字需读原文。
- [V] Vidi/VUE-TR、Timeline-Bench、MEDit-Bench 的代码与许可未核实。

---
## Snowball 记录
- **Otani 2019**：OpenAlex 前向 169 篇，按标题关键词筛出评测相关；后向 41 条中解析出 29 个标题（经典：Gygli 2014 Creating Summaries from User Videos，Song 2015 TVSum，Zhang 2016 LSTM，Zhou 2018 DR-DSN，DPP，VideoSET 等）。
- **TimeLens**：Semantic Scholar 返回 ≥60 条 2026 年引用（OpenAlex 因索引滞后为 0）。与我们相关者：Kwai Keye-VL-2.0 (2606.10651)、CAPD (2609.34581)、TimeLens2 (2607.17423)、TimePLE (2607.23951)、DRIFT (2606.05758)、OMTG (2606.06294)、Grounding with Confidence (2609.39883)、MEDit-Bench (2607.25300)、MLLMs Know When Before Speaking (2605.21954)、Foresee-to-Ground (2605.21973)、Beyond Visual Boundaries (2608.28699，电影 RAG 场景分割，建议交簇 5 agent)、TLive-Omni (2608.20958) 与 Grounded Product Understanding in Livestream Videos (2609.20508)（直播域，建议交簇 1/8 agent）。其余为通用 VTG/omni 论文。后向：Time-R1、TRACE、VideoChat-R1、TimeSuite、Grounded-VideoLLM、MiMo-VL（均在其 Table 1）。标题级 [F]；内容多数未读 [V]。
