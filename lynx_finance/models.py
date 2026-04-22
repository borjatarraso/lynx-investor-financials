"""Data models for Lynx Financials — Financials-focused fundamental analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Company tier classification (market cap based)
# ---------------------------------------------------------------------------

class CompanyTier(str, Enum):
    MEGA = "Mega Cap"
    LARGE = "Large Cap"
    MID = "Mid Cap"
    SMALL = "Small Cap"
    MICRO = "Micro Cap"
    NANO = "Nano Cap"


def classify_tier(market_cap: Optional[float]) -> CompanyTier:
    if market_cap is None or market_cap <= 0:
        return CompanyTier.NANO
    if market_cap >= 200_000_000_000:
        return CompanyTier.MEGA
    if market_cap >= 10_000_000_000:
        return CompanyTier.LARGE
    if market_cap >= 2_000_000_000:
        return CompanyTier.MID
    if market_cap >= 300_000_000:
        return CompanyTier.SMALL
    if market_cap >= 50_000_000:
        return CompanyTier.MICRO
    return CompanyTier.NANO


# ---------------------------------------------------------------------------
# Financials lifecycle stage classification
# ---------------------------------------------------------------------------

class CompanyStage(str, Enum):
    STARTUP = "De Novo / Early-Stage"
    GROWTH = "Expansion"
    SCALE = "Scaling Regional"
    MATURE = "Mature / Cash-Generative"
    PLATFORM = "Systemic / Dominant Franchise"


# ---------------------------------------------------------------------------
# Financials sub-sector classification
# ---------------------------------------------------------------------------

class FinanceCategory(str, Enum):
    BANK_DIVERSIFIED = "Diversified / G-SIB Banks"
    BANK_REGIONAL = "Regional Banks"
    INVESTMENT_BANK = "Investment Banks & Capital Markets"
    INSURANCE_PC = "P&C Insurance"
    INSURANCE_LIFE = "Life & Health Insurance"
    REINSURANCE = "Reinsurance"
    INSURANCE_BROKER = "Insurance Brokers"
    ASSET_MANAGER = "Asset & Wealth Management"
    CAPITAL_MARKETS = "Exchanges & Capital Markets Infra"
    CONSUMER_FINANCE = "Consumer Finance & Credit"
    FINTECH = "Fintech & Payments"
    MORTGAGE_FINANCE = "Mortgage Finance / Mortgage REITs"
    DIVERSIFIED = "Diversified Financial Services"
    OTHER = "Other Financials"


# ---------------------------------------------------------------------------
# Regulatory / jurisdiction tiering (Financials lens: Basel III, Solvency II)
# ---------------------------------------------------------------------------

class JurisdictionTier(str, Enum):
    TIER_1 = "Tier 1 — Strong Supervision (Basel III / Solvency II)"
    TIER_2 = "Tier 2 — Moderate Regulatory Risk"
    TIER_3 = "Tier 3 — High Regulatory / Geopolitical Risk"
    UNKNOWN = "Unknown"


class Relevance(str, Enum):
    CRITICAL = "critical"
    IMPORTANT = "important"
    RELEVANT = "relevant"
    CONTEXTUAL = "contextual"
    IRRELEVANT = "irrelevant"


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    WATCH = "WATCH"
    OK = "OK"
    STRONG = "STRONG"
    NA = "N/A"


# ---------------------------------------------------------------------------
# Presentation helpers for Severity and Relevance (colors + wrappers)
# ---------------------------------------------------------------------------

SEVERITY_STYLE = {
    Severity.CRITICAL: {"wrap": ("***", "***"), "color": "bold red",  "label": "CRITICAL"},
    Severity.WARNING:  {"wrap": ("*", "*"),     "color": "#ff8800",   "label": "WARNING"},
    Severity.WATCH:    {"wrap": ("[", "]"),     "color": "yellow",    "label": "WATCH"},
    Severity.OK:       {"wrap": ("[", "]"),     "color": "green",     "label": "OK"},
    Severity.STRONG:   {"wrap": ("[", "]"),     "color": "grey70",    "label": "STRONG"},
    Severity.NA:       {"wrap": ("[", "]"),     "color": "grey50",    "label": "N/A"},
}


def format_severity(sev: "Severity") -> str:
    """Return a Rich-markup formatted severity tag."""
    style = SEVERITY_STYLE.get(sev, SEVERITY_STYLE[Severity.NA])
    pre, post = style["wrap"]
    label = style["label"]
    if sev == Severity.CRITICAL:
        label = label.upper()
    return f"[{style['color']}]{pre}{label}{post}[/]"


def severity_plain(sev: "Severity") -> str:
    """Plain-text severity token (no markup)."""
    style = SEVERITY_STYLE.get(sev, SEVERITY_STYLE[Severity.NA])
    pre, post = style["wrap"]
    label = style["label"]
    if sev == Severity.CRITICAL:
        label = label.upper()
    return f"{pre}{label}{post}"


IMPACT_STYLE = {
    Relevance.CRITICAL:   {"color": "blink bold red",  "label": "Critical"},
    Relevance.IMPORTANT:  {"color": "#ff8800",         "label": "Important"},
    Relevance.RELEVANT:   {"color": "yellow",          "label": "Relevant"},
    Relevance.CONTEXTUAL: {"color": "green",           "label": "Informational"},
    Relevance.IRRELEVANT: {"color": "grey70",          "label": "Irrelevant"},
}


def format_impact(rel: "Relevance") -> str:
    style = IMPACT_STYLE.get(rel, IMPACT_STYLE[Relevance.RELEVANT])
    return f"[{style['color']}]{style['label']}[/]"


def impact_plain(rel: "Relevance") -> str:
    style = IMPACT_STYLE.get(rel, IMPACT_STYLE[Relevance.RELEVANT])
    return style["label"]


# ---------------------------------------------------------------------------
# Core data models
# ---------------------------------------------------------------------------

@dataclass
class CompanyProfile:
    ticker: str
    name: str
    isin: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    exchange: Optional[str] = None
    currency: Optional[str] = None
    market_cap: Optional[float] = None
    description: Optional[str] = None
    website: Optional[str] = None
    employees: Optional[int] = None
    tier: CompanyTier = CompanyTier.NANO
    stage: CompanyStage = CompanyStage.STARTUP
    finance_category: FinanceCategory = FinanceCategory.OTHER
    jurisdiction_tier: JurisdictionTier = JurisdictionTier.UNKNOWN
    jurisdiction_country: Optional[str] = None


@dataclass
class ValuationMetrics:
    pe_trailing: Optional[float] = None
    pe_forward: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    p_fcf: Optional[float] = None
    ev_ebitda: Optional[float] = None
    ev_revenue: Optional[float] = None
    ev_gross_profit: Optional[float] = None
    peg_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    earnings_yield: Optional[float] = None
    enterprise_value: Optional[float] = None
    market_cap: Optional[float] = None
    price_to_tangible_book: Optional[float] = None
    price_to_ncav: Optional[float] = None
    cash_to_market_cap: Optional[float] = None
    # Financials-specific valuation
    price_to_tangible_book_value: Optional[float] = None  # P/TBV — bank anchor
    price_to_aum: Optional[float] = None                  # asset managers
    price_to_premium: Optional[float] = None              # insurers (P&C)
    price_to_embedded_value: Optional[float] = None       # life insurers
    earnings_yield_vs_10y: Optional[float] = None         # earnings yield - 10Y treasury
    excess_capital_pct_market_cap: Optional[float] = None # CET1 surplus / market cap
    # Legacy IT-flavour fields kept for display/export compatibility (always None for Financials)
    ev_to_arr: Optional[float] = None
    ev_per_employee: Optional[float] = None
    rule_of_40_adj_multiple: Optional[float] = None


@dataclass
class ProfitabilityMetrics:
    roe: Optional[float] = None
    roa: Optional[float] = None
    roic: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    fcf_margin: Optional[float] = None
    ebitda_margin: Optional[float] = None
    # Financials-specific profitability
    rotce: Optional[float] = None                # Return on Tangible Common Equity (banks)
    nim: Optional[float] = None                  # Net Interest Margin
    net_interest_spread: Optional[float] = None  # Asset yield - liability cost
    yield_on_assets: Optional[float] = None      # Interest income / earning assets
    cost_of_funds: Optional[float] = None        # Interest expense / interest-bearing liabilities
    efficiency_ratio: Optional[float] = None     # Non-interest expense / total revenue (lower = better)
    fee_income_ratio: Optional[float] = None     # Non-interest income / total revenue
    pre_provision_margin: Optional[float] = None # Pre-provision profit / revenue
    # Insurance
    combined_ratio: Optional[float] = None       # (losses + expenses) / earned premium
    loss_ratio: Optional[float] = None
    expense_ratio: Optional[float] = None
    underwriting_margin: Optional[float] = None  # 1 - combined_ratio
    investment_yield: Optional[float] = None     # Net investment income / invested assets
    # Asset Managers
    effective_fee_rate_bps: Optional[float] = None  # mgmt fees / avg AUM in bps
    operating_margin_aum: Optional[float] = None    # Operating income / revenue (asset managers)
    # Legacy IT-flavour fields kept for display/export compatibility (always None for Financials)
    rule_of_40: Optional[float] = None
    rule_of_40_ebitda: Optional[float] = None
    magic_number: Optional[float] = None
    sbc_to_revenue: Optional[float] = None
    sbc_to_fcf: Optional[float] = None
    gaap_vs_adj_gap: Optional[float] = None


@dataclass
class SolvencyMetrics:
    debt_to_equity: Optional[float] = None
    debt_to_ebitda: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    interest_coverage: Optional[float] = None
    altman_z_score: Optional[float] = None
    net_debt: Optional[float] = None
    total_debt: Optional[float] = None
    total_cash: Optional[float] = None
    cash_burn_rate: Optional[float] = None
    cash_runway_years: Optional[float] = None
    working_capital: Optional[float] = None
    cash_per_share: Optional[float] = None
    tangible_book_value: Optional[float] = None
    ncav: Optional[float] = None
    ncav_per_share: Optional[float] = None
    quarterly_burn_rate: Optional[float] = None
    burn_as_pct_of_market_cap: Optional[float] = None
    # Financials-specific solvency / capital adequacy
    cet1_ratio: Optional[float] = None             # Common Equity Tier 1 ratio (Basel III)
    tier1_ratio: Optional[float] = None
    total_capital_ratio: Optional[float] = None
    leverage_ratio: Optional[float] = None         # Tier 1 / total exposure (Basel III)
    loan_to_deposit_ratio: Optional[float] = None  # LDR
    loan_to_asset_ratio: Optional[float] = None
    npl_ratio: Optional[float] = None              # Non-performing loans / gross loans
    npl_coverage_ratio: Optional[float] = None     # Allowance / NPLs
    net_charge_off_ratio: Optional[float] = None   # NCOs / avg loans
    cost_of_risk: Optional[float] = None           # Provisions / avg loans
    texas_ratio: Optional[float] = None            # NPLs / (TCE + Reserves) — bank distress
    liquidity_coverage_ratio: Optional[float] = None  # LCR (Basel III)
    nsfr: Optional[float] = None                   # Net Stable Funding Ratio
    # Insurance
    solvency_ratio: Optional[float] = None         # Solvency II ratio (EU) or RBC (US)
    reserve_to_premium: Optional[float] = None
    catastrophe_exposure: Optional[float] = None   # Catastrophe limits / equity
    # Asset Manager
    aum_concentration: Optional[float] = None      # Top-10 client share
    # Legacy IT-flavour fields kept for display/export compatibility (always None for Financials)
    cash_coverage_months: Optional[float] = None
    capex_to_revenue: Optional[float] = None
    rpo_coverage: Optional[float] = None
    goodwill_to_assets: Optional[float] = None
    deferred_revenue_ratio: Optional[float] = None


@dataclass
class GrowthMetrics:
    revenue_growth_yoy: Optional[float] = None
    revenue_cagr_3y: Optional[float] = None
    revenue_cagr_5y: Optional[float] = None
    earnings_growth_yoy: Optional[float] = None
    earnings_cagr_3y: Optional[float] = None
    earnings_cagr_5y: Optional[float] = None
    fcf_growth_yoy: Optional[float] = None
    book_value_growth_yoy: Optional[float] = None
    dividend_growth_5y: Optional[float] = None
    shares_growth_yoy: Optional[float] = None
    shares_growth_3y_cagr: Optional[float] = None
    fully_diluted_shares: Optional[float] = None
    dilution_ratio: Optional[float] = None
    # Financials-specific growth
    nii_growth_yoy: Optional[float] = None             # Net interest income growth
    loan_growth_yoy: Optional[float] = None            # Loan book growth
    deposit_growth_yoy: Optional[float] = None
    fee_income_growth_yoy: Optional[float] = None
    tangible_book_growth_yoy: Optional[float] = None   # TBV/share growth — bank quality signal
    # Insurance
    premium_growth_yoy: Optional[float] = None         # Earned premium growth
    # Asset managers
    aum_growth_yoy: Optional[float] = None
    net_inflows_pct_aum: Optional[float] = None        # Net flows / starting AUM
    # Productivity
    revenue_per_employee: Optional[float] = None
    operating_leverage: Optional[float] = None
    # Legacy IT-flavour fields kept for display/export compatibility (always None for Financials)
    arr_growth_yoy: Optional[float] = None
    net_revenue_retention: Optional[float] = None
    gross_revenue_retention: Optional[float] = None
    rd_intensity: Optional[float] = None
    rd_growth_yoy: Optional[float] = None
    sales_marketing_intensity: Optional[float] = None
    employee_growth_yoy: Optional[float] = None


@dataclass
class EfficiencyMetrics:
    asset_turnover: Optional[float] = None
    inventory_turnover: Optional[float] = None
    receivables_turnover: Optional[float] = None
    days_sales_outstanding: Optional[float] = None
    days_inventory: Optional[float] = None
    cash_conversion_cycle: Optional[float] = None
    # Financials-specific efficiency
    cost_to_income_ratio: Optional[float] = None  # Same as efficiency_ratio (alias)
    assets_per_employee: Optional[float] = None
    revenue_per_dollar_aum: Optional[float] = None  # Asset managers
    fcf_conversion: Optional[float] = None          # FCF / net income — low signal for banks
    # Legacy IT-flavour fields kept for display/export compatibility (always None for Financials)
    rule_of_x_score: Optional[float] = None
    cac_payback_months: Optional[float] = None


@dataclass
class FinanceQualityIndicators:
    """Quality scoring specific to Financials companies."""
    quality_score: Optional[float] = None
    management_quality: Optional[str] = None
    insider_ownership_pct: Optional[float] = None
    founder_led: Optional[str] = None
    moat_assessment: Optional[str] = None
    moat_type: Optional[str] = None
    competitive_position: Optional[str] = None
    # Financials-specific quality axes
    capital_adequacy_assessment: Optional[str] = None     # CET1 / Tier1 strength
    asset_quality_assessment: Optional[str] = None        # NPL, NCO, coverage
    profitability_assessment: Optional[str] = None        # ROE, ROTCE, NIM
    efficiency_assessment: Optional[str] = None           # Efficiency ratio band
    liquidity_assessment: Optional[str] = None            # LCR, LDR
    underwriting_assessment: Optional[str] = None         # Combined ratio (insurers)
    franchise_position: Optional[str] = None              # Tier-based franchise strength
    fee_income_diversification: Optional[str] = None      # Fee income % of revenue
    near_term_catalysts: list[str] = field(default_factory=list)
    revenue_predictability: Optional[str] = None
    roe_history: list[Optional[float]] = field(default_factory=list)
    nim_history: list[Optional[float]] = field(default_factory=list)
    # Legacy IT-flavour fields kept for display/export compatibility (always None for Financials)
    catalyst_density: Optional[str] = None
    rd_efficiency_assessment: Optional[str] = None
    unit_economics: Optional[str] = None
    platform_position: Optional[str] = None
    financial_position: Optional[str] = None
    dilution_risk: Optional[str] = None
    rule_of_40_assessment: Optional[str] = None
    sbc_risk_assessment: Optional[str] = None
    roic_history: list[Optional[float]] = field(default_factory=list)
    gross_margin_history: list[Optional[float]] = field(default_factory=list)


@dataclass
class IntrinsicValue:
    dcf_value: Optional[float] = None
    graham_number: Optional[float] = None
    lynch_fair_value: Optional[float] = None
    ncav_value: Optional[float] = None
    asset_based_value: Optional[float] = None
    ev_sales_implied_price: Optional[float] = None
    reverse_dcf_growth: Optional[float] = None
    current_price: Optional[float] = None
    margin_of_safety_dcf: Optional[float] = None
    margin_of_safety_graham: Optional[float] = None
    margin_of_safety_ncav: Optional[float] = None
    margin_of_safety_asset: Optional[float] = None
    margin_of_safety_ev_sales: Optional[float] = None
    primary_method: Optional[str] = None
    secondary_method: Optional[str] = None
    # Financials-specific
    excess_return_value: Optional[float] = None     # Excess Return Model: BV + (ROE-CoE)/CoE * BV
    p_tbv_implied_price: Optional[float] = None     # Tangible book × peer multiple
    margin_of_safety_excess_return: Optional[float] = None
    margin_of_safety_p_tbv: Optional[float] = None


@dataclass
class ShareStructure:
    shares_outstanding: Optional[float] = None
    fully_diluted_shares: Optional[float] = None
    warrants_outstanding: Optional[float] = None
    options_outstanding: Optional[float] = None
    rsu_outstanding: Optional[float] = None
    insider_ownership_pct: Optional[float] = None
    institutional_ownership_pct: Optional[float] = None
    float_shares: Optional[float] = None
    dual_class_structure: Optional[bool] = None
    share_structure_assessment: Optional[str] = None
    buyback_intensity: Optional[str] = None
    # Legacy IT-flavour field kept for display/export compatibility (always None for Financials)
    sbc_overhang_risk: Optional[str] = None


@dataclass
class InsiderTransaction:
    insider: str = ""
    position: str = ""
    transaction_type: str = ""
    shares: Optional[float] = None
    value: Optional[float] = None
    date: str = ""


@dataclass
class MarketIntelligence:
    """Market sentiment, insider activity, institutional holdings, and technicals."""
    insider_transactions: list[InsiderTransaction] = field(default_factory=list)
    net_insider_shares_3m: Optional[float] = None
    insider_buy_signal: Optional[str] = None

    top_holders: list[str] = field(default_factory=list)
    institutions_count: Optional[int] = None
    institutions_pct: Optional[float] = None

    analyst_count: Optional[int] = None
    recommendation: Optional[str] = None
    target_high: Optional[float] = None
    target_low: Optional[float] = None
    target_mean: Optional[float] = None
    target_upside_pct: Optional[float] = None

    shares_short: Optional[float] = None
    short_pct_of_float: Optional[float] = None
    short_ratio_days: Optional[float] = None
    short_squeeze_risk: Optional[str] = None

    price_current: Optional[float] = None
    price_52w_high: Optional[float] = None
    price_52w_low: Optional[float] = None
    pct_from_52w_high: Optional[float] = None
    pct_from_52w_low: Optional[float] = None
    price_52w_range_position: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    above_sma_50: Optional[bool] = None
    above_sma_200: Optional[bool] = None
    golden_cross: Optional[bool] = None
    beta: Optional[float] = None
    avg_volume: Optional[float] = None
    volume_10d_avg: Optional[float] = None
    volume_trend: Optional[str] = None

    projected_dilution_annual_pct: Optional[float] = None
    projected_shares_in_2y: Optional[float] = None
    financing_warning: Optional[str] = None

    # Financials benchmark context (XLF / KBE / KIE / KRE / IAI)
    benchmark_name: Optional[str] = None
    benchmark_ticker: Optional[str] = None
    benchmark_price: Optional[float] = None
    benchmark_52w_high: Optional[float] = None
    benchmark_52w_low: Optional[float] = None
    benchmark_52w_position: Optional[float] = None
    benchmark_ytd_change: Optional[float] = None

    sector_etf_name: Optional[str] = None
    sector_etf_ticker: Optional[str] = None
    sector_etf_price: Optional[float] = None
    sector_etf_3m_perf: Optional[float] = None
    peer_etf_name: Optional[str] = None
    peer_etf_ticker: Optional[str] = None
    peer_etf_price: Optional[float] = None
    peer_etf_3m_perf: Optional[float] = None

    risk_warnings: list[str] = field(default_factory=list)
    disclaimers: list[str] = field(default_factory=list)


@dataclass
class FinancialStatement:
    period: str
    revenue: Optional[float] = None
    cost_of_revenue: Optional[float] = None
    gross_profit: Optional[float] = None
    operating_income: Optional[float] = None
    net_income: Optional[float] = None
    ebitda: Optional[float] = None
    interest_expense: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    total_equity: Optional[float] = None
    total_debt: Optional[float] = None
    total_cash: Optional[float] = None
    current_assets: Optional[float] = None
    current_liabilities: Optional[float] = None
    operating_cash_flow: Optional[float] = None
    capital_expenditure: Optional[float] = None
    free_cash_flow: Optional[float] = None
    dividends_paid: Optional[float] = None
    shares_outstanding: Optional[float] = None
    eps: Optional[float] = None
    book_value_per_share: Optional[float] = None
    # Financials-specific line items
    interest_income: Optional[float] = None
    net_interest_income: Optional[float] = None
    non_interest_income: Optional[float] = None
    non_interest_expense: Optional[float] = None
    provision_for_credit_losses: Optional[float] = None
    total_loans: Optional[float] = None
    total_deposits: Optional[float] = None
    earning_assets: Optional[float] = None
    interest_bearing_liabilities: Optional[float] = None
    allowance_for_loan_losses: Optional[float] = None
    non_performing_loans: Optional[float] = None
    net_charge_offs: Optional[float] = None
    cet1_capital: Optional[float] = None
    risk_weighted_assets: Optional[float] = None
    tangible_common_equity: Optional[float] = None
    # Insurance line items
    earned_premium: Optional[float] = None
    losses_incurred: Optional[float] = None
    underwriting_expenses: Optional[float] = None
    net_investment_income: Optional[float] = None
    invested_assets: Optional[float] = None
    insurance_reserves: Optional[float] = None
    # Asset managers
    aum: Optional[float] = None
    management_fees: Optional[float] = None
    performance_fees: Optional[float] = None
    net_inflows: Optional[float] = None
    # Common to all financials
    goodwill: Optional[float] = None
    intangibles: Optional[float] = None
    # Legacy IT-flavour fields kept for display/export compatibility (always None for Financials)
    research_development: Optional[float] = None
    selling_general_admin: Optional[float] = None
    stock_based_compensation: Optional[float] = None
    deferred_revenue: Optional[float] = None


@dataclass
class AnalysisConclusion:
    overall_score: float = 0.0
    verdict: str = ""
    summary: str = ""
    category_scores: dict = field(default_factory=dict)
    category_summaries: dict = field(default_factory=dict)
    strengths: list = field(default_factory=list)
    risks: list = field(default_factory=list)
    tier_note: str = ""
    stage_note: str = ""
    screening_checklist: dict = field(default_factory=dict)


@dataclass
class MetricExplanation:
    key: str
    full_name: str
    description: str
    why_used: str
    formula: str
    category: str


@dataclass
class Filing:
    form_type: str
    filing_date: str
    period: str
    url: str
    description: Optional[str] = None
    local_path: Optional[str] = None


@dataclass
class NewsArticle:
    title: str
    url: str
    published: Optional[str] = None
    source: Optional[str] = None
    summary: Optional[str] = None
    local_path: Optional[str] = None


@dataclass
class AnalysisReport:
    profile: CompanyProfile
    valuation: Optional[ValuationMetrics] = None
    profitability: Optional[ProfitabilityMetrics] = None
    solvency: Optional[SolvencyMetrics] = None
    growth: Optional[GrowthMetrics] = None
    efficiency: Optional[EfficiencyMetrics] = None
    finance_quality: Optional[FinanceQualityIndicators] = None
    intrinsic_value: Optional[IntrinsicValue] = None
    share_structure: Optional[ShareStructure] = None
    market_intelligence: Optional[MarketIntelligence] = None
    financials: list[FinancialStatement] = field(default_factory=list)
    filings: list[Filing] = field(default_factory=list)
    news: list[NewsArticle] = field(default_factory=list)
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ---------------------------------------------------------------------------
# Stage classification helpers (Financials lifecycle)
# ---------------------------------------------------------------------------

_STAGE_KEYWORDS = {
    CompanyStage.PLATFORM: [
        "g-sib", "globally systemically important", "global universal bank",
        "systemically important", "money center bank", "trillion in assets",
        "global financial franchise", "diversified global bank",
    ],
    CompanyStage.MATURE: [
        "mature", "free cash flow positive", "buyback", "dividend",
        "established franchise", "investment-grade", "established insurer",
        "stable underwriter", "consistent dividend",
    ],
    CompanyStage.SCALE: [
        "super-regional", "expanding nationally", "scaling distribution",
        "consolidator", "build out branch network",
    ],
    CompanyStage.GROWTH: [
        "expansion", "rapid loan growth", "branch expansion", "regional bank",
        "growth-stage insurer", "scaling aum", "rapid premium growth",
    ],
    CompanyStage.STARTUP: [
        "de novo", "newly chartered", "early-stage", "neobank", "challenger bank",
        "insurtech", "newly public", "recently chartered", "fintech startup",
    ],
}


_CATEGORY_KEYWORDS = {
    FinanceCategory.BANK_DIVERSIFIED: [
        "diversified bank", "universal bank", "money center bank", "global bank",
        "g-sib", "globally systemically important",
    ],
    FinanceCategory.BANK_REGIONAL: [
        "regional bank", "community bank", "super-regional", "savings bank",
        "thrift", "deposit-taking institution",
    ],
    FinanceCategory.INVESTMENT_BANK: [
        "investment bank", "broker-dealer", "investment banking",
        "trading and underwriting", "primary dealer", "prime brokerage",
        "merger advisory",
    ],
    FinanceCategory.INSURANCE_PC: [
        "property and casualty", "p&c insurer", "property & casualty",
        "auto insurance", "homeowners insurance", "commercial lines",
        "specialty insurance",
    ],
    FinanceCategory.INSURANCE_LIFE: [
        "life insurance", "annuities", "life and health", "pension provider",
        "life insurer", "variable annuity",
    ],
    FinanceCategory.REINSURANCE: [
        "reinsurance", "reinsurer", "catastrophe reinsurance",
    ],
    FinanceCategory.INSURANCE_BROKER: [
        "insurance brokerage", "insurance broker", "risk advisory",
        "employee benefits brokerage",
    ],
    FinanceCategory.ASSET_MANAGER: [
        "asset management", "wealth management", "investment manager",
        "etf provider", "mutual fund", "private banking", "fund manager",
    ],
    FinanceCategory.CAPITAL_MARKETS: [
        "exchange operator", "stock exchange", "clearing house",
        "market infrastructure", "post-trade", "trading venue",
        "depositary services",
    ],
    FinanceCategory.CONSUMER_FINANCE: [
        "consumer finance", "credit card", "auto finance", "personal loans",
        "subprime lending", "buy now pay later", "buy-now-pay-later",
        "installment lending",
    ],
    FinanceCategory.FINTECH: [
        "fintech", "payments", "payment processor", "neobank",
        "digital wallet", "remittance", "merchant acquiring", "payment network",
    ],
    FinanceCategory.MORTGAGE_FINANCE: [
        "mortgage reit", "mortgage finance", "mortgage origination",
        "mortgage servicing", "agency mbs",
    ],
    FinanceCategory.DIVERSIFIED: [
        "diversified financial services", "financial conglomerate",
        "diversified financials",
    ],
}


_TIER_1_JURISDICTIONS = {
    "united states", "usa", "canada", "united kingdom", "uk", "ireland",
    "germany", "france", "netherlands", "sweden", "denmark", "finland",
    "norway", "switzerland", "luxembourg", "belgium", "austria",
    "australia", "new zealand", "japan", "south korea", "singapore",
    "hong kong",
}

_TIER_2_JURISDICTIONS = {
    "spain", "portugal", "italy", "poland", "czech republic", "estonia",
    "latvia", "lithuania", "hungary", "greece", "cyprus",
    "india", "brazil", "mexico", "south africa", "chile",
    "uruguay", "turkey", "israel", "taiwan",
}


def classify_stage(description: Optional[str], revenue: Optional[float],
                   info: Optional[dict] = None) -> CompanyStage:
    if description is None:
        description = ""
    desc_lower = description.lower()

    rev = revenue or 0
    info = info or {}
    profit_margin = info.get("profitMargins")
    growth = info.get("revenueGrowth")
    mcap = info.get("marketCap") or 0

    # Very small banks / fintechs / insurers without traction → STARTUP
    if rev < 10_000_000 and (growth is None or growth < 0.10):
        return CompanyStage.STARTUP

    for stage in [CompanyStage.PLATFORM, CompanyStage.MATURE, CompanyStage.SCALE,
                  CompanyStage.GROWTH, CompanyStage.STARTUP]:
        for kw in _STAGE_KEYWORDS[stage]:
            if kw.lower() in desc_lower:
                return stage

    # G-SIBs / mega-cap diversified banks default to PLATFORM
    if mcap >= 200_000_000_000:
        return CompanyStage.PLATFORM
    if profit_margin is not None and profit_margin > 0.20 and mcap >= 10_000_000_000:
        return CompanyStage.MATURE
    if growth is not None and growth > 0.30:
        return CompanyStage.GROWTH
    if rev >= 1_000_000_000:
        return CompanyStage.SCALE
    return CompanyStage.GROWTH


def classify_category(description: Optional[str],
                      industry: Optional[str] = None) -> FinanceCategory:
    import re
    text = ((description or "") + " " + (industry or "")).lower()
    scores: dict[FinanceCategory, int] = {}
    for cat, keywords in _CATEGORY_KEYWORDS.items():
        count = 0
        for kw in keywords:
            kw_lower = kw.lower()
            if len(kw_lower) <= 3:
                if re.search(r'\b' + re.escape(kw_lower) + r'\b', text):
                    count += 1
            else:
                if kw_lower in text:
                    count += 1
        if count > 0:
            scores[cat] = count
    if scores:
        return max(scores, key=scores.get)
    # Fallback: industry-only mapping
    ind = (industry or "").lower()
    if "bank" in ind and "diversified" in ind:
        return FinanceCategory.BANK_DIVERSIFIED
    if "bank" in ind and ("regional" in ind or "community" in ind):
        return FinanceCategory.BANK_REGIONAL
    if "investment bank" in ind or "broker-dealer" in ind:
        return FinanceCategory.INVESTMENT_BANK
    if "bank" in ind:
        return FinanceCategory.BANK_DIVERSIFIED
    if "insurance" in ind and ("life" in ind or "annuit" in ind):
        return FinanceCategory.INSURANCE_LIFE
    if "insurance" in ind and ("property" in ind or "casualty" in ind):
        return FinanceCategory.INSURANCE_PC
    if "reinsurance" in ind:
        return FinanceCategory.REINSURANCE
    if "insurance broker" in ind:
        return FinanceCategory.INSURANCE_BROKER
    if "insurance" in ind:
        return FinanceCategory.INSURANCE_PC
    if "asset management" in ind or "capital markets" in ind:
        return FinanceCategory.ASSET_MANAGER
    if "credit services" in ind or "consumer finance" in ind:
        return FinanceCategory.CONSUMER_FINANCE
    if "mortgage" in ind:
        return FinanceCategory.MORTGAGE_FINANCE
    if "financial data" in ind or "exchange" in ind:
        return FinanceCategory.CAPITAL_MARKETS
    return FinanceCategory.OTHER


def classify_jurisdiction(country: Optional[str],
                          description: Optional[str] = None) -> JurisdictionTier:
    if not country:
        return JurisdictionTier.UNKNOWN
    c_lower = country.lower().strip()
    desc_lower = (description or "").lower()
    for j in _TIER_1_JURISDICTIONS:
        if j in c_lower or j in desc_lower:
            return JurisdictionTier.TIER_1
    for j in _TIER_2_JURISDICTIONS:
        if j in c_lower or j in desc_lower:
            return JurisdictionTier.TIER_2
    return JurisdictionTier.TIER_3


# Backwards-compat aliases — kept for callers that still import the old names.
classify_commodity = classify_category  # pragma: no cover
Commodity = FinanceCategory  # pragma: no cover
TechCategory = FinanceCategory  # pragma: no cover  (legacy alias)
