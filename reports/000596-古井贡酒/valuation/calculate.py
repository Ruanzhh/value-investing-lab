#!/usr/bin/env python3
"""古井贡酒：联合情景、归母现金桥和期望现金流 IRR；仅使用标准库。"""
import copy
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def date(s):
    return dt.date.fromisoformat(s)

def years(a, b):
    return (date(b) - date(a)).days / 365.25

def pv(flows, start, rate):
    return sum(v / (1 + rate) ** years(start, day) for day, v in flows)

def irr(cost, flows, start):
    lo, hi = -.999, 10.
    if cost <= 0 or any(value < 0 for _, value in flows):
        raise ValueError('本模型仅支持一次买入及后续非负现金流')
    if not pv(flows, start, lo) > cost > pv(flows, start, hi):
        raise ValueError('IRR超出求解区间，须检查现金流及价格')
    for _ in range(160):
        mid = (lo + hi) / 2
        if pv(flows, start, mid) > cost:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

def operating_case(d, case):
    c = d['business_cases'][case]
    l = d['liquidity']
    cash = l['cash_equivalents'] + l['trading_financial'] - l['nci_cash_estimate'] - l['operating_reserve'] + l['sep30_to_research_net_change_assumption']
    initial_cash = cash
    revenue = c['revenue_start']
    rows, dividends = [], []
    start = date(d['research_date'])
    for i, end_s in enumerate(d['cashflow_year_ends']):
        end = date(end_s)
        revenue *= (1+c['volume_growth'][i]) * (1+c['mix_price_growth'][i])
        pretax_margin = c['gross_margin'][i] - sum(c[k][i] for k in ['selling_ratio', 'admin_ratio', 'surtax_ratio', 'rd_ratio', 'interest_cost_ratio'])
        core_np = revenue * (pretax_margin * .75 - c['nci_profit_ratio'][i]) + l['operating_reserve'] * l['reserve_aftertax_yield']
        capex = c['maintenance'][i] + c['growth_capex'][i]
        operating_fcfe = core_np + c['da'][i] - capex - c['nwc_increase'][i]
        if i == 0:
            annual_dividend = d['fy2026_profit_estimate'] * d['fy2026_total_payout_assumption'] - d['initial_dividend']['per_share'] * d['shares']
        else:
            annual_dividend = rows[-1]['total_np'] * c['payout']
        events = {date(d['annual_dividend_dates'][i]): annual_dividend}
        if i == 0:
            events[date(d['initial_dividend']['date'])] = d['initial_dividend']['per_share'] * d['shares']
        assert all(start < day <= end for day in events)
        days = (end-start).days
        interest_total, cash_open = 0., cash
        # 各年经营自由现金按日均匀形成；金融收益按实际天数滚存，分红当日扣减。
        daily_yield = (1+l['excess_cash_aftertax_yield'])**(1/365.25)-1
        for n in range(1, days+1):
            day = start + dt.timedelta(days=n)
            interest = cash * daily_yield
            cash += operating_fcfe/days + interest
            interest_total += interest
            if day in events:
                cash -= events[day]
                dividends.append((day.isoformat(), events[day]/d['shares']))
            assert cash > 0, '现金不足；须显式建模融资，不能隐含透支'
        row = dict(year=i+1, end=end_s, revenue=revenue, core_np=core_np,
                   core_margin=core_np/revenue, da=c['da'][i], capex=capex,
                   maintenance=c['maintenance'][i], growth_capex=c['growth_capex'][i],
                   nwc_increase=c['nwc_increase'][i], operating_fcfe=operating_fcfe,
                   excess_cash_interest=interest_total, total_np=core_np+interest_total,
                   cash_open=cash_open, dividend_total=sum(events.values()), cash_close=cash)
        assert abs(cash_open+operating_fcfe+interest_total-sum(events.values())-cash) < 1e-8
        rows.append(row)
        start=end
    return dict(initial_excess_cash=initial_cash, rows=rows, dividends=dividends,
                terminal_excess_cash=cash)

def flows_for(d, path, share_class='a', terminal_multiplier=1., delay_years=0, dividend_tax=None):
    f=d['tax_fees']
    tax=f[share_class+'_dividend_tax'] if dividend_tax is None else dividend_tax
    flows=[(day, value*(1-tax)) for day, value in path['dividends']]
    end=date(d['terminal_date'])
    end=end.replace(year=end.year+delay_years).isoformat()
    terminal=path['terminal_value']/d['shares']*terminal_multiplier*(1-f[share_class+'_sell'])
    flows.append((end, terminal))
    return flows

def weighted_flows(d, paths, **kwargs):
    totals={}
    for p in paths:
        for day, value in flows_for(d,p,**kwargs):
            totals[day]=totals.get(day,0)+p['weight']*value
    return sorted(totals.items())

def run(d):
    if d['tax_fees']['capital_gains_tax'] != 0:
        raise ValueError('本模型仅实现资本利得税为0的假设；其他税率须先补充成本基础与计税逻辑')
    assert abs(sum(p['weight'] for p in d['joint_scenarios'])-1)<1e-10
    assert abs(d['a_shares']+d['b_shares']-d['shares'])<1e-10
    cases={k:operating_case(d,k) for k in d['business_cases']}
    paths=[]
    for s in d['joint_scenarios']:
        assert s['weight']>=0 and s['pe_range'][0]<=s['pe']<=s['pe_range'][1]
        c=cases[s['business']]
        op_value=c['rows'][-1]['core_np']*s['pe']
        paths.append(dict(**s, terminal_operating_value=op_value,
                          terminal_cash=c['terminal_excess_cash'],
                          terminal_value=op_value+c['terminal_excess_cash']+d['liquidity']['other_assets_added'],
                          dividends=c['dividends']))
    flows=weighted_flows(d,paths)
    buy=pv(flows,d['research_date'],d['target_return'])/(1+d['tax_fees']['a_buy'])
    price=d['market']['a_price']
    expected={k:sum(p['weight']*p[k] for p in paths) for k in ['terminal_operating_value','terminal_cash','terminal_value']}
    expected['years']=[{k:sum(s['weight']*cases[s['business']]['rows'][i][k] for s in paths) for k in ['revenue','core_np','total_np','operating_fcfe','capex','nwc_increase','dividend_total']} for i in range(3)]
    expected.update(a_buy_price=buy, a_equivalent_buy_market_cap=buy*d['shares'],
                    a_price_irr=irr(price*(1+d['tax_fees']['a_buy']),flows,d['research_date']),
                    a_price=price, weighted_net_cashflows=flows,
                    a_buy_price_irr=irr(buy*(1+d['tax_fees']['a_buy']),flows,d['research_date']))
    assert abs(expected['a_buy_price_irr']-d['target_return'])<1e-9
    for p in paths:
        fl=flows_for(d,p)
        p['irr_at_a_price']=irr(price*(1+d['tax_fees']['a_buy']),fl,d['research_date'])
        p['irr_at_buy']=irr(buy*(1+d['tax_fees']['a_buy']),fl,d['research_date'])
        p['cumulative_at_a_price']=sum(v for _,v in fl)/(price*(1+d['tax_fees']['a_buy']))-1
        p['cumulative_at_buy']=sum(v for _,v in fl)/(buy*(1+d['tax_fees']['a_buy']))-1
        p['own_18pct_buy']=pv(fl,d['research_date'],.18)/(1+d['tax_fees']['a_buy'])
    m=d['market']; b_cny=m['b_price_hkd']*m['cny_per_hkd']; b_relative=b_cny/price
    bflows=weighted_flows(d,paths,share_class='b',terminal_multiplier=b_relative)
    bbuy=pv(bflows,d['research_date'],.18)/(1+d['tax_fees']['b_buy'])
    b=dict(relative_exit_price=b_relative,price_cny=b_cny,buy_cny=bbuy,buy_hkd=bbuy/m['cny_per_hkd'],
           irr_constant_relative_discount=irr(b_cny*(1+d['tax_fees']['b_buy']),bflows,d['research_date']),
           actual_ab_market_cap=price*d['a_shares']+b_cny*d['b_shares'],a_equivalent_market_cap=price*d['shares'])
    sensitivity={}
    for r in [.12,.15,.18,.20]:
        sensitivity['target_'+str(r)]=pv(flows,d['research_date'],r)/(1+d['tax_fees']['a_buy'])
    for change in [-4,4]:
        alt=copy.deepcopy(paths)
        for p in alt:
            delta=cases[p['business']]['rows'][-1]['core_np']*change
            p['terminal_value']+=delta
        sensitivity['all_pe_shift_'+str(change)]=pv(weighted_flows(d,alt),d['research_date'],.18)/(1+d['tax_fees']['a_buy'])
    for src,dst in [('R','D'),('R','R_low'),('S','U')]:
        alt=copy.deepcopy(paths)
        for p in alt:
            p['weight']+= .1 if p['id']==dst else (-.1 if p['id']==src else 0)
        sensitivity['weight_10pp_'+src+'_to_'+dst]=pv(weighted_flows(d,alt),d['research_date'],.18)/(1+d['tax_fees']['a_buy'])
    for delay in [1,2]:
        delayed=weighted_flows(d,paths,delay_years=delay)
        sensitivity['delay_'+str(delay)]=dict(irr_at_a_price=irr(price*(1+d['tax_fees']['a_buy']),delayed,d['research_date']),irr_at_buy=irr(buy*(1+d['tax_fees']['a_buy']),delayed,d['research_date']))
    # 反推：期间分红与期末现金保持原模型，仅改变经营利润×PE。
    divs=flows[:-1]; end_years=years(d['research_date'],d['terminal_date'])
    expected_core=expected['years'][-1]['core_np']
    implied={}
    for label,p0 in [('market',price),('buy',buy)]:
        for r in [0,.18]:
            total_needed=(p0*(1+d['tax_fees']['a_buy'])-pv(divs,d['research_date'],r))*(1+r)**end_years/(1-d['tax_fees']['a_sell'])*d['shares']
            op_needed=total_needed-expected['terminal_cash']
            implied[label+'_'+str(r)]=dict(terminal_equity_needed=total_needed,pe_on_expected_core=op_needed/expected_core,core_np_at_20pe=op_needed/20)
    return dict(expected=expected,b_share_conditional=b,business_cases=cases,joint_scenarios=paths,sensitivity=sensitivity,reverse_conditions=implied)

def main():
    d=json.loads((ROOT/'inputs.json').read_text())
    result=run(d)
    for name,delta in [('cash_minus10',-10),('cash_plus10',10)]:
        alt=copy.deepcopy(d);alt['liquidity']['sep30_to_research_net_change_assumption']+=delta
        result['sensitivity'][name]=run(alt)['expected']['a_buy_price']
    for tax in [.1,.2]:
        alt=copy.deepcopy(d);alt['tax_fees']['a_dividend_tax']=tax
        result['sensitivity']['dividend_tax_'+str(tax)]=run(alt)['expected']['a_buy_price']
    for name,y in [('yield_zero',0),('yield_2.4pct',.024)]:
        alt=copy.deepcopy(d);alt['liquidity']['excess_cash_aftertax_yield']=y
        result['sensitivity'][name]=run(alt)['expected']['a_buy_price']
    for change in [-.02,.02]:
        alt=copy.deepcopy(d)
        for case in alt['business_cases'].values():
            case['selling_ratio']=[x+change for x in case['selling_ratio']]
        result['sensitivity']['selling_ratio_shift_'+str(change)]=run(alt)['expected']['a_buy_price']
    alt=copy.deepcopy(d)
    for scenario in alt['joint_scenarios']:
        scenario['pe']=25
        scenario['pe_range']=[25,25]
    result['sensitivity']['all_paths_pe25']=run(alt)['expected']['a_buy_price']
    (ROOT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['expected','b_share_conditional','sensitivity','reverse_conditions']},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
