---
name: v3-sub-M5d
description: v3 子流程 M5d 电信运营·类债（PB-ROE/DDM）。仅由 master 在 business_model=M5d 时调度；草案未安装。
---

# 子流程 M5d · 电信运营·类债（PB-ROE/DDM）

状态：staged draft（t423u；**r4 t430u 去污**：资料/驱动改为电信，去掉公用发电量/来水串味）。上游：`master/SKILL.md` S2 调度；下游：统一接口 `schema/plugin_output.v3.schema.json`。本子流程只决定 **FV3 怎么来**，不得改 L1（门槛、B20 公式、收益卖、仓位、置换）。

## 适用名单（master/ROUTING.csv）
| 代码 | 名称 | 评级 | 现行方法 | 方法错配 | 严重度 |
|---|---|---|---|---|---|
| 600941.SH | 中国移动 | B+·暂定 | NI3×退出PE (status_quo_low_growth) | 是 | 中 |

## 锚点
- L2 方法锚：A.L2.M5（draft）
- L3 参数锚：
  - `A.L3.M5.roe_take_lower` ROE 取低规则 · spec_drafted
  - `A.L3.M5.rf` 无风险利率 · draft
  - `A.L3.M5.erp.M5d` ERP 电信 · **undefined（V§20-3，不编造）**
  - `A.L3.M5.g` 永续 g · draft
  - `A.L3.M5.bvps_basis` BVPS 基准日 · error
  - `A.L3.M5.bear_roe` 熊景 ROE · error

## 步骤
1. **S1 资料清单**（缺项登记 `data_gap`，不得用估计值硬填）：年报 BPS/ROE/分红政策原文、交易所分红实施公告、中债 10Y、**ARPU**、**用户/订户数**（移动/宽带/政企）、**5G/网络 capex**、**铁塔/租赁成本**、监管资费政策
2. **S2 利润基数**：按 master V§2 清洗（核心/扣非、首年 = 9M+上年Q4、所有者盈余、应计/F-score、套保上限），再加本模式剥离项。
3. **S3 驱动表**：填下方模板；top-2 驱动必须标 `is_top2`，每个驱动带一手出处。核心驱动：**ARPU、用户/订户、5G/网络 capex、铁塔成本、分红率政策、ROE、BVPS 增长（留存率）、10Y 国债、风险溢价（ERP 电信 = V§20 未定）**
4. **S4 估值方法**：FV3 = 合理 P/B × BVPS3；合理 P/B=(ROE−g)/(r−g)；r=10Y+ERP_M5d（**ERP 未定义 → 不得签发正式 B20，可出并列参考并标 `dual_method_exception.code=V20_pending`**）；g 结构位与 M5 族一致但不抄公用电价驱动。等价可持续派息 **DDM** 作交叉。
5. **S5 倍数/折现锚**：ROE 基准=近 3 年均值与最新年化取低；不得用窗口 PE（类债资产 PE 窗口受利率周期主导）（V§3：`exit_date_convention=FY3_yearend`，`multiple_basis` 同财年；非 PE 锚须声明替代口径）
   - **双方法（r4 / P3）**：默认方法对 = `PB_ROE` + `DDM`；独立性 = 不同价值身份（账面权益 vs 股息折现），禁止两个 PE 孪生。`methods[]` ≥2，或 `dual_method_exception` ∈ {V20_pending, data_gap}+reason。
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
- 双方法：methods≥2 或 dual_method_exception。

## Kill-lines（可证伪、带阈值、带数据源）
ARPU 连续 2 季同比 ≤−5%；移动用户净减连续 2 季；5G/网络 capex 指引上修且 FCF 转负两季；分红率跌破政策下限；ROE 连续 2 年 < r（r 在 ERP 未定前仅作监控）

## 子型/特别说明
- 子型参数：ERP **未定义**（A.L3.M5.erp.M5d undefined；V§20-3）；未定前 FV3 只出并列参考，不替换现行卡；可标 `dual_method_exception.code=V20_pending`。
- 注：MAPPING 旧标签「M5b 电信」与插件 M5b=核电冲突，v3 子码为 **M5d**（ROUTING.sub 已是 M5d；mapping_label r4 对齐）。
- L1 适配：买点公式见 **V§5-2**，`n=exit_multiple.n_years`，`B20=(FV3_base+n×DPS_min3)/(1+h)^n`（禁止写死 ³）；是否叠息 / 20% 三年门槛 = 用户决策（V§20）。

## L4 个股锚点（只补充/细化本子流程，不得推翻上层；每条须写来源、依据、失效条件）
| 锚点 | 名称 | 状态 | 说明 |
|---|---|---|---|
| — | 本子流程名单尚未建 L4（仅持仓/重点票已建） | gap | |

## 从旧主规则下放到本子流程的条款（RULE_MAPPING.csv v3_sub 列）
- ### NI/FCF 双轨（P3 fcf_ni_dual_track · 202 第8项 L592-L593）

## 输出（统一接口，摘要）
`business_model, plugin_version, as_of, currency, base_year, drivers[], FV3{bear,base,bull}, FV3_build, dps_path, multiple_anchor, methods[]|dual_method_exception, fragility, kill_lines[], forecast_ledger_entries[], notes_double_count, data_gaps[]` — 全字段与必填见 schema。
