---
name: a-share-deep-valuation
description: >-
  A 股单只深度估值：默认走简约六步（收材料→看懂生意→基准情景→约三年基准合理价与买入闸价→独立挑刺→结论卡）。
  对人只报基准线，不分熊/基/牛三档；用投资透镜做分析/筛选/估值/置换对照；筛选三性含现金转化硬关；定价只走 PE 轨（无现金流定价轨）；不编造；材料不够仍可出研究结论，但不说买点已正式启用。完整关卡模式可选。银行正式闸价走 bank 分支。
---
# A 股深度估值（简约默认）

**默认读并执行：** [`references/SIMPLE-FLOW.md`](references/SIMPLE-FLOW.md) · 生意深读 [`references/BUSINESS-DEPTH.md`](references/BUSINESS-DEPTH.md) · 投资透镜 [`references/INVESTMENT-LENS.md`](references/INVESTMENT-LENS.md)  
**对照：** [`references/SIMPLE-vs-FULL.md`](references/SIMPLE-vs-FULL.md)  
**对人用语：** [`references/user-facing-glossary.md`](references/user-facing-glossary.md)  
**结论卡首屏：** [`references/card-template.md`](references/card-template.md) 人读层  

公式与门槛**数值**仍以 [`references/valuation-rules-v3.md`](references/valuation-rules-v3.md) 为准；本 skill **不改常数**，只规定默认怎么走。

---

## 投资透镜（每单必过心智，不改公式）

1. **分析企业**：被需要 · 很难被替代 · 价格不受管制；用波特五力与可证伪护城河解释超额净资产收益率。  
2. **筛选企业**：利润为真 · 利润可持续 · 维持盈利不需大量资本（**现金转化在此过关**）；看不懂不硬启用买点。  
3. **企业估值**：筛选过关后只走 PE 轨估约三年合理价，再留安全边际；估值本质是相对其他机会的比较。  
4. **股票置换**：预期收益率明显不如类现金或其他机会时考虑置换；技术面不抬买点。  

细则见 `INVESTMENT-LENS.md`；写法约束见 `BUSINESS-DEPTH.md` / `SIMPLE-FLOW.md`。

---

## 默认六步（对人进度只用这些标题）

1. 【收材料】现价、股本、财报；缺什么写清楚  
2. 【看懂生意】按 BUSINESS-DEPTH：先过生意质量三性 + **筛选三性（含现金转化硬关）**，再深读七块；筛选不过 / 现金转化不过 → 不得估正式合理价  
2b. 【驱动树深挖】按 [`references/DRILL-TREE.md`](references/DRILL-TREE.md)：建驱动树，敏感度排序后 DFS，按条件自停（影响<5% / 已核对 / 公开信息已尽），6 层仅作安全上限，每个节点有数值+出处+置信度  
3. 【经营情景】只做基准（中性最可能）；不对人报熊/牛档  
4. 【合理价与闸价】**只走利润（PE）轨**：约三年基准净利 × 退出市盈率 → 合理价 + 闸价草稿；退出倍数主报约 **20～30** 视生意判断（历史中位仅参照）；无第二条定价轨；不够则**买点未正式启用**，仍出研究卡  
5. 【独立挑刺】必须由未参与估值的另一个助手做，出 review_report；自查不算；问题回流到驱动树节点（DRILL-TREE §5）  
5a. 【进展账本】每轮记 iteration_ledger；连续两轮无进展判停滞交用户（DRILL-TREE §6）。drill_tree 为数字唯一来源（§7）  
5b. 【数字核对关卡】关键数字对年报原文或第二来源；闸价一次变动>15%、或粗对照（如股权盈利收益率、无风险收益倒数）与主路径差>1.25 倍 → 须解释或**退回筛选三性**  
6. 【结论卡】人读层六项（结论 / 基准合理价 / 闸价 / 到价否 / 动作 / 最大风险）
7. 【研报验收】按 [`references/REPORT-GATE.md`](references/REPORT-GATE.md) 写完整研报；写不满的章节退回补调研，研报通过才算深估完成  

产物目录建议：`<代码>_simple_<YYYYMMDD>/`

### 核心思想
不编造 · 中性基准 · 先估约三年合理价 · 买入留安全边际 · 风险只扣一次 · 技术面不抬买点 · 尽量独立挑刺 · 筛选三前提（含现金转化） · 只走 PE 轨 · 退出PE约20–30判断取值 · 估值是比较  

### 术语关卡怎么用
完整模式里那些长检查清单与英文字段：**不挡**研究结论卡；**只影响**能否写「买点已正式启用」。缺材料或交叉未齐 → 人读层写「买点未启用」+ 原因，继续给基准合理价。平时不要把那些代号当日常用语。

---

## 完整模式（可选）

仅当用户明确要求「完整关卡 / 正式签发买点 / 银行分支全套」时启用：

- 状态机：`workflow.yaml` + `python3 scripts/workflow_runtime.py open|commit|inspect`
- 主规则细文：`references/valuation-rules-v3.md`、`references/v3/SKILL-master.md`
- 需要时再跑校验脚本（完整模式说明里有命令）
- 银行：另载 `bank-gates.md` / `bank-valuation-rules.md`
- Legacy 只读：`valuation-rules-v25.md`；备份目录 `a-share-deep-valuation.bak-v25-20261031`

完整模式执行协议（摘要）：主 Agent 唯一 commit；独立复核不可代审；材料不足则买点不启用；外部交叉永不抬买入闸价；不要先折现一遍再叠一层回报门槛（避免双重打折）。

---

## 硬约束（两种模式共用）
- 不编造基本面；缺项登记并说明保守处理  
- 不改用户已拍板保留的门槛常数  
- 不执行交易；输出仅个人研究  
- 对人沟通禁止堆英文字段当主句  

用例教训：`references/refinement-notes.md`。切换记录 `workflow-v3/CUTOVER_20261031.md` 未随本仓发布。

