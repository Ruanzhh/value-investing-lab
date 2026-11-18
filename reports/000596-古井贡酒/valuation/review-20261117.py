"""重估前审查：原时点压力复算，不覆盖正式估值。"""
import copy
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
m = runpy.run_path(str(ROOT / 'calculate.py'))
x = json.loads((ROOT / 'inputs.json').read_text())
old = json.loads((ROOT / 'results.json').read_text())['expected']

def evaluate(data):
    z = m['run'](data)['expected']
    return dict(buy=z['a_buy_price'], sell=z['reasonable_sell']['price'],
                irr_at_original_price=z['a_price_irr'], terminal_equity=z['terminal_value'],
                annual_total_profit=[row['total_np'] for row in z['years']])

out = {'status': '原时点条件压力测试，不是新正式估值；金额亿元，每股元',
       'original_pricing_date': x['research_date'], 'original_price': x['market']['a_price'],
       'original': evaluate(x), 'tests': {}}
assert abs(out['original']['buy'] - old['a_buy_price']) < 1e-9
assert abs(out['original']['sell'] - old['reasonable_sell']['price']) < 1e-9
for shift in [.02, .04]:
    y = copy.deepcopy(x)
    for case in y['business_cases'].values():
        case['selling_ratio'] = [v + shift for v in case['selling_ratio']]
    out['tests'][f'all_selling_ratio_plus_{shift}'] = evaluate(y)
y = copy.deepcopy(x)
y['business_cases']['recovery']['selling_ratio'] = [.33, .33, .33]
out['tests']['ordinary_recovery_selling_ratio_stays33pct'] = evaluate(y)
for profit in [23.1, 20]:
    y = copy.deepcopy(x)
    y['fy2026_profit_estimate'] = profit
    out['tests'][f'fy2026_profit_only_{profit}'] = evaluate(y)
    # 原模型此字段只控制分红。再用同额归母现金损失检查一次性冲击，
    # 不能把单改分红基数的微小影响说成经营下滑没有影响。
    y['liquidity']['sep30_to_research_net_change_assumption'] -= x['fy2026_profit_estimate'] - profit
    out['tests'][f'fy2026_profit_and_equal_cash_loss_{profit}'] = evaluate(y)
for key, delta in [('nwc_increase', 5), ('growth_capex', 5)]:
    y = copy.deepcopy(x)
    for case in y['business_cases'].values():
        case[key] = [v + delta for v in case[key]]
    out['tests'][f'all_annual_{key}_plus5'] = evaluate(y)
y = copy.deepcopy(x)
y['initial_dividend']['date'] = '2027-03-31'
out['tests']['interim_dividend_delayed_90days'] = evaluate(y)
out['broker_2026_2028_parent_profit'] = {
    'guotai_haitong_eps_times_shares': [v*x['shares'] for v in [4.37, 5.99, 7.03]],
    'china_merchants_eps_times_shares': [v*x['shares'] for v in [4.37, 4.96, 5.2]],
    'soochow': [24.3, 26.5, 29.6]}
out['time_passage_only_buy_nov17'] = out['original']['buy'] * 1.18**(10/365.25)
(ROOT / 'review-20261117.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(out, ensure_ascii=False, indent=2))
