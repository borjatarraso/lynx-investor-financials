"""Financials-focused report synthesis engine.

Generates the weighted overall score + verdict + strengths/risks for a
Financials sector company. Weights adapt by both tier and Financials
lifecycle stage. Screening checklist covers the 10 most important
Financials quality criteria.
"""

from __future__ import annotations

import math

from lynx_finance.models import AnalysisConclusion, AnalysisReport, CompanyStage, CompanyTier, JurisdictionTier


def _safe(val, default: float = 0.0) -> float:
    if val is None or isinstance(val, bool):
        return default
    try:
        f = float(val)
        return default if (math.isnan(f) or math.isinf(f)) else f
    except (TypeError, ValueError):
        return default


# Weights: (valuation, profitability, solvency, growth, finance_quality)
_WEIGHTS = {
    # Platforms & Mature: capital + quality + profitability dominate
    (CompanyStage.PLATFORM, CompanyTier.MEGA):  (0.20, 0.20, 0.20, 0.15, 0.25),
    (CompanyStage.PLATFORM, CompanyTier.LARGE): (0.20, 0.20, 0.20, 0.15, 0.25),
    (CompanyStage.MATURE, CompanyTier.MEGA):    (0.20, 0.20, 0.20, 0.15, 0.25),
    (CompanyStage.MATURE, CompanyTier.LARGE):   (0.20, 0.20, 0.20, 0.15, 0.25),
    (CompanyStage.MATURE, CompanyTier.MID):     (0.20, 0.15, 0.20, 0.20, 0.25),

    # Scale-up: growth still matters but capital + quality rising
    (CompanyStage.SCALE, CompanyTier.LARGE): (0.15, 0.15, 0.25, 0.20, 0.25),
    (CompanyStage.SCALE, CompanyTier.MID):   (0.15, 0.15, 0.25, 0.20, 0.25),
    (CompanyStage.SCALE, CompanyTier.SMALL): (0.10, 0.10, 0.30, 0.20, 0.30),

    # Expansion / hyper-growth: capital + quality + growth
    (CompanyStage.GROWTH, CompanyTier.LARGE): (0.15, 0.15, 0.25, 0.20, 0.25),
    (CompanyStage.GROWTH, CompanyTier.MID):   (0.10, 0.15, 0.30, 0.20, 0.25),
    (CompanyStage.GROWTH, CompanyTier.SMALL): (0.10, 0.10, 0.30, 0.20, 0.30),
    (CompanyStage.GROWTH, CompanyTier.MICRO): (0.05, 0.05, 0.35, 0.20, 0.35),

    # De Novo / Startup: solvency / capital adequacy + quality dominate
    (CompanyStage.STARTUP, CompanyTier.SMALL): (0.10, 0.05, 0.40, 0.15, 0.30),
    (CompanyStage.STARTUP, CompanyTier.MICRO): (0.05, 0.05, 0.45, 0.10, 0.35),
    (CompanyStage.STARTUP, CompanyTier.NANO):  (0.05, 0.05, 0.45, 0.10, 0.35),
}
_DEFAULT_WEIGHTS = (0.15, 0.15, 0.25, 0.20, 0.25)


def generate_conclusion(report: AnalysisReport) -> AnalysisConclusion:
    c = AnalysisConclusion()
    tier, stage = report.profile.tier, report.profile.stage

    val_score = _score_valuation(report)
    prof_score = _score_profitability(report)
    solv_score = _score_solvency(report)
    grow_score = _score_growth(report)
    quality_score = _safe(report.finance_quality.quality_score) if report.finance_quality else 0

    c.category_scores = {"valuation": round(val_score, 1), "profitability": round(prof_score, 1),
                         "solvency": round(solv_score, 1), "growth": round(grow_score, 1),
                         "finance_quality": round(quality_score, 1)}

    w = _WEIGHTS.get((stage, tier), _DEFAULT_WEIGHTS)
    c.overall_score = round(val_score * w[0] + prof_score * w[1] + solv_score * w[2] + grow_score * w[3] + quality_score * w[4], 1)
    c.verdict = _verdict(c.overall_score)
    c.category_summaries = _build_summaries(report)
    c.strengths = _find_strengths(report)
    c.risks = _find_risks(report)
    c.summary = _build_narrative(report, c)
    c.tier_note = _tier_note(tier)
    c.stage_note = _stage_note(stage)
    c.screening_checklist = _finance_screening(report)
    return c


def _verdict(score: float) -> str:
    if score >= 75: return "Strong Buy"
    if score >= 60: return "Buy"
    if score >= 45: return "Hold"
    if score >= 30: return "Caution"
    return "Avoid"


def _score_valuation(r: AnalysisReport) -> float:
    v = r.valuation
    if v is None:
        return 50.0
    score = 50.0
    stage = r.profile.stage

    # P/TBV — the bank anchor (lower is cheaper)
    ptbv = _safe(v.price_to_tangible_book_value, None)
    if ptbv is not None:
        if ptbv < 1.0: score += 20
        elif ptbv < 1.3: score += 12
        elif ptbv < 1.8: score += 4
        elif ptbv > 2.5: score -= 12
        elif ptbv > 3.5: score -= 20

    # P/E for mature financials
    if stage in (CompanyStage.MATURE, CompanyStage.PLATFORM, CompanyStage.SCALE):
        pe = _safe(v.pe_trailing, None)
        if pe is not None and pe > 0:
            if pe < 10: score += 12
            elif pe < 14: score += 6
            elif pe > 20: score -= 8

    # Dividend yield bonus for mature / platform
    if stage in (CompanyStage.MATURE, CompanyStage.PLATFORM):
        dy = _safe(v.dividend_yield, None)
        if dy is not None:
            if dy > 0.04: score += 8
            elif dy > 0.025: score += 4

    # Excess capital surplus
    excess = _safe(v.excess_capital_pct_market_cap, None)
    if excess is not None and excess > 0.05:
        score += 6

    # Cash-to-market-cap bonus for fintech / startup
    ctm = _safe(v.cash_to_market_cap, None)
    if ctm is not None and stage == CompanyStage.STARTUP:
        if ctm > 0.50: score += 10
        elif ctm > 0.25: score += 5

    return max(0, min(100, score))


def _score_profitability(r: AnalysisReport) -> float:
    p = r.profitability
    stage = r.profile.stage
    if p is None:
        return 50.0
    score = 50.0

    # ROE / ROTCE — the franchise quality anchor
    rotce = _safe(p.rotce, None)
    roe = _safe(p.roe, None)
    quality_return = rotce if rotce is not None else roe
    if quality_return is not None:
        if quality_return >= 0.17: score += 20
        elif quality_return >= 0.12: score += 12
        elif quality_return >= 0.08: score += 4
        elif quality_return >= 0: score -= 5
        else: score -= 15

    # NIM
    nim = _safe(p.nim, None)
    if nim is not None:
        if nim >= 0.035: score += 8
        elif nim >= 0.025: score += 4
        elif nim < 0.015: score -= 5

    # Efficiency ratio
    eff = _safe(p.efficiency_ratio, None)
    if eff is not None:
        if eff < 0.50: score += 10
        elif eff < 0.60: score += 5
        elif eff > 0.75: score -= 10

    # Combined ratio (insurers)
    cr = _safe(p.combined_ratio, None)
    if cr is not None:
        if cr < 0.92: score += 15
        elif cr < 0.98: score += 8
        elif cr < 1.02: score -= 5
        else: score -= 15

    # Fee income diversification
    fee = _safe(p.fee_income_ratio, None)
    if fee is not None and fee >= 0.30:
        score += 5

    return max(0, min(100, score))


def _score_solvency(r: AnalysisReport) -> float:
    s = r.solvency
    if s is None:
        return 50.0
    score = 50.0
    stage = r.profile.stage

    # CET1 ratio — primary signal
    cet1 = _safe(s.cet1_ratio, None)
    if cet1 is not None:
        if cet1 >= 0.16: score += 20
        elif cet1 >= 0.13: score += 12
        elif cet1 >= 0.105: score += 4
        elif cet1 >= 0.085: score -= 10
        else: score -= 25

    # NPL ratio
    npl = _safe(s.npl_ratio, None)
    if npl is not None:
        if npl < 0.01: score += 12
        elif npl < 0.02: score += 6
        elif npl < 0.04: score -= 5
        else: score -= 15

    # NPL coverage
    cov = _safe(s.npl_coverage_ratio, None)
    if cov is not None:
        if cov >= 1.0: score += 6
        elif cov >= 0.7: score += 3
        else: score -= 6

    # Texas Ratio — distress
    tx = _safe(s.texas_ratio, None)
    if tx is not None:
        if tx > 1.0: score -= 25
        elif tx > 0.5: score -= 12
        elif tx < 0.10: score += 4

    # LDR optimal range
    ldr = _safe(s.loan_to_deposit_ratio, None)
    if ldr is not None:
        if 0.70 <= ldr <= 0.90: score += 6
        elif ldr > 1.0: score -= 8

    # LCR
    lcr = _safe(s.liquidity_coverage_ratio, None)
    if lcr is not None and lcr >= 1.10:
        score += 5

    # Solvency ratio (insurers)
    sr = _safe(s.solvency_ratio, None)
    if sr is not None:
        if sr >= 2.0: score += 10
        elif sr >= 1.5: score += 5
        elif sr < 1.0: score -= 20

    # Capital-light financials: leverage check
    if not cet1 and stage in (CompanyStage.GROWTH, CompanyStage.STARTUP):
        de = _safe(s.debt_to_equity, None)
        if de is not None and de > 1.5:
            score -= 10

    return max(0, min(100, score))


def _score_growth(r: AnalysisReport) -> float:
    g = r.growth
    if g is None:
        return 50.0
    score = 50.0
    stage = r.profile.stage

    # Revenue growth
    rg = _safe(g.revenue_growth_yoy, None)
    if rg is not None:
        if stage in (CompanyStage.STARTUP, CompanyStage.GROWTH):
            if rg > 0.25: score += 18
            elif rg > 0.12: score += 10
            elif rg > 0.05: score += 4
            elif rg < 0: score -= 12
        else:
            if rg > 0.10: score += 12
            elif rg > 0.04: score += 6
            elif rg < -0.05: score -= 12

    # Tangible book value compounding (durable signal)
    tbg = _safe(g.tangible_book_growth_yoy, None)
    if tbg is not None:
        if tbg > 0.10: score += 12
        elif tbg > 0.05: score += 6
        elif tbg < 0: score -= 8

    # Loan growth (banks)
    lg = _safe(g.loan_growth_yoy, None)
    if lg is not None:
        if 0.04 <= lg <= 0.10: score += 6
        elif lg > 0.20: score -= 5  # aggressive — credit risk
        elif lg < -0.05: score -= 5

    # Deposit growth
    dg = _safe(g.deposit_growth_yoy, None)
    if dg is not None and dg > 0.04:
        score += 4

    # Net inflows (asset managers)
    flows = _safe(g.net_inflows_pct_aum, None)
    if flows is not None:
        if flows > 0.05: score += 8
        elif flows > 0: score += 3
        elif flows < -0.03: score -= 10

    # Premium growth (insurers)
    pg = _safe(g.premium_growth_yoy, None)
    if pg is not None:
        if pg > 0.10: score += 6
        elif pg > 0.04: score += 3

    # Share dilution / buybacks
    dil = _safe(g.shares_growth_yoy, None)
    if dil is not None:
        if dil < -0.04: score += 8  # aggressive buyback
        elif dil < -0.01: score += 5
        elif dil < 0.02: score += 2
        elif dil > 0.05: score -= 8
        elif dil > 0.10: score -= 15

    return max(0, min(100, score))


def _finance_screening(r: AnalysisReport) -> dict:
    """Ten-point Financials screening checklist."""
    checks: dict = {}
    p, s, g, ss, fq = r.profitability, r.solvency, r.growth, r.share_structure, r.finance_quality
    stage = r.profile.stage

    # 1. CET1 above 11% (well-capitalized)
    cet1 = _safe(s.cet1_ratio, None) if s else None
    if cet1 is not None:
        checks["cet1_well_capitalized"] = cet1 >= 0.11
    else:
        # If insurance/non-bank, fall back to solvency ratio
        sr = _safe(s.solvency_ratio, None) if s else None
        if sr is not None:
            checks["cet1_well_capitalized"] = sr >= 1.5
        else:
            checks["cet1_well_capitalized"] = None

    # 2. NPL ratio < 2%
    npl = _safe(s.npl_ratio, None) if s else None
    checks["asset_quality_healthy"] = npl < 0.02 if npl is not None else None

    # 3. ROE / ROTCE >= 12%
    rotce = _safe(p.rotce, None) if p else None
    roe = _safe(p.roe, None) if p else None
    quality_return = rotce if rotce is not None else roe
    checks["high_returns"] = quality_return >= 0.12 if quality_return is not None else None

    # 4. Efficiency ratio < 65%
    eff = _safe(p.efficiency_ratio, None) if p else None
    checks["efficient_cost_base"] = eff < 0.65 if eff is not None else None

    # 5. Combined ratio < 100% (insurers)
    cr = _safe(p.combined_ratio, None) if p else None
    checks["profitable_underwriting"] = cr < 1.00 if cr is not None else None

    # 6. LDR in optimal range (60-100%)
    ldr = _safe(s.loan_to_deposit_ratio, None) if s else None
    checks["liquidity_optimal"] = 0.60 <= ldr <= 1.00 if ldr is not None else None

    # 7. Sustainable dividend (yield > 0 and payout reasonable)
    if r.valuation:
        dy = _safe(r.valuation.dividend_yield, None)
        checks["dividend_paying"] = dy > 0 if dy is not None else None
    else:
        checks["dividend_paying"] = None

    # 8. Capital return / no dilution
    dil = _safe(g.shares_growth_yoy, None) if g else None
    checks["no_excess_dilution"] = dil < 0.03 if dil is not None else None

    # 9. Texas Ratio < 50% (distress check)
    tx = _safe(s.texas_ratio, None) if s else None
    if tx is not None:
        checks["no_distress_signal"] = tx < 0.50
    elif npl is not None:
        checks["no_distress_signal"] = npl < 0.04
    else:
        checks["no_distress_signal"] = None

    # 10. Tier 1/2 jurisdiction
    jt = r.profile.jurisdiction_tier
    checks["tier_1_2_jurisdiction"] = jt in (JurisdictionTier.TIER_1, JurisdictionTier.TIER_2) if jt != JurisdictionTier.UNKNOWN else None

    return checks


def _build_summaries(r: AnalysisReport) -> dict[str, str]:
    summaries: dict[str, str] = {}
    if r.valuation:
        ptbv = _safe(r.valuation.price_to_tangible_book_value, None)
        if ptbv is not None:
            summaries["valuation"] = f"P/TBV: {ptbv:.2f}x"
        else:
            pe = _safe(r.valuation.pe_trailing, None)
            summaries["valuation"] = f"P/E of {pe:.1f}" if pe else "Limited valuation data"
    else:
        summaries["valuation"] = "Limited valuation data"

    if r.profitability:
        rotce = _safe(r.profitability.rotce, None)
        roe = _safe(r.profitability.roe, None)
        anchor = rotce if rotce is not None else roe
        if anchor is not None:
            label = "ROTCE" if rotce is not None else "ROE"
            summaries["profitability"] = f"{label}: {anchor*100:.1f}%"
        else:
            cr = _safe(r.profitability.combined_ratio, None)
            summaries["profitability"] = f"Combined ratio: {cr*100:.1f}%" if cr is not None else "Limited data"
    else:
        summaries["profitability"] = "Limited data"

    if r.solvency:
        cet1 = _safe(r.solvency.cet1_ratio, None)
        if cet1 is not None:
            summaries["solvency"] = f"CET1: {cet1*100:.1f}%"
        else:
            npl = _safe(r.solvency.npl_ratio, None)
            if npl is not None:
                summaries["solvency"] = f"NPL ratio: {npl*100:.2f}%"
            else:
                summaries["solvency"] = "Limited solvency data"
    else:
        summaries["solvency"] = "Limited solvency data"

    if r.growth:
        tbg = _safe(r.growth.tangible_book_growth_yoy, None)
        if tbg is not None:
            summaries["growth"] = f"TBV/share growth: {tbg*100:.1f}%/yr"
        else:
            rg = _safe(r.growth.revenue_growth_yoy, None)
            summaries["growth"] = f"Revenue growth: {rg*100:.1f}%/yr" if rg is not None else "Limited growth data"
    else:
        summaries["growth"] = "Limited growth data"

    summaries["finance_quality"] = (r.finance_quality.competitive_position or "N/A") if r.finance_quality else "N/A"
    return summaries


def _find_strengths(r: AnalysisReport) -> list[str]:
    strengths = []
    if r.solvency:
        cet1 = _safe(r.solvency.cet1_ratio, None)
        if cet1 is not None and cet1 >= 0.13:
            strengths.append(f"Strong CET1 capital ({cet1*100:.1f}%) — comfortable buffer above well-capitalized")
        npl = _safe(r.solvency.npl_ratio, None)
        if npl is not None and npl < 0.01:
            strengths.append(f"Pristine asset quality (NPL {npl*100:.2f}%)")
        ldr = _safe(r.solvency.loan_to_deposit_ratio, None)
        if ldr is not None and 0.70 <= ldr <= 0.90:
            strengths.append(f"Optimal LDR ({ldr*100:.0f}%) — balanced funding & lending")
    if r.profitability:
        rotce = _safe(r.profitability.rotce, None)
        if rotce is not None and rotce >= 0.15:
            strengths.append(f"Best-in-class ROTCE ({rotce*100:.1f}%)")
        eff = _safe(r.profitability.efficiency_ratio, None)
        if eff is not None and eff < 0.55:
            strengths.append(f"Strong efficiency ratio ({eff*100:.0f}%)")
        cr = _safe(r.profitability.combined_ratio, None)
        if cr is not None and cr < 0.95:
            strengths.append(f"Profitable underwriting ({cr*100:.1f}% combined ratio)")
    if r.growth:
        tbg = _safe(r.growth.tangible_book_growth_yoy, None)
        if tbg is not None and tbg > 0.10:
            strengths.append(f"Strong TBV/share compounding ({tbg*100:.1f}%/yr)")
        flows = _safe(r.growth.net_inflows_pct_aum, None)
        if flows is not None and flows > 0.05:
            strengths.append(f"Strong AUM inflows ({flows*100:.1f}% of starting AUM)")
    if r.share_structure and r.share_structure.buyback_intensity:
        if "buyback" in (r.share_structure.buyback_intensity or "").lower() and "Aggressive" in r.share_structure.buyback_intensity:
            strengths.append("Aggressive buyback program — accretive capital return")
    if r.profile.jurisdiction_tier == JurisdictionTier.TIER_1:
        strengths.append("Tier 1 jurisdiction (strong supervision: Basel III / Solvency II)")
    return strengths[:6]


def _find_risks(r: AnalysisReport) -> list[str]:
    risks = []
    if r.solvency:
        cet1 = _safe(r.solvency.cet1_ratio, None)
        if cet1 is not None and cet1 < 0.105:
            risks.append(f"CET1 below well-capitalized buffer ({cet1*100:.1f}%)")
        npl = _safe(r.solvency.npl_ratio, None)
        if npl is not None and npl > 0.04:
            risks.append(f"Elevated NPL ratio ({npl*100:.1f}%) — credit-cycle stress")
        tx = _safe(r.solvency.texas_ratio, None)
        if tx is not None and tx > 0.50:
            risks.append(f"Texas Ratio {tx*100:.0f}% — distress-level loan losses vs capital")
        ldr = _safe(r.solvency.loan_to_deposit_ratio, None)
        if ldr is not None and ldr > 1.0:
            risks.append(f"LDR {ldr*100:.0f}% — funding-stress risk if deposits flee")
    if r.profitability:
        rotce = _safe(r.profitability.rotce, None)
        roe = _safe(r.profitability.roe, None)
        anchor = rotce if rotce is not None else roe
        if anchor is not None and anchor < 0.05:
            risks.append(f"Subscale returns ({anchor*100:.1f}%) — franchise quality questionable")
        eff = _safe(r.profitability.efficiency_ratio, None)
        if eff is not None and eff > 0.75:
            risks.append(f"Bloated cost base (efficiency ratio {eff*100:.0f}%)")
        cr = _safe(r.profitability.combined_ratio, None)
        if cr is not None and cr > 1.05:
            risks.append(f"Heavy underwriting loss ({cr*100:.1f}% combined ratio)")
    if r.growth:
        dil = _safe(r.growth.shares_growth_yoy, None)
        if dil is not None and dil > 0.06:
            risks.append(f"Heavy share dilution ({dil*100:.1f}%/yr)")
        flows = _safe(r.growth.net_inflows_pct_aum, None)
        if flows is not None and flows < -0.03:
            risks.append(f"AUM net outflows ({flows*100:.1f}% of starting AUM)")
        lg = _safe(r.growth.loan_growth_yoy, None)
        if lg is not None and lg > 0.20:
            risks.append(f"Aggressive loan growth ({lg*100:.0f}%/yr) — credit-risk vintage")
    if r.profile.jurisdiction_tier == JurisdictionTier.TIER_3:
        risks.append("Tier 3 jurisdiction — elevated regulatory/geopolitical risk")
    if r.profile.stage == CompanyStage.STARTUP:
        risks.append("De Novo / Early-Stage — execution and funding risk dominate")
    return risks[:6]


def _build_narrative(r: AnalysisReport, c: AnalysisConclusion) -> str:
    parts = [f"{r.profile.name} ({r.profile.tier.value}, {r.profile.stage.value}) scores {c.overall_score:.0f}/100 — '{c.verdict}'."]
    if c.strengths:
        parts.append(f"Strengths: {c.strengths[0].lower()}" + (f" and {c.strengths[1].lower()}" if len(c.strengths) > 1 else "") + ".")
    if c.risks:
        parts.append(f"Risks: {c.risks[0].lower()}" + (f" and {c.risks[1].lower()}" if len(c.risks) > 1 else "") + ".")
    return " ".join(parts)


def _tier_note(tier: CompanyTier) -> str:
    return {
        CompanyTier.MEGA: "Mega-cap: G-SIB / dominant franchise. CET1 surcharge applies. ROTCE compounding is the signal.",
        CompanyTier.LARGE: "Large-cap: established franchise. Capital adequacy + ROE drive the thesis.",
        CompanyTier.MID: "Mid-cap regional / specialty: watch loan-to-deposit and credit cycle exposure.",
        CompanyTier.SMALL: "Small-cap financials: execution & funding risk elevated. Capital adequacy is critical.",
        CompanyTier.MICRO: "Micro-cap: survival metrics dominate. CET1, NPLs, deposit base must-checks.",
        CompanyTier.NANO: "Nano-cap: highly speculative. Most metrics unreliable — capital backing only.",
    }.get(tier, "")


def _stage_note(stage: CompanyStage) -> str:
    return {
        CompanyStage.PLATFORM: "Systemic / Dominant Franchise: regulatory + scale moats compound for decades. ROTCE & DDM primary.",
        CompanyStage.MATURE: "Mature / Cash-Generative: predictable earnings, buybacks, dividends. Excess Return Model & DDM primary.",
        CompanyStage.SCALE: "Scaling Regional: growth still strong, capital + asset quality the gates. Watch LDR & loan-growth quality.",
        CompanyStage.GROWTH: "Expansion: rapid loan / premium / AUM growth. Quality of growth (vintage credit) matters most.",
        CompanyStage.STARTUP: "De Novo / Early-Stage: capital adequacy and funding access dominate. Path to scale is the key risk.",
    }.get(stage, "")
