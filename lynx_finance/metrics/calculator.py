"""Financials-specialized metrics calculation engine.

All calculations are both tier-aware AND stage-aware. This module computes
traditional financial metrics plus Financials-specific indicators:

  * Net Interest Margin (NIM) and Net Interest Spread
  * Yield on Assets and Cost of Funds
  * Efficiency Ratio (Cost-to-Income)
  * Fee Income Ratio (non-interest income share)
  * Capital adequacy: CET1, Tier 1, Total Capital, Leverage Ratio (Basel III)
  * Loan-to-Deposit Ratio (LDR), Loan-to-Asset Ratio
  * NPL Ratio, NPL Coverage, Net Charge-Offs, Cost of Risk
  * Texas Ratio (NPLs / (TCE + Reserves)) — bank distress indicator
  * Liquidity Coverage Ratio (LCR), NSFR
  * Combined / Loss / Expense Ratios (insurers)
  * Investment Yield, Underwriting Margin
  * AUM growth and Effective Fee Rate (asset managers)
  * Excess Return Model intrinsic value (banks)
"""

from __future__ import annotations

import math
from typing import Optional

from datetime import datetime, timedelta

import yfinance as yf

from lynx_finance.models import (
    CompanyStage, CompanyTier, EfficiencyMetrics, FinancialStatement,
    GrowthMetrics, InsiderTransaction, IntrinsicValue, MarketIntelligence,
    FinanceQualityIndicators, ProfitabilityMetrics, ShareStructure,
    SolvencyMetrics, ValuationMetrics,
)


def calc_valuation(
    info: dict, statements: list[FinancialStatement],
    tier: CompanyTier, stage: CompanyStage,
) -> ValuationMetrics:
    v = ValuationMetrics()
    v.pe_trailing = info.get("trailingPE")
    v.pe_forward = info.get("forwardPE")
    v.pb_ratio = info.get("priceToBook")
    v.ps_ratio = info.get("priceToSalesTrailing12Months")
    v.peg_ratio = info.get("pegRatio")
    v.ev_ebitda = info.get("enterpriseToEbitda")
    v.ev_revenue = info.get("enterpriseToRevenue")
    v.dividend_yield = info.get("trailingAnnualDividendYield") or info.get("dividendYield")
    v.enterprise_value = info.get("enterpriseValue")
    v.market_cap = info.get("marketCap")

    if v.pe_trailing and v.pe_trailing > 0:
        v.earnings_yield = 1.0 / v.pe_trailing

    price = info.get("currentPrice") or info.get("regularMarketPrice")
    shares = info.get("sharesOutstanding")

    if price and shares and statements:
        latest = statements[0]
        if latest.free_cash_flow and latest.free_cash_flow > 0:
            v.p_fcf = (price * shares) / latest.free_cash_flow

    # Tangible book / NCAV — useful for distressed financials
    if statements:
        latest = statements[0]
        if latest.total_equity and price and shares:
            tangibles = (latest.total_equity or 0) - (latest.goodwill or 0) - (latest.intangibles or 0)
            if shares > 0 and tangibles > 0:
                tbv_per_share = tangibles / shares
                v.price_to_tangible_book = price / tbv_per_share
                v.price_to_tangible_book_value = v.price_to_tangible_book
        if latest.current_assets and latest.total_liabilities and shares and shares > 0:
            ncav = latest.current_assets - latest.total_liabilities
            ncav_ps = ncav / shares
            if ncav_ps > 0 and price:
                v.price_to_ncav = price / ncav_ps

    total_cash = info.get("totalCash")
    if total_cash and v.market_cap and v.market_cap > 0:
        v.cash_to_market_cap = total_cash / v.market_cap

    # ── Asset-Manager Price-to-AUM
    if statements and v.market_cap and v.market_cap > 0:
        latest = statements[0]
        if latest.aum and latest.aum > 0:
            v.price_to_aum = v.market_cap / latest.aum

    # ── Insurance Price-to-Premium (P&C anchor)
    if statements and v.market_cap and v.market_cap > 0:
        latest = statements[0]
        if latest.earned_premium and latest.earned_premium > 0:
            v.price_to_premium = v.market_cap / latest.earned_premium

    # ── Excess capital surplus vs market cap (CET1 over 12% target)
    if statements and v.market_cap and v.market_cap > 0:
        latest = statements[0]
        if latest.cet1_capital and latest.risk_weighted_assets and latest.risk_weighted_assets > 0:
            cet1_required = latest.risk_weighted_assets * 0.12  # 12% well-capitalized target
            excess = latest.cet1_capital - cet1_required
            if excess > 0:
                v.excess_capital_pct_market_cap = excess / v.market_cap

    return v


def calc_profitability(
    info: dict, statements: list[FinancialStatement],
    tier: CompanyTier, stage: CompanyStage,
) -> ProfitabilityMetrics:
    p = ProfitabilityMetrics()
    p.roe = info.get("returnOnEquity")
    p.roa = info.get("returnOnAssets")
    p.gross_margin = info.get("grossMargins")
    p.operating_margin = info.get("operatingMargins")
    p.net_margin = info.get("profitMargins")

    if not statements:
        return p
    s = statements[0]

    if s.operating_income is not None and s.total_assets and s.total_cash is not None:
        nopat = s.operating_income * 0.79  # assume 21% tax
        invested_capital = s.total_assets - (s.total_cash or 0)
        if invested_capital > 0:
            p.roic = nopat / invested_capital
    if s.free_cash_flow and s.revenue and s.revenue > 0:
        p.fcf_margin = s.free_cash_flow / s.revenue
    if s.ebitda and s.revenue and s.revenue > 0:
        p.ebitda_margin = s.ebitda / s.revenue

    # ── ROTCE — Return on Tangible Common Equity (banks)
    if s.net_income is not None and s.tangible_common_equity and s.tangible_common_equity > 0:
        p.rotce = s.net_income / s.tangible_common_equity
    elif s.net_income is not None and s.total_equity and s.total_equity > 0:
        tce = s.total_equity - (s.goodwill or 0) - (s.intangibles or 0)
        if tce > 0:
            p.rotce = s.net_income / tce

    # ── Net Interest Margin (NIM)
    if s.net_interest_income is not None and s.earning_assets and s.earning_assets > 0:
        p.nim = s.net_interest_income / s.earning_assets
    elif s.interest_income is not None and s.interest_expense is not None and s.earning_assets and s.earning_assets > 0:
        nii = s.interest_income - abs(s.interest_expense)
        p.nim = nii / s.earning_assets
    elif s.net_interest_income is not None and s.total_assets and s.total_assets > 0:
        # Fallback using total assets as proxy
        p.nim = s.net_interest_income / s.total_assets

    # ── Yield on Assets & Cost of Funds
    if s.interest_income and s.earning_assets and s.earning_assets > 0:
        p.yield_on_assets = s.interest_income / s.earning_assets
    if s.interest_expense and s.interest_bearing_liabilities and s.interest_bearing_liabilities > 0:
        p.cost_of_funds = abs(s.interest_expense) / s.interest_bearing_liabilities

    if p.yield_on_assets is not None and p.cost_of_funds is not None:
        p.net_interest_spread = p.yield_on_assets - p.cost_of_funds

    # ── Efficiency Ratio (Cost-to-Income) — non-interest expense / total revenue
    if s.non_interest_expense and s.revenue and s.revenue > 0:
        p.efficiency_ratio = s.non_interest_expense / s.revenue

    # ── Fee Income Ratio
    if s.non_interest_income is not None and s.revenue and s.revenue > 0:
        p.fee_income_ratio = s.non_interest_income / s.revenue

    # ── Pre-provision margin (banks)
    if s.revenue and s.revenue > 0 and s.non_interest_expense is not None:
        pre_provision_profit = s.revenue - s.non_interest_expense
        p.pre_provision_margin = pre_provision_profit / s.revenue

    # ── Insurance: Combined / Loss / Expense ratios
    if s.earned_premium and s.earned_premium > 0:
        if s.losses_incurred is not None:
            p.loss_ratio = s.losses_incurred / s.earned_premium
        if s.underwriting_expenses is not None:
            p.expense_ratio = s.underwriting_expenses / s.earned_premium
        if p.loss_ratio is not None and p.expense_ratio is not None:
            p.combined_ratio = p.loss_ratio + p.expense_ratio
            p.underwriting_margin = 1.0 - p.combined_ratio

    # ── Investment yield (insurers)
    if s.net_investment_income and s.invested_assets and s.invested_assets > 0:
        p.investment_yield = s.net_investment_income / s.invested_assets

    # ── Asset Manager: Effective fee rate (bps)
    if s.management_fees and s.aum and s.aum > 0:
        p.effective_fee_rate_bps = (s.management_fees / s.aum) * 10000  # in basis points

    # ── Asset Manager: Operating margin on AUM-driven revenue
    if s.operating_income is not None and s.revenue and s.revenue > 0 and s.aum:
        p.operating_margin_aum = s.operating_income / s.revenue

    return p


def calc_solvency(
    info: dict, statements: list[FinancialStatement],
    tier: CompanyTier, stage: CompanyStage,
) -> SolvencyMetrics:
    s = SolvencyMetrics()
    s.debt_to_equity = info.get("debtToEquity")
    if s.debt_to_equity:
        s.debt_to_equity /= 100
    s.current_ratio = info.get("currentRatio")
    s.quick_ratio = info.get("quickRatio")
    s.total_debt = info.get("totalDebt")
    s.total_cash = info.get("totalCash")

    if s.total_debt is not None and s.total_cash is not None:
        s.net_debt = s.total_debt - s.total_cash

    shares = info.get("sharesOutstanding")
    market_cap = info.get("marketCap")

    if not statements:
        return s
    st = statements[0]

    if st.ebitda and st.ebitda > 0 and s.total_debt:
        s.debt_to_ebitda = s.total_debt / st.ebitda

    if st.operating_income:
        ie = abs(st.interest_expense) if st.interest_expense else None
        if ie is None and s.total_debt:
            ie = s.total_debt * 0.05
        if ie and ie > 0:
            s.interest_coverage = st.operating_income / ie

    # Altman Z — less meaningful for banks but kept as a generic risk anchor
    if st.total_assets and st.total_assets > 0 and st.revenue and st.revenue > 0:
        ta = st.total_assets
        wc = 0
        if st.current_assets is not None and st.current_liabilities is not None:
            wc = st.current_assets - st.current_liabilities
        re_ = (st.total_equity or 0) * 0.5
        ebit = st.operating_income or 0
        mcap = info.get("marketCap", 0) or 0
        tl = st.total_liabilities or 1
        rev = st.revenue or 0
        z = (1.2 * wc / ta + 1.4 * re_ / ta + 3.3 * ebit / ta +
             0.6 * mcap / tl + 1.0 * rev / ta)
        s.altman_z_score = round(z, 2)

    if st.current_assets is not None and st.current_liabilities is not None:
        s.working_capital = st.current_assets - st.current_liabilities

    if s.total_cash and shares and shares > 0:
        s.cash_per_share = s.total_cash / shares

    # Tangible book value — strip goodwill & intangibles
    if st.total_equity is not None:
        tangibles = st.total_equity - (st.goodwill or 0) - (st.intangibles or 0)
        s.tangible_book_value = tangibles

    if st.current_assets is not None and st.total_liabilities is not None:
        s.ncav = st.current_assets - st.total_liabilities
        if shares and shares > 0:
            s.ncav_per_share = s.ncav / shares

    # ── Capital Adequacy (Basel III)
    if st.cet1_capital and st.risk_weighted_assets and st.risk_weighted_assets > 0:
        s.cet1_ratio = st.cet1_capital / st.risk_weighted_assets
        s.tier1_ratio = s.cet1_ratio  # CET1 is the strict subset of Tier 1
        # Total capital approximated by adding ~2% buffer typical for Tier 2
        s.total_capital_ratio = s.cet1_ratio + 0.02

    # Bank leverage ratio (Tier 1 capital / total exposure)
    if st.cet1_capital and st.total_assets and st.total_assets > 0:
        s.leverage_ratio = st.cet1_capital / st.total_assets

    # ── Loan-to-Deposit (LDR) and Loan-to-Asset
    if st.total_loans and st.total_deposits and st.total_deposits > 0:
        s.loan_to_deposit_ratio = st.total_loans / st.total_deposits
    if st.total_loans and st.total_assets and st.total_assets > 0:
        s.loan_to_asset_ratio = st.total_loans / st.total_assets

    # ── Asset Quality
    if st.non_performing_loans is not None and st.total_loans and st.total_loans > 0:
        s.npl_ratio = st.non_performing_loans / st.total_loans
    if st.allowance_for_loan_losses is not None and st.non_performing_loans and st.non_performing_loans > 0:
        s.npl_coverage_ratio = st.allowance_for_loan_losses / st.non_performing_loans

    # Net Charge-Off Ratio
    if st.net_charge_offs is not None and st.total_loans and st.total_loans > 0:
        s.net_charge_off_ratio = abs(st.net_charge_offs) / st.total_loans

    # Cost of Risk — provisions / average loans
    if st.provision_for_credit_losses is not None and st.total_loans and st.total_loans > 0:
        avg_loans = st.total_loans
        if len(statements) >= 2 and statements[1].total_loans:
            avg_loans = (st.total_loans + statements[1].total_loans) / 2
        if avg_loans > 0:
            s.cost_of_risk = abs(st.provision_for_credit_losses) / avg_loans

    # ── Texas Ratio — distress indicator: NPL / (TCE + Reserves)
    if st.non_performing_loans and st.non_performing_loans > 0:
        tce = s.tangible_book_value or 0
        reserves = st.allowance_for_loan_losses or 0
        denom = tce + reserves
        if denom > 0:
            s.texas_ratio = st.non_performing_loans / denom

    # ── Reserve adequacy for insurers
    if st.insurance_reserves and st.earned_premium and st.earned_premium > 0:
        s.reserve_to_premium = st.insurance_reserves / st.earned_premium

    return s


def calc_growth(
    statements: list[FinancialStatement],
    tier: CompanyTier, stage: CompanyStage,
    info: Optional[dict] = None,
) -> GrowthMetrics:
    g = GrowthMetrics()
    info = info or {}
    if len(statements) < 2:
        return g
    stmts = statements

    if stmts[0].revenue and stmts[1].revenue and stmts[1].revenue != 0:
        g.revenue_growth_yoy = (stmts[0].revenue - stmts[1].revenue) / abs(stmts[1].revenue)

    if stmts[0].net_income and stmts[1].net_income and stmts[1].net_income != 0:
        g.earnings_growth_yoy = (stmts[0].net_income - stmts[1].net_income) / abs(stmts[1].net_income)

    if stmts[0].free_cash_flow and stmts[1].free_cash_flow and stmts[1].free_cash_flow != 0:
        g.fcf_growth_yoy = (stmts[0].free_cash_flow - stmts[1].free_cash_flow) / abs(stmts[1].free_cash_flow)

    if stmts[0].book_value_per_share and stmts[1].book_value_per_share and stmts[1].book_value_per_share != 0:
        g.book_value_growth_yoy = (stmts[0].book_value_per_share - stmts[1].book_value_per_share) / abs(stmts[1].book_value_per_share)

    # Tangible Book Value per share growth — bank quality signal
    def _tbv_per_share(stmt: FinancialStatement) -> Optional[float]:
        if not stmt or not stmt.shares_outstanding or stmt.shares_outstanding <= 0:
            return None
        if stmt.total_equity is None:
            return None
        tce = stmt.total_equity - (stmt.goodwill or 0) - (stmt.intangibles or 0)
        return tce / stmt.shares_outstanding if tce > 0 else None

    tbv_now = _tbv_per_share(stmts[0])
    tbv_prior = _tbv_per_share(stmts[1])
    if tbv_now and tbv_prior and tbv_prior > 0:
        g.tangible_book_growth_yoy = (tbv_now - tbv_prior) / tbv_prior

    if stmts[0].shares_outstanding and stmts[1].shares_outstanding and stmts[1].shares_outstanding > 0:
        g.shares_growth_yoy = (stmts[0].shares_outstanding - stmts[1].shares_outstanding) / stmts[1].shares_outstanding

    if len(stmts) >= 4 and stmts[0].shares_outstanding and stmts[3].shares_outstanding:
        g.shares_growth_3y_cagr = _cagr(stmts[3].shares_outstanding, stmts[0].shares_outstanding, 3)

    if len(stmts) >= 4:
        g.revenue_cagr_3y = _cagr(stmts[3].revenue, stmts[0].revenue, 3)
        g.earnings_cagr_3y = _cagr(stmts[3].net_income, stmts[0].net_income, 3)

    if len(stmts) >= 5:
        g.revenue_cagr_5y = _cagr(stmts[-1].revenue, stmts[0].revenue, len(stmts) - 1)
        g.earnings_cagr_5y = _cagr(stmts[-1].net_income, stmts[0].net_income, len(stmts) - 1)

    # ── Banks: NII / Loan / Deposit / Fee growth
    if stmts[0].net_interest_income and stmts[1].net_interest_income and stmts[1].net_interest_income != 0:
        g.nii_growth_yoy = (stmts[0].net_interest_income - stmts[1].net_interest_income) / abs(stmts[1].net_interest_income)
    if stmts[0].total_loans and stmts[1].total_loans and stmts[1].total_loans > 0:
        g.loan_growth_yoy = (stmts[0].total_loans - stmts[1].total_loans) / stmts[1].total_loans
    if stmts[0].total_deposits and stmts[1].total_deposits and stmts[1].total_deposits > 0:
        g.deposit_growth_yoy = (stmts[0].total_deposits - stmts[1].total_deposits) / stmts[1].total_deposits
    if stmts[0].non_interest_income and stmts[1].non_interest_income and stmts[1].non_interest_income != 0:
        g.fee_income_growth_yoy = (stmts[0].non_interest_income - stmts[1].non_interest_income) / abs(stmts[1].non_interest_income)

    # ── Insurance: premium growth
    if stmts[0].earned_premium and stmts[1].earned_premium and stmts[1].earned_premium > 0:
        g.premium_growth_yoy = (stmts[0].earned_premium - stmts[1].earned_premium) / stmts[1].earned_premium

    # ── Asset Managers: AUM growth and net inflows / starting AUM
    if stmts[0].aum and stmts[1].aum and stmts[1].aum > 0:
        g.aum_growth_yoy = (stmts[0].aum - stmts[1].aum) / stmts[1].aum
    if stmts[0].net_inflows is not None and stmts[1].aum and stmts[1].aum > 0:
        g.net_inflows_pct_aum = stmts[0].net_inflows / stmts[1].aum

    # ── Productivity
    employees_now = info.get("fullTimeEmployees")
    if employees_now and stmts[0].revenue and stmts[0].revenue > 0:
        g.revenue_per_employee = stmts[0].revenue / employees_now

    if g.revenue_growth_yoy and g.earnings_growth_yoy and g.revenue_growth_yoy != 0:
        g.operating_leverage = g.earnings_growth_yoy / g.revenue_growth_yoy

    return g


def calc_efficiency(
    info: dict, statements: list[FinancialStatement], tier: CompanyTier,
) -> EfficiencyMetrics:
    e = EfficiencyMetrics()
    if not statements:
        return e
    s = statements[0]
    if s.revenue and s.total_assets and s.total_assets > 0:
        e.asset_turnover = s.revenue / s.total_assets

    # Cost-to-Income (alias of efficiency_ratio)
    if s.non_interest_expense and s.revenue and s.revenue > 0:
        e.cost_to_income_ratio = s.non_interest_expense / s.revenue

    # Assets per employee
    employees = info.get("fullTimeEmployees")
    if employees and employees > 0 and s.total_assets:
        e.assets_per_employee = s.total_assets / employees

    # Revenue per dollar AUM (asset managers) — basis points
    if s.aum and s.aum > 0 and s.revenue:
        e.revenue_per_dollar_aum = (s.revenue / s.aum) * 10000  # in bps

    # FCF conversion: FCF / net income — flagged as low signal for banks
    if s.free_cash_flow is not None and s.net_income and s.net_income > 0:
        e.fcf_conversion = s.free_cash_flow / s.net_income

    return e


def calc_share_structure(
    info: dict, statements: list[FinancialStatement],
    growth: GrowthMetrics, tier: CompanyTier, stage: CompanyStage,
) -> ShareStructure:
    ss = ShareStructure()
    ss.shares_outstanding = info.get("sharesOutstanding")
    ss.float_shares = info.get("floatShares")
    ss.insider_ownership_pct = info.get("heldPercentInsiders")
    ss.institutional_ownership_pct = info.get("heldPercentInstitutions")

    implied = info.get("impliedSharesOutstanding")
    if implied:
        ss.fully_diluted_shares = implied
    elif ss.shares_outstanding:
        ss.fully_diluted_shares = ss.shares_outstanding

    if ss.shares_outstanding and ss.fully_diluted_shares and ss.shares_outstanding > 0:
        ratio = ss.fully_diluted_shares / ss.shares_outstanding
        if growth:
            growth.dilution_ratio = ratio
            growth.fully_diluted_shares = ss.fully_diluted_shares

    # Financials companies typically have large floats; thresholds match insurers/banks
    if ss.fully_diluted_shares:
        fd = ss.fully_diluted_shares
        if fd < 100_000_000:
            ss.share_structure_assessment = "Tight (<100M shares)"
        elif fd < 500_000_000:
            ss.share_structure_assessment = "Standard (100-500M shares)"
        elif fd < 2_000_000_000:
            ss.share_structure_assessment = "Large Float (0.5-2B shares)"
        elif fd < 10_000_000_000:
            ss.share_structure_assessment = "Mega Float (2-10B shares)"
        else:
            ss.share_structure_assessment = "Hyper-Diluted (>10B shares)"

    # Buyback intensity — share growth < 0 means buybacks
    if growth and growth.shares_growth_yoy is not None:
        sg = growth.shares_growth_yoy
        if sg < -0.05:
            ss.buyback_intensity = "Aggressive buyback (>5%/yr reduction)"
        elif sg < -0.02:
            ss.buyback_intensity = "Active buyback (2-5%/yr reduction)"
        elif sg < 0.01:
            ss.buyback_intensity = "Low dilution (<1%/yr)"
        elif sg < 0.04:
            ss.buyback_intensity = "Moderate dilution (1-4%/yr)"
        else:
            ss.buyback_intensity = f"Heavy dilution ({sg*100:.1f}%/yr)"

    # Dual-class structure — flag when insider voting rights skew heavy
    if ss.insider_ownership_pct and ss.float_shares and ss.shares_outstanding:
        if ss.insider_ownership_pct > 0.15 and ss.float_shares < ss.shares_outstanding * 0.70:
            ss.dual_class_structure = True

    return ss


def calc_finance_quality(
    profitability: ProfitabilityMetrics,
    growth: GrowthMetrics,
    solvency: SolvencyMetrics,
    share_structure: ShareStructure,
    statements: list[FinancialStatement],
    info: dict,
    tier: CompanyTier,
    stage: CompanyStage,
) -> FinanceQualityIndicators:
    """Composite quality score 0-100 with Financials-specific axes.

    Weights:
      - Capital Adequacy (CET1 / leverage)   (20 pts)
      - Asset Quality (NPL / coverage / NCO) (20 pts)
      - Profitability (ROE / ROTCE / NIM)    (15 pts)
      - Efficiency (cost-to-income)          (10 pts)
      - Liquidity (LDR / LCR)                (10 pts)
      - Underwriting (combined ratio)         (10 pts) — applies to insurers
      - Franchise & fee diversification      (10 pts)
      - Capital return / dilution             (5 pts)
    """
    m = FinanceQualityIndicators()
    score = 0.0
    max_score = 0.0

    # ── 1. Capital Adequacy (20 pts) ───────────────────────────────
    max_score += 20
    cet1 = solvency.cet1_ratio if solvency else None
    if cet1 is not None:
        if cet1 >= 0.16:
            m.capital_adequacy_assessment = f"Fortress CET1 ({cet1*100:.1f}%)"
            score += 20
        elif cet1 >= 0.13:
            m.capital_adequacy_assessment = f"Strong CET1 ({cet1*100:.1f}%) — well above 10.5% minimum"
            score += 16
        elif cet1 >= 0.105:
            m.capital_adequacy_assessment = f"Adequate CET1 ({cet1*100:.1f}%)"
            score += 10
        elif cet1 >= 0.08:
            m.capital_adequacy_assessment = f"Marginal CET1 ({cet1*100:.1f}%) — below buffer"
            score += 4
        else:
            m.capital_adequacy_assessment = f"Critical CET1 ({cet1*100:.1f}%) — undercapitalized"
    else:
        m.capital_adequacy_assessment = "Capital adequacy data unavailable"
        score += 8

    # ── 2. Asset Quality (20 pts) ──────────────────────────────────
    max_score += 20
    npl = solvency.npl_ratio if solvency else None
    coverage = solvency.npl_coverage_ratio if solvency else None
    aq_score = 0
    if npl is not None:
        if npl < 0.01:
            aq_score += 12
            aq_note = f"Pristine NPLs ({npl*100:.2f}%)"
        elif npl < 0.02:
            aq_score += 9
            aq_note = f"Healthy NPLs ({npl*100:.2f}%)"
        elif npl < 0.04:
            aq_score += 5
            aq_note = f"Elevated NPLs ({npl*100:.2f}%)"
        else:
            aq_score += 0
            aq_note = f"Stressed NPLs ({npl*100:.2f}%)"
    else:
        aq_note = "NPL data unavailable"
        aq_score += 5
    if coverage is not None:
        if coverage >= 1.0:
            aq_score += 8
            cov_note = f"Full reserve coverage ({coverage*100:.0f}%)"
        elif coverage >= 0.7:
            aq_score += 5
            cov_note = f"Adequate coverage ({coverage*100:.0f}%)"
        else:
            aq_score += 1
            cov_note = f"Light coverage ({coverage*100:.0f}%)"
    else:
        cov_note = "Coverage data unavailable"
        aq_score += 3
    m.asset_quality_assessment = f"{aq_note}; {cov_note}"
    score += min(20, aq_score)

    # ── 3. Profitability (15 pts) ──────────────────────────────────
    max_score += 15
    roe = profitability.roe if profitability else None
    rotce = profitability.rotce if profitability else None
    nim = profitability.nim if profitability else None
    pf_score = 0
    if rotce is not None:
        if rotce >= 0.15:
            pf_score += 8
            roe_note = f"Excellent ROTCE ({rotce*100:.1f}%)"
        elif rotce >= 0.10:
            pf_score += 5
            roe_note = f"Solid ROTCE ({rotce*100:.1f}%)"
        elif rotce >= 0.05:
            pf_score += 2
            roe_note = f"Modest ROTCE ({rotce*100:.1f}%)"
        else:
            roe_note = f"Weak ROTCE ({rotce*100:.1f}%)"
    elif roe is not None:
        if roe >= 0.15:
            pf_score += 7
            roe_note = f"Excellent ROE ({roe*100:.1f}%)"
        elif roe >= 0.10:
            pf_score += 4
            roe_note = f"Solid ROE ({roe*100:.1f}%)"
        else:
            roe_note = f"Modest ROE ({roe*100:.1f}%)"
    else:
        roe_note = "Return data unavailable"
        pf_score += 3
    if nim is not None:
        if nim >= 0.035:
            pf_score += 7
            nim_note = f"Strong NIM ({nim*100:.2f}%)"
        elif nim >= 0.025:
            pf_score += 4
            nim_note = f"Healthy NIM ({nim*100:.2f}%)"
        elif nim >= 0.015:
            pf_score += 2
            nim_note = f"Compressed NIM ({nim*100:.2f}%)"
        else:
            nim_note = f"Thin NIM ({nim*100:.2f}%)"
    else:
        nim_note = "NIM not applicable / data unavailable"
        pf_score += 3
    m.profitability_assessment = f"{roe_note}; {nim_note}"
    score += min(15, pf_score)

    # ── 4. Efficiency Ratio (10 pts) ───────────────────────────────
    max_score += 10
    eff = profitability.efficiency_ratio if profitability else None
    if eff is not None:
        if eff < 0.50:
            m.efficiency_assessment = f"Best-in-class efficiency ({eff*100:.0f}%)"
            score += 10
        elif eff < 0.60:
            m.efficiency_assessment = f"Strong efficiency ({eff*100:.0f}%)"
            score += 7
        elif eff < 0.70:
            m.efficiency_assessment = f"Average efficiency ({eff*100:.0f}%)"
            score += 4
        else:
            m.efficiency_assessment = f"Bloated cost base ({eff*100:.0f}%)"
            score += 1
    else:
        m.efficiency_assessment = "Efficiency ratio data unavailable"
        score += 4

    # ── 5. Liquidity (10 pts) ──────────────────────────────────────
    max_score += 10
    ldr = solvency.loan_to_deposit_ratio if solvency else None
    if ldr is not None:
        if 0.70 <= ldr <= 0.90:
            m.liquidity_assessment = f"Optimal LDR ({ldr*100:.0f}%)"
            score += 10
        elif 0.60 <= ldr < 0.70 or 0.90 < ldr <= 1.00:
            m.liquidity_assessment = f"Acceptable LDR ({ldr*100:.0f}%)"
            score += 7
        elif ldr > 1.00:
            m.liquidity_assessment = f"Over-lent ({ldr*100:.0f}%) — funding stress risk"
            score += 3
        else:
            m.liquidity_assessment = f"Under-lent ({ldr*100:.0f}%) — earnings drag"
            score += 5
    else:
        m.liquidity_assessment = "Loan-to-deposit data unavailable"
        score += 4

    # ── 6. Underwriting (10 pts) — insurers
    max_score += 10
    cr = profitability.combined_ratio if profitability else None
    if cr is not None:
        if cr < 0.95:
            m.underwriting_assessment = f"Profitable underwriting ({cr*100:.1f}% combined ratio)"
            score += 10
        elif cr < 1.00:
            m.underwriting_assessment = f"Marginal profit ({cr*100:.1f}% combined ratio)"
            score += 7
        elif cr < 1.05:
            m.underwriting_assessment = f"Underwriting loss ({cr*100:.1f}% combined ratio)"
            score += 3
        else:
            m.underwriting_assessment = f"Heavy underwriting loss ({cr*100:.1f}% combined ratio)"
            score += 0
    else:
        m.underwriting_assessment = "Combined ratio not applicable / data unavailable"
        score += 5

    # ── 7. Franchise & Fee Diversification (10 pts)
    max_score += 10
    franchise_score = 0
    if tier == CompanyTier.MEGA:
        m.franchise_position = "Mega-cap — likely systemic / dominant franchise"
        franchise_score += 6
    elif tier == CompanyTier.LARGE:
        m.franchise_position = "Large-cap — established franchise"
        franchise_score += 4
    elif tier == CompanyTier.MID:
        m.franchise_position = "Mid-cap regional franchise"
        franchise_score += 3
    else:
        m.franchise_position = "Small/micro-cap — niche franchise risk"
        franchise_score += 1
    fee_ratio = profitability.fee_income_ratio if profitability else None
    if fee_ratio is not None:
        if fee_ratio >= 0.40:
            franchise_score += 4
            m.fee_income_diversification = f"Highly diversified ({fee_ratio*100:.0f}% fee income)"
        elif fee_ratio >= 0.25:
            franchise_score += 3
            m.fee_income_diversification = f"Diversified ({fee_ratio*100:.0f}% fee income)"
        elif fee_ratio >= 0.15:
            franchise_score += 2
            m.fee_income_diversification = f"Moderate diversification ({fee_ratio*100:.0f}% fee income)"
        else:
            franchise_score += 0
            m.fee_income_diversification = f"NII-dependent ({fee_ratio*100:.0f}% fee income)"
    else:
        m.fee_income_diversification = "Fee income mix unavailable"
        franchise_score += 2
    score += min(10, franchise_score)

    # ── 8. Capital return / dilution (5 pts)
    max_score += 5
    dil = growth.shares_growth_yoy if growth else None
    if dil is not None:
        if dil < -0.03:
            score += 5  # buybacks
            m.moat_assessment = "Active buybacks — accretive capital return"
        elif dil < 0:
            score += 4
        elif dil < 0.02:
            score += 3
        elif dil < 0.05:
            score += 1
        else:
            score += 0
    else:
        score += 2

    # ── Moat / competitive position (qualitative anchor)
    if not m.moat_assessment:
        if m.franchise_position and "systemic" in (m.franchise_position or "").lower():
            m.moat_assessment = "Systemic franchise — regulatory & scale moats"
            m.moat_type = "Regulatory + scale + funding cost advantage"
        elif fee_ratio is not None and fee_ratio >= 0.40:
            m.moat_assessment = "Fee-income diversification — capital-light moats"
            m.moat_type = "Fee businesses (asset mgmt / capital markets)"
        else:
            m.moat_assessment = "Standard franchise — depends on cost-of-funds advantage"
            m.moat_type = "Funding cost / scale"

    # Insider alignment
    insider_pct = share_structure.insider_ownership_pct if share_structure else None
    if insider_pct is not None:
        m.insider_ownership_pct = insider_pct
        if insider_pct > 0.10:
            m.founder_led = "Material insider stake (>10%)"
            m.management_quality = "High alignment"
        elif insider_pct > 0.02:
            m.founder_led = "Meaningful insider stake (2-10%)"
            m.management_quality = "Decent alignment"
        else:
            m.founder_led = "Diffuse ownership (<2% insiders)"
            m.management_quality = "Typical large-cap structure"

    # Revenue predictability based on stage
    if stage in (CompanyStage.MATURE, CompanyStage.PLATFORM):
        m.revenue_predictability = "Mature franchise — predictable revenue"
    elif stage == CompanyStage.SCALE:
        m.revenue_predictability = "Scaling — increasingly predictable"
    elif stage == CompanyStage.GROWTH:
        m.revenue_predictability = "Expansion — earnings sensitive to credit cycle"
    else:
        m.revenue_predictability = "Early stage — earnings highly variable"

    m.roe_history = _calc_roe_history(statements)
    m.nim_history = _calc_nim_history(statements)

    m.quality_score = round((score / max_score) * 100, 1) if max_score > 0 else 0
    if m.quality_score >= 75:
        m.competitive_position = "Best-in-Class — Elite Financials Franchise"
    elif m.quality_score >= 60:
        m.competitive_position = "Strong — High-Quality Business"
    elif m.quality_score >= 45:
        m.competitive_position = "Viable — Average Quality"
    elif m.quality_score >= 30:
        m.competitive_position = "Weak — Below Average Quality"
    else:
        m.competitive_position = "Poor — Elevated Risk"

    return m


def calc_intrinsic_value(
    info: dict, statements: list[FinancialStatement],
    growth: GrowthMetrics, solvency: SolvencyMetrics,
    tier: CompanyTier, stage: CompanyStage,
    discount_rate: float = 0.10, terminal_growth: float = 0.03,
) -> IntrinsicValue:
    iv = IntrinsicValue()
    iv.current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    shares = info.get("sharesOutstanding")

    # Method selection for Financials
    if stage == CompanyStage.PLATFORM:
        iv.primary_method = "Excess Return Model + DDM"
        iv.secondary_method = "P/TBV Peer Multiple"
    elif stage == CompanyStage.MATURE:
        iv.primary_method = "Excess Return Model"
        iv.secondary_method = "Dividend Discount Model"
    elif stage == CompanyStage.SCALE:
        iv.primary_method = "P/TBV Peer Multiple"
        iv.secondary_method = "Excess Return Model"
    elif stage == CompanyStage.GROWTH:
        iv.primary_method = "P/TBV with growth premium"
        iv.secondary_method = "Forward P/E"
    else:  # STARTUP
        iv.primary_method = "P/Tangible Book"
        iv.secondary_method = "Cash + Capital Backing"

    if not statements:
        return iv
    latest = statements[0]

    # ── Excess Return Model: Equity Value = BV + (ROE - CoE) / (CoE - g) * BV
    if latest.total_equity and latest.total_equity > 0 and shares and shares > 0:
        roe = info.get("returnOnEquity") or 0
        if roe and roe > 0:
            cost_of_equity = discount_rate
            if tier == CompanyTier.SMALL:
                cost_of_equity = 0.12
            elif tier in (CompanyTier.MICRO, CompanyTier.NANO):
                cost_of_equity = 0.14
            g_term = min(max(terminal_growth, 0), cost_of_equity - 0.01)
            if cost_of_equity > g_term:
                bv_per_share = latest.total_equity / shares
                excess_return_value = bv_per_share + bv_per_share * (roe - cost_of_equity) / (cost_of_equity - g_term)
                if not math.isnan(excess_return_value) and not math.isinf(excess_return_value) and excess_return_value > 0:
                    iv.excess_return_value = round(excess_return_value, 2)

    # ── P/TBV Peer Multiple
    if latest.total_equity is not None and shares and shares > 0:
        tce = latest.total_equity - (latest.goodwill or 0) - (latest.intangibles or 0)
        if tce > 0:
            tbv_per_share = tce / shares
            peer_multiple = _peer_p_tbv_multiple(stage)
            iv.p_tbv_implied_price = round(tbv_per_share * peer_multiple, 2)

    # ── Reverse DCF — what growth rate is the current price pricing in (FCF-based)
    if iv.current_price and shares and latest.free_cash_flow and latest.free_cash_flow > 0:
        mc = iv.current_price * shares
        fcf = latest.free_cash_flow
        try:
            implied_g = discount_rate - (fcf / mc)
            if -0.05 < implied_g < 0.50:
                iv.reverse_dcf_growth = round(implied_g, 4)
        except Exception:
            pass

    # ── DCF for cash-flow-positive financials with FCF
    if stage in (CompanyStage.PLATFORM, CompanyStage.MATURE, CompanyStage.SCALE):
        if latest.free_cash_flow and latest.free_cash_flow > 0 and shares and shares > 0:
            fcf = latest.free_cash_flow
            growth_rate = min(growth.revenue_cagr_3y or growth.revenue_growth_yoy or 0.06, 0.20)
            growth_rate = max(growth_rate, 0.0)
            dr = discount_rate
            if tier == CompanyTier.SMALL:
                dr = 0.12
            elif tier in (CompanyTier.MICRO, CompanyTier.NANO):
                dr = 0.15
            if dr > terminal_growth:
                total_pv = 0.0
                projected_fcf = fcf
                for year in range(1, 11):
                    yr_growth = growth_rate - (growth_rate - terminal_growth) * (year / 10)
                    projected_fcf *= (1 + yr_growth)
                    total_pv += projected_fcf / ((1 + dr) ** year)
                terminal_fcf = projected_fcf * (1 + terminal_growth)
                terminal_value = terminal_fcf / (dr - terminal_growth)
                pv_terminal = terminal_value / ((1 + dr) ** 10)
                dcf = (total_pv + pv_terminal) / shares
                if not math.isnan(dcf) and not math.isinf(dcf) and dcf > 0:
                    iv.dcf_value = round(dcf, 2)

    eps = latest.eps or (latest.net_income / shares if latest.net_income and shares else None)
    bvps = latest.book_value_per_share or info.get("bookValue")
    if eps and eps > 0 and bvps and bvps > 0:
        iv.graham_number = round(math.sqrt(22.5 * eps * bvps), 2)

    if eps and eps > 0 and growth.earnings_cagr_3y and growth.earnings_cagr_3y > 0:
        eg = min(growth.earnings_cagr_3y * 100, 100)
        if eg > 0:
            result = eps * eg
            if not math.isnan(result) and not math.isinf(result):
                iv.lynch_fair_value = round(result, 2)

    if solvency.ncav_per_share is not None:
        iv.ncav_value = round(solvency.ncav_per_share, 4)

    if latest.total_equity and shares and shares > 0:
        iv.asset_based_value = round(latest.total_equity / shares, 4)

    if iv.current_price and iv.current_price > 0:
        if iv.dcf_value:
            iv.margin_of_safety_dcf = round((iv.dcf_value - iv.current_price) / iv.dcf_value, 4)
        if iv.graham_number:
            iv.margin_of_safety_graham = round((iv.graham_number - iv.current_price) / iv.graham_number, 4)
        if iv.ncav_value and iv.ncav_value > 0:
            iv.margin_of_safety_ncav = round((iv.ncav_value - iv.current_price) / iv.ncav_value, 4)
        if iv.asset_based_value and iv.asset_based_value > 0:
            iv.margin_of_safety_asset = round((iv.asset_based_value - iv.current_price) / iv.asset_based_value, 4)
        if iv.excess_return_value and iv.excess_return_value > 0:
            iv.margin_of_safety_excess_return = round((iv.excess_return_value - iv.current_price) / iv.excess_return_value, 4)
        if iv.p_tbv_implied_price and iv.p_tbv_implied_price > 0:
            iv.margin_of_safety_p_tbv = round((iv.p_tbv_implied_price - iv.current_price) / iv.p_tbv_implied_price, 4)

    return iv


def _peer_p_tbv_multiple(stage: CompanyStage) -> float:
    """Rough peer P/TBV multiple for fair-value estimation."""
    return {
        CompanyStage.PLATFORM: 1.8,
        CompanyStage.MATURE: 1.5,
        CompanyStage.SCALE: 1.4,
        CompanyStage.GROWTH: 1.6,
        CompanyStage.STARTUP: 1.2,
    }.get(stage, 1.4)


def calc_market_intelligence(
    info: dict, ticker_obj, solvency: SolvencyMetrics,
    share_structure: ShareStructure, growth: GrowthMetrics,
    tier: CompanyTier, stage: CompanyStage,
) -> MarketIntelligence:
    """Aggregate market sentiment, insider activity, technicals, and risk warnings."""
    mi = MarketIntelligence()
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    shares_outstanding = info.get("sharesOutstanding")
    mi.price_current = price

    # ── Insider transactions ───────────────────────────────────────
    try:
        insider_df = ticker_obj.insider_transactions
        if insider_df is not None and not insider_df.empty:
            top_rows = insider_df.head(10)
            for _, row in top_rows.iterrows():
                txn = InsiderTransaction(
                    insider=str(row.get("Insider", row.get("insider", ""))),
                    position=str(row.get("Position", row.get("position", ""))),
                    transaction_type=str(row.get("Transaction", row.get("transaction", ""))),
                    shares=row.get("Shares", row.get("shares")),
                    value=row.get("Value", row.get("value")),
                    date=str(row.get("Start Date", row.get("startDate", row.get("date", "")))),
                )
                mi.insider_transactions.append(txn)

            cutoff = datetime.now() - timedelta(days=90)
            net_shares = 0.0
            buy_count = 0
            sell_count = 0
            for _, row in insider_df.iterrows():
                date_val = row.get("Start Date", row.get("startDate", row.get("date")))
                try:
                    if hasattr(date_val, "to_pydatetime"):
                        txn_date = date_val.to_pydatetime()
                    elif isinstance(date_val, str) and date_val:
                        txn_date = datetime.strptime(date_val[:10], "%Y-%m-%d")
                    else:
                        continue
                    if txn_date.tzinfo is not None:
                        txn_date = txn_date.replace(tzinfo=None)
                    if txn_date < cutoff:
                        continue
                except (ValueError, TypeError):
                    continue

                txn_type = str(row.get("Transaction", row.get("transaction", ""))).lower()
                shares_val = row.get("Shares", row.get("shares", 0)) or 0

                if any(kw in txn_type for kw in ("acquisition", "exercise", "purchase", "buy")):
                    net_shares += abs(shares_val)
                    buy_count += 1
                elif any(kw in txn_type for kw in ("disposition", "sale", "sell")):
                    net_shares -= abs(shares_val)
                    sell_count += 1

            mi.net_insider_shares_3m = net_shares

            if net_shares > 0 and buy_count > 3:
                mi.insider_buy_signal = "Open-market insider buying — strong signal"
            elif net_shares > 0:
                mi.insider_buy_signal = "Net positive insider activity"
            elif net_shares < 0 and sell_count > buy_count * 2:
                mi.insider_buy_signal = "Heavy insider selling"
            else:
                mi.insider_buy_signal = "Mixed / Neutral"
    except Exception:
        mi.insider_buy_signal = "Data unavailable"

    # ── Institutional holders ───────────────────────────────────────
    try:
        inst_df = ticker_obj.institutional_holders
        if inst_df is not None and not inst_df.empty:
            holder_col = "Holder" if "Holder" in inst_df.columns else (
                "holder" if "holder" in inst_df.columns else None
            )
            if holder_col:
                mi.top_holders = inst_df[holder_col].head(5).tolist()
    except Exception:
        pass
    mi.institutions_count = info.get("institutionsCount")
    mi.institutions_pct = share_structure.institutional_ownership_pct if share_structure else None

    # ── Analyst consensus ───────────────────────────────────────────
    mi.target_high = info.get("targetHighPrice")
    mi.target_low = info.get("targetLowPrice")
    mi.target_mean = info.get("targetMeanPrice")
    mi.recommendation = info.get("recommendationKey")
    mi.analyst_count = info.get("numberOfAnalystOpinions")

    if mi.target_mean and price and price > 0:
        mi.target_upside_pct = (mi.target_mean - price) / price

    # ── Short interest ──────────────────────────────────────────────
    mi.shares_short = info.get("sharesShort")
    short_pct_raw = info.get("shortPercentOfFloat")
    if short_pct_raw is not None:
        mi.short_pct_of_float = short_pct_raw * 100
    mi.short_ratio_days = info.get("shortRatio")

    short_pct = mi.short_pct_of_float or 0
    short_ratio = mi.short_ratio_days or 0
    if short_pct > 15 and short_ratio > 5:
        mi.short_squeeze_risk = "High squeeze potential"
    elif short_pct > 8:
        mi.short_squeeze_risk = "Elevated short interest — possible bank-run concerns"
    else:
        mi.short_squeeze_risk = "Normal"

    # ── Price technicals ────────────────────────────────────────────
    mi.price_52w_high = info.get("fiftyTwoWeekHigh")
    mi.price_52w_low = info.get("fiftyTwoWeekLow")
    mi.sma_50 = info.get("fiftyDayAverage")
    mi.sma_200 = info.get("twoHundredDayAverage")
    mi.beta = info.get("beta")
    mi.avg_volume = info.get("averageVolume")
    mi.volume_10d_avg = info.get("averageDailyVolume10Day")

    if price and mi.price_52w_high and mi.price_52w_high > 0:
        mi.pct_from_52w_high = (price - mi.price_52w_high) / mi.price_52w_high
    if price and mi.price_52w_low and mi.price_52w_low > 0:
        mi.pct_from_52w_low = (price - mi.price_52w_low) / mi.price_52w_low
    if price and mi.price_52w_high and mi.price_52w_low is not None:
        range_span = mi.price_52w_high - mi.price_52w_low
        if range_span > 0:
            mi.price_52w_range_position = (price - mi.price_52w_low) / range_span

    if price and mi.sma_50:
        mi.above_sma_50 = price > mi.sma_50
    if price and mi.sma_200:
        mi.above_sma_200 = price > mi.sma_200
    if mi.sma_50 and mi.sma_200:
        mi.golden_cross = mi.sma_50 > mi.sma_200

    if mi.volume_10d_avg and mi.avg_volume and mi.avg_volume > 0:
        vol_ratio = mi.volume_10d_avg / mi.avg_volume
        if vol_ratio > 1.25:
            mi.volume_trend = "Increasing"
        elif vol_ratio < 0.75:
            mi.volume_trend = "Decreasing"
        else:
            mi.volume_trend = "Stable"

    # ── Financials benchmark context — XLF as headline + sub-sector ETF ───
    from lynx_finance.models import FinanceCategory, classify_category
    _CATEGORY_ETFS = {
        FinanceCategory.BANK_DIVERSIFIED: [("XLF", "Financial Select Sector SPDR"),
                                           ("KBE", "SPDR S&P Bank ETF")],
        FinanceCategory.BANK_REGIONAL: [("KRE", "SPDR S&P Regional Banking"),
                                        ("KBE", "SPDR S&P Bank ETF")],
        FinanceCategory.INVESTMENT_BANK: [("IAI", "iShares US Broker-Dealers"),
                                          ("XLF", "Financial Select Sector SPDR")],
        FinanceCategory.INSURANCE_PC: [("KIE", "SPDR S&P Insurance"),
                                       ("IAK", "iShares US Insurance")],
        FinanceCategory.INSURANCE_LIFE: [("KIE", "SPDR S&P Insurance"),
                                         ("IAK", "iShares US Insurance")],
        FinanceCategory.REINSURANCE: [("KIE", "SPDR S&P Insurance"),
                                      ("IAK", "iShares US Insurance")],
        FinanceCategory.INSURANCE_BROKER: [("KIE", "SPDR S&P Insurance"),
                                           ("XLF", "Financial Select Sector SPDR")],
        FinanceCategory.ASSET_MANAGER: [("IAI", "iShares US Broker-Dealers"),
                                        ("XLF", "Financial Select Sector SPDR")],
        FinanceCategory.CAPITAL_MARKETS: [("IAI", "iShares US Broker-Dealers"),
                                          ("XLF", "Financial Select Sector SPDR")],
        FinanceCategory.CONSUMER_FINANCE: [("XLF", "Financial Select Sector SPDR"),
                                           ("VFH", "Vanguard Financials")],
        FinanceCategory.FINTECH: [("FINX", "Global X FinTech ETF"),
                                  ("IPAY", "ETFMG Prime Mobile Payments")],
        FinanceCategory.MORTGAGE_FINANCE: [("REM", "iShares Mortgage Real Estate"),
                                           ("XLF", "Financial Select Sector SPDR")],
        FinanceCategory.DIVERSIFIED: [("XLF", "Financial Select Sector SPDR"),
                                      ("VFH", "Vanguard Financials")],
        FinanceCategory.OTHER: [("XLF", "Financial Select Sector SPDR"),
                                ("VFH", "Vanguard Financials")],
    }

    category = FinanceCategory.OTHER
    try:
        desc = info.get("longBusinessSummary", "")
        industry = info.get("industry", "")
        category = classify_category(desc, industry)
    except Exception:
        pass

    # Headline financials benchmark: XLF (Financial Select Sector SPDR)
    try:
        qt = yf.Ticker("XLF")
        qi = qt.info or {}
        mi.benchmark_name = "Financial Select Sector SPDR (XLF)"
        mi.benchmark_ticker = "XLF"
        mi.benchmark_price = qi.get("regularMarketPrice") or qi.get("previousClose")
        mi.benchmark_52w_high = qi.get("fiftyTwoWeekHigh")
        mi.benchmark_52w_low = qi.get("fiftyTwoWeekLow")
        if mi.benchmark_price and mi.benchmark_52w_high and mi.benchmark_52w_low:
            rng = mi.benchmark_52w_high - mi.benchmark_52w_low
            if rng > 0:
                mi.benchmark_52w_position = (mi.benchmark_price - mi.benchmark_52w_low) / rng
        try:
            hist = qt.history(period="1y")
            if hist is not None and len(hist) > 1:
                mi.benchmark_ytd_change = (hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1)
        except Exception:
            pass
    except Exception:
        pass

    # Sub-sector ETFs
    try:
        etf_list = _CATEGORY_ETFS.get(category, _CATEGORY_ETFS[FinanceCategory.OTHER])
        if len(etf_list) >= 1:
            etf_ticker, etf_name = etf_list[0]
            et = yf.Ticker(etf_ticker)
            ei = et.info or {}
            mi.sector_etf_name = etf_name
            mi.sector_etf_ticker = etf_ticker
            mi.sector_etf_price = ei.get("regularMarketPrice") or ei.get("previousClose")
            try:
                hist = et.history(period="3mo")
                if hist is not None and len(hist) > 1:
                    mi.sector_etf_3m_perf = (hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1)
            except Exception:
                pass
        if len(etf_list) >= 2:
            etf_ticker2, etf_name2 = etf_list[1]
            et2 = yf.Ticker(etf_ticker2)
            ei2 = et2.info or {}
            mi.peer_etf_name = etf_name2
            mi.peer_etf_ticker = etf_ticker2
            mi.peer_etf_price = ei2.get("regularMarketPrice") or ei2.get("previousClose")
            try:
                hist2 = et2.history(period="3mo")
                if hist2 is not None and len(hist2) > 1:
                    mi.peer_etf_3m_perf = (hist2["Close"].iloc[-1] / hist2["Close"].iloc[0] - 1)
            except Exception:
                pass
    except Exception:
        pass

    # ── Risk warnings (Financials-specific) ─────────────────────────
    warnings: list[str] = []

    if mi.beta and mi.beta > 1.4:
        warnings.append(
            f"Elevated volatility (beta {mi.beta:.1f}) — sensitivity to credit & rate cycles"
        )

    if short_pct > 8:
        warnings.append(
            f"Elevated short interest ({short_pct:.1f}%) — possible deposit / credit-quality concerns"
        )

    if not mi.analyst_count or mi.analyst_count == 0:
        warnings.append("No analyst coverage — higher information asymmetry")

    if mi.pct_from_52w_low is not None and mi.pct_from_52w_low < 0.20:
        warnings.append("Trading near 52-week low — capitulation or genuine value?")

    if mi.insider_buy_signal and "Heavy insider selling" in (mi.insider_buy_signal or ""):
        warnings.append("Heavy insider selling detected")

    # Capital adequacy warnings
    if solvency and solvency.cet1_ratio is not None and solvency.cet1_ratio < 0.105:
        warnings.append(
            f"CET1 ratio {solvency.cet1_ratio*100:.1f}% — below well-capitalized buffer"
        )

    # Asset quality warnings
    if solvency and solvency.npl_ratio is not None and solvency.npl_ratio > 0.04:
        warnings.append(
            f"NPL ratio {solvency.npl_ratio*100:.1f}% — elevated credit stress"
        )

    if solvency and solvency.texas_ratio is not None and solvency.texas_ratio > 0.50:
        warnings.append(
            f"Texas Ratio {solvency.texas_ratio*100:.0f}% — distress-level loan losses vs capital"
        )

    if solvency and solvency.loan_to_deposit_ratio is not None:
        ldr = solvency.loan_to_deposit_ratio
        if ldr > 1.0:
            warnings.append(
                f"Loan-to-deposit {ldr*100:.0f}% — funding risk if deposits flee"
            )

    mi.risk_warnings = warnings

    # ── Financials disclaimers ──────────────────────────────────────
    disclaimers: list[str] = [
        "Financials are highly sensitive to interest-rate cycles and the credit cycle.",
        "Bank balance sheets carry maturity-mismatch and unrealized-loss risk on bond portfolios.",
        "Capital ratios (CET1) and asset quality (NPLs) are the regulatory must-watch metrics.",
    ]
    if category in (FinanceCategory.BANK_DIVERSIFIED, FinanceCategory.BANK_REGIONAL,
                    FinanceCategory.INVESTMENT_BANK):
        disclaimers.append(
            "Banks rely on confidence — deposit flight can rapidly turn solvent banks into failures."
        )
    if category in (FinanceCategory.INSURANCE_PC, FinanceCategory.REINSURANCE):
        disclaimers.append(
            "Insurers face long-tail liability risk and catastrophe exposure — reserve adequacy is critical."
        )
    if category == FinanceCategory.ASSET_MANAGER:
        disclaimers.append(
            "Asset managers' revenue is mark-to-market: AUM declines compress fees immediately."
        )
    disclaimers.extend([
        "Past performance and insider activity do not guarantee future results.",
        "This analysis is for informational purposes only and does not constitute investment advice.",
    ])
    mi.disclaimers = disclaimers

    return mi


def _calc_roe_history(statements: list[FinancialStatement]) -> list[Optional[float]]:
    vals = []
    for s in statements:
        if s.net_income is not None and s.total_equity and s.total_equity > 0:
            vals.append(s.net_income / s.total_equity)
    return vals


def _calc_nim_history(statements: list[FinancialStatement]) -> list[Optional[float]]:
    vals = []
    for s in statements:
        if s.net_interest_income is not None and s.earning_assets and s.earning_assets > 0:
            vals.append(s.net_interest_income / s.earning_assets)
        elif s.net_interest_income is not None and s.total_assets and s.total_assets > 0:
            vals.append(s.net_interest_income / s.total_assets)
    return vals


def _cagr(start: Optional[float], end: Optional[float], years: int) -> Optional[float]:
    if not start or not end or start <= 0 or end <= 0 or years <= 0:
        return None
    try:
        result = (end / start) ** (1 / years) - 1
        if math.isnan(result) or math.isinf(result):
            return None
        return result
    except (ValueError, OverflowError, ZeroDivisionError):
        return None


# Backwards-compat alias
calc_mining_quality = calc_finance_quality  # pragma: no cover
calc_tech_quality = calc_finance_quality  # pragma: no cover
