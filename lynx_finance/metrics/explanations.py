"""Metric explanations for Lynx Financials Analysis."""

from __future__ import annotations
from lynx_finance.models import MetricExplanation

METRIC_EXPLANATIONS: dict[str, MetricExplanation] = {}

def _add(key, full_name, description, why_used, formula, category):
    METRIC_EXPLANATIONS[key] = MetricExplanation(key=key, full_name=full_name, description=description,
                                                  why_used=why_used, formula=formula, category=category)

# ── Valuation ──────────────────────────────────────────────────────
_add("pe_trailing", "Price-to-Earnings (TTM)", "Compares stock price to trailing 12-month earnings per share.", "Traditional anchor for mature financials. Less meaningful when reserve releases or one-offs distort earnings.", "P/E = Price / EPS (TTM)", "valuation")
_add("pe_forward", "Forward P/E", "Forward P/E based on next-year analyst EPS estimates.", "Useful when earnings normalise after rate or credit cycles.", "Fwd P/E = Price / Est. EPS (next FY)", "valuation")
_add("pb_ratio", "Price-to-Book", "Compares stock price to book value per share.", "Cornerstone valuation anchor for banks and insurers. Mature banks usually trade 0.8-1.5x book; <1x signals distress or low ROE.", "P/B = Price / Book Value per Share", "valuation")
_add("price_to_tangible_book_value", "Price-to-Tangible Book (P/TBV)", "Strips goodwill and intangibles from book value before dividing the price.", "THE primary valuation anchor for banks. Mega-cap quality banks 1.5-2.5x; troubled banks <1x.", "P/TBV = Price / (Equity - Goodwill - Intangibles) / Shares", "valuation")
_add("ps_ratio", "Price-to-Sales", "Compares market cap to revenue.", "Useful for de-novo banks or insurtechs where earnings are not yet representative.", "P/S = Market Cap / Revenue", "valuation")
_add("p_fcf", "Price-to-Free-Cash-Flow", "Compares market cap to free cash flow.", "Meaningful for capital-light financials (asset managers, exchanges, payments). Less reliable for banks where 'FCF' is conceptually muddled.", "P/FCF = Market Cap / FCF", "valuation")
_add("ev_ebitda", "Enterprise Value / EBITDA", "Capital-structure-neutral earnings multiple.", "Useful for capital-light financials (asset managers, exchanges, brokers). Not used for banks.", "EV/EBITDA = (Market Cap + Debt - Cash) / EBITDA", "valuation")
_add("price_to_aum", "Price-to-AUM", "Market cap divided by Assets Under Management.", "The asset-manager valuation anchor. Typical range 1.5%-3.5% (15-35 bps); pure-passive managers trade lower (<1%).", "P/AUM = Market Cap / AUM", "valuation")
_add("price_to_premium", "Price-to-Premium", "Market cap divided by earned premium (insurers).", "P&C insurance valuation anchor. Quality insurers 1.0-2.0x earned premium.", "P/Premium = Market Cap / Earned Premium", "valuation")
_add("excess_capital_pct_market_cap", "Excess Capital % of Market Cap", "CET1 capital above the 12% well-capitalized buffer, as a share of market cap.", "Indicates buyback / dividend / M&A optionality. >10% suggests significant capital return potential.", "(CET1 - 12% × RWA) / Market Cap", "valuation")
_add("dividend_yield", "Dividend Yield", "Annual dividend / current price.", "Mature financials are dividend-anchored. Sustainable bank yields 3-5%, payouts of 30-50% are healthy.", "Annual Dividend / Price", "valuation")
_add("earnings_yield", "Earnings Yield", "Inverse P/E — earnings per dollar invested.", "Used for spread vs 10Y treasury yield to gauge risk premium.", "1 / P/E", "valuation")
_add("earnings_yield_vs_10y", "Earnings Yield vs 10Y Treasury", "Earnings yield minus 10-year treasury yield.", "Risk premium proxy. >5pp = wide spread (cheap); <2pp = compressed spread (expensive).", "(1/PE) - 10Y Yield", "valuation")
_add("peg_ratio", "PEG Ratio", "P/E adjusted by growth rate.", "Useful for mid-cycle financials with durable growth.", "PEG = P/E / Annual EPS growth rate", "valuation")
_add("cash_to_market_cap", "Cash / Market Cap", "How much of market cap is backed by cash on the balance sheet.", "More relevant for fintech & payment platforms than for banks.", "Cash / Market Cap", "valuation")

# ── Profitability ──────────────────────────────────────────────────
_add("roe", "Return on Equity", "Profit per dollar of equity.", "THE bank quality anchor. Quality banks 12-15%; best-in-class 17-20%; <8% = subscale.", "ROE = Net Income / Equity", "profitability")
_add("rotce", "Return on Tangible Common Equity (ROTCE)", "ROE adjusted to strip goodwill/intangibles from equity.", "Sharper bank quality measure. Quality banks 13-17%; mega-cap leaders 15-20%.", "ROTCE = Net Income / (Equity - Goodwill - Intangibles)", "profitability")
_add("roa", "Return on Assets", "Profit per dollar of total assets.", "Critical bank metric. >1% = quality; >1.3% = best-in-class; <0.5% = subscale.", "ROA = Net Income / Total Assets", "profitability")
_add("roic", "Return on Invested Capital", "Return on all invested capital. Less informative for banks (deposits are not 'invested capital').", "Use cautiously for banks; meaningful for asset managers and capital-light financials.", "ROIC = NOPAT / Invested Capital", "profitability")
_add("nim", "Net Interest Margin (NIM)", "Net interest income divided by interest-earning assets.", "Core bank profitability metric. US banks 2.5-4.0%; insurers far below; emerging markets >5%.", "NIM = Net Interest Income / Avg Earning Assets", "profitability")
_add("yield_on_assets", "Yield on Assets", "Interest income / earning assets.", "Asset-side yield component of NIM. Compares asset mix and pricing power.", "Interest Income / Avg Earning Assets", "profitability")
_add("cost_of_funds", "Cost of Funds", "Interest expense / interest-bearing liabilities.", "Liability-side cost. Funding moats: low cost of funds (<1%) is a durable advantage.", "Interest Expense / Avg IB Liabilities", "profitability")
_add("net_interest_spread", "Net Interest Spread", "Yield on assets minus cost of funds.", "The pure pricing spread. Distinct from NIM (which is influenced by mix).", "Yield on Assets - Cost of Funds", "profitability")
_add("efficiency_ratio", "Efficiency Ratio (Cost-to-Income)", "Non-interest expense divided by total revenue.", "Lower is better. Best-in-class <50%; quality 50-60%; bloated >70%. Operating leverage signal.", "Non-Interest Expense / Total Revenue", "profitability")
_add("fee_income_ratio", "Fee Income Ratio", "Non-interest income / total revenue.", "Diversification away from rate sensitivity. >40% = highly diversified; <15% = NII-dependent.", "Non-Interest Income / Revenue", "profitability")
_add("pre_provision_margin", "Pre-Provision Margin", "Pre-provision profit divided by revenue.", "Earnings power before credit costs — a normalized profitability gauge through the credit cycle.", "(Revenue - Non-Int Expense) / Revenue", "profitability")
_add("combined_ratio", "Combined Ratio", "(Losses + Underwriting Expenses) / Earned Premium.", "THE insurance underwriting profitability metric. <100% = profitable underwriting; >100% = underwriting loss; <90% = best-in-class.", "(Losses + Expenses) / Earned Premium", "profitability")
_add("loss_ratio", "Loss Ratio", "Incurred losses / earned premium.", "Half of the combined ratio. Catastrophe years can spike loss ratios temporarily.", "Losses Incurred / Earned Premium", "profitability")
_add("expense_ratio", "Expense Ratio", "Underwriting expenses / earned premium.", "The other half of the combined ratio. Reflects acquisition cost and operating leverage.", "Underwriting Expenses / Earned Premium", "profitability")
_add("underwriting_margin", "Underwriting Margin", "1 − Combined Ratio.", "Direct profitability signal from underwriting alone (excludes investment income).", "1 - Combined Ratio", "profitability")
_add("investment_yield", "Investment Yield", "Net investment income / invested assets.", "Insurance investment portfolio return. Sensitive to rate cycle.", "Net Investment Income / Invested Assets", "profitability")
_add("effective_fee_rate_bps", "Effective Fee Rate (bps)", "Management fees / average AUM, in basis points.", "Asset manager pricing power. Active 50-80 bps; passive 5-15 bps; alts 100-200 bps + perf fees.", "Mgmt Fees / Avg AUM × 10000", "profitability")
_add("gross_margin", "Gross Margin", "Revenue remaining after cost of revenue.", "Largely irrelevant for banks/insurers; meaningful for fintech and capital-markets platforms.", "Gross Margin = (Revenue - COGS) / Revenue", "profitability")
_add("operating_margin", "Operating Margin", "Operating income / revenue.", "Useful for fintech, exchanges, and asset managers; less so for banks.", "Operating Income / Revenue", "profitability")
_add("net_margin", "Net Margin", "Bottom-line profitability.", "Banks and insurers report high net margins by design; compare cross-sub-sector.", "Net Income / Revenue", "profitability")

# ── Solvency / Capital ─────────────────────────────────────────────
_add("cet1_ratio", "CET1 Ratio (Basel III)", "Common Equity Tier 1 capital divided by risk-weighted assets.", "THE primary bank capital adequacy metric. Minimum 4.5% + 2.5% buffer + G-SIB surcharge; well-capitalized >10.5%; fortress >14%.", "CET1 / Risk-Weighted Assets", "solvency")
_add("tier1_ratio", "Tier 1 Capital Ratio", "Tier 1 capital / RWA.", "Slightly broader than CET1; same regulatory weight.", "Tier 1 Capital / RWA", "solvency")
_add("total_capital_ratio", "Total Capital Ratio", "Total regulatory capital / RWA.", "Includes Tier 2 (subordinated debt). Minimum 8% under Basel III.", "Total Capital / RWA", "solvency")
_add("leverage_ratio", "Basel III Leverage Ratio", "Tier 1 capital / total exposure (un-risk-weighted).", "Safety floor against RWA gaming. Minimum 3%; G-SIBs ≥4.5%.", "Tier 1 Capital / Total Exposure", "solvency")
_add("loan_to_deposit_ratio", "Loan-to-Deposit Ratio (LDR)", "Loans / deposits.", "Liquidity / leverage gauge. Optimal 70-90%; >100% = funding-stress risk if deposits flee.", "Total Loans / Total Deposits", "solvency")
_add("loan_to_asset_ratio", "Loan-to-Asset Ratio", "Loans / total assets.", "Asset-mix indicator. Higher = more credit-intensive; lower = more securities-portfolio exposure.", "Total Loans / Total Assets", "solvency")
_add("npl_ratio", "Non-Performing Loan Ratio", "Non-performing loans / gross loans.", "Asset quality must-watch. <1% = pristine; 1-2% = healthy; 2-4% = elevated; >4% = stressed.", "NPLs / Gross Loans", "solvency")
_add("npl_coverage_ratio", "NPL Coverage Ratio", "Allowance for loan losses / NPLs.", "Reserve adequacy. >100% = full coverage; 70-100% = adequate; <70% = under-reserved.", "Allowance for Loan Losses / NPLs", "solvency")
_add("net_charge_off_ratio", "Net Charge-Off Ratio", "Annualized net charge-offs / average loans.", "Realised losses run-rate. Through-cycle: 0.3-0.6% normal; >1.5% = stress.", "NCOs / Avg Loans", "solvency")
_add("cost_of_risk", "Cost of Risk", "Provision for credit losses / average loans.", "Forward-looking version of NCOs. Spikes in recessions; tracks credit-cycle turn.", "Provisions / Avg Loans", "solvency")
_add("texas_ratio", "Texas Ratio", "Non-performing loans / (Tangible Common Equity + Loan-Loss Reserves).", "Bank distress indicator. >100% historically signals failure risk; >50% = elevated stress.", "NPLs / (TCE + Reserves)", "solvency")
_add("liquidity_coverage_ratio", "Liquidity Coverage Ratio (LCR)", "High-quality liquid assets / 30-day net cash outflows.", "Basel III liquidity rule. Minimum 100%; quality banks 110-130%; G-SIBs 120%+.", "HQLA / 30-day Net Outflows", "solvency")
_add("nsfr", "Net Stable Funding Ratio (NSFR)", "Available stable funding / required stable funding (1-year horizon).", "Long-term liquidity rule. Minimum 100%.", "Available Stable Funding / Required Stable Funding", "solvency")
_add("solvency_ratio", "Solvency Ratio (Insurance)", "Eligible own funds / Solvency Capital Requirement (Solvency II) or RBC ratio (US).", "Insurance regulatory adequacy. EU SCR ≥100%; US RBC well-capitalized ≥200%.", "Own Funds / SCR (or RBC)", "solvency")
_add("reserve_to_premium", "Reserve-to-Premium Ratio", "Insurance reserves / earned premium.", "Reserve adequacy gauge. Long-tail lines (workers' comp, GL) carry higher ratios than short-tail (auto).", "Insurance Reserves / Earned Premium", "solvency")
_add("debt_to_equity", "Debt / Equity", "Long-term debt vs equity (capital-light financials).", "Useful for asset managers and exchanges; banks measure capital differently.", "D/E = Total Debt / Equity", "solvency")
_add("interest_coverage", "Interest Coverage", "Operating income / interest expense.", "Capital-light financials only; meaningless for banks where interest is the business.", "Operating Income / Interest Expense", "solvency")
_add("altman_z_score", "Altman Z-Score", "Bankruptcy probability predictor.", "Less meaningful for banks; useful sanity check for capital-light financials.", "Z = 1.2(WC/TA) + 1.4(RE/TA) + 3.3(EBIT/TA) + 0.6(MV/TL) + 1.0(Sales/TA)", "solvency")

# ── Growth ─────────────────────────────────────────────────────────
_add("revenue_growth_yoy", "Revenue Growth (YoY)", "Annual revenue change.", "Top-line growth. For banks, decompose into NII growth + fee income growth.", "(Rev - Rev_Prior) / |Rev_Prior|", "growth")
_add("revenue_cagr_3y", "Revenue CAGR (3Y)", "3-year compound revenue growth.", "Smooths cyclical noise. >10% = strong franchise expansion; <3% = mature.", "CAGR = (End / Start)^(1/3) - 1", "growth")
_add("earnings_growth_yoy", "Earnings Growth (YoY)", "Annual net income change.", "Drives mature financials valuations. Distorted by reserve releases / one-offs.", "(NI - NI_Prior) / |NI_Prior|", "growth")
_add("nii_growth_yoy", "Net Interest Income Growth (YoY)", "Year-over-year NII change.", "Bank top-line driver. Reflects loan growth + NIM expansion.", "(NII - NII_Prior) / |NII_Prior|", "growth")
_add("loan_growth_yoy", "Loan Growth (YoY)", "Year-over-year loan book change.", "Bank balance-sheet expansion. >8% = aggressive; 4-8% = healthy; <2% = stagnant.", "(Loans - Loans_Prior) / Loans_Prior", "growth")
_add("deposit_growth_yoy", "Deposit Growth (YoY)", "Year-over-year deposits change.", "Funding moat expansion. Sticky low-cost deposits are the bank franchise.", "(Deposits - Deposits_Prior) / Deposits_Prior", "growth")
_add("fee_income_growth_yoy", "Fee Income Growth (YoY)", "Year-over-year non-interest income change.", "Diversification and capital-light revenue growth.", "(Fees - Fees_Prior) / Fees_Prior", "growth")
_add("tangible_book_growth_yoy", "Tangible Book / Share Growth (YoY)", "TBV/share year-over-year change.", "Compounding signal for banks. Quality compounders 8-12%/yr; mature franchises 4-6%.", "(TBV/sh - TBV/sh_Prior) / TBV/sh_Prior", "growth")
_add("premium_growth_yoy", "Earned Premium Growth (YoY)", "Year-over-year earned premium change (insurers).", "Top-line growth signal. Hard markets see 8-15%/yr; soft markets <5%.", "(Premium - Premium_Prior) / Premium_Prior", "growth")
_add("aum_growth_yoy", "AUM Growth (YoY)", "Year-over-year AUM change (asset managers).", "Decompose into market performance + net flows. Net inflows are the durable growth signal.", "(AUM - AUM_Prior) / AUM_Prior", "growth")
_add("net_inflows_pct_aum", "Net Inflows / Starting AUM", "Annual net flows divided by starting AUM.", "Pure organic growth signal for asset managers. >5% = strong; negative = outflows (red flag).", "Net Flows / Prior AUM", "growth")
_add("shares_growth_yoy", "Share Dilution (YoY)", "Annual change in shares outstanding.", "Banks/insurers commonly buy back stock. Negative = buybacks (good); >2%/yr issuance = dilution risk.", "(Shares - Shares_Prior) / Shares_Prior", "growth")
_add("revenue_per_employee", "Revenue per Employee", "Productivity metric.", "Money-center banks $700k-$1.2M; regional $400-700k; insurers $500k-$1M; asset mgrs >$1M.", "Revenue / Employees", "growth")
_add("book_value_growth_yoy", "Book Value / Share Growth (YoY)", "BV/share year-over-year change.", "Total compounding (includes goodwill). Use TBV/share for sharper bank quality signal.", "(BV/sh - BV/sh_Prior) / BV/sh_Prior", "growth")

# ── Finance Quality ────────────────────────────────────────────────
_add("quality_score", "Financials Quality Score", "Composite Financials-quality score (0-100).", "Weighted: Capital Adequacy (20), Asset Quality (20), Profitability (15), Efficiency (10), Liquidity (10), Underwriting (10), Franchise (10), Capital Return (5). >75 elite, <30 weak.", "Weighted sum of 8 Financials-specific axes", "finance_quality")
_add("moat_assessment", "Moat Assessment", "Qualitative moat classification tied to franchise + cost-of-funds + scale.", "Funding moats (low CoF), regulatory moats (G-SIB scale), distribution moats (branch network), switching costs (treasury services).", "Derived from CoF, fee mix, tier", "finance_quality")
_add("capital_adequacy_assessment", "Capital Adequacy Verdict", "Assessment of CET1 / Tier 1 strength.", "Pass/fail grade vs Basel III well-capitalized buffer.", "CET1 ratio band", "finance_quality")
_add("asset_quality_assessment", "Asset Quality Verdict", "Assessment of NPLs + reserve coverage.", "Combines NPL ratio and coverage ratio for a holistic credit-quality view.", "NPL ratio + Coverage", "finance_quality")
_add("profitability_assessment", "Profitability Verdict", "Assessment of ROE/ROTCE and NIM.", "Banking franchise quality summary.", "ROE / ROTCE / NIM bands", "finance_quality")
_add("efficiency_assessment", "Efficiency Verdict", "Cost-to-income band assessment.", "Operating leverage signal.", "Efficiency ratio band", "finance_quality")
_add("liquidity_assessment", "Liquidity Verdict", "LDR / LCR assessment.", "Funding-stress resilience signal.", "LDR / LCR band", "finance_quality")
_add("underwriting_assessment", "Underwriting Verdict (Insurers)", "Combined ratio assessment.", "P&C insurer profitability gate.", "Combined ratio band", "finance_quality")
_add("franchise_position", "Franchise Position", "Scale and category position.", "G-SIBs and mega-insurers compound; sub-scale players struggle.", "Tier + category analysis", "finance_quality")
_add("fee_income_diversification", "Fee Income Diversification", "Fee income share of revenue.", "Diversifies away from rate sensitivity. Mega-banks 35-50% fees; regional banks 15-25%.", "Fee Income / Revenue band", "finance_quality")
_add("founder_led", "Founder-Led / Insider Ownership Signal", "Insider control or material insider stake.", "Insider alignment matters more for fintech/insurtech than mega-banks.", "Insider ownership % band", "finance_quality")

# ── Share Structure ────────────────────────────────────────────────
_add("shares_outstanding", "Shares Outstanding", "Basic shares currently issued.", "Baseline for per-share metrics.", "—", "share_structure")
_add("fully_diluted_shares", "Fully Diluted Shares", "Shares + RSUs + options + warrants.", "True dilution floor — use this for per-share calculations.", "Basic + RSUs + Options + Warrants", "share_structure")
_add("insider_ownership_pct", "Insider Ownership %", "% of shares held by insiders/founders.", "More relevant for fintech/insurtech than for mega-cap banks where insiders rarely hold >5%.", "Insider Shares / Total Shares", "share_structure")
_add("dual_class_structure", "Dual-Class Structure", "Whether insiders hold super-voting shares.", "Common in fintech/payments. Locks in founder control — governance trade-off.", "Voting class structure", "share_structure")
_add("buyback_intensity", "Buyback Intensity", "Aggressiveness of share repurchases.", "Mature financials return capital aggressively. Quality buybacks of 3-6%/yr accrete BV/share rapidly.", "Negative share growth bands", "share_structure")

# ── Efficiency ─────────────────────────────────────────────────────
_add("cost_to_income_ratio", "Cost-to-Income Ratio", "Same as efficiency_ratio — non-interest expense / revenue.", "Operating leverage signal. Lower is better.", "Non-Int Expense / Revenue", "efficiency")
_add("assets_per_employee", "Assets per Employee", "Total assets / FTE.", "Productivity scale gauge. Mega-banks $25-50M/employee; community banks $5-10M.", "Total Assets / FTE", "efficiency")
_add("revenue_per_dollar_aum", "Revenue per $ AUM (bps)", "Asset-manager pricing efficiency in basis points.", "Comparable to effective fee rate; the all-in revenue intensity per dollar managed.", "Revenue / AUM × 10000", "efficiency")
_add("fcf_conversion", "FCF Conversion", "FCF divided by net income.", "Low signal for banks (FCF concept is muddled); meaningful for asset managers and exchanges.", "FCF / Net Income", "efficiency")

SECTION_EXPLANATIONS = {
    "profile": {"title": "Company Profile", "description": "Company identification, market cap tier, Financials lifecycle stage, sub-category (Banks/Insurance/Asset Mgmt/Capital Markets/Fintech/etc.), and jurisdiction risk."},
    "valuation": {"title": "Valuation Metrics", "description": "Traditional + Financials-specific valuation ratios. P/TBV is the bank anchor; Price-to-AUM for asset managers; Price-to-Premium for insurers; P/E and dividend yield for mature franchises."},
    "profitability": {"title": "Profitability Metrics", "description": "Margin analysis plus Financials-specific: NIM, ROTCE, Efficiency Ratio, Combined Ratio (insurers), Effective Fee Rate (asset mgrs), Fee Income Ratio. ROE / ROTCE are the core franchise quality gates."},
    "solvency": {"title": "Solvency & Capital Adequacy", "description": "Basel III capital ratios (CET1, Tier 1, Total, Leverage), liquidity (LCR, NSFR, LDR), asset quality (NPLs, coverage, NCOs, Cost of Risk, Texas Ratio), and insurance solvency (RBC / Solvency II)."},
    "growth": {"title": "Growth & Franchise Expansion", "description": "Revenue + NII + loan + deposit + fee growth. Insurance: premium growth. Asset mgrs: AUM growth and net inflows. Tangible Book / Share growth is the durable bank compounding signal."},
    "share_structure": {"title": "Share Structure", "description": "Basic/fully-diluted shares, insider & institutional ownership, dual-class flag, buyback intensity — Financials-specific capital-return signals."},
    "finance_quality": {"title": "Financials Quality Assessment", "description": "Financials-specialized scoring. Evaluates capital adequacy, asset quality, profitability (ROE/ROTCE/NIM), efficiency, liquidity, underwriting (insurers), franchise position, and fee diversification."},
    "intrinsic_value": {"title": "Intrinsic Value Estimates", "description": "Multiple methods adapted by stage. Mature/Platform: Excess Return Model + DDM. Scale/Growth: P/TBV peer multiples. Startup: P/Tangible Book + capital backing. Reverse DCF shows the growth rate embedded in the price."},
    "conclusion": {"title": "Assessment Conclusion", "description": "Weighted scoring across 5 categories with weights adapted by tier AND Financials lifecycle stage. Includes a 10-point Financials screening checklist evaluating CET1, NPLs, ROE, efficiency, LDR, dividend safety, capital return, dilution, and jurisdiction."},
}

CONCLUSION_METHODOLOGY = {
    "overall": {"title": "Conclusion Methodology", "description": "Score is a weighted average of 5 categories (valuation, profitability, solvency/capital, growth, finance quality). Weights vary by company tier AND Financials lifecycle stage. De-novo / startup banks weight solvency/capital at 35-40% and quality at 30%. Mature platforms use balanced weights with capital + quality dominating. Verdicts: Strong Buy (>=75), Buy (>=60), Hold (>=45), Caution (>=30), Avoid (<30)."},
    "valuation": {"title": "Valuation Score", "description": "Starts at 50. Adjusted by P/TBV (the bank anchor), P/E (mature), P/AUM (asset mgrs), P/Premium (insurers), dividend yield, excess capital pct of market cap."},
    "profitability": {"title": "Profitability Score", "description": "Starts at 50. ROE / ROTCE band, NIM band, efficiency ratio band, combined ratio (insurers), fee income diversification."},
    "solvency": {"title": "Solvency / Capital Score", "description": "Starts at 50. CET1 ratio (THE primary signal), NPL ratio, coverage, Texas ratio, LDR. Sub-buffer CET1 = -25 points; Texas Ratio >100% = -25 points."},
    "finance_quality": {"title": "Financials Quality Score", "description": "Composite of capital adequacy (20pts), asset quality (20pts), profitability (15pts), efficiency (10pts), liquidity (10pts), underwriting (10pts) — applies to insurers, franchise & fee diversification (10pts), capital return (5pts)."},
}

def get_explanation(key): return METRIC_EXPLANATIONS.get(key)
def get_section_explanation(section): return SECTION_EXPLANATIONS.get(section)
def get_conclusion_explanation(category=None): return CONCLUSION_METHODOLOGY.get(category or "overall")
def list_metrics(category=None):
    metrics = list(METRIC_EXPLANATIONS.values())
    return [m for m in metrics if m.category == category] if category else metrics
