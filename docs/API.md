# Lynx Financials Analysis -- API Reference

Public Python API for the `lynx_finance` package (v2.0).

## Package Structure

```
lynx_finance/
├── __init__.py          # Version, about text
├── __main__.py          # Entry point
├── cli.py               # CLI argument parser
├── display.py           # Rich console display
├── interactive.py       # Interactive REPL mode
├── easter.py            # Hidden features
├── models.py            # Data models
├── core/
│   ├── analyzer.py      # Analysis orchestrator
│   ├── conclusion.py    # Verdict synthesis
│   ├── fetcher.py       # yfinance data fetching
│   ├── news.py          # News aggregation
│   ├── reports.py       # SEC/SEDAR filing fetching
│   ├── storage.py       # Cache management
│   └── ticker.py        # Ticker resolution
├── metrics/
│   ├── calculator.py    # Metric calculations
│   ├── relevance.py     # Metric relevance by stage/tier
│   ├── explanations.py  # Metric educational content
│   └── sector_insights.py # Financials industry insights
├── export/
│   ├── __init__.py      # Export dispatcher
│   ├── txt_export.py    # Plain text export
│   ├── html_export.py   # HTML export
│   └── pdf_export.py    # PDF export
├── gui/
│   └── app.py           # Tkinter GUI
└── tui/
    ├── app.py           # Textual TUI
    └── themes.py        # TUI color themes
```

---

## Core API

### Analysis (`lynx_finance.core.analyzer`)

#### `run_full_analysis`

```python
def run_full_analysis(
    identifier: str,
    download_reports: bool = True,
    download_news: bool = True,
    max_filings: int = 10,
    verbose: bool = False,
    refresh: bool = False,
) -> AnalysisReport
```

Run a complete fundamental analysis for an Financials sector company.
This is a convenience wrapper around `run_progressive_analysis` with
`on_progress=None`.

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `identifier` | `str` | required | Ticker symbol (`JPM`), ISIN (`US46625H1005`), or company name (`JPMorgan Chase`). |
| `download_reports` | `bool` | `True` | Fetch SEC/SEDAR filings. |
| `download_news` | `bool` | `True` | Fetch recent news articles. |
| `max_filings` | `int` | `10` | Maximum number of filings to download locally. |
| `verbose` | `bool` | `False` | Enable verbose console output. |
| `refresh` | `bool` | `False` | Force re-fetch from network even if cached data exists. |

**Returns:** `AnalysisReport` -- fully populated report dataclass.

**Example:**

```python
from lynx_finance.core.analyzer import run_full_analysis

report = run_full_analysis("JPM")
print(report.profile.name)       # "JPMorgan Chase & Co"
print(report.profile.tier.value) # "Mid Cap"
print(report.solvency.cash_runway_years)
```

---

#### `run_progressive_analysis`

```python
def run_progressive_analysis(
    identifier: str,
    download_reports: bool = True,
    download_news: bool = True,
    max_filings: int = 10,
    verbose: bool = False,
    refresh: bool = False,
    on_progress: Optional[Callable[[str, AnalysisReport], None]] = None,
) -> AnalysisReport
```

Same as `run_full_analysis`, but accepts a progress callback that is invoked
after each analysis stage completes.  Used by the TUI and GUI interfaces to
update the display incrementally.

**Callback stages** (passed as the first `str` argument):

`"profile"` | `"financials"` | `"valuation"` | `"profitability"` |
`"solvency"` | `"growth"` | `"share_structure"` | `"finance_quality"` |
`"intrinsic_value"` | `"market_intelligence"` | `"filings"` | `"news"` |
`"conclusion"` | `"complete"`

**Example:**

```python
from lynx_finance.core.analyzer import run_progressive_analysis

def on_progress(stage: str, report):
    print(f"Stage complete: {stage}")

report = run_progressive_analysis("JPM", on_progress=on_progress)
```

---

### Conclusion (`lynx_finance.core.conclusion`)

#### `generate_conclusion`

```python
def generate_conclusion(report: AnalysisReport) -> AnalysisConclusion
```

Synthesize a scored verdict from a completed `AnalysisReport`.

Scoring weights are determined by the company's `(stage, tier)` combination.
For example, solvency and finance quality are weighted much more heavily for
nano-cap fintechs than for mega-cap diversified banks.

**Returns:** `AnalysisConclusion` with:

- `overall_score` -- 0-100 composite score.
- `verdict` -- one of `"Strong Buy"`, `"Buy"`, `"Hold"`, `"Caution"`, `"Avoid"`.
- `summary` -- one-paragraph narrative.
- `category_scores` -- dict with scores for `valuation`, `profitability`, `solvency`, `growth`, `finance_quality`.
- `category_summaries` -- dict with human-readable summary per category.
- `strengths` / `risks` -- lists of up to 6 key points each.
- `tier_note` / `stage_note` -- explanations of why certain metrics matter for this company.
- `screening_checklist` -- dict of boolean pass/fail/None checks (e.g. `cet1_well_capitalized`, `asset_quality_healthy`, `high_returns`).

**Example:**

```python
from lynx_finance.core.conclusion import generate_conclusion

conclusion = generate_conclusion(report)
print(conclusion.verdict)          # "Hold"
print(conclusion.overall_score)    # 52.3
print(conclusion.strengths)        # ["Strong CET1 capital (14.1%)", ...]
print(conclusion.screening_checklist)
```

---

## Data Models (`lynx_finance.models`)

All models are Python `dataclasses`.  Every numeric field defaults to `None`
(meaning "not available") unless otherwise noted.

### Enums

| Enum | Values |
|---|---|
| `CompanyTier` | `MEGA`, `LARGE`, `MID`, `SMALL`, `MICRO`, `NANO` |
| `CompanyStage` | `STARTUP`, `GROWTH`, `SCALE`, `MATURE`, `PLATFORM` |
| `FinanceCategory` | `BANK_DIVERSIFIED`, `BANK_REGIONAL`, `INVESTMENT_BANK`, `INSURANCE_PC`, `INSURANCE_LIFE`, `REINSURANCE`, `INSURANCE_BROKER`, `ASSET_MANAGER`, `CAPITAL_MARKETS`, `CONSUMER_FINANCE`, `FINTECH`, `MORTGAGE_FINANCE`, `DIVERSIFIED`, `OTHER` |
| `JurisdictionTier` | `TIER_1` (Low Risk), `TIER_2` (Moderate Risk), `TIER_3` (High Risk), `UNKNOWN` |
| `Relevance` | `CRITICAL`, `RELEVANT`, `CONTEXTUAL`, `IRRELEVANT` |

### Core Dataclasses

#### `CompanyProfile`

Company identity and classification.

| Field | Type | Description |
|---|---|---|
| `ticker` | `str` | Resolved ticker symbol. |
| `name` | `str` | Company name. |
| `isin` | `Optional[str]` | ISIN code if resolved. |
| `sector` | `Optional[str]` | Sector (e.g. `"Financial Services"` / `"Financials"`). |
| `industry` | `Optional[str]` | Industry (e.g. `"Banks - Diversified"`). |
| `country` | `Optional[str]` | Country of domicile. |
| `exchange` | `Optional[str]` | Primary exchange. |
| `currency` | `Optional[str]` | Reporting currency. |
| `market_cap` | `Optional[float]` | Market capitalization. |
| `description` | `Optional[str]` | Company description from filings. |
| `website` | `Optional[str]` | Corporate website. |
| `employees` | `Optional[int]` | Number of employees. |
| `tier` | `CompanyTier` | Market-cap tier (default `NANO`). |
| `stage` | `CompanyStage` | Financials lifecycle stage (default `STARTUP`). |
| `finance_category` | `FinanceCategory` | Primary Financials sub-category (default `OTHER`). |
| `jurisdiction_tier` | `JurisdictionTier` | Jurisdiction risk tier (default `UNKNOWN`). |
| `jurisdiction_country` | `Optional[str]` | Country used for jurisdiction classification. |

#### `ValuationMetrics`

Traditional and Financials-specific valuation ratios.

Key fields: `pe_trailing`, `pe_forward`, `pb_ratio`, `ps_ratio`, `p_fcf`,
`ev_ebitda`, `ev_revenue`, `peg_ratio`, `dividend_yield`, `earnings_yield`,
`enterprise_value`, `market_cap`, `price_to_tangible_book`, `price_to_ncav`,
`ev_per_resource_oz`, `ev_per_resource_lb`, `p_nav`, `cash_to_market_cap`,
`nav_per_share`.

#### `ProfitabilityMetrics`

Margins and returns, plus Financials-specific metrics (NIM, ROTCE, Efficiency, Combined Ratio).

Key fields: `roe`, `roa`, `roic`, `gross_margin`, `operating_margin`,
`net_margin`, `fcf_margin`, `ebitda_margin`, `aisc_per_unit`, `aisc_unit`,
`cash_cost_per_unit`, `aisc_margin`.

#### `SolvencyMetrics`

Balance sheet health and cash survival metrics.

Key fields: `debt_to_equity`, `debt_to_ebitda`, `current_ratio`, `quick_ratio`,
`interest_coverage`, `altman_z_score`, `net_debt`, `total_debt`, `total_cash`,
`cash_burn_rate`, `cash_runway_years`, `working_capital`, `cash_per_share`,
`tangible_book_value`, `ncav`, `ncav_per_share`, `quarterly_burn_rate`,
`burn_as_pct_of_market_cap`.

#### `GrowthMetrics`

Revenue, earnings, and dilution growth rates.

Key fields: `revenue_growth_yoy`, `revenue_cagr_3y`, `revenue_cagr_5y`,
`earnings_growth_yoy`, `earnings_cagr_3y`, `earnings_cagr_5y`,
`fcf_growth_yoy`, `book_value_growth_yoy`, `dividend_growth_5y`,
`shares_growth_yoy`, `shares_growth_3y_cagr`, `fully_diluted_shares`,
`dilution_ratio`, `production_growth_yoy`.

#### `EfficiencyMetrics`

Operational efficiency ratios.

Key fields: `asset_turnover`, `inventory_turnover`, `receivables_turnover`,
`days_sales_outstanding`, `days_inventory`, `cash_conversion_cycle`.

#### `FinanceQualityIndicators`

Composite quality score and qualitative assessments.

Key fields: `quality_score` (0-100), `management_quality`,
`high_returns_pct`, `management_track_record`,
`jurisdiction_assessment`, `jurisdiction_score`, `geological_quality`,
`resource_grade_assessment`, `resource_scale_assessment`,
`financial_position`, `dilution_risk`, `share_structure_assessment`,
`catalyst_density`, `near_term_catalysts` (list), `strategic_backing`,
`competitive_position`, `asset_backing`, `niche_position`,
`insider_alignment`, `revenue_predictability`,
`roic_history` (list), `gross_margin_history` (list).

#### `IntrinsicValue`

Intrinsic value estimates using multiple methods.

Key fields: `dcf_value`, `graham_number`, `lynch_fair_value`, `ncav_value`,
`asset_based_value`, `nav_per_share`, `ev_resource_implied_price`,
`current_price`, `margin_of_safety_dcf`, `margin_of_safety_graham`,
`margin_of_safety_ncav`, `margin_of_safety_asset`, `margin_of_safety_nav`,
`primary_method`, `secondary_method`.

The `primary_method` and `secondary_method` fields indicate which valuation
approach is most appropriate for the company's stage (e.g. `"dcf"` for
producers, `"asset_based"` for explorers).

#### `ShareStructure`

Share count, dilution, and ownership breakdown.

Key fields: `shares_outstanding`, `fully_diluted_shares`,
`warrants_outstanding`, `options_outstanding`, `high_returns_pct`,
`institutional_ownership_pct`, `float_shares`,
`share_structure_assessment`, `warrant_overhang_risk`.

#### `InsiderTransaction`

A single insider buy/sell transaction.

Fields: `insider`, `position`, `transaction_type`, `shares`, `value`, `date`.

#### `MarketIntelligence`

Market sentiment, insider activity, institutional holdings, technicals, and
projected dilution.

Groups of fields:
- **Insider activity:** `insider_transactions` (list of `InsiderTransaction`),
  `net_insider_shares_3m`, `insider_buy_signal`.
- **Institutional holders:** `top_holders`, `institutions_count`, `institutions_pct`.
- **Analyst consensus:** `analyst_count`, `recommendation`, `target_high`,
  `target_low`, `target_mean`, `target_upside_pct`.
- **Short interest:** `shares_short`, `short_pct_of_float`, `short_ratio_days`,
  `short_squeeze_risk`.
- **Price technicals:** `price_current`, `price_52w_high`, `price_52w_low`,
  `pct_from_52w_high`, `pct_from_52w_low`, `price_52w_range_position`,
  `sma_50`, `sma_200`, `above_sma_50`, `above_sma_200`, `golden_cross`,
  `beta`, `avg_volume`, `volume_10d_avg`, `volume_trend`.
- **Projected dilution:** `projected_dilution_annual_pct`,
  `projected_shares_in_2y`, `financing_warning`.
- **Risk warnings:** `risk_warnings` (list), `disclaimers` (list).

#### `FinancialStatement`

One annual fiscal period.

Fields: `period`, `revenue`, `cost_of_revenue`, `gross_profit`,
`operating_income`, `net_income`, `ebitda`, `interest_expense`,
`total_assets`, `total_liabilities`, `total_equity`, `total_debt`,
`total_cash`, `current_assets`, `current_liabilities`,
`operating_cash_flow`, `capital_expenditure`, `free_cash_flow`,
`dividends_paid`, `shares_outstanding`, `eps`, `book_value_per_share`,
`exploration_expenditure`, `mineral_properties`.

#### `AnalysisConclusion`

Scored verdict produced by `generate_conclusion`.

Fields: `overall_score`, `verdict`, `summary`, `category_scores`,
`category_summaries`, `strengths`, `risks`, `tier_note`, `stage_note`,
`screening_checklist`.

#### `Filing`

An SEC/SEDAR filing reference.

Fields: `form_type`, `filing_date`, `period`, `url`, `description`,
`local_path`.

#### `NewsArticle`

A news article reference.

Fields: `title`, `url`, `published`, `source`, `summary`, `local_path`.

#### `AnalysisReport`

The main container returned by analysis functions.

| Field | Type | Description |
|---|---|---|
| `profile` | `CompanyProfile` | Always populated. |
| `valuation` | `Optional[ValuationMetrics]` | Valuation ratios. |
| `profitability` | `Optional[ProfitabilityMetrics]` | Margin and return metrics. |
| `solvency` | `Optional[SolvencyMetrics]` | Balance sheet health. |
| `growth` | `Optional[GrowthMetrics]` | Growth rates and dilution. |
| `efficiency` | `Optional[EfficiencyMetrics]` | Operational efficiency. |
| `finance_quality` | `Optional[FinanceQualityIndicators]` | Composite quality score. |
| `intrinsic_value` | `Optional[IntrinsicValue]` | Intrinsic value estimates. |
| `share_structure` | `Optional[ShareStructure]` | Share count and ownership. |
| `market_intelligence` | `Optional[MarketIntelligence]` | Sentiment and technicals. |
| `financials` | `list[FinancialStatement]` | Annual financial statements. |
| `filings` | `list[Filing]` | SEC/SEDAR filings. |
| `news` | `list[NewsArticle]` | Recent news articles. |
| `fetched_at` | `str` | ISO timestamp of when data was fetched. |

---

## Classification Helpers (`lynx_finance.models`)

#### `classify_tier`

```python
def classify_tier(market_cap: Optional[float]) -> CompanyTier
```

Classify by market capitalization:

| Threshold | Tier |
|---|---|
| >= $200B | Mega Cap |
| >= $10B | Large Cap |
| >= $2B | Mid Cap |
| >= $300M | Small Cap |
| >= $50M | Micro Cap |
| < $50M or None | Nano Cap |

#### `classify_stage`

```python
def classify_stage(
    description: Optional[str],
    revenue: Optional[float],
    info: Optional[dict] = None,
) -> CompanyStage
```

Classify Financials lifecycle stage by keyword matching against the company
description.  Companies with revenue > $10M and royalty/streaming keywords
are classified as `PLATFORM`.  Falls back to industry-based heuristics from
`info` if no keywords match.

#### `classify_category`

```python
def classify_category(
    description: Optional[str],
    industry: Optional[str] = None,
) -> FinanceCategory
```

Identify primary Financials sub-category from description and industry text using
keyword frequency scoring.  Uses word-boundary matching for short keywords
(e.g. "Au", "Cu") to avoid false positives.

#### `classify_jurisdiction`

```python
def classify_jurisdiction(
    country: Optional[str],
    description: Optional[str] = None,
) -> JurisdictionTier
```

Classify jurisdiction risk:

- **Tier 1 (Low Risk):** Canada, USA, Australia, Finland, Ireland, Sweden.
- **Tier 2 (Moderate Risk):** Mexico, Peru, Chile, Brazil, Argentina, Botswana, Namibia, Tanzania, Ghana, Spain, Portugal, Turkey, Serbia, and others.
- **Tier 3 (High Risk):** Everything else.

---

## Metrics Calculator (`lynx_finance.metrics.calculator`)

All `calc_*` functions accept `info` (yfinance info dict), `statements`
(list of `FinancialStatement`), and tier/stage classification.  They return
the corresponding metrics dataclass with all fields computed from available
data.

| Function | Returns | Description |
|---|---|---|
| `calc_valuation(info, statements, tier, stage)` | `ValuationMetrics` | P/E, P/B, EV/EBITDA, P/FCF, cash-to-market-cap, tangible book, NCAV. Financials-specific: P/TBV, P/AUM, P/Premium, Excess Capital % MC. |
| `calc_profitability(info, statements, tier, stage)` | `ProfitabilityMetrics` | ROE, ROA, ROIC, gross/operating/net/FCF/EBITDA margins. Financials-specific: NIM, ROTCE, Efficiency Ratio, Combined Ratio (insurers), Fee Income Ratio. |
| `calc_solvency(info, statements, tier, stage)` | `SolvencyMetrics` | D/E, current/quick ratios, Altman Z, cash burn rate, cash runway, working capital, NCAV. |
| `calc_growth(statements, tier, stage)` | `GrowthMetrics` | Revenue/earnings YoY and CAGR (3y, 5y). Share dilution YoY and 3y CAGR. Book value growth. |
| `calc_efficiency(info, statements, tier)` | `EfficiencyMetrics` | Asset turnover. |
| `calc_share_structure(info, statements, growth, tier, stage)` | `ShareStructure` | Outstanding/fully-diluted shares, insider/institutional ownership %, structure assessment. |
| `calc_finance_quality(profitability, growth, solvency, share_structure, statements, info, tier, stage)` | `FinanceQualityIndicators` | Composite quality score (0-100) based on insider ownership, financial position, dilution risk, jurisdiction, and more. |
| `calc_intrinsic_value(info, statements, growth, solvency, tier, stage, discount_rate=0.10, terminal_growth=0.03)` | `IntrinsicValue` | DCF, Graham number, Lynch fair value, NCAV, asset-based value, NAV/share. Method selection is stage-aware. |
| `calc_market_intelligence(info, ticker_obj, solvency, share_structure, growth, tier, stage)` | `MarketIntelligence` | Insider transactions, institutional holders, analyst consensus, short interest, price technicals, projected dilution, risk warnings. |

---

## Relevance System (`lynx_finance.metrics.relevance`)

#### `get_relevance`

```python
def get_relevance(
    metric_key: str,
    tier: CompanyTier,
    category: str = "valuation",
    stage: CompanyStage = CompanyStage.GROWTH,
) -> Relevance
```

Look up the relevance level of a metric given the company's tier and stage.

**Stage overrides take precedence** over tier-based lookups, because
development stage is the primary analytical axis for Financials sector companies.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `metric_key` | `str` | Metric field name (e.g. `"cash_runway_years"`, `"pe_trailing"`). |
| `tier` | `CompanyTier` | Company size tier. |
| `category` | `str` | One of `"valuation"`, `"profitability"`, `"solvency"`, `"growth"`, `"finance_quality"`, `"share_structure"`. |
| `stage` | `CompanyStage` | Financials lifecycle stage. |

**Returns:** `Relevance` enum value.

### Relevance Levels

| Level | Meaning | Visual Treatment |
|---|---|---|
| `CRITICAL` | Must-check metric for this stage/tier. | Bold with star marker. |
| `RELEVANT` | Important, displayed normally. | Normal display. |
| `CONTEXTUAL` | Informational only, not a primary decision driver. | Dimmed. |
| `IRRELEVANT` | Not meaningful for this stage/tier. | Hidden or struck-through. |

**Stage-driven examples:**

- `cash_runway_years` is `CRITICAL` for Startup, Hyper-Growth, Scale-Up; `CONTEXTUAL` for Mature; `IRRELEVANT` for Platform.
- `pe_trailing` is `IRRELEVANT` for Startup, Hyper-Growth, Scale-Up; `RELEVANT` for Mature and Platform.
- `shares_growth_yoy` is `CRITICAL` for Startup, Hyper-Growth, Scale-Up; `RELEVANT` for Mature and Platform.

---

## Storage (`lynx_finance.core.storage`)

Two isolated data directories: `data/` (production) and `data_test/` (testing).

#### `set_mode`

```python
def set_mode(mode: str) -> None
```

Set the storage mode.  `mode` must be `"production"` or `"testing"`.

In testing mode, cache reads are disabled (always returns `None`/`False`)
to ensure fresh data.

#### `has_cache`

```python
def has_cache(ticker: str) -> bool
```

Returns `True` if a cached `analysis_latest.json` exists for this ticker.
Always returns `False` in testing mode.

#### `load_cached_report`

```python
def load_cached_report(ticker: str) -> Optional[dict]
```

Load the latest cached analysis as a raw dict, or `None` if unavailable.

#### `save_analysis_report`

```python
def save_analysis_report(ticker: str, report_dict: dict) -> Path
```

Save an analysis report dict.  Creates both a timestamped file
(`analysis_YYYYMMDD_HHMMSS.json`) and an `analysis_latest.json` symlink.
Returns the path to the timestamped file.

#### `list_cached_tickers`

```python
def list_cached_tickers() -> list[dict]
```

List all cached tickers with metadata.  Each dict contains:
`ticker`, `path`, `name`, `tier`, `stage`, `fetched_at`, `age_hours`,
`files` (count), `size_mb`.

#### `drop_cache_ticker`

```python
def drop_cache_ticker(ticker: str) -> bool
```

Delete all cached data for a ticker.  Returns `True` if data existed.

#### `drop_cache_all`

```python
def drop_cache_all() -> int
```

Delete all cached data.  Returns the number of ticker directories removed.

---

## Ticker Resolution (`lynx_finance.core.ticker`)

#### `resolve_identifier`

```python
def resolve_identifier(identifier: str) -> tuple[str, str | None]
```

Resolve a user-provided identifier to a `(ticker, isin)` tuple.

Accepts:
- **Ticker symbols:** `JPM`, `BLK`, `BAC`, `TRV`
- **ISIN codes:** `US46625H1005` (12-character format)
- **Company names:** `"JPMorgan Chase"`, `"BlackRock"`

Resolution strategy:
1. ISIN -- search via yfinance, return best equity match.
2. Company name (contains spaces or > 12 chars) -- search.
3. Direct ticker probe -- check if the symbol has price data.
4. Suffix scan -- try common exchange suffixes (`.V`, `.TO`, `.DE`, etc.).
5. Broadened search -- append "stock" or "corp" to query.

Raises `ValueError` if no match is found.

#### `search_companies`

```python
def search_companies(query: str, max_results: int = 10) -> list[SearchResult]
```

Search for companies by name or ticker via yfinance.

Returns a list of `SearchResult` dataclasses:

```python
@dataclass
class SearchResult:
    symbol: str
    name: str
    exchange: str
    quote_type: str
    score: float = 0.0
```

---

## Export (`lynx_finance.export`)

#### `export_report`

```python
def export_report(
    report: AnalysisReport,
    fmt: ExportFormat,
    output_path: Optional[Path] = None,
) -> Path
```

Export an analysis report to the specified format.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `report` | `AnalysisReport` | The completed analysis report. |
| `fmt` | `ExportFormat` | `ExportFormat.TXT`, `ExportFormat.HTML`, or `ExportFormat.PDF`. |
| `output_path` | `Optional[Path]` | Output file path.  Defaults to `data/<TICKER>/report_<timestamp>.<ext>`. |

**Returns:** `Path` to the written file.

```python
from lynx_finance.export import ExportFormat
```

---

## Sector Insights (`lynx_finance.metrics.sector_insights`)

#### `get_sector_insight`

```python
def get_sector_insight(sector: str | None) -> SectorInsight | None
```

Get sector-level analysis guidance.  Returns `None` if the sector is not
recognized.

```python
@dataclass
class SectorInsight:
    sector: str
    overview: str
    critical_metrics: list[str]
    key_risks: list[str]
    what_to_watch: list[str]
    typical_valuation: str
```

Available sectors: `"Financial Services"`, `"Financials"`.

#### `get_industry_insight`

```python
def get_industry_insight(industry: str | None) -> IndustryInsight | None
```

Get industry-level analysis guidance.  Returns `None` if the industry is
not recognized.

```python
@dataclass
class IndustryInsight:
    industry: str
    sector: str
    overview: str
    critical_metrics: list[str]
    key_risks: list[str]
    what_to_watch: list[str]
    typical_valuation: str
```

Available industries: `"Banks - Diversified"`, `"Banks - Regional"`,
`"Capital Markets"`, `"Asset Management"`, `"Credit Services"`,
`"Insurance - Property & Casualty"`, `"Insurance - Life"`,
`"Insurance - Reinsurance"`, `"Insurance - Specialty"`, `"Insurance Brokers"`,
`"Mortgage Finance"`, `"Financial Data & Stock Exchanges"`,
`"Software - Financial"` (fintech).

---

## Usage Examples

### 1. Basic Analysis

```python
from lynx_finance.core.analyzer import run_full_analysis
from lynx_finance.core.conclusion import generate_conclusion

report = run_full_analysis("JPM")

print(f"{report.profile.name} ({report.profile.ticker})")
print(f"Tier: {report.profile.tier.value}")
print(f"Stage: {report.profile.stage.value}")
print(f"FinanceCategory: {report.profile.finance_category.value}")
print(f"Jurisdiction: {report.profile.jurisdiction_tier.value}")

conclusion = generate_conclusion(report)
print(f"Score: {conclusion.overall_score}/100 -- {conclusion.verdict}")
```

### 2. Progressive Analysis with Callback

```python
from lynx_finance.core.analyzer import run_progressive_analysis

def progress_handler(stage: str, report):
    if stage == "profile":
        print(f"Analyzing: {report.profile.name}")
    elif stage == "solvency":
        runway = report.solvency.cash_runway_years
        if runway is not None:
            print(f"Cash runway: {runway:.1f} years")
    elif stage == "complete":
        print("Analysis complete.")

report = run_progressive_analysis("JPM", on_progress=progress_handler)
```

### 3. Accessing Specific Metrics

```python
report = run_full_analysis("JPM")

# Solvency -- critical for explorers
if report.solvency:
    print(f"Cash: ${report.solvency.total_cash:,.0f}")
    print(f"Burn rate: ${report.solvency.cash_burn_rate:,.0f}/yr")
    print(f"Runway: {report.solvency.cash_runway_years:.1f} years")
    print(f"D/E: {report.solvency.debt_to_equity:.2f}")

# Share structure -- dilution risk
if report.share_structure:
    print(f"Shares outstanding: {report.share_structure.shares_outstanding:,.0f}")
    print(f"Insider ownership: {report.share_structure.high_returns_pct:.1%}")

# Market intelligence
if report.market_intelligence:
    mi = report.market_intelligence
    print(f"Insider signal: {mi.insider_buy_signal}")
    print(f"Short % of float: {mi.short_pct_of_float:.1%}")
    print(f"Analyst target upside: {mi.target_upside_pct:.1%}")

# Intrinsic value
if report.intrinsic_value:
    iv = report.intrinsic_value
    print(f"Primary method: {iv.primary_method}")
    print(f"Current price: ${iv.current_price:.2f}")
    if iv.graham_number:
        print(f"Graham number: ${iv.graham_number:.2f}")
```

### 4. Checking Metric Relevance

```python
from lynx_finance.metrics.relevance import get_relevance
from lynx_finance.models import CompanyTier, CompanyStage, Relevance

# For a nano-cap early-stage startup, which metrics matter?
tier = CompanyTier.NANO
stage = CompanyStage.STARTUP

# Cash runway is CRITICAL for explorers
rel = get_relevance("cash_runway_years", tier, "solvency", stage)
assert rel == Relevance.CRITICAL

# P/E is IRRELEVANT for pre-revenue explorers
rel = get_relevance("pe_trailing", tier, "valuation", stage)
assert rel == Relevance.IRRELEVANT

# Shares growth (dilution) is CRITICAL for all early-stage Financials companies
rel = get_relevance("shares_growth_yoy", tier, "growth", stage)
assert rel == Relevance.CRITICAL
```

### 5. Exporting Reports

```python
from pathlib import Path
from lynx_finance.core.analyzer import run_full_analysis
from lynx_finance.export import ExportFormat, export_report

report = run_full_analysis("FUU.V")

# Export as HTML (default path: data/FUU.V/report_<timestamp>.html)
html_path = export_report(report, ExportFormat.HTML)
print(f"HTML report: {html_path}")

# Export as plain text to a custom path
txt_path = export_report(report, ExportFormat.TXT, Path("./fuu_report.txt"))
print(f"Text report: {txt_path}")

# Export as PDF
pdf_path = export_report(report, ExportFormat.PDF)
print(f"PDF report: {pdf_path}")
```
