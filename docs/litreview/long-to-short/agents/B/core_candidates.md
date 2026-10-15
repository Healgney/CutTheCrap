# Agent B：建议 core（7 篇）
威胁等级 = 与我们"长语音视频 → K 个自包含 clip + 边界精修 + 多解评测"最接近的程度。

| id | 论文 | RQ | 一句理由 | 威胁 | 建议深读 |
|---|---|---|---|---|---|
| B21 | MEDit-Bench (2607.25300) | RQ4, RQ3 | 长视频 → 多份专业剪辑参考、cut 级匹配 F1@θ、严格阈值下人类自身仅 R@0.7=0.033，并实证 LLM judge 与人类方向相反（位置偏差摆幅 35.4pp）；Otani 组后续，正是我们评测章节要对标/区分的对象。 | 中（视觉-only、message 条件、1–3 分钟剪辑，无语音/自包含/engagement） | Sec 3.2 一致性、3.5 指标、App E judge 局限、App B.5 |
| B22 | Timeline-Bench (2609.35143) | RQ4 | 唯一给出完整"人类校准 LLM judge"配方（z-score 面板 + 平局边距 + leave-one-agent-out）及其边界：系统级 ρ=0.93、单件 κ=0.15。 | 低（评 agent 成片，非选段） | App D 全部、App F/G、Sec 6 与 App N |
| B17 | Otani 2019 (1903.11328) | RQ4 | "随机≈SOTA、分段主导分数、改用 τ/ρ"是评测批判的原点；我们的候选切点集同样会主导分数。 | 低（评测批判，非方法） | 已 full-text；可补读 Sec 4.3 与附录用户研究 |
| B02 | TimeLens (2512.14698) | RQ3, RQ4 | 证明边界标注质量能重排模型排名；给出 tIoU-RLVR（thinking-free）最佳配方与时间戳编码消融；是我们若用 MLLM 回归边界时要对比的最强基线。 | 低–中（单 query 单片段，短视频，只到 IoU 0.7） | App B 基准统计、App C RLVR 细节、Sec 3.1 标注准则 |
| B05 | How Should Video LLMs Output Time? (2604.08966) | RQ3 | 目前唯一同骨干受控比较"文本数字 / 时间 token / 连续分布头"的工作；同时明确显示"仍无候选切点选择臂"。 | 低 | Sec 5.1–5.5 全部表与失败案例 |
| B18 | Margin MCC (ACM MM 2023, doi 10.1145/3581783.3613760) | RQ3, RQ4 | 唯一找到的带容忍窗口且做机会校正的边界指标，专门指出"F1 + allowed margin"会被随机预测充高。 | 低（指标论文，视频事件边界） | 全文（目前仅读摘要；无 arXiv 版本） |
| B01 | Vidi / VUE-TR (2504.15681) | RQ3, RQ4 | 小时级视频、多段时间范围、阈值扫描 IoU-AUC 的现成评测，与训练配方（场景切 + 字幕标点分段）；产业界对标对象。 | 中（query 条件检索，非 engagement 选段；Vidi2.5 由簇 1 覆盖） | Sec 5 数据流水线、Sec 6.2 指标、Table 3 |

备注：
- B23 VlogReward 不建议列 core：没有与独立人类评审的一致性数字；另外 brief 中"arXiv 未找到"需更正为 arXiv:2607.22632。
- B03 Time-R1、B06 Moment-DETR 作为方法背景，不必深读。
