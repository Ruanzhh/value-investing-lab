# 风险登记与唯一归属
目的：防止同一风险在情景、hurdle、仓位、击穿码多处重复扣减（v2.4 审计发现的主要偏差）。

| owner | 放什么 | 如何体现 |
|---|---|---|
| bear_scenario | 可量化的经营下行（价格、单位利润、份额、税负、利用率、减值） | 只改熊市驱动，不改基准、不改 hurdle |
| hurdle_grade | 不可量化的质量/可持续性不确定（老唐前提、治理、未定价开放问题） | 只影响评级档 |
| position_rule | 估值路径分布宽（熊/基差距大、脆弱性） | 只影响仓位档 |
| break_code | 论点失效的可观测阈值 | 只在持有期触发退出 |

规则：
- 每条风险一行：id、描述、来源（enterprise_analysis/data_gap ID）、owner、体现位置、量化。
- 同一风险不得出现在两个 owner；若既可量化又有尾部，量化部分归熊市，尾部阈值另立击穿码并说明区别。
- data_gap 默认归 hurdle_grade（未定价）或 bear_scenario（已用保守数）二选一。
- 基准情景不是 owner；任何风险都不得同时压低基准。

示例（CATL）：消费税/退税 → bear_scenario（单位利润 0.05–0.055）；764GWh 再投入 → hurdle_grade（③不满足→B）；熊/基差距 → position_rule（脆弱比 0.43）；单位净利 <0.06 两年 → break_code X1。见 `（内部文稿未发布）`、`reaudit_v25.md`。
