<div align="center">

# 价值投资实验室

**一家公司，一篇主报告，一套可以被挑战的判断。**

[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg?style=flat-square)](LICENSE)
![AI-Powered](https://img.shields.io/badge/AI_Workflow-Trae-4a5568.svg?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active_Research-3182ce.svg?style=flat-square)

这是一个由 AI 辅助、开源共建的价值投资研究项目。<br>
我们致力于用公开信息理解企业，将经营判断推导为盈利、现金与价值。<br>
在这里，事实有出处，假设可质疑，结论能复算。

[**我们的理念 ↓**](#研究理念一份判断三层依据)　 /　 [**阅读报告 ↓**](#公司研究)　 /　 [**发起研究 ↓**](#人机协作工作流)　 /　 [**提出挑战 ↗**](https://github.com/Ruanzhh/value-investing-lab/issues/new/choose)

</div>

---

## 研究理念：一份判断，三层依据

本项目的核心动机在于构建一个**高度透明、逻辑严密且可被证伪**的研究环境。我们摒弃玄学与跟风，通过以下三个层次，构建对一家公司的完整认知：

- **01 · 看懂生意**
  谁付钱，为什么选它？优势能持续多久，增长需要多少投入？
- **02 · 算清价值**
  利润能否成为股东现金？从经营假设推导未来价值与买入条件。
- **03 · 接受挑战**
  最强反方解释是什么？哪些证据出现后，必须改变判断？

> **方法与基建**：[`value-investing`](skills/value-investing/SKILL.md) 维护投资理念与[量化原则](skills/value-investing/references/quantitative-principles.md)；[`deep-valuation`](skills/deep-valuation/SKILL.md) 指导取证、挑战与报告产出；[`portfolio-decision`](skills/portfolio-decision/SKILL.md) 根据已有研究、个人持仓与可投资现金形成组合建议。

## 公司研究

**按三年预测、18%目标年化反推，金额均为人民币，采用报告中的税费假设。** 点击公司查看完整判断、证据与计算。

| 公司 · A股代码 | 合理买入市值（亿元） | 对应A股股价（元/股） | 研究日期 |
| :--- | ---: | ---: | :--- |
| [**宁德时代 · 300750**](reports/300750-宁德时代/README.md) | 约10,945 | 约239.01 | 2026-11-07 |
| [**古井贡酒 · 000596**](reports/000596-古井贡酒/README.md) | 440.98 | 83.42 | 2026-11-07 |

<sub>市值为对应A股价格乘全部普通股股数的等价市值，不是A/H或A/B分别报价后的实际总市值。数字沿用研究日测算，不随行情或日期自动更新；达到该价格不等于可以直接买入。</sub>

## 人机协作工作流

本实验室采用人机协作模式。你可以通过具备本地代码读取能力的 AI Agent（如 Trae / Cursor），发送以下指令来启动对新公司的自动化分析：

```text
按照 deep-valuation skill 的准则完成对「公司名」的评估，需要保证 value-investing skill 中的准则都已经深刻执行，且市场公开信息已充分利用。
```

已有研究后，可在私人会话中分析组合：

```text
使用 portfolio-decision skill，根据已有研究和最新行情，分析我提供的持仓与可投资现金，给出买入、持有或换仓方案，并说明调整后的仓位和剩余现金。
```

该技能每次开始分析时提示适用前提与风险，不执行交易。持仓、资金及私人方案不要提交到本仓库或公开 Issue。

<details>
<summary><strong>查看目录结构与极简管理原则</strong></summary>

研究结果将保存在 `reports/<代码>-<中文公司名>/` 目录下，保持极简的结构：

```text
reports/<代码>-<中文公司名>/
├── README.md          唯一主报告：判断、推导、反方与更新条件
├── evidence/
│   ├── README.md      来源索引、证据与缺口
│   └── raw/           实际取得的原始材料
└── valuation/
    ├── README.md      假设、公式、敏感性与适用范围
    └── …              必要输入、计算脚本和结果
```

**内容管理原则：**
- **围绕问题，按需生长**：正文围绕公司的关键问题组织，不强制套用固定模板。附件和专题计算按需添加，仅在获取到真实原件时才创建对应文件，拒绝无效的“空白占位”。
- **事实与推导分离**：事实、计算和预测分开呈现，正文给出一个概率加权主预测，而详尽的假设、情景和敏感性分析则归入附录。
- **历史交由版本控制**：历史版本和旧稿交由 Git 妥善保存，不再并列维护结论卡或多份冗余副本。

</details>

## 欢迎探讨与纠错

在价值投资中，证伪比证实更重要。数据偏差、假设漏洞，或是出现了足以推翻判断的新证据，都是推动研究深化的宝贵契机。

**[提交 Issue →](https://github.com/Ruanzhh/value-investing-lab/issues/new/choose)** 
请附上公司代码、仓库内文件路径和可复核的证据链接。我们期待讨论聚焦于事实、口径、计算与证伪条件；关于短期买卖操作的咨询，暂不在本实验室讨论范围内。

如果你希望直接改进内容，欢迎提交 Pull Request，并在说明中写明修改对象及证据。请确保不包含未披露的内部数据、个人持仓、密钥或未经审阅的草稿。（完整贡献指南见 [AGENTS.md](AGENTS.md)）

---

**研究边界**：研究由 AI 辅助完成，来源不足和未解问题会在报告中如实披露。报告中的现价、合理价与买入点均为理论推演，绝非买卖指令。本仓库不提供交易服务，亦不代客下单。

<div align="center">

[更新记录](CHANGELOG.md)　 ·　 [理念文章 · 待补](philosophy/README.md)　 ·　 [MIT License](LICENSE)

<sub>保持好奇，尊重事实，允许自己改变判断。</sub>

</div>
