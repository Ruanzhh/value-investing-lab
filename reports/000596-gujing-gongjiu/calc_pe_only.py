#!/usr/bin/env python3
"""古井贡酒 000596 PE-only 重算（新规则：筛选三性现金转化过关后只走 PE 轨）。
2026-11-06 Asia/Shanghai。常数遵 valuation-rules-v3：hurdle 20%，n=估值日→FY2029年末。
禁止现金流定价轨 / 两轨取低；RI PE、无风险 25×、P/F 只作交叉对照。"""
import json, statistics as st
from datetime import date

ASOF = date(2026, 11, 6)
FY3 = date(2029, 12, 31)
n = (FY3 - ASOF).days / 365.25
H = 0.20
DPS = 4.40  # FY23 4.50 / FY24 5.00 / FY25 4.40 → min
SH = 5.286  # 亿股（A 4.086 + B 1.20）
PX = 105.01  # 2026-11-06 15:52 Asia/Shanghai 腾讯行情

# 年末未复权收盘 × 当年总股本 / 同年归母（与 r2 已核窗口一致）
snap = {
    2016: (44.51, 5.036, 8.2963),
    2017: (66.71, 5.036, 11.4874),
    2018: (53.55, 5.036, 16.9523),
    2019: (133.92, 5.036, 20.9753),
    2020: (275.64, 5.036, 18.5458),
    2021: (249.35, 5.286, 22.9789),
    2022: (268.97, 5.286, 31.4314),
    2023: (234.77, 5.286, 45.8916),
    2024: (171.50, 5.286, 55.1725),
    2025: (135.63, 5.286, 35.4911),
}
pe_hist = {y: round(p * s / ni, 2) for y, (p, s, ni) in snap.items()}
pe_vals = sorted(pe_hist.values())
pe_exit_median = st.median(pe_vals)  # 28.145 仅参照
pe_exit = 23.0  # 主报：弱护城河/区域/去库 → 20–25 带中位附近
ys = sorted(pe_hist)
trim1 = st.median([pe_hist[y] for y in ys[1:]])
trim2 = st.median([pe_hist[y] for y in ys[:-1]])

# 富余现金 2026-09-30（保持到 FY3）：货币+交易性 − 有息 − 合同负债 − 应付票据 − 应付账款 − 其他应付款
excess_cash = 53.1123  # 亿；≈10.05 元/股
xc_ps = excess_cash / SH

# 筛选用现金转化（东方财富年报接口 2026-11-06 拉取）
fin = {
    2021: dict(ni=22.98, ocf=52.54, capex=5.78, rev=132.70),
    2022: dict(ni=31.43, ocf=31.08, capex=15.80, rev=167.13),
    2023: dict(ni=45.89, ocf=44.96, capex=23.81, rev=202.54),
    2024: dict(ni=55.17, ocf=47.28, capex=24.27, rev=235.78),
    2025: dict(ni=35.49, ocf=19.47, capex=16.63, rev=188.32),
}
conv = {y: round(v["ocf"] / v["ni"], 3) for y, v in fin.items()}
# 对照 k≈(OCF−维持性capex)/NI；维持性未知时用 min(capex, D&A≈8) 粗代理不进定价
k_cross = {y: round((v["ocf"] - min(v["capex"], 8.0)) / v["ni"], 3) for y, v in fin.items()}

# 基准情景（与 r2 一致，经驱动树确认）：营收≈180、净利率≈19% → NI3=34.2
NI3 = 34.2
pe_ri = (1 - 0.03 / 0.18) / (0.07 - 0.03)  # 剩余收益正当 PE，仅交叉

def fv_pe(ni, pe):
    return (ni * pe + excess_cash) / SH

def gate(fv, h=H):
    return (fv + n * DPS) / (1 + h) ** n

fv = fv_pe(NI3, pe_exit)
b20 = gate(fv, 0.20)
b22 = gate(fv, 0.22)

# 交叉（不进定价）
fv_ri = fv_pe(NI3, pe_ri)
fv_rf25 = fv_pe(NI3, 25)
fv_rf30 = fv_pe(NI3, 30)

# 敏感度：对合理价 ±10%
sens = {}
for name, lo_fv, hi_fv in [
    ("NI3", fv_pe(NI3 * 0.9, pe_exit), fv_pe(NI3 * 1.1, pe_exit)),
    ("pe_exit", fv_pe(NI3, pe_exit * 0.9), fv_pe(NI3, pe_exit * 1.1)),
    ("excess_cash", (NI3 * pe_exit + excess_cash * 0.9) / SH, (NI3 * pe_exit + excess_cash * 1.1) / SH),
]:
    sens[name] = dict(
        minus10=round((lo_fv / fv - 1) * 100, 1),
        plus10=round((hi_fv / fv - 1) * 100, 1),
        gate_minus10=round(gate(lo_fv), 2),
        gate_plus10=round(gate(hi_fv), 2),
    )
# 收入/净利率分解（NI3=rev×m）：等价于对 NI3，另列 rev0 / m 示意
rev3, m = 180.0, 0.19
assert abs(rev3 * m - NI3) < 0.01
sens["rev3"] = sens["NI3"]  # 线性
sens["net_margin"] = sens["NI3"]

old_gate = 89.3
gate_chg = round((b20 / old_gate - 1) * 100, 1)

# 翻倍交叉：从现价 / 从闸价，三年后 15/20/25×
def flip(entry, mult):
    exit_px = fv_pe(NI3, mult)
    return round(((exit_px + n * DPS) / entry) , 3)

out = {
    "as_of": "2026-11-06 Asia/Shanghai",
    "rule": "PE-only; exit PE judged in 20-30 by business quality (hist median reference only)",
    "px": PX,
    "shares_yi": SH,
    "n": n,
    "fy3": str(FY3),
    "hurdle": H,
    "dps_min3": DPS,
    "pe_hist_same_fy": pe_hist,
    "pe_exit_median": pe_exit_median,
    "pe_exit_main": pe_exit,
    "trim_medians": [trim1, trim2],
    "trim_ok": abs(trim1 - pe_exit_median) / pe_exit_median <= 0.10 and abs(trim2 - pe_exit_median) / pe_exit_median <= 0.10,
    "P20": sorted(pe_vals)[int(0.2 * (len(pe_vals) - 1))],
    "P80": sorted(pe_vals)[int(0.8 * (len(pe_vals) - 1))],
    "pe_min_snap": min(pe_vals),
    "excess_cash_yi": excess_cash,
    "xc_ps": xc_ps,
    "NI3_base": NI3,
    "rev3_base": rev3,
    "net_margin_base": m,
    "FV3_pe": round(fv, 3),
    "B20": round(b20, 3),
    "B22": round(b22, 3),
    "gate_fv_ratio": round(b20 / fv, 3),
    "cross_only": {
        "pe_ri": pe_ri,
        "FV3_ri": round(fv_ri, 3),
        "spread_pe_over_ri": round(fv / fv_ri, 3),
        "FV3_rf25": round(fv_rf25, 3),
        "spread_pe_over_rf25": round(fv / fv_rf25, 3),
        "FV3_rf30": round(fv_rf30, 3),
    },
    "conv_ocf_ni": conv,
    "k_cross_proxy": k_cross,
    "sens_fv_pct": {k: {"minus10": v["minus10"], "plus10": v["plus10"]} for k, v in sens.items()},
    "sens_gate": {k: {"minus10": v["gate_minus10"], "plus10": v["gate_plus10"]} for k, v in sens.items()},
    "vs_old_dual_track_gate_89.3": {"new_gate": round(b20, 3), "change_pct": gate_chg},
    "flip_from_px": {str(m): flip(PX, m) for m in (15, 20, 25)},
    "flip_from_b20": {str(m): flip(b20, m) for m in (15, 20, 25)},
    "ttm_ni": 18.49,
    "pe_ttm": round(PX * SH / 18.49, 2),
    "earn_yield": round(18.49 / (PX * SH), 4),
    "pe_exit_reason": "区域白酒龙头+轻资本现金转化周期修正后过→不低于20；难替代第3/省外退缩/去库修复/费用粘性→不得用增长期中位28.1，也难顶25–30强护城河上沿；取弱护城河区域周期带20–25之中位附近23",
    "pe_hist_median_ref_only": pe_exit_median,
    "gate_vs_prior_pe116_pct": round((b20 / 115.975 - 1) * 100, 1),
    "gate_vs_r2_893_pct": round((b20 / 89.3 - 1) * 100, 1),
    "note_pe_exit": "主报已改为 pe_exit_main=23；pe_exit_median 仅历史参照",
    "old_r2": {"FV3_headline_ri": 145, "B20_ri": 89.3, "FV3_pe_side": 192, "B20_pe_side": 115.9, "NI3": 34.2},
}
path = "calc_pe_only_out.json"
json.dump(out, open(path, "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
