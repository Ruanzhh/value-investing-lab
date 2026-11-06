---
name: v3-sub-M3
description: v3 子流程 M3 制造业·规模成本（分部+同业锚+套保剥离）。仅由 master 在 business_model=M3 时调度；草案未安装。
---

# 子流程 M3 · 制造业·规模成本（分部+同业锚+套保剥离）

状态：staged draft（t423u）。上游：`master/SKILL.md` S2 调度；下游：统一接口 `schema/plugin_output.v3.schema.json`。本子流程只决定 **FV3 怎么来**，不得改 L1（门槛、B20 公式、收益卖、仓位、置换）。

## 适用名单（master/ROUTING.csv）
| 代码 | 名称 | 评级 | 现行方法 | 方法错配 | 严重度 |
|---|---|---|---|---|---|
| 000333.SZ | 美的集团 | B+·暂定 | NI3×退出PE (conservative_flat_main) | 是 | 高 |
| 600660.SH | 福耀玻璃 | B+·暂定 | NI3×退出PE (normalized_midcycle) | 否 | 低 |
| 300628.SZ | 亿联网络 | B+·暂定 | NI3×退出PE (normalized_midcycle) | 否 | 低 |
| 002050.SZ | 三花智控 | B·暂定 | NI3×退出PE (normalized_midcycle) | 是 | 中 |
| 002032.SZ | 苏泊尔 | B·暂定 | NI3×退出PE (normalized_midcycle) | 否 | 低 |
| 601799.SH | 星宇股份 | B·暂定 | NI3×退出PE (recovery_path) | 否 | 低 |
| 600690.SH | 海尔智家 | B+·暂定 | NI3×退出PE (recovery_path) | 是 | 中 |

## 锚点
- L2 方法锚：A.L2.M3（draft）
- L3 参数锚：
  - `A.L3.M3.segments` 分部切分 · draft
  - `A.L3.M3.peer_margin` 同业利润率锚 · draft
  - `A.L3.M3.hedge_strip` 套保/汇兑剥离 · draft
  - `A.L3.M3.calib_factor` 校准系数 · draft
  - `A.L3.M3.fx_persistence` 汇率冲击持续性假设 · draft
  - `A.L3.M3.exit_pe` 退出PE锚 · draft
  - `A.L3.M3.tob_reinvest` ToB 再投入 · draft

## 步骤
1. **S1 资料清单**（缺项登记 `data_gap`，不得用估计值硬填）：年报分产品/分地区收入毛利、季报非经常性损益表与财务费用、衍生金融资产附注、同业（格力/海尔/海信）年报
2. **S2 利润基数**：按 master V§2 清洗（核心/扣非、首年 = 9M+上年Q4、所有者盈余、应计/F-score、套保上限），再加本模式剥离项。
3. **S3 驱动表**：填下方模板；top-2 驱动必须标 `is_top2`，每个驱动带一手出处。核心驱动：分部（内销/外销/ToB）收入增速、分部毛利率、费用率、原材料、汇率与套保
4. **S4 估值方法**：Step1 口径：扣非 ± 汇兑（财务费用中非利息部分）± 已识别套保收益（处置衍生品投资收益+衍生资产公允变动）；权益类公允价值变动不还原。Step2 基年 = 9M 实际 + 上年 Q4（P1）。Step3 NI3 = Σ分部收入×(分部毛利−费用率)×校准系数（基年核心利润 / 基年贡献）
5. **S5 倍数/折现锚**：自身窗口 P50；同业 PE 中位只作上限，不作抬升；超额净现金单列加回（扣三年计划派息防双计）（V§3：`exit_date_convention=FY3_yearend`，`multiple_basis` 同财年；非 PE 锚须声明替代口径）
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
分部毛利率偏离同业 >2pp 且持续 2 季；海外收入同比 <0 两季；核心利润（扣非+套保经济对冲）连续两季同比 <−10%

## 子型/特别说明
—
- L1 适配：L1 买点见 V§5-2：B20=(FV3_base+n×DPS_min3)/(1+h)^n（n=exit_multiple.n_years；禁止写死 ³）；原 L597 tob_reinvestment_vs_A、L614 scale_economics_shared 归入

## L4 个股锚点（只补充/细化本子流程，不得推翻上层；每条须写来源、依据、失效条件）
| 锚点 | 名称 | 状态 | 说明 |
|---|---|---|---|
| `A.L4.midea.kuka_tob` | 库卡/ToB 再投入与商誉 | draft | ToB 单列低毛利+商誉风险 |
| `A.L4.midea.export_fx` | 外销汇兑敞口 | error | 外销收入占比×汇率；套保经济对冲拆分 |
| `A.L4.midea.domestic_subsidy` | 内销国补透支 | draft | 内销国补后下行段 |
| `A.L4.fuyao.us_phase2` | 美国二期利用率 | gap | 海外属地化工厂利润率 |
| `A.L4.fuyao.fx_strip` | 汇兑剔除 | draft | 剔汇兑后主业 |
| `A.L4.haier.casarte` | 卡萨帝溢价 | gap | 高端品牌份额+均价 |
| `A.L4.haier.overseas_wc` | 海外营运资金/商誉 | draft | FCF₃≈NI3×0.85 |
| `A.L4.xingyu.top5_customers` | 前五客户集中度 | draft | 前五客户收入 |
| `A.L4.xingyu.hshare_dilution` | H股稀释 | draft | H股发行稀释压测 |
| `A.L4.xingyu.lamp_asp` | 单车灯具价值 | draft | 智能 ASP 与年降 |
| `A.L4.yealink.tariff_fx` | 关税/汇兑 | draft | 海外欧+美≈80.5% |
| `A.L4.yealink.meeting_curve` | 会议第二曲线 | gap | 三线拆分（桌面/会议/云办公） |


## 从旧主规则下放到本子流程的条款（RULE_MAPPING.csv v3_sub 列）
- ### 三腿凳 · Power 类型 · 质量 edge 处理（Akre Goo 第4项 L531-L532：4. **scale_economics_shared_note（Sleep，可选）**：`durable_low_cost` 证据可加「规
- ### 资本配置序列 · 每股价值分母（Gayner Markel 2025 / 第1项 L595-L595：1. **capital_allocation_sequence_note（触管理层/ToB扩张/回购分红卡补，车道1）**：领导层质量证据
- ### 规模节省回馈 vs 近端 NI 下滑 · 期权回购净稀释（Nick Sl 第1项 L614-L614：1. **scale_economics_shared_vs_ni_dip（强制加固 scale_economics_shared_note


## 输出（统一接口，摘要）
`business_model, plugin_version, as_of, currency, base_year, drivers[], FV3{bear,base,bull}, FV3_build, dps_path, multiple_anchor{method, multiple_basis, exit_date_convention}, fragility, kill_lines[], forecast_ledger_entries[], notes_double_count, data_gaps[]` — 全字段与必填见 schema。
