#!/usr/bin/env python3
"""福耀 600660 PE-only：筛选现金转化打折 0.88 后只走 PE 轨。
2026-11-06 Asia/Shanghai。hurdle 20%，n=估值日→FY2029年末。
禁止 FCF×P/F 与 PE 取低；历史 P/F、无风险收益倒数只作交叉对照。"""
from pathlib import Path
import json, statistics
from datetime import date

n = (date(2029, 12, 31) - date(2026, 11, 5)).days / 365.25
H = 0.20
DPS = 1.3
SH = 2609.743532  # 百万股；市值=px*SH/100 亿元

AR = {
    2023: dict(ni=56.29, core=55.27, ocf=76.25, px=37.39, da=25.22, capex=44.75, rev=331.61),
    2024: dict(ni=74.98, core=74.46, ocf=85.62, px=62.40, da=27.27, capex=54.81, rev=392.52),
    2025: dict(ni=93.12, core=91.65, ocf=120.55, px=64.77, da=30.77, capex=61.64, rev=457.87),
}
pe_hist = {
    2022: 19.62,
    2023: round(AR[2023]["px"] * SH / 100 / AR[2023]["core"], 2),
    2024: round(AR[2024]["px"] * SH / 100 / AR[2024]["core"], 2),
    2025: round(AR[2025]["px"] * SH / 100 / AR[2025]["core"], 2),
}
pf_hist = {y: round(v["px"] * SH / 100 / (v["ocf"] - v["da"]), 2) for y, v in AR.items()}
k_hist = {y: round((v["ocf"] - v["da"]) / v["ni"], 4) for y, v in AR.items()}
conv = {y: round(v["ocf"] / v["ni"], 3) for y, v in AR.items()}

pe_hist_median = round(statistics.median([pe_hist[y] for y in (2022, 2023, 2024, 2025)]), 2)
pe_exit = 22.0
disc = 0.88
pf_med = round(statistics.median(list(pf_hist.values())), 2)
k_mean = round(sum(k_hist.values()) / len(k_hist), 3)
conv_mean = round(sum(conv.values()) / len(conv), 2)

def model(p):
    rev3 = p["rev0"] * (1 + p["g"]) ** 3
    ni3 = rev3 * p["m"]
    ni_use = ni3 * p["disc"]
    fv = ni_use * p["pe"] * 100 / SH
    gate = (fv + n * DPS) / (1 + H) ** n
    fv_pf_x = ni3 * p["k"] * p["pf"] * 100 / SH
    fv_rf25 = ni_use * 25 * 100 / SH
    return dict(
        rev3=rev3, ni3=ni3, ni_use=ni_use, fv=fv, gate=gate,
        fv_pf_cross=fv_pf_x, fv_rf25=fv_rf25,
        spread_pf=fv / fv_pf_x if fv_pf_x else None,
        spread_rf25=fv_rf25 / fv if fv else None,
    )

base_p = dict(rev0=466.08, g=0.06, m=0.165, pe=pe_exit, disc=disc, k=k_mean, pf=pf_med)
base = model(base_p)
sens = {}
for key in ("rev0", "g", "m", "pe", "disc"):
    lo = model({**base_p, key: base_p[key] * 0.9})["fv"]
    hi = model({**base_p, key: base_p[key] * 1.1})["fv"]
    sens[key] = dict(
        minus10=round((lo / base["fv"] - 1) * 100, 1),
        plus10=round((hi / base["fv"] - 1) * 100, 1),
    )
sens = dict(sorted(sens.items(), key=lambda x: -max(abs(x[1]["minus10"]), abs(x[1]["plus10"]))))
per_1pct = round(model({**base_p, "m": base_p["m"] + 0.01})["fv"] - base["fv"], 2)

out = {
    "as_of": "2026-11-06 Asia/Shanghai",
    "rule": "PE-only; cash-conversion=discount 0.88 then PE",
    "n": n,
    "hurdle": H,
    "dps": DPS,
    "shares_yi": SH / 100,
    "pe_hist_core": pe_hist,
    "pe_exit": pe_exit,
    "pe_ref_hist_median": pe_hist_median,
    "pe_exit_reason": "cost-moat mfr, no franchise pricing, expansion ongoing, OEM strong → band 20-25 pick 22",
    "cash_conversion": "打折",
    "discount": disc,
    "discount_reason": "(OCF-D&A)/NI mean 0.883; expansion Capex/D&A~2.0; maintain-competitiveness Capex undisclosed → discount NI×0.88 before PE; not 不过 because OCF/NI 1.26 and weak-expansion Capex≈D&A",
    "pf_hist_cross": pf_hist,
    "pf_med_cross": pf_med,
    "k_hist": k_hist,
    "k_mean": k_mean,
    "conv_hist": conv,
    "conv_mean": conv_mean,
    "base": {k: (round(v, 3) if isinstance(v, float) else v) for k, v in base.items()},
    "inputs": base_p,
    "sens": sens,
    "per_1pct_margin_fv": per_1pct,
    "vs_prior_undisc_gate_45.8": dict(new_gate=round(base["gate"], 3), change_pct=round((base["gate"] / 45.753 - 1) * 100, 1)),
    "gate_fv_ratio": round(base["gate"] / base["fv"], 3),
    "price_A": 55.82,
    "price_to_gate": round(55.82 / base["gate"], 2),
}
json.dump(out, open(Path(__file__).with_name("calc_pe_only_out.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
