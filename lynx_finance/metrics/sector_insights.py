"""Financials-focused sector and industry insights."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SectorInsight:
    sector: str; overview: str; critical_metrics: list[str] = field(default_factory=list)
    key_risks: list[str] = field(default_factory=list); what_to_watch: list[str] = field(default_factory=list)
    typical_valuation: str = ""

@dataclass
class IndustryInsight:
    industry: str; sector: str; overview: str; critical_metrics: list[str] = field(default_factory=list)
    key_risks: list[str] = field(default_factory=list); what_to_watch: list[str] = field(default_factory=list)
    typical_valuation: str = ""

_SECTORS: dict[str, SectorInsight] = {}
_INDUSTRIES: dict[str, IndustryInsight] = {}

def _add_sector(sector, overview, cm, kr, wtw, tv):
    _SECTORS[sector.lower()] = SectorInsight(sector=sector, overview=overview, critical_metrics=cm, key_risks=kr, what_to_watch=wtw, typical_valuation=tv)

def _add_industry(industry, sector, overview, cm, kr, wtw, tv):
    _INDUSTRIES[industry.lower()] = IndustryInsight(industry=industry, sector=sector, overview=overview, critical_metrics=cm, key_risks=kr, what_to_watch=wtw, typical_valuation=tv)


_add_sector("Financial Services",
    "The Financials sector intermediates capital between savers and borrowers (banks), prices and pools risk (insurers), and manages wealth on behalf of investors (asset managers). Returns are highly sensitive to interest-rate cycles, credit cycles, and regulation. Banks operate on tight spreads (2-4% NIM) leveraged 10-12x — small changes in asset quality or funding costs cascade powerfully through earnings. Insurers monetize the float between premiums received and claims paid. Asset managers earn fees on AUM, which itself fluctuates with markets and flows. Capital adequacy (CET1) and asset quality (NPLs) are the regulatory must-watch metrics for banks; combined ratio dominates insurance; net inflows dominate asset managers.",
    ["CET1 / Tier 1 Capital Ratio", "Non-Performing Loans (NPL) ratio", "ROE / Return on Tangible Common Equity (ROTCE)", "Net Interest Margin (NIM)", "Efficiency Ratio (Cost-to-Income)", "Loan-to-Deposit Ratio", "Combined Ratio (insurers)", "Net Inflows / AUM (asset managers)"],
    ["Credit cycle turn — provisions spike, NPLs rise", "Deposit flight / funding stress (SVB-style runs)", "Maturity-mismatch losses on bond portfolios when rates rise", "Catastrophe shocks (insurers)", "AUM compression in market drawdowns (asset managers)", "Regulatory capital uplifts (Basel III endgame)", "Litigation / reserve releases distorting earnings"],
    ["CET1 trajectory and capital return programs", "NPL trends and reserve coverage", "NIM evolution as rates change", "Deposit growth and beta (cost-of-funds sensitivity)", "Combined ratio trends (insurers)", "AUM net flows split (active vs passive vs alts)", "Insider buying signals around bank stress events"],
    "P/TBV is the bank anchor (1.0-2.5x quality range). P/E for mature insurers (10-15x). P/AUM for asset managers (1.5-3.5%). Dividend yield 3-5% for mature franchises.")

_add_sector("Financials",
    "Same as 'Financial Services' — alternative naming used by some data providers (S&P GICS).",
    ["CET1 Ratio", "NPL Ratio", "ROE / ROTCE", "NIM", "Efficiency Ratio", "Combined Ratio"],
    ["Credit cycle, deposit flight, rate-cycle compression", "Catastrophe risk for insurers", "Regulatory uplifts"],
    ["CET1 trajectory", "Asset quality trends", "Net flows / AUM dynamics"],
    "P/TBV 1.0-2.5x for banks; P/E 10-15x for insurers; P/AUM 1.5-3.5% for asset managers.")

# ── Diversified / G-SIB Banks ─────────────────────────────────────
_add_industry("Banks - Diversified", "Financial Services",
    "Money-center / globally systemically important banks (JPM, BAC, C, HSBC, BNP, MUFG). Diversified across consumer banking, wealth management, investment banking, and trading. Benefit from scale, regulatory moats, and low-cost-of-deposits funding advantages. Heavily regulated under Basel III with G-SIB capital surcharges (1-3.5pp on top of CET1 minimums).",
    ["CET1 Ratio (target 12-14%)", "ROTCE (target >15%)", "Efficiency Ratio (<60%)", "Tangible Book / Share growth", "Fee Income mix (35-50%)"],
    ["G-SIB capital surcharge expansion (Basel III endgame)", "Trading-revenue volatility", "Litigation reserves (FX, mortgage, AML)", "Geopolitical exposure (China, Russia, EM)", "Bond-portfolio AOCI losses on rate moves"],
    ["CET1 trajectory + capital return announcements", "ROTCE through-cycle", "Investment-bank fee pool conditions", "Loan growth vs GDP", "Deposit beta (cost-of-funds sensitivity)"],
    "P/TBV 1.5-2.0x quality; P/E 9-12x; dividend yield 2.5-4%; payout ratios 25-35%.")

_add_industry("Banks - Regional", "Financial Services",
    "US regional / super-regional banks (USB, PNC, TFC, FITB, RF). Concentrated in commercial & industrial lending, commercial real estate, and consumer banking. More NIM-sensitive than diversified banks; less fee-income diversification. Vulnerable to deposit flight (SVB lesson) and CRE credit deterioration.",
    ["CET1 (target >11%)", "ROE / ROTCE (target >12%)", "NIM (3.0-3.5% normal)", "Efficiency Ratio (50-65%)", "Loan-to-Deposit (75-90%)", "CRE concentration"],
    ["CRE losses (office)", "Deposit beta acceleration in rate cycles", "Held-to-Maturity bond losses (AOCI)", "Loan-growth deceleration with rate hikes", "M&A / consolidation pressure on subscale players"],
    ["NIM trajectory and deposit beta", "CRE credit quality trends", "Loan growth vs deposit growth", "Capital return programs", "Regional economic conditions"],
    "P/TBV 1.0-1.5x quality; P/E 8-12x; dividend yield 3-5%; payout ratios 30-45%.")

_add_industry("Banks", "Financial Services",
    "General banking sector — covers diversified, regional, and savings banks. Quality depends on funding mix (deposit-heavy = quality), capital strength, and asset quality through cycles.",
    ["CET1", "NPL Ratio", "ROE / ROTCE", "NIM", "Efficiency Ratio", "LDR"],
    ["Credit cycle turn", "Deposit flight", "Rate-cycle NIM compression"],
    ["CET1 trajectory", "Asset quality", "Deposit and loan growth"],
    "P/TBV 1.0-2.0x; P/E 8-12x; dividend yield 3-5%.")

# ── Investment Banks & Capital Markets ────────────────────────────
_add_industry("Capital Markets", "Financial Services",
    "Investment banks, broker-dealers, and capital-markets infrastructure (GS, MS, MKTX, ICE). Revenue tied to deal activity (M&A, IPO, debt issuance), trading volumes, and asset-management fees. Highly cyclical with deal cycles; trading FICC revenue spikes in volatility.",
    ["ROTCE (>15% target)", "Compensation Ratio (35-45%)", "Pre-tax margin", "Investment Banking fee pool"],
    ["Deal cycle downturn", "Trading-revenue volatility", "Litigation / regulatory fines", "Compensation inflation", "Private-credit substitution risk"],
    ["IB fee-pool indicators (M&A pipeline, IPO calendar)", "Trading volumes vs market vols", "Comp ratio trends", "Wealth-management AUM growth"],
    "P/TBV 1.2-1.8x; P/E 8-13x; cyclically depressed multiples in down years.")

_add_industry("Financial Data & Stock Exchanges", "Financial Services",
    "Exchange operators (CME, ICE, NDAQ, MKTX, MCO) and financial-data providers (S&P Global, MSCI, FactSet, MORN). Capital-light, recurring-revenue, mission-critical infrastructure. Trade at premium multiples — among the highest-quality businesses in financials.",
    ["Recurring Revenue %", "Operating Margin (40-60%)", "Revenue Growth", "FCF Conversion (>1.0)", "Subscription renewals"],
    ["Pricing pressure from regulators", "Index-licensing competition", "Market-structure changes (decimalization, MIFID)"],
    ["Pricing actions and renewal rates", "Trading volume trends (exchanges)", "ESG / index licensing wins"],
    "EV/EBITDA 18-30x; P/E 25-40x; dividend yield 1-2%; among the highest-multiple financials.")

# ── Insurance ──────────────────────────────────────────────────────
_add_industry("Insurance - Property & Casualty", "Financial Services",
    "P&C insurers (TRV, ALL, PGR, CB, WRB). Underwriting cycles drive profitability — combined ratio is the gate. Catastrophe years (e.g. 2017, 2022) hammer earnings; soft markets compress pricing. Quality insurers achieve combined ratios <95% through cycles + 4-5% investment yield on float.",
    ["Combined Ratio (<100% = profit)", "Loss Ratio", "Expense Ratio", "Investment Yield (3-5%)", "Premium Growth", "Reserve Adequacy"],
    ["Catastrophe events (hurricanes, wildfires)", "Reserve inadequacy on long-tail lines (workers' comp)", "Soft pricing cycles", "Climate-driven loss escalation", "Reinsurance pricing (impacts retained losses)"],
    ["Combined ratio trends (peer comparison)", "Hard / soft pricing market signals", "Catastrophe budget vs actuals", "Reserve releases / strengthening"],
    "P/E 10-15x; P/TBV 1.2-2.0x; dividend yield 2-3%.")

_add_industry("Insurance - Life", "Financial Services",
    "Life and annuities (MET, PRU, AFL, MFC). Long-duration liabilities, sensitive to long-rates and mortality assumptions. Embedded value (EV) is the alternative valuation anchor. Variable-annuity guarantees create equity-market sensitivity.",
    ["Embedded Value", "VNB Margin", "Statutory Capital", "Investment Yield", "Spread compression"],
    ["Low-rate environment crushing spreads", "Mortality assumptions update (COVID)", "Variable-annuity guarantee losses in market crashes", "Long-duration asset/liability mismatch"],
    ["EV growth", "Spread evolution", "VNB margins by product", "Capital generation"],
    "P/E 7-12x; P/EV 0.6-1.0x; dividend yield 3-5%.")

_add_industry("Insurance - Reinsurance", "Financial Services",
    "Reinsurance (RNR, EG, MUV2, RGA). Take outsized cat risk; benefit from hard pricing post-cat events. Highly cyclical with 2-4 year hard-soft cycles. ILS / catastrophe bond competition pressures pricing in soft markets.",
    ["Combined Ratio", "Catastrophe Budget", "Reinsurance pricing index", "Capital Adequacy"],
    ["Cat event clusters compounding losses", "Soft-market pricing collapse", "ILS substitution"],
    ["Cat budget burn rate", "Reinsurance renewal pricing trends", "Hard vs soft cycle indicators"],
    "P/E 8-13x; P/TBV 1.0-1.5x; cyclically depressed in hard-market lead years.")

_add_industry("Insurance - Specialty", "Financial Services",
    "Specialty insurance (WRB, MKL, AFG). Niche underwriting (E&S, professional liability). Higher-quality combined ratios than generalists; smaller, more focused competitive moats.",
    ["Combined Ratio (<90% target)", "Premium Growth", "Reserve Releases", "Tier 1 capital"],
    ["Specialty-line cycle deterioration", "Reserve inadequacy on long-tail specialty lines"],
    ["Combined ratio peer comparison", "Specialty-line pricing trends"],
    "P/E 10-15x; P/TBV 1.5-2.5x; quality premium for consistent <95% CR.")

_add_industry("Insurance - Diversified", "Financial Services",
    "Diversified insurers — combine P&C, life, asset management (BRK, AIG, ZURN). Conglomerate structure with cross-segment capital allocation. Berkshire Hathaway is the archetype; trades on book value compounding.",
    ["Book Value Growth", "Operating Earnings", "Investment Income", "Combined Ratio"],
    ["Conglomerate discount", "Capital allocation missteps", "Reserve adequacy across segments"],
    ["Book value/share growth", "Float growth (insurers)", "Capital deployment record"],
    "P/B 1.2-1.8x; quality compounders trade closer to 1.5-2.0x BV.")

_add_industry("Insurance Brokers", "Financial Services",
    "Insurance brokers (MMC, AON, AJG, BRO, WTW). Capital-light, fee-based. Don't take underwriting risk — earn commissions on premiums placed. Mid-single-digit organic growth; high free-cash-flow conversion. Trade at premium multiples.",
    ["Organic Revenue Growth (4-7%)", "Operating Margin (20-30%)", "FCF Conversion (>0.9)", "Free cash flow yield"],
    ["M&A integration risk", "Pricing pressure from insurer consolidation", "Wage inflation"],
    ["Organic revenue growth (key signal)", "M&A pace and integration", "Margin trajectory"],
    "P/E 25-35x; EV/EBITDA 18-28x; among the most highly-rated financials.")

# ── Asset & Wealth Management ─────────────────────────────────────
_add_industry("Asset Management", "Financial Services",
    "Asset managers (BLK, BX, KKR, APO, TROW, STT). Revenue tied to fee × AUM. Net inflows are the durable growth signal — market performance is exogenous. Fee compression from passive (ETFs) is a 20-year secular headwind for active managers; alternatives (PE, RE, credit) command premium fees.",
    ["AUM Growth (decompose into market + flows)", "Net Inflows / Starting AUM (>3% = healthy)", "Effective Fee Rate (bps)", "Operating Margin (40-50% mature)", "Compensation Ratio"],
    ["Market drawdown compressing fee revenue immediately", "Active-to-passive flow migration", "Fee compression in active strategies", "Performance-fee volatility (alts)"],
    ["Net flows by asset class (active/passive/alts)", "Effective fee rate trends", "AUM mix shift to alts"],
    "P/AUM 1.5-3.5%; P/E 12-22x for diversified; alts managers (BX, KKR, APO) trade at premium 20-30x.")

# ── Consumer Finance & Credit ─────────────────────────────────────
_add_industry("Credit Services", "Financial Services",
    "Consumer credit, credit cards, BNPL (V, MA, AXP, COF, DFS, SYF, AFRM). Mix of network operators (V, MA — capital-light, near-monopolies), card issuers (AXP, COF — credit-cycle sensitive), and BNPL upstarts. Network operators trade at premium tech-like multiples.",
    ["Loan growth", "Net Charge-Off Ratio (3-5% normal for cards)", "Reserve Coverage", "Operating Margin", "Active Cardholder Growth"],
    ["Consumer credit-cycle deterioration", "BNPL credit-quality unknowns", "Interchange fee regulation"],
    ["Charge-off trends (leading indicator)", "Credit-card spend volume", "Consumer-credit availability"],
    "Network operators (V, MA): P/E 25-35x — premium quality. Issuers (AXP, COF): P/E 8-13x — cycle-dependent.")

_add_industry("Consumer Finance", "Financial Services",
    "Personal loans, auto finance, BNPL (DFS, SLM, ALLY, AFRM, UPST). Credit-cycle sensitive; FICO mix matters enormously. Subprime issuers see severe charge-off swings.",
    ["Charge-off Ratio", "Loan Loss Reserve Coverage", "Funding cost", "Origination volumes"],
    ["Subprime credit-cycle losses", "Funding-cost spikes", "Regulatory caps on interest rates / late fees"],
    ["Charge-off trends", "Origination quality (FICO mix)", "Funding spread"],
    "P/E 7-13x; P/TBV 0.8-1.5x; cyclically depressed in stress.")

# ── Mortgage Finance ───────────────────────────────────────────────
_add_industry("Mortgage Finance", "Financial Services",
    "Mortgage originators, servicers, and mortgage REITs (RKT, COOP, NRZ, AGNC, NLY). Highly rate-sensitive — origination volumes plunge in rate hikes; mortgage REITs face spread compression and prepayment shocks.",
    ["MSR Valuation", "Gain on Sale Margin", "Origination Volume", "Net Interest Spread (mREITs)"],
    ["Rate-cycle origination collapse", "MSR write-downs", "Prepayment shocks for mREITs"],
    ["Mortgage origination volumes vs prior year", "MSR mark-to-market", "30Y mortgage rate vs 10Y treasury"],
    "P/E volatile (cycle-dependent). mREITs valued on dividend yield + book value preservation.")

# ── Fintech & Payments ────────────────────────────────────────────
_add_industry("Software - Financial / Fintech", "Financial Services",
    "Pure-play fintech and payment platforms (SQ, PYPL, ADYEY, UPST, AFRM). Mix of capital-light tech-like models (payments) and capital-intensive lenders. High revenue growth at the cost of GAAP profitability for many.",
    ["Take Rate", "Payment Volume Growth", "Active Customer Growth", "Operating Margin", "FCF Margin"],
    ["Take-rate compression from competition", "Big-tech payment competition (Apple Pay)", "Regulatory scrutiny on BNPL", "Crypto exposure unknowns"],
    ["Payment volume growth normalization", "Active user trends", "Take-rate trajectory"],
    "EV/Revenue 3-12x for fintech; mature payment networks trade like infrastructure (P/E 25-35x).")


def get_sector_insight(sector: str | None) -> SectorInsight | None:
    return _SECTORS.get(sector.lower()) if sector else None

def get_industry_insight(industry: str | None) -> IndustryInsight | None:
    return _INDUSTRIES.get(industry.lower()) if industry else None

def list_sectors() -> list[str]:
    return sorted(s.sector for s in _SECTORS.values())

def list_industries() -> list[str]:
    return sorted(i.industry for i in _INDUSTRIES.values())
