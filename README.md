# 价值投资实验室

## English

This is a public notebook for a value-investing way of thinking and for AI-written equity research. It is built for people and for AI agents: anything in this repository may be read, and anyone may open an issue or send a pull request. Gate prices copied from the reports are research figures. They are not instructions to buy or sell.

## 这是什么

这里分享价值投资（value investing）的看法，以及 AI 写出的公司研究报告。仓库按 AI Agent 可直接阅读的方式组织：规则在 `AGENTS.md`，研报在 `reports/`，估值技能在 `skills/a-share-deep-valuation/`。

任何人、任何 agent 都可以读完全部公开内容，也可以开 issue 纠错、补充证伪信号、提议新公司，或用 pull request 改内容。

## 怎么参与

- 读：从下表进每家的摘要，再进研报原文。
- 提问和纠错：用 [Issue 表单](https://github.com/ruanzh6/value-investing-lab/issues/new/choose)。请写公司代码、引用的文件路径、证据链接。只问「该不该买 / 该不该卖」的 issue 不会受理。
- 改内容：走 pull request。不要在 PR 里夹带未披露的内部硬数、个人持仓或未审草稿。

## 十二家最新研报

数字以各目录 `decision_card.md` 为准，摘要页只照抄、不另算。

| 代码 | 公司 | 摘要 | 研报 |
|------|------|------|------|
| 300750 | 宁德时代 | [摘要](reports/300750-ningde-shidai/README.md) | [研报](reports/300750-ningde-shidai/research_report.md) |
| 600519 | 贵州茅台 | [摘要](reports/600519-guizhou-maotai/README.md) | [研报](reports/600519-guizhou-maotai/research_report.md) |
| 000333 | 美的集团 | [摘要](reports/000333-meidi-jituan/README.md) | [研报](reports/000333-meidi-jituan/research_report.md) |
| 600690 | 海尔智家 | [摘要](reports/600690-haier-zhijia/README.md) | [研报](reports/600690-haier-zhijia/research_report.md) |
| 002027 | 分众传媒 | [摘要](reports/002027-fenzhong-chuanmei/README.md) | [研报](reports/002027-fenzhong-chuanmei/research_report.md) |
| 300760 | 迈瑞医疗 | [摘要](reports/300760-mairui-yiliao/README.md) | [研报](reports/300760-mairui-yiliao/research_report.md) |
| 000423 | 东阿阿胶 | [摘要](reports/000423-donge-ejiao/README.md) | [研报](reports/000423-donge-ejiao/research_report.md) |
| 600036 | 招商银行 | [摘要](reports/600036-zhaoshang-yinhang/README.md) | [研报](reports/600036-zhaoshang-yinhang/research_report.md) |
| 002415 | 海康威视 | [摘要](reports/002415-haikang-weishi/README.md) | [研报](reports/002415-haikang-weishi/research_report.md) |
| 601318 | 中国平安 | [摘要](reports/601318-zhongguo-pingan/README.md) | [研报](reports/601318-zhongguo-pingan/research_report.md) |
| 600660 | 福耀玻璃 | [摘要](reports/600660-fuyao-boli/README.md) | [研报](reports/600660-fuyao-boli/research_report.md) |
| 000596 | 古井贡酒 | [摘要](reports/000596-gujing-gongjiu/README.md) | [研报](reports/000596-gujing-gongjiu/research_report.md) |

## 目录

- `philosophy/` — 理念文章。首版只有骨架，正文待补。
- `reports/<代码-公司拼音>/` — 每家一份摘要，加上该次研究的原件。
- `skills/a-share-deep-valuation/` — 当前使用的深估技能。
- `AGENTS.md` — 给 agent 的阅读和改稿规则。
- `.github/` — Issue 表单和 pull request 模板。

## 声明

报告里的现价、合理价、闸价都是研究用数字，用来记录某次估值怎么算出来。它们不是买卖建议，也不表示买点已经启用。结论卡若写明「不出正式合理价」「不设闸价」或「买点未启用」，就以结论卡为准。

本仓库不提供交易服务，不代客下单。
