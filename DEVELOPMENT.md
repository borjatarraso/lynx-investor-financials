# Development Guide

## Architecture

The application shares core architecture with other Lynx specialists (Information Technology, Basic Materials, Energy, etc.) but applies Financials-specific domain logic end-to-end.

### Data Flow

```
User Input (ticker/ISIN/name)
    ↓
CLI/Interactive/TUI/GUI → cli.py
    ↓
analyzer.py: run_progressive_analysis()
    ↓
ticker.py: resolve_identifier() → (ticker, isin)
    ↓
storage.py: check cache → return if cached
    ↓
fetcher.py: yfinance data (profile + financials, incl. NII, loans, deposits, CET1, NPL, premium, AUM)
    ↓
models.py: classify_stage / classify_category / classify_jurisdiction
    ↓
calculator.py: calc_valuation / profitability / solvency / growth / efficiency
    ↓
calculator.py: calc_share_structure + calc_finance_quality
    ↓
calculator.py: calc_market_intelligence (insider, analyst, short, technicals, XLF + sector ETF)
    ↓
calculator.py: calc_intrinsic_value (Excess Return Model, P/TBV peer, DCF, Reverse DCF)
    ↓
[parallel] reports.py + news.py
    ↓
conclusion.py: generate_conclusion() → verdict + 10-point Financials screening
    ↓
storage.py: save_analysis_report()
    ↓
display.py / tui/app.py / gui/app.py / export/* → render with severity + impact columns
```

### Key Design Decisions

1. **Stage > Tier**: Financials lifecycle stage (De Novo → Expansion → Scaling Regional → Mature → Systemic Franchise) is the primary analysis axis. The relevance system prioritizes stage overrides.

2. **CET1 ratio as the regulatory anchor**: Wherever a single metric is "The Headline" for banks, CET1 capital adequacy wins. It's the regulatory must-watch metric across every Basel III jurisdiction.

3. **NPL ratio + coverage as asset quality core**: Asset quality is summarized by combining NPL ratio (the size of the bad loans) with the coverage ratio (how much is reserved). Texas Ratio (NPL / (TCE + Reserves)) is the distress trigger.

4. **ROE / ROTCE = franchise quality anchor**: The classification of a financial business' quality starts with returns on equity. Banks: 12-15% normal, 17-20% best-in-class. ROTCE (excluding goodwill) is the sharper signal for acquisition-heavy banks.

5. **Combined ratio for insurers**: Underwriting profitability (losses + expenses / earned premium) is the insurance quality gate. <100% = profitable underwriting; <90% = best-in-class.

6. **Severity + Impact dual-axis display**: Every metric row shows BOTH a severity tag (how bad is this reading?) and an impact column (how much does this metric matter for this stage?). The two are independent.

7. **Progressive Rendering**: The analyzer emits progress callbacks so UIs can render sections as data arrives.

8. **Reverse DCF sanity check**: We compute the growth rate implied by the current price to spot priced-in expectations.

9. **Excess Return Model for banks**: BV + (ROE − CoE) / (CoE − g) × BV is the canonical bank intrinsic-value method, replacing FCF DCF (which is conceptually muddled for banks).

### Adding New Metrics

1. Add field to the appropriate dataclass in `models.py`
2. Calculate in `calculator.py` (in the relevant `calc_*` function)
3. Add relevance entry in `relevance.py` (`_STAGE_OVERRIDES` and tier tables)
4. Add explanation in `explanations.py`
5. Add display row in `display.py`, `tui/app.py`, `gui/app.py`
6. Add export row in `export/html_export.py` and `export/txt_export.py`

### Adding New Finance Categories

1. Add to `FinanceCategory` enum in `models.py`
2. Add keywords to `_CATEGORY_KEYWORDS`
3. Add sub-sector ETFs to `_CATEGORY_ETFS` in `calculator.py`
4. Add industry insight in `sector_insights.py`

### Adding New Stages

1. Add to `CompanyStage` enum
2. Add keywords to `_STAGE_KEYWORDS` in `models.py`
3. Add weights to `_WEIGHTS` in `conclusion.py`
4. Add relevance overrides in `relevance.py`
5. Update method selection in `calc_intrinsic_value`

## Running Tests

```bash
# Python unit tests
pytest tests/ -v --tb=short

# Robot Framework (requires robotframework)
pip install robotframework
robot --outputdir results robot/

# Syntax check all files
python -c "import py_compile, glob; [py_compile.compile(f, doraise=True) for f in glob.glob('lynx_finance/**/*.py', recursive=True)]"
```

## Code Style

- Python 3.10+ with type hints
- Dataclasses for all data models
- Rich for console rendering
- Textual for TUI
- Tkinter for GUI (dark theme)

## Severity & Impact System

The dual-axis display is implemented in `lynx_finance/display.py`:

- `_SEVERITY_FMT` → maps `Severity.*` to `[color]***CRITICAL***[/]`, `[color]*WARNING*[/]`, `[color][WATCH][/]` etc.
- `_IMPACT_DISPLAY` → maps `Relevance.*` to `[blink bold red]Critical[/]`, `[#ff8800]Important[/]`, etc.

Both are shown as separate columns in every metric table, alongside the Value and Assessment columns.

## Backwards Compatibility Notes

To avoid breaking the shared display/export rendering layer (which is largely sector-agnostic), several IT-flavour field names are preserved on the Financials dataclasses as `Optional` fields with `None` defaults:

- `ProfitabilityMetrics`: `rule_of_40`, `rule_of_40_ebitda`, `magic_number`, `sbc_to_revenue`, `sbc_to_fcf`, `gaap_vs_adj_gap`
- `SolvencyMetrics`: `cash_coverage_months`, `capex_to_revenue`, `rpo_coverage`, `goodwill_to_assets`, `deferred_revenue_ratio`
- `GrowthMetrics`: `arr_growth_yoy`, `net_revenue_retention`, `gross_revenue_retention`, `rd_intensity`, `rd_growth_yoy`, `sales_marketing_intensity`, `employee_growth_yoy`
- `EfficiencyMetrics`: `rule_of_x_score`, `cac_payback_months`
- `FinanceQualityIndicators`: `catalyst_density`, `rd_efficiency_assessment`, `unit_economics`, `platform_position`, `financial_position`, `dilution_risk`, `rule_of_40_assessment`, `sbc_risk_assessment`, `roic_history`, `gross_margin_history`
- `ShareStructure`: `sbc_overhang_risk`
- `FinancialStatement`: `research_development`, `selling_general_admin`, `stock_based_compensation`, `deferred_revenue`

These fields remain `None` for Financials companies and the corresponding tables simply render "—" or are skipped. Future work could replace these legacy display sections with Financials-specific tables (NIM trend, loan-mix breakdown, capital-stack composition, premium-by-line for insurers).
