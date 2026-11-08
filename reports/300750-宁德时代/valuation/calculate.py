"""三年正常化归母经营净利与PE区间；只用标准库，金额亿元、股数亿股。"""
from copy import deepcopy
from datetime import date
import json
from math import isclose
from pathlib import Path

HERE = Path(__file__).resolve().parent


def bridge(x, s):
    f,c=x['facts'],x['common']
    debt=sum(f[k] for k in ('short_debt','long_debt','bonds','current_noncurrent_liabilities',
                            'lease_liabilities','long_payables'))
    repayment=debt if c['repay_debt_at_start'] else 0
    group_cash=(f['cash_equivalents']+f['trading_assets']-repayment-c['operating_cash_buffer']
                -f['provisions']*c['old_provision_reserve_fraction']-f['net_derivative_liabilities']
                -(f['buyback_at_oct31']-f['buyback_at_sep30']))
    portfolio=sum(f[k] for k in ('long_equity_investments','other_equity_investments','other_financial_investments'))
    return {'opening_debt':debt,'debt_repaid':repayment,'continuing_debt':debt-repayment,
            'group_cash_after_reserves':group_cash,'parent_cash':group_cash*c['cash_parent_fraction'],
            'parent_portfolio':portfolio*s['portfolio_realization']*c['portfolio_parent_fraction'],
            'initial_shares':f['registered_a']+f['registered_h']-f['employee_treasury']-f['pending_cancel']}


def simulate(x,name='base',*,pe,margin_shift=0,portfolio_override=None):
    c,s=x['common'],x['scenarios'][name]
    b=bridge(x,s)
    cash,portfolio,shares=b['parent_cash'],b['parent_portfolio'],b['initial_shares']
    if portfolio_override is not None:portfolio=portfolio_override
    assert cash>=0 and portfolio>=0 and pe>0
    d0=date.fromisoformat(x['research_date']);rows=[]
    for i,ds in enumerate(x['forecast_dates']):
        t=(date.fromisoformat(ds)-d0).days/365.25
        revenue=s['battery_gwh'][i]*s['battery_asp_cny_kwh'][i]*.01+s['other_revenue'][i]
        nopat=revenue*(s['core_nopat_margin'][i]+margin_shift)
        interest=b['continuing_debt']*s['borrowing_rate']
        aftertax_interest=interest*(1-c['normal_tax_rate'])
        net_income=nopat-aftertax_interest
        parent_income=net_income*c['operating_parent_fraction']
        reinvestment=(s['maintenance_capex'][i]+s['growth_capex'][i]-s['da'][i]
                      +s['working_capital_increase'][i]+s['other_growth_investment'][i])
        parent_fcfe=(net_income-reinvestment)*c['operating_parent_fraction']
        opening_cash,opening_portfolio,opening_shares=cash,portfolio,shares
        financial_cash=cash*c['cash_aftertax_yield']+portfolio*c['portfolio_cash_yield']
        buyback=c['remaining_buyback'] if i==0 else 0
        transfer=c['employee_transfer_shares'] if i==0 else 0
        proceeds=transfer*c['employee_transfer_price']
        shares+=transfer-buyback/c['buyback_execution_price']
        cash+=parent_fcfe+financial_cash+proceeds-buyback
        sale=max(-cash,0)
        if sale>portfolio+1e-8:raise ValueError('资金不足：须显式调整融资或投资，不隐含填平')
        portfolio-=sale;cash+=sale
        # 分红参考核心净利及资产现金收益，未假定全部权益法收益可以收到现金。
        target=max(parent_income+financial_cash,0)*c['dividend_target_fraction']
        dividend=min(max(cash,0),target);cash-=dividend
        assert shares>0 and cash>=-1e-8 and portfolio>=-1e-8
        assert isclose(opening_cash+parent_fcfe+financial_cash+proceeds-buyback+sale-dividend,cash,abs_tol=1e-7)
        assert isclose(opening_portfolio-sale,portfolio,abs_tol=1e-7)
        assert isclose(opening_shares+transfer-buyback/c['buyback_execution_price'],shares,abs_tol=1e-10)
        rows.append({'date':ds,'years_from_research':t,'revenue':revenue,'group_nopat':nopat,
                     'group_interest_expense':interest,'group_aftertax_interest':aftertax_interest,
                     'group_operating_net_income':net_income,'parent_operating_net_income':parent_income,
                     'group_net_reinvestment':reinvestment,'parent_operating_fcfe':parent_fcfe,
                     'financial_cash_income':financial_cash,'dividend':dividend,
                     'dividend_per_share':dividend/shares,'buyback':buyback,
                     'employee_proceeds':proceeds,'employee_transfer_shares':transfer,
                     'cash':cash,'portfolio':portfolio,'portfolio_sale':sale,'shares':shares})
    operating=rows[-1]['parent_operating_net_income']*pe
    equity=operating+cash+portfolio
    return {'research_date':x['research_date'],'scenario':name,'terminal_pe':pe,'bridge':b,'rows':rows,
            'terminal_operating_equity':operating,'terminal_nonoperating_assets':cash+portfolio,
            'terminal_equity':equity,'terminal_per_share':equity/shares,
            'terminal_date':rows[-1]['date'],'terminal_years':rows[-1]['years_from_research']}


def price_for_return(result,rate,c,dividend_tax=None):
    tax=c['dividend_tax'] if dividend_tax is None else dividend_tax
    pv=sum(row['dividend_per_share']*(1-tax)/(1+rate)**row['years_from_research'] for row in result['rows'])
    pv+=result['terminal_per_share']*(1-c['exit_fee'])/(1+rate)**result['terminal_years']
    return pv/(1+c['entry_fee'])


def irr(result,price,c,dividend_tax=None):
    lo,hi=-.99,5.
    assert price_for_return(result,lo,c,dividend_tax)>price>price_for_return(result,hi,c,dividend_tax)
    for _ in range(100):
        mid=(lo+hi)/2
        if price_for_return(result,mid,c,dividend_tax)>price:lo=mid
        else:hi=mid
    return (lo+hi)/2


def cumulative_return(result,price,c):
    return price_for_return(result,0,c)/price-1


def delayed_realization(result,years=2):
    z=deepcopy(result)
    end=date.fromisoformat(z['terminal_date'])
    end=end.replace(year=end.year+years)
    z['terminal_date']=end.isoformat()
    z['terminal_years']=(end-date.fromisoformat(z['research_date'])).days/365.25
    return z  # 金额不变，额外两年不增加分红；只是静态延迟压力。


def required_pe(result,price,c,rate=0):
    h=result['terminal_years'];last=result['rows'][-1]
    target=price*(1+c['entry_fee'])*(1+rate)**h
    paid=sum(row['dividend_per_share']*(1-c['dividend_tax'])*(1+rate)**(h-row['years_from_research']) for row in result['rows'])
    equity=(target-paid)/(1-c['exit_fee'])*last['shares']
    return (equity-result['terminal_nonoperating_assets'])/last['parent_operating_net_income']


def historical_reconciliation(x,market):
    h=x['financial_reconciliation'];out={}
    for key in ['parent_profit','cfo','capex']:
        out['ttm_'+key]=h['fy2025_'+key]+h['ytd2026_'+key]-h['ytd2025_'+key]
    out['ttm_cfo_less_capex']=out['ttm_cfo']-out['ttm_capex']
    out['headline_ttm_pe']=market/out['ttm_parent_profit']
    out['q32026_cfo']=h['ytd2026_cfo']-h['h12026_cfo']
    out['q32026_capex']=h['ytd2026_capex']-h['h12026_capex']
    out['q32026_cfo_yoy']=out['q32026_cfo']/h['q32025_cfo']-1
    out['core_ytd_ebit']=h['ytd2026_revenue']-sum(h['ytd2026_operating_costs_ex_finance'])
    out['core_ytd_nopat']=out['core_ytd_ebit']*(1-h['normal_operating_tax_assumption'])
    out['core_ytd_parent_net_income']=(out['core_ytd_ebit']-h['ytd2026_interest_expense'])*(1-h['normal_operating_tax_assumption'])*x['common']['operating_parent_fraction']
    for period in ['fy2025','h12026']:
        out[period+'_three_wc_items_net']=sum(h[period+'_'+key+'_cash_change'] for key in ['inventory','receivables','payables'])
    return out


def self_checks(x):
    base=simulate(x,pe=15);c=x['common'];last=base['rows'][-1]
    assert isclose(base['rows'][0]['revenue'],6430)
    assert isclose(base['terminal_equity'],last['parent_operating_net_income']*15+last['cash']+last['portfolio'])
    assert base['bridge']['debt_repaid']==0 and base['bridge']['continuing_debt']>0
    y=deepcopy(x);y['common']['repay_debt_at_start']=True
    paid=simulate(y,pe=15)
    assert paid['bridge']['continuing_debt']==0 and all(row['group_interest_expense']==0 for row in paid['rows'])
    assert isclose(base['bridge']['parent_cash']-paid['bridge']['parent_cash'],base['bridge']['opening_debt']*c['cash_parent_fraction'])
    y=deepcopy(x);y['scenarios']['base']['maintenance_capex'][0]+=10
    assert simulate(y,pe=15)['terminal_equity']<base['terminal_equity']
    for rate in [0,.12,.15,.20]:
        price=price_for_return(base,rate,c)
        assert isclose(irr(base,price,c),rate,abs_tol=1e-10)
        assert isclose(required_pe(base,price,c,rate),15,rel_tol=1e-10)
    price=x['facts']['a_price']
    assert irr(delayed_realization(base),price,c)<irr(base,price,c)
    higher=simulate(x,pe=20)
    assert higher['rows']==base['rows']  # 倍数变化不应偷偷改变经营与分红。
    assert price_for_return(base,.20,c)<price_for_return(base,.12,c)
    assert isclose(53.297804*13.29*.792,560.99562960672,rel_tol=1e-10)


def probability_weighted_forecast(x, cases=None):
    assert x['decision_policy']['return_metric']=='irr_of_expected_cashflows'
    cases=x['probability_assessment']['cases'] if cases is None else cases
    assert cases and all(0 <= item['probability'] <= 1 for item in cases)
    assert isclose(sum(item['probability'] for item in cases),1,abs_tol=1e-10)
    pairs=[(item,simulate(x,item['scenario'],pe=item['representative_pe'])) for item in cases]
    # 分别汇总整体价值和每股现金流；不能用平均利润乘平均PE，也不能用平均股数换算。
    template=pairs[0][1]
    weighted={'research_date':template['research_date'],'scenario':'probability_weighted',
              'primary_return_metric':x['decision_policy']['return_metric'],
              'terminal_date':template['terminal_date'],'terminal_years':template['terminal_years'],'rows':[]}
    for key in ['terminal_equity','terminal_per_share','terminal_operating_equity','terminal_nonoperating_assets']:
        weighted[key]=sum(item['probability']*z[key] for item,z in pairs)
    for i,row in enumerate(template['rows']):
        assert all(z['rows'][i]['date']==row['date'] for _,z in pairs)
        out={'date':row['date'],'years_from_research':row['years_from_research']}
        for key in ['revenue','parent_operating_net_income','parent_operating_fcfe','dividend','dividend_per_share']:
            out[key]=sum(item['probability']*z['rows'][i][key] for item,z in pairs)
        weighted['rows'].append(out)
    c=x['common'];price=x['facts']['a_price']
    weighted['a_irr_of_expected_cashflows']=irr(weighted,price,c)
    weighted['probability_weighted_a_scenario_irr']=sum(item['probability']*irr(z,price,c) for item,z in pairs)
    weighted['a_expected_cumulative_return']=cumulative_return(weighted,price,c)
    weighted['cases']=[{'scenario':item['scenario'],'probability':item['probability'],
                       'representative_pe':item['representative_pe'],'terminal_equity':z['terminal_equity'],
                       'a_scenario_irr':irr(z,price,c)} for item,z in pairs]
    shares=bridge(x,x['scenarios']['base'])['initial_shares']
    weighted['price_return_relationship']=[{'target_return':rate,'entry_price':price_for_return(weighted,rate,c),
            'entry_equity':price_for_return(weighted,rate,c)*shares}
            for rate in x['decision_policy']['target_return_examples']]
    target=x['decision_policy']['selected_target_return']
    assert target is not None and target > -1
    buy_price=price_for_return(weighted,target,c)
    weighted['reasonable_buy']={'target_return':target,'return_metric':x['decision_policy']['return_metric'],
                                'source':x['decision_policy']['target_return_source'],
                                'entry_price':buy_price,'entry_equity':buy_price*shares}
    assert isclose(irr(weighted,buy_price,c),target,abs_tol=1e-10)
    # 期望现金流现值必须等于情景现值的加权和；平均IRR没有这一性质。
    for rate in [0,.12,.15,.20]:
        assert isclose(price_for_return(weighted,rate,c),
                       sum(item['probability']*price_for_return(z,rate,c) for item,z in pairs),rel_tol=1e-10)
    assert isclose(weighted['a_expected_cumulative_return'],
                   sum(item['probability']*cumulative_return(z,price,c) for item,z in pairs),abs_tol=1e-10)
    assert min(z['terminal_equity'] for _,z in pairs)<=weighted['terminal_equity']<=max(z['terminal_equity'] for _,z in pairs)
    return weighted


def calculate(x):
    self_checks(x)
    f,c=x['facts'],x['common']
    shares=bridge(x,x['scenarios']['base'])['initial_shares']
    market=(shares-f['registered_h'])*f['a_price']+f['registered_h']*f['h_price_hkd']*f['hkd_cny']
    scenarios={}
    for name,s in x['scenarios'].items():
        bounds=[]
        for pe in s['terminal_pe_range']:
            z=simulate(x,name,pe=pe)
            z['a_annual_return']=irr(z,f['a_price'],c)
            z['a_cumulative_return']=cumulative_return(z,f['a_price'],c)
            z['h_cny_annual_return_assuming_premium_converges']=irr(z,f['h_price_hkd']*f['hkd_cny'],c)
            z['whole_equity_annual_return_at_snapshot']=irr(z,market/shares,c)
            bounds.append(z)
        scenarios[name]={'pe_range':s['terminal_pe_range'],'bounds':bounds}
    base=scenarios['base']['bounds'];down=scenarios['downside']['bounds'][0]
    target_tables=[]
    for rate in x['decision_policy']['target_return_examples']:
        endpoints=[]
        for z in base:
            price=price_for_return(z,rate,c)
            endpoints.append({'terminal_pe':z['terminal_pe'],'entry_price':price,'entry_equity':price*shares,
                              'downside_annual_return':irr(down,price,c),
                              'downside_cumulative_return':cumulative_return(down,price,c)})
        target_tables.append({'illustrative_target_return':rate,'bounds':endpoints})
    sensitivities={}
    for label,key,value in [('repay_debt_at_start','repay_debt_at_start',True),
                            ('half_old_provisions','old_provision_reserve_fraction',.5),
                            ('no_remaining_buyback','remaining_buyback',0),
                            ('no_employee_transfer','employee_transfer_shares',0)]:
        y=deepcopy(x);y['common'][key]=value
        zs=[simulate(y,pe=pe) for pe in x['scenarios']['base']['terminal_pe_range']]
        sensitivities[label]={'terminal_equity_range':[z['terminal_equity'] for z in zs],
                              'a_return_range':[irr(z,f['a_price'],c) for z in zs]}
    for amount in [0,1500]:
        zs=[simulate(x,pe=pe,portfolio_override=amount) for pe in x['scenarios']['base']['terminal_pe_range']]
        sensitivities[f'parent_portfolio_{amount}']={'terminal_equity_range':[z['terminal_equity'] for z in zs],
                                                  'a_return_range':[irr(z,f['a_price'],c) for z in zs]}
    sensitivity_grid=[]
    for shift in [-.01,0,.01]:
        sensitivity_grid.append({'nopat_margin_shift':shift,'by_pe':[
            {'pe':pe,'terminal_equity':simulate(x,pe=pe,margin_shift=shift)['terminal_equity'],
             'a_annual_return':irr(simulate(x,pe=pe,margin_shift=shift),f['a_price'],c)}
            for pe in [12,15,20,25]]})
    weighted=probability_weighted_forecast(x)
    weighted['reasonable_buy']['downside_cumulative_return']=cumulative_return(down,weighted['reasonable_buy']['entry_price'],c)
    weight_sensitivities=[]
    for target in ['downside','upside']:
        cases=deepcopy(x['probability_assessment']['cases'])
        for item in cases:
            if item['scenario']=='base':item['probability']-=.10
            elif item['scenario']==target:item['probability']+=.10
        z=probability_weighted_forecast(x,cases)
        weight_sensitivities.append({'move_10pp_from_base_to':target,'terminal_equity':z['terminal_equity'],
                                    'a_irr_of_expected_cashflows':z['a_irr_of_expected_cashflows']})
    return {'research_date':x['research_date'],'currency':x['currency'],'amount_unit':'亿元',
            'method':x['valuation_policy']['method'],'current_fair_equity':None,'current_downside_equity':None,
            'missing_reason':'本次提供三年后概率加权价值预测及目标回报下的合理买入价，未单独估计当前合理价值',
            'selected_target_return':x['decision_policy']['selected_target_return'],'market_equity_at_snapshot':market,
            'historical_reconciliation':historical_reconciliation(x,market),
            'probability_weighted_forecast':weighted,'probability_weight_sensitivities':weight_sensitivities,
            'scenarios':scenarios,'price_return_relationship':target_tables,
            'a_required_terminal_pe_at_base_profit':{str(rate):required_pe(base[0],f['a_price'],c,rate) for rate in [0,.12,.15,.20]},
            'a_required_terminal_pe_at_downside_profit_for_break_even':required_pe(down,f['a_price'],c,0),
            'downside_break_even_equity':price_for_return(down,0,c)*shares,
            'base_two_year_delay_a_annual_return':[irr(delayed_realization(z),f['a_price'],c) for z in base],
            'base_dividend_tax_20pct_a_annual_return':[irr(z,f['a_price'],c,.2) for z in base],
            'sensitivities':sensitivities,'margin_and_multiple_grid':sensitivity_grid,
            'verification':'现金/组合/股份守恒、利息与偿债口径、PE与经营分离、IRR和盈亏平衡逆推、单位及延迟、概率归一和期望现金流检查通过；预测未经独立审阅'}


if __name__=='__main__':
    x=json.loads((HERE/'inputs.json').read_text())
    out=calculate(x)
    (HERE/'results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    weighted=out['probability_weighted_forecast']
    print(json.dumps({'expected_terminal_equity':round(weighted['terminal_equity']),
                      'expected_terminal_operating_profit':round(weighted['rows'][-1]['parent_operating_net_income']),
                      'irr_of_expected_cashflows':round(weighted['a_irr_of_expected_cashflows'],4),
                      'reasonable_buy':weighted['reasonable_buy']},
                     ensure_ascii=False,indent=2))
