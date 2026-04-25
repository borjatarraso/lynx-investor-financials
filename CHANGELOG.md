# Changelog

## 6.0.0 — 2026-04-26

**Major release synchronising the entire Lince Investor Suite.**

### What's new across the Suite

- **lynx-fund** — brand-new mutual / index fund analysis tool, rejecting
  ETFs and stocks at the resolver level. Surfaces share classes, loads,
  12b-1 fees, manager tenure, persistence, capital-gains tax drag, and
  20-rule passive-investor checklist with tailored tips.
- **lynx-compare-fund** — head-to-head comparison for two mutual / index
  funds. Adds a Boglehead-style Passive-Investor Verdict, plus warnings
  for active-vs-passive, UCITS, soft- / hard-close, and distribution-
  policy mismatches.
- **lynx-theme** — visual theme editor for the entire Suite (GUI + TUI
  only). Edit colours, fonts, alignment, bold / italic / underline /
  blink / marquee for 15 styled areas with live preview. Three built-in
  read-only reference themes (`lynx-mocha`, `lynx-latte`,
  `lynx-high-contrast`). Sets the default theme persisted to
  `$XDG_CONFIG_HOME/lynx-theme/default.json`.
- **i18n** — every Suite CLI now accepts `--language=us|es|it|de|fr|fa`
  and persists the user's choice to `$XDG_CONFIG_HOME/lynx/language.json`.
  GUI apps mount a small bottom-right language toggle (left-click
  cycles, right-click opens a chooser); TUI apps bind `g` to cycle.
  Honours `LYNX_LANG` for ad-hoc shells.
- **Author signature footer** — every txt / html / pdf export now ends
  with the Suite-wide author block: *Borja Tarraso
  &lt;borja.tarraso@member.fsf.org&gt;*. Provided by the new
  `lynx_investor_core.author_footer` module.

### Dashboard

- Two new APP launchables (Lynx Fund, Lynx Compare Fund, Lynx Theme),
  raising the catalogue to **8 apps + 11 sector agents = 19
  launchables**.
- Per-app launch dialect (`run_mode_dialect`, `ui_mode_flags`,
  `accepts_identifier`) so the launcher emits argv each app
  understands; lynx-theme + lynx-portfolio launch correctly from every
  mode.
- `--recommend` now rejects empty queries instead of silently passing.

### Bug fixes

- `__main__.py` of every fund / compare-fund / etf / compare-etf entry
  point now propagates `run_cli`'s return code so non-zero exits are
  visible to shell scripts and CI pipelines.
- Stale-install hygiene: pyproject editable installs now overwrite
  cached site-packages copies cleanly.
- Cosmetic clean-up: remaining "ETF" labels in fund / compare-fund
  GUI / TUI / interactive prompts → "Fund".
- Validation: empty positional ticker, missing second comparison
  ticker, and `--recommend ""` now exit non-zero with a clear message.


## [4.0] - 2026-04-23

Part of **Lince Investor Suite v4.0** coordinated release.

### Added
- URL-safety enforcement for every RSS-sourced news URL and every
  `webbrowser.open(...)` site — powered by
  `lynx_investor_core.urlsafe`.
- Sector-specific ASCII art in easter-egg visuals (replaces the shared
  pickaxe motif that leaked into non-mining sectors).

### Changed
- Aligned every user-visible sector string with the package's real
  sector: titles, subtitles, app class names, splash taglines, news
  keywords, User-Agent headers, themes, export headers, and fortune
  quotes no longer carry template leftovers.
- Depends on `lynx-investor-core>=4.0`.

All notable changes to Lynx Financials Analysis are documented here.

## [3.0] - 2026-04-22

Part of **Lince Investor Suite v3.0** coordinated release.

### Added
- Uniform PageUp / PageDown navigation across every UI mode (GUI, TUI,
  interactive, console). Scrolling never goes above the current output
  in interactive and console mode; Shift+PageUp / Shift+PageDown remain
  reserved for the terminal emulator's own scrollback.
- Sector-mismatch warning now appends a `Suggestion: use
  'lynx-investor-<other>' instead.` line sourced from
  `lynx_investor_core.sector_registry`. The original warning text is
  preserved as-is.

### Changed
- TUI wires `lynx_investor_core.pager.PagingAppMixin` and
  `tui_paging_bindings()` into the main application.
- Graphical mode binds `<Prior>` / `<Next>` / `<Control-Home>` /
  `<Control-End>` via `bind_tk_paging()`.
- Interactive mode pages long output through `console_pager()` /
  `paged_print()`.
- Depends on `lynx-investor-core>=2.0`.

## [2.0] - 2026-04-22

Initial release of **Lynx Financials Analysis**, part of the **Lince Investor Suite v2.0**.

### Added
- **Financials-specific lifecycle stages**: De Novo / Early-Stage / Expansion / Scaling Regional / Mature / Systemic Franchise (replaces IT lifecycle stages)
- **Financials sub-category classification**: Diversified / G-SIB Banks, Regional Banks, Investment Banks & Capital Markets, P&C Insurance, Life & Health Insurance, Reinsurance, Insurance Brokers, Asset & Wealth Management, Capital Markets Infra, Consumer Finance, Fintech & Payments, Mortgage Finance / Mortgage REITs
- **Financials-specific valuation metrics**: P/Tangible Book Value (P/TBV — bank anchor), Price-to-AUM (asset managers), Price-to-Premium (insurers), Earnings Yield vs 10Y Treasury, Excess Capital % of Market Cap (CET1 surplus)
- **Financials-specific profitability metrics**: ROTCE (Return on Tangible Common Equity), Net Interest Margin (NIM), Net Interest Spread, Yield on Assets, Cost of Funds, Efficiency Ratio (Cost-to-Income), Fee Income Ratio, Pre-Provision Margin, Combined Ratio (insurers), Loss / Expense Ratios, Underwriting Margin, Investment Yield, Effective Fee Rate (basis points, asset managers)
- **Capital adequacy & Basel III**: CET1 Ratio, Tier 1 Ratio, Total Capital Ratio, Leverage Ratio, Liquidity Coverage Ratio (LCR), Net Stable Funding Ratio (NSFR)
- **Asset-quality metrics**: NPL Ratio, NPL Coverage, Net Charge-Off Ratio, Cost of Risk, **Texas Ratio** (bank distress indicator)
- **Insurance solvency**: Solvency II / RBC Ratio, Reserve-to-Premium, Catastrophe Exposure
- **Liquidity / funding metrics**: Loan-to-Deposit Ratio (LDR), Loan-to-Asset Ratio
- **Financials-specific growth metrics**: NII Growth, Loan Growth, Deposit Growth, Fee Income Growth, Tangible Book / Share Growth (durable bank compounding signal), Premium Growth (insurers), AUM Growth, Net Inflows / Starting AUM (asset managers)
- **Financials Quality scoring**: Capital Adequacy (20pts), Asset Quality (20pts), Profitability (15pts), Efficiency (10pts), Liquidity (10pts), Underwriting (10pts — insurers), Franchise & Fee Diversification (10pts), Capital Return (5pts)
- **Severity system with 5 levels**: `***CRITICAL***` (red uppercase), `*WARNING*` (orange), `[WATCH]` (yellow), `[OK]` (green), `[STRONG]` (silver)
- **Impact column** on every metric table: Critical (blinking red), Important (orange), Relevant (yellow), Informational (green), Irrelevant (silver)
- **Financials sector validation gate**: refuses to analyze non-Financials companies with prominent red-blinking warning
- **Financials benchmark context**: XLF headline benchmark + sub-sector ETFs (KBE, KRE, KIE, IAK, IAI, FINX, IPAY, REM, VFH) based on detected sub-category
- **Financials investment disclaimers**: rate-cycle sensitivity, credit-cycle exposure, deposit-flight risk, catastrophe risk for insurers, AUM mark-to-market for asset managers
- **Intrinsic value adapted per stage**: Excess Return Model (BV + (ROE − CoE)/CoE × BV) for mature/platform, P/TBV peer multiple for scale/growth, P/Tangible Book + capital backing for startup, Reverse DCF for all
- **Comprehensive unit tests** (200 passing): models, calculator, relevance, conclusion, explanations, export, sector validation, storage, edge cases
- **Financials-specific test fixtures** (Regional Bank Corp, Mature stage, Banks - Regional industry)

### Changed (vs Information Technology predecessor)
- Package renamed `lynx_tech` → `lynx_finance`
- CLI command renamed `lynx-tech` → `lynx-finance`
- `CompanyStage` enum value strings updated (Startup/Hyper-Growth/Scale-Up/Mature/Platform → De Novo / Expansion / Scaling Regional / Mature / Systemic Franchise)
- `TechCategory` enum replaced with `FinanceCategory` (Banks, Insurance, Asset Mgmt, Capital Markets, Fintech, Mortgage)
- `TechQualityIndicators` replaced with `FinanceQualityIndicators` (capital adequacy / asset quality / profitability / efficiency / liquidity / underwriting / franchise / fee diversification axes)
- `tech_quality` field on AnalysisReport renamed to `finance_quality`
- `tech_category` field on CompanyProfile renamed to `finance_category`
- IT-specific metrics replaced with Financials-specific metrics (NIM/CET1/NPL/Combined Ratio replace Rule-of-40/Magic Number/SBC/R&D Intensity)
- Sector validation gate now allows Financial Services / Financials and blocks Technology, Basic Materials, Energy, Healthcare, etc.
- Sub-sector ETFs updated to financials peers (XLF/KBE/KRE/KIE/IAI/FINX/REM)

### Notes
- IT-flavour field names (`rule_of_40`, `sbc_to_revenue`, `magic_number`, etc.) are preserved as `Optional[None]` defaults on the dataclasses so legacy display/export code continues to work — they simply remain unset for Financials companies.
- Backwards-compat aliases retained for `TechCategory` (= `FinanceCategory`) and `calc_tech_quality` (= `calc_finance_quality`).
