"""CNY亿元、亿股；仅标准库；从脚本位置读取输入。"""
import json
from pathlib import Path
from datetime import date
P=Path(__file__).resolve().parent
x=json.loads((P/'inputs.json').read_text())
t=[(date.fromisoformat(d)-date.fromisoformat(x['start'])).days/365 for d in x['dates']]
n=x['shares']; price=x['price']; bf=x['buy_fee']; sf=x['sell_fee']; tax=x['dividend_tax']
def pv(c,r): return sum(v/(1+r)**a for a,v in zip(t,c))
def irr(c,p):
 lo,hi=-.99,5
 for _ in range(150):
  m=(lo+hi)/2
  if pv(c,m)>p*(1+bf):lo=m
  else:hi=m
 return (lo+hi)/2
rows=[]; ec=[0.,0.,0.]; ev=ep=0
for s in x['scenarios']:
 cash=x['opening_surplus']; div=[]; profits=[]; bridges=[]
 for revenue,margin in zip(s['revenue'],s['margin']):
  profit=revenue*margin; interest=cash*x['cash_yield']; fc=profit*s['conversion']+interest
  dividend=(profit+interest)*s['payout']; cash+=fc-dividend
  profits.append(profit); div.append(dividend/n*(1-tax)); bridges.append({'profit':profit,'interest':interest,'fcfe':fc,'dividend':dividend,'closing_surplus':cash})
 value=profits[-1]*s['pe']+cash
 c=div.copy(); c[-1]+=value/n*(1-sf)
 for i in range(3):ec[i]+=s['p']*c[i]
 ev+=s['p']*value; ep+=s['p']*profits[-1]
 rows.append(dict(name=s['name'],p=s['p'],profit=profits[-1],pe=s['pe'],value=value,terminal_price=value/n,dividends=div,bridge=bridges,cashflows=c,irr=irr(c,price),total_return=sum(c)/(price*(1+bf))-1))
limit=pv(ec,.18)/(1+bf)
for r in rows:
 r['irr_at_limit']=irr(r['cashflows'],limit);r['loss_at_limit']=sum(r['cashflows'])/(limit*(1+bf))-1
out=dict(expected_profit=ep,expected_terminal_value=ev,expected_terminal_price=ev/n,expected_cashflows=ec,irr=irr(ec,price),buy_limit=limit,buy_market_cap=limit*n,reference_market_cap=price*n,scenarios=rows,target_sensitivity={str(r):pv(ec,r)/(1+bf) for r in [.12,.15,.18,.20]},pe_shift_limit_per_turn=sum(s['p']*r['profit'] for s,r in zip(x['scenarios'],rows))/n*(1-sf)/(1.18**t[-1])/(1+bf))
# 继续持有以立即卖出的净额为机会成本；未来现金流已扣分红税及期末卖出费。
sell_pv=pv(ec,x['sell_target_return']); sell_price=sell_pv/(1-sf)
out['reasonable_sell']=dict(target_return=x['sell_target_return'],pricing_date=x['start'],
                           terminal_date=x['dates'][-1],price=sell_price,
                           equivalent_market_cap=sell_price*n,net_sale_proceeds=sell_pv,
                           return_metric='irr_of_expected_cashflows_on_net_sale_proceeds')
assert abs(irr(ec,sell_price*(1-sf)/(1+bf))-x['sell_target_return'])<1e-9
# 反推：固定期望分红、非经营资产，统一期末PE
ed=[sum(r['p']*r['dividends'][i] for r in rows) for i in range(3)]
net=sum(r['p']*r['bridge'][-1]['closing_surplus'] for r in rows)
for rate in [0,.18]:
 terminal=(price*(1+bf)-pv(ed,rate))*(1+rate)**t[-1]/(1-sf)*n
 out['required_pe_'+str(rate)]=(terminal-net)/ep
# 兑现延迟一年：前三次分红不变，期末价值推迟，第四年不额外假设分红
c=ec.copy();terminal=ev/n*(1-sf); c[-1]-=terminal
out['one_year_delay_pv18']=(pv(c,.18)+terminal/1.18**(t[-1]+1))/(1+bf)
# 发行10%新股，净募资保留至期末；不假定免费增长，分红总额不变
out['ipo_sensitivity']={}
for issue in [120,160,200]:
 diluted=[v/1.1 for v in ed]; diluted[-1]+=(ev+n*.1*issue*.98)/(n*1.1)*(1-sf)
 out['ipo_sensitivity'][str(issue)]={'limit':pv(diluted,.18)/(1+bf),'irr':irr(diluted,price)}
assert abs(sum(s['p'] for s in x['scenarios'])-1)<1e-9
assert abs(pv(ec,.18)-limit*(1+bf))<1e-8
(P/'results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='scenarios'},ensure_ascii=False,indent=2))
for r in rows: print(r['name'],r['profit'],r['value'],r['irr'],r['irr_at_limit'],r['loss_at_limit'])
