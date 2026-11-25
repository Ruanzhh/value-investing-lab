"""三一重工 A 股。金额为亿元人民币，股数为亿股，回报采用 ACT/365。"""
from dataclasses import dataclass, replace
from datetime import date

START = date(2026, 11, 24)
END = date(2029, 11, 23)
DATES = (date(2027, 7, 16), date(2028, 7, 17), date(2029, 7, 17), END)
ISSUED = 91.95004437
CURRENT = ISSUED - 0.42272113
PRICE = 18.28
BUY_FEE, SELL_FEE = .00026, .00076


@dataclass(frozen=True)
class State:
    name: str
    prob: float
    domestic_growth: float
    overseas_growth: float
    domestic_gm: float
    overseas_gm: float
    burden: float
    growth_capex: float
    working_capital: float
    unwind: tuple
    payout: float
    g: float
    roe: float
    k: float


normal = State('常态', .45, .04, .11, .211, .321, .162, .014, .20, (0, 0, 0), .45, .035, .14, .09)
states = (normal, replace(normal, name='常态压倍数', prob=.20, k=.115),
          State('下行', .20, -.04, .015, .18, .27, .174, .006, .22, (35, 15, 0), .25, .015, .09, .115),
          State('扩张兑现', .15, .075, .165, .22, .343, .156, .022, .23, (0, 0, 0), .50, .045, .16, .088))


def project(s):
    domestic, overseas = 365., 650.
    cash = 0.        # 估值日起新增的可归母闲置现金
    previous_profit = 98.    # 2026所属年预测，用于首次分配
    distributions, rows = [], []
    for year in range(1, 4):
        previous_sales = domestic + overseas
        domestic *= 1 + s.domestic_growth
        overseas *= 1 + s.overseas_growth
        sales = domestic + overseas
        # 地区毛利与成本负担由观察起点逐年过渡到正常状态
        w = year / 3
        domestic_gm = .207 + w * (s.domestic_gm - .207)
        overseas_gm = .325 + w * (s.overseas_gm - .325)
        burden = .170 + w * (s.burden - .170)
        profit = (domestic * domestic_gm + overseas * overseas_gm - sales * burden) * .85 * .99
        # 所列折旧、资本开支及营运占用为归母代理；租赁费用与实付近似相抵
        conversion = sales * (.030 - .026 - s.growth_capex)
        working = max(0, sales - previous_sales) * s.working_capital + s.unwind[year - 1]
        fcfe = profit + conversion - working
        dividend = previous_profit * s.payout
        cash = cash * 1.015 + fcfe - dividend
        distributions.append(dividend / ISSUED)
        rows.append((sales, profit, fcfe, dividend, cash))
        previous_profit = profit
    pe = (1 + s.g) * (1 - s.g / s.roe) / (s.k - s.g)
    value = profit * pe + cash
    return rows, pe, value, distributions + [value / ISSUED * (1 - SELL_FEE)]


def pv(flows, rate, dates=DATES):
    return sum(cf / (1 + rate) ** ((d - START).days / 365) for cf, d in zip(flows, dates, strict=True))


def irr(flows, price, dates=DATES):
    low, high = -.9, 2.
    outlay = price * (1 + BUY_FEE)
    assert pv(flows, low, dates) > outlay > pv(flows, high, dates)
    for _ in range(90):
        mid = (low + high) / 2
        if pv(flows, mid, dates) > outlay:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def expected(probs):
    assert abs(sum(probs) - 1) < 1e-10
    return [sum(p * project(s)[3][i] for p, s in zip(probs, states, strict=True)) for i in range(4)]


def main():
    flows = expected([s.prob for s in states])
    buy = pv(flows, .18) / (1 + BUY_FEE)
    sell = pv(flows, .04) / (1 - SELL_FEE)
    print('期望现金流（末笔扣卖费）', flows)
    for price in (PRICE, buy):
        for s in states:
            rows, pe, value, cf = project(s)
            print('买入价', round(price, 2), s.name, [tuple(round(x, 2) for x in row) for row in rows],
                  'PE/股权价值/IRR/累计', round(pe, 3), round(value, 2),
                  round(irr(cf, price), 5), round(sum(cf) / (price * (1 + BUY_FEE)) - 1, 5))
    income = sum(s.prob * project(s)[0][-1][1] for s in states)
    cash = sum(s.prob * project(s)[0][-1][-1] for s in states)
    value = sum(s.prob * project(s)[2] for s in states)
    print('期望盈利/留存现金/股权价值/每股终值', income, cash, value, value / ISSUED)
    print('买价/等价市值/卖价/等价市值/当前年化', buy, buy * CURRENT, sell, sell * CURRENT, irr(flows, PRICE))
    for rate in (0., .18):
        future = (PRICE * (1 + BUY_FEE) - pv(flows[:3], rate, DATES[:3])) * (1 + rate) ** ((END-START).days/365)
        required = future * ISSUED / (1 - SELL_FEE)
        print('现价反推', rate, '期末价值/统一PE/按经营有效倍数所需利润', required, (required-cash)/income,
              (required-cash) / ((value-cash)/income))
    print('延迟一年，无额外股息', [(p, irr(flows, p, DATES[:3] + (date(2030, 11, 22),))) for p in (PRICE,buy)])
    print('下行权重由常态挪入10点', pv(expected([.35, .20, .30, .15]), .18) / (1 + BUY_FEE))
    print('每一倍PE/50亿期末资产对买价影响', *[pv([0,0,0,x / ISSUED * (1-SELL_FEE)],.18)/(1+BUY_FEE) for x in (income,50)])
    no_cash = flows[:3] + [flows[3] - cash / ISSUED * (1 - SELL_FEE)]
    years = (END - START).days / 365
    cash_shortfall = (sell - PRICE) * ISSUED * 1.04 ** years
    print('卖出线触及现价的现金缺口/占比', cash_shortfall, cash_shortfall / cash)
    print('全部新增现金无法实现时买价/卖价',
          pv(no_cash, .18) / (1 + BUY_FEE), pv(no_cash, .04) / (1 - SELL_FEE))
    print('期末成交价低于内在值10%', irr(flows[:3] + [flows[3]*.9], PRICE))


if __name__ == '__main__':
    main()
