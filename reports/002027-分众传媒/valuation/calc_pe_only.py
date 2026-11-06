#!/usr/bin/env python3
"""分众传媒 002027 PE-only 重算（筛选三性现金转化打折×0.92 后只走 PE 轨）。
2026-11-06 Asia/Shanghai。常数遵 valuation-rules-v3：hurdle 20%（B档）、
n=估值日→FY2029年末、含息=(FV+n×DPS)/(1+h)^n、不含息=FV/(1+h)^n。
禁止股息率定价轨 / FCF 定价轨 / 两轨取低；历史 P/F、股息率、DDM、无风险收益倒数只作交叉对照。

退出市盈率主报硬规则（SIMPLE-FLOW §4 · 2026-11-06）：约20～30内按生意质量/周期/定价权判断取值；
历史同年PE中位数等只作参照，不得直接主报。本轮主报 pe_exit=20（带内下沿）。
"""
from pathlib import Path
import json
import statistics as st
from datetime import date

as_of = date(2026, 11, 6)
fy3 = date(2029, 12, 31)
n = (fy3 - as_of).days / 365.25
H = 0.20
DPS = 0.33  # DPS_min3 = FY23–25 每股分红最小值
px = 5.51   # 2026-11-05 收盘（Yahoo/公开行情）

# 股本：现有 144.42199726 亿 + 新潮发行约 15.3540509 亿（分红调整后修订稿；交割未完成）
sh0 = 144.42199726
newsh = 15.3540509
sh_yi = sh0 + newsh  # ≈159.776

# 历史同年 PE 快照（仅参照，不进定价）——谷底 2022 剔除出基窗
pe_snaps = {2021: 21.85, 2022: 40.29, 2023: 20.87, 2024: 21.75, 2025: 21.85}
keep = [pe_snaps[y] for y in (2021, 2023, 2024, 2025)]
pe_hist_median_ref = round(st.median(keep), 2)  # 21.8 仅参照

# 主报退出 PE：按生意质量/周期/定价权判断 → 带内下沿 20（见 README.md）
pe_exit = 20.0

# —— 基准经营情景（沿用 11-05；本轮未改经营假设）——
rev_fy26 = 122.0
rev_cagr = 0.015
rev_fy29 = rev_fy26 * (1 + rev_cagr) ** 3
core_margin = 0.360
xinchao_ni = 0.54
ni3_raw = rev_fy29 * core_margin + xinchao_ni

# 现金转化：独立挑刺后改判「打折×0.92」（正常年2023–25扣租/核心均值≈0.915；见 review_report.md）
cash_conv_haircut = 0.92
ni3 = ni3_raw * cash_conv_haircut

fv = ni3 * pe_exit / sh_yi
gate_with_div = (fv + n * DPS) / (1 + H) ** n
gate_ex_div = fv / (1 + H) ** n

# 交叉对照（不进定价）
# 股息率法（旧腿，仅展示）
yl = [0.338 / 8.19, 0.33 / 6.32, 0.33 / 7.03, 0.34 / 7.37]
y_med = st.median(yl)
payout = 0.95
fv_div_cross = (ni3 / sh_yi) * payout / y_med
# DDM 展示
dps_post = DPS * (sh0 / sh_yi)
r_ddm, g_ddm = 0.09, 0.02
fv_ddm = dps_post * (1 + g_ddm) ** 3 / (r_ddm - g_ddm)

# 扣租现金转化历史（亿元；出处 fcf_dividend_stress / 年报）
conv_hist = {
    2021: dict(ocf=95.90, rent=29.24, after_rent=66.66, core=54.14),
    2022: dict(ocf=66.99, rent=27.98, after_rent=39.01, core=23.94),
    2023: dict(ocf=76.78, rent=31.82, after_rent=44.96, core=43.74),
    2024: dict(ocf=66.42, rent=30.60, after_rent=35.82, core=46.68),
    2025: dict(ocf=72.09, rent=25.81, after_rent=46.28, core=48.71),
}
for y, v in conv_hist.items():
    v["ocf_ni"] = round(v["ocf"] / v["core"], 3)
    v["ar_ni"] = round(v["after_rent"] / v["core"], 3)

ar_ratios = [v["ar_ni"] for v in conv_hist.values()]
ar_excl22 = [conv_hist[y]["ar_ni"] for y in (2021, 2023, 2024, 2025)]
ocf_ratios = [v["ocf_ni"] for v in conv_hist.values()]

# 对照锚点
old_tr, old_ex = 3.93, 3.34                    # 11-05 两轨取低对外
old_pe_tr, old_pe_ex = 4.15, 3.57              # 挑刺前 PE-only（haircut=1.0, pe=21.8）
prior_fv, prior_tr, prior_ex = 5.83, 3.87, 3.28  # 挑刺小修后（haircut=0.92, pe=21.8）— 改前一次

out = {
    "as_of": "2026-11-06 Asia/Shanghai",
    "rule": "PE-only after cash-conversion screen (rent-adjusted); exit PE judged in 20–30 band",
    "px_ref": px,
    "px_date": "2026-11-05 close",
    "n_years": round(n, 6),
    "fy3": str(fy3),
    "hurdle": H,
    "dps_min3": DPS,
    "shares_yi": round(sh_yi, 6),
    "shares_note": "144.422现有+15.354新潮(分红调整后修订稿);交割未完成",
    "pe_exit": pe_exit,
    "pe_exit_judgment": {
        "main": pe_exit,
        "band": "20–30",
        "rationale": "价格三性不过+周期中位偏弱+增速近平台 → 带内下沿20；历史中位21.8仅参照；与独立挑刺「可把退出压到约20」一致。详见 README.md",
        "hist_median_ref_only": pe_hist_median_ref,
        "hist_snaps_keep": keep,
        "hist_not_pricing": True,
    },
    "cash_conversion": {
        "screen": "打折",
        "haircut_applied": cash_conv_haircut,
        "method": "IFRS16下用OCF−偿还租赁负债本金和利息相对核心净利",
        "conv_hist": conv_hist,
        "mean_ocf_ni": round(sum(ocf_ratios) / len(ocf_ratios), 3),
        "mean_ar_ni_all": round(sum(ar_ratios) / len(ar_ratios), 3),
        "mean_ar_ni_excl2022": round(sum(ar_excl22) / len(ar_excl22), 3),
        "note": "独立挑刺后：正常年2023–25扣租/核心均值≈0.915、2024=0.77 → 改判打折×0.92（非干净过）。维持性capex约1–3亿很轻；营运资本未长期吸血。出处 review_report.md §C7。",
    },
    "scenario_base": {
        "rev_fy26": rev_fy26,
        "rev_cagr": rev_cagr,
        "rev_fy29": round(rev_fy29, 2),
        "core_margin": core_margin,
        "xinchao_ni": xinchao_ni,
        "ni3_raw": round(ni3_raw, 2),
        "ni3_after_haircut": round(ni3, 2),
        "assumptions": "单位经济正常年锚利润率;限价无提价;Q3偏弱压FY26;新潮0.54;中位偏弱+1.5%量;独立挑刺后现金转化打折×0.92",
    },
    "fv3_base_pe": round(fv, 2),
    "gate": {
        "with_div_TR": round(gate_with_div, 2),
        "ex_div": round(gate_ex_div, 2),
        "mainline": "待用户原话拍板（含息 vs 不含息）",
        "formula": "含息=(FV+n×DPS)/(1.2)^n；不含息=FV/(1.2)^n",
    },
    "cross_only_not_pricing": {
        "fv_div_yield_method": round(fv_div_cross, 2),
        "yield_median": round(y_med, 4),
        "fv_ddm_r9_g2": round(fv_ddm, 2),
        "spread_pe_vs_ddm": round(fv / fv_ddm, 3) if fv_ddm else None,
        "pe_hist_median_ref": pe_hist_median_ref,
        "note": "股息率法/DDM/历史PE中位只交叉；禁止进定价或与PE取低；历史21.8不得再当主报",
    },
    "vs_prior": {
        "prior_label": "挑刺小修后（haircut0.92 × pe21.8）",
        "prior_fv": prior_fv,
        "prior_gate_TR": prior_tr,
        "prior_gate_ex": prior_ex,
        "new_fv": round(fv, 2),
        "new_gate_TR": round(gate_with_div, 2),
        "new_gate_ex": round(gate_ex_div, 2),
        "chg_fv_pct": round((fv / prior_fv - 1) * 100, 1),
        "chg_TR_pct": round((gate_with_div / prior_tr - 1) * 100, 1),
        "chg_ex_pct": round((gate_ex_div / prior_ex - 1) * 100, 1),
        "reason": "退出PE主报由历史剔谷中位21.8改为判断取值带内下沿20（SIMPLE-FLOW §4 2026-11-06）；NI3/股本/haircut/hurdle未改。相对改前一次合理买入点约−7%/−8%（<15%）。",
    },
    "vs_old_20261105": {
        "old_fv_range": [5.9, 6.3],
        "old_gate_published_TR": old_tr,
        "old_gate_published_ex": old_ex,
        "old_gate_pe_leg_TR": old_pe_tr,
        "old_gate_pe_leg_ex": old_pe_ex,
        "pre_critique_fv": 6.34,
        "pre_critique_gate_TR": 4.15,
        "pre_critique_gate_ex": 3.57,
        "post_critique_fv_pe218": 5.83,
        "post_critique_gate_TR": 3.87,
        "post_critique_gate_ex": 3.28,
        "new_fv": round(fv, 2),
        "new_gate_TR": round(gate_with_div, 2),
        "new_gate_ex": round(gate_ex_div, 2),
        "chg_vs_published_TR_pct": round((gate_with_div / old_tr - 1) * 100, 1),
        "chg_vs_published_ex_pct": round((gate_ex_div / old_ex - 1) * 100, 1),
        "chg_vs_pre_critique_TR_pct": round((gate_with_div / old_pe_tr - 1) * 100, 1),
        "chg_vs_pre_critique_ex_pct": round((gate_ex_div / old_pe_ex - 1) * 100, 1),
        "chg_vs_post_critique_TR_pct": round((gate_with_div / prior_tr - 1) * 100, 1),
        "chg_vs_post_critique_ex_pct": round((gate_ex_div / prior_ex - 1) * 100, 1),
        "reason": "累计：现金转化九折 + 退出PE由21.8（历史中位参照）改为判断主报20。相对改前一次（挑刺后）约−7%/−8%<15%；相对挑刺前PE-only累计约−13%/−16%（累计路径，非单次>15%硬关）。仍只走PE轨，禁止两轨取低。",
    },
    "buy_point_enabled": False,
    "gate_block_reasons": [
        "生意质量三性：价格受管制不通过",
        "新潮未交割，并表利润与股本未定",
        "独立挑刺已完成·小修后可用（仍不得启用买点）",
        "含息/不含息主线待用户原话",
        "扣非同口径一致预期n≥5仍缺",
        "未进正式路由签发",
    ],
    "cross_checks": {
        "earn_yield_at_px_ttm_approx": round(1 / 24.7, 4),
        "static_div_yield": round(0.34 / px, 4),
        "from_px_to_fv_ann": round((fv / px) ** (1 / n) - 1, 4),
        "from_px_to_fv_plus_div_ann": round(((fv + n * DPS) / px) ** (1 / n) - 1, 4),
        "double_in_3y_at_15_25pe_from_gate_TR": {
            str(pe_x): round((ni3 * pe_x / sh_yi + n * DPS) / gate_with_div, 2)
            for pe_x in (15, 20, 25)
        },
    },
}

path = Path(__file__).with_name("calc_pe_only_out.json")
json.dump(out, open(path, "w"), ensure_ascii=False, indent=2)
print(json.dumps(out, ensure_ascii=False, indent=2))
