"""中际旭创条件估值；标准库；亿元、亿股、CNY；不依赖调用目录。"""
from copy import deepcopy
from datetime import date
from math import isclose
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent

def simulate(x,case):
    f,c=x['facts'],x['common'];s=x['scenarios'][case['scenario']]
    cash=(f['cash_equivalents']-c['nci_cash_exclusion']-c['operating_cash_buffer']
          -c['old_equipment_payable_reserve']-c['old_warranty_reserve']
          -f['post_balance_dividend']+c['opening_parent_cash_adjustment'])
    portfolio=f['financial_assets']*c['portfolio_parent_fraction']*s['portfolio_realization']
    shares=f['registered_shares']-f['treasury_shares']
    revenue=c['revenue_anchor_2026'];nwc=c['opening_nwc'];rows=[]
    for i,ds in enumerate(x['forecast_dates']):
        t=(date.fromisoformat(ds)-date.fromisoformat(x['research_date'])).days/365.25
        revenue*= (1+s['volume_growth'][i])*(1+s['mix_asp_change'][i])
        ebit_rate=s['gross_margin'][i]-s['cash_and_recurring_opex_rate'][i]-s['fx_cost_rate'][i]-s['impairment_rate'][i]
        interest=f['ordinary_debt']*c['borrowing_rate']
        group_profit=(revenue*ebit_rate-interest)*(1-c['tax_rate'])
        sub=s['terahop_profit_share'][i]
        ownership=(1-sub)*c['parent_other_ownership']+sub*c['terahop_ownership_after_warrant']
        parent_profit=group_profit*ownership
        next_nwc=revenue*s['nwc_revenue_ratio'][i];change_nwc=next_nwc-nwc
        capex=s['maintenance_capex'][i]+s['growth_capex'][i]
        net_reinvestment=capex-s['da'][i]+change_nwc+s['other_investment_cash'][i]
        funding=c['capex_funding_fraction_override']
        funding=ownership if funding is None else funding
        fraction=c.get('first_period_fraction',1) if i==0 else 1
        # 流量按剩余年度缩短；期末营运资金余额是存量目标，不能整体按天打折。
        period_reinvestment=(capex-s['da'][i]+s['other_investment_cash'][i])*fraction+change_nwc
        fcfe=parent_profit*fraction-period_reinvestment*funding
        financial_cash=(cash*c['cash_yield_aftertax']+portfolio*c['portfolio_yield_aftertax'])*fraction
        vest=f['awards_shares']*c['awards_vesting_fractions'][i]
        proceeds=vest*c['award_proceeds_price_proxy']
        start_cash,start_portfolio,start_shares=cash,portfolio,shares
        shares+=vest
        # 0.5亿元已公告基金认缴，首期全额缴足的代理；对应资产一并加入，不作为纯损失。
        fund=.5 if i==0 else 0
        cash+=fcfe+financial_cash+proceeds-fund
        portfolio+=fund*s['portfolio_realization']
        sale=max(0,c['liquidity_reserve']-cash)
        sale=min(sale,portfolio)
        cash+=sale;portfolio-=sale
        if cash<0:raise ValueError('现金不足，需要显式融资/稀释；不自动补资金')
        dividend=min(max(cash-c['liquidity_reserve'],0),max(parent_profit*fraction+financial_cash,0)*s['payout'])
        cash-=dividend
        assert isclose(cash,start_cash+fcfe+financial_cash+proceeds-fund+sale-dividend,abs_tol=1e-8)
        assert isclose(portfolio,start_portfolio+fund*s['portfolio_realization']-sale,abs_tol=1e-8)
        assert isclose(shares,start_shares+vest,abs_tol=1e-10)
        rows.append(dict(date=ds,years=t,revenue=revenue,ebit_margin=ebit_rate,group_aftertax_interest=interest*(1-c['tax_rate']),group_operating_profit=group_profit,parent_fraction=ownership,parent_operating_profit=parent_profit,nwc=next_nwc,change_nwc=change_nwc,capex=capex,da=s['da'][i],net_reinvestment=net_reinvestment,period_fraction=fraction,period_net_reinvestment=period_reinvestment,fcfe=fcfe,financial_cash=financial_cash,dividend=dividend,dps=dividend/shares,shares=shares,cash=cash,portfolio=portfolio,portfolio_sale=sale,award_proceeds=proceeds))
        nwc=next_nwc
    # 对合约不完备的赎回权作经济压力代理：只在结算额高于取得权益价值时行权。
    # 结算款与取得少数股权同时入桥，不将负债本金与永久少数利润双扣。
    original_profit=rows[-1]['parent_operating_profit']
    acquired_profit=rows[-1]['group_operating_profit']*s['terahop_profit_share'][-1]*c['redemption_covered_stake']
    acquired_value=acquired_profit*case['pe']
    settlement=f['redemption_book_liability']*(1+c['redemption_annual_growth'])**3*c['redemption_cost_multiplier']
    exercise=settlement>acquired_value
    if exercise:
        if cash+portfolio<settlement:raise ValueError('赎回压力需新增融资；不能隐含消失')
        sale=max(settlement-cash,0);portfolio-=sale;cash+=sale-settlement
        terminal_profit=original_profit+acquired_profit
    else:terminal_profit=original_profit
    operating_value=terminal_profit*case['pe']
    equity=operating_value+cash+portfolio
    assert isclose(equity,original_profit*case['pe']+rows[-1]['cash']+rows[-1]['portfolio']-max(settlement-acquired_value,0),abs_tol=1e-7)
    return dict(label=case['label'],scenario=case['scenario'],probability=case['probability'],pe=case['pe'],research_date=x['research_date'],terminal_date=x['forecast_dates'][-1],terminal_years=rows[-1]['years'],rows=rows,terminal_operating_profit=terminal_profit,terminal_pre_redemption_profit=original_profit,terminal_operating_value=operating_value,terminal_assets=cash+portfolio,terminal_equity=equity,terminal_price=equity/shares,redemption_exercised=exercise,redemption_settlement=settlement if exercise else 0,redemption_acquired_profit=acquired_profit if exercise else 0,redemption_net_value_loss=max(settlement-acquired_value,0))

def pv(z,r,c):
    return sum(v['dps']*(1-c['dividend_tax'])/(1+r)**v['years'] for v in z['rows'])+z['terminal_price']*(1-c['exit_fee'])/(1+r)**z['terminal_years']

def irr(z,price,c,entry_fee=None):
    cost=price*(1+(c['entry_fee'] if entry_fee is None else entry_fee));lo,hi=-.99,10
    assert pv(z,lo,c)>cost>pv(z,hi,c)
    for _ in range(120):
        mid=(lo+hi)/2
        if pv(z,mid,c)>cost:lo=mid
        else:hi=mid
    return (lo+hi)/2

def weighted(x):
    assert isclose(sum(v['probability'] for v in x['cases']),1,abs_tol=1e-10)
    cases=[simulate(x,v) for v in x['cases']]
    z=dict(research_date=x['research_date'],terminal_date=x['forecast_dates'][-1],terminal_years=cases[0]['terminal_years'],rows=[])
    for k in ['terminal_equity','terminal_price','terminal_operating_value','terminal_assets','terminal_operating_profit','terminal_pre_redemption_profit','redemption_net_value_loss']:
        z[k]=sum(v[k]*v['probability'] for v in cases)
    for i in range(3):
        row=dict(date=cases[0]['rows'][i]['date'],years=cases[0]['rows'][i]['years'])
        for k in ['revenue','parent_operating_profit','fcfe','dividend','dps','capex','change_nwc','net_reinvestment']:
            row[k]=sum(v['rows'][i][k]*v['probability'] for v in cases)
        z['rows'].append(row)
    c=x['common'];p=x['facts']['reference_price'];shares=x['facts']['registered_shares']-x['facts']['treasury_shares']
    z['buy_price']=pv(z,c['buy_return'],c)/(1+c['entry_fee'])
    z['sell_price']=pv(z,c['sell_return'],c)/(1-c['exit_fee'])
    z['buy_equivalent_market_cap']=z['buy_price']*shares;z['sell_equivalent_market_cap']=z['sell_price']*shares
    z['reference_irr']=irr(z,p,c)
    for v in cases:
        v['reference_irr']=irr(v,p,c)
        v['buy_irr']=irr(v,z['buy_price'],c)
        v['reference_cumulative_return']=pv(v,0,c)/(p*(1+c['entry_fee']))-1
        v['buy_cumulative_return']=pv(v,0,c)/(z['buy_price']*(1+c['entry_fee']))-1
    for r in [0,.04,.18]:assert isclose(pv(z,r,c),sum(v['probability']*pv(v,r,c) for v in cases),abs_tol=1e-7)
    assert isclose(irr(z,z['buy_price'],c),c['buy_return'],abs_tol=1e-10)
    assert isclose(irr(z,z['sell_price']*(1-c['exit_fee']),c,entry_fee=0),c['sell_return'],abs_tol=1e-10)
    return z,cases

def concise(z):return {k:z[k] for k in ['buy_price','sell_price','reference_irr','terminal_equity','terminal_operating_profit']}

def stresses(x,z,cases):
    out={}
    for field,delta in [('gross_margin',-.03),('gross_margin',.03),('nwc_revenue_ratio',.05),('growth_capex',50),('terahop_profit_share',.10)]:
        y=deepcopy(x)
        for s in y['scenarios'].values():s[field]=[v+delta for v in s[field]]
        out[f'{field}_{delta:+g}']=concise(weighted(y)[0])
    for field,val in [('opening_parent_cash_adjustment',-100),('opening_parent_cash_adjustment',100),('redemption_cost_multiplier',2),('capex_funding_fraction_override',1),('dividend_tax',.2),('award_proceeds_price_proxy',0),('portfolio_parent_fraction',.5)]:
        y=deepcopy(x);y['common'][field]=val;out[f'{field}_{val}']=concise(weighted(y)[0])
    # 倍数压缩与政策概率分别调整，不用平均IRR。
    for dest in ['access','upside']:
        y=deepcopy(x);normal=sum(v['probability'] for v in y['cases'] if v['scenario']=='normal');target=sum(v['probability'] for v in y['cases'] if v['scenario']==dest)
        for v in y['cases']:
            if v['scenario']=='normal':v['probability']*=1-.10/normal
            if v['scenario']==dest:v['probability']*=1+.10/target
        out['move10pp_normal_to_'+dest]=concise(weighted(y)[0])
    y=deepcopy(x)
    for v in y['cases']:v['pe']=min(v['pe'],10)
    out['all_pe_capped10']=concise(weighted(y)[0])
    delayed=deepcopy(z)
    delayed['terminal_years']=(date(2031,11,17)-date.fromisoformat(x['research_date'])).days/365.25
    out['terminal_delay_two_years_no_extra_dividend']={'reference_irr':irr(delayed,x['facts']['reference_price'],x['common']),'buy_price':pv(delayed,.18,x['common'])/(1+x['common']['entry_fee']),'irr_at_original_buy':irr(delayed,z['buy_price'],x['common'])}
    # 双上市退出权：公平价换股取得额外权益；按H股价格相对模型每股价值检验。
    # 与现金赎回为同一批权益的互斥安排，只作用于未触发现金赎回路径。
    swap={}
    for h_ratio in [.7,1,1.3]:
        eq,ps=0,0
        for v in cases:
            acquired=0 if v['redemption_exercised'] else v['rows'][-1]['group_operating_profit']*x['scenarios'][v['scenario']]['terahop_profit_share'][-1]*x['common']['redemption_covered_stake']*v['pe']
            new_shares=acquired/(v['terminal_price']*h_ratio)
            p=(v['terminal_equity']+acquired)/(v['rows'][-1]['shares']+new_shares)
            eq+=(v['terminal_equity']+acquired)*v['probability'];ps+=p*v['probability']
            if h_ratio==1:assert isclose(p,v['terminal_price'],abs_tol=1e-8)
        zz=deepcopy(z);zz['terminal_price']=ps
        swap[str(h_ratio)]={'expected_total_equity':eq,'expected_per_share':ps,'buy_price':pv(zz,.18,x['common'])/(1+x['common']['entry_fee'])}
    out['fair_value_subsidiary_stake_swap_h_price_ratio']=swap
    return out

def policy_review(x):
    """调权仅从正常状态按原有倍数比例拨入，其他状态互斥且固定。"""
    reference = x['facts']['reference_price']
    central = {s: sum(c['probability'] for c in x['cases'] if c['scenario'] == s)
               for s in ('normal', 'access', 'limited')}

    def price(severe, limited, margin_shift=0):
        y = deepcopy(x)
        weights = dict(access=severe, limited=limited,
                       normal=sum(central.values()) - severe - limited)
        assert min(weights.values()) >= 0
        for case in y['cases']:
            state = case['scenario']
            if state in weights:
                case['probability'] *= weights[state] / central[state]
        for state in ('normal', 'limited'):
            margins = y['scenarios'][state]['gross_margin']
            y['scenarios'][state]['gross_margin'] = [m + margin_shift for m in margins]
        return weighted(y)[0]['buy_price']

    limited = central['limited']
    severe = central['access']
    movable = sum(central.values())
    def crossing(weight, fixed, calculate_price):
        # 固定逐路径现金流时，目标回报对应的入场价格对联合权重呈线性。
        limit = movable - fixed
        start, end = calculate_price(0), calculate_price(limit)
        if isclose(start, end) or not min(start, end) <= reference <= max(start, end):
            return None
        threshold = limit * (start - reference) / (start - end)
        assert isclose(calculate_price(threshold), reference, abs_tol=1e-7), weight
        return threshold

    table = []
    for margin_shift in (-.02, 0, .02):
        threshold = crossing('severe', limited, lambda w: price(w, limited, margin_shift))
        table.append(dict(margin_shift=margin_shift,
                          prices={str(w): price(w, limited, margin_shift) for w in (.05, .10, .15, .20, .25)},
                          severe_weight_at_reference=threshold))
    base = price(severe, limited)
    assert isclose(base, weighted(x)[0]['buy_price'], abs_tol=1e-8)
    no_limited = price(severe, 0)
    limited_threshold = crossing('limited', severe, lambda w: price(severe, w))
    same_multiple = deepcopy(x)
    normal_pe = sum(c['pe'] * c['probability'] for c in x['cases']
                    if c['scenario'] == 'normal') / central['normal']
    for case in same_multiple['cases']:
        if case['scenario'] == 'limited':
            case['pe'] = normal_pe
    return dict(prior_price_without_limited=no_limited, joint_sensitivity=table,
                limited_at_normal_mean_pe=weighted(same_multiple)[0]['buy_price'],
                limited_weight_at_reference=limited_threshold,
                limited_sensitivity={str(w): price(severe, w) for w in (0,.10,.15,.20,.30)})

def breakeven(x):
    out={}
    for target in [0,.18]:
        def price_at(pe):
            y=deepcopy(x)
            for c in y['cases']:c['pe']=pe
            z,_=weighted(y)
            return pv(z,target,y['common'])/(1+y['common']['entry_fee'])
        lo,hi=.05,50
        for _ in range(90):
            mid=(lo+hi)/2
            if price_at(mid)<x['facts']['reference_price']:lo=mid
            else:hi=mid
        out[str(target)]=(lo+hi)/2
    return out

def run(x):
    z,cases=weighted(x)
    # 与终值倍数无关的现金桥应相同，回购只在终点压力中结算。
    assert cases[0]['rows']==cases[1]['rows'] and cases[2]['rows']==cases[3]['rows']
    assert all(v['rows'][-1]['shares']>x['facts']['registered_shares']-x['facts']['treasury_shares'] for v in cases)
    assert all(v['rows'][-1]['cash']>=0 for v in cases)
    f=x['facts'];core_ebit=f['revenue_9m2026']-sum(f['operating_costs_9m2026_ex_finance'])
    reconciliation={'core_ebit_9m':core_ebit,'reported_parent_fraction_9m':f['parent_profit_9m2026']/f['group_profit_9m2026'],'normalized_parent_profit_9m_proxy':(core_ebit-f['revenue_9m2026']*.007-f['interest_expense_9m2026'])*(1-x['common']['tax_rate'])*f['parent_profit_9m2026']/f['group_profit_9m2026'],'cfo_less_capex_9m':f['cfo_9m2026']-f['capex_9m2026'],'q3_cfo':f['cfo_9m2026']-f['cfo_h12026']}
    return dict(research_date=x['research_date'],currency=x['currency'],amount_unit='亿元',historical_reconciliation=reconciliation,weighted=z,cases=cases,stress=stresses(x,z,cases),policy_review=policy_review(x),uniform_terminal_pe_required=breakeven(x),verification='逐路径现金与股数守恒、同经营不同PE、期望现金流现值线性、18%及4%逆推、回购权益与结算对称、平价换股每股中性、准入权重临界点回代检查通过。')

if __name__=='__main__':
    x=json.loads((HERE/'inputs.json').read_text());o=run(x)
    (HERE/'results.json').write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(concise(o['weighted']),ensure_ascii=False,indent=2))
