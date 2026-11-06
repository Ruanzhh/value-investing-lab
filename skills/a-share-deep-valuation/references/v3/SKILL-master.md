---
name: a-share-deep-valuation-v3-master
description: >-
  （LIVE · cutover 2026-10-31）A 股深度估值 v3 总流程：建档+生意模式路由 → 调度子流程 → 统一输出接口 →
  validate_anchors 硬闸 → S5a 内部 B20 → S4c 外部交叉校验 → S5b 签发/到价 → 独立复核 → 决策卡 → 预测对账 → 喂 a-3 队列。
  LIVE 入口：references/valuation-rules-v3.md；v25 为 legacy 附录。
---
# A 股深度估值 v3 · 总流程（workflow of workflows · 两层）

状态：LIVE (installed · cutover 2026-10-31；t423u 两层；t425u r2；t428u r3；**t430u r4**：S4c 闭环重排 S5a→S4c→S5b、条件 B20 schema、双方法进子流程、M5d/M7 去污、校验器补全）。**入口规则 `references/valuation-rules-v3.md`；legacy v25 md5 `0486682f…`；映射冻结源 `5d691d8b…`**。迁移见 `../MIGRATION.md`；框架变更见 `../FRAMEWORK_OPT.md`（含 r5 回填/抽查）。a-4/执行器不调锚点数值、不发明买点。
两层：上层本文件只管顺序与关卡 + L1 共用规则（`rules-master-v3.md`）；下层 `../sub/<模式>/SKILL.md` 只管「FV3 怎么来」。不再往下拆第三层，参数留在锚点（`（内部文稿未发布）`）。

## 执行协议（沿用 v2.5 状态机）
- v3 草案期用 `workflow-v3/scripts/workflow_state_v3.py open/commit/status`（S0–S9 状态、`--test-run` 沙盒；r2, D11），安装时再并入 `（内部文稿未发布） open/commit`；v3 安装时 workflow.yaml 增加 S2/S3/S4 三个 state（见 MIGRATION）。主 Agent 是唯一 commit 写入者；子流程由 subagent 执行，只返回 artifact。
- 不编造数据；缺项登记 `data_gap`；独立复核不可用即 blocked，绝不代审；TA 永不抬 B20；不执行交易，输出仅个人研究；交易一律置换语言。

## 阶段
| # | state | 做什么 | 产出 | 关卡 |
|---|---|---|---|---|
| S0 | intake | 建档、资料收集（v2.5 artifact-contracts / deep-analysis-gates 不变） | intake.json | 资料清单齐或登记 gap |
| S1 | routing | 按「利润由什么驱动」定 `business_model`（主 1 + 副 ≤1）；查 `ROUTING.csv`；改模式须 `model_change_reason` | routing.json | V§16；与路由表不符且无理由 → FAIL |
| S2 | dispatch_sub | 调 `sub/<模式>/SKILL.md` S1–S10；D1–D12 深度分析按子流程驱动表模板填 | deep_analysis + drivers | 子流程硬断言 |
| S3 | unified_output | 子流程交回 `plugin_output.json`（`schema/plugin_output.v3.schema.json`） | plugin_output.json | schema 必填 |
| S4 | validate_gate | `python3 scripts/validate_anchors.py --kind plugin plugin_output.json` | validate_report.json | 任一 FAIL → 退回 S2，不出卡 |
| S5a | compute_internal_B20 | 用 FV3+dps 按 V§5 算出 **内部** B20_TR/B22、r_bear、脆弱比、仓位档草稿（尚未接外部、未签发） | B20_internal + valuation_decision_draft | 公式用 n；双方法未齐 → 标记拟不出 B20 |
| S4c | external_crosscheck | 外部交叉校验（V§4c）：对照一致预期、多方法三角、区间买入、护栏「外部永不抬 B20」。**必须在内部 B20 算出之后**；产出并入 decision | external_crosscheck 块 | URL/日期/同口径/≥2 方法/B20_final≤B20_internal/min(range)；阈值 PROVISIONAL |
| S5b | finalize_buy_sell | 取 B20_final=min(区间)；签发或置 `B20_issued=false`+`gate_block_reason`；到价判定（整区间）；收益卖/打平/置换定稿（V§5–V§9、V§15、V§5b） | valuation_decision.json | 自检 V§19；未签发则 B20_TR 可为 null |
| S6 | independent_review | 独立 subagent 按 `review-template.md`：事前验尸 + 逐锚点核对 + 反方；≤3 轮。**启动路径（r2, D12）**：执行器（subagent）不能也不得自启复核员；执行器写 `review_request.json`（artifact 路径列表、author_id、需裁决问题）后以 `blocked_on_independent_review` 交回；**主 Agent** 另起一个只读 artifact、未参与估值的 subagent 作复核员，复核员写 `review.json`（`reviewer_id`≠`author_id`、verdict）；主 Agent 原样透传并 commit，不改判词。同代理自查只能写 `verdict=PENDING` | review.json | PASS / PASS_WITH_CHANGES；FAIL 退回；card gate 校验 independent、reviewer_id≠author_id、verdict |
| S7 | decision_card | TA 可达性 + 决策卡（`schema/card.v3.schema.json`），`anchor_trace` 每个数字→叶子锚点 | decision_card.json/md | `validate_anchors.py --kind card` 无 FAIL |
| S8 | ledger_register | 写 forecast_ledger：FY+1 核心 NI、top-2 驱动、NI3 P10/P50/P90 + 锚点归因 | ledger rows | V§18 |
| S9 | reconcile_feed | 财报后写 actual；偏差 >15% 归因锚点；同锚点 ≥3 票或连续 2 期同向 → 写入 a-3 队列 `anchor_queue.json` | queue entries | V§17 单锚点治理 |

## 调度表（S1→S2）
| 模式 | 子流程 | 代表 |
|---|---|---|
| M1 定价权稀缺供给 | sub/M1 | 茅台、古井 |
| M2 大众快消 | sub/M2 | 伊利、珀莱雅、贝泰妮、公牛 |
| M2b 连锁服务 | sub/M2b | 爱尔 |
| M3 制造规模成本 | sub/M3 | 美的、海尔、福耀、苏泊尔、星宇、亿联… |
| M4 强周期 | sub/M4 | 宁德 |
| M5a 水电 / M5b 核电 / M5c 环保特许 / M5d 电信 | sub/M5a…M5d | 长江 / 核电、广核 / 瀚蓝 / 移动 |
| M6 创新药 / M6b 器械 | sub/M6, sub/M6b | 恒瑞、百济 / 迈瑞、联影… |
| M7a 银行 / M7b 保险 | sub/M7a, sub/M7b | 招行、宁波 / 平安 |
| M8 平台分部 | sub/M8 | 腾讯 |
| M9 订单驱动 | sub/M9 | 北方华创、汇川、南瑞、中控… |
银行仍同时加载 live `bank-gates.md` / `bank-valuation-rules.md`（M7a 引用）。

## 统一输出接口要点
FV3 三档 = **除息**每股价值（第三个完整财年年末）；`dps_path` 单列；`multiple_anchor.{kind, multiple_basis, exit_date_convention=FY3_yearend}`；`fragility`（top-2 ±10%）；`kill_lines`；`forecast_ledger_entries`；`data_gaps`。M5*/M7* 另须 `roe`、`bvps`。L1 只吃 FV3 + dps_path。
**S4c / 稳定性（r3/r4）**：顺序 = S5a 内部 B20 → S4c → S5b 签发。`methods[]` ≥2 独立方法才可出 B20；`external_crosscheck`（来源 URL+fetched_at、同口径、只可压不可抬）；`range_buy`（B20=min(区间)；区间内任一不到价 → 未到价）。DISPLAY（R4–R6、外部 FV 对照）与 GATE（硬校验、双方法、区间买入、外部护栏）必须分栏，禁止把展示项当买入理由。

## 进化接口
a-3 每轮只取 `anchor_queue.json` 中一个叶子锚点；改动走 V§17（前后值、受影响名、回测、独立复核、版本、可回退）；V§20 用户保留项不得触碰。

## 进度反馈
`[workflow] <state>` · `[route] <模式>` · `[gate] validate: pass/fail(<anchor ids>)` · `[gate] S5a/S4c/S5b: pass/fail` · `[gate] dual_method/range_buy` · `[artifact] produced` · `[next]`
