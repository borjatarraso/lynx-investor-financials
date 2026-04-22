# Lynx Financials Analysis

> Fundamental analysis specialized for banks, insurers, asset managers, capital-markets infrastructure, consumer finance, and fintech / payments companies.

Part of the **Lince Investor Suite**.

## Overview

Lynx Financials is a comprehensive fundamental analysis tool built specifically for investors in the Financials sector. It evaluates companies across all lifecycle stages — from de-novo / early-stage challenger banks and insurtechs to systemic / globally dominant franchises (G-SIBs) — using Financials-specific metrics, valuation methods, and risk assessments.

### Key Features

- **Stage-Aware Analysis**: Automatically classifies companies as De Novo / Early-Stage, Expansion, Scaling Regional, Mature / Cash-Generative, or Systemic / Dominant Franchise — and adapts all metrics and scoring accordingly
- **Financials-Specific Metrics**: Net Interest Margin (NIM), Yield on Assets, Cost of Funds, Net Interest Spread, Efficiency Ratio (Cost-to-Income), Fee Income Ratio, Combined Ratio (insurers), Loss / Expense Ratios, Investment Yield, ROE / ROTCE, Effective Fee Rate (asset managers), Excess Capital % of Market Cap
- **Capital Adequacy (Basel III)**: CET1 Ratio, Tier 1 Ratio, Total Capital Ratio, Leverage Ratio, Liquidity Coverage Ratio (LCR), Net Stable Funding Ratio (NSFR)
- **Asset Quality**: Non-Performing Loan (NPL) Ratio, NPL Coverage Ratio, Net Charge-Off Ratio, Cost of Risk, **Texas Ratio** (bank distress indicator)
- **Insurance Solvency**: Solvency II / RBC Ratio, Reserve-to-Premium, Catastrophe Exposure
- **Sub-Sector Detection**: Automatic identification of Diversified / G-SIB Banks, Regional Banks, Investment Banks & Capital Markets, P&C Insurance, Life & Health Insurance, Reinsurance, Insurance Brokers, Asset & Wealth Management, Capital Markets Infra, Consumer Finance, Fintech & Payments, Mortgage Finance / Mortgage REITs
- **5-Level Relevance System**: Critical, Important, Relevant, Informational, Irrelevant — plus an **Impact column** with colored labels (blinking red / orange / yellow / green / silver)
- **5-Level Severity System**: `***CRITICAL***` (red), `*WARNING*` (orange), `[WATCH]` (yellow), `[OK]` (green), `[STRONG]` (silver)
- **Market Intelligence**: Insider transactions, institutional holders, analyst consensus, short interest (with bank-run concern flags), price technicals with golden/death cross detection, **XLF + sub-sector ETF** comparison (XLF / KBE / KRE / KIE / IAI / FINX / REM)
- **10-Point Financials Screening Checklist**: CET1 well-capitalized, asset quality healthy, ROE / ROTCE ≥ 12%, efficient cost base, profitable underwriting (insurers), liquidity optimal, dividend paying, no excess dilution, no distress signal (Texas Ratio), Tier 1/2 jurisdiction
- **Jurisdiction Risk Classification**: Tier 1/2/3 based on bank supervision (Basel III), insurance regulation (Solvency II / RBC), and regulatory stability
- **Multiple Interface Modes**: Console CLI, Interactive REPL, Textual TUI, Tkinter GUI
- **Export**: TXT, HTML, and PDF report generation
- **Sector & Industry Insights**: Deep context for Diversified Banks, Regional Banks, Investment Banks, P&C / Life Insurance, Reinsurance, Asset Management, Capital Markets, Credit Services, Mortgage Finance, Insurance Brokers

### Target Companies

Designed for analyzing companies like:
- **Mega-Cap Banks**: JPMorgan (JPM), Bank of America (BAC), Wells Fargo (WFC), Citigroup (C), HSBC (HSBC), UBS, BNP Paribas
- **Regional Banks**: U.S. Bancorp (USB), PNC, Truist (TFC), Fifth Third (FITB), Regions Financial (RF), KeyCorp (KEY)
- **Investment Banks & Capital Markets**: Goldman Sachs (GS), Morgan Stanley (MS), Charles Schwab (SCHW), Interactive Brokers (IBKR), Tradeweb (TW)
- **Asset Managers**: BlackRock (BLK), Blackstone (BX), KKR, Apollo (APO), T. Rowe Price (TROW), Franklin Resources (BEN)
- **Insurers**: Berkshire Hathaway (BRK.B), Travelers (TRV), Chubb (CB), Progressive (PGR), Allstate (ALL), MetLife (MET), Prudential (PRU)
- **Insurance Brokers**: Marsh McLennan (MMC), Aon (AON), Arthur J. Gallagher (AJG), Brown & Brown (BRO), Willis Towers Watson (WTW)
- **Reinsurers**: Munich Re (MUV2), Swiss Re (SREN), RenaissanceRe (RNR), Everest Group (EG)
- **Capital Markets Infra**: CME Group (CME), Intercontinental Exchange (ICE), Nasdaq (NDAQ), MarketAxess (MKTX), Moody's (MCO), S&P Global (SPGI), MSCI
- **Consumer Finance & Cards**: Visa (V), Mastercard (MA), American Express (AXP), Capital One (COF), Discover (DFS)
- **Fintech & Payments**: Block (SQ), PayPal (PYPL), Adyen (ADYEY), Affirm (AFRM)
- **Mortgage REITs**: Annaly Capital (NLY), AGNC Investment (AGNC), New Residential (NRZ)

## Installation

```bash
# Clone the repository
git clone https://github.com/borjatarraso/lynx-investor-financials.git
cd lynx-investor-financials

# Install in editable mode (creates the `lynx-finance` command)
pip install -e .
```

### Dependencies

| Package        | Purpose                              |
|----------------|--------------------------------------|
| yfinance       | Financial data from Yahoo Finance    |
| requests       | HTTP calls (OpenFIGI, EDGAR, etc.)   |
| beautifulsoup4 | HTML parsing for SEC filings         |
| rich           | Terminal tables and formatting       |
| textual        | Full-screen TUI framework            |
| feedparser     | News RSS feed parsing                |
| pandas         | Data analysis                        |
| numpy          | Numerical computing                  |

All dependencies are installed automatically via `pip install -e .`.

## Usage

### Direct Execution
```bash
# Via the runner script
./lynx-investor-financials.py -p JPM

# Via Python
python3 lynx-investor-financials.py -p BLK

# Via pip-installed command
lynx-finance -p MMC
```

### Execution Modes

| Flag | Mode | Description |
|------|------|-------------|
| `-p` | Production | Uses `data/` for persistent cache |
| `-t` | Testing | Uses `data_test/` (isolated, always fresh) |

### Interface Modes

| Flag | Interface | Description |
|------|-----------|-------------|
| (none) | Console | Progressive CLI output |
| `-i` | Interactive | REPL with commands |
| `-tui` | TUI | Textual terminal UI with themes |
| `-x` | GUI | Tkinter graphical interface |

### Examples

```bash
# Analyze a mega-cap diversified bank
lynx-finance -p JPM

# Force fresh data download
lynx-finance -p USB --refresh

# Search by company name
lynx-finance -p "BlackRock"

# Interactive mode
lynx-finance -p -i

# Export HTML report
lynx-finance -p TRV --export html

# Explain a Financials-specific metric
lynx-finance --explain cet1_ratio
lynx-finance --explain combined_ratio
lynx-finance --explain efficiency_ratio

# Skip filings and news for faster analysis
lynx-finance -t MMC --no-reports --no-news
```

## Severity & Impact System

Every metric displays a **Severity tag** and an **Impact column**.

### Severity Levels

| Severity        | Marker          | Color           | Meaning                  |
|-----------------|-----------------|-----------------|--------------------------|
| `***CRITICAL***` | uppercase, red bold | Red             | Urgent red flag          |
| `*WARNING*`     | italic          | Orange          | Significant concern      |
| `[WATCH]`       | bracketed       | Yellow          | Needs monitoring         |
| `[OK]`          | bracketed       | Green           | Normal range             |
| `[STRONG]`      | bracketed       | Silver / Grey   | Excellent signal         |

### Impact Column

| Impact          | Color (text)      |
|-----------------|-------------------|
| Critical        | Blinking red      |
| Important       | Orange            |
| Relevant        | Yellow            |
| Informational   | Green             |
| Irrelevant      | Grey / Silver     |

## Analysis Sections

1. **Company Profile** — Tier, stage, finance category, jurisdiction classification
2. **Sector & Industry Insights** — Financials-specific context and benchmarks
3. **Valuation Metrics** — Traditional + Financials-specific (P/TBV, P/AUM, P/Premium, Excess Capital % MC, Earnings Yield vs 10Y)
4. **Profitability Metrics** — ROE / ROTCE, NIM, Efficiency Ratio, Combined Ratio (insurers), Effective Fee Rate (asset mgrs), Fee Income Ratio, Investment Yield
5. **Solvency & Capital Adequacy** — CET1 / Tier 1 / Total Capital / Leverage Ratios, LCR / NSFR (Basel III), NPL Ratio, Coverage, Net Charge-Offs, Cost of Risk, **Texas Ratio**, Solvency II / RBC (insurers)
6. **Growth & Franchise Expansion** — Revenue + NII + loan + deposit + fee growth. Insurance: premium growth. Asset mgrs: AUM growth & net inflows. **TBV / Share growth** is the durable bank compounding signal
7. **Share Structure** — Outstanding/diluted shares, insider/institutional ownership, **Buyback Intensity**, Dual-Class flag
8. **Financials Quality** — Capital Adequacy, Asset Quality, Profitability, Efficiency, Liquidity, Underwriting (insurers), Franchise Position, Fee Income Diversification
9. **Intrinsic Value** — Excess Return Model (BV + (ROE − CoE)/CoE × BV), P/TBV peer multiple, DDM, Reverse DCF (method selection by stage)
10. **Market Intelligence** — Analysts, short interest, technicals, insider trades, financials benchmark (XLF + sub-sector ETF)
11. **Financial Statements** — 5-year annual summary with NII, fee income, loans, deposits, capital ratios
12. **SEC Filings** — Downloadable regulatory filings (10-K, 10-Q, 8-K, FFIEC Call Reports, Y-9C)
13. **News** — Yahoo Finance + Google News RSS
14. **Assessment Conclusion** — Weighted score, verdict, strengths/risks, 10-point Financials screening checklist
15. **Financials Disclaimers** — Stage- and category-specific risk disclosures

## Relevance System

Each metric is classified by importance for the company's lifecycle stage:

| Level | Prefix | Impact Column    | Meaning |
|-------|--------|------------------|---------|
| **Critical**    | `*`      | Blinking Red    | Must-check for this stage |
| **Important**   | `!`      | Orange          | Primary metric |
| **Relevant**    | normal   | Yellow          | Important context |
| **Informational** (Contextual) | dimmed | Green | Background only |
| **Irrelevant**  | hidden   | Silver          | Not meaningful for this stage |

Example: For a Mature diversified bank, **CET1 Ratio**, **NPL Ratio**, **ROE / ROTCE**, and **P/TBV** are all **Critical**, while traditional P/S is **Contextual**.

## Scoring Methodology

The overall score (0-100) is a weighted average of 5 categories, with weights adapted by both company tier AND Financials lifecycle stage:

| Stage | Valuation | Profitability | Solvency | Growth | Finance Quality |
|-------|-----------|---------------|----------|--------|-----------------|
| De Novo / Early-Stage | 5-10% | 5% | 40-45% | 10-20% | 30-35% |
| Expansion | 5-15% | 10-15% | 25-35% | 20% | 25-35% |
| Scaling Regional | 10-15% | 10-15% | 25-30% | 20% | 25-30% |
| Mature / Cash-Generative | 20% | 20% | 20% | 15-20% | 25% |
| Systemic / Dominant Franchise | 20% | 20% | 20% | 15% | 25% |

Verdicts: Strong Buy (>=75), Buy (>=60), Hold (>=45), Caution (>=30), Avoid (<30).

## Project Structure

```
lynx-investor-financials/
├── lynx-investor-financials.py  # Runner script
├── pyproject.toml                # Build configuration
├── requirements.txt              # Dependencies
├── img/                          # Logo images
├── data/                         # Production cache
├── data_test/                    # Testing cache
├── docs/                         # Documentation
│   └── API.md                    # API reference
├── robot/                        # Robot Framework tests
│   ├── cli_tests.robot
│   ├── api_tests.robot
│   └── export_tests.robot
├── tests/                        # Unit tests
└── lynx_finance/                 # Main package
```

## Testing

```bash
# Unit tests
pytest tests/ -v

# Robot Framework acceptance tests
robot robot/
```

## License

BSD 3-Clause License. See LICENSE in source.

## Author

**Borja Tarraso** — borja.tarraso@member.fsf.org
