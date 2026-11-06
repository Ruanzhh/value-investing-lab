---
name: v3-sub-M6
description: v3 子流程 M6 创新药（存量 + 管线 rNPV）。仅由 master 在 business_model=M6 时调度；草案未安装。
---

# 子流程 M6 · 创新药（存量 + 管线 rNPV）

状态：staged draft（t423u）。上游：`master/SKILL.md` S2 调度；下游：统一接口 `schema/plugin_output.v3.schema.json`。本子流程只决定 **FV3 怎么来**，不得改 L1（门槛、B20 公式、收益卖、仓位、置换）。

## 适用名单（master/ROUTING.csv）
| 代码 | 名称 | 评级 | 现行方法 | 方法错配 | 严重度 |
|---|---|---|---|---|---|
| 600276.SH | 恒瑞医药 | B+·暂定 | NI3×退出PE (normalized_midcycle) | 是 | 高 |
| 688235.SH | 百济神州 | B·暂定 | NI3×退出PE (normalized_midcycle) | 是 | 高 |

## 锚点
- L2 方法锚：A.L2.M6（draft）
- L3 参数锚：
  - `A.L3.M6.pos_table` 各阶段成功概率表 · spec_drafted
  - `A.L3.M6.milestone_haircut` 里程碑折扣 · draft
  - `A.L3.M6.peak_sales` 峰值销售曲线 · undefined
  - `A.L3.M6.rd_cut_flag` 研发削减警示 §60 · draft

## 步骤
1. **S1 资料清单**（缺项登记 `data_gap`，不得用估计值硬填）：年报产品收入、CDE/ClinicalTrials 登记、授权公告、医保目录
2. **S2 利润基数**：按 master V§2 清洗（核心/扣非、首年 = 9M+上年Q4、所有者盈余、应计/F-score、套保上限），再加本模式剥离项。
3. **S3 驱动表**：填下方模板；top-2 驱动必须标 `is_top2`，每个驱动带一手出处。核心驱动：已上市产品销售与峰值曲线、管线阶段与成功率、授权首付/里程碑、医保谈判降价
4. **S4 估值方法**：FV3 = 存量业务 NI3×PE + Σ管线 rNPV（III 期/NDA 按行业基准概率；I/II 期只进牛景）；授权收入按已到账计，里程碑打 50%
5. **S5 倍数/折现锚**：存量业务按自身窗口 P50；未盈利者 EV/Sales 只交叉（V§3：`exit_date_convention=FY3_yearend`，`multiple_basis` 同财年；非 PE 锚须声明替代口径）
   - **双方法（r4 / P3）**：默认方法对 = `same_FY_PE` + `rNPV_SOTP`；独立性 = 存量 PE vs 管线 rNPV/SOTP；禁止两个 PE 孪生。plugin `methods[]` ≥2，或 `dual_method_exception` ∈ {V20_pending, data_gap}+reason。
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



- M6：管线概率只用 R7 pos_table（BIO 2011–2020）；肿瘤分期成功率空缺不得自编。

## Kill-lines（可证伪、带阈值、带数据源）
关键 III 期失败；医保降价 >预期 20pp；研发投入同比下降且调整后利润低于报表 20%（原 §60）

## 子型/特别说明
—
- L1 适配：L1 买点见 V§5-2：B20=(FV3_base+n×DPS_min3)/(1+h)^n（n=exit_multiple.n_years；禁止写死 ³）；原 L722–726 AA1/AA2、§60 归入

## L4 个股锚点（只补充/细化本子流程，不得推翻上层；每条须写来源、依据、失效条件）
| 锚点 | 名称 | 状态 | 说明 |
|---|---|---|---|
| — | 本子流程名单尚未建 L4（仅持仓/重点票已建） | gap | |


## 从旧主规则下放到本子流程的条款（RULE_MAPPING.csv v3_sub 列）
- 无


## 输出（统一接口，摘要）
`business_model, plugin_version, as_of, currency, base_year, drivers[], FV3{bear,base,bull}, FV3_build, dps_path, multiple_anchor{method, multiple_basis, exit_date_convention}, fragility, kill_lines[], forecast_ledger_entries[], notes_double_count, data_gaps[]` — 全字段与必填见 schema。
