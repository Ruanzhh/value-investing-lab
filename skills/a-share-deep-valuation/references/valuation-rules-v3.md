# 主规则 v3（已安装 · 2026-10-31 Asia/Shanghai cutover t435u）

**状态：LIVE**（用户 t435u / widget t435s2100：装流程并且马上批量重算所有买点）。
**前置备份：** `a-share-deep-valuation.bak-v25-20261031`；安装前 rules md5 `0486682f73048deb5ecda336936190c8`（valuation-rules-v25.md 仍保留为 legacy 附录，不再作为主路径）。
**映射冻结源：** `references/v3/legacy/valuation-rules-v25.frozen.md`（md5 5d691d8b…）。

## V§20_LIVE_INHERIT（用户未新拍板；本轮继承 live 字面，不发明）
| 项 | 继承自 live | 执行口径 |
|---|---|---|
| M5 三年 20% 门槛 | valuation-rules-v25 公用 hurdle/字面 | 保持 live 写法；不改数值 |
| M5/M7 叠息 | §71 / t396u：银行/保险/公用**不叠加**；其余叠 3×DPS_min3 | 保持 live stacking |
| M5 ERP 分档 / M5d 电信 ERP | live 若已写则照旧；未定义则 `erp_undefined` + gap | 不发明分档 |
| R4–R6 | live 为展示 | **DISPLAY not GATE** 直至用户覆盖 |
| M7b NBV 倍数 | live 空 | `nbv_mult_missing`；不发明 |

标签：所有相关卡/重算记录写 `V20_LIVE_INHERIT=true`。

## Round-1 倍数口径（t420u 方案 A · 本轮 cutover 授权批量）
- `exit_date_convention=FY3_yearend`；`multiple_basis=same_FY`
- n = 估值日 → FY3 年末实际年数（天/365.25）
- 材料不足不得发明 NI3/PE；`B20_issued=false` + `gate_block_reason`

## 文件布局
- 本文件 = 安装入口（下接 master 全文）
- 详细 L1：见下方嵌入的 `rules-master-v3` 正文（与 `references/v3/rules-master-v3.md` 同步）
- 子流程：`references/v3/sub/<模式>/SKILL.md`
- Schema / 校验：`references/v3/schema/*` · `scripts/validate_anchors_v3.py`
- 路由：`references/v3/ROUTING.csv`
- 旧全文：`references/valuation-rules-v25.md`（legacy 附录）+ frozen 副本

---

# 主规则 v3（L1 共用层）· LIVE cutover 2026-10-31
状态：LIVE (installed)（t423u；r2=t425u；r3=t428u；**r4=t430u**：S4c 闭环重排、条件 B20、双方法进子流程、M5d/M7 去污、校验器补全）。legacy 规则 `references/valuation-rules-v25.md` 现 md5 **`0486682f…`**（a-4 卫生后；v3 映射冻结源仍为 legacy `5d691d8b…`）**已被本文件接替为 LIVE；v25 降为 legacy 附录**。框架轮次只改结构/关卡/治理，**不调任何锚点参数数值**（见 `../FRAMEWORK_OPT.md` r5）。
本文件只保留：所有生意模式共用的流程纪律与 L1 锚点。生意模式方法 → `sub/<模式>/SKILL.md`（L2/L3 锚点）；单票补丁 → L4 个股锚点（`sub/<模式>/SKILL.md` §L4 表 + `（内部文稿未发布）`）。
旧条款 → 新位置 全表：`master/RULE_MAPPING.md`（逐段覆盖旧文件 768 行，0 条未映射）。旧全文冻结副本：`legacy/valuation-rules-v25.frozen.md`（出处、学习来源、标签长定义仍以该副本为参考文本）。
每条格式：`V§n 标题 [锚点 id] ← 旧来源`。数值未标来源者为经验值/待回测。

## V§0 读法与优先级 [A.L0.root] ← 旧 L1–2 读法、硬闸导言 L296
1. 冲突优先级：用户明示决定 > 本文件 V§ > 子流程 SKILL > L4 个股锚点 > legacy 学习节。
2. 子流程与 L4 只能**补充或细化**上层，不得推翻 L1（不得为单票改门槛、改公式、改仓位上限）。
3. 每张卡的每个数字必须可追溯到唯一叶子锚点 id；追不到 → `anchor_untraceable`，校验 FAIL。
4. 「经验值/待回测」参数不得在无回测时升格为硬门控，除非用户明示。

## V§1 情景与基准中性 [A.L1.scenario, A.L1.bear_stress] ← 旧 §1 L4–9、§3 熊/基/牛、硬闸 39/1b
1. 熊/基/牛均由经营驱动构建，具体驱动由子流程的驱动表定义；三档须满足 熊 ≤ 基 ≤ 牛（FV3 与 NI3）。
2. 基准 = 中性最可能路径；平台期/零增长属熊，除非 `base_neutrality_note` 给一手证据。
3. 熊 NI3 ≤ 基率中位路径（旧 r19 P-X4 `bear_ni3_le_base_rate_median`，硬闸）。
4. 熊景压力不得比历史最差年份更乐观（R2，A.L3.*.bear_* 由子流程具体化）。**r2 具体化（Tencent pre-mortem）**：熊倍数 = 合格快照最低值（`bear_rule=min_snapshot`，M8 强制，其余模式取 min(P20,基) 与最低快照中更低者为推荐）；熊利润率 ≤ 窗口内最差年 `worst_in_window`；若最差年有一手证据证明为一次性（须写 `exemption_reason`），熊利润率仍 ≤ 近 3 个完整财年最差 `worst_last3`。[A.L1.bear_stress.multiple / .margin]
   **r3 / RC2 低谷年地板 [A.L1.bear_stress.trough_floor]**：凡因 RC1 从基/牛窗口剔除的低谷年，**不得**再被 `exemption_reason` 豁免出熊景地板。熊利润率 ≤ 该低谷年利润率；熊倍数 ≤ 该低谷年倍数（与 min_snapshot 取更严）。卡上必须并列「含低谷地板」的熊 FV3 / r_bear / 仓位档。
5. 概率只作展示（V§14），永不触发。

## V§2 利润基数清洗 [A.L1.profit_base, A.L1.base_year] ← 旧 §5⑧ r49-P1/r51-C1、硬闸 39/50/55/112、r12/r13/r19 会计节；R3
1. 利润基数 = 核心/扣非口径，剔一次性；子流程声明额外剥离项（如 M3 套保/汇兑、M8 联营与投资收益）。
2. 首年(FY)基准 `base_year.method`：Q3 已披露 → `9M+priorQ4`（9M 实际 + 上年 Q4，核心口径；上年 Q4 异常须注明并给敏感性；收入同法，旧 §5⑧）；Q3 未出或港股季报名 → `TTM_4Q`（最近四个已披露季度，= 上年全年 + 本年已披露期 − 上年同期）；`FY_actual` 仅在两者不可得时，须写 `fy_actual_reason`。[r2, D9]
3. 所有者盈余 owner_earnings = 核心 NI − SBC(若核心口径已加回) − 维持性 capex + D&A（R3，草案 r2）。
   - 维持性 capex 未披露 → `maint_capex_basis=DA_proxy`（维持性 capex = D&A，等价于 OE = 核心 NI − SBC）；若当期 capex < D&A 用 `DA_proxy_capped_capex`（取 capex）。式子只在 capex 指维持性时成立，增长性 capex 不扣（进入 R5 再投入）。
   - SBC：核心口径加回 SBC 时必须填 `sbc` 与 `sbc_treatment`：若退出倍数快照是**同一加回口径**（如 M8 non-IFRS）→ `sensitivity_same_basis_multiple`，NI3 不扣、卡上并列「NI3×(1−SBC/核心NI)」的 B20；倍数为 IFRS 口径 → 必须 `deducted_in_NI3`。OE 一律扣 SBC。[A.L1.profit_base.sbc, D8]
   - **r3 / RC5 禁止单边扣 SBC [A.L1.profit_base.sbc_both_sides]**：禁止把「只从 NI3 扣 SBC、倍数仍用加回口径」的 B20 当作标题数或到价依据（口径错配）。若做扣 SBC 敏感性，必须**两边同口径**（NI3 与倍数均扣 / 均不加回），结果只进 `sbc_sensitivity_both_sides`，不得替代 headline B20。
4. 质量门槛（R3，阈值待回测）：应计比率 (NI−CFO)/平均总资产 >0.05 观察、>0.10 须 NI3 打折；Piotroski F ≤3 须打折；打折幅度 = 开放参数。
5. 套保/汇兑加回：只认利润表已实现部分，须有上限 `hedge_fx_cap`；资产负债表 OCI 项不得加回（美的重复计算教训）。
6. 执行距离只认 NI 轨；FCF 轨为并行观察（旧 P3 L583–592，§111/§112 互斥）。
7. 非经常性重分类（证监会〔2023〕65号）、无形投入资本化交叉（§55–§57）、研发削减警示（§60）均为展示/注记，不改数。

## V§3 退出倍数通用纪律 [A.L1.exit_multiple, A.L1.exit_date_convention, A.L1.exit_multiple.basis] ← 旧 §3 L75–91、硬闸 10/38；R1
1. **退出日期 = 第三个完整财年年末**（`exit_date_convention=FY3_yearend`），用户 t420u 授权执行器定为方案 A。
   **r2 精确定义（D5，执行器按 t420u「你定吧」授权取定，可由用户推翻）**：FY3 = 年末日期最接近「估值日 + 3 年」的财年（等距取较晚者）；折现指数 n = 估值日到 FY3 年末的实际年数（天数/365.25，必落在 [2.5, 3.5]）。B20_TR = (FV3_base + n×DPS_min3)/(1+h)^n。卡上必须写 `fy3` 与 `n_years`，validator 复算。
   理由：① 门槛的本意是「约三年、每年 20%」，n 用实际时间，不白送也不白扣增长年；② 「FY2028+n=3.0」在 10 月估值时多折 0.83 年却少算 0.83 年增长，是错配；③ 「FY2028+n=2.17」会把 2.17 年的价值按 3 年门槛的买点给出，抬高买点；④ 字面「第三个完整财年」在年初时 n≈4，过严。腾讯 2026-10-30：FY2029/n=3.17 → B20 421.41；FY2028/n=3.0 → 408.70；FY2028/n=2.17 → 473.57。
2. **倍数与利润同一财年**（`multiple_basis=same_FY`）：历史窗口 PE = 年末市值 / 同财年核心 NI；TTM 或错年口径 → FAIL。
   **快照表强制（r2, D1）**：任何历史窗口倍数（PE / SOTP 核心 PE / EV 系 / PS）必须附 `multiple_anchor.snapshots[]`，每行 `fy, price_date, profit_fy, price, price_basis, shares_mn, shares_basis, fx, fx_date, value, source`；validator 断言 profit_fy = fy 且 price_date 在 FY 年末 ±10 天。
   **输入卫生（r2, D4）[A.L1.exit_multiple.input_hygiene]**：价格 = 年末**未复权**收盘（`price_basis=unadjusted`，禁用前/后复权；源须可复核，如 gtimg kline 不复权）；股本 = 该年末**已发行股数**（年报「total number of issued Shares」；`shares_basis=YE_issued`；无年末数时 `period_weighted_YE` 须注明），禁用 WABS/当前股本代替；FX = 年末参考汇率（ECB/Frankfurter 或人行中间价，写明来源），`fx_date` = `price_date`；市值统一换算到报表币种（十亿），股数单位百万。
   **公司行动**：年末价格若为含权价（如实物分派登记日在年末之后），被分派资产按 0% 折价从市值中扣除；登记日在年末之前的分派不调整。
3. 窗口：结构可比窗 ≥4 年（年末快照 ≥4 个）；修剪检验：去掉最早一年、去掉最近一年的中位数各与全窗中位数相差 ≤10%（年度快照版的「两端各缩 0.5 年」），否则写 `trim_fail_reason` 并交复核；基 = 中位数；熊=min(P20, 基, 最低快照*)，牛=min(P80, 30)（旧 L80–86；*M8 强制最低快照）。拒用合格窗须一手证据；卡须标路径标签（窗口/中点/回退）。子流程不得用少于 4 个快照，除非写 `window_exception_reason`（上市不足 4 年等）并交复核。[D6]
   **r3 / RC1 利润低谷年剔除结构 [A.L1.exit_multiple.trough_exclusion]**：基/牛窗口**不得**纳入「利润低谷」快照。判定（结构规则；阈值 **PROVISIONAL_UNBACKTESTED**）：快照 `core_margin`（或同口径利润率）低于窗口内其余年最低值超过 `trough_margin_gap_pp`（暂定 3pp），或作者显式标 `exclude_from_base_bull=true` + `exclude_reason` 含 trough/depressed。被剔除快照必须仍留在 `snapshots[]`（供熊景与敏感性），并写入 `excluded_from_base_bull[]`。基倍数 = **未剔除**快照的中位数；修剪检验也只在未剔除集合上跑。低谷年只作敏感性展示，不得抬升基/牛。
4. 同业 PE、卖方目标 PE、板块 PE 只作上限，不作抬升（旧 J1/absolute_mos）。
5. 不以 PE 为价值锚的模式（M5/M7/M8 部分）由子流程声明 `multiple_basis` 的替代口径（如 `PB_same_date`）。
6. 溢价字段唯一口径 `premium_vs_B20_pct`（硬闸 10）。

## V§4 评级与确信 [A.L1.grade] ← 旧 §2–§2.2 L11–55、§59 A7、硬闸 16/17、P1 升档 L544–556
1. quality_grade∈{A,B,C}；B 名须有 b_tier∈{B+,B,B-}；confidence∈{确认,暂定}；展示串 `{b_tier|quality}·{confidence}`。
2. A 升档硬标准 A1–A7（OCF/NI、ROE/ROIC 持久、轻再投入、资产负债表、管理层、生意类型、10 年 8 年 ROE>12%；§59 双口径）——原文保留于 legacy L26–40 与 §59，迁入 `master/grade-A1-A7.md` 前以 legacy 为准。
3. 升档只经独立复核；永不因价格、TA、看板重点升 A；改档当轮不改数，设 `hurdle_reval_pending`。
4. 升档触发 `upgrade_triggers`（P1）2–4 条可证伪领先指标；独立复核双向。


## V§4c 外部交叉校验 S4c [A.L1.EXT] ← 新增 r3（t428u；提案 `external-crosscheck/PROPOSAL.md`）
位于**内部 B20 算出之后、签发/到价判定之前**（阶段序：S5a → S4c → S5b；不得在尚无 B20_internal 时跑 S4c）。外部数据是交叉验证，**不是**抬高买点的借口。
1. **EXT.1 一致预期对照 [A.L1.EXT.consensus]**：NI3_base vs 同口径一致预期（FY3 缺失时按 FY+2 与一致预期增速外推，必须标 `extrapolated=true`）。偏离绝对值超过 `consensus_tol_pct`（**暂定 15%，PROVISIONAL_UNBACKTESTED**）必须写 `deviation_reason`，否则 FAIL。口径字段 `basis` ∈ {non-IFRS, IFRS, 扣非} 两侧必须一致。
2. **EXT.2 乐观偏差折扣 [A.L1.EXT.optimism_haircut]**：一致预期按 3 年期先打 `optimism_haircut_pct`（**暂定 10%，PROVISIONAL_UNBACKTESTED**）折扣再比较。文献依据：卖方长期 EPS 系统性偏乐观；具体折扣待回测，升门控前不得当硬阈值用到「必须打折后才算」以外的别处。
3. **EXT.3 外部公允价值对照 [A.L1.EXT.external_fv] · DISPLAY**：FV3 vs {卖方 12 个月目标价中位推到 FY3、Morningstar FV、Damodaran 行业倍数×NI3}。**只展示、记录方向**，永不单独触发买卖。
4. **EXT.4 多方法三角 [A.L1.EXT.triangulation] · GATE**：至少 2 种独立方法（如 同年口径 PE、反向 DCF、DDM/PB-ROE、SOTP）。任两者 FV3 之比 max/min 超过 `method_spread_max`（**暂定 1.25 i.e. 差>25%，PROVISIONAL_UNBACKTESTED**）→ 不出买点（B20 字段置空或 `B20_issued=false`）。
5. **EXT.5 区间买入 [A.L1.EXT.range_buy] · GATE**：B20_final = min(脆弱性网格 ∪ 方法间 FV3 推得的 B20 区间)；只要区间内任一取值使「现价≤B20」不成立 → 一律判「未到价」。禁止用点估计到价覆盖区间分歧。
6. **EXT.6 护栏 [A.L1.EXT.guardrail] · GATE**：
   - 外部数据**只能下调或拦截，不能单独上调 B20**：断言 `B20_final ≤ B20_internal`（S5a 内部值，未接外部前）。
   - 每条 `ext_sources[]`：`url` 非空、`fetched_at` 距 `as_of` ≤ `ext_max_age_days`（**暂定 30 天，PROVISIONAL_UNBACKTESTED**）。
   - 单篇研报不算一致预期（`n_analysts≥5`，暂定）；修正趋势 90 天下修 >`revision_down_pct`（**暂定 5%，PROVISIONAL_UNBACKTESTED**）时熊情景须再压一档或写书面理由。
7. **DISPLAY vs GATE 分栏**：EXT.3 与 R4–R6 为 DISPLAY；EXT.1 理由门、EXT.4/5/6 与 S4 硬校验为 GATE。卡上不得把 DISPLAY 项写成买入依据。

## V§5 门槛与买点 [A.L1.hurdle, A.L1.dividend_tr] ← 旧 §2.3 L56–74、t339u、t396u、§3 L77、§7
1. hurdle：A 档 18%/20%（A18/A20），B 档 20%/22%（B20/B22），C 25% 或只观察。
2. **B20_TR = (基准 FV3 + n×DPS_min3)/(1+h)^n**（n 见 V§3-1 r2；旧式 n=3）；DPS_min3 = FY23–25 每股分红最小值（t396u）。B22 同式用次档 h。
   币种（r2, D14）：FV3 由报表币种换成价格币种时用**估值日（price_date）当日或之前最近的参考汇率**；DPS_min3 用价格币种的宣派金额；市值/组合/净现金单位十亿、股数百万。
   FY3 资产负债项（r2, D15）：净现金、投资组合按最近报告日数值**保持不变**到 FY3（不累加 FCF、不扣回购/分红），保守且避免与 n×DPS 双计；卡上写明。
3. 现行适用域：非银/保险/公用名叠息；银行/保险/公用按 legacy 字面不叠（§71 行）。**v3 草案统一接口输出除息 FV3，是否全部叠息 = 用户待定（V§20-2）**；未决前 M5/M7 子流程两种都算、卡上并列，执行按 live 规则。
4. FV3 由子流程唯一给出（统一接口 `FV3.{bear,base,bull}`）；L1 统一计算 B20/B22、打平价、仓位档。
5. 不做 Ke 折现后再叠 hurdle；每个风险只在 risk_register 指定一处扣减（旧 §7）。
6. 降价才买：重估改 B20 只许下调或持平；上调须正式深研 + 独立复核（旧 §5⑦、r5 严格锁）。
7. TA 永不抬 B20/B22/收益卖线（硬闸 1）。
8. **双方法前置（r3）[A.L1.stability.dual_method]**：`methods[]` 未满 2 个独立方法 → **禁止签发 B20**（`B20_issued=false`）；与 EXT.4 同一关卡。

## V§5b 框架稳定性：区间买入与多方法 [A.L1.stability] ← 新增 r3（t426u/t428u）
1. **多方法三角**：见 V§4c-4；方法定义在子流程，L1 只检查数量与离散度。
2. **区间买入**：见 V§4c-5；到价判定用「整个合理区间都到价」，不是点估计。
3. **点估计只作展示**：headline B20 必须等于区间最小值；卡上可并列中位/最大作 DISPLAY。
4. **状态翻转披露（RC3）[A.L1.review.gaming]**：相对上一版正式/测试卡，若 B20 上调超过 `b20_up_disclose_pct`（**暂定 5%，PROVISIONAL_UNBACKTESTED**），或「到价」状态翻转，必须在 `round_delta.listed_changes[]` 逐条列出改动、方向、对 B20 的贡献、作者理由；缺省 → FAIL。复核模板 A3 自动对照。

## V§6 脆弱性与仓位档 [A.L1.fragility, A.L1.sizing] ← 旧 §4 L143–162、硬闸 13、r18 sizing_discipline、老唐 10% 规则；**r3/RC4：公式一律用 n，禁止写死 3**
1. 熊市回报 r_bear = ((熊FV3 + **n**×DPS_min3)/现价)^(**1/n**)−1：≥0% 首批满额；[−15%,0) 半首批；<−15% 只试仓。n = `exit_multiple.n_years`（V§3-1），不得写死 3。
2. 脆弱比_TR = (熊FV3 + **n**×DPS_min3)/(基FV3 + **n**×DPS_min3) <0.5 → 最多试仓。取更严者；暂定 → 试仓封顶。
3. 确认后阶梯：B·确认 50%(F1–F3)；B 超半 75%(F4: 脆弱比≥0.70 ∧ r_bear_exec≥+10% ∧ 无 edge/事件闸)；A·确认 75%；A 满仓 100%(F5: ≥0.60 ∧ ≥+5%)。F4/F5 触发价非新买点。
4. 驱动敏感性：子流程 top-2 驱动各 ±10% 及同时，任一使「现价≤B20」翻转 → `fragile=true`，到价也只按半首批/试仓，不得称「明显便宜」。
5. 收益卖读数 `base_revert_ann_pct` 的折现年数同样用 n（V§7），与 B20 一致。

## V§7 收益卖与击穿码 [A.L1.return_sell, A.L1.kill_code] ← 旧 §5 L163–183（t388u、r47-D1 ①–⑧）、硬闸 5/6/40/41
1. 读数 `base_revert_ann_pct` = (基FV3/现价)^(**1/n**)−1 + TTM 股息率（n = exit_multiple.n_years；r3/RC4）；「估值不修复」腿只作研究旗。
2. 线 = max(511990 实际收益, §46 最佳真实去处年化) + 2pp；打平价求根时股息率随价反比缩放。
3. 低于线 → 一次重估（≤10 交易日，独立复核+反方）；仍低 → 分批置换出，每步 ≤半，6 个月 ≤两步。
4. 击穿码 ①–⑦ 照旧：停新买 → 硬否决直通 → 一次性保守重估（基准 NI3 不得高于触发前卡值）→ 比真实去处 → 裁决 → 不二次重估。
5. 适用域：M5/M7 PB-ROE 版未装前不触发（看板「PB-ROE 待装」）；代理 FV3 名不触发。v3 子流程 M5/M7a/M7b 给出 PB-ROE 读数后，安装仍需独立复核 + 用户批准。
6. 旧价格卖点退役 `sell_archived_t388u`。回测不显示收益卖更赚；FY2026 年报后复测（≤2027-05-05）。

## V§8 置换总纲 [A.L1.swap] ← 旧硬闸 40/42/43/44/46/54/67/70/71、§5 观念 t320u、组合置换动作带 L700–711
1. 组合 = 单一可互换池；只说 `置换：A→B`；无独立买/卖。
2. 换出触发：收益卖线 / 击穿码 / 质量硬否决 / 超限 / 为更优出资；涨停、PE 高、大盘、宏观、成本浮盈**不是**理由。
3. 去处：511990 兜底；股票去处须 正式池 ∧ ≤自身适用 B20 ∧ 事件闸清无 edge 无击穿码 ∧ 通道可执行 ∧ 至少 1 手。种子/候补/贴近带/正式观察不得作去处。
4. 股换股免见底；现金→新名保留见底闸。暂定去处上限 = trial_cap 5%。
5. 去处须保守路径 ≥5pp 优于持有袖（§46④）；全文仍以 `（内部文稿未发布）` 为准。
6. 证据纪律（t373u）：每笔置换须证据充分并在保守路径上证明收益。

## V§9 仓位上限与簇上限 [A.L1.caps, A.L1.cluster_caps] ← 旧 §47（t396u/t400u）、§53、§58、§90–§98、§123、§140–§142
1. 单名（组合%）：极优质 30%/硬顶 30%；确认 20%/硬顶 20%；暂定 15%/硬顶 25%；新开暂定首笔 5%。
2. 极优质 = A·确认 ∧ 正式卡 ∧ 无 edge/击穿码 ∧ 脆弱比_TR≥0.60 ∧ r_bear_exec≥+5%；失效当日回落、只减不加。
3. 超限部分 = 资金袖，不强卖；硬顶越线 ≥1 手交用户裁决。
4. 簇：quality_consumer 单风格 ≥30% 标集中（§97/§123）；quality_consumer+healthcare_quality ≥40% 标集中；只作诚实尺，不自动下单。
5. ¼ Kelly 理想权重只作研究参照（§92③/§95/§123），永不作可执行仓位公式。
6. 交易后簇越线须预演（§142）。

## V§10 执行硬闸 [A.L1.execution] ← 旧硬闸 1–4、7–9、13、15、19、24、33、35、36；t304u L503–517；重点门控 L560–568
1. 正式池收盘≤B20 → 按分批执行（置换语言）；候补/非正式到价 → 字面 `到价·候补不执行`。
2. 贴近带 (0%,5%]：正式可执行路径开放时整笔试仓，需技术见底（仅现金→新名）。
3. 到价/贴近带必须写分批计划 + 正式仓升级计划（t304u/t306u–t308u）。
4. 事件闸未清 → `到价·正式·事件闸不试仓`；质量 edge → 到价亦受限。
5. 重点 = (A/B+ ∧ 溢价≤20%) ∪ (B/B- ∧ ≤B20)；重点≠试仓。
6. 卖前先写退出线；下行先于上行定宽；不理解不做。
7. 就地修卡：缺标签或文案冲突就地补，不改数。

## V§11 质量闸（共用）[A.L1.quality_gates] ← 旧 L109–142、L204–294、L527–531、L569–574、L594–598、L613–651、L659–681
1. 四优门 four_quality_gate（企业/生意/管理层/价格）为统摄；competence_tag、economic_goodwill_tag、moat_source_tag、fisher_quality_gate、power_type_tag 等标签定义保留于 legacy，v3 卡字段名不变。
2. 禁伪证据：知名度、市占第一、主题热、好产品 ≠ 护城河。
3. 增长必须挣来：`growth_decomposition` 强制；高再投入低增量 ROIC → 价值毁灭检查。
4. Disconfirming line、Lollapalooza 怀疑、激励偏差、社会认同禁令：复核模板逐项（review-template）。
5. 生意模式专属的质量钉（品牌≠知名度→M2；平台单店经济→M2b；ToB 再投入→M3；半导体双标→M9）已下放到子流程。

## V§12 相对估值与套利禁令 [A.L1.relative] ← 旧 L193–198、L219–224、L241–246、L518–537、L575–577、L608–612、L626–628、L637–641、L663–666、L682–686；硬闸 8/15/38/57/65/73/75/79/84/136
1. 相对便宜（同行/链内/屏选/A-H 价差）永不单独打开执行、永不抬 B20/Exit PE；须盖 `relative_exec_void` 戳。
2. 绝对 MOS 优先（absolute_mos_gate，§93）；最不贵陷阱、cheap_for_a_reason 检查。
3. A/H 价差 = 折现率差，非收敛套利（ah_canon）；套利须有终点与对冲腿。

## V§13 组合层账本 [A.L1.portfolio_ledger] ← 旧硬闸 45、47–49、51、58、62–66、68–69、72、74、76–78、80–83、85–92、94–107、109–110、113–122、124–127、130–135、137–141
1. 账本字段与卫生闸（组合期望读数、相关袖、风险贡献启发式、现金期权、因子暴露、种子管道、FV3 重跑队列、时间止损、缺口诚实等）**全部原样沿用**，定义见 legacy 硬闸对应编号；v3 不改其语义。
2. 共同约束：只作读数/卫生，不改 B20/收益卖线/股数；禁止用组合叙事绕过单票绝对 MOS（§93）。
3. 精简计划（不在本次）：按 RULE_MAPPING 的分组合并为 ≤12 条账本字段规范，须单独复核。

## V§14 展示项（永不触发）[A.L1.display, A.L1.base_rate_prior, A.L1.consistency.roic_g, A.L1.reverse_dcf] ← 旧 §6、L247–253、L599–604、L653–658、L687–699；R4–R6
1. 三情景概率加权三年年化。
2. R4 基础比率：NI3 隐含 CAGR 对照 Base Rate Book（注意该表为销售增速）；>前 25% 写依据。
3. R5 g/RONIC 一致性与价值驱动隐含 PE；R6 反向 DCF（现价隐含 NI3 增速）。r2（D2/D10）：输入一律放在 `display_checks`（price, price_ccy, shares_mn, fx_price_ccy_per_report, hurdle_pct, n_years, dps_min3, multiple_base, ni0, 以及 M8 的 portfolio_after_disc、net_cash）；按模式反推：PE/EV 类 = 股权价值/倍数；M8 先扣折后组合与净现金再除核心 PE；M5/M7 反推 ROE。反推增速落在 (−30%, 60%) 以外或 ≤0 → FAIL（单位/币种错误），可用 `reverse_dcf_sanity_override` 写明理由。
4. R4–R6 是否升为门控 = 用户待定（V§20-4）；两周展示期内只 DISPLAY。
5. **DISPLAY ≠ GATE（r3）**：DISPLAY 项（R4–R6、EXT.3 外部 FV 对照、点估计中位/最大）不得写入执行理由或「到价」判定句；GATE 项（S4 硬校验、EXT.1 理由门、EXT.4/5/6、双方法、区间买入、RC1–RC5 结构断言）失败则不出卡/不出 B20。

## V§15 现金门槛与停泊 [A.L1.cash_hurdle] ← 旧 §52、§61、§43、§66、§68、§77、§83、§86、§88
1. 现金门槛 = 默认停泊工具 511990 的 7 日年化（§61 唯一口径）；活期 0.05% 仅并列展示。
2. 闲置现金 >10% 须写停泊计划句；资金袖闲置与现金停泊对等合法。

## V§16 生意模式路由治理 [A.L1.routing] ← 新增（ARCHITECTURE §3）；旧 SKILL industry_branch=bank
1. intake 第一步定 `business_model`（主模式 1 个，副模式 ≤1 只用于交叉），按「利润由什么驱动」而非行业名。
2. 路由表：`master/ROUTING.csv`（43 名初始映射）。模式码：M1, M2, M2b, M3, M4, M5a, M5b, M5c, M5d, M6, M6b, M7a, M7b, M8, M9。
3. 改模式须 `model_change_reason`（收入/利润结构变化 ≥2 年一手证据）+ 独立复核；新旧模式 B20 差 >15% 时复核员必须单列「是否为了让买点变近而改模式」。
4. 卡上实际方法与 `method_by_model` 不一致 → `method_mismatch=true`，不得出正式卡。

## V§17 单锚点进化治理 [A.L1.evolution] ← 新增（anchor-tree t415u 治理）；替代旧 a-3 自由增条做法
1. a-3 每轮只改 **一个**叶子锚点；动到第二个节点 → 本轮作废。
2. 每次改动附：改前/改后值、受影响票与 B20 变化、回测、独立复核结论、版本号；可单独回退。
3. 新增规则只能挂到锚点（L1/L2/L3/L4），禁止再往主规则追加单票补丁；同类 L4 锚点 ≥3 票出现 → 提议升级为 L2/L3。
4. 用户保留项（V§20）进化不得触碰。
5. 出卡前全量跑 `scripts/validate_anchors.py`；FAIL → 不出卡。

## V§18 预测对账 [A.L1.reconcile, A.L1.forecast_ledger.calibration] ← 新增 R8；ARCHITECTURE L4 层
1. 每卡登记 FY+1 核心 NI 与 top-2 驱动、NI3 的 P10/P50/P90，并标归因锚点 id。
2. 财报后写 actual；偏差 >15% 须解释并归因到锚点；同锚点 ≥3 票或连续 2 期同向偏 → 自动排入 a-3 队列。
3. 年度统计 P10–P90 覆盖率（目标 ≈80%，开放参数）。

## V§18b 状态机与沙盒 [A.L1.workflow_state] ← r2 D11
1. v3 状态 S0–S9 由 `scripts/workflow_state_v3.py open/commit/status` 维护（`runs/<run>/v3_state.json`）；`--test-run` 标记的运行写在 `test-runs/`，永不写 live 卡/看板/watchlist。
2. S9 偏差入队写 `anchor_queue.json`（schema 见文件头），a-3 每轮只取一条。

## V§19 自检 self_check [A.L1.self_check] ← 旧 §7；r3 增补
1. 无 Ke-then-hurdle；2. 风险只扣一次；3. 基准 FV3 按 hurdle 折现 ≈ 市价 ±15% 时写明为何与市场一致；4. 参数标来源或经验值；5. validate_anchors 无 FAIL。
6. S4c 已跑：`external_crosscheck` 有 URL/日期/同口径；B20_final ≤ B20_internal；B20_final == min(range)。
7. `methods[]` ≥2 且离散度未超限；`B20_issued=true` 才可谈「到价」。
8. 公式中的年数均为 n（无写死 3）；RC1/RC2 低谷年结构满足；无 SBC 单边扣。
9. 若本轮 B20 上调 >5% 或到价状态翻转，`round_delta.listed_changes` 非空。

## V§20 用户保留决定（执行器与 a-3 不得自定）
1. M5 公用是否保留「三年 20%」门槛。
2. M5/M7 是否叠 3×DPS_min3（统一接口已按除息 FV3 输出，两种都算）。
3. M5 ERP 分档（水电 4.5 / 核电 5.5 / 环保特许 6.5pp，无回测）及 M5d 电信 ERP（空）。
4. R4–R6 是否由 DISPLAY 升为门控。
5. M7b 保险 NBV 倍数（空，不编造）。
