#!/usr/bin/env python3
"""000423.SZ simple revaluation 2026-11-06 — PE-only; exit PE judgment-based (not median)."""
import json
from datetime import date
from pathlib import Path

asof = date(2026, 11, 6)
fy3_date = date(2029, 12, 31)
n = (fy3_date - asof).days / 365.25
px = 50.53
shares_mn = 639.826824
exit_pe = 22  # judgment: mid-lower band; see README.md (median 20.11 is reference only)
rev0, g, margin = 68.74, 0.04, 0.255
ni3 = rev0 * (1 + g) ** 3 * margin
eps3 = ni3 * 100 / shares_mn
fv3 = eps3 * exit_pe
dps_min3 = 1.78
b20 = (fv3 + n * dps_min3) / (1.20 ** n)
b22 = (fv3 + n * dps_min3) / (1.22 ** n)
# sensitivity if cash-conversion haircut applied
fv3_h = (ni3 * 0.90 * 100 / shares_mn) * exit_pe
b20_h = (fv3_h + n * dps_min3) / (1.20 ** n)
out = {
    "as_of": "2026-11-06",
    "px": px,
    "shares_mn": shares_mn,
    "n": round(n, 6),
    "exit_pe": exit_pe,
    "exit_pe_source": "judgment_band_20_30_lower_mid",
    "ni3": round(ni3, 4),
    "eps3": round(eps3, 6),
    "fv3_pe_only": round(fv3, 2),
    "b20_research": round(b20, 2),
    "b22_research": round(b22, 2),
    "cash_conversion": "过",
    "haircut_applied": 1.0,
    "sensitivity_haircut_0_90": {"fv3": round(fv3_h, 2), "b20": round(b20_h, 2)},
    "reverse_DCF": "已废止/不作定价",
    "B20_issued": False,
    "premium": round(px / b20 - 1, 4),
    "vs_prior_pe_only": {
        "old_exit_pe": 20.11,
        "old_fv3": 61.97,
        "old_b20": 38.05,
        "note": "废止中位直接主报；判断取值22",
    },
}
print(json.dumps(out, ensure_ascii=False, indent=2))
Path(__file__).with_name("calc_out.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)
