---
name: v3-sub-M1
description: v3 子流程 M1 定价权·稀缺供给（量×价）。仅由 master 在 business_model=M1 时调度；草案未安装。
---

# 子流程 M1 · 定价权·稀缺供给（量×价）

状态：staged draft（t423u）。上游：`master/SKILL.md` S2 调度；下游：统一接口 `schema/plugin_output.v3.schema.json`。本子流程只决定 **FV3 怎么来**，不得改 L1（门槛、B20 公式、收益卖、仓位、置换）。

## 适用名单（master/ROUTING.csv）
| 代码 | 名称 | 评级 | 现行方法 | 方法错配 | 严重度 |
|---|---|---|---|---|---|
| 600519.SH | 贵州茅台 | A·暂定 | NI3×退出PE (normalized_midcycle) | 否 | 低 |
| 000596.SZ | 古井贡酒 | B-·暂定 | NI3×退出PE (conservative_flat_main) | 是 | 中 |

## 锚点
- L2 方法锚：A.L2.M1（draft）
- L3 参数锚：
  - `A.L3.M1.volume_yield` 出酒率区间 · draft
  - `A.L3.M1.base_liquor_lag` 基酒滞后年数 · draft
  - `A.L3.M1.price_mix` 出厂价/直销占比/批价差 · undefined
  - `A.L3.M1.series_liquor` 系列酒单列 · draft
  - `A.L3.M1.channel_inventory` 渠道库存月数 · draft
  - `A.L3.M1.exit_pe` 退出PE锚 · draft
  - `A.L3.M1.guidance_use` 管理层指引读取 · draft

## 步骤
1. **S1 资料清单**（缺项登记 `data_gap`，不得用估计值硬填）：年报产量/基酒产量、i茅台/直销收入、出厂价公告、批价（今日酒价等第三方，标注非一手）、年度营收指引
2. **S2 利润基数**：按 master V§2 清洗（核心/扣非、首年 = 9M+上年Q4、所有者盈余、应计/F-score、套保上限），再加本模式剥离项。
3. **S3 驱动表**：填下方模板；top-2 驱动必须标 `is_top2`，每个驱动带一手出处。核心驱动：量=4 年前基酒产量×出酒率(75–85%)；价=出厂价×直销占比+批价差；系列酒单列；渠道库存月数
4. **S4 估值方法**：NI3 = Σ(可售量×吨价) × (1−税金及附加率) − 费用 → ×(1−所得税) × 归母比例；与 FCF≈NI 交叉
5. **S5 倍数/折现锚**：自身 10 年窗口 P50，且 ≤ 同业高位；不因稀缺抬到窗口外（V§3：`exit_date_convention=FY3_yearend`，`multiple_basis` 同财年；非 PE 锚须声明替代口径）
   - **双方法（r4 / P3）**：默认方法对 = `same_FY_PE` + `reverse_DCF`；独立性 = 同年口径 PE vs 反推 DCF（不同价值身份）；禁止两个 PE 孪生。plugin `methods[]` ≥2，或 `dual_method_exception` ∈ {V20_pending, data_gap}+reason。
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
批价连续 2 季 < 出厂价；渠道库存 >6 个月；营收指引下调；直销占比下降

## 子型/特别说明
—
- L1 适配：L1 买点见 V§5-2：B20=(FV3_base+n×DPS_min3)/(1+h)^n（n=exit_multiple.n_years；禁止写死 ³）；B20 公式不变；熊景 = 价格冻结 + 量按基酒下限；卖点 = 收益卖（PE 上沿只作展示）

## L4 个股锚点（只补充/细化本子流程，不得推翻上层；每条须写来源、依据、失效条件）
| 锚点 | 名称 | 状态 | 说明 |
|---|---|---|---|
| `A.L4.moutai.series_liquor` | 系列酒单独估 | gap | 茅台酒与系列酒分开量×价；系列酒吨价承压单列 |
| `A.L4.moutai.batch_price` | 飞天批价/出厂价差 | draft | 批价-出厂价差作渠道利润与提价空间锚 |
| `A.L4.moutai.base_liquor_capacity` | 基酒产能→四年后可售 | draft | 2025茅台酒基酒5.85万吨(+3.9%)，五年陈酿约束 |
| `A.L4.moutai.direct_sales_mix` | 直营占比 | gap | i茅台/直营占比对吨价的抬升 |
| `A.L4.moutai.contract_liab` | 合同负债塌缩 | draft | 合同负债作收入前瞻 |
| `A.L4.gujing.nianfen_mix` | 年份原浆吨价/结构 | draft | 年份原浆出厂吨价 |
| `A.L4.gujing.anhui_competition` | 徽酒省内竞争/渠道库存 | gap | 省内外拆分、渠道库存 |
| `A.L4.gujing.contract_liab` | 合同负债去库 | draft | 合同负债路径 |


## 从旧主规则下放到本子流程的条款（RULE_MAPPING.csv v3_sub 列）
- 无


## 输出（统一接口，摘要）
`business_model, plugin_version, as_of, currency, base_year, drivers[], FV3{bear,base,bull}, FV3_build, dps_path, multiple_anchor{method, multiple_basis, exit_date_convention}, fragility, kill_lines[], forecast_ledger_entries[], notes_double_count, data_gaps[]` — 全字段与必填见 schema。
