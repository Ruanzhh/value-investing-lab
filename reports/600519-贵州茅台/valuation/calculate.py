"""人民币亿元，股数以亿股计。运行 python calculate.py。"""
from datetime import date

SHARES = 12.50081601
PRICE = 1442.66
BUY_FEE, SELL_FEE = 0.00026, 0.00076
START = date(2026, 11, 18)
DATES = [date(y, m, d) for y, m, d in (
    (2026,12,24), (2027,6,25), (2027,12,24), (2028,6,25),
    (2028,12,24), (2029,6,25), (2029,11,18))]
TIMES = [(day - START).days / 365 for day in DATES]
OPEN_CASH = 499.27 + 1560.56 + 10 + 11.13 + 23.99 + 4.09 + 40.16 - 378.83 - 92.17 - 400
# 权重、综合销量增速、吨价增速、税后归母经营净利率、经营PE、增长资本开支、营运资本增量
SCENARIOS = {
    '需求受损': (.25, -.02, -.01, .44, 13, 10, 44),
    '正常但估值收缩': (.20, .02, .015, .47, 15, 20, 54),
    '温和恢复': (.40, .02, .015, .47, 20, 20, 54),
    '品牌溢价回升': (.15, .03, .03, .485, 24, 30, 65),
}

def project(params, opening=OPEN_CASH, later_payout=.75):
    weight, volume, unit_price, margin, pe, expansion, working = params
    revenue, prior, cash = 1715, 824, opening
    flows = []
    for year in range(3):
        revenue *= (1 + volume) * (1 + unit_price)
        operating = revenue * margin
        interest = cash * .01
        profit = operating + interest
        dividends = prior * (.75 if year == 0 else later_payout)
        flows.extend([dividends * fraction / SHARES for fraction in (.46, .54)])
        cash += operating + interest + 23 - 22 - expansion - working - dividends
        prior = profit
    equity = operating * pe + cash
    flows.append(equity / SHARES * (1 - SELL_FEE))
    return flows, (revenue, operating, profit, cash, equity)

def pv(flows, rate, times=TIMES):
    return sum(f / (1+rate)**t for f,t in zip(flows,times))

def irr(flows, price, times=TIMES):
    low, high = -.8, 2.
    for _ in range(90):
        mid = (low+high)/2
        if pv(flows,mid,times) > price*(1+BUY_FEE):
            low = mid
        else:
            high = mid
    return (low+high)/2

def main():
    assert abs(sum(s[0] for s in SCENARIOS.values())-1)<1e-12
    rows = [project(s) for s in SCENARIOS.values()]
    weights = [s[0] for s in SCENARIOS.values()]
    def weighted(items):
        return [sum(w*v for w,v in zip(weights,col)) for col in zip(*items)]
    flows = weighted([f for f,_ in rows])
    metrics = weighted([m for _,m in rows])
    buy, sell = pv(flows,.18)/(1+BUY_FEE), pv(flows,.04)/(1-SELL_FEE)
    print('weighted revenue, operating, profit, net cash, equity', metrics)
    print('weighted flows',flows,'buy/sell/mcaps/irr',buy,sell,buy*SHARES,sell*SHARES,irr(flows,PRICE))
    for name,(f,m) in zip(SCENARIOS,rows):
        print(name,m,'returns at market / buy',[(irr(f,p),sum(f)/(p*(1+BUY_FEE))-1) for p in (PRICE,buy)])
    print('delayed terminal only',irr(flows,PRICE,TIMES[:-1]+[TIMES[-1]+1]))
    for r in (0,.18):
        required = (PRICE*(1+BUY_FEE)-pv(flows[:-1],r))*(1+r)**TIMES[-1]*SHARES/(1-SELL_FEE)
        print('implied uniform PE',r,(required-metrics[3])/metrics[1])
    print('PE +1 change in buy',metrics[1]/SHARES*(1-SELL_FEE)/(1.18**TIMES[-1])/(1+BUY_FEE))
    stress_shift = [f+.1*(s-n) for f,s,n in zip(flows,rows[0][0],rows[2][0])]
    print('move 10pt to demand damage',pv(stress_shift,.18)/(1+BUY_FEE),irr(stress_shift,PRICE))
    print('cash buffer +200',pv(weighted([project(s,OPEN_CASH-200)[0] for s in SCENARIOS.values()]),.18)/(1+BUY_FEE))
    retained = weighted([project(s, later_payout=.60)[0] for s in SCENARIOS.values()])
    print('60% later payout',pv(retained,.18)/(1+BUY_FEE),irr(retained,PRICE))
    sell_per_turn = metrics[1] / SHARES / (1.04**TIMES[-1])
    print('sell per PE turn and turns to current price',sell_per_turn,(PRICE-sell)/sell_per_turn)

if __name__ == '__main__':
    main()
