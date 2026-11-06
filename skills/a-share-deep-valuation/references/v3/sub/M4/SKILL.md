---
name: v3-sub-M4
description: v3 子流程 M4 强周期（正常化）。仅由 master 在 business_model=M4 时调度；草案未安装。
---

# 子流程 M4 · 强周期（正常化）

状态：staged draft（t423u）。上游：`master/SKILL.md` S2 调度；下游：统一接口 `schema/plugin_output.v3.schema.json`。本子流程只决定 **FV3 怎么来**，不得改 L1（门槛、B20 公式、收益卖、仓位、置换）。

## 适用名单（master/ROUTING.csv）
| 代码 | 名称 | 评级 | 现行方法 | 方法错配 | 严重度 |
|---|---|---|---|---|---|
| 300750.SZ | 宁德时代 | B+·暂定 | NI3×退出PE (normalized_midcycle) | 否 | 低 |

## 锚点
- L2 方法锚：A.L2.M4（draft）
- L3 参数锚：
  - `A.L3.M4.cycle_window` 周期窗口长度 · spec_drafted
  - `A.L3.M4.unit_profit_mid` 单位利润中位 · draft
  - `A.L3.M4.path_tag` ni3_path_tag · draft
  - `A.L3.M4.pb_percentile` PB周期分位交叉 · draft
  - `A.L3.M4.strict_lock` strict_cycle_lock / 近峰禁令 · draft

## 步骤
1. **S1 资料清单**（缺项登记 `data_gap`，不得用估计值硬填）：年报产量/单位成本、交易所/上海有色网价格、行业产能数据
2. **S2 利润基数**：按 master V§2 清洗（核心/扣非、首年 = 9M+上年Q4、所有者盈余、应计/F-score、套保上限），再加本模式剥离项。
3. **S3 驱动表**：填下方模板；top-2 驱动必须标 `is_top2`，每个驱动带一手出处。核心驱动：商品价格、产量、单位利润、capex 周期、产能利用率
4. **S4 估值方法**：NI3 = 产量 × (周期中位价 − 单位成本)；至少 3 档价格情景；**禁止**用峰值单位利润
5. **S5 倍数/折现锚**：正常化 NI × 中枢 PE，或 PB 周期分位（P50）交叉取低（V§3：`exit_date_convention=FY3_yearend`，`multiple_basis` 同财年；非 PE 锚须声明替代口径）
   - **双方法（r4 / P3）**：默认方法对 = `midcycle_PE` + `PB_cycle`；独立性 = 中枢 PE vs 周期 PB 分位（不同主驱动）；或 midcycle_PE + reverse_DCF；禁止两个 PE 孪生。plugin `methods[]` ≥2，或 `dual_method_exception` ∈ {V20_pending, data_gap}+reason。
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


- M4：NI 基 = 7–10 年平均净利率×当前收入 与 周期中位 ROE×BVPS 取低（窗口长度开放参数）；ni3_path_tag 必填。


## Kill-lines（可证伪、带阈值、带数据源）
单位利润跌破周期中位 2 季；capex/折旧 >2 且 ROIC<WACC

## 子型/特别说明
—
- L1 适配：L1 买点见 V§5-2：B20=(FV3_base+n×DPS_min3)/(1+h)^n（n=exit_multiple.n_years；禁止写死 ³）；原 L99–107 ni3_path_tag、L197、L200 strict_cycle_lock、L202 近峰禁令归入

## L4 个股锚点（只补充/细化本子流程，不得推翻上层；每条须写来源、依据、失效条件）
| 锚点 | 名称 | 状态 | 说明 |
|---|---|---|---|
| `A.L4.catl.unit_profit` | 单位利润中枢 | draft | 税后核心单位利润中枢 |
| `A.L4.catl.storage_gm` | 储能毛利 | draft | 储能分部毛利 |


## 从旧主规则下放到本子流程的条款（RULE_MAPPING.csv v3_sub 列）
- ### 2.1 quality_grade ∈ {A, B, C} 第2项 L22-L22：2. 老唐② 利润可持续：满足，**或**仅「温和周期/批价波动/净利率中枢缓下移」而特许/品牌/牌照护城河仍在（茅台类）；**不得**因行
- ### 2.1 quality_grade ∈ {A, B, C} 第4项 L24-L24：4. 生意类型：franchise / 平台 / 受监管公用特许等「优质生意」主叙事；**不是**强周期商品、重资本扩产成长、投放驱动尚未证
- ## 3. 买点 L75-L77：## 3. 买点
- ### 退出 PE · 合格窗硬清单（2026-10-26 进化试跑；经验值/待 第3项 L84-L84：3. 拒用合格窗，必须书面给出一手证据之一：利润规模与 PE 中枢同步断裂、亏损/利润塌陷、周期失真（含可核对数字）。禁止以「含高成长溢价」
- ### 周期/商品类 · NI3 路径标签（Damodaran；2026-10-26 经典学习） L99-L108：### 周期/商品类 · NI3 路径标签（Damodaran；2026-10-26 经典学习）
- ### 证伪优先与认知偏差过滤（Munger / Marks；2026-10-2 第3项 L112-L112：3. **周期价格夸大（Marks）**：模块 b 强/中周期票，若外部利用率/价格已回升，压力测试优先假设「价格已部分透支修复」；政策原文
- ### 能力圈声明 · 高于收益卖线侧倾 · 候补禁句（Buffett 1987 第3项 L121-L122：3. **周期位置侧倾（Prepare，不预测拐点）**：模块 b 强/中，且「强需求叙事 + 产能/资本开支仍扩张 + 定价隐含永续高增」
- ### 永久损失风险折价 · ni3_path 触票补标（Marks 2015  第4项 L137-L142：4. **ni3_path_tag 触票补标（不改数）**：模块 b 强/中且字段空时，按已写 cycle_position 映射补标后才可
- ### 买卖点严格锁 · 降价才买（Buffett 2008 / Marks 1 第1项 L200-L200：1. **strict_cycle_lock（周期/窗口票）**：当模块 b 强/中且已用 `normalized_midcycle`（或窗
- ### 买卖点严格锁 · 降价才买（Buffett 2008 / Marks 1 第4项 L202-L203：4. **商品近峰禁令（Conoco 课）**：动力煤/锂盐/设备订单等价格或利用率近阶段高位时，基准 NI3 不得年化峰利；安监/保供/长
- ### 增长必须挣来 · NI3 分解（Damodaran Growth and 第4项 L216-L216：4. **与周期标签衔接**：模块 b 强/中时，分解结果不得推翻 `ni3_path_tag` / `strict_cycle_lock`
- 硬闸§7 L304-L304：7. **strict_cycle_lock**：模块 b 强/中且中枢/守窗路径下，溢价≥100% 或已 return_below_lin
- 硬闸§22 L319-L319：22. **SES 让利致近端 NI 下滑（r14）**：禁止无独立证据改打 `peak_fade`；期权+高价回购净稀释进 account
- ### 特许 vs 中周期再投入 · 品牌≠知名度（Li Lu Columbia 第1项 L570-L570：1. **franchise_vs_midcycle_reinvestment_bar（强制，车道1）**：四优前三全 pass **不足以
- ### 资本配置序列 · 每股价值分母（Gayner Markel 2025 / 第3项 L597-L598：3. **tob_reinvestment_vs_A（加固 franchise_vs_midcycle）**：ToC 现金牛养 ToB 再投
- ### 规模节省回馈 vs 近端 NI 下滑 · 期权回购净稀释（Nick Sl 第3项 L616-L617：3. **invisible_reinvestment_not_peak**：营销/渠道/换电网络/价格给回等「可见费用或不可见让利」压近端
- ### 候补晋升卫生 · 特许现金牛 vs 中周期龙头狩猎（Rochon/Giv 第2项 L623-L623：2. **franchise_cash_cow_vs_midcycle_leader_hunt（加固 Q1/P2b，车道1）**：狩猎正式池
- ### Five Ms 狩猎清单 · 结构支撑长期 · EBIT 默认（Trac 第3项 L650-L650：3. **short_and_long_both_required（加固 capacity_to_suffer，车道1）**：只盯长期战略而
- ### 期望反向读取 · 增长久期高估 · 财会33号交叉（Mauboussin 第2项 L655-L655：2. **growth_duration_overestimation_flag（加固严格周期 / return_below_line，车道


## 输出（统一接口，摘要）
`business_model, plugin_version, as_of, currency, base_year, drivers[], FV3{bear,base,bull}, FV3_build, dps_path, multiple_anchor{method, multiple_basis, exit_date_convention}, fragility, kill_lines[], forecast_ledger_entries[], notes_double_count, data_gaps[]` — 全字段与必填见 schema。
