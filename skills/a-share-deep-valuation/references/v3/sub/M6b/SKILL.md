---
name: v3-sub-M6b
description: v3 子流程 M6b 医疗器械（集采后量价 + 出海）。仅由 master 在 business_model=M6b 时调度；草案未安装。
---

# 子流程 M6b · 医疗器械（集采后量价 + 出海）

状态：staged draft（t423u）。上游：`master/SKILL.md` S2 调度；下游：统一接口 `schema/plugin_output.v3.schema.json`。本子流程只决定 **FV3 怎么来**，不得改 L1（门槛、B20 公式、收益卖、仓位、置换）。

## 适用名单（master/ROUTING.csv）
| 代码 | 名称 | 评级 | 现行方法 | 方法错配 | 严重度 |
|---|---|---|---|---|---|
| 300760.SZ | 迈瑞医疗 | B+·暂定 | NI3×退出PE (conservative_flat_main) | 是 | 中 |
| 688271.SH | 联影医疗 | B·暂定 | NI3×退出PE (recovery_path) | 是 | 中 |
| 688050.SH | 爱博医疗 | B·暂定 | NI3×退出PE (normalized_midcycle) | 否 | 低 |
| 300595.SZ | 欧普康视 | B-·暂定 | NI3×退出PE (normalized_midcycle) | 否 | 低 |
| 688617.SH | 惠泰医疗 | B·暂定 | NI3×退出PE (normalized_midcycle) | 否 | 低 |

## 锚点
- L2 方法锚：A.L2.M6b（draft）
- L3 参数锚：
  - `A.L3.M6b.vbp_cut` 集采降幅假设 · undefined
  - `A.L3.M6b.overseas_growth` 海外增速 · draft
  - `A.L3.M6b.post_vbp_window` 集采后PE窗口 · draft

## 步骤
1. **S1 资料清单**（缺项登记 `data_gap`，不得用估计值硬填）：年报分产线收入、集采结果公告、招投标统计
2. **S2 利润基数**：按 master V§2 清洗（核心/扣非、首年 = 9M+上年Q4、所有者盈余、应计/F-score、套保上限），再加本模式剥离项。
3. **S3 驱动表**：填下方模板；top-2 驱动必须标 `is_top2`，每个驱动带一手出处。核心驱动：国内招标量、集采降幅、海外收入、产品线毛利
4. **S4 估值方法**：NI3 = Σ产线 × 集采后量价 + 海外；集采后利润率锚同业
5. **S5 倍数/折现锚**：自身窗口 P50（集采后窗口优先）（V§3：`exit_date_convention=FY3_yearend`，`multiple_basis` 同财年；非 PE 锚须声明替代口径）
   - **双方法（r4 / P3）**：默认方法对 = `same_FY_PE` + `reverse_DCF`；独立性 = 同年口径 PE vs 反推 DCF；禁止两个 PE 孪生。plugin `methods[]` ≥2，或 `dual_method_exception` ∈ {V20_pending, data_gap}+reason。
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





## Kill-lines（可证伪、带阈值、带数据源）
集采降幅 >预期；海外增速 <10% 两年；国内招标连续 2 季负增长

## 子型/特别说明
—
- L1 适配：L1 买点见 V§5-2：B20=(FV3_base+n×DPS_min3)/(1+h)^n（n=exit_multiple.n_years；禁止写死 ³）；原 L572 耗材 ASP 句归入

## L4 个股锚点（只补充/细化本子流程，不得推翻上层；每条须写来源、依据、失效条件）
| 锚点 | 名称 | 状态 | 说明 |
|---|---|---|---|
| `A.L4.mindray.vbp` | 集采/国内设备 | gap | 分产线集采降幅 |
| `A.L4.mindray.goodwill` | 并购商誉 | draft | 商誉减值敏感 |
| `A.L4.mindray.fx` | 汇兑 | gap | 海外收入汇兑 |


## 从旧主规则下放到本子流程的条款（RULE_MAPPING.csv v3_sub 列）
- 无


## 输出（统一接口，摘要）
`business_model, plugin_version, as_of, currency, base_year, drivers[], FV3{bear,base,bull}, FV3_build, dps_path, multiple_anchor{method, multiple_basis, exit_date_convention}, fragility, kill_lines[], forecast_ledger_entries[], notes_double_count, data_gaps[]` — 全字段与必填见 schema。
