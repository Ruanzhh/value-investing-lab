#!/usr/bin/env python3
"""Dry-run: load existing live cards (read-only), adapt legacy fields that map 1:1, report v3 gaps.
Never writes cards. Output only to workflow-v3/dryrun/."""
import json,glob,os,re,sys,csv,collections
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,'..'); sys.path.insert(0,HERE)
import validate_anchors as V
RUNS=os.path.join(ROOT,'..','workflow','runs')
routing_rows=list(csv.DictReader(open(os.path.join(ROOT,'master','ROUTING.csv'),encoding='utf-8')))
by_num={r['code'].split('.')[0]:r for r in routing_rows}
card_req=V.load_schema('card')['required']; plug_req=V.load_schema('plugin')['required']
def num(x):
    if isinstance(x,(int,float)): return x
    if isinstance(x,dict):
        for k in('value','fv3','FV3','fv3_ps','per_share','fv3_per_share','total','base','close','price','B20','b20'):
            if isinstance(x.get(k),(int,float)): return x[k]
def adapt(d,run):
    m=re.match(r'([a-z_\-]+?)-(\d{5,6})-(\d{8})',run); code=m.group(2) if m else None
    r=by_num.get(code) or {}
    fv=d.get('fv3_by_scenario') or {}
    if isinstance(fv,dict) and 'base' not in fv and isinstance(fv.get('per_share'),dict): fv=fv['per_share']
    def g(k): return num(fv.get(k)) if isinstance(fv,dict) else None
    ep=d.get('exit_pe') or {}; ch=ep.get('chosen') if isinstance(ep,dict) else None
    gr=d.get('grade'); 
    c={'ticker':r.get('code'),'name':r.get('name') or d.get('name'),'as_of':d.get('as_of'),
       'price':num(d.get('price')) if d.get('price') is not None else num((d.get('price_snapshot') or {}) if isinstance(d.get('price_snapshot'),dict) else None),
       'price_date':d.get('price_date'),'business_model':r.get('sub'),
       'method_by_model':None,'method_mismatch':(r.get('mismatch')=='是') if r else None,
       'exit_date_convention':d.get('exit_date_convention'),
       'exit_multiple':({'kind':'PE','bear':ch.get('bear'),'base':ch.get('base'),'bull':ch.get('bull'),'multiple_basis':ep.get('multiple_basis'),'window':ep.get('source')} if isinstance(ch,dict) else None),
       'grade':({'display':gr.get('value'),'quality_grade':d.get('quality_grade') or gr.get('quality_grade'),'confidence':d.get('confidence') or gr.get('confidence')} if isinstance(gr,dict) else ({'display':gr,'quality_grade':d.get('quality_grade'),'confidence':d.get('confidence')} if gr else None)),
       'hurdle':d.get('hurdle') and {'primary_pct':None,'secondary_pct':None},
       'FV3':({'bear':g('bear'),'base':g('base'),'bull':g('bull')} if fv else None),
       'dps_min3':d.get('dps_min3'),'buy_point':None,'return_sell':None,
       'fragility':None,'position_band':d.get('position_band'),'plugin_output_ref':None,'validate_report':None,'review':None,
       'forecast_ledger_entries':None,'anchor_trace':None}
    if isinstance(c.get('grade'),dict) and None in c['grade'].values(): pass
    return c,code,r
def run():
    files=[f for f in glob.glob(os.path.join(RUNS,'**','valuation_decision.json'),recursive=True) if '_backup' not in f and '_r7_scratch' not in f and '.bak' not in f]
    res=[];miss_card=collections.Counter();miss_plug=collections.Counter();fails=collections.Counter()
    for f in sorted(files):
        run_id=os.path.relpath(f,RUNS).split(os.sep)[0]
        try: d=json.load(open(f,encoding='utf-8'))
        except Exception as e: res.append({'run':run_id,'error':str(e)}); continue
        c,code,r=adapt(d,run_id)
        mc=[k for k in card_req if c.get(k) is None or (isinstance(c.get(k),dict) and any(v is None for v in c[k].values()))]
        mp=[k for k in plug_req if k not in d]  # legacy cards carry no plugin_output
        o=V.validate({k:v for k,v in c.items() if v is not None},'card',{})
        hard=[x for x in o if x['level']=='FAIL' and not x['anchor'].startswith('schema')]
        for k in mc: miss_card[k]+=1
        for k in mp: miss_plug[k]+=1
        for x in hard: fails[x['anchor']]+=1
        res.append({'run':run_id,'path':os.path.relpath(f,os.path.join(ROOT,'..')),'ticker':c['ticker'],'name':c['name'],'business_model':c['business_model'],'routed':bool(r),
                    'card_missing':mc,'card_missing_n':len(mc),'plugin_missing_n':len(mp),'anchor_fails':[x['anchor'] for x in hard]})
    latest={}
    for x in res:
        if x.get('ticker'): 
            if x['ticker'] not in latest or x['run']>latest[x['ticker']]['run']: latest[x['ticker']]=x
    summ={'cards_scanned':len(res),'parse_errors':sum('error' in x for x in res),'routed_cards':sum(bool(x.get('routed')) for x in res),
          'unrouted_cards':[x['run'] for x in res if not x.get('routed')],'routed_names_with_card':len(latest),
          'routed_names_without_card':[r['name'] for r in routing_rows if r['code'] not in latest],
          'v3_ready_cards':sum(1 for x in res if x.get('card_missing_n')==0 and not x.get('anchor_fails')),
          'card_field_missing_counts':dict(miss_card.most_common()),'plugin_output_missing_counts':dict(miss_plug.most_common()),'anchor_fail_counts':dict(fails.most_common()),
          'latest_per_name':{k:{'run':v['run'],'model':v['business_model'],'card_missing_n':v['card_missing_n'],'anchor_fails':v['anchor_fails']} for k,v in sorted(latest.items())}}
    os.makedirs(os.path.join(ROOT,'dryrun'),exist_ok=True)
    json.dump({'summary':summ,'cards':res},open(os.path.join(ROOT,'dryrun','dryrun_report.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
    return summ
if __name__=='__main__':
    s=run(); print(json.dumps({k:v for k,v in s.items() if k!='latest_per_name'},ensure_ascii=False,indent=1))
