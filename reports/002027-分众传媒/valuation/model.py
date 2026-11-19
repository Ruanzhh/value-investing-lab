#!/usr/bin/env python3
"""分众传媒三年每股现金流模型。金额：亿元；股数：亿股；仅使用标准库。

从任意目录运行；默认只向 stdout 输出，不改文件。参数说明见同目录 README。
"""
import copy
import json
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent


def years(start, end):
    return (date.fromisoformat(end) - date.fromisoformat(start)).days / 365.25


def irr(price, payments, times, buy_fee):
    lo, hi = -0.95, 5.0
    for _ in range(160):
        r = (lo + hi) / 2
        pv = sum(c / (1 + r) ** t for c, t in zip(payments, times))
        if pv > price * (1 + buy_fee):
            lo = r
        else:
            hi = r
    return (lo + hi) / 2


def path(s, data):
    a = data['assets']
    liquid = (a['cash'] + a['wealth_products'] + a['deposits']
              - a['restricted_reserve'] - a['operating_cash']
              - a['minority_reserve'] + a['shuhe_receivable'] * s['shuhe_recovery']
              + a['stub_fcfe'])
    illiquid = a['other_investments'] * s['investment_recovery']
    acquired = s['acquired']
    shares = data['shares'] + (data['new_shares'] if acquired else 0)
    if acquired:
        liquid += (a['target_liquid'] - a['target_restricted']
                   - a['target_operating_cash'] - a['target_property_debt']
                   - a['target_minority_reserve'] - data['cash_consideration'])
    opening_liquid = liquid
    annual = []
    for i in range(3):
        revenue = s['revenue'][i]
        margin = (s['gross_margin'][i] - s['selling_ratio'][i]
                  - s['admin_ratio'] - s['research_ratio'] - s['sales_tax_ratio'])
        old_pretax = (revenue * margin - s['financial_cost'][i]
                      - s['credit_loss'][i] + s['subsidy'][i])
        old_np = old_pretax * (1 - s['tax']) - s['minority_profit'][i]
        target_pretax = 0
        amort = data['ppa_amortization'] if acquired else 0
        if acquired:
            target_pretax = (s['target_revenue'][i] * s['target_margin'][i]
                             + s['synergy'][i])
        # 目标业务税率单列；现有分众境外少数归属已在 old_np 扣除。
        # 亏损不预支现金退税。PPA摊销的递延税转回不是现金税盾。
        ppa_net_charge = amort * (1 - data['target_tax'])
        target_np = (target_pretax - max(target_pretax, 0)*data['target_tax']
                     - ppa_net_charge)
        profit = old_np + target_np
        # 此处只加回非租赁折旧摊销；租赁本金利息与利润表租赁费用差异另调。
        noncash = s['depreciation'][i] + ppa_net_charge
        capex = s['maintenance_capex'][i] + s['growth_capex'][i]
        fcfe = (profit + noncash - capex - s['working_capital_increase'][i]
                - s['lease_cash_gap'][i])
        investment_cash_income = max(liquid, 0) * data['net_cash_yield']
        dividend = max(profit, 0) * s['payout'][i]
        integration = s['integration_cash'][i] if acquired else 0
        liquid += fcfe + investment_cash_income - dividend - integration
        assert liquid >= 0, '预测需要外部融资，必须重新建模'
        annual.append(dict(profit=profit, old_profit=old_np, target_profit=target_np,
                           revenue=revenue + (s['target_revenue'][i] if acquired else 0),
                           fcfe=fcfe, dividend=dividend, dps=dividend/shares,
                           investment_cash_income=investment_cash_income,
                           integration_cash=integration, liquid_end=liquid))
    terminal_assets = liquid + illiquid
    terminal_equity = (annual[-1]['profit'] * s['pe'] + terminal_assets
                       + s.get('terminal_cash_adjustment', 0))
    price = terminal_equity / shares
    times = [years(data['date'], d) for d in data['payment_dates']]
    payments = [x['dps'] * (1-data['dividend_tax']) for x in annual]
    payments[-1] += price * (1-data['sell_fee'])
    return dict(id=s['id'], weight=s['weight'], shares=shares, pe=s['pe'],
                opening_liquid=opening_liquid, illiquid_value=illiquid,
                annual=annual, terminal_assets=terminal_assets,
                terminal_equity=terminal_equity, terminal_price=price,
                payments=payments,
                irr_at_reference=irr(data['reference_price'],payments,times,data['buy_fee']))


def calculate(data):
    assert abs(sum(s['weight'] for s in data['scenarios']) - 1) < 1e-9
    assert len({s['id'] for s in data['scenarios']}) == len(data['scenarios'])
    paths = [path(s, data) for s in data['scenarios']]
    times = [years(data['date'], d) for d in data['payment_dates']]
    weighted_payments = [sum(p['weight']*p['payments'][i] for p in paths) for i in range(3)]
    expected_dps = [sum(p['weight']*p['annual'][i]['dps'] for p in paths) for i in range(3)]
    expected_profit = [sum(p['weight']*p['annual'][i]['profit'] for p in paths) for i in range(3)]
    terminal_equity = sum(p['weight']*p['terminal_equity'] for p in paths)
    terminal_price = sum(p['weight']*p['terminal_price'] for p in paths)
    pv = lambda r: sum(c/(1+r)**t for c,t in zip(weighted_payments,times))
    buy = pv(data['buy_return'])/(1+data['buy_fee'])
    sell = pv(data['sell_return'])/(1-data['sell_fee'])
    for p in paths:
        p['irr_at_buy_limit'] = irr(buy,p['payments'],times,data['buy_fee'])
        p['total_return_at_reference'] = sum(p['payments'])/(data['reference_price']*(1+data['buy_fee']))-1
        p['total_return_at_buy_limit'] = sum(p['payments'])/(buy*(1+data['buy_fee']))-1
    # 达到指定收益所需的加权期末每股价；不能以平均PE乘平均利润。
    def needed_terminal_price(r, price):
        dist_pv = sum(d*(1-data['dividend_tax'])/(1+r)**t for d,t in zip(expected_dps,times))
        return (price*(1+data['buy_fee'])-dist_pv)*(1+r)**times[-1]/(1-data['sell_fee'])
    # 所有路径PE同时变动一倍，所需额外PE；现金及股数保持各路径口径。
    eps = sum(p['weight']*p['annual'][-1]['profit']/p['shares'] for p in paths)
    needed18 = needed_terminal_price(data['buy_return'],data['reference_price'])
    return dict(buy_price=buy, sell_price=sell,
                buy_equity_equivalent=buy*data['shares'],
                sell_equity_equivalent=sell*data['shares'],
                reference_equity=data['reference_price']*data['shares'],
                expected_profit=expected_profit, expected_dps=expected_dps,
                expected_terminal_equity=terminal_equity,
                expected_terminal_price=terminal_price,
                old_holder_equivalent_terminal_equity=terminal_price*data['shares'],
                expected_irr=irr(data['reference_price'],weighted_payments,times,data['buy_fee']),
                required_terminal_price_for_18=needed18,
                required_terminal_price_for_breakeven=needed_terminal_price(0,data['reference_price']),
                uniform_pe_increase_for_18=(needed18-terminal_price)/eps,
                paths=paths)


def main():
    data = json.loads((HERE/'inputs.json').read_text())
    result = calculate(data)
    sensitivities = {}
    for label in ['pe_minus_2','investment_zero','tax_25pct','three_year_capex_plus_2','persistent_capex_plus_2','payout_60pct','operating_cash_plus_10','stub_zero','bear_weight_plus_10pp','synergy_zero','no_acquisition_all','only_9002_percent']:
        d=copy.deepcopy(data)
        if label=='operating_cash_plus_10': d['assets']['operating_cash']+=10
        if label=='stub_zero': d['assets']['stub_fcfe']=0
        if label=='only_9002_percent':
            # 仅90.02%完成：现金少付5.055755亿，剥离9.98%的目标资产/盈利与协同。
            # 全集团协同均按9.98%扣减是该边界测试的简化保守归属。
            d['cash_consideration']-=5.055755
            for k in ['target_liquid','target_restricted','target_operating_cash','target_property_debt','target_minority_reserve']:
                d['assets'][k]*=.9002
            d['ppa_amortization']*=.9002
        for s in d['scenarios']:
            if label=='pe_minus_2': s['pe']-=2
            if label=='investment_zero': s['investment_recovery']=0
            if label=='tax_25pct': s['tax']=.25
            if label in ['three_year_capex_plus_2','persistent_capex_plus_2']:
                s['maintenance_capex']=[x+2 for x in s['maintenance_capex']]
                if label=='persistent_capex_plus_2':
                    s['terminal_cash_adjustment']=-2*s['pe']/.9
            if label=='payout_60pct': s['payout']=[.6]*3
            if label=='bear_weight_plus_10pp':
                if s['id']=='base': s['weight']-=.1
                if s['id']=='bear': s['weight']+=.1
            if label=='synergy_zero': s['synergy']=[0]*3
            if label=='no_acquisition_all':
                s['acquired']=False
                # 剥离标的相应资本开支和折旧；旧业务假设保持。
                s['depreciation']=[max(0,x-.6) for x in s['depreciation']]
                s['maintenance_capex']=[max(0,x-.6) for x in s['maintenance_capex']]
            if label=='only_9002_percent':
                s['target_revenue']=[x*.9002 for x in s['target_revenue']]
                s['synergy']=[x*.9002 for x in s['synergy']]
        r=calculate(d)
        sensitivities[label]={k:r[k] for k in ['buy_price','sell_price','expected_irr']}
    # 价值兑现延期：第3年以后无新增分配、期末价值不增加，推迟两年实现。
    # 这是冻结价值压力测试，避免免费延长增长预测。
    times=[years(data['date'],x) for x in data['payment_dates']]+[years(data['date'],'2031-11-19')]
    payments=[x*(1-data['dividend_tax']) for x in result['expected_dps']]
    payments.append(result['expected_terminal_price']*(1-data['sell_fee']))
    sensitivities['two_year_delay_frozen_value']={
        'irr_at_reference':irr(data['reference_price'],payments,times,data['buy_fee']),
        'irr_at_buy_limit':irr(result['buy_price'],payments,times,data['buy_fee'])}
    result['sensitivities']=sensitivities
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
