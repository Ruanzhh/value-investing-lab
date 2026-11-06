# 外部交叉校验阶段（S4c）提案 — 仅提案，未改现行规则/卡片/看板

日期 2026-10-30（UTC+8）。现行规则 md5 5d691d8b… 未动。

## 1. 外部来源清单（2026-10-30 实测）
| 来源 | URL | 访问 | 提供 | 可靠性/注意 |
|---|---|---|---|---|
| Yahoo Finance 分析页 | finance.yahoo.com/quote/0700.HK/analysis/ | 免费，可抓 | 一致预期 EPS/收入 当年+次年、高低值、分析师数、90天修正趋势 | 只到 FY+1；IFRS/调整口径不明 |
| 东方财富研报中心 | data.eastmoney.com/report/stock.jshtml | 免费，200 | A股/港股研报列表、评级、盈利预测表（3年） | A股最全的免费一致预期代理；需脚本解析 |
| 同花顺 F10 盈利预测 | basic.10jqka.com.cn/HK0700/worth.html | 免费，200 | 机构 EPS 预测均值/分布 | 需解析 |
| 新浪/智通/中金在线 研报摘要 | finance.sina.com.cn 等 | 免费 | 单家券商目标价、方法、3年净利润 | 单篇，非一致预期；新闻转述 |
| 萝卜投研 | robo.datayes.com | 免费注册 | 一致预期、研报 | 需登录 |
| 慧博 | hibor.com.cn | 部分付费 | 研报全文 | 302 跳转，需账号 |
| 雪球 | xueqiu.com/S/00700 | 免费，200 | 个人估值帖（老唐等）、讨论 | 质量参差，只作定性/反方 |
| Damodaran 数据 | pages.stern.nyu.edu/~adamodar/.../ctryprem.html、pedata.html | 免费，200 | ERP（中国 5.14%、香港 5.01%，2026-01）、行业 PE/EV 倍数 | 高可靠，年更；适合锚定风险溢价与倍数 |
| Morningstar 公允价值/护城河 | morningstar.com | 403，需浏览器/订阅 | FV、moat、uncertainty | 可靠但未取得 |
| GuruFocus / Simply Wall St DCF | 两站 | 403 | 模板 DCF | 机械模板，可靠性低，仅参考 |
| Investing.com 一致预期 | investing.com | 403 | 一致预期 | 未取得 |
| 公司指引 | 腾讯 IR / 年报 / 巨潮 | 免费 | 资本开支、回购、分红指引 | 一手，最高优先 |

## 2. 腾讯实测对比（详见 tencent_external.json）
- 一致预期（Yahoo，32–33 家）：FY2026 EPS 28.8 元，FY2027 30.19 元（90天前 32.65，下修 7.5%）。
- 券商 3 年：国海 Non-IFRS 净利 2660/2754/2891 亿（FY26–28）；海通 FY26 2655 亿。
- 目标价（12个月，5家）：470（海通）/550（大摩，DCF-SOTP，≈16.4x FY27）/666（国海、中金）/755（花旗），中位 666。
- 我们 v3 r2：核心 NI3 基准 3020 亿（FY2029）；B20 390.56，隐含 FV3≈696 港元。
  - NI3 vs 国海 FY28 外推至 FY29（约 3036 亿）：差 <5%，在 ±15% 内。⚠ 父任务给的 2819 亿在 r2 文件中未找到，口径（核心 vs 含联营）需先对齐。
  - 估值倍数：大摩 16.4x 与我们核心 PE 15.55x 一致。
  - 分歧在折现门槛而非利润：卖方 12 个月目标 666 ≈ 我们 3 年 FV3；我们 B20 只有目标价中位的 0.59。
  - 预期下修趋势 + 文献的卖方乐观偏差 → 不支持上调 B20。
- 未取得：Morningstar FV、老唐等可核实原文 —— 未录入，未编造。

## 3. 接入 workflow-v3：新增 S4c「外部交叉校验」（位于 S4 硬校验之后、S5 买卖点之前）
锚点（新增 A.L1.EXT.*）：
- EXT.1 一致预期对照：NI3_base vs 同口径一致预期（FY3 缺失时按 FY+2 和一致预期增速外推，标注"外推"）。偏离 >±15% 必须写理由，否则 FAIL。
- EXT.2 乐观偏差折扣：一致预期按 3 年期先打 10% 折扣再比较（文献：卖方长期 EPS 系统性偏乐观；参数待回测，暂定）。
- EXT.3 外部公允价值对照：FV3 vs {卖方目标价中位按 1 年推到 FY3、Morningstar FV、Damodaran 行业倍数×NI3}。只展示、记录方向。
- EXT.4 多方法三角：至少 2 种独立方法（如 同年口径 PE、反向 DCF、DDM/PB-ROE、SOTP），任两者 FV3 差 >25% → 不出买点。
- EXT.5 区间买入规则：B20 在参数合理区间（脆弱性网格 + 方法间）取最小值；只要任一取值不到价即判"未到价"。
- EXT.6 护栏：外部数据只能下调或拦截，不能单独上调 B20（assert B20_after ≤ B20_before）；外部数据日期 ≤30 天、需 URL；单篇研报不算一致预期（n≥5）；修正趋势 90 天下修 >5% 时熊情景再压。
硬校验（scripts/validate 新增断言）：
- ext_sources[].url 非空且 fetched_at ≤30d
- abs(NI3/consensus_adj −1) ≤0.15 或 reason 非空
- methods ≥2 且 max/min ≤1.25
- B20_final == min(range) 且 B20_final ≤ B20_internal
- 口径字段 basis ∈ {non-IFRS, IFRS, 扣非} 两侧一致

## 4. 推进
1. 先对齐腾讯 NI3 口径（3020 vs 2819）。2. 写东财/同花顺抓取脚本，落到每卡 ext_sources。3. EXT.2 折扣、EXT.4 25% 阈值回测。4. 独立复核后再由用户批准安装。
