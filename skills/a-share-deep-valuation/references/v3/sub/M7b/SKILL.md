---
name: v3-sub-M7b
description: v3 子流程 M7b 保险·资产负债表（P/EV + NBV）。仅由 master 在 business_model=M7b 时调度；草案未安装。
---

# 子流程 M7b · 保险·资产负债表（P/EV + NBV）

状态：staged draft（t423u；**r4 t430u 去污**：删除银行条文；NBV 空缺保留）。上游：`master/SKILL.md` S2 调度；下游：统一接口 `schema/plugin_output.v3.schema.json`。本子流程只决定 **FV3 怎么来**，不得改 L1（门槛、B20 公式、收益卖、仓位、置换）。

## 适用名单（master/ROUTING.csv）
| 代码 | 名称 | 评级 | 现行方法 | 方法错配 | 严重度 |
|---|---|---|---|---|---|
| 601318.SH | 中国平安 | B-·暂定 | NI3×退出PE (normalized_midcycle) | 是 | 高 |

## 锚点
- L2 方法锚：A.L2.M7（draft）
- L3 参数锚：
  - `A.L3.M7.ins.pev` 保险 P/EV 锚 · draft
  - `A.L3.M7.ins.nbv_mult` NBV 倍数 · **空缺（V§20-5，不编造）** → 标 `nbv_mult_missing`
  - `A.L3.M7.ins.inv_yield` 投资收益率假设 · undefined

## 步骤
1. **S1 资料清单**（缺项登记 `data_gap`，不得用估计值硬填）：年报/内含价值（EV）报告、NBV、投资收益率假设披露、偿付能力监管指标
2. **S2 利润基数**：按 master V§2 清洗（核心/扣非、首年 = 9M+上年Q4、所有者盈余、应计/F-score、套保上限），再加本模式剥离项。
3. **S3 驱动表**：填下方模板；top-2 驱动必须标 `is_top2`，每个驱动带一手出处。核心驱动：**EV、NBV、投资收益率假设、新业务价值率、偿付能力**（本子流程不含银行 BVPS/净息差/不良）
4. **S4 估值方法**：FV3 = EV3 × P/EV 锚 + 当年 NBV×倍数（或 EV 增长内生）。**NBV 倍数空缺时**不得编造倍数；只用「EV 内生增长」近似并标 `nbv_mult_missing`，必要时 `dual_method_exception.code=V20_pending`。
5. **S5 倍数/折现锚**：保险 P/EV 自身窗口 P50（V§3：`exit_date_convention=FY3_yearend`，`multiple_basis` 同财年；非 PE 锚须声明替代口径）
   - **双方法（r4 / P3）**：默认方法对 = `P_EV` + `EV_growth`（NBV 腿待 V§20）；独立性 = 不同主驱动（倍数 vs 内生增长），禁止两个 PE 孪生。
6. **S6 三情景**：熊=top-2 驱动取周期下沿 + 倍数取锚下沿；基=中位；牛=上沿。熊 NI3 须 ≤ 基率中位路径（r19 P-X4 不变）。
7. **S7 脆弱性**：top-2 驱动各 ±10% 及同时；任一使「现价 ≤B20」翻转 → `fragile=true`。
8. **S8 断言**：跑 `scripts/validate_anchors.py`（见下「硬断言」）；FAIL 不得交回 master。
9. **S9 输出**：按统一接口写 `plugin_output.json`（FV3 三档为**除息**价值，`dps_path` 单列，`stack_into_B20` 由 L1 按 live/用户决定）。
10. **S10 预测登记**：FY+1 核心 NI、top-2 驱动、NI3 P10/P50/P90 + 归因锚点 id 写入 `forecast_ledger_entries`。

## 驱动表模板
| driver | unit | bear | base | bull | source(一手+页/行) | is_top2 | anchor_id |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

## 硬断言（validate_anchors.py）
- 通用：exit_date_convention=FY3_yearend；PE 锚 multiple_basis=same_FY；熊≤基≤牛；profit_base 字段齐 + 应计/F-score/套保上限（R3，阈值待回测）；business_model 与路由一致。
- M5/M7：ROE 基准 ≤ min(三年均值, 最新年化)；熊 ROE ≤ 历史最差年；BVPS 日期为价格日前最新报告并声明（若本卡使用 PB 腿）。
- 双方法：methods≥2 或 dual_method_exception；NBV 空缺须 `nbv_mult_missing`。

## Kill-lines（可证伪、带阈值、带数据源）
NBV 负增长 2 年；投资收益假设下调；偿付能力跌破监管/内部下限

## 子型/特别说明
- 保险：FV3 = EV3 × P/EV 锚 + NBV×倍数；**NBV 倍数空缺（A.L3.M7.ins.nbv_mult，V§20-5），投资收益率假设 undefined**——不编造；未定前只能用「EV 内生增长」近似并标 `nbv_mult_missing`，不得替换现行卡。
- L1 适配：买点公式见 **V§5-2**（`n=exit_multiple.n_years`）；股息叠加口径同 M5（待拍板）；禁止写死 `+3×DPS` / `1.2³`。

## L4 个股锚点（只补充/细化本子流程，不得推翻上层；每条须写来源、依据、失效条件）
| 锚点 | 名称 | 状态 | 说明 |
|---|---|---|---|
| — | 本子流程名单尚未建 L4（仅持仓/重点票已建） | gap | |

## 从旧主规则下放到本子流程的条款（RULE_MAPPING.csv v3_sub 列）
- ### NI/FCF 双轨（P3 fcf_ni_dual_track · 202 第8项 L592-L593）

## 输出（统一接口，摘要）
`business_model, plugin_version, as_of, currency, base_year, drivers[], FV3{bear,base,bull}, FV3_build, dps_path, multiple_anchor, methods[]|dual_method_exception, fragility, kill_lines[], forecast_ledger_entries[], notes_double_count, data_gaps[]` — 全字段与必填见 schema。
