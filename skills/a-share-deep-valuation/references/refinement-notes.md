# Refinement pass 记录

## 2026-11-05 · 对人只报基准合理价
- 用户拍板：简约路径结论卡与聊天摘要**不再**报熊/基/牛三档，只给约三年基准合理价 + 闸价。
- 已改：`SIMPLE-FLOW.md`、`card-template.md`、`INVESTMENT-LENS.md`、`SKILL.md`。
- **未改** `valuation-rules-v3.md` 门槛常数；完整模式内部仍可保留多档自检，但不作为默认对人输出。

## 2026-11-05 · 投资透镜并入简约路径
- 新增 `references/INVESTMENT-LENS.md`：分析 / 筛选 / 估值 / 置换四块心智。
- `BUSINESS-DEPTH.md`：开头强制「被需要 / 难替代 / 价格不受管制」；竞争节写波特五力 + 护城河类型清单；利润质量强调假钱与自由现金流。
- `SIMPLE-FLOW.md`：核心思想补筛选三前提与「估值是比较」；合理价步骤加 15–25x 翻倍粗对照（不改闸价公式）。
- **未改** `valuation-rules-v3.md` 常数。

## 结构（2026-10-22 初版）
- 合并：TA 可达性与决策卡为一个 terminal state、一个 artifact（decision_card），因二者无独立 gate/恢复点。
- 合并：scenario_model 与 risk_register 同一 state 产出（同一修正回路），但保留两个 artifact（事实所有权不同，复核可分别回流）。
- 删除：独立的 laotang_assessment / gate_checklist artifact，并入 enterprise_analysis（同一 owner）。
- 删除：独立 data_gaps artifact，并入 source_index（缺口由来源事实拥有）。
- 删除：intake 单独的「用户对齐」state（默认缺数据不停问）。
- 降级：概率加权回报只作 valuation_decision 展示字段，不设 condition。
- 降级：D12 不再是独立阻断 condition，改为 gate 状态 + 评级影响（规则在 valuation-rules-v25.md）。
- 新增（相对用户 6 状态设计的唯一补充）：review 的 route=deep_analysis 回流（数据来源/闸门问题）。
- 去重：references 不含状态表/流转；SKILL.md 只含协议、硬约束、路由。

## 用例沉淀 · 宁德时代（default / PE 路径，2026-10-22）
- 投资收益禁止双计；excess cash 为零时不得再加回。
- 退出 PE：结构可比窗 ≥4y + 缩短 0.5y 时 P50 变动 ≤10%；回退档作下限对照。
- 窗口 P50 偏乐观时，基准退出 PE 可取 window_P50 与 fallback 中值**下压**（不得中值上修）。
- B 档暂定（B+/B/B-·暂定）封顶试仓；复核最多 3 轮、独立 subagent。（历史「B-暂定」读作质量 B + 确信暂定，须补 b_tier）
- 买点历史（策略 Page）：127→143.2→218.3→252.8→210.5（v2.5）。

## 用例沉淀 · 招商银行（bank / PB–ROE 路径，2026-10-22）
- **银行 hurdle = 总回报**：买点 FV3/(1+(h−y))³；y=前瞻可持续股息率（书面论证）；决策卡并列总回报/纯价格两列；仓位用熊市总回报。制造股低息框架直接套银行会系统性压低买点。
- **退出 PB 中值方向**：仅当窗口 P50 **高于**回退 base 时中值下压；窗口更严时直接用窗口 P50，禁止向回退中值上修（招行 R1 误用 0.975）。
- **无倍数修复列** = min(主路径, 回退路径)；回退不更严须注明。
- **ROE/PB 双杀**：同一 NIM/政策叙事不得既下调基准 ROE 又用历史低 PB 窗口双扣；二选一主扣减（招行选：ROE 回中性 13% + 保留低 PB 窗）。
- **老唐③**：须「有条件满足」级证据——权重法 vs 高级法 CET1、g≈ROE×(1−payout) vs 贷款增速、分红约束可检验不等式；不可只写高级法 CET1 高。
- **B5 护城河**：至少 3–5 家可比股份行 NIM/ROA/不良/CET1/PB 迷你表（实数，禁编造）。
- **脆弱比**：用熊/基同档买点或 FV 比，不用回报比误标。
- 终卡：B-暂定；B20/B22 总回报 35.32/33.55；现价 41.82 不买；卖点 88.48；可达性中。

## 行业分支
- intake 判定 `industry_branch`：`bank` | `default`。银行走 bank-gates + bank-valuation-rules；其余走制造/消费默认路径。
## 用例沉淀 · 策略进化试跑 #1（2026-10-26）
- 便宜≠买：执行前三角闸（增值空间 / 管理层进取 / 风险充分折价）；未齐不 promote、不试仓。
- 退出 PE：合格窗禁止默默退回纯回退；中点下压 ≠ 回退；拒窗须一手断裂证据（pe-audit 六只买侧变化已示范）。
- 文案纪律：候补到价 → `到价·候补不执行`；勿与贴近带「无底不试仓」混用（璞泰来卡曾混用）。
- 事件闸可压过价格到价：星宇 pre_Q3、亿纬 H股定价 → 抽象为 pre_event_hold。
- candidates 溢价字段统一用 premium_vs_B20_pct=(px−B20)/B20；gap_B20_pct 曾出现符号语义分裂。
- 高于卖点（迈为等）：观察/降频，不改买点；不把远溢价当「便宜候选」。
- 元学习：草案未安装 = 假进化；每轮至少 1 条审计→可粘贴 patch；规则原文 vs 决策卡原文做 diff。

## 用例沉淀 · 经典框架学习（2026-10-26）
- 源：Marks *It's Not Easy*；Buffett 1992 信；Damodaran cyclical/commodity PDF；老唐《估值的误区》；长桥行业生命周期。草稿：`（内部文稿未发布）`。
- 已装 L1 二级检查 + L2 周期 NI3 标签/峰谷自检进 valuation-rules-v25；**未**改任何正式买点。
- L3 阶段仪表盘五格暂缓，与 D15 lifecycle 一并装；利用率/政策只压力测试、禁止抬 B20。
- 进化例行配额：每轮 ≥1 篇经典框架原文（URL）+ ≥1 条可粘贴 patch；市场结构数字不得冒充框架学习。

## 用例沉淀 · 策略进化重跑（2026-10-26 a-3）
- 真读：Marks 2003 *The Most Important Thing*；Munger *Psychology of Human Misjudgment*；政府网动力/储能电池产能监测部署。草稿：`（内部文稿未发布）`。
- 批判吸收：不照搬「无买入清单/只做好年景平均」；耐心落在执行层；政策/利用率只压力测试。
- 已装 E1：证伪优先句 + lollapalooza 升级怀疑 + 周期价格夸大 + 外部激励过滤（valuation-rules-v25 / external-views）。
- 债务：Batch18 等缺 `ni3_path_tag`（L2 已装未回填）；~32 票 `gap_B20_pct` 符号分裂 → 看板只认 `premium_vs_B20_pct`。
- 到价短名单仍 promote=false；三角闸未齐不试仓。

## 用例沉淀 · 策略进化手动 r3（2026-10-26）
- 真读：Marks 2001 *You Can't Predict. You Can Prepare.*；Buffett 1987 信（Mr Market）；工信部光伏产业座谈会（规范竞争，2025-08-19）。草稿：`（内部文稿未发布）`。
- 边界：璞泰来到价正确但不执行，卡文案仍把主因写成「技术底不成立」（违已装候补叠层）；迈为等 ~18 只高于卖点拒试仓正确，缺 `above_sell_watch` 字面与降频。
- 已装 F1：competence_tag + above_sell_watch + 周期位置侧倾 + 候补禁句加固（valuation-rules-v25 / ta-reachability / card-template）。
- 债务延续：全员缺 ni3_path_tag；gap 符号污染；L3/D14/D15/Patch D 候装。未改任何 B20/卖点/promote。

## 用例沉淀 · 策略进化手动 r4（2026-10-26）
- 车道：**1 挖优质公司** + **3 估得更准**（相对 r3 买卖点轮换）。
- 真读：Buffett 1983（经济商誉附录）；Damodaran *Value of Control*；Marks *Risk Revisited Again*；工信部锂电规范条件 2024；工信部 2026H1 锂电运行。草稿：`（内部文稿未发布）`。
- 边界：璞泰来文案违规复发；恩捷/天赐远溢价缺 tag；迈为高于卖点；茅台 franchise 正例；智飞 eroded→FV=0 正确；珀莱雅 PE 窗纠正守住。
- 已装 G1（economic_goodwill_tag + status_quo）+ G2（永久损失风险语言 + ni3_path 触票补标映射）。未改任何 B20/卖点/promote。

## 用例沉淀 · 策略进化手动 r5（2026-10-26）
- 车道：**2 挖套利/相对错价** + **4 更好的买卖点**（相对 r4 轮换）。
- 真读：Damodaran *Relative Valuation*；Marks 1992 Microeconomics；Buffett 2008；Marks 1997 Investor/Speculator；NCEXC 2026电煤保供中长期合同；统计局 2026-09 能源生产。草稿：`（内部文稿未发布）`。
- 边界：陕西煤业 above_sell +225%（用户「严格是好的」→不放松）；璞泰来到价候补文案债；迈为高于卖点；恩捷/天赐远溢价相对链。
- 已装 H1（相对错价只压力测试）+ H2（strict_cycle_lock + marked_down 域 + 商品近峰禁令）。未改任何 B20/卖点/promote。

## 用例沉淀 · 策略进化手动 r6（2026-10-26）
- 车道：**1 挖优质公司** + **3 估得更准**（相对 r5 套利+买卖点轮换）。
- 真读：Marks 2014 *Dare to Be Great II*；Buffett *An Owner's Manual*；Damodaran *Growth and Value* (2008)；工信厅科函〔2026〕147号质量工作通知；统计局 2026年1—8月规上工业利润。草稿：`（内部文稿未发布）`。
- 边界：璞泰来文案债就地改→`到价·候补不执行`；迈为补字面 `above_sell_watch`；恩捷/天赐/亿纬补 `ni3_path_tag=recovery_path`；智飞 `spurious_or_eroded`；茅台/珀莱雅 franchise 正例补标；陕煤 `relative_mispricing_note`。**不改任何 B20/卖点/promote**。
- 已装 I1（quality_screen_note / 伪优质禁令 / look_through / dare_to_look_wrong 窄域）+ I2（growth_decomposition / 禁 CAGR·卖方·宏观利润直写 NI3）。

## 用例沉淀 · 策略进化手动 r7（2026-10-26）
- 车道：**2 挖套利/相对错价** + **4 更好的买卖点**（相对 r6 优质+估准轮换）。
- 真读：Montier *Seven Immutable Laws* + *I Want to Break Free*（绝对vs相对）；Tweedy Browne *What Has Worked in Investing*；李录 Columbia 2010 演讲实录；神华2025业绩说明会IR；统计局2026-09工业增加值；证监会2026财务造假专项。草稿：`（内部文稿未发布）`。
- **≤1** Marks/Buffett信/Damodaran（本轮 **0**）；含访谈/演讲配额（李录）。
- 边界：陕煤相对神华仍禁抬点；中国核电贴卖点→`near_sell_watch`；璞泰来分批「技术底」文案债再清；隆基/先导/阳光「链内相对」不打开试仓；亿纬到价候补不变。
- 已装 **J1**（absolute_mos_gate / least_bad_trap）+ **J2**（fat_pitch_patience / near_sell_watch / downside_first）。未改任何 B20/卖点/promote。

## 用例沉淀 · 策略进化手动 r8（2026-10-26 · 加厚 a-3）
- 车道：**1 挖优质** + **2 挖套利/相对错价** + **3 估得更准**（相对 r7 套利+买卖点；≥3 车道）。
- 真读：Mauboussin *Measuring the Moat*；Dorsey *Little Book That Builds Wealth*；Greenblatt Columbia Special Situations 课堂笔记；Schloss 1989 OID 访谈；段永平 2025-01-05 浙大问答；茅台2025年报；统计局固投1–9月；王新工业解读；工信部光伏规范2026征求意见；Lowenstein Perfect Storm。草稿：`（内部文稿未发布）`。
- **≤1** Marks/Buffett信/Damodaran（本轮 **0**）；访谈/演讲 ≥2（Greenblatt+Schloss+段永平）。
- 边界：茅台特许正例 / 智飞伪护城河 / 福耀成本 / 迈瑞切换成本 / 恩捷·天赐链内相对 / 隆基+光伏规范 / 陕煤成本曲线 / 恒瑞管线预支 / 宁德贴近买点 / 迈为设备伪优质。
- 已装 **K1**（moat_source_tag / 伪护城河 / ROIC–WACC 持续性）+ **K2**（special_situation_note / relative_overvalued_trap）+ **K3**（price_implied_vc_note / 不懂不碰 / 宏观禁抬点）。未改任何 B20/卖点/promote。
- 旧卡就地补标：迈瑞/福耀/恒瑞/宁德/汇川/爱尔/公牛/茅台/珀莱雅/智飞/恩捷/天赐/隆基/迈为/陕煤/璞泰来（文案/标签，不改数）。

## 用例沉淀 · 策略进化手动 r9（2026-10-26 · 加厚 a-3）
- 车道：**1 挖优质** + **3 估得更准** + **4 更好的买卖点**（相对 r8 轮换掉车道2重仓；≥3 车道）。
- 真读：Phil Fisher *Common Stocks* 15 Points + When to Sell；Charlie Munger *Psychology of Human Misjudgment*（1995 Harvard）；Seth Klarman FAJ 2010 访谈；Bruce Greenwald Columbia「Value Investing’s Long Run」；Terry Smith Fundsmith 2024 年信；迈瑞2026业绩说明会IR；统计局2026-09 PPI/CPI；财政部《企业会计准则解释第20号》；证监会退市后监管指导意见（2026）。草稿：`（内部文稿未发布）`。
- **≤1** Marks/Buffett信/Damodaran（本轮 **0**）；访谈/演讲 ≥2（Klarman FAJ + Munger Harvard）。
- 边界：珀莱雅贴近带剥夺感 / 璞泰来到价候补 / 中国核电 near_sell / 陕煤·百济 above_sell / 迈瑞IR禁抬点 / 爱尔·公牛特许贵 / 汇川成本切换 / 智飞伪护城河延续。
- 已装 **L1**（fisher_quality_gate）+ **L2**（epv_reliability_note）+ **L3**（full_price_discipline / proximity_deprival_trap / incentive_caused_bias）。未改任何 B20/卖点/promote。

## 用例沉淀 · 用户公理四优（2026-10-26 t220u）
- **四优缺一不可**：优质企业 + 优质生意 + 优质领导层 + 优质价格。
- 已装 **N1**（four_quality_gate）入 valuation-rules-v25 + card-template。不改 B20/卖点公式。
- 执行含义：到价≠升池；平庸生意/管理层不得因便宜 promote。

### N1b 候补生意+领导层闸（t222u · 2026-10-26）
- 用户：「候补里面也必须满足优质生意和优质领导层的标准」。
- 已装：valuation-rules-v25 §四优；candidates.json rules.candidate_entry；当时 active 83→27（归档 56）。**嗣后 t227u：关注列表只留已深研；候补 active→0（历史计数作废，以 watchlist/candidates 现状为准）。**
- 不改任何 B20/卖点；归档保留深估。

### N2 两层重定义（t225u · 2026-10-26）
- 正式 = 研究完成盯盘（E+B+M + 深估复核）；试仓另卡价格。
- 候补 = 够格待研（B+M；深估未完或事件闸）。
- 本轮：23 只研究完成候补升正式盯盘。**嗣后 t227u：柏楚/惠泰/南瑞/星宇凡已深研进正式；候补 active=0；关注列表≈35 全深研。**不改 B20/卖点公式。

## 用例沉淀 · 策略整理清洗（2026-10-26 cleanup · 非 a-3）
- 触发：用户 t232u「现在先整理一遍」；同日常 routine a-4 口径，立即跑一轮。
- **规则收口**：valuation-rules / ta-reachability 合并 r3–r9 重复的候补文案·above_sell·strict_cycle 叠层为「执行硬闸（权威收口）」；进化段保留出处、冲突服从收口节。同步 agent-data 与 （内部文稿未发布） 镜像。
- **池状态核对（t227u）**：正式 watchlist=仅已深研；候补 active=0（够格未研不进关注列表）。N1b/N2 旧计数（active 27/4）作废。
- **卡/池文案**：璞泰来等到价候补改 `到价·候补不执行`；正式贴近带保留「见底前不试仓」合法语义；中国核电动作对齐 `near_sell_watch`；补 formal `card_path`。
- **未做**：不整池重估、不改 B20/B22/卖点、不跑 a-3 进化学习。

## 用例沉淀 · 策略进化手动 r10（2026-10-26 · a-3 补完）
- 车道：**2 挖套利/相对错价** + **3 估得更准** + **4 更好的买卖点**（相对 r9 的 1+3+4 / r8 的 1+2+3）。
- 真读：Pabrai Fool 清单访谈；Bakshi Bullet-Proof 演讲；Thorp Meb Faber/AQR 访谈；Gatev pairs RFS；Einhorn Colossus 访谈；恒瑞/百济 H2026；统计局能源2026-09；证监会财务造假综合惩防意见答问。草稿：`（内部文稿未发布）`。
- **≤1** Marks/Buffett信/Damodaran（本轮 **0**）；访谈/演讲 ≥2。
- 边界：璞泰来 ta 文案债、恩捷/天赐/隆基链内相对、迈为/陕煤 above_sell、核电 near_sell、星宇正式事件闸、珀莱雅/欧普贴近带、百济/恒瑞管线预支。
- 已装 **M1**（chain_relative_ban / pair_spread_note）+ **M2**（premium_field_canon / accounting_ni_quality_note）+ **M3**（at_price_action_canon / formal_event_gate）。未改任何 B20/卖点/promote。
- 就地：璞泰来 ta JSON；恩捷/天赐/隆基/百济/迈为/陕煤标签；星宇 action 句式；candidates 链标记。

## 用例沉淀 · 策略进化 r11（2026-10-26 · a-3 21:24 fire）
- 车道：**1 挖优质公司** + **2 挖套利/相对错价** + **4 更好的买卖点**（相对 r10 的 2+3+4 / r9 的 1+3+4 / r8 的 1+2+3）。
- 真读：Nomad Letters（Sleep/Zakaria）；Akre Talks at Google 转录；Helmer×Lawson NFX 7 Powers 访谈；Druckenmiller NBIM In Good Company 转录；Mitchell–Pulvino JF2001 风险套利；Xiong–Yu AER2011 中国权证泡沫；北方华创 H1 2026；SEMI 2Q26 设备开支；国家能源局 1–9 月电力统计；智通 AH 统计 10-26；证监会减持暂行办法。草稿：`（内部文稿未发布）`。
- 已装 **O1** quality_edge_resolution/three_legged_stool/power_type_tag；**O2** arb_reality_check/ah_discount_note/short_constraint_persistence；**O3** thesis_break_exit/sell_reason_audit/forward_18_24m_check/overhang_note/above_sell_literal_canon；**O4** semi_equip_dual_tag。执行硬闸 +13/14/15。
- 就地：中微/北方华创 watchlist sell 空值→卡锁定数投影 + above_sell_watch；35 张正式卡加 r11 投影行（四优/premium/卖侧标签/ni3）；19 张卡旧「不进正式/留候补」文案注释为「试仓不执行」；11 名补 ni3_path_tag；汇川/贝泰妮 quality_edge_note；宁德/药明/招行/美的/恒瑞 ah_discount_note。未改任何 B20/B22/卖点数字、未 promote/降层。

## 用例沉淀 · P1 升档触发 + P1b（2026-10-26 t251u/t253u；cleanup-20261027 合并两节）
- 用户弧：市场 PE 有道理；老打 B- 会永远没机会；问如何预估快于定价 →「优化」（t251u）；随后「不用压力轨，增加复杂度」（t253u）。
- 现行：`leading_indicator_upgrade` = `upgrade_triggers` + `upgrade_review_due` + 双向复核（硬闸 §16 + 专节）；压力轨已退役（唯一表述在硬闸 §16）。
- 就地：珀莱雅/汇川/贝泰妮/欧普康视/星宇写 triggers；不改任何执行 B20/B22/卖点；不 promote/降层。routine：`（内部文稿未发布）`。

## 用例沉淀 · P2 评级双轴（2026-10-26 t258u「重新制定评级规则」）
- 用户弧：看板全是 B-暂定不合理；老唐会给茅台更高评级；同意拆 **质量档 vs 确信档**。
- 已装 **P2** `grade_two_axis`：valuation-rules-v25 §2 重写 + 硬闸 +17 + 专节；card-template 评级行；本注。
- 展示：`grade=质量·确信`（A·确认 / A·暂定 / B·确认 / B·暂定 / C…）；字段 `quality_grade` + `confidence`。
- 关键纠偏：温和批价/需求周期 **不挡** 特许现金牛给 A（茅台类）；edge → 最高 B；**暂定**→试仓封顶；A·确认按脆弱比/熊市年化正常档。
- 就地：正式池 35 名重标；茅台/招行 → A·暂定 + `hurdle_reval_pending`；**零改动**任何 B20/B22/卖点。
- 审计：`（内部文稿未发布）`；routine：`（内部文稿未发布）`。

## 用例沉淀 · P2b B 内档（2026-10-26 t262u「B档也要分好坏；宁德比珀莱雅好」）
- 用户弧：B 也应分好坏；宁德时代明显强于珀莱雅。
- 已装 **P2b** `b_quality_tier`：valuation-rules-v25 §2.1b + 硬闸 +17 扩展 + 专节；card-template；本注。
- 展示：`quality=B` → `grade={b_tier}·{confidence}`（B+·暂定 / B·暂定 / B-·暂定）；A/C 不变；`b_tier` 字段。
- **不改** A/C 规则、**零改动** B20/B22/卖点；仓位仍看确信+edge/事件闸。
- 种子：宁德→B+；珀莱雅/贝泰妮/欧普/汇川(edge)→B-；优势龙头四优全 pass→B+。
- 审计：`（内部文稿未发布）`；routine：`（内部文稿未发布）`。

## 用例沉淀 · 重点门控 t298u（2026-10-27「只关注 A 和 B+；B/B- 只有足够便宜才进重点」）
- 用户 t298u：主注意力给 A 与 B+；B 与 B- 仅当价格足够便宜才进重点关注。
- **重点定义（现行权威）**：
  - A/B+：`(A·|B+·) ∧ premium_vs_B20_pct≤20`（近价带不变）
  - B/B-：`(B·|B-·) ∧ premium_vs_B20_pct≤0`（**收盘≤NI B20**；不用 20% 近价带）
- 取代 t266u/t267u（2026-10-26「重点只留 A 与 B+」，该节已删）；正式池与「全部」仍保留全部档；**零改** B20/B22/卖点；重点≠试仓。
- 就地：重算 `focus_list`；星宇（B· −17.3%）进重点；珀莱雅/欧普等 B- 贴近带仍不进。
- 审计：`（内部文稿未发布）`；routine 草稿同文件（供 parent UpdateRoutine a / a-4）。

## 用例沉淀 · P3 NI/FCF 双轨（2026-10-27 t280u/t282u）
- 用户弧：严格 FCF→统一 ~20x；利润口径→窗口 PE；对照不够 → fuller 双轨；「你看着办」锁定默认并安装。
- 已装 **P3** `fcf_ni_dual_track`：valuation-rules-v25 专节 + 硬闸 +18；card-template 双轨字段；本注。
- 锁定：分歧阈值 **20%**；PE_fcf=**20**；≤FCF_B20且>NI_B20→`FCF到价·并行观察`；卖点只认 NI；看板可选列 `FCF_B20`；推广美的/海尔→A/B+。
- 样板：美的/海尔写入 FCF 字段；gate 诚实 pending → `fcf_track_executable=false`；**零改** NI buy_b20/buy_b22/sell。
- 草案：`（内部文稿未发布）`；routine：`（内部文稿未发布）`（parent UpdateRoutine）。

## 用例沉淀 · 策略进化手动 r13（2026-10-27 · 用户 t293u「先学习一次」）
- 车道：**1 挖优质公司** + **3 估得更准** + **4 更好的买卖点**（相对 r12=1+2+3；**必须含 r12 跳过的车道4**）。
- 真读：Gayner Markel Omaha 2025 转录；Thorndike Southeastern P2V 访谈；Mauboussin *Expectations Investing*（官网章节导读）；Chanos The Market 访谈；Bloomstran Semper 2024 信（检索摘要+Graham 纪律）；美的IR 2026-09-15；商务部新国补；财政部2025准则实施报告；海尔/美的既有H1披露对照。草稿：`（内部文稿未发布）`。
- **≤1** Marks/Buffett信/Damodaran（本轮 **0**）；访谈/演讲 ≥2（Gayner+Thorndike+Chanos）。
- 边界：美的/海尔 P3 pending；海尔重点+贴近带；茅台/招行 hurdle_reval×重点；汇川 edge+会计；中微/北方华创 above_sell；珀莱雅/欧普 B- 非重点；星宇事件闸；宁德 overhang。
- 已装 **R1** capital_allocation_sequence_note / tob_reinvestment_vs_A；**R2** price_implied_expectations_note / fcf_pending_not_soft_buy / adjusted_ni_red_flag；**R3** focus_gate_not_trial / trim_when_rich。执行硬闸 +19/+20。
- 就地：重点6名打 `focus_list`+禁试仓注；美的/海尔卡钉 FCF pending≠软买；汇川 accounting 注；茅台/招行重点∩hurdle_reval 注。**未改任何 B20/B22/卖点/promote**。

## 用例沉淀 · 策略进化 a-3 r14（2026-10-27）
- 车道：**2 挖套利/相对错价** + **3 估得更准** + **4 更好的买卖点**（相对 r13=1+3+4；**必须含 r13 跳过的车道2**）。
- 真读：Greenblatt Ritholtz MIB 转录；Nick Sleep Nomad Letters PDF；Akre Latticework 访谈；John Huber Acquirers Ep.70 转录；Tweedy *What Has Worked* PDF；宁德/亿联 IR；经济参考报年报问询；证监会再融资征求意见；上交所再融资一揽子。草稿：`（内部文稿未发布）`。
- **≤1** Marks/Buffett信/Damodaran（本轮 **0**）；访谈/演讲 ≥2（Greenblatt+Huber+Akre）。
- 边界：宁德 A/H+SES；美的 A 溢价+FCF pending；星宇到价事件闸；核电 near_sell；东方电缆 recovery+链相对；公牛品牌溢价；福耀/亿联重点缺 ni3；半导 above_sell 组内相对；招行/茅台 hurdle×重点；锂电 archived 链。
- 已装 **S1** peer_history_screen_not_b20 / special_situation_mispricing_hunt / refi_dilution_stress_only；**S2** scale_economics_shared_vs_ni_dip / option_buyback_net_dilution；**S3** watchlist_wait_absolute_pitch / size_by_downside_not_upside / formal_event_gate_holds_at_price。执行硬闸 +21/+22/+23。
- 就地：缺 ni3 正式名投影补标；宁德/美的/星宇/东方电缆等钉相对与事件闸注。**未改任何 B20/B22/卖点/promote**。

## 用例沉淀 · 策略进化 a-3 r15（2026-10-27）
- 车道：**1 挖优质公司** + **2 挖套利/相对错价** + **4 更好的买卖点**（轮换：r14=2+3+4 → 本轮必须 1+2+4）。
- 真读：François Rochon Giverny 2025 年信 PDF；Terry Smith Fundsmith Equity Fund 2025 年信 PDF；Marathon/Chancellor *Capital Returns*（资本周期）+ Marathon London 框架页；Chris Davis Excess Returns/100 Year Thinkers 访谈转录（2026-10）；Joel Greenblatt Farnam Street Knowledge Project Ep.111 访谈要点；海尔智家 IR 2026-10-16；证监会《上市公司2025年年度财务报告会计监管报告》；中国政府网消费品以旧换新；港交所 A-H 估值研究 2016；星宇半年度业绩说明要点。草稿：`（内部文稿未发布）`。
- **≤1** Marks/Buffett信/Damodaran（本轮 **0**）；访谈/演讲 ≥2（Davis + Greenblatt KP）。
- 边界：星宇到价事件闸；海尔贴近带+重点+FCF pending；珀莱雅/欧普 B-贴近带；茅台重点∩hurdle；美的溢价+FCF div；宁德 B+重点+A/H；中微/北创 above_sell；核电 near_sell；候补全 archived 卫生；美的/海尔 NI/FCF 分歧书面原因。
- 已装 **T1** candidate_active_requires_biz_mgmt_pass / franchise_cash_cow_vs_midcycle_leader_hunt / compounder_seed_not_b20；**T2** ah_premium_not_catalyst / stub_spinoff_hunt_not_b20；**T3** near_band_not_trial_without_bottom / focus_list_priority_not_size / above_sell_no_averaging_up。执行硬闸 +24/+25/+26。
- 就地：美的/海尔补 `divergence_written_reason`；海尔/珀莱雅/欧普/茅台/星宇/中微/北创/核电钉 r15 标签；候补池抽检无 active 缺闸。**未改任何 B20/B22/卖点/promote**。

## 用例沉淀 · 策略进化 a-3 r16（2026-10-27）
- 真读：Pat Dorsey Morningstar Long View 访谈全文（经济护城河/管理层/premortem）；Thomas Russo TIP Richer Wiser Happier 访谈全文（capacity to suffer/reinvest、agency cost）；Cliff Asness et al. *Fact, Fiction, and Value Investing*（JPM 2015 PDF）；Bruce Greenwald Motley Fool 访谈（EPV/回报空间）；Baillie Gifford Scottish Mortgage 2025 年报 Managers' Review（outliers/适应性/Northvolt 课）；CFA Residual Income Valuation 2026 refresher；财政部财会〔2024〕26号年报通知；政府网/工信部动力储能电池产能治理；经济观察网锂电库存与利用率分层；福耀/汇川 Q3 业绩说明会安排与已知季报数字。草稿：`（内部文稿未发布）`。
- 已装 **U1** capacity_to_suffer_reinvest_hunt / moat_not_great_product / founder_scale_micromanage_liability+premortem_signal_weight；**U2** pure_value_screen_not_b20 / cheap_for_a_reason_check / multi_measure_relative_only；**U3** returns_space_not_growth_pe / residual_income_equity_charge_cross / epv_before_franchise_growth。执行硬闸 +27/+28/+29。
- 就地：汇川/贝泰妮/招行/恒瑞/药明/美的(pe_fcf规则错配钉)/福耀/国电南瑞/中控·绿的 等钉 r16 标签；候补池抽检无 active。**未改任何 B20/B22/卖点/FCF_B20 数字**。

## 用例沉淀 · 到价/贴近带强制分批计划 t304u（2026-10-27「结合技术面制定分批计划；以后所有公司都需要」）
- 用户 t304u：到价名要有买入分批计划；以后正式到价或贴近带一律结合技术面写计划。
- **规则**：决策卡 + digest 强制「分批计划」节；T1/T2/T3 + 第一支撑 + 暂缓；闸（事件闸/edge/暂定封顶/候补）挡执行不挡写计划（「闸清后执行」）；TA 永不抬 B20；重点≠试仓。
- 已装：valuation-rules-v25 硬闸 +33 + 专节；card-template；ta-reachability；本注。
- 就地：星宇（到价·事件闸）+ 腾讯（到价·暂定试仓封顶）写出完整计划；**零改** B20/B22/卖点。
- 审计/routine：`（内部文稿未发布）`（供 parent UpdateRoutine a / a-4）。

## 用例沉淀 · 正式仓升级计划 t306u（2026-10-27「为什么你没有定正式仓的计划呢」→「补上，现在就做」）
- 用户 t306u：到价卡只写了试仓 T1–T3，缺「何时、如何从试仓升到正式仓」。
- **规则**（扩展 t304u 专节第6/7条 + 硬闸§33 一句，不另起层）：到价/贴近带正式名同卡并列两段——①试仓 T1–T3（现可执行）；②正式仓升级计划（命名验证点→确认、解封条件、F1/F2/F3 TA 触发与规模、暂缓、降档/中止）。升级前 F 只写不执行；TA 不触发升级、不抬 B20；FCF pending≠软买；重点≠试仓。
- 已装：valuation-rules-v25（§33 + 专节6/7）；card-template；ta-reachability；本注。
- 就地：星宇（UT1 Q3≤10-31 + UT3 FY2026 年报 → 确认；F 用 59.7–62.2 / 55.6–58.3）；腾讯（cash_quality_gate + OQ2/OQ4 连续 2–3 季 + OQ1/OQ3 无 BRK2/3 + IR7/8 → 确认；F 用 355–360 / 周线 HL）。**零改** B20/B22/卖点。
- 审计/routine：`（内部文稿未发布）`（供 parent UpdateRoutine a / a-4）。
- **t307u 修订（「开放问题永远存在＝永远等」）**：升级前置只许**定日硬条件**（具名报告/事件+阈值+预计日期）+ 独立复核无击穿码；禁多季观察/OQ 解决作前置；OQ 与确认型后续验证（次年年报）转**持有期跟踪项**，各配恶化信号→暂缓F/降档/重估。就地改专节第6/7条（未加层）。
- **t308u 补充（「别反射性等下一个节点」）**：手头数据可判者当轮判；未来节点仅当能翻转结论才作前置（须写理由）。腾讯 `cash_quality_gate` 用 FY21–25 年报当轮判=**borderline**（OCF/NI 稳、一次性已由 non-IFRS 剔除；但 FY24 起 capex 强度 3–4%→10–12%、H1'26≈21%，维持性 capex 不可估 + 2Q'26 AI 预付扭曲占款）→ FCF 仍仅展示；Q3'26 降为跟踪项。星宇 Q3（≤10-31）保留为前置：H1 归母−5.26%/OCF−17.3%，Q3 可落 <3.2 亿回流阈，确能翻转。UT3 FY26 年报转跟踪项。
- 结果：星宇最早解封≈Q3 披露（≤10-31）+复核；腾讯最早解封=**现在**待独立复核。审计：`（内部文稿未发布）`。

## 用例沉淀 · 仓位阶梯与升A路径 t310u（2026-10-27「那半仓和全仓的区分不是就没有意义」）
- 问题：§2.3/§4「B·确认 默认≤半仓除非脆弱比低」未定义，且无 B→A 书面路径 → B 名永远卡半仓，满仓只靠罕见 A·确认。
- **就地改** §2.3 表 + §4（确认后阶梯表）+ §2.1 A 段（B→A 升档路径 A1–A6）；仓位 % 明确为该股计划仓位份额。
- 阈值：B 超半 75%（F4）= 脆弱比 ≥0.70 ∧ r_bear_exec ≥+10% ∧ 无 edge/闸；A 满仓 100%（F5）= 脆弱比 ≥0.60 ∧ r_bear_exec ≥+5%。校准：37 名正式池脆弱比 P50≈0.52，0.70 为自然断层（5 名过）；r_bear≥0 在 ≤B20 执行时对脆弱比 ≥0.579 恒真，不区分，故提到 +10%。
- 腾讯 B+·确认 脆弱比 0.57 → 上限 50%，无 F4；卡/看板不变。当前无 A·确认；A·暂定=茅台/招行。
- 审计：`（内部文稿未发布）`。

## 用例沉淀 · r19 P-X4/P-X5（2026-10-27 用户授权 t312s1485）
- **P-X4**：`ni3_base_rate_cross` 的 >30% 软句升级为硬闸 `bear_ni3_le_base_rate_median`——熊市 NI3 ≤ NI0×(1.068)^T；违例 → `bear_rebase_pending`+`hurdle_reval_pending`，**禁止**安装轮静默改 B20/B22/卖点；NI0 缺失 → `ni0_base_rate_pending`（不视为违例）。银行分支不适用。硬闸 §39 + 文末 X3 专节 1b。
- **P-X5**：§2.1 B→A 路径增 **A7**（Tillinghast）：10 年 ROE>12% 至少 8/10；程序改为 A1–A7 全过。`four_elements_cross` 改为指向 A7 硬门槛。
- 就地核对（本轮零改 B20）：可抽取 NI0 的 7 名（美的/茅台/福耀/百济/柏楚/海尔/腾讯）熊市均 ≤ 中位 → **无** `bear_rebase_pending`；其余缺 NI0 待下次 scenarios 补写，不打违例标。
- A7 当轮：茅台 **pass**（10/10 加权ROE>12%）；招行 **pass**（可核 9 年加权ROE 全>12%，2021 缺数仍 ≥8）；腾讯 **pass**（HK ROE_AVG 2017–2025 共 9 年全>12%，最差仍 ≥8/10）。
- 审计：`（内部文稿未发布）`（P-X4/P-X5 标已装）。

## 用例沉淀 · 持仓卖出带宽补丁 t319u（2026-10-27「先对上面的问题优化一版」）
- **批判原点**：卖点≈B20×2.6 → 中间持有带过宽；质量降级名可借「未到卖点」占仓；换仓条款空转；与个人账户现金及个股权重（已略）打架。
- **已装（零改 B20/B22/卖点公式）**：硬闸 §40–§42 S1/S2/S3 机制；§5 指针；sell_reason_audit / full_price_discipline；card-template。**文案已被 t320u 统一为置换句**（见下节）。
- **压力测试（holdings-20261027）**：分众→不合格置换出；美的→公允溢价置换带；古井/中兴→研究缺口；宁德等→持有观察；腾讯 F1 可执行（后被 14:42 用户确认无港股通推翻 → channel_unavailable）。
- 审计：`（内部文稿未发布）`。

## 用例沉淀 · 只有置换 t320u（2026-10-27 用户观念对齐）
- **观念**：现金与每只股票对等；忘掉买/卖，只有 `置换：A→B`。持有现金（≈r_f）而存在更高期望到价名，也是需写明的选择。
- **已装（零改 B20/B22/卖点数字）**：§5 硬原则；§40–§42 与文末专节改写为置换主语言（旧「退出/减仓」作别名）；full_price_discipline / sell_reason_audit；card-template；看板美的/腾讯；本注。
- **映射**：S1 `置换：不合格持仓→现金/更优`；S2 `置换：公允附近溢价仓→现金/更优`；S3 到价加仓必须具名资金袖 `置换：现金→到价名` 或 `持仓→到价名`。
- 审计：`（内部文稿未发布）`；routine 一句供 a / a-4 / a-3。

## 用例沉淀 · 策略整理清洗（2026-10-27 cleanup · 非 a-3）
- 触发：日常 a-4 清洗；复杂度闸 t296u（删冗余、合并叠层、不新增分支/买点公式）。
- **规则收口**：valuation-rules-v25 硬闸 §11/§12/§14/§21/§23/§25/§26/§28/§34/§36 并入 §3/§5/§8/§15/§38（编号保留为「并入」桩，避免外部引用断链）；P2/P2b 两专节删正文改指针（§2 权威）；r12/r15/r18 AH 节删正文（ah_canon）；r13/r15/r17/r18 买卖点/重点重复节压成指针；「组合置换动作带」删与 §40–§42 重复的 S1–S3；~40 条「与…关系：冲突服从」样板句删除，改为文首一句读法。
- **现金门槛**：唯一口径 §61（511990 停泊收益率）；§52 保留位置/来源账本；r20/r21 的中债 10Y 1.64% / 3Y 1.26% 门槛口径标废止并从 §43/§48/Y1/Y3 删除。
- **港股**：§44/§46/Y2 改为 `channel_unavailable`（用户无港股通）。A7 在 §2.1 指向 §59 双口径。
- **池/卡**：37 张正式卡删通用 r12/r13/r14 叠层投影、加一行当前权威投影；美的/腾讯/古井/中兴/宁德动作与 swap-plan v3 对齐；candidates `gap_*` 字段清为 `premium_vs_B20_pct`。审计：`（内部文稿未发布）`。

## cleanup-20261028（a-4 · 非 a-3）
- 规则：进化学习节 r10 链内/溢价/套利/卖出纪律 + r23–r35 安装叙事收成出处指针；硬闸 §1–§112 全文保留（含组合层 §90–§112）。
- deep-analysis-gates D12：禁光秃 `B-暂定` 作唯一档，改 P2b `{b_tier}·{confidence}`。
- 零改 B20/B22/卖点/股数；agent-data 规则镜同步。

## 2026-11-06 · 退出市盈率改判断带（用户拍板）

问题：用历史同年 PE 中位数当主报，易把增长扩张期高倍数写进退出常态（古井 28.1 案例）。  
改法：简约默认主报退出倍数在约 **20～30** 内按生意质量/周期位置判断取值；中位数与修剪窗只作参照。已写入 `SIMPLE-FLOW` §4、`INVESTMENT-LENS` §3、`SKILL` 步骤4、glossary。
