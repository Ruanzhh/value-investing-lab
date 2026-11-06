# 独立复核模板 v3（S6）· 草案
复核员必须是独立 subagent，由**主 Agent** 启动（执行器只写 `review_request.json` 并以 blocked 交回）；主 Agent 不得代审。输出 review.json：`{independent:true, author_id, reviewer_id(≠author_id), verdict, rounds, premortem, anchor_checklist[], devil_advocate, required_changes[{id,anchor,change,resolved}]}`。同代理自查只能 `independent:false, verdict:PENDING`。
必查（r2）：快照表输入卫生（未复权价/年末股本/年末 FX）、FY3 与 n、熊倍数=最低快照、熊利润率地板与豁免理由、SBC 口径、凡使 B20 上调或使状态变到价的口径改动逐条列出并单独裁决。
必查（r3）：RC1 低谷年是否已从基/牛剔除且仍留在快照；RC2 熊景是否含该低谷地板；RC3 `round_delta.listed_changes`（B20 上调>5% 暂定或到价翻转）；RC4 公式用 n；RC5 无 SBC 单边扣；S4c 外部交叉（URL/日期/同口径/≥2 方法/B20_final≤internal/min(range)）；区间买入与 DISPLAY/GATE 分栏。

## A. 事前验尸（R8，A.L1.review.premortem）
1. 假设三年后该笔投资亏 30%。列 3 个最可能原因（具体到驱动/锚点 id）。
2. 逐条检查：熊景是否已覆盖？未覆盖 → 要求改熊景或写书面理由。
3. 是否存在「改模式/改口径让买点变近」的激励？新旧模式 B20 差 >15% 必须单列结论（V§16-3）。

## B. 逐锚点核对（每行：锚点 id · 卡值 · 一手出处 · 复算值 · 通过/不通过 · 备注）
- L1：profit_base（核心口径、9M+Q4、应计、F-score、套保上限）· exit_date_convention · exit_multiple.basis（同财年）· scenario 顺序 · bear_stress（≤历史最差/≤基率中位）· hurdle 档 · dividend_tr（DPS_min3 年份、叠息口径与 live 一致）· fragility · excess_cash（不与股息/投资组合双计）· return_sell 读数 · caps/cluster
- L2：business_model 与路由一致；方法与子流程一致（method_mismatch=false）
- L3：子流程参数锚逐个（例：M5 roe_take_lower、bvps_basis、erp 子型；M8 core_pe_basis、no_double_count；M3 hedge_strip、peer_margin；M4 cycle_window、path_tag；M6 pos_table）
- L4：该名每个个股锚点：来源、依据、失效条件是否写全；是否越权推翻上层

## C. 偏差检查（旧 V2.5 学习节压缩）
Disconfirming line · 共识已定价什么/我与共识差在哪/若共识对了现价是否仍贵 · Lollapalooza · 激励偏差 · 社会认同 · 相对便宜不得开执行。

## D. 展示项（不作门控，除非用户升格）
R4 基础比率位置 · R5 g/RONIC · R6 反向 DCF。

## A3. 轮次间买点变动（RC3，A.L1.review.gaming）
若相对上一版 B20 上调超过 `b20_up_disclose_pct`（**暂定 5%，PROVISIONAL_UNBACKTESTED**），或「到价」状态翻转：必须逐条列出 `round_delta.listed_changes[]`（change / direction / b20_contribution / author_reason），并单独裁决是否在凑结果。缺省 → FAIL。

## A4. S4c / 稳定性
确认 `external_crosscheck` 已跑；外部只压不抬；`methods[]`≥2；B20=min(range)；到价仅当整个区间到价；DISPLAY 项未写入执行理由。

## E. 结论
verdict ∈ {PASS, PASS_WITH_CHANGES, FAIL}；required_changes 每条带锚点 id。≤3 轮，超出交用户裁决。
