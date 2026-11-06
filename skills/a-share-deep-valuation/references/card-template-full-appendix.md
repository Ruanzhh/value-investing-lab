# 决策卡 · 完整模式机器附录（非默认）

> 仅完整模式 / 需要机器字段投影时读取。简约路径**不要**把本节堆进首屏。

## 附录 · 机器投影规则（原模板 · 执行仍服从）

> **卡面规则投影（cleanup-20261027 合并原 r10–r19 / t298u–t308u / P1–P3 共 15 行叠层；权威=valuation-rules-v3 V§4/V§7/V§8/V§10（legacy v25 §2 + 硬闸 §1–§142 映射）；§5 击穿码先重估证收益再置换（r47-D1）/§42 到价具名资金袖）**
> - 评级：`{b_tier|quality}·{confidence}`（B 必标 B+/B/B-；禁光秃 `B-暂定`/`B·暂定`）；改档不改 B20，A/hurdle 带变→`hurdle_reval_pending`；A 升档=A1–A7，A7 双口径（报表+§55 调整后 ROE 均 ≥8/10 年 >12%，贴线→`a7_margin_thin`，§59）；`predictability_edge` 不走 A；中周期/ToB 再投入最高 B+，挡 A 须写机制（§56）。
> - 卡首投影行：层级 + four_quality_gate + premium_vs_B20_pct（唯一溢价字段）+ 卖侧字面 + ni3_path_tag(周期) ；四优 edge→`quality_edge_note` 且到价不试仓；熊 NI3≤基率中位路径（违例只打 `bear_rebase_pending`）。
> - 重点(t298u)=(A·|B+·)∧≤20% 或 (B·|B-·)∧≤NI B20；重点≠试仓。相对/历史/AH/特殊情形永不抬 B20（ah_canon）。
> - 到价/贴近带：必须写分批计划 T1–T3 + 正式仓升级计划（定日硬条件+复核；现数先判；OQ→跟踪项；闸挡执行不挡写计划）；TA 永不抬 B20；贴近带未见底=`见底前不试仓`。
> - P1 `upgrade_triggers`（edge / B 档暂定存疑 / 纯回退 / 事件闸）只标 `upgrade_review_due`；P3 FCF 轨 gate≠pass 仅展示、卖点只认 NI；`NI_only`/分歧锁定时禁止并列「FCF到价·并行观察」（§111）；距B20 只认 NI（§112）。
> - 组合层：只用 `置换：A→B`；S1 `置换：不合格持仓→现金/更优`；S2 `置换：公允附近溢价仓→现金/更优`（含股息>现金门槛→仅为可执行目的地出资，§54）；S3 须具名资金袖；现金门槛=511990 停泊收益率（§61）；新置换入试仓上限 5% 组合/名，2026-10-27 存量暂定 12.5%（§53）；港股名 `channel_unavailable`。
卡片是投影：所有数字引用 owner artifact，不得新增事实。执行标签冲突时服从 `valuation-rules-v3.md`（LIVE；V§8/V§10）与 `ta-reachability.md` 投影；legacy 长文见 `valuation-rules-v25.md`。

## 默认（制造/消费 · PE）
```
# <名称>（<代码>）决策卡 · <日期> · 现价 <p>
评级：<A|B+|B|B-|C>·<确认|暂定>（B 用 b_tier 展示） · hurdle <x%> · 复核轮次 <n>（subagent <id>）
grade_fields：quality_grade=<A|B|C>；b_tier=<B+|B|B-|null>；confidence=<确认|暂定>；hurdle_reval_pending=<true|false>
a7_roe_persistence：years_checked=<n>/10；above_12pct 报表=<k>／调整后(§55)=<k_adj>；threshold=12%；a7_margin_thin=<bool>（调整后第8高<13%）；verdict=<pass|fail|pending>（两口径均过才 pass，§59）；source=<加权ROE|ROE_AVG|…>（升 A / A·暂定确认时强制）
bear_ni3_vs_base_rate：ni0=<x>；T=<年>；median_path=<ni0×1.068^T>；bear_ni3=<y>；verdict=<pass|fail|ni0_pending>；bear_rebase_pending=<true|false>（非银 NI3 卡强制；违例只打标不改数）
## 买卖点
买点 <b>（NI 轨 · 基准 FV3 <f> / (1+h)^3）｜老唐参照 <l>（是否入 min）｜卖点 <s>（NI 轨）
FCF 轨：FCF₃ <fcf3> × PE_fcf=20 + excess → FCF_FV3 <ff> → FCF_B20/B22 <fb20>/<fb22>（敏感性 18/22 可选）
cash_quality_gate=<pass|fail|pending>；fcf_track_executable=<true|false>
分歧：div_pct=<x%>；阈值=20%；fcf_ni_divergence_review=<true|false>；divergence_written_reason=<强制一句，禁静默>；note=<…>
无倍数修复对照：min(主,回退)
熊/基/牛 FV3：… ｜三年年化（展示）：…
回报拆解（§109，执行价=min(现价,B20)）：盈利增长 <x>% / 估值修复 <y>% / 股息 <z>%；估值不修复（PE 维持执行时）年化 <r_nr>%（含息）；y≥50% → 首屏标「主要靠估值修复」
## 仓位
「估值不修复」档（§109，仅主要靠估值修复名）：r_nr ≥10% 不另压 / 0–10% 半首批 / <0 只试仓；与下列取最严
熊市年化 <r_bear> → <档>；脆弱比 <x>（熊/基买点或 FV）→ <结论>；确信=暂定→试仓封顶；A·确认按正常档；最终：<满额首批/半首批/试仓/观察>
## 分批计划（t304u · 到价或贴近带强制；闸挡执行不挡写计划）
计划仓位封顶 <试仓|半首批|满额>（单股 ≤25% 组合）；确信=暂定→试仓封顶（新置换入 ≤5% 组合/名，§47）；**T/F 规模 % = 该股计划仓位份额，非组合 %**（t310u）；资金袖：`置换：<具名资金袖>→本股`
T1：触发价/条件（到价确认；或贴近带+见底整笔试仓）；规模 ≈30%
T2：回第一关键支撑 <区> **或** 自 T1 再跌≥5%（先到）；规模 ≈30%
T3：仅可达性≠低且第二笔后逻辑仍在；试仓封顶时常不做；规模 ≈40% 或「不做」
闸门投影：事件闸/质量edge/候补不执行/暂定封顶 → 写「闸清后执行」步骤，禁止空缺本节
暂缓：放量跌破第一关键支撑且收盘不收回 → 未执行下一笔暂缓
## 正式仓升级计划（t306u/t307u/t308u · 到价/贴近带强制；升级前只写不执行）
现状：<grade>·暂定 → 试仓封顶；闸/gate：<事件闸|edge|cash_quality_gate=pass|borderline|fail>；upgrade_review_due=<bool>
现数先判：<用既有年报/run 数据当轮判定的条件 → 结论 + 理由>（pending 仅限确无数据）
升级前置（仅定日硬条件 + 复核；不自动确认）：<P1 具名报告/事件 + 阈值 + 预计日期 + 「为何可翻转」一句> ；<Pn 独立复核：无击穿码>
跟踪项（持有期；不阻断升级）：<OQn/确认型验证 → 恶化信号 → 暂缓F | 降档 | 重估>
最早解封：<日期（含复核）>；解封后上限按 §4 确认后阶梯（脆弱比 <x>；r_bear_exec <y>；→ <50%|75%|100%> 计划仓位）
F1：确认生效且收盘≤NI B20 <b> → 补至首批满额（计划仓位≈30%，含已成交试仓）
F2：回第二支撑 <区> 或自 F1 再跌≥5%（先到），且≤B22 <b22> → 至≈40%
F3：第三支撑 <区> 或周线首个 HL，收盘仍≤B20 且可达性≠低 → 至 50%
F4（仅 B 超半档或 A·确认）：收盘 ≤ min(B20, 熊FV3/1.331)（A：仅需≤B20 且回第三支撑/周线 HL）→ 至 75%；不满足写「无 F4（脆弱比 <x> <0.70）」
F5（仅 A·确认满仓档）：收盘 ≤ min(B20, 熊FV3/1.158) ∧ 脆弱比 ≥0.60 → 至 100%
暂缓：放量破当时关键支撑不收回 / 收盘>B20 / 跟踪项暂缓信号 / owner 待重算 → 下一 F 暂缓
降档/中止：<回流阈 / 击穿码 / 跟踪项降档信号 / 复核降档> → F 作废，回试仓封顶或退出复核
## 技术可达性与执行
距离、支撑阶梯（含第一关键支撑）、周线趋势、等级；是否上调首批触发（理由）
贴近带：是否（溢价 x% / 否）；见底候选是否；动作（整笔试仓 / 观察）
到价分批：须与上方「分批计划」一致；是否技术暂缓加仓；digest 须能复述 T1/T2
能力圈：competence_tag=<in_circle|edge|outside>（outside→能力圈外·观察；edge→试仓封顶+额外证伪）
卖侧：现价>卖点 → `above_sell_watch`；sell×0.95≤现价≤卖点 → `near_sell_watch`；持仓侧写 `置换：<本股>→停泊现金(511990)/具名可执行更优名`，非持仓侧不从现金/他袖置换入；降频、禁抬点
置换·不合格（t319u S1 / t320u）：四优企/生/管 fail 或质量 demote/archive → `置换：不合格持仓→现金`（或→更优到价名；不等卖点；可分批）
置换·公允溢价（t319u S2 / t320u）：B 档已持仓且 FV0×0.95≤现价<sell×0.95 → `置换：公允附近溢价仓→现金/更优`（朝上限修剪；非清袖；不改卖点；>B20 禁再置换入）；含股息 implied_3y_total>现金门槛(§61) → `S2·含股息>现金→仅为可执行目的地出资`（§54）；A 档默认持有该袖除非硬顶
置换·到价（t319u S3 / t320u）：到价可执行 → 必须写 `置换：<资金袖>→<到价名>`，资金袖∈{停泊现金, 不合格, 公允溢价(受§54限), 近25%硬顶, 期望差≥10pp持有袖, 超档部分}，按 implied_3y 由低到高取（到价腿绝对 MOS，禁发明买点；目的地须 A 股可执行）
研究缺口：无正式深研持仓 → `研究缺口·优先补研或限仓`（禁发明 B20）
观念：现金与各股对等；无独立买/卖，只有置换
绝对优先：相对便宜禁开执行；least_bad_trap=整组无MOS时链内最不贵仍观察
fat_pitch_patience：机会集无绝对MOS→等待/观察；禁为行动偏见降纪律
候补到价：promote=false 且≤B20 → 动作必须含 `到价·候补不执行`（禁写「无技术底」作主因）
经济商誉：economic_goodwill_tag=<franchise_pricing|durable_low_cost|regulated_franchise|tangible_heavy|spurious_or_eroded>
估值口径：valuation_basis=status_quo（禁止 optimal/控制溢价抬 B20）
风险折价：永久损失检查句；脆弱时 risk_in_price=addressed|insufficient
周期：ni3_path_tag 触票按 cycle_position 补标（recovery_path|peak_fade|normalized_midcycle）
相对错价：relative_mispricing_note=peer_stress_only（可选；禁抬 B20）
严格锁：周期/窗口票溢价≥100% 或 above_sell_watch → 禁止为贴价放松 NI3/PE；现价>卖点≠marked down
优质筛选：quality_screen_note=超额回报证据+共识舒适/难受点（缺则不得标 franchise/durable）
增长分解：growth_decomposition=g_sustainable+g_efficiency(耗尽时点)；禁历史CAGR/卖方/宏观利润直写 NI3
dare_to_look_wrong：仅正式到价路径；禁覆盖 above_sell_watch / 候补不执行
护城河来源：moat_source_tag=<intangible_pricing|switching_costs|network_effects|cost_advantage|efficient_scale_or_size|none_or_eroding>（与 economic_goodwill 同向；伪护城河禁令）
特殊情形/相对：special_situation_note 不抬点；relative_overvalued_trap=整组贵时相对尺禁开执行
估准交叉：price_implied_vc_note=现价隐含未来价值创造（拟试仓强制）；EBIT/EV 仅敏感性
四优闸：four_quality_gate=企业/生意/管理层/价格 全 pass 才可 promote/试仓（缺一不可）
Fisher优质闸：fisher_quality_gate=诚信披露/稀释/利润率难受点；增长跑道≠护城河；scuttlebutt不含卖方目标价
EPV分层：epv_reliability_note=资产→无增长盈利能力→特许增长（拟试仓强制）；无特许则增长不抬 Exit PE/B20
满价/剥夺感：full_price_discipline + proximity_deprival_trap（细则见卖侧/贴近带行）
升档触发（P1，quality_edge / B 档暂定存疑 / 纯回退存疑 / 事件闸时强制）：2–4 条 metric/threshold/lookback/effect；达成→upgrade_review_due=true（不自动改 B20）；禁止第二套熊倍买点字段
双向复核：证据达标可升退出倍数/清 edge；TA 永不抬 B20；不发明 digest 买点
## 论点与击穿码
## 复查触发
季报/年报时点、领先指标阈值、价格触及各档
## 数据缺口与保守处理
<gap id> · 影响 · 处理
免责声明：个人研究，非投资建议。
```

## 银行分支（PB–ROE · 总回报）
```
# <名称>（<代码>）决策卡 · <日期> · 现价 <p>
评级：… · hurdle 总回报 <h>%（y=<前瞻股息率>）· 复核轮次 …
industry_branch=bank
## 买卖点
| 口径 | A15 | A18 | B20 | B22 | C25 |
| 总回报（主，y=…） | … | … | … | … | … |
| 纯价格（并列） | … | … | … | … | … |
| 无倍数修复 min | — | — | … | … | — |
退出 PB 熊/基/牛；BPS₃；FV3；卖点（公允上限×150% 为主）
三年年化：价格路径 / **总回报**（展示）
回报拆解（§109，PB 口径）：BPS 增长 / PB 修复 / 股息；PB 不修复年化 <r_nr>%；PB 修复 ≥50% → 标「主要靠估值修复」并按 §109 控仓
## 仓位
熊市**总**回报 → 档；脆弱比；确信=暂定→试仓上限；现价 vs B20 动作
## 分批 / 技术可达性与执行 / 击穿 / 复查
同默认（含贴近带≤B20溢价5%整笔试仓、到价分批与暂缓）；银行击穿须含 NIM、零售/信用卡不良、CET1、评级被迫下调
## 披露
y 敏感性、权重法 CET1、复核 low 项
免责声明：个人研究，非投资建议。
```
