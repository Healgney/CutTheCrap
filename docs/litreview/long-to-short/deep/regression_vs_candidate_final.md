# "连续回归 vs 在候选切点上选择"——直接对比证据的最终确认（Agent B）

## 结论
**未找到**同时满足以下条件的论文/表：同一骨干、同一数据、仅"边界由连续回归/生成得到"与"边界从离散候选切点（句末、说话人轮次、镜头切、停顿等）中选择（或选择后再微调）"不同，并报告边界精度。[F: 在本次读过的 6 篇 core 全文 + 1 篇 Time-R1 全文中均无此臂；检索见下]

## 本次全文核对的论文中的"输出空间"
| 论文（id） | 边界如何产生 | 是否含候选选择臂 | 依据 |
|---|---|---|---|
| TimeLens (B02) | 文本形式连续时间戳（0.1 s），tIoU 的 GRPO | 否 | Table 2 比较的是时间戳"编码"（位置嵌入/overlay/文本前缀）；Table 3 比较训练范式 |
| How Should Video LLMs Output Time (B05) | 文本数字 / 专用时间 token / 33-bin 分布期望（连续） | 否 | Table 2 三个范式都输出自由时间；结论 Sec 6 的开放问题也不含候选选择 |
| Time-R1 (B03) | 文本形式连续时间戳 | 否 | Table 1–2 |
| Vidi / VUE-TR (B01) | 生成时间范围；训练监督按"场景+字幕标点"分段构造 | 否（分段只用于造训练数据） | Sec 4.3, 5 |
| MEDit-Bench (B21) | 模型输出秒数列表，无后处理 | 否 | App B.4 |
| Otani 2019 (B17) | 分段 + 背包选择（摘要任务，非学习边界） | 属于"候选段选择"的经典范式，但无与回归的对比 | Sec 4 的随机化检验，只比较分段方式对 F1 的影响 |

## 补充检索（本阶段新增的 query 与来源）
1. WebSearch：LLM selects transcript sentence indices / segment IDs as clip boundaries instead of timestamps → 仅得到实务博客（先编号转写句，由 LLM 返回起止编号，代码再映射到时间）与专利（句嵌入相似度选句索引）；无论文对比。博客/专利不作证据，仅作线索。
2. WebSearch：ablation boundary regression vs classification over candidate boundaries / snapping to shot boundaries → 无 moment retrieval 论文做"吸附到镜头切"消融；结果只有：CMIN/BMRN 在固定候选窗口之上加边界回归以突破离散边界限制（说明"候选+微调"在 2019–2023 的传统方法中是常规设计，但其论文里没有与纯回归对比的表）；BSN/BMN 的"边界概率分类 + 组合"；ClipTBP 指出逐 snippet 偏移回归会把相邻相似片段合并或边界不准（摘要）。
3. 间接证据：Boundary-sensitive Pre-training（Xu et al., ICCV 2021，arXiv 2011.10830，已读摘要+Table 8 的文字）——在合成拼接视频上预训练视频编码器时，"边界类型分类"预训练任务一致优于"变化点回归"预训练任务。这是编码器预训练目标的对比，不是推理时从候选中选边界，不能直接外推。[F: 文字] 
4. TSGV 综述（2109.08039）：proposal/anchor 与 proposal-free 方法族在不同数据集上各有胜负，因素混杂。[F]
5. QVHighlights Table 3（B06）：DETR 式回归在 R1@0.5 上优于 span 基线 XML+（52.89 vs 46.69），在 mAP@0.75 上更弱（29.40 vs 34.67）。[F]
6. DisTime/TimeRefine/DRIFT/TimePLE/BAM-DETR 均为"改进连续输出"的方案（摘要级），未含候选选择对照；MeCo（ICLR 2026）用结构 token 把视频切成事件/背景段，是"段式"输出，但摘要未提及与回归的消融数字 [V]。

## MEDit-Bench 数字与表号核实（回应上一条指令）
- 35.4pp（人类剪辑被 judge 选中 55.6%→20.2%，A/B 位对调）：出处 App E "Position bias" 段落与 Fig 8（右，按模型分解）。**不在 Table 3。** [F]
- 62.1%（双序平均后 AI 胜率，Human 37.9%）：出处同在 App E；该段称此为"主文报告的数字"，但主文 Table 3 的 "LLM Pref." 中 Gemini-3-pro 为 72.8%，GPT-5 为 77.8%。两者不一致（可能是 540 全量 vs 用户研究 90 对子集，或 judge 版本不同；judge 型号也在 Sec 3.5/App E/App F.4 间不一致：Gemini-3-pro / Gemini-3.5-flash / Gemini-3.5-Pro）。需向作者确认。[V]
- 其它：judge–人类一致率 59.9%、κ=0.18、Pearson 0.185、Spearman 0.167：App E "Correlation with human judgment" 段。人类研究 56.7%/56.8% 偏好人类剪辑：Fig 4（左）、App D。[F]

## 对新颖性判断的影响
- "候选切点选择 + 精修 vs 连续回归"的受控消融在文献中仍是空白，可作为可声称的实证贡献；但属于"未找到"而非"已证明不存在"，建议论文中使用措辞 "to our knowledge, no prior work compares…"，并保留上述检索记录。[I]
