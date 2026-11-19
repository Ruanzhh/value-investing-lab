"""美的A股三年期人民币现金流，金额亿元、亿股，日期按实际天数。"""
from copy import deepcopy
from datetime import date
import json
from math import isclose
from pathlib import Path

HERE = Path(__file__).resolve().parent


def years(start, end):
    return (date.fromisoformat(end) - date.fromisoformat(start)).days / 365.25


def opening(x, s):
    b = x['balance']
    shares = x['a_ex_treasury'] + x['h_ex_treasury']
    liquid = b['cash_equivalents'] + b['current_deposits_proxy'] + b['long_deposits_proxy']
    reserve = sum(b[k] for k in ('pledged_deposits', 'operating_buffer', 'nci_cash_buffer',
                                  'after_q3_net_repurchase_cost', 'other_settlement_reserve'))
    debt = sum(b[k] for k in ('short_loans', 'long_loans', 'current_debt_and_leases', 'long_leases'))
    liquid -= reserve + debt + 2 * x['cb_par_cny_per_tranche'] + shares * x['old_interim_per_share']
    assets = sum(b[k] for k in ('trade_assets', 'other_equity_assets', 'associates'))
    nav = assets * s['nav_fraction'] * b['nav_parent_share'] - b['financial_trading_liability']
    return shares, liquid, nav


def path(x, case):
    s = x['paths'][case['path']]
    shares, cash, nav = opening(x, s)
    base_shares = shares
    consumer, other = x['fy26_consumer_sales'], x['fy26_other_sales']
    prior_total = x['fy26_reported_profit_proxy']
    last_interim = shares * x['old_interim_per_share']
    flows, rows = {}, []
    # 2026中期总款已从起点拨备，A股如能领款，仅在投资者端恢复其权利。
    if x['a_old_interim_entitled']:
        flows['2026-11-27'] = x['old_interim_per_share']
    for i in range(3):
        year = 2027 + i
        start_shares, start_cash = shares, cash
        # 上一滚动经营期的中期股息在十一月末支付。首期既有中期款已另作拨备。
        interim = 0 if i == 0 else last_interim
        if interim:
            flows[f'{year-1}-11-27'] = interim / shares
        cash -= interim
        # 2027年五月短券结算，长券的未转股本金全额留作债务；上行按第三期夏季分红前长券转股测算。
        convert = s['cb'][0] if i == 0 else (s['cb'][1] if i == 2 else 0)
        tranche = 0 if i == 0 else 1
        converted_shares = convert * x['cb_shares'][tranche]
        conversion_cash = convert * x['cb_par_cny_per_tranche']
        vest = x['a_options_to_vest'] / 3
        shares += vest + converted_shares
        proceeds = vest * x['option_price_proxy']
        cash += proceeds + conversion_cash
        final_dividend = max(0, prior_total * s['payout'] - last_interim)
        flows[f'{year}-07-15'] = final_dividend / shares
        consumer *= (1 + s['volume'][i]) * (1 + s['asp'][i])
        other *= 1 + s['other_growth'][i]
        revenue = consumer + other
        operating = revenue * s['margin'][i] * (1 - x['income_tax']) * x['parent_interest']
        reinvest = (s['maint'][i] + s['growth'][i] - s['da'][i] + s['wc'][i] + s['ma'][i]) * x['parent_interest']
        fcfe = operating - reinvest
        # 以期初流动资金计息，七月分红扣约四个月利息；当年净经营现金取半年。
        financial_income = x['liquid_yield_after_tax'] * (start_cash - interim + .5 * (fcfe + proceeds + conversion_cash) - final_dividend / 3)
        cash += fcfe + financial_income - final_dividend
        assert cash > 0 and isclose(cash, start_cash + fcfe + financial_income + proceeds + conversion_cash - interim - final_dividend)
        assert isclose(shares, start_shares + vest + converted_shares)
        prior_total = operating + financial_income
        last_interim = min(0.5 * shares, prior_total * s['payout'])
        rows.append(dict(year=year, revenue=revenue, consumer=consumer, other=other,
                         operating=operating, total_recurring=prior_total, fcfe=fcfe, reinvest=reinvest,
                         holders_dividend=interim + final_dividend, retained_liquid=cash,
                         shares=shares, option_proceeds=proceeds, conversion_cash=conversion_cash))
    terminal_equity = operating * case['pe'] + cash + nav
    terminal_per_share = terminal_equity / shares
    return dict(**case, rows=rows, opening_cash=opening(x, s)[1], base_shares=base_shares,
                nav=nav, terminal_equity=terminal_equity, terminal_per_share=terminal_per_share,
                flows=flows, operating=operating)


def pv(flows, rate, asof):
    return sum(v / (1 + rate) ** years(asof, day) for day, v in flows.items())


def irr(flows, cost, asof):
    lo, hi = -.90, 5.
    assert pv(flows, lo, asof) > cost > pv(flows, hi, asof)
    for _ in range(80):
        mid = (lo + hi) / 2
        if pv(flows, mid, asof) > cost:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def evaluate(x, delay=0):
    cases = [path(x, c) for c in x['cases']]
    assert isclose(sum(c['p'] for c in cases), 1)
    expected = {}
    terminal = x['end'] if not delay else str(2029 + delay) + x['end'][4:]
    for c in cases:
        flows = {d: v * (1 - x['dividend_tax']) for d, v in c['flows'].items()}
        flows[terminal] = c['terminal_per_share'] * (1 - x['exit_fee'])
        for d, v in flows.items():
            expected[d] = expected.get(d, 0) + c['p'] * v
        cost = x['reference'] * (1 + x['entry_fee'])
        c['reference_irr'] = irr(flows, cost, x['asof'])
        c['cumulative'] = sum(flows.values()) / cost - 1
    buy = pv(expected, x['buy_yield'], x['asof']) / (1 + x['entry_fee'])
    sell = pv(expected, x['sell_yield'], x['asof']) / (1 - x['exit_fee'])
    assert isclose(irr(expected, buy * (1 + x['entry_fee']), x['asof']), x['buy_yield'])
    assert isclose(irr(expected, sell * (1 - x['exit_fee']), x['asof']), x['sell_yield'])
    for c in cases:
        flows = {d: v*(1-x['dividend_tax']) for d,v in c['flows'].items()}
        flows[terminal] = c['terminal_per_share']*(1-x['exit_fee'])
        c['buy_irr'] = irr(flows,buy*(1+x['entry_fee']),x['asof'])
        c['buy_cumulative'] = sum(flows.values())/(buy*(1+x['entry_fee']))-1
    weights = {k: sum(c['p'] * c[k] for c in cases) for k in ('operating', 'terminal_equity', 'terminal_per_share')}
    count = cases[0]['base_shares']
    return dict(**weights, buy=buy, sell=sell, buy_cap=buy*count, sell_cap=sell*count,
                reference_irr=irr(expected,x['reference']*(1+x['entry_fee']),x['asof']),
                net_flows=expected,cases=cases)


def compact(o):
    return {k: o[k] for k in ('buy','sell','reference_irr')}


def run(x):
    out = evaluate(x)
    stress = {}
    for name in ('margin_minus_2pp','wc_extra_60','lower_nav_300','all_pe_10max',
                 'base_ttm_margin','supplier_credit_unwind','downweight_to_40','cb_cash','cb_all_convert','tax20','exclude_old_interim'):
        y = deepcopy(x)
        for s in y['paths'].values():
            if name == 'margin_minus_2pp':
                s['margin'] = [m-.02 for m in s['margin']]
            if name == 'wc_extra_60':
                s['wc'] = [v+60 for v in s['wc']]
            if name in ('cb_cash','cb_all_convert'):
                s['cb'] = [int(name=='cb_all_convert')]*2
        if name == 'base_ttm_margin':
            y['paths']['base']['margin'] = [0.0947] * 3
        if name == 'supplier_credit_unwind':
            for s in y['paths'].values():
                s['wc'][0] += 250
        if name == 'lower_nav_300':
            y['balance']['operating_buffer'] += 300
        if name == 'all_pe_10max':
            for c in y['cases']:
                c['pe'] = min(10,c['pe'])
        if name == 'downweight_to_40':
            for c in y['cases']:
                if c['path']=='down': c['p'] += .15
                if c['path']=='base': c['p'] *= .40/.55
        if name == 'tax20': y['dividend_tax']=.20
        if name == 'exclude_old_interim': y['a_old_interim_entitled']=False
        stress[name]=compact(evaluate(y))
    delayed=evaluate(x,2)
    stress['two_year_delay_no_further_dividends'] = dict(**compact(delayed),irr_at_buy=irr(delayed['net_flows'],out['buy']*(1+x['entry_fee']),x['asof']))
    multiples={}
    for rate in (0, x['buy_yield']):
        measures=[]
        for pe in (10, 11):
            y=deepcopy(x)
            for c in y['cases']: c['pe']=pe
            measures.append(pv(evaluate(y)['net_flows'],rate,x['asof'])/(1+x['entry_fee']))
        multiples[str(rate)]=10+(x['reference']-measures[0])/(measures[1]-measures[0])
    return dict(asof=x['asof'],end=x['end'],expected=out,stress=stress,uniform_pe_required=multiples)


if __name__=='__main__':
    result = run(json.loads((HERE/'inputs.json').read_text()))
    (HERE/'results.json').write_text(json.dumps(result, ensure_ascii=False,indent=2)+'\n')
    print(compact(result['expected']))
