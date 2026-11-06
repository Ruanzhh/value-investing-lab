---
name: v3-sub-M8
description: v3 子流程 M8 平台·多分部（SOTP）。仅由 master 在 business_model=M8 时调度；草案未安装。
---

# 子流程 M8 · 平台·多分部（SOTP）

状态：staged draft（t423u）。上游：`master/SKILL.md` S2 调度；下游：统一接口 `schema/plugin_output.v3.schema.json`。本子流程只决定 **FV3 怎么来**，不得改 L1（门槛、B20 公式、收益卖、仓位、置换）。

## 适用名单（master/ROUTING.csv）
| 代码 | 名称 | 评级 | 现行方法 | 方法错配 | 严重度 |
|---|---|---|---|---|---|
| 00700.HK | 腾讯控股 | B+·确认 | NI3×退出PE (mid_cycle_reinvestment) | 是 | 高 |

## 锚点
- L2 方法锚：A.L2.M8（draft）
- L3 参数锚：
  - `A.L3.M8.core_pe_basis` 核心PE年份口径 · error
  - `A.L3.M8.core_pe_window` 核心PE样本 · defined r2：≥4 个年末快照 + 修剪检验（V§3-3），熊 = 最低快照
  - `A.L3.M8.portfolio_discount` 组合折价 · draft
  - `A.L3.M8.portfolio_smoothing` 组合腿平滑 · defined r2：上市腿 = min(最新, 最近 4 季均值)；未上市 = 最新账面
  - `A.L3.M8.segment_ni3` 分部 NI3 搭建 · draft
  - `A.L3.M8.sbc` SBC 处理 · draft
  - `A.L3.M8.no_double_count` 总PE×核心NI 双计禁令 · draft

## 步骤
1. **S1 资料清单**（缺项登记 `data_gap`，不得用估计值硬填）：季报/年报 non-IFRS 调节表、投资组合披露、净现金定义
2. **S2 利润基数**：按 master V§2 清洗（核心/扣非、首年 = 9M+上年Q4，Q3 未出用 TTM_4Q、SBC 按 V§2-3 r2（non-IFRS 同口径倍数 → 敏感性）、所有者盈余、应计/F-score、套保上限），再加本模式剥离项。
3. **S3 驱动表**（r2, D13：公司不披露分部经营利润时，「分部 NI3」= 分部收入 × **集团**核心利润率，利润率是集团级驱动，须在驱动表写明 `GROUP-level`；不得编造分部利润率）：填下方模板；top-2 驱动必须标 `is_top2`，每个驱动带一手出处。核心驱动：核心 non-IFRS NI（剔除 non-IFRS 联营/合营份额）、分部收入（VAS/营销/金融科技）、投资组合（上市市值、未上市账面）、净现金、SBC、AI capex
4. **S4 估值方法**：FV3 = 核心 NI3 × 核心 PE + 上市组合×(1−折价) + 未上市账面×(1−折价) + 净现金；核心 PE = 历史(市值−组合折价−净现金)/核心 NI，**不得包含当日价格点**
5. **S5 倍数/折现锚**（r2：与 V§3-3 一致，≥4 个年末快照，输入卫生按 V§3-2；快照表写入 `multiple_anchor.snapshots`，并填 `total_mcap_pe_used=false`、`bear_rule=min_snapshot`；公司行动：FY2022 年末价含美团实物分派权（登记日 2023-01-10）→ 待分派资产 147,965m 按 0% 折价扣除；京东实物分派除权 2022-01-20 在 YE2021 之后、YE2022 之前，YE2022 不调整）：核心 PE：历史年末快照中位（熊=最低、牛=min(最高,30)）；组合折价 基 30%/50%、熊 50%/70%、牛 20%/30%（V§3：`exit_date_convention=FY3_yearend`，`multiple_basis` 同财年；非 PE 锚须声明替代口径）
   - **双方法（r4 / P3）**：默认方法对 = `SOTP` + `reverse_DCF`；独立性 = 分部 SOTP vs 反推 DCF（DISPLAY 反推可作第二方法槽）；禁止两个 PE 孪生。plugin `methods[]` ≥2，或 `dual_method_exception` ∈ {V20_pending, data_gap}+reason。
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

- M8（r2 已实现于 validate_anchors.py `r_snap`/`r_m8`）：快照表每行 profit_fy=fy、价格日在 FY 年末 ±10 天、未复权价、年末已发行股、FX 日=价格日；市值与核心 PE 复算 ±1%；≥4 快照 + 修剪检验；熊核心 PE ≤ 最低快照；`total_mcap_pe_used=false`；FV3 三档由 `FV3_components` 复算 ±0.5%；组合平滑 = min(最新, 4Q 均值)；组合/净现金 FY3 保持不变；恰好 2 个 top-2 驱动；熊利润率地板（V§1-4 r2）；R6 反推扣组合与净现金（DISPLAY，单位错误 FAIL）。
- 变异测试：`validate_anchors.py --mutation-tests plugin_output.json decision_card.json`（错年 PE、无快照表、复权价、3 快照、双计、熊PE高于最低、top-2 缺/多、n=3.0、反推单位错、熊利润率越界、非独立复核、复核 FAIL、脆弱标志错、B20 不可复算）全部必须 FAIL。



## FY3 资产负债腿（r2, D15）
净现金、投资组合取最近报告日并保持不变到 FY3；FCF 累积与回购/分红均不计入（保守，且避免与 n×DPS 双计）。FX = 估值日参考汇率（D14）。

## Kill-lines（可证伪、带阈值、带数据源）
核心 non-IFRS 经营利润同比 ≤0 两季；连续 3 季 FCF≤0 且上调 capex 指引；回购同比降且 capex 升两季

## 子型/特别说明
—
- L1 适配：L1 买点见 V§5-2：B20=(FV3_base+n×DPS_min3)/(1+h)^n（n=exit_multiple.n_years；禁止写死 ³）；窗口总 PE 已隐含组合 → **禁止**总 PE × 核心 NI 再加组合（双计）；SBC 扣除作敏感性

## L4 个股锚点（只补充/细化本子流程，不得推翻上层；每条须写来源、依据、失效条件）
| 锚点 | 名称 | 状态 | 说明 |
|---|---|---|---|
| `A.L4.tencent.named_portfolio` | 具名投资组合 | gap | 上市/未上市持仓逐项市值×折价 |
| `A.L4.tencent.video_account` | 视频号/营销变现节奏 | draft | 营销服务增速与视频号时长 |
| `A.L4.tencent.game_license` | 游戏版号/长青游戏 | draft | 国内游戏收入、长青游戏数、版号 |
| `A.L4.tencent.buyback_vs_capex` | 回购 vs AI capex | draft | SBC 由回购对冲；FCF conv=0.7 |


## 从旧主规则下放到本子流程的条款（RULE_MAPPING.csv v3_sub 列）
- 无


## 输出（统一接口，摘要）
`business_model, plugin_version, as_of, currency, base_year, drivers[], FV3{bear,base,bull}, FV3_build, dps_path, multiple_anchor{method, multiple_basis, exit_date_convention}, fragility, kill_lines[], forecast_ledger_entries[], notes_double_count, data_gaps[]` — 全字段与必填见 schema。
