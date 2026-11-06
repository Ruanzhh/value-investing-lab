# 价值投资实验室

这里分享价值投资的思考与公司研究。每家公司只有一篇主报告，供读者审阅、复核和挑战：从生意机制、事实证据和盈利假设推导估值，并列出反方解释与判断更新条件。

研究由 AI 辅助完成。主报告后的 `evidence/` 存放来源、经营财务证据与实质性审阅异议，`valuation/` 存放假设、公式及计算材料。本次结构整理未重新核验财务事实，也不随行情自动更新；来源不足的地方在报告中明确标注。

## 怎么参与

- 读：从下表打开主报告，沿正文链接核对证据与计算。每项判断都可以针对事实、推理或参数提出异议。
- 提问和纠错：用 [Issue 表单](https://github.com/ruanzh6/value-investing-lab/issues/new/choose)。请写公司代码、引用的文件路径、证据链接。只问「该不该买 / 该不该卖」的 issue 不会受理。
- 改内容：走 pull request。不要在 PR 里夹带未披露的内部硬数、个人持仓或未审草稿。

## 十二家公司研究

研究日期均为 **2026-11-06**，各页另标明报告所用股价的日期或口径。现行价格口径与状态集中写在各公司主报告中；“约三年后合理价”不是今天的价值，“研究闸价”不是买卖指令。

| 公司 | 核心问题 | 主报告 | 复核材料 |
|---|---|---|---|
| 宁德时代（300750） | 增长之外，多少利润能留给股东 | [主报告](reports/300750-ningde-shidai/README.md) | [来源与附录](reports/300750-ningde-shidai/evidence/README.md) |
| 贵州茅台（600519） | 品牌优势与渠道承受力 | [主报告](reports/600519-guizhou-maotai/README.md) | [来源与附录](reports/600519-guizhou-maotai/evidence/README.md) |
| 美的集团（000333） | 扣非利润与现金揭示的经营压力 | [主报告](reports/000333-meidi-jituan/README.md) | [来源与附录](reports/000333-meidi-jituan/evidence/README.md) |
| 海尔智家（600690） | 低于研究闸价，仍需看清海外利润 | [主报告](reports/600690-haier-zhijia/README.md) | [来源与附录](reports/600690-haier-zhijia/evidence/README.md) |
| 分众传媒（002027） | 点位网络、租金与价格约束 | [主报告](reports/002027-fenzhong-chuanmei/README.md) | [来源与附录](reports/002027-fenzhong-chuanmei/evidence/README.md) |
| 迈瑞医疗（300760） | 现金质量与需求修复 | [主报告](reports/300760-mairui-yiliao/README.md) | [来源与附录](reports/300760-mairui-yiliao/evidence/README.md) |
| 东阿阿胶（000423） | 用回款验证增长 | [主报告](reports/000423-donge-ejiao/README.md) | [来源与附录](reports/000423-donge-ejiao/evidence/README.md) |
| 招商银行（600036） | 低成本存款与信用成本 | [主报告](reports/600036-zhaoshang-yinhang/README.md) | [来源与附录](reports/600036-zhaoshang-yinhang/evidence/README.md) |
| 海康威视（002415） | 高毛利、库存与现金回收 | [主报告](reports/002415-haikang-weishi/README.md) | [来源与附录](reports/002415-haikang-weishi/evidence/README.md) |
| 中国平安（601318） | 账面利润与可分配现金的距离 | [主报告](reports/601318-zhongguo-pingan/README.md) | [来源与附录](reports/601318-zhongguo-pingan/evidence/README.md) |
| 福耀玻璃（600660） | 制造优势与资本投入 | [主报告](reports/600660-fuyao-boli/README.md) | [来源与附录](reports/600660-fuyao-boli/evidence/README.md) |
| 古井贡酒（000596） | 去库存后费用能否降下来 | [主报告](reports/000596-gujing-gongjiu/README.md) | [来源与附录](reports/000596-gujing-gongjiu/evidence/README.md) |

## 一家公司怎样组织

```text
reports/<代码>-<公司拼音>/
├── README.md          主报告：判断、证据、假设、估值、反方与更新条件
├── evidence/
│   ├── README.md      来源索引、可核范围与材料缺口
│   ├── business.md    行业与生意机制
│   ├── financials.md  财务数据及口径
│   ├── risks.md       风险触发条件
│   ├── review.md      实质性历史审阅意见（有则保留）
│   └── raw/           已收录的原始文件（有则保留）
└── valuation/
    ├── README.md      假设、公式、敏感性与适用范围
    └── …              必要输入、输出和计算脚本（有则保留）
```

专题证据按需增加，不要求每家公司凑齐相同附件。不再并列维护摘要、结论卡和多份报告；旧版及过程记录可由 Git 历史追溯。附录里的历史审阅意见不等于对现行所有参数的独立认可。

## 目录

- `philosophy/` — 理念文章。首版只有骨架，正文待补。
- `reports/<代码-公司拼音>/` — 每家一篇主报告，必要证据与估值计算分目录存放。
- `skills/a-share-deep-valuation/` — 当前使用的深估技能。
- `AGENTS.md` — 给 agent 的阅读和改稿规则。
- `.github/` — Issue 表单和 pull request 模板。

## 声明

报告里的现价、合理价、闸价都是研究用数字，用来记录某次估值怎么算出来。它们不是买卖建议，也不表示买点已经启用。主报告若写明「不出正式合理价」「不设闸价」或「买点未启用」，就以该结论为准。

本仓库不提供交易服务，不代客下单。
