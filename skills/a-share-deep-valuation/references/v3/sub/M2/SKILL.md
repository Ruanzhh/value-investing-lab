---
name: v3-sub-M2
description: v3 子流程 M2 大众快消·规模渠道。仅由 master 在 business_model=M2 时调度；草案未安装。
---

# 子流程 M2 · 大众快消·规模渠道

状态：staged draft（t423u）。上游：`master/SKILL.md` S2 调度；下游：统一接口 `schema/plugin_output.v3.schema.json`。本子流程只决定 **FV3 怎么来**，不得改 L1（门槛、B20 公式、收益卖、仓位、置换）。

## 适用名单（master/ROUTING.csv）
| 代码 | 名称 | 评级 | 现行方法 | 方法错配 | 严重度 |
|---|---|---|---|---|---|
| 603195.SH | 公牛集团 | B·暂定 | NI3×退出PE (normalized_midcycle) | 否 | 低 |
| 603605.SH | 珀莱雅 | B-·暂定 | NI3×退出PE (normalized_midcycle) | 是 | 中 |
| 300957.SZ | 贝泰妮 | B-·暂定 | NI3×退出PE (normalized_midcycle) | 是 | 中 |
| 600887.SH | 伊利股份 | B+·暂定 | NI3×退出PE (conservative_flat_main) | 是 | 中 |

## 锚点
- L2 方法锚：A.L2.M2（draft）
- L3 参数锚：
  - `A.L3.M2.raw_material_norm` 原料价正常化 · draft
  - `A.L3.M2.opex_peer_band` 费用率同业锚 · draft
  - `A.L3.M2.new_biz_exclusion` 新业务亏损剔出 · draft
  - `A.L3.M2.brand_gate` 品牌证据门 · draft
  - `A.L3.M2.exit_pe` 退出PE锚 · draft

## 步骤
1. **S1 资料清单**（缺项登记 `data_gap`，不得用估计值硬填）：年报分产品收入/毛利、原奶价格（农业农村部周价）、同业（蒙牛/上美/华熙）费用率
2. **S2 利润基数**：按 master V§2 清洗（核心/扣非、首年 = 9M+上年Q4、所有者盈余、应计/F-score、套保上限），再加本模式剥离项。
3. **S3 驱动表**：填下方模板；top-2 驱动必须标 `is_top2`，每个驱动带一手出处。核心驱动：分品类收入、原料价格（原奶/油脂）、毛利率、销售费用率、份额、价格战
4. **S4 估值方法**：NI3 = Σ品类收入 × 正常化毛利（原料价格取周期中位）− 费用率（同业锚±2pp）；新业务亏损单列不进基准增长
5. **S5 倍数/折现锚**：自身窗口 P50 且 ≤ M1；股息率下限作卖点辅助展示（V§3：`exit_date_convention=FY3_yearend`，`multiple_basis` 同财年；非 PE 锚须声明替代口径）
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
销售费用率连升 2 季 >1pp；份额连续下滑；原料价格 >周期 P80 且无法提价

## 子型/特别说明
—
- L1 适配：L1 买点见 V§5-2：B20=(FV3_base+n×DPS_min3)/(1+h)^n（n=exit_multiple.n_years；禁止写死 ³）；B20 用正常化毛利；品牌证据门（原 L571 brand_vs_awareness_gate）

## L4 个股锚点（只补充/细化本子流程，不得推翻上层；每条须写来源、依据、失效条件）
| 锚点 | 名称 | 状态 | 说明 |
|---|---|---|---|
| `A.L4.yili.raw_milk` | 原奶周期 | gap | 毛利率剔除奶价周期 |
| `A.L4.yili.ausnutria_goodwill` | 澳优商誉 | draft | 商誉减值剥离 |
| `A.L4.yili.mengniu_comp` | 蒙牛竞争 | gap | 份额/价格战 |
| `A.L4.proya.sell_exp_ratio` | 销售费用率/投放效率 | draft | 毛销差 |
| `A.L4.proya.main_brand` | 主品牌/彩棠 | draft | 主品牌收入 |


## 从旧主规则下放到本子流程的条款（RULE_MAPPING.csv v3_sub 列）
- ### 优质挖掘 · 难受才可能优质 / look-through（Marks  第2项 L206-L206：2. **禁止伪优质标签**：市占第一、主题热、专精特新/小巨人认定、工信部质量管理能力高等级（经验级→卓越级）名单、品牌知名度口号 ≠ 自
- ### 三腿凳 · Power 类型 · 质量 edge 处理（Akre Goo 第3项 L530-L530：3. **power_type_tag（Helmer，可选但触卡补）**：`moat_source_tag` 须能落到 7 Powers 之
- ### 特许 vs 中周期再投入 · 品牌≠知名度（Li Lu Columbia 第2项 L571-L571：2. **brand_vs_awareness_gate（触品牌名补）**：`economic_goodwill_tag=franchise


## 输出（统一接口，摘要）
`business_model, plugin_version, as_of, currency, base_year, drivers[], FV3{bear,base,bull}, FV3_build, dps_path, multiple_anchor{method, multiple_basis, exit_date_convention}, fragility, kill_lines[], forecast_ledger_entries[], notes_double_count, data_gaps[]` — 全字段与必填见 schema。
