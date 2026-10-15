# Repurpose-10K 划分审计（2026-10-15）

来源：`github.com/yongliang-wu/Repurpose` 的 `data/{train,val,test}.json`，本地复算 [F]。

| 划分 | 条目（≤30 分钟块） | 唯一视频 | clip 数 | clip 中位时长 | clip 平均时长 |
|---|---|---|---|---|---|
| train | 8,968 | 7,065 | 96,996 | 36.6 s | 39.5 s |
| val | 1,121 | 1,092 | 11,921 | 36.5 s | 39.5 s |
| test | 1,122 | 1,081 | 12,025 | 36.0 s | 39.4 s |

- 全部唯一视频 8,399，clip 总数 120,942（论文写 8,398 / 120,925）。
- clip 中位约 36 秒，论文称约 60 秒：**确认不符**。
- **泄漏确认**：train∩test 404 个视频，train∩val 404 个，val∩test 63 个。
  train∩test 中 48 个视频有**完全相同的块**（同一 `timeRange`）同时出现在两边，即重复样本；其余 356 个是同一视频的不同 30 分钟块。

## 清理规则

按视频 ID 去重，优先保留 train：test 去掉所有在 train 中出现的视频；val 去掉所有在 train 或 clean test 中出现的视频。

| 划分 | 视频 | 条目 | clip |
|---|---|---|---|
| test_clean | 677 | 700 | 6,438 |
| val_clean | 657 | 669 | 5,987 |
| train（不变） | 7,065 | 8,968 | 96,996 |

ID 列表：`train_ids.txt`、`val_clean_ids.txt`、`test_clean_ids.txt`。
论文主表用 clean 划分；同时在原划分上报告一次，以便与 Repurpose-10K 的 11.57 对比。
