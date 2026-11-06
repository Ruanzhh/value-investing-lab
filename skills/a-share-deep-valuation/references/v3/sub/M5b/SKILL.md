---
name: v3-sub-M5b
description: v3 子流程 M5b 公用事业·核电/重资本扩张（类债，PB-ROE/DDM）。仅由 master 在 business_model=M5b 时调度；草案未安装。
---

# 子流程 M5b · 公用事业·核电/重资本扩张（类债，PB-ROE/DDM）

状态：staged draft（t423u）。上游：`master/SKILL.md` S2 调度；下游：统一接口 `schema/plugin_output.v3.schema.json`。本子流程只决定 **FV3 怎么来**，不得改 L1（门槛、B20 公式、收益卖、仓位、置换）。

## 适用名单（master/ROUTING.csv）
| 代码 | 名称 | 评级 | 现行方法 | 方法错配 | 严重度 |
|---|---|---|---|---|---|
| 601985.SH | 中国核电 | B+·暂定 | NI3×退出PE (normalized_midcycle) | 是 | 高 |
| 003816.SZ | 中国广核 | B+·暂定 | NI3×退出PE (recovery_path) | 是 | 高 |

## 锚点
- L2 方法锚：A.L2.M5（draft）
- L3 参数锚：
  - `A.L3.M5.roe_take_lower` ROE 取低规则 · spec_drafted
  - `A.L3.M5.rf` 无风险利率 · draft
  - `A.L3.M5.erp.M5b` ERP 核电 · draft
  - `A.L3.M5.g` 永续 g · draft
  - `A.L3.M5.bvps_basis` BVPS 基准日 · error
  - `A.L3.M5.finite_dcf` 有限期特许 DCF · spec_drafted
  - `A.L3.M5.bear_roe` 熊景 ROE · error

## 步骤
1. **S1 资料清单**（缺项登记 `data_gap`，不得用估计值硬填）：年报 BPS/ROE/分红政策原文、交易所分红实施公告、中债 10Y、发电量公告、电价政策
2. **S2 利润基数**：按 master V§2 清洗（核心/扣非、首年 = 9M+上年Q4、所有者盈余、应计/F-score、套保上限），再加本模式剥离项。
3. **S3 驱动表**：填下方模板；top-2 驱动必须标 `is_top2`，每个驱动带一手出处。核心驱动：ROE（受监管/电价）、BVPS 增长（留存率）、分红率政策、10Y 国债、风险溢价、发电量/来水/利用小时
4. **S4 估值方法**：FV3 = 合理 P/B × BVPS3；合理 P/B=(ROE−g)/(r−g)；r=10Y+ERP（M5a 4.5 / M5b 5.5 / M5c 6.5pp，熊+1/牛−1）；g 1/2/2.5%；BVPS3=BVPS0×(1+ROE×(1−payout))³。等价于可持续派息 DDM。M5c 特许经营期有限 → 须另做有限期 DCF 交叉，取低
5. **S5 倍数/折现锚**：ROE 基准=近 3 年均值与最新年化取低；不得用窗口 PE（类债资产 PE 窗口受利率周期主导）（V§3：`exit_date_convention=FY3_yearend`，`multiple_basis` 同财年；非 PE 锚须声明替代口径）
   - **双方法（r4 / P3）**：默认方法对 = `PB_ROE` + `DDM`；独立性 = PB-ROE vs 可持续派息 DDM；禁止两个 PE 孪生。plugin `methods[]` ≥2，或 `dual_method_exception` ∈ {V20_pending, data_gap}+reason。
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
- M5/M7：ROE 基准 ≤ min(三年均值, 最新年化)；熊 ROE ≤ 历史最差年；BVPS 日期为价格日前最新报告并声明。




## Kill-lines（可证伪、带阈值、带数据源）
电价下调 >10%；10Y 上行 >100bp；分红率跌破政策下限；ROE 连续 2 年 < r

## 子型/特别说明
- 子型参数：ERP 5.5pp（A.L3.M5.erp.M5b）；重资本扩张 → ROE 基准必须执行「三年均值与最新年化取低」（核电 8.2%→6.7% 错误即此锚，A.L3.M5.roe_take_lower 状态 spec_drafted，validate 硬校验）。
- L1 适配：L1 买点见 V§5-2：B20=(FV3_base+n×DPS_min3)/(1+h)^n（n=exit_multiple.n_years；禁止写死 ³）；统一叠 3×DPS_min3（待拍板）；**是否保留 20% 三年门槛 = 用户决策**；原 L69/L71 例外、L170、§141 归入

## L4 个股锚点（只补充/细化本子流程，不得推翻上层；每条须写来源、依据、失效条件）
| 锚点 | 名称 | 状态 | 说明 |
|---|---|---|---|
| — | 本子流程名单尚未建 L4（仅持仓/重点票已建） | gap | |


## 从旧主规则下放到本子流程的条款（RULE_MAPPING.csv v3_sub 列）
- ### NI/FCF 双轨（P3 fcf_ni_dual_track · 202 第8项 L592-L593：8. **看板**：列 `FCF_B20`；gate=pass 显示数字；gate≠pass 显示「数字 仅参考」；银行写「银行不适用」；分


## 输出（统一接口，摘要）
`business_model, plugin_version, as_of, currency, base_year, drivers[], FV3{bear,base,bull}, FV3_build, dps_path, multiple_anchor{method, multiple_basis, exit_date_convention}, fragility, kill_lines[], forecast_ledger_entries[], notes_double_count, data_gaps[]` — 全字段与必填见 schema。
