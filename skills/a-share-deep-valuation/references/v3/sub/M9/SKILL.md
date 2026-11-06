---
name: v3-sub-M9
description: v3 子流程 M9 订单/合同负债驱动成长。仅由 master 在 business_model=M9 时调度；草案未安装。
---

# 子流程 M9 · 订单/合同负债驱动成长

状态：staged draft（t423u）。上游：`master/SKILL.md` S2 调度；下游：统一接口 `schema/plugin_output.v3.schema.json`。本子流程只决定 **FV3 怎么来**，不得改 L1（门槛、B20 公式、收益卖、仓位、置换）。

## 适用名单（master/ROUTING.csv）
| 代码 | 名称 | 评级 | 现行方法 | 方法错配 | 严重度 |
|---|---|---|---|---|---|
| 300124.SZ | 汇川技术 | B-·暂定 | NI3×退出PE (normalized_midcycle) | 是 | 中 |
| 688777.SH | 中控技术 | B·暂定 | NI3×退出PE (recovery_path) | 是 | 中 |
| 688017.SH | 绿的谐波 | B·暂定 | NI3×退出PE (peak_fade) | 否 | 低 |
| 603259.SH | 药明康德 | B+·暂定 | NI3×退出PE (peak_fade) | 是 | 中 |
| 603606.SH | 东方电缆 | B·暂定 | NI3×退出PE (recovery_path) | 否 | 低 |
| 002371.SZ | 北方华创 | B+·暂定 | NI3×退出PE (peak_fade) | 是 | 中 |
| 688012.SH | 中微公司 | B+·暂定 | NI3×退出PE (peak_fade) | 是 | 中 |
| 688072.SH | 拓荆科技 | B·暂定 | NI3×退出PE (peak_fade) | 是 | 中 |
| 688120.SH | 华海清科 | B·暂定 | NI3×退出PE (peak_fade) | 是 | 中 |
| 688082.SH | 盛美上海 | B·暂定 | NI3×退出PE (peak_fade) | 是 | 中 |
| 600406.SH | 国电南瑞 | B·暂定 | NI3×退出PE (normalized_midcycle) | 否 | 低 |
| 688188.SH | 柏楚电子 | B+·暂定 | NI3×退出PE (normalized_midcycle) | 否 | 低 |

## 锚点
- L2 方法锚：A.L2.M9（draft）
- L3 参数锚：
  - `A.L3.M9.backlog_conversion` backlog 转化率 · undefined
  - `A.L3.M9.peak_fade_calib` peak_fade 覆盖率校准 · draft
  - `A.L3.M9.exit_pe` PE 锚 · draft
  - `A.L3.M9.semi_dual_tag` 半导体双标 L539-542 · draft
  - `A.L3.M9.subtypes` 子型拆分 · undefined

## 步骤
1. **S1 资料清单**（缺项登记 `data_gap`，不得用估计值硬填）：年报/季报合同负债、存货（发出商品）、订单公告、SEMI/WFE 数据
2. **S2 利润基数**：按 master V§2 清洗（核心/扣非、首年 = 9M+上年Q4、所有者盈余、应计/F-score、套保上限），再加本模式剥离项。
3. **S3 驱动表**：填下方模板；top-2 驱动必须标 `is_top2`，每个驱动带一手出处。核心驱动：合同负债、在手订单、行业 capex 周期、国产化率、毛利率
4. **S4 估值方法**：NI3 = (期初 backlog 确认 + 新签) × 毛利 − 费用；peak_fade 基准须用 backlog 覆盖率校准
5. **S5 倍数/折现锚**：全球同业中枢 PE 与自身窗口取低（V§3：`exit_date_convention=FY3_yearend`，`multiple_basis` 同财年；非 PE 锚须声明替代口径）
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
合同负债同比转负；应收增速 >收入增速 20pp；毛利率下滑 >3pp

## 子型/特别说明
—
- L1 适配：L1 买点见 V§5-2：B20=(FV3_base+n×DPS_min3)/(1+h)^n（n=exit_multiple.n_years；禁止写死 ³）；原 L539–542 半导体双标、L200 strict_cycle_lock 引用

## L4 个股锚点（只补充/细化本子流程，不得推翻上层；每条须写来源、依据、失效条件）
| 锚点 | 名称 | 状态 | 说明 |
|---|---|---|---|
| — | 本子流程名单尚未建 L4（仅持仓/重点票已建） | gap | |


## 从旧主规则下放到本子流程的条款（RULE_MAPPING.csv v3_sub 列）
- ### 半导体设备 · 质量与周期双标（Helmer power + SEMI 数据 + 北方华创  L539-L539：### 半导体设备 · 质量与周期双标（Helmer power + SEMI 数据 + 北方华创 H1 2026；2026-10-26 进
- ### 半导体设备 · 质量与周期双标（Helmer power + SEMI  第1项 L540-L540：1. **semi_equip_dual_tag（强制，车道1+4）**：正式池半导体设备名（北方华创/中微/拓荆/华海清科/盛美）须同时写


## 输出（统一接口，摘要）
`business_model, plugin_version, as_of, currency, base_year, drivers[], FV3{bear,base,bull}, FV3_build, dps_path, multiple_anchor{method, multiple_basis, exit_date_convention}, fragility, kill_lines[], forecast_ledger_entries[], notes_double_count, data_gaps[]` — 全字段与必填见 schema。
