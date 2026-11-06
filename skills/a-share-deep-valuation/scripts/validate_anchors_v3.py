#!/usr/bin/env python3
"""v3 anchor validator (draft r4, 2026-10-30; read-only; FRAMEWORK only).
FAIL = hard gate; DISPLAY = R4–R6 / EXT.2–EXT.3 (promotion = USER decision V§20-4).
Usage: validate_anchors.py --kind plugin|card file.json [...] | --selftest | --mutation-tests
r2: D1–D16. r3 (t428u): S4c / RC1–RC5 / dual-method / range-buy.
r4 (t430u): S5a→S4c→S5b loop; B20_issued conditional; plugin dual-method|exception;
n_analysts / RC3 prior require round_delta; EXT.2 DISPLAY-assist only.
Threshold numbers are PROVISIONAL_UNBACKTESTED placeholders — values unchanged."""
import json,sys,os,re,datetime as dt,statistics as st
HERE=os.path.dirname(os.path.abspath(__file__)); SCH=os.path.join(HERE,'..','schema')
VERSION='v3-draft-r4-20261030'
WINDOW_KINDS={'PE','SOTP','EV_EBIT','EV_EBITDA','PS'}   # any historical-window multiple
def load_schema(kind): return json.load(open(os.path.join(SCH,f'{"plugin_output" if kind=="plugin" else "card"}.v3.schema.json'),encoding='utf-8'))
def F(o,a,l,m): o.append({'anchor':a,'level':l,'msg':m})
def num(x): return isinstance(x,(int,float)) and not isinstance(x,bool)
def close(a,b,tol=0.01): return abs(a-b)<=tol*max(abs(a),abs(b),1e-9)
def _check(node,sch,path,o):
    if 'const' in sch and node!=sch['const']: F(o,'schema'+path,'FAIL',f'{path} must be {sch["const"]!r}, got {node!r}')
    if 'enum' in sch and node not in sch['enum']: F(o,'schema'+path,'FAIL',f'{path}={node!r} not in enum')
    if isinstance(node,dict):
        for k in sch.get('required',[]):
            if k not in node or node[k] is None: F(o,'schema.missing','FAIL',f'missing {path}/{k}')
        for k,s in sch.get('properties',{}).items():
            if k in node and node[k] is not None: _check(node[k],s,f'{path}/{k}',o)
        for c in sch.get('allOf',[]):
            cond=c.get('if',{}).get('properties',{})
            if all(isinstance(node.get(k),str) and re.search(v.get('pattern','.*'),node.get(k,'')) for k,v in cond.items()):
                _check(node,c['then'],path,o)
    if isinstance(node,list):
        if len(node)<sch.get('minItems',0): F(o,'schema.minItems','FAIL',f'{path} needs ≥{sch["minItems"]} items')
        if 'items' in sch: [_check(x,sch['items'],f'{path}[{i}]',o) for i,x in enumerate(node)]
def schema_check(c,kind,o): _check(c,load_schema(kind),'',o)
def ma(c): return c.get('multiple_anchor') or c.get('exit_multiple') or {}
def D(s): return dt.date.fromisoformat(s[:10])

# ---- D5: FY3 rule (A.L1.exit_date_convention r2) ----
def fy3_rule(as_of,fye_mmdd='12-31'):
    """FY3 = fiscal year whose year-end is closest to as_of+3y (tie → later); n = actual years as_of→FY3 YE."""
    a=D(as_of); m,d=map(int,fye_mmdd.split('-')); tgt=a+dt.timedelta(days=round(3*365.25))
    cands=[dt.date(y,m,d) for y in range(a.year+1,a.year+5)]
    ye=min(cands,key=lambda x:(abs((x-tgt).days),-x.toordinal()))
    return ye.year,round((ye-a).days/365.25,3)
def r1(c,o):
    e=ma(c); conv=c.get('exit_date_convention',e.get('exit_date_convention'))
    if conv!='FY3_yearend': F(o,'A.L1.exit_date_convention','FAIL','exit_date_convention must be FY3_yearend')
    basis=e.get('multiple_basis'); kind=e.get('kind','PE')
    if kind in WINDOW_KINDS and basis not in ('same_FY','SOTP_component_same_FY','EV_same_FY'):
        F(o,'A.L1.exit_multiple.basis','FAIL',f'{kind} multiple_basis={basis} (need same-FY basis)')
    as_of=c.get('as_of')
    if as_of:
        fy3,n=fy3_rule(as_of,c.get('fiscal_year_end','12-31'))
        if e.get('fy3') is None or e.get('n_years') is None: F(o,'A.L1.exit_date_convention.fy3','FAIL','multiple_anchor.fy3 and n_years required (V§3-1 r2)')
        else:
            if str(e['fy3']).replace('FY','')!=str(fy3): F(o,'A.L1.exit_date_convention.fy3','FAIL',f"fy3={e['fy3']} but rule gives FY{fy3}")
            if not close(float(e['n_years']),n,0.005): F(o,'A.L1.exit_date_convention.n','FAIL',f"n_years={e['n_years']} but rule gives {n}")

# ---- D1/D4/D6: snapshot table for every window multiple ----
def r_snap(c,o):
    e=ma(c); kind=e.get('kind','PE')
    if kind not in WINDOW_KINDS: return
    S=e.get('snapshots')
    if not S: F(o,'A.L1.exit_multiple.snapshots','FAIL',f'{kind} window multiple without snapshot table (fy, price_date, profit_fy, …)'); return
    fye=c.get('fiscal_year_end','12-31'); vals=[]
    for s in S:
        need=('fy','price_date','profit_fy','price','price_basis','shares_mn','shares_basis','fx_date','value')
        miss=[k for k in need if s.get(k) is None]
        if miss: F(o,'A.L1.exit_multiple.snapshots','FAIL',f"snapshot {s.get('fy')} missing {miss}"); continue
        pdte=D(s['price_date']); fy=int(str(s['fy']).replace('FY',''))
        if int(str(s['profit_fy']).replace('FY',''))!=fy: F(o,'A.L1.exit_multiple.basis','FAIL',f"snapshot FY{fy}: profit_fy={s['profit_fy']} ≠ fy (lagged/led multiple)")
        ye=dt.date(fy,*map(int,fye.split('-')))
        if abs((pdte-ye).days)>10: F(o,'A.L1.exit_multiple.basis','FAIL',f"snapshot FY{fy}: price_date {s['price_date']} not at FY{fy} year-end ±10d")
        if s['price_basis']!='unadjusted': F(o,'A.L1.exit_multiple.input_hygiene','FAIL',f"FY{fy}: price_basis={s['price_basis']} (need unadjusted close)")
        if s['shares_basis'] not in ('YE_issued','period_weighted_YE'): F(o,'A.L1.exit_multiple.input_hygiene','FAIL',f"FY{fy}: shares_basis={s['shares_basis']} (need YE_issued)")
        if s.get('fx') is not None and abs((D(s['fx_date'])-pdte).days)>5: F(o,'A.L1.exit_multiple.input_hygiene','FAIL',f"FY{fy}: fx_date {s['fx_date']} ≠ price_date")
        vals.append(s['value'])
    # r3/RC1: trough exclusion structure — base/bull from non-excluded only
    gap=(c.get('trough_exclusion') or {}).get('trough_margin_gap_pp', 3)  # PROVISIONAL_UNBACKTESTED
    margins=[(s,s.get('core_margin')) for s in S if num(s.get('core_margin'))]
    if len(margins)>=2:
        for s,mrg in margins:
            others=[x for y,x in margins if y is not s and num(x)]
            if others and mrg < min(others) - gap:
                if not s.get('exclude_from_base_bull'):
                    F(o,'A.L1.exit_multiple.trough_exclusion','FAIL',f"FY{s.get('fy')}: core_margin {mrg} is trough (>{gap}pp below peers) but exclude_from_base_bull not set (RC1)")
    base_S=[s for s in S if not s.get('exclude_from_base_bull')]
    base_vals=[s['value'] for s in base_S if num(s.get('value'))]
    if len(vals)<4 and not e.get('window_exception_reason'): F(o,'A.L1.exit_multiple.window','FAIL',f'{len(vals)} snapshots <4 (V§3-3)')
    use_vals=base_vals if base_vals else vals
    if len(use_vals)>=3:
        so=sorted(use_vals); m=st.median(so)
        # trim on chronological non-excluded
        chron=[s['value'] for s in sorted(base_S or S,key=lambda s:int(str(s['fy']).replace('FY',''))) if num(s.get('value'))]
        if len(chron)>=3:
            t1=st.median(chron[1:]); t2=st.median(chron[:-1])
            if max(abs(t1/m-1),abs(t2/m-1))>0.10 and not e.get('trim_fail_reason'): F(o,'A.L1.exit_multiple.window','FAIL',f'trim test: drop-first {t1:.2f}/drop-last {t2:.2f} vs median {m:.2f} >10%')
        b=e.get('base',e.get('value'))
        if num(b) and not close(b,m,0.01) and not e.get('base_not_median_reason'): F(o,'A.L1.exit_multiple.window','FAIL',f'base {b} ≠ non-excluded snapshot median {m:.2f} (RC1)')
    if vals and (c.get('business_model')=='M8' or e.get('bear_rule')=='min_snapshot'):
        bear=e.get('bear')
        if not num(bear) or bear>min(vals)+1e-6: F(o,'A.L1.bear_stress.multiple','FAIL',f'bear multiple {bear} > lowest valid snapshot {min(vals):.2f}')
    # r3/RC2: trough years excluded from base cannot be exempted from bear floor
    excl=[s for s in S if s.get('exclude_from_base_bull')]
    bm=c.get('bear_margin') or {}
    if excl and bm:
        trough_margins=[s['core_margin'] for s in excl if num(s.get('core_margin'))]
        if trough_margins and num(bm.get('bear')):
            floor=min(trough_margins)
            # exemption cannot lift above trough floor
            if bm['bear']>floor+1e-9:
                F(o,'A.L1.bear_stress.trough_floor','FAIL',f"bear margin {bm['bear']} > trough-excluded floor {floor} (RC2: cannot exempt trough used for RC1 exclusion)")

# ---- M8 (sub/M8 hard asserts) ----
def r_m8(c,o):
    if c.get('business_model')!='M8': return
    e=ma(c)
    if e.get('kind')!='SOTP': F(o,'A.L2.M8','FAIL','M8 multiple_anchor.kind must be SOTP')
    if e.get('total_mcap_pe_used') is not False: F(o,'A.L3.M8.no_double_count','FAIL','total_mcap_pe_used must be explicitly false (total-mcap PE × core NI + portfolio = double count)')
    for s in e.get('snapshots') or []:
        k=('mcap_report_ccy','portfolio_deduct','net_cash','core_ni')
        if any(not num(s.get(x)) for x in k): F(o,'A.L3.M8.core_pe_basis','FAIL',f"FY{s.get('fy')}: snapshot needs {k}"); continue
        mc=s['price']*s['shares_mn']/1000/(s.get('fx') or 1)
        if not close(mc,s['mcap_report_ccy'],0.005): F(o,'A.L3.M8.core_pe_basis','FAIL',f"FY{s['fy']}: mcap {s['mcap_report_ccy']} ≠ price×YE shares/FX {mc:.1f}")
        v=(s['mcap_report_ccy']-s['portfolio_deduct']-s['net_cash'])/s['core_ni']
        if not close(v,s['value'],0.01): F(o,'A.L3.M8.core_pe_basis','FAIL',f"FY{s['fy']}: core PE {s['value']} ≠ recomputed {v:.2f}")
    comp=c.get('FV3_components') or {}
    if not comp: F(o,'A.L3.M8.sotp_build','FAIL','FV3_components{bear,base,bull} required'); return
    for k in ('bear','base','bull'):
        x=comp.get(k) or {}
        need=('core_ni3','core_pe','portfolio_after_disc','net_cash','fx_price_ccy_per_report','shares_mn')
        if any(not num(x.get(n)) for n in need): F(o,'A.L3.M8.sotp_build','FAIL',f'FV3_components.{k} needs {need}'); continue
        fv=(x['core_ni3']*x['core_pe']+x['portfolio_after_disc']+x['net_cash'])*x['fx_price_ccy_per_report']/x['shares_mn']*1000
        if not close(fv,(c.get('FV3') or {}).get(k,0),0.005): F(o,'A.L3.M8.sotp_build','FAIL',f'FV3.{k} {c["FV3"].get(k)} ≠ recomputed {fv:.2f}')
    if num((comp.get('bear') or {}).get('core_pe')) and e.get('snapshots'):
        mn=min(s['value'] for s in e['snapshots'] if num(s.get('value')))
        if comp['bear']['core_pe']>mn+1e-6: F(o,'A.L1.bear_stress.multiple','FAIL',f"bear core PE {comp['bear']['core_pe']} > min snapshot {mn:.2f}")
    pf=c.get('portfolio') or {}
    if pf.get('smoothing_rule')!='min(latest, trailing_4Q_avg)': F(o,'A.L3.M8.portfolio_smoothing','FAIL','listed leg smoothing must be min(latest, trailing_4Q_avg)')
    if pf.get('fy3_treatment')!='hold_latest_constant': F(o,'A.L3.M8.fy3_balance','FAIL','portfolio/net cash at FY3 must be hold_latest_constant (D15)')

def r_drivers(c,o):
    t=[d for d in c.get('drivers') or [] if d.get('is_top2') is True]
    if len(t)!=2: F(o,'A.L1.fragility.top2','FAIL',f'need exactly 2 is_top2 drivers, got {len(t)}')
def r_base_year(c,o):
    b=c.get('base_year') or {}; m=b.get('method')
    if m not in ('9M+priorQ4','TTM_4Q','FY_actual'): F(o,'A.L1.base_year','FAIL',f'base_year.method={m} not in 9M+priorQ4|TTM_4Q|FY_actual'); return
    if m=='FY_actual' and not b.get('fy_actual_reason'): F(o,'A.L1.base_year','FAIL','FY_actual base requires fy_actual_reason (V§2-2 r2: use TTM_4Q when 9M unavailable)')
def r2(c,o):
    m=c.get('business_model') or ''
    if m.startswith(('M5','M7')):
        r=c.get('roe') or {}; need={'avg3','latest_annualized','base','bear','worst_hist'}
        if not need<=set(r): F(o,'A.L3.M5.roe_take_lower','FAIL',f'missing roe fields {sorted(need-set(r))}')
        else:
            lo=min(r['avg3'],r['latest_annualized'])
            if r['base']>lo+1e-9: F(o,'A.L3.M5.roe_take_lower','FAIL',f"base ROE {r['base']} > min(avg3,latest)={lo}")
            if r['bear']>r['worst_hist']+1e-9: F(o,'A.L3.M5.bear_roe','FAIL',f"bear ROE {r['bear']} > worst hist {r['worst_hist']}")
        b=c.get('bvps') or {}
        if b.get('date_rule')!='latest_reported_before_price': F(o,'A.L3.M5.bvps_basis','FAIL','BVPS date_rule must be latest_reported_before_price')
    s=c.get('FV3') or {}
    if all(num(s.get(k)) for k in('bear','base','bull')) and not s['bear']<=s['base']<=s['bull']: F(o,'A.L1.scenario.order','FAIL','FV3 must be bear<=base<=bull')
    bm=c.get('bear_margin')
    if bm:
        ok=bm['bear']<=bm['worst_in_window']+1e-9 or (bm.get('exemption_reason') and bm['bear']<=bm['worst_last3']+1e-9)
        if not ok: F(o,'A.L1.bear_stress.margin','FAIL',f"bear margin {bm['bear']} > worst-in-window {bm['worst_in_window']} (exemption floor worst_last3 {bm.get('worst_last3')})")
def r3(c,o):
    p=c.get('profit_base')
    if p is None: return
    for k in('reported_ni','core_ni','cfo','avg_total_assets','maint_capex','da'):
        if not num(p.get(k)): F(o,'A.L1.profit_base','FAIL',f'profit_base.{k} missing/non-numeric'); return
    acc=(p['reported_ni']-p['cfo'])/p['avg_total_assets']
    if acc>0.10: F(o,'A.L1.profit_base.quality','FAIL',f'accrual {acc:.3f}>0.10 → NI3 haircut required')
    elif acc>0.05: F(o,'A.L1.profit_base.quality','DISPLAY',f'accrual {acc:.3f} watch band')
    fs=p.get('piotroski')
    if fs is not None and fs<=3: F(o,'A.L1.profit_base.quality','FAIL',f'F-score {fs}<=3 → haircut required')
    h=p.get('hedge_fx_addback',0); cap=p.get('hedge_fx_cap')
    if h and cap is None: F(o,'A.L1.profit_base.hedge_fx','FAIL','hedge add-back without cap')
    elif cap is not None and h>cap+1e-9: F(o,'A.L1.profit_base.hedge_fx','FAIL',f'hedge add-back {h}>cap {cap}')
    if p.get('sbc_added_back_in_core'):
        if not num(p.get('sbc')) or p.get('sbc_treatment') not in ('deducted_in_OE','deducted_in_NI3','sensitivity_same_basis_multiple'):
            F(o,'A.L1.profit_base.sbc','FAIL','core adds back SBC → sbc value + sbc_treatment required (V§2-3 r2)')
    # r3/RC5: ban deduct-only SBC headline (mismatched basis)
    if p.get('sbc_deduct_only_B20') is not None or c.get('sbc_deduct_only_B20') is not None:
        F(o,'A.L1.profit_base.sbc_both_sides','FAIL','sbc_deduct_only_B20 banned (RC5); publish sbc_sensitivity_both_sides only')
    if p.get('maint_capex_basis') not in ('disclosed','DA_proxy','DA_proxy_capped_capex'): F(o,'A.L1.profit_base.maint_capex','FAIL','maint_capex_basis required (disclosed|DA_proxy|DA_proxy_capped_capex)')
def r_route(c,o,routing):
    t=c.get('ticker'); m=c.get('business_model')
    if t in routing and m and m!=routing[t] and not c.get('model_change_reason'): F(o,'A.L1.routing','FAIL',f'business_model {m} ≠ routing {routing[t]} without model_change_reason')
    if c.get('method_mismatch') is True: F(o,'A.L1.routing.method_mismatch','FAIL','method_mismatch=true → no formal card')

# ---- R4–R6 DISPLAY (D2/D10): inputs under display_checks ----
def reverse_dcf(dc,model):
    """Return implied NI3 (report ccy, bn) s.t. B20 == price, and its CAGR vs ni0. All money in bn, shares in mn."""
    px,h,n,dps=dc['price'],dc['hurdle_pct']/100,dc['n_years'],dc.get('dps_min3',0)
    eq_price_ccy=(px*(1+h)**n-n*dps)*dc['shares_mn']/1000           # bn, price ccy
    eq=eq_price_ccy/dc['fx_price_ccy_per_report']                     # bn, report ccy
    if model=='M8': eq-=dc['portfolio_after_disc']+dc['net_cash']
    elif model.startswith(('M5','M7')): return None                  # PB-ROE: see reverse_roe
    ni3=eq/dc['multiple_base']
    return ni3,((ni3/dc['ni0'])**(1/n)-1)*100 if ni3>0 else None
def reverse_roe(dc):
    px,h,n,dps=dc['price'],dc['hurdle_pct']/100,dc['n_years'],dc.get('dps_min3',0)
    return (px*(1+h)**n-n*dps)/dc['pb_base']/dc['bvps3_per_unit_roe'] if dc.get('bvps3_per_unit_roe') else None
def r456(c,o):
    dc=c.get('display_checks') or {}
    n0,n3,n=dc.get('ni0'),dc.get('ni3_base'),dc.get('n_years',3)
    if num(n0) and num(n3) and n0>0 and n3>0:
        g=((n3/n0)**(1/n)-1)*100; F(o,'A.L1.base_rate_prior','DISPLAY',f'NI3 CAGR {g:.1f}% vs Base Rate Book 3y sales median 5.4%'+(' — ≥15% tail: written evidence' if g>=15 else ''))
    if num(dc.get('g_pct')) and dc.get('ronic_pct'): F(o,'A.L1.consistency.roic_g','DISPLAY',f"g/RONIC={dc['g_pct']/dc['ronic_pct']:.2f}")
    need=('price','hurdle_pct','n_years','shares_mn','fx_price_ccy_per_report','multiple_base','ni0')
    if all(num(dc.get(k)) for k in need):
        r=reverse_dcf(dc,c.get('business_model') or '')
        if r and r[1] is not None: F(o,'A.L1.reverse_dcf','DISPLAY',f'price implies NI3 {r[0]:.1f}bn ({c.get("currency_report","report ccy")}), CAGR {r[1]:.1f}%/yr over {n}y at h={dc["hurdle_pct"]}%')
        if r and (r[1] is None or not (-30<r[1]<60)) and not dc.get('reverse_dcf_sanity_override'): F(o,'A.L1.reverse_dcf.sanity','FAIL',f'reverse DCF implied NI3 {r[0]:.1f} / CAGR {r[1]} outside sanity band (−30%,60%) or ≤0 → unit/currency error')
def load_routing():
    import csv; p=os.path.join(HERE,'..','master','ROUTING.csv')
    return {r['code']:r['sub'] for r in csv.DictReader(open(p,encoding='utf-8'))}


# ---- r3 PROVISIONAL thresholds (NOT tuned; structure only) ----
PROVISIONAL = {
    'consensus_tol_pct': 15.0,      # EXT.1
    'optimism_haircut_pct': 10.0,   # EXT.2
    'method_spread_max': 1.25,      # EXT.4
    'ext_max_age_days': 30,         # EXT.6
    'b20_up_disclose_pct': 5.0,     # RC3
    'trough_margin_gap_pp': 3.0,    # RC1
    'revision_down_pct': 5.0,       # EXT.6
    'min_analysts_consensus': 5,    # EXT.6
}

# ---- S4c external cross-check + stability (card) ----
def r_s4c(c,o):
    """r4: B20_issued always required. If false → gate_block_reason + skip never-lift numerics (escape hatch).
    If true → external_crosscheck, methods≥2, range_buy, numeric B20_TR; URL/date/same-basis/never-lift/min-range.
    n_analysts asserted when source kind=consensus (uses PROVISIONAL min_analysts_consensus; value unchanged).
    EXT.2 optimism haircut = DISPLAY-assist only until backtested."""
    issued=c.get('B20_issued')
    if issued is None:
        F(o,'A.L1.stability.B20_issued','FAIL','B20_issued required (true|false)')
        return
    if issued is False:
        reason=c.get('gate_block_reason')
        if not reason or not str(reason).strip():
            F(o,'A.L1.stability.gate_block_reason','FAIL','B20_issued=false requires non-empty gate_block_reason (r4 escape)')
        # Escape: skip never-lift / range / dual-method numeric asserts (documented SHOULD-5)
        return
    # issued True
    ext=c.get('external_crosscheck')
    bp=c.get('buy_point') or {}
    methods=(ext or {}).get('methods') or c.get('methods') or []
    if len(methods)<2:
        F(o,'A.L1.stability.dual_method','FAIL','methods <2 → cannot issue B20 (V§5-8 / EXT.4)')
        return
    if not c.get('range_buy'):
        F(o,'A.L1.EXT.range_buy','FAIL','range_buy required when B20_issued=true')
    if not num(bp.get('B20_TR')):
        F(o,'A.L1.buy_point','FAIL','buy_point.B20_TR must be numeric when B20_issued=true')
    if not ext:
        F(o,'A.L1.EXT','FAIL','external_crosscheck missing (S4c required before B20 issue)')
        return
    as_of=c.get('as_of') or c.get('price_date')
    srcs=ext.get('ext_sources') or []
    if not srcs:
        F(o,'A.L1.EXT.guardrail','FAIL','ext_sources empty')
    for s in srcs:
        if not s.get('url'):
            F(o,'A.L1.EXT.guardrail','FAIL','ext_sources[].url required')
        if not s.get('fetched_at'):
            F(o,'A.L1.EXT.guardrail','FAIL','ext_sources[].fetched_at required')
        elif as_of:
            try:
                age=(D(as_of)-D(s['fetched_at'])).days
                if abs(age)>PROVISIONAL['ext_max_age_days']:
                    F(o,'A.L1.EXT.guardrail','FAIL',f"ext source age {age}d > provisional {PROVISIONAL['ext_max_age_days']}d (PROVISIONAL_UNBACKTESTED)")
            except Exception:
                F(o,'A.L1.EXT.guardrail','FAIL','ext_sources fetched_at/as_of date parse fail')
        if s.get('basis') and ext.get('basis') and s['basis']!=ext['basis']:
            F(o,'A.L1.EXT.consensus','FAIL',f"source basis {s.get('basis')} ≠ ext.basis {ext.get('basis')} (same-basis required)")
        # P5: n_analysts when kind=consensus
        kind=(s.get('kind') or '').lower()
        if kind=='consensus':
            na=s.get('n_analysts')
            if not num(na) or na < PROVISIONAL['min_analysts_consensus']:
                F(o,'A.L1.EXT.guardrail','FAIL',f"consensus n_analysts={na} < provisional min_analysts_consensus={PROVISIONAL['min_analysts_consensus']} (PROVISIONAL_UNBACKTESTED)")
    if num(ext.get('deviation_pct')):
        if abs(ext['deviation_pct'])>PROVISIONAL['consensus_tol_pct'] and not ext.get('deviation_reason'):
            F(o,'A.L1.EXT.consensus','FAIL',f"|deviation| {ext['deviation_pct']}% > provisional {PROVISIONAL['consensus_tol_pct']}% without deviation_reason (PROVISIONAL_UNBACKTESTED)")
    # EXT.2 DISPLAY-assist only
    if num(ext.get('consensus_ni3')) and ext.get('optimism_haircut_pct') is None:
        F(o,'A.L1.EXT.optimism_haircut','DISPLAY','optimism_haircut_pct missing (EXT.2 DISPLAY-assist; not hardened until backtested)')
    # revision flag when provided → DISPLAY if above provisional without action/reason
    if 'revision_down_pct' in ext and num(ext.get('revision_down_pct')):
        if abs(ext['revision_down_pct'])>PROVISIONAL['revision_down_pct']:
            if not ext.get('revision_bear_action') and not ext.get('revision_reason'):
                F(o,'A.L1.EXT.revision','DISPLAY',f"revision_down_pct {ext['revision_down_pct']}% > provisional {PROVISIONAL['revision_down_pct']}% without revision_bear_action/reason (DISPLAY-assist)")
    fvs=[m['FV3_base'] for m in methods if num(m.get('FV3_base')) and m['FV3_base']>0]
    if len(fvs)>=2:
        spread=max(fvs)/min(fvs)
        if spread>PROVISIONAL['method_spread_max']:
            F(o,'A.L1.EXT.triangulation','FAIL',f'method FV3 spread {spread:.3f} > provisional {PROVISIONAL["method_spread_max"]} → no B20 (PROVISIONAL_UNBACKTESTED)')
    rng=ext.get('range') or {}
    vals=list(rng.get('values') or [])
    if num(rng.get('min')): vals.append(rng['min'])
    Bf,Bi=ext.get('B20_final'),ext.get('B20_internal')
    if not num(Bf) or not num(Bi):
        F(o,'A.L1.EXT.guardrail','FAIL','B20_final and B20_internal required')
    else:
        if Bf>Bi+1e-6:
            F(o,'A.L1.EXT.guardrail','FAIL',f'B20_final {Bf} > B20_internal {Bi} (external must never lift B20)')
        if vals:
            mn=min(vals)
            if not close(Bf,mn,0.002) and not close(Bf,rng.get('min',mn),0.002):
                F(o,'A.L1.EXT.range_buy','FAIL',f'B20_final {Bf} ≠ min(range) {mn} (EXT.5)')
            if num(rng.get('min')) and not close(rng['min'],mn,0.002):
                F(o,'A.L1.EXT.range_buy','FAIL',f"range.min {rng['min']} ≠ min(values) {mn}")
    rb=c.get('range_buy') or {}
    if rb:
        if num(rb.get('B20_TR')) and num(Bf) and not close(rb['B20_TR'],Bf,0.002):
            F(o,'A.L1.EXT.range_buy','FAIL',f"range_buy.B20_TR {rb['B20_TR']} ≠ B20_final {Bf}")
        if num(rb.get('range_min')) and num(Bf) and not close(rb['range_min'],Bf,0.002):
            F(o,'A.L1.EXT.range_buy','FAIL','range_buy.B20_TR must equal range_min')
        px=c.get('price')
        if num(px) and vals and rb.get('at_price_whole_range') is True:
            if any(px>v+1e-9 for v in vals):
                F(o,'A.L1.EXT.range_buy','FAIL','at_price_whole_range=true but price > some range value')
    if num(bp.get('B20_TR')) and num(Bf) and not close(bp['B20_TR'],Bf,0.002):
        F(o,'A.L1.EXT.guardrail','FAIL',f"buy_point.B20_TR {bp['B20_TR']} ≠ B20_final {Bf}")

def r_rc3(c,o):
    """RC3: if prior_card_ref / prior_as_of / prior_ledger_ref exists → round_delta required.
    When round_delta present: B20 up >provisional% or status flip must list changes."""
    rd=c.get('round_delta')
    has_prior=bool(c.get('prior_card_ref') or c.get('prior_as_of') or c.get('prior_ledger_ref'))
    if has_prior and not rd:
        F(o,'A.L1.review.gaming','FAIL','prior_card_ref/prior_as_of/prior_ledger_ref present but round_delta missing (RC3 r4)')
        return
    if not rd: return
    thr=rd.get('b20_up_disclose_pct', PROVISIONAL['b20_up_disclose_pct'])  # PROVISIONAL value unchanged
    up=rd.get('b20_up_pct'); flip=rd.get('status_flipped')
    need= (num(up) and up>thr) or (flip is True)
    if need:
        ch=rd.get('listed_changes') or []
        if not ch:
            F(o,'A.L1.review.gaming','FAIL',f'round_delta requires listed_changes when B20 up>{thr}% (provisional) or status flip (RC3)')
        for i,x in enumerate(ch):
            for k in ('change','direction','b20_contribution','author_reason'):
                if x.get(k) in (None,''):
                    F(o,'A.L1.review.gaming','FAIL',f'listed_changes[{i}] missing {k}')

def r_rc5_card(c,o):
    if c.get('sbc_deduct_only_B20') is not None:
        F(o,'A.L1.profit_base.sbc_both_sides','FAIL','card sbc_deduct_only_B20 banned (RC5)')
    pb=c.get('profit_base') or {}
    if pb.get('sbc_treatment')=='sensitivity_same_basis_multiple' or c.get('sbc_treatment')=='sensitivity_same_basis_multiple':
        # if a deduct-only number appears under buy_point sensitivities wrongly shaped — only both_sides allowed
        sens=c.get('sensitivities') or {}
        if 'sbc_deduct_only' in sens:
            F(o,'A.L1.profit_base.sbc_both_sides','FAIL','sensitivities.sbc_deduct_only banned; use sbc_sensitivity_both_sides')


def r_plugin_methods(c,o):
    """P3: plugin must have methods≥2 OR dual_method_exception {V20_pending|data_gap}+reason."""
    methods=c.get('methods') or []
    ex=c.get('dual_method_exception')
    if len(methods)>=2:
        return
    if isinstance(ex,dict) and ex.get('code') in ('V20_pending','data_gap') and str(ex.get('reason') or '').strip():
        return
    F(o,'A.L1.stability.dual_method','FAIL','plugin methods <2 and no dual_method_exception (V20_pending|data_gap + reason)')

# ---- D3: card gate ----
def b20(fv,dps,h,n): return (fv+n*dps)/(1+h/100)**n
def r_card(c,o):
    rv=c.get('review') or {}
    if rv.get('independent') is not True: F(o,'A.L1.review.independent','FAIL','review.independent must be true')
    if not rv.get('reviewer_id') or rv.get('reviewer_id')==rv.get('author_id'): F(o,'A.L1.review.independent','FAIL','reviewer_id missing or == author_id')
    if rv.get('verdict') not in ('PASS','PASS_WITH_CHANGES'): F(o,'A.L1.review.verdict','FAIL',f"verdict={rv.get('verdict')!r} not PASS/PASS_WITH_CHANGES")
    if rv.get('verdict')=='PASS_WITH_CHANGES' and any(not x.get('resolved') for x in rv.get('required_changes',[])): F(o,'A.L1.review.verdict','FAIL','unresolved required_changes')
    fr=c.get('fragility') or {}; px=c.get('price'); bp=c.get('buy_point') or {}; B=bp.get('B20_TR')
    res=fr.get('results_B20_TR')
    if not res: F(o,'A.L1.fragility','FAIL','fragility.results_B20_TR required for recompute')
    elif num(px) and num(B):
        flips=any((px<=B)!=(px<=v) for v in res.values())
        if bool(fr.get('fragile'))!=flips: F(o,'A.L1.fragility','FAIL',f"fragile={fr.get('fragile')} but recompute → {flips}")
    s=c.get('FV3') or {}; n=(c.get('exit_multiple') or {}).get('n_years'); h=(c.get('hurdle') or {}).get('primary_pct'); d=c.get('dps_min3')
    if all(num(x) for x in (s.get('base'),n,h,d)) and num(B):
        if not close(b20(s['base'],d if bp.get('stack_dividend') else 0,h,n),B,0.002): F(o,'A.L1.buy_point','FAIL',f'B20_TR {B} ≠ recompute {b20(s["base"],d if bp.get("stack_dividend") else 0,h,n):.2f} (n={n})')
        if num(s.get('bear')) and num(fr.get('frag_TR')):
            ft=(s['bear']+n*d)/(s['base']+n*d)
            if not close(ft,fr['frag_TR'],0.01): F(o,'A.L1.fragility','FAIL',f"frag_TR {fr['frag_TR']} ≠ recompute {ft:.3f}")
        # RC4: r_bear must use n, not hardcoded 3 (accept decimal or percent storage)
        if num(s.get('bear')) and num(fr.get('r_bear')) and num(px) and px>0 and num(n) and n>0:
            rb=((s['bear']+(n*d if num(d) else 0))/px)**(1/n)-1
            got=fr['r_bear']; got_dec=got/100.0 if abs(got)>1 else got
            # also check wrong hardcoded-3 would differ when n!=3
            if not close(got_dec,rb,0.02):
                F(o,'A.L1.fragility','FAIL',f"r_bear {got} ≠ recompute with n={n}: {rb:.4f} / {rb*100:.2f}% (RC4: must use n not 3)")
def validate(c,kind='plugin',routing=None):
    o=[]; schema_check(c,kind,o)
    if kind=='plugin':
        fs=(r1,r_snap,r2,r3,r456,r_m8,r_drivers,r_base_year,r_plugin_methods)
    else:
        fs=(r1,r2,r_card,r_s4c,r_rc3,r_rc5_card)
    for f in fs: f(c,o)
    r_route(c,o,routing if routing is not None else load_routing())
    return o
def fails(v): return {x['anchor'] for x in v if x['level']=='FAIL'}

# ---- self-test + mutation tests ----
def _fixture_dir(): return os.path.join(HERE,'..','test-fixtures')
def selftest():
    good=json.load(open(os.path.join(_fixture_dir(),'m5b_good.json'),encoding='utf-8'))
    v=validate(good,'plugin',{}); assert not fails(v),v
    bad=json.loads(json.dumps(good)); bad['roe']['base']=8.2; bad['profit_base']['hedge_fx_addback']=5
    assert {'A.L3.M5.roe_take_lower','A.L1.profit_base.hedge_fx'}<=fails(validate(bad,'plugin',{}))
    print('selftest OK',VERSION)
def mutation_tests(plugin_path,card_path):
    """Each mutation of a passing (or gate-known) artifact MUST raise the named FAIL."""
    P=json.load(open(plugin_path,encoding='utf-8')); C=json.load(open(card_path,encoding='utf-8'))
    # r4: ensure plugin control has dual methods (does not rewrite on-disk file)
    P=json.loads(json.dumps(P))
    if len(P.get('methods') or [])<2 and not P.get('dual_method_exception'):
        P['methods']=[{'id':'m1','kind':'SOTP','FV3_base':(P.get('FV3') or {}).get('base') or 100},
                      {'id':'m2','kind':'reverse_DCF','FV3_base':((P.get('FV3') or {}).get('base') or 100)*1.02}]
    base_p=fails(validate(P,'plugin')); res=[]
    # control card: real card with a clearly-labelled FIXTURE review so the gate can pass; real review untouched on disk
    C=json.loads(json.dumps(C)); C['review']={'independent':True,'author_id':'fixture-author','reviewer_id':'fixture-reviewer','verdict':'PASS',
        'premortem':['FIXTURE'],'anchor_checklist':['FIXTURE'],'required_changes':[],'note':'SYNTHETIC control for mutation tests only'}
    # r3: synthetic S4c/stability so control card is clean (does not touch on-disk card)
    B=float((C.get('buy_point') or {}).get('B20_TR') or 100)
    C['B20_issued']=True
    C['methods']=[{'id':'m1','kind':'primary','FV3_base':100},{'id':'m2','kind':'cross','FV3_base':105}]
    C['external_crosscheck']={
        'ext_sources':[{'url':'https://example.com/fixture','fetched_at':C.get('as_of') or C.get('price_date') or '2026-10-30','basis':'non-IFRS','n_analysts':10,'kind':'consensus'}],
        'methods':C['methods'],'basis':'non-IFRS',
        'B20_internal':B,'B20_final':B,
        'range':{'min':B,'max':B,'values':[B]},
        'optimism_haircut_pct':PROVISIONAL['optimism_haircut_pct'],
        'consensus_tol_pct':PROVISIONAL['consensus_tol_pct'],
        'method_spread_max':PROVISIONAL['method_spread_max'],
        'at_price_by_range':False,'external_fv_display':None,
    }
    C['range_buy']={'B20_TR':B,'range_min':B,'range_max':B,'at_price_whole_range':False}
    C.pop('sbc_deduct_only_B20',None); C.pop('round_delta',None)
    base_c=fails(validate(C,'card'))
    if base_p or base_c: print('control not clean → mutation results not meaningful:',sorted(base_p),sorted(base_c)); return False
    def run(name,obj,kind,expect):
        f=fails(validate(obj,kind)); ok=expect in f; res.append((name,expect,ok)); return ok
    m=json.loads(json.dumps(P))  # 1 lagged PE: profit_fy = fy-1
    for s in m['multiple_anchor']['snapshots']: s['profit_fy']=int(str(s['fy']).replace('FY',''))-1
    run('lagged_PE(profit_fy=fy-1)',m,'plugin','A.L1.exit_multiple.basis')
    m=json.loads(json.dumps(P)); m['multiple_anchor']['snapshots'][0]['price_date']=m['multiple_anchor']['snapshots'][1]['price_date']
    run('lagged_PE(price_date=next YE)',m,'plugin','A.L1.exit_multiple.basis')
    m=json.loads(json.dumps(P)); m['multiple_anchor']['kind']='SOTP'; m['multiple_anchor'].pop('snapshots')
    run('SOTP_without_snapshot_table',m,'plugin','A.L1.exit_multiple.snapshots')
    m=json.loads(json.dumps(P)); m['multiple_anchor']['snapshots'][0]['price_basis']='qfq'
    run('qfq_price',m,'plugin','A.L1.exit_multiple.input_hygiene')
    m=json.loads(json.dumps(P)); m['multiple_anchor']['snapshots']=m['multiple_anchor']['snapshots'][1:]
    run('3_snapshots',m,'plugin','A.L1.exit_multiple.window')
    m=json.loads(json.dumps(P)); m['multiple_anchor']['total_mcap_pe_used']=True
    run('double_count',m,'plugin','A.L3.M8.no_double_count')
    m=json.loads(json.dumps(P)); m['FV3_components']['bear']['core_pe']+=1.0
    run('bear_PE_above_min',m,'plugin','A.L1.bear_stress.multiple')
    m=json.loads(json.dumps(P)); [d.__setitem__('is_top2',False) for d in m['drivers'][1:]]
    run('missing_top2(1 driver)',m,'plugin','A.L1.fragility.top2')
    m=json.loads(json.dumps(P)); [d.__setitem__('is_top2',True) for d in m['drivers']]
    run('too_many_top2',m,'plugin','A.L1.fragility.top2')
    m=json.loads(json.dumps(P)); m['multiple_anchor']['n_years']=3.0
    run('FY3_n_years_3.0',m,'plugin','A.L1.exit_date_convention.n')
    m=json.loads(json.dumps(P)); m['display_checks']['fx_price_ccy_per_report']=1/m['display_checks']['fx_price_ccy_per_report']; m['display_checks']['shares_mn']/=1000
    run('reverse_dcf_unit_error',m,'plugin','A.L1.reverse_dcf.sanity')
    m=json.loads(json.dumps(P)); m['bear_margin']['bear']=m['bear_margin']['worst_last3']+1
    run('bear_margin_above_floor',m,'plugin','A.L1.bear_stress.margin')
    c=json.loads(json.dumps(C)); c['review'].update(independent=False,reviewer_id='fixture-author')
    run('non_independent_review',c,'card','A.L1.review.independent')
    c=json.loads(json.dumps(C)); c['review']['verdict']='FAIL'
    run('review_verdict_FAIL',c,'card','A.L1.review.verdict')
    c=json.loads(json.dumps(C)); c['fragility']['fragile']=not c['fragility']['fragile']
    run('wrong_fragility_flag',c,'card','A.L1.fragility')
    c=json.loads(json.dumps(C)); c['buy_point']['B20_TR']*=1.05
    run('B20_not_recomputable',c,'card','A.L1.buy_point')
    # r3 S4c / RC mutations
    c=json.loads(json.dumps(C)); c['external_crosscheck']['ext_sources'][0]['url']=''
    run('S4c_missing_url',c,'card','A.L1.EXT.guardrail')
    c=json.loads(json.dumps(C)); c['external_crosscheck']['B20_final']=c['external_crosscheck']['B20_internal']*1.1; c['buy_point']['B20_TR']=c['external_crosscheck']['B20_final']; c['range_buy']['B20_TR']=c['external_crosscheck']['B20_final']; c['range_buy']['range_min']=c['external_crosscheck']['B20_final']; c['external_crosscheck']['range']={'min':c['external_crosscheck']['B20_final'],'max':c['external_crosscheck']['B20_final'],'values':[c['external_crosscheck']['B20_final']]}
    run('S4c_external_lifts_B20',c,'card','A.L1.EXT.guardrail')
    c=json.loads(json.dumps(C)); c['external_crosscheck']['B20_final']=c['external_crosscheck']['B20_internal']*0.9; c['buy_point']['B20_TR']=c['external_crosscheck']['B20_final']; c['range_buy']={'B20_TR':c['external_crosscheck']['B20_final'],'range_min':c['external_crosscheck']['B20_final'],'range_max':c['external_crosscheck']['B20_internal'],'at_price_whole_range':False}; c['external_crosscheck']['range']={'min':c['external_crosscheck']['B20_internal']*0.85,'max':c['external_crosscheck']['B20_internal'],'values':[c['external_crosscheck']['B20_internal']*0.85,c['external_crosscheck']['B20_internal']]}
    run('S4c_not_min_of_range',c,'card','A.L1.EXT.range_buy')
    c=json.loads(json.dumps(C)); c['methods']=[{'id':'only','kind':'PE','FV3_base':100}]; c['external_crosscheck']['methods']=c['methods']
    run('dual_method_missing',c,'card','A.L1.stability.dual_method')
    c=json.loads(json.dumps(C)); c['external_crosscheck']['methods']=[{'id':'a','kind':'PE','FV3_base':100},{'id':'b','kind':'DCF','FV3_base':140}]; c['methods']=c['external_crosscheck']['methods']
    run('method_spread_too_wide',c,'card','A.L1.EXT.triangulation')
    c=json.loads(json.dumps(C)); c['round_delta']={'prior_B20_TR':B*0.9,'prior_at_price':False,'b20_up_pct':12.0,'status_flipped':True,'listed_changes':[],'b20_up_disclose_pct':5.0}
    run('RC3_missing_listed_changes',c,'card','A.L1.review.gaming')
    c=json.loads(json.dumps(C)); c['sbc_deduct_only_B20']=123.45
    run('RC5_sbc_deduct_only',c,'card','A.L1.profit_base.sbc_both_sides')
    # RC1 trough on plugin
    m=json.loads(json.dumps(P))
    if m.get('multiple_anchor',{}).get('snapshots') and all(num(s.get('value')) for s in m['multiple_anchor']['snapshots']):
        # tag first snap as clear trough via core_margin without exclude flag
        for i,s in enumerate(m['multiple_anchor']['snapshots']):
            s['core_margin']=30.0 if i else 20.0
            s.pop('exclude_from_base_bull',None)
        run('RC1_trough_not_excluded',m,'plugin','A.L1.exit_multiple.trough_exclusion')
        m=json.loads(json.dumps(P))
        for i,s in enumerate(m['multiple_anchor']['snapshots']):
            s['core_margin']=30.0 if i else 20.0
            if i==0: s['exclude_from_base_bull']=True; s['exclude_reason']='trough'
        m['bear_margin']=dict(m.get('bear_margin') or {}, bear=25.0, worst_in_window=20.0, worst_last3=23.0, exemption_reason='one-off')
        run('RC2_trough_exempted',m,'plugin','A.L1.bear_stress.trough_floor')
    # r4 mutations
    c=json.loads(json.dumps(C)); c['B20_issued']=False; c['gate_block_reason']=''; c.pop('external_crosscheck',None)
    run('r4_issued_false_no_reason',c,'card','A.L1.stability.gate_block_reason')
    c=json.loads(json.dumps(C)); c.pop('B20_issued',None)
    run('r4_B20_issued_missing',c,'card','A.L1.stability.B20_issued')
    c=json.loads(json.dumps(C)); c['external_crosscheck']['ext_sources'][0]['n_analysts']=2
    run('r4_consensus_n_analysts_low',c,'card','A.L1.EXT.guardrail')
    c=json.loads(json.dumps(C)); c['prior_card_ref']='runs/prior/decision_card.json'; c.pop('round_delta',None)
    run('r4_prior_without_round_delta',c,'card','A.L1.review.gaming')
    m=json.loads(json.dumps(P)); m.pop('methods',None); m.pop('dual_method_exception',None)
    run('r4_plugin_no_dual_method',m,'plugin','A.L1.stability.dual_method')
    for r in res: print(('PASS ' if r[2] else 'MISS ')+f'{r[0]:34s} → expects FAIL {r[1]}')
    print(f'mutation tests: {sum(r[2] for r in res)}/{len(res)} caught (controls: plugin & fixture-review card 0 FAIL)')
    return all(r[2] for r in res)
if __name__=='__main__':
    a=sys.argv[1:]
    if '--selftest' in a: selftest(); sys.exit()
    if '--mutation-tests' in a: i=a.index('--mutation-tests'); sys.exit(0 if mutation_tests(a[i+1],a[i+2]) else 1)
    kind='plugin'
    if '--kind' in a: i=a.index('--kind'); kind=a[i+1]; del a[i:i+2]
    bad=0
    for p in a:
        for x in validate(json.load(open(p,encoding='utf-8')),kind): print(p,x); bad|=x['level']=='FAIL'
    sys.exit(1 if bad else 0)
