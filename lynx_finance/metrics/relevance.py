"""Metric relevance by company tier AND Financials lifecycle stage.

Defines which metrics are CRITICAL, IMPORTANT, RELEVANT, CONTEXTUAL (informational)
or IRRELEVANT for each combination of company size tier and Financials lifecycle stage.

For Financials analysis:
  CRITICAL    — Must-check metric. Highlighted; feeds Critical Impact column (blinking red).
  IMPORTANT   — Primary metric for this stage (Impact column → Important, orange).
  RELEVANT    — Useful context (Impact column → Relevant, yellow).
  CONTEXTUAL  — Shown dimmed, informational only (Impact column → Informational, green).
  IRRELEVANT  — Not meaningful; hidden or struck-through (Impact column → Irrelevant, silver).

Stage axis (Financials-specific):
  STARTUP    - De Novo / Early-Stage (challenger banks, neobanks, insurtech)
  GROWTH     - Expansion (regional banks growing footprint)
  SCALE      - Scaling Regional (super-regional banks, growing insurers)
  MATURE     - Mature / Cash-Generative (established franchise)
  PLATFORM   - Systemic / Dominant Franchise (G-SIBs, mega-insurers)

Example: For a MATURE diversified bank, CET1 ratio and NPL ratio are CRITICAL,
P/E and ROTCE are IMPORTANT, and price-to-tangible-book is the valuation anchor.
"""

from __future__ import annotations

from lynx_finance.models import CompanyStage, CompanyTier, Relevance

C = Relevance.CRITICAL
P = Relevance.IMPORTANT
R = Relevance.RELEVANT
X = Relevance.CONTEXTUAL
I = Relevance.IRRELEVANT


def get_relevance(
    metric_key: str,
    tier: CompanyTier,
    category: str = "valuation",
    stage: CompanyStage = CompanyStage.MATURE,
) -> Relevance:
    """Look up relevance for a metric given tier and stage.

    Stage overrides take precedence — the lifecycle stage is the primary axis
    for Financials analysis (lifecycle dimension parallels other sector kits).
    """
    stage_override = _STAGE_OVERRIDES.get(metric_key, {}).get(stage)
    if stage_override is not None:
        return stage_override

    table = {
        "valuation": VALUATION_RELEVANCE,
        "profitability": PROFITABILITY_RELEVANCE,
        "solvency": SOLVENCY_RELEVANCE,
        "growth": GROWTH_RELEVANCE,
        "finance_quality": FINANCE_QUALITY_RELEVANCE,
        "share_structure": SHARE_STRUCTURE_RELEVANCE,
        "efficiency": EFFICIENCY_RELEVANCE,
    }.get(category, {})
    entry = table.get(metric_key, {})
    return entry.get(tier, Relevance.RELEVANT)


# ======================================================================
# Stage-based overrides (take precedence over tier-based lookups)
# ======================================================================

_STAGE_OVERRIDES: dict[str, dict[CompanyStage, Relevance]] = {
    # ── VALUATION ──────────────────────────────────────────────────
    "pe_trailing":           {CompanyStage.STARTUP: I, CompanyStage.GROWTH: R, CompanyStage.SCALE: P, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "pe_forward":            {CompanyStage.STARTUP: I, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "pb_ratio":              {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "ps_ratio":              {CompanyStage.STARTUP: R, CompanyStage.GROWTH: R, CompanyStage.SCALE: R, CompanyStage.MATURE: X, CompanyStage.PLATFORM: X},
    "price_to_tangible_book_value":{CompanyStage.STARTUP: C, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "p_fcf":                 {CompanyStage.STARTUP: I, CompanyStage.GROWTH: X, CompanyStage.SCALE: R, CompanyStage.MATURE: P, CompanyStage.PLATFORM: P},
    "ev_ebitda":             {CompanyStage.STARTUP: I, CompanyStage.GROWTH: X, CompanyStage.SCALE: R, CompanyStage.MATURE: R, CompanyStage.PLATFORM: R},
    "ev_revenue":            {CompanyStage.STARTUP: R, CompanyStage.GROWTH: R, CompanyStage.SCALE: X, CompanyStage.MATURE: X, CompanyStage.PLATFORM: X},
    "peg_ratio":             {CompanyStage.STARTUP: I, CompanyStage.GROWTH: R, CompanyStage.SCALE: P, CompanyStage.MATURE: P, CompanyStage.PLATFORM: R},
    "dividend_yield":        {CompanyStage.STARTUP: I, CompanyStage.GROWTH: X, CompanyStage.SCALE: R, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "earnings_yield":        {CompanyStage.STARTUP: I, CompanyStage.GROWTH: R, CompanyStage.SCALE: P, CompanyStage.MATURE: P, CompanyStage.PLATFORM: P},
    "earnings_yield_vs_10y": {CompanyStage.STARTUP: I, CompanyStage.GROWTH: R, CompanyStage.SCALE: P, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "cash_to_market_cap":    {CompanyStage.STARTUP: P, CompanyStage.GROWTH: R, CompanyStage.SCALE: X, CompanyStage.MATURE: X, CompanyStage.PLATFORM: X},
    "price_to_tangible_book":{CompanyStage.STARTUP: C, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "price_to_ncav":         {CompanyStage.STARTUP: P, CompanyStage.GROWTH: R, CompanyStage.SCALE: X, CompanyStage.MATURE: I, CompanyStage.PLATFORM: I},
    "price_to_aum":          {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: P},
    "price_to_premium":      {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: P, CompanyStage.PLATFORM: P},
    "excess_capital_pct_market_cap": {CompanyStage.STARTUP: R, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: P, CompanyStage.PLATFORM: P},
    # ── PROFITABILITY ───────────────────────────────────────────────
    "roe":                   {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "roa":                   {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "rotce":                 {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "roic":                  {CompanyStage.STARTUP: X, CompanyStage.GROWTH: R, CompanyStage.SCALE: R, CompanyStage.MATURE: R, CompanyStage.PLATFORM: R},
    "gross_margin":          {CompanyStage.STARTUP: I, CompanyStage.GROWTH: I, CompanyStage.SCALE: I, CompanyStage.MATURE: I, CompanyStage.PLATFORM: I},
    "operating_margin":      {CompanyStage.STARTUP: R, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: P, CompanyStage.PLATFORM: P},
    "net_margin":            {CompanyStage.STARTUP: P, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "fcf_margin":            {CompanyStage.STARTUP: X, CompanyStage.GROWTH: X, CompanyStage.SCALE: R, CompanyStage.MATURE: R, CompanyStage.PLATFORM: R},
    "ebitda_margin":         {CompanyStage.STARTUP: I, CompanyStage.GROWTH: X, CompanyStage.SCALE: X, CompanyStage.MATURE: X, CompanyStage.PLATFORM: X},
    "nim":                   {CompanyStage.STARTUP: C, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "yield_on_assets":       {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: P, CompanyStage.PLATFORM: P},
    "cost_of_funds":         {CompanyStage.STARTUP: C, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "net_interest_spread":   {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: P},
    "efficiency_ratio":      {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "fee_income_ratio":      {CompanyStage.STARTUP: R, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "pre_provision_margin":  {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "combined_ratio":        {CompanyStage.STARTUP: C, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "loss_ratio":            {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "expense_ratio":         {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "underwriting_margin":   {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "investment_yield":      {CompanyStage.STARTUP: R, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "effective_fee_rate_bps":{CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    # ── SOLVENCY / CAPITAL ─────────────────────────────────────────
    "cet1_ratio":            {CompanyStage.STARTUP: C, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "tier1_ratio":           {CompanyStage.STARTUP: C, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "total_capital_ratio":   {CompanyStage.STARTUP: P, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: P, CompanyStage.PLATFORM: P},
    "leverage_ratio":        {CompanyStage.STARTUP: C, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: P, CompanyStage.PLATFORM: P},
    "loan_to_deposit_ratio": {CompanyStage.STARTUP: C, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: P},
    "loan_to_asset_ratio":   {CompanyStage.STARTUP: P, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: P, CompanyStage.PLATFORM: R},
    "npl_ratio":             {CompanyStage.STARTUP: C, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "npl_coverage_ratio":    {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "net_charge_off_ratio":  {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "cost_of_risk":          {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "texas_ratio":           {CompanyStage.STARTUP: C, CompanyStage.GROWTH: C, CompanyStage.SCALE: P, CompanyStage.MATURE: P, CompanyStage.PLATFORM: R},
    "liquidity_coverage_ratio":{CompanyStage.STARTUP: P, CompanyStage.GROWTH: P, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "nsfr":                  {CompanyStage.STARTUP: P, CompanyStage.GROWTH: P, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "solvency_ratio":        {CompanyStage.STARTUP: C, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "reserve_to_premium":    {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "catastrophe_exposure":  {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "aum_concentration":     {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: P, CompanyStage.MATURE: R, CompanyStage.PLATFORM: R},
    "debt_to_equity":        {CompanyStage.STARTUP: R, CompanyStage.GROWTH: R, CompanyStage.SCALE: X, CompanyStage.MATURE: X, CompanyStage.PLATFORM: X},
    "debt_to_ebitda":        {CompanyStage.STARTUP: I, CompanyStage.GROWTH: X, CompanyStage.SCALE: X, CompanyStage.MATURE: X, CompanyStage.PLATFORM: X},
    "interest_coverage":     {CompanyStage.STARTUP: I, CompanyStage.GROWTH: X, CompanyStage.SCALE: X, CompanyStage.MATURE: X, CompanyStage.PLATFORM: X},
    "altman_z_score":        {CompanyStage.STARTUP: X, CompanyStage.GROWTH: X, CompanyStage.SCALE: R, CompanyStage.MATURE: R, CompanyStage.PLATFORM: X},
    "current_ratio":         {CompanyStage.STARTUP: X, CompanyStage.GROWTH: X, CompanyStage.SCALE: X, CompanyStage.MATURE: I, CompanyStage.PLATFORM: I},
    "quick_ratio":           {CompanyStage.STARTUP: X, CompanyStage.GROWTH: X, CompanyStage.SCALE: I, CompanyStage.MATURE: I, CompanyStage.PLATFORM: I},
    # ── GROWTH ─────────────────────────────────────────────────────
    "revenue_growth_yoy":    {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: P, CompanyStage.PLATFORM: P},
    "revenue_cagr_3y":       {CompanyStage.STARTUP: R, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: P, CompanyStage.PLATFORM: P},
    "revenue_cagr_5y":       {CompanyStage.STARTUP: X, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: R, CompanyStage.PLATFORM: R},
    "earnings_growth_yoy":   {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "earnings_cagr_3y":      {CompanyStage.STARTUP: R, CompanyStage.GROWTH: P, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "earnings_cagr_5y":      {CompanyStage.STARTUP: X, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: P, CompanyStage.PLATFORM: P},
    "fcf_growth_yoy":        {CompanyStage.STARTUP: X, CompanyStage.GROWTH: R, CompanyStage.SCALE: P, CompanyStage.MATURE: P, CompanyStage.PLATFORM: P},
    "book_value_growth_yoy": {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "tangible_book_growth_yoy":{CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "shares_growth_yoy":     {CompanyStage.STARTUP: P, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "shares_growth_3y_cagr": {CompanyStage.STARTUP: P, CompanyStage.GROWTH: P, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: P},
    "nii_growth_yoy":        {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "loan_growth_yoy":       {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: P, CompanyStage.PLATFORM: P},
    "deposit_growth_yoy":    {CompanyStage.STARTUP: C, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "fee_income_growth_yoy": {CompanyStage.STARTUP: R, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "premium_growth_yoy":    {CompanyStage.STARTUP: C, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "aum_growth_yoy":        {CompanyStage.STARTUP: C, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "net_inflows_pct_aum":   {CompanyStage.STARTUP: C, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: P},
    "revenue_per_employee":  {CompanyStage.STARTUP: R, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: P, CompanyStage.PLATFORM: P},
    # ── FINANCE QUALITY ────────────────────────────────────────────
    "quality_score":         {CompanyStage.STARTUP: C, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: P, CompanyStage.PLATFORM: P},
    "moat_assessment":       {CompanyStage.STARTUP: P, CompanyStage.GROWTH: P, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "capital_adequacy_assessment":{CompanyStage.STARTUP: C, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "asset_quality_assessment":{CompanyStage.STARTUP: C, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "profitability_assessment":{CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "efficiency_assessment": {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "liquidity_assessment":  {CompanyStage.STARTUP: C, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "underwriting_assessment":{CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "franchise_position":    {CompanyStage.STARTUP: R, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "fee_income_diversification":{CompanyStage.STARTUP: R, CompanyStage.GROWTH: P, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "founder_led":           {CompanyStage.STARTUP: P, CompanyStage.GROWTH: P, CompanyStage.SCALE: R, CompanyStage.MATURE: R, CompanyStage.PLATFORM: R},
    "revenue_predictability":{CompanyStage.STARTUP: R, CompanyStage.GROWTH: P, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    # ── SHARE STRUCTURE ────────────────────────────────────────────
    "shares_outstanding":    {CompanyStage.STARTUP: C, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: R, CompanyStage.PLATFORM: R},
    "fully_diluted_shares":  {CompanyStage.STARTUP: P, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: P, CompanyStage.PLATFORM: P},
    "insider_ownership_pct": {CompanyStage.STARTUP: C, CompanyStage.GROWTH: C, CompanyStage.SCALE: P, CompanyStage.MATURE: R, CompanyStage.PLATFORM: R},
    "institutional_ownership_pct":{CompanyStage.STARTUP: R, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: P, CompanyStage.PLATFORM: R},
    "dual_class_structure":  {CompanyStage.STARTUP: P, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: P, CompanyStage.PLATFORM: P},
    "buyback_intensity":     {CompanyStage.STARTUP: X, CompanyStage.GROWTH: R, CompanyStage.SCALE: P, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "share_structure_assessment":{CompanyStage.STARTUP: P, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: R, CompanyStage.PLATFORM: R},
    # ── EFFICIENCY ─────────────────────────────────────────────────
    "cost_to_income_ratio":  {CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "assets_per_employee":   {CompanyStage.STARTUP: R, CompanyStage.GROWTH: P, CompanyStage.SCALE: P, CompanyStage.MATURE: P, CompanyStage.PLATFORM: P},
    "revenue_per_dollar_aum":{CompanyStage.STARTUP: P, CompanyStage.GROWTH: C, CompanyStage.SCALE: C, CompanyStage.MATURE: C, CompanyStage.PLATFORM: C},
    "fcf_conversion":        {CompanyStage.STARTUP: X, CompanyStage.GROWTH: X, CompanyStage.SCALE: R, CompanyStage.MATURE: R, CompanyStage.PLATFORM: R},
}


# ======================================================================
# Tier-based relevance tables (fallback when no stage override exists)
# ======================================================================

VALUATION_RELEVANCE: dict[str, dict[CompanyTier, Relevance]] = {
    "pe_trailing":           {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: P, CompanyTier.MICRO: X, CompanyTier.NANO: I},
    "pb_ratio":              {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: P, CompanyTier.NANO: P},
    "ps_ratio":              {CompanyTier.MEGA: R, CompanyTier.LARGE: R, CompanyTier.MID: R, CompanyTier.SMALL: R, CompanyTier.MICRO: P, CompanyTier.NANO: R},
    "price_to_tangible_book_value":{CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "p_fcf":                 {CompanyTier.MEGA: P, CompanyTier.LARGE: P, CompanyTier.MID: P, CompanyTier.SMALL: R, CompanyTier.MICRO: X, CompanyTier.NANO: X},
    "ev_ebitda":             {CompanyTier.MEGA: R, CompanyTier.LARGE: R, CompanyTier.MID: R, CompanyTier.SMALL: X, CompanyTier.MICRO: X, CompanyTier.NANO: X},
    "cash_to_market_cap":    {CompanyTier.MEGA: I, CompanyTier.LARGE: X, CompanyTier.MID: R, CompanyTier.SMALL: P, CompanyTier.MICRO: P, CompanyTier.NANO: P},
    "price_to_tangible_book":{CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "price_to_aum":          {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: P, CompanyTier.NANO: P},
}

PROFITABILITY_RELEVANCE: dict[str, dict[CompanyTier, Relevance]] = {
    "roe":              {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: P, CompanyTier.NANO: R},
    "rotce":            {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: P, CompanyTier.NANO: R},
    "roa":              {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: P},
    "nim":              {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: P},
    "efficiency_ratio": {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: P, CompanyTier.NANO: P},
    "fee_income_ratio": {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: P, CompanyTier.SMALL: P, CompanyTier.MICRO: R, CompanyTier.NANO: R},
    "combined_ratio":   {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: P},
}

SOLVENCY_RELEVANCE: dict[str, dict[CompanyTier, Relevance]] = {
    "cet1_ratio":            {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "tier1_ratio":           {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "loan_to_deposit_ratio": {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: P, CompanyTier.NANO: P},
    "npl_ratio":             {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "npl_coverage_ratio":    {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: P, CompanyTier.NANO: P},
    "texas_ratio":           {CompanyTier.MEGA: P, CompanyTier.LARGE: P, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "liquidity_coverage_ratio":{CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: P, CompanyTier.SMALL: P, CompanyTier.MICRO: R, CompanyTier.NANO: R},
}

GROWTH_RELEVANCE: dict[str, dict[CompanyTier, Relevance]] = {
    "shares_growth_yoy":      {CompanyTier.MEGA: P, CompanyTier.LARGE: P, CompanyTier.MID: P, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "revenue_growth_yoy":     {CompanyTier.MEGA: P, CompanyTier.LARGE: P, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: P},
    "loan_growth_yoy":        {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: P},
    "deposit_growth_yoy":     {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: P},
    "tangible_book_growth_yoy":{CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: P, CompanyTier.NANO: R},
    "premium_growth_yoy":     {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: P, CompanyTier.NANO: R},
    "aum_growth_yoy":         {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: P, CompanyTier.NANO: R},
}

FINANCE_QUALITY_RELEVANCE: dict[str, dict[CompanyTier, Relevance]] = {
    "quality_score":               {CompanyTier.MEGA: P, CompanyTier.LARGE: P, CompanyTier.MID: P, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "moat_assessment":             {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: P, CompanyTier.NANO: P},
    "capital_adequacy_assessment": {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "asset_quality_assessment":    {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
}

SHARE_STRUCTURE_RELEVANCE: dict[str, dict[CompanyTier, Relevance]] = {
    "shares_outstanding":       {CompanyTier.MEGA: R, CompanyTier.LARGE: R, CompanyTier.MID: P, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "fully_diluted_shares":     {CompanyTier.MEGA: P, CompanyTier.LARGE: P, CompanyTier.MID: P, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "insider_ownership_pct":    {CompanyTier.MEGA: R, CompanyTier.LARGE: R, CompanyTier.MID: P, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "buyback_intensity":        {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: P, CompanyTier.MICRO: R, CompanyTier.NANO: R},
    "dual_class_structure":     {CompanyTier.MEGA: P, CompanyTier.LARGE: P, CompanyTier.MID: P, CompanyTier.SMALL: R, CompanyTier.MICRO: R, CompanyTier.NANO: R},
}

EFFICIENCY_RELEVANCE: dict[str, dict[CompanyTier, Relevance]] = {
    "cost_to_income_ratio":  {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: P, CompanyTier.NANO: P},
    "assets_per_employee":   {CompanyTier.MEGA: P, CompanyTier.LARGE: P, CompanyTier.MID: P, CompanyTier.SMALL: P, CompanyTier.MICRO: R, CompanyTier.NANO: R},
    "fcf_conversion":        {CompanyTier.MEGA: R, CompanyTier.LARGE: R, CompanyTier.MID: R, CompanyTier.SMALL: X, CompanyTier.MICRO: X, CompanyTier.NANO: X},
}


# Backwards-compat alias
TECH_QUALITY_RELEVANCE = FINANCE_QUALITY_RELEVANCE  # pragma: no cover
