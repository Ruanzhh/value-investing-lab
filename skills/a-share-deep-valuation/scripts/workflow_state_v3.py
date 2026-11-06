#!/usr/bin/env python3
"""v3 workflow state machine (draft r2, D11). Sandbox only: never touches live cards/board/watchlist.
usage: workflow_state_v3.py open <run_dir> --ticker T [--test-run]
       workflow_state_v3.py commit <run_dir> <state> <artifact> [--status ok|blocked|fail] [--note ..]
       workflow_state_v3.py status <run_dir>"""
import json,sys,os,datetime as dt
STATES=['S0_intake','S1_routing','S2_dispatch_sub','S3_unified_output','S4_validate_gate','S5_L1_buy_sell','S6_independent_review','S7_decision_card','S8_ledger_register','S9_reconcile_feed']
LIVE_GUARD=('live-workflows','watchlist','/board')
def now(): return dt.datetime.now().isoformat(timespec='seconds')
def path(d): return os.path.join(d,'v3_state.json')
def main(a):
    cmd,d=a[0],a[1]; ap=os.path.abspath(d)
    if any(g in ap for g in LIVE_GUARD): sys.exit(f'refuse: {ap} is a live path')
    if cmd=='open':
        st={'ticker':a[a.index('--ticker')+1],'test_run':'--test-run' in a,'opened':now(),'states':{},'next':STATES[0]}
        if st['test_run'] and '/test-runs/' not in ap+'/': sys.exit('test runs must live under workflow-v3/test-runs/')
        os.makedirs(d,exist_ok=True); json.dump(st,open(path(d),'w'),indent=1); print('[workflow] opened',d)
    elif cmd=='commit':
        st=json.load(open(path(d))); s,art=a[2],a[3]
        if s not in STATES: sys.exit(f'unknown state {s}')
        i=STATES.index(s); prev=[x for x in STATES[:i] if st['states'].get(x,{}).get('status')!='ok']
        if prev: sys.exit(f'cannot commit {s}: earlier states not ok {prev}')
        if not os.path.exists(os.path.join(d,art)): sys.exit(f'artifact missing {art}')
        status=a[a.index('--status')+1] if '--status' in a else 'ok'
        st['states'][s]={'artifact':art,'status':status,'at':now(),'note':a[a.index('--note')+1] if '--note' in a else ''}
        st['next']=STATES[i+1] if status=='ok' and i+1<len(STATES) else s
        json.dump(st,open(path(d),'w'),indent=1); print(f'[workflow] {s} {status} → next {st["next"]}')
    elif cmd=='status': print(json.dumps(json.load(open(path(d))),indent=1,ensure_ascii=False))
if __name__=='__main__': main(sys.argv[1:])
