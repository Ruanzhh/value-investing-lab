#!/usr/bin/env python3
"""宁德时代 300750 PE-only · 2026-11-06 Asia/Shanghai。

现金转化终判：打折 0.80（用户授权自定折扣后回流）。
正式只走 PE：ni3_adj=858×0.80；退出PE=22（判断取值）；禁止双轨取低。
"""
from pathlib import Path
import json
from datetime import date

AS_OF = date(2026, 11, 6)
FY3_END = date(2029, 12, 31)
n = (FY3_END - AS_OF).days / 365.25
H = 0.20
DPS = 5.028
SH = 46.27249686
PRICE = 264.06

NI3_GROSS = 858.0
DISC = 0.80
DISC_REASON = (
    "购建类维持300–450 vs DA≈266 → OE/NI粗算约0.75–0.95（中位偏维持取八折）；"
    "海外门票80–150与2026 9M OCF/NI=0.95作下压，不定0.85；"
    "利润为真且OE仍显著为正 → 不选永久不过；Capex/DA未入收获期 → 不选过。"
)
PE_EXIT = 22.0
NI3_ADJ = NI3_GROSS * DISC
fv = NI3_ADJ * PE_EXIT / SH
gate = (fv + n * DPS) / ((1 + H) ** n)

# cross: undiscounted informal (full NI3 × 22) for comparison only
fv_full = NI3_GROSS * PE_EXIT / SH
gate_full = (fv_full + n * DPS) / ((1 + H) ** n)

out = {
    "as_of": "2026-11-06 Asia/Shanghai",
    "rule": "cash_conversion_discount_then_PE_only",
    "exit_pe_rule": "SIMPLE-FLOW §4 2026-11-06: judge 20-30; hist median reference only",
    "screen": {
        "profit_real": "pass_with_watch",
        "profit_sustainable": "pass_midcycle",
        "cash_conversion": "discount",
        "discount": DISC,
        "discount_reason": DISC_REASON,
        "maint_capex_proxy_yi_pa": "300-450 ex-R&D",
        "overseas_ticket_yi_pa_est": "80-150",
        "ocf_ni_2026_9M": 0.95,
    },
    "formal_valuation": {
        "issued": True,
        "ni3_gross_yi": NI3_GROSS,
        "discount": DISC,
        "ni3_adj_yi": round(NI3_ADJ, 2),
        "pe_exit": PE_EXIT,
        "fv3_base": round(fv, 2),
        "fv3_display": round(fv),
        "buy_gate": round(gate, 2),
        "buy_gate_display": round(gate),
        "n": n,
        "hurdle": H,
        "dps_min3": DPS,
        "shares_yi": SH,
        "buy_point_formally_enabled": False,
        "enablement_gaps": [
            "税负官方转嫁比例未知",
            "投产后利用率无公司%",
            "系统净利不可拆",
            "FY2029一致预期交叉未齐",
            "购建维持/扩张官方拆分仍缺",
        ],
    },
    "price": PRICE,
    "premium_vs_gate_pct": round((PRICE / gate - 1) * 100, 1),
    "cross_undiscounted_informal_not_for_card": {
        "note": "全额NI3×22仅交叉；正式用打折后数字",
        "fv3": round(fv_full, 2),
        "gate": round(gate_full, 2),
    },
    "vs_old_anchors": {
        "old_formal_fv_406_status": "废止（两轨取低）",
        "old_formal_gate_237_status": "废止",
        "new_fv_vs_406_pct": round((fv / 406.15 - 1) * 100, 1),
        "new_gate_vs_237_pct": round((gate / 237.46 - 1) * 100, 1),
        "prior_informal_undisc_fv_408": 407.93,
        "prior_informal_undisc_gate_239": 238.57,
        "new_vs_prior_informal_fv_pct": round((fv / 407.93 - 1) * 100, 1),
        "new_vs_prior_informal_gate_pct": round((gate / 238.57 - 1) * 100, 1),
    },
}

path = Path(__file__).with_name("calc_pe_only_out.json")
json.dump(out, open(path, "w"), ensure_ascii=False, indent=1)
print(json.dumps(out["formal_valuation"], ensure_ascii=False, indent=1))
print("premium", out["premium_vs_gate_pct"])
print("vs old", out["vs_old_anchors"])
