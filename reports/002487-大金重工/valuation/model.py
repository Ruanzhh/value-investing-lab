"""大金重工。收入、盈利、现金单位亿元，数量万吨，单价万元/吨，股本亿股。"""
from datetime import date
from math import isclose

START = date(2026, 11, 24)
END = date(2029, 11, 23)
PAY = [date.fromisoformat(d) for d in ("2027-06-25", "2027-09-22", "2028-06-23",
                                      "2028-09-22", "2029-06-25", "2029-09-21")]
SHARES = 7.40085849
QUOTE = 25.64
BUY_FEE, SELL_FEE = .00031, .00081
# 经营现值与期末净现金同口径。H股历史股息已除权，留在9月末现金中的应付部分扣除。
LIQUID = 70.8648310072 + 17.0348072529 - .089425443
ADVANCES = 31.5461696381
STUB_FCF = -3.0

# 每行预测自研究日起连续12个月（末期止于最后一个周五）。
# 海工量/全口径价/毛利率，塔筒及其他收入/毛利率，对外造船收入/毛利率，
# 电站收入/毛利率，税金期间费用及净融资成本（剔除闲置现金利息），
# 非租赁折摊、维持开支、增长开支、经营营运资金净增加（不含现金储备）。
OPERATIONS = {
    "受阻": [
        (15,2.30,.30,18,.15,5,.05,3.7,.51,8.9,3.4,2.8,20,2),
        (12,2.20,.26,17,.14,17,.06,4.5,.50,9.3,4.2,3.1,15,2),
        (13,2.20,.25,16,.14,25,.08,5.5,.50,9.7,4.8,3.4,9,1.5)],
    "续单": [
        (18,2.45,.34,20,.17,6,.08,4,.55,9.4,3.6,2.9,23,2),
        (21,2.45,.33,19,.17,21,.11,5.5,.55,10.5,4.8,3.4,21,3),
        (26,2.45,.32,19,.17,35,.13,6.5,.55,11.5,5.4,3.9,12,2.5)],
    "放量": [
        (21,2.55,.35,21,.18,7,.10,4,.57,9.8,3.8,3.1,25,2.5),
        (29,2.60,.35,21,.18,29,.15,6,.57,12.0,5.2,3.8,25,4),
        (38,2.60,.35,22,.18,48,.16,7.5,.57,14.3,6.3,4.5,17,4)],
}
PATHS = [
    ("受阻", "订单与估值受损", .25, 8),
    ("续单", "正常、倍数压缩", .20, 9),
    ("续单", "正常、稳定定价", .40, 13),
    ("放量", "放量、溢价有限", .05, 11),
    ("放量", "放量、优势延续", .10, 16),
]


def project(state, pe, asp_factor=1.):
    liquid = LIQUID + STUB_FCF
    annual = []
    for qty, asp, margin, towers, tm, ships, sm, power, pm, expense, da, maintain, growth, wc in OPERATIONS[state]:
        asp *= asp_factor
        revenue = qty * asp + towers + ships + power
        gross = qty * asp * margin + towers * tm + ships * sm + power * pm
        earnings = (gross - expense) * .85
        fcfe = earnings + da - maintain - growth - wc
        distribution = max(earnings, 0) * .10
        liquid += fcfe - distribution
        reserve = (revenue - gross + expense - da) / 6
        excess = liquid - ADVANCES - reserve
        annual.append(dict(revenue=revenue, earnings=earnings, fcfe=fcfe, gross=gross,
                           payout=distribution, reserve=reserve, liquid=liquid, excess=excess))
    value = earnings * pe + excess
    divs = [row["payout"] / SHARES / 2 for row in annual for _ in range(2)]
    return annual, value, divs


def years(d):
    return (d - START).days / 365


def pv(rate, divs, terminal, *, end=END, div_tax=(0,) * 6, exit_fee=SELL_FEE):
    return sum(d * (1 - tax) / (1 + rate)**years(t) for d, tax, t in zip(divs, div_tax, PAY)) + terminal * (1 - exit_fee) / (1 + rate)**years(end)


def irr(price, divs, terminal, entry_fee=BUY_FEE, **kwargs):
    low, high = -.99, 4
    for _ in range(100):
        mid = (low + high) / 2
        if pv(mid, divs, terminal, **kwargs) > price * (1 + entry_fee):
            low = mid
        else:
            high = mid
    return (low + high) / 2


def main():
    weighted = [0.] * 6
    avg = [0.] * 3
    value = cash = 0.
    results = []
    assert isclose(sum(p for _, _, p, _ in PATHS), 1)
    for state, label, weight, pe in PATHS:
        annual, v, divs = project(state, pe)
        value += weight * v
        cash += weight * annual[-1]["excess"]
        for i, row in enumerate(annual):
            avg[i] += weight * row["earnings"]
        for i, d in enumerate(divs):
            weighted[i] += weight * d
        results.append((label, divs, v))
        print(label, pe, [(round(x["earnings"],2), round(x["fcfe"],2), round(x["excess"],2)) for x in annual], round(v,2))
    terminal = value / SHARES
    buy = pv(.18, weighted, terminal) / (1 + BUY_FEE)
    sell = pv(.04, weighted, terminal) / (1 - SELL_FEE)
    print("归母经营利润、期末股权、额外现金、每股期末、期间股息", avg, value, cash, terminal, weighted)
    print("买卖价格、市值、现价IRR", buy, sell, buy*SHARES, sell*SHARES, irr(QUOTE, weighted, terminal))
    for label, divs, v in results:
        for price in (QUOTE, buy):
            print(label, round(price,2), "IRR、累计", irr(price,divs,v/SHARES), pv(0,divs,v/SHARES)/(price*(1+BUY_FEE))-1)
    for r in (0, .18):
        need = (QUOTE*(1+BUY_FEE)-pv(r,weighted,0))*(1+r)**years(END)/(1-SELL_FEE)*SHARES
        print("反推回报、所需股权、按13倍所需盈利",r,need,(need-cash)/13)
    print("延迟一年", irr(QUOTE,weighted,terminal,end=date(2030,11,22)), irr(buy,weighted,terminal,end=date(2030,11,22)))
    print("时点与口径敏感性（买入价改变额）")
    for label, change in (("期末现金少10亿",-10),("所有经营状态PE少2倍",-2*avg[-1]),("稳定定价转10个百分点至受阻",.10*(results[0][2]-results[2][2]))):
        dividends = weighted
        if label.startswith("稳定"):
            dividends = [d+.10*(a-b) for d,a,b in zip(weighted,results[0][1],results[2][1])]
        print(label, pv(.18,dividends,terminal+change/SHARES)/(1+BUY_FEE)-buy)
    for factor in (.9, 1.1):
        stressed_divs = [0.] * 6
        stressed_value = 0.
        for state, _, weight, pe in PATHS:
            _, v, divs = project(state, pe, factor)
            stressed_value += weight * v
            stressed_divs = [total+weight*d for total, d in zip(stressed_divs, divs)]
        term = stressed_value / SHARES
        print("海工实现价系数、买卖价、IRR", factor,
              pv(.18, stressed_divs, term)/(1+BUY_FEE), pv(.04, stressed_divs, term)/(1-SELL_FEE),
              irr(QUOTE, stressed_divs, term))
    print("持有门槛与收盘重合所需额外现金",
          (QUOTE*(1-SELL_FEE)-pv(.04,weighted,terminal))*1.04**years(END)*SHARES/(1-SELL_FEE))
    h_price = 17.76 * .85587
    for ratio in (h_price / QUOTE, .8, 1.):
        print("H股期末实现比例、条件年化", ratio, irr(h_price, weighted, terminal * ratio,
              entry_fee=.0016, exit_fee=.0016, div_tax=(.20,) * 6))
    for state in OPERATIONS:
        ann, _, _ = project(state, 1)
        print(state, "收入、毛利、储备、流动资源", [
            tuple(round(row[k],2) for k in ("revenue","gross","reserve","liquid")) for row in ann])


if __name__ == "__main__":
    main()
