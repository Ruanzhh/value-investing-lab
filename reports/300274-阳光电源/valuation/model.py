"""阳光电源普通股，金额亿元、股数亿股、单价元。仅使用 Python 标准库。"""
from dataclasses import dataclass, replace
from datetime import date

START = date(2026, 11, 24)
END = date(2029, 11, 24)
SPOT = 73.62
REGISTERED = 20.73211424
OUT = REGISTERED - 0.17637543
BUY_FEE, SELL_FEE = 0.00021, 0.00071
TIMES = [date(y, m, d) for y in range(2027, 2030) for m, d in [(5, 20), (9, 20)]]
PARENT = 494.445692 / 524.566393
# 只留可从营业中抽走的余额。认缴基金按成本置换现金，未计超额回报。
OPERATING_CASH = 3.5 * 551.940716 / 9
OPENING_POOL = (266.233792 + 45.281323 - OPERATING_CASH
                 - 8.943208 - 0.7927 + 24.230214 * 0.70)
START_ASSETS = OPENING_POOL * PARENT - 1.7504


@dataclass(frozen=True)
class State:
    name: str
    weight: float
    gwh: float
    asp: float
    storage_margin: float
    inverter: float
    inverter_margin: float
    other: float
    other_margin: float
    costs: float
    capex: float
    working: float
    pe: float


NORMAL = State("部分恢复", .45, 105, .58, .29, 315, .365, 125, .16, .145, .036, .34, 15)
GROWTH = State("高质量放量", .10, 140, .61, .335, 365, .385, 145, .18, .133, .043, .34, 19)
STATES = [
    NORMAL,
    replace(NORMAL, name="经营恢复但倍数收缩", weight=.15, pe=10),
    State("成本和准入持续承压", .25, 76, .53, .22, 250, .33, 95, .12, .156, .030, .40, 10),
    GROWTH,
    replace(GROWTH, name="放量但倍数收缩", weight=.05, pe=12),
]
# 研究日滚动基数近似。时间步长为每年11月24日到下一年同日。
SEED_SALES, SEED_PROFIT = 745, 82


def path(s, margin_change=0.0, equity_share=PARENT):
    storage = s.gwh * s.asp * 10
    revenue = storage + s.inverter + s.other
    gross = storage * (s.storage_margin + margin_change) + s.inverter * s.inverter_margin + s.other * s.other_margin
    # 费用含销售、管理、研发、正常融资净成本及税金；减值净额另计。
    profit = (gross - revenue * (s.costs + .012)) * (1 - .18) * .99
    assets = OPENING_POOL * equity_share - 1.7504
    previous_revenue = SEED_SALES
    previous_profit = SEED_PROFIT
    distributions, audit = [], []
    for index, progress in enumerate((.30, .66, 1.0)):
        sales = SEED_SALES + progress * (revenue - SEED_SALES)
        earnings = SEED_PROFIT + progress * (profit - SEED_PROFIT)
        cash = earnings + equity_share * (sales * (.013 - s.capex) -
                                         (s.working + OPERATING_CASH / SEED_SALES) * max(0, sales - previous_revenue))
        final_prior = (max(0, SEED_PROFIT * .25 - 13.1679) if index == 0
                       else previous_profit * .55 * .25)
        interim = earnings * .45 * .25
        shares = OUT + (index + 1) / 3 * (REGISTERED - OUT)
        distributions.extend([final_prior / shares, interim / shares])
        assets += cash - final_prior - interim
        audit.append((sales, earnings, cash, assets))
        previous_profit, previous_revenue = earnings, sales
    terminal = profit * s.pe + assets
    return profit, terminal, distributions, audit


def years(d):
    return (d - START).days / 365


def pv(rate, divs, terminal_price, end=END):
    return (sum(c / (1 + rate)**years(d) for c, d in zip(divs, TIMES))
            + terminal_price * (1 - SELL_FEE) / (1 + rate)**years(end))


def irr(price, divs, end_price, end=END):
    lo, hi = -.90, 2.
    for _ in range(100):
        mid = (lo + hi) / 2
        if pv(mid, divs, end_price, end) > price * (1 + BUY_FEE):
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def weighted(states=STATES, margin_change=0.0):
    assert abs(sum(s.weight for s in states) - 1) < 1e-9
    rows = [path(s, margin_change) for s in states]
    return (sum(s.weight * r[0] for s, r in zip(states, rows)),
            sum(s.weight * r[1] for s, r in zip(states, rows)),
            [sum(s.weight * r[2][i] for s, r in zip(states, rows)) for i in range(6)])


def summary(states=STATES, margin_change=0.0):
    profit, value, divs = weighted(states, margin_change)
    quote = value / REGISTERED
    buy = pv(.18, divs, quote) / (1 + BUY_FEE)
    sell = pv(.04, divs, quote) / (1 - SELL_FEE)
    return profit, value, quote, buy, sell, irr(SPOT, divs, quote)


def show():
    e, v, d = weighted()
    p, value, end, buy, sell, rate = summary()
    print(f"期望盈利 {p:.3f} 期末价值 {value:.3f} 元/股 {end:.3f} 年化 {rate:.4%}")
    print(f"买价 {buy:.4f} 卖价 {sell:.4f} 等价市值 {buy*OUT:.3f} / {sell*OUT:.3f}")
    print("期初独立资产", round(START_ASSETS, 3), "六笔股息", [round(x, 4) for x in d])
    for s in STATES:
        profit, terminal, divs, audit = path(s)
        quote = terminal / REGISTERED
        results = []
        for price in (SPOT, buy):
            total = (quote * (1 - SELL_FEE) + sum(divs)) / (price * (1 + BUY_FEE)) - 1
            results.append((round(irr(price, divs, quote)*100, 2), round(total*100, 2)))
        print(s.name, round(profit, 3), round(terminal, 3), round(quote, 3), results,
              "收入/盈利/归母现金/独立资产", [[round(x, 2) for x in a] for a in audit])
    assets = sum(s.weight * path(s)[3][-1][-1] for s in STATES)
    for target in (0, .18):
        required = ((SPOT*(1+BUY_FEE) - pv(target, d, 0)) * (1+target)**years(END)
                    / (1-SELL_FEE) * REGISTERED)
        print("现价所需价值/有效PE/15倍所需盈利", target, required, (required-assets)/e, (required-assets)/15)
    for delta in (-.05, .05):
        print("储能毛利率变动", delta, summary(margin_change=delta))
    stress = [replace(s, weight=w) for s, w in zip(STATES, (.35, .15, .35, .10, .05))]
    print("10个百分点正常转承压", summary(stress))
    for price in (SPOT, buy):
        print("延后一年", price, irr(price, d, end, date(2030, 11, 24)),
              (end*(1-SELL_FEE)+sum(d))/(price*(1+BUY_FEE))-1)
    for cost in (10, 40):
        print("独立资产少", cost, pv(.18,d,(v-cost)/REGISTERED)/(1+BUY_FEE))
    for share in (.85, 1.0):
        stressed = sum(s.weight * path(s, equity_share=share)[1] for s in STATES)
        print("归属比例/期末价值/买价", share, stressed,
              pv(.18, d, stressed / REGISTERED) / (1 + BUY_FEE))
    print("期望期末独立资产", assets)


if __name__ == "__main__":
    show()
