"""人民币、亿元、亿股。以实际天数/365折现，打印报告的研究结果。"""
from datetime import date

START = date(2026, 11, 18)
END = date(2029, 11, 18)
SHARES = 91.64871550
QUOTE = 35.29
BUY_FEE, SELL_FEE = 0.00026, 0.00076
# 路径、权重、期末收入、归母经营净利率、PE、独立净资产、三次年度现金分配总额/股
PATHS = [
    ("受损", .20, 1050, .14, 11, 40, (1.15, 1.05, 1.00)),
    ("压缩", .20, 1225, .17, 13, 80, (1.35, 1.45, 1.55)),
    ("常态", .45, 1225, .17, 17, 80, (1.35, 1.45, 1.55)),
    ("上行", .15, 1400, .185, 21, 100, (1.40, 1.65, 1.85)),
]
DATES = [date(y,m,d) for y in (2027,2028,2029) for m,d in ((5,20),(8,19))] + [END]
TIMES = [(d - START).days / 365 for d in DATES]


def pv(flows, rate, times=TIMES):
    return sum(cf / (1 + rate) ** t for cf, t in zip(flows, times))


def irr(price, flows, times=TIMES):
    low, high = -.95, 2.
    for _ in range(100):
        mid = (low + high) / 2
        if pv(flows, mid, times) > price * (1 + BUY_FEE):
            low = mid
        else:
            high = mid
    return (low + high) / 2


def calculate():
    expected = [0.] * 7
    profit = value = 0.
    scenarios = {}
    for name, w, sales, margin, pe, extra, divs in PATHS:
        income = sales * margin
        equity = income * pe + extra
        flows = [d * part for d in divs for part in (.60, .40)]
        flows.append(equity / SHARES * (1 - SELL_FEE))
        expected = [a + w*b for a, b in zip(expected, flows)]
        profit += w * income
        value += w * equity
        scenarios[name] = flows
    buy = pv(expected, .18) / (1 + BUY_FEE)
    sell = pv(expected, .04) / (1 - SELL_FEE)
    print("期望盈利、价值、期末每股、分配与期末净款",profit,value,value/SHARES,expected)
    print("行情市值、买卖门槛及市值、行情IRR",QUOTE*SHARES,buy,buy*SHARES,sell,sell*SHARES,irr(QUOTE,expected))
    for p in (QUOTE, buy):
        for name, flows in scenarios.items():
            print(p,name,irr(p,flows),sum(flows)/(p*(1+BUY_FEE))-1)
        for r in (0.,.18):
            terminal = (p*(1+BUY_FEE)-pv(expected[:-1],r))*(1+r)**TIMES[-1]/(1-SELL_FEE)
            print("反推：价格、要求、期末价、常态利润及80亿净资产对应PE",p,r,terminal,(terminal*SHARES-80)/(1225*.17))
        late = TIMES[:-1] + [(date(2030,11,18)-START).days/365]
        print("延迟一年无新增派息",p,irr(p,expected,late))
    delta= [a+.10*(b-c) for a,b,c in zip(expected,scenarios["受损"],scenarios["常态"])]
    print("常态转10个百分点至受损",pv(delta,.18)/(1+BUY_FEE),irr(QUOTE,delta))
    assert abs(sum(p[1] for p in PATHS)-1) < 1e-10
    assert abs(irr(buy, expected)-.18) < 1e-10


if __name__ == "__main__":
    calculate()
