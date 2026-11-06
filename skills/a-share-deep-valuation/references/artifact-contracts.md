# Artifact 契约细则
字段名以 workflow.yaml 为准；本文件只补充格式与事实所有权。存储：`<ticker>_v25/`，结构化产物用 JSON，叙述用 Markdown。

## 事实所有权
| 事实 | 唯一 owner | 其他产物只能引用 |
|---|---|---|
| 来源、现价、股本、数据缺口 | source_index | 用 source_id / gap_id 引用 |
| 模块结论、闸门、老唐三前提、论点、击穿码、开放问题 | enterprise_analysis | |
| 经营驱动、NI3、超额净现金、情景概率 | scenario_model | |
| 风险归属 | risk_register | |
| 评级、hurdle、退出 PE、FV3、买/卖点、仓位档、脆弱性 | valuation_decision | |
| 复核 issue | review_report | |
| decision_card | 投影，不是事实源 | 发现新事实须回写 owner |

## source_index
```json
{"sources":[{"id":"AR2025","type":"annual_report","path":"pdf/...","pages":"p192"}],
 "price_snapshot":{"price":0,"date":"YYYY-MM-DD","source":"..."},
 "share_count":{"value":0,"unit":"亿股","source":"AR2025 p192"},
 "data_gaps":[{"id":"G1","item":"互动易问答","affects":["D3"],"conservative_handling":"不使用正面管理层表述；不确定性登记入 risk_register"}]}
```
证据分级：有依据 / 推导 / 经验值 / 待验证（同框架 §0）。

## review_report
```json
{"subagent_id":"...","round":1,"issues":[{"id":"R1","category":"assumption_bias|double_conservatism|provenance|depth_gate|formula","severity":"high|medium|low","evidence":"...","route":"deep_analysis|scenarios_risk|valuation_buy_sell"}],"verdict":"pass|revise"}
```
每轮追加，不覆盖历史。low 级 issue 只记录，不回流。

## 示例
CATL 材料可作格式参考（尚未经本 workflow 运行）：`（内部文稿未发布）`、`catl_deep_v22_FINAL.md`、`p7_v24_rules.json`、`reaudit_v25.md`。
