"""Unit tests for data models and classification functions (Financials)."""

import pytest
from lynx_finance.models import (
    CompanyProfile, CompanyStage, CompanyTier, FinanceCategory,
    JurisdictionTier, Relevance, Severity, AnalysisReport,
    ValuationMetrics, SolvencyMetrics, GrowthMetrics,
    FinanceQualityIndicators, ShareStructure, MarketIntelligence,
    FinancialStatement, AnalysisConclusion,
    classify_tier, classify_stage, classify_category, classify_jurisdiction,
    format_severity, format_impact, SEVERITY_STYLE, IMPACT_STYLE,
)


class TestClassifyTier:
    def test_mega_cap(self):
        assert classify_tier(300_000_000_000) == CompanyTier.MEGA

    def test_large_cap(self):
        assert classify_tier(50_000_000_000) == CompanyTier.LARGE

    def test_mid_cap(self):
        assert classify_tier(5_000_000_000) == CompanyTier.MID

    def test_small_cap(self):
        assert classify_tier(1_000_000_000) == CompanyTier.SMALL

    def test_micro_cap(self):
        assert classify_tier(100_000_000) == CompanyTier.MICRO

    def test_nano_cap(self):
        assert classify_tier(10_000_000) == CompanyTier.NANO

    def test_none_returns_nano(self):
        assert classify_tier(None) == CompanyTier.NANO

    def test_zero_returns_nano(self):
        assert classify_tier(0) == CompanyTier.NANO

    def test_negative_returns_nano(self):
        assert classify_tier(-100) == CompanyTier.NANO


class TestClassifyStage:
    def test_platform_from_description(self):
        assert classify_stage("globally systemically important diversified global bank",
                              50_000_000_000,
                              {"marketCap": 300_000_000_000}) == CompanyStage.PLATFORM

    def test_mature_by_profit_margin(self):
        assert classify_stage("generic banking franchise", 10_000_000_000,
                              {"marketCap": 50_000_000_000, "profitMargins": 0.25}) == CompanyStage.MATURE

    def test_growth_hyper(self):
        assert classify_stage("rapid loan growth regional bank", 100_000_000,
                              {"revenueGrowth": 0.40}) == CompanyStage.GROWTH

    def test_scale_by_revenue(self):
        assert classify_stage("super-regional bank consolidator", 2_000_000_000,
                              {"revenueGrowth": 0.10}) == CompanyStage.SCALE

    def test_startup_low_revenue(self):
        assert classify_stage("de novo neobank", 0) == CompanyStage.STARTUP

    def test_none_description(self):
        assert classify_stage(None, None) == CompanyStage.STARTUP

    def test_empty_description(self):
        assert classify_stage("", 0) == CompanyStage.STARTUP


class TestClassifyCategory:
    def test_diversified_bank(self):
        assert classify_category("diversified universal bank money center bank",
                                 "Banks - Diversified") == FinanceCategory.BANK_DIVERSIFIED

    def test_regional_bank(self):
        assert classify_category("regional bank community bank",
                                 "Banks - Regional") == FinanceCategory.BANK_REGIONAL

    def test_investment_bank(self):
        assert classify_category("investment bank prime brokerage merger advisory",
                                 None) == FinanceCategory.INVESTMENT_BANK

    def test_pc_insurance(self):
        assert classify_category("property and casualty insurer auto insurance",
                                 "Insurance - Property & Casualty") == FinanceCategory.INSURANCE_PC

    def test_life_insurance(self):
        assert classify_category("life insurance and annuities",
                                 "Insurance - Life") == FinanceCategory.INSURANCE_LIFE

    def test_reinsurance(self):
        assert classify_category("catastrophe reinsurance reinsurer",
                                 "Insurance - Reinsurance") == FinanceCategory.REINSURANCE

    def test_asset_manager(self):
        assert classify_category("asset management wealth management investment manager",
                                 None) == FinanceCategory.ASSET_MANAGER

    def test_capital_markets(self):
        assert classify_category("stock exchange operator clearing house",
                                 None) == FinanceCategory.CAPITAL_MARKETS

    def test_consumer_finance(self):
        assert classify_category("credit card issuer consumer finance",
                                 None) == FinanceCategory.CONSUMER_FINANCE

    def test_fintech(self):
        assert classify_category("fintech payments processor neobank",
                                 None) == FinanceCategory.FINTECH

    def test_mortgage(self):
        assert classify_category("mortgage reit agency mbs",
                                 "Mortgage Finance") == FinanceCategory.MORTGAGE_FINANCE

    def test_other_when_no_match(self):
        assert classify_category("generic company", None) == FinanceCategory.OTHER

    def test_none_inputs(self):
        assert classify_category(None, None) == FinanceCategory.OTHER

    def test_industry_only_fallback_bank(self):
        """When no description keywords match, industry-only mapping should pick up 'Bank'."""
        assert classify_category(None, "Banks - Regional") == FinanceCategory.BANK_REGIONAL


class TestClassifyJurisdiction:
    def test_us_tier1(self):
        assert classify_jurisdiction("United States") == JurisdictionTier.TIER_1

    def test_ireland_tier1(self):
        assert classify_jurisdiction("Ireland") == JurisdictionTier.TIER_1

    def test_japan_tier1(self):
        assert classify_jurisdiction("Japan") == JurisdictionTier.TIER_1

    def test_singapore_tier1(self):
        assert classify_jurisdiction("Singapore") == JurisdictionTier.TIER_1

    def test_india_tier2(self):
        assert classify_jurisdiction("India") == JurisdictionTier.TIER_2

    def test_spain_tier2(self):
        assert classify_jurisdiction("Spain") == JurisdictionTier.TIER_2

    def test_unknown_country_tier3(self):
        assert classify_jurisdiction("SomeCountry") == JurisdictionTier.TIER_3

    def test_none_unknown(self):
        assert classify_jurisdiction(None) == JurisdictionTier.UNKNOWN


class TestDataModels:
    def test_analysis_report_defaults(self):
        r = AnalysisReport(profile=CompanyProfile(ticker="TEST", name="Test"))
        assert r.valuation is None
        assert r.market_intelligence is None
        assert r.financials == []
        assert r.fetched_at != ""

    def test_company_profile_defaults(self):
        p = CompanyProfile(ticker="X", name="X Corp")
        assert p.tier == CompanyTier.NANO
        assert p.stage == CompanyStage.STARTUP
        assert p.finance_category == FinanceCategory.OTHER
        assert p.jurisdiction_tier == JurisdictionTier.UNKNOWN

    def test_solvency_metrics_defaults(self):
        s = SolvencyMetrics()
        assert s.cet1_ratio is None
        assert s.npl_ratio is None
        assert s.loan_to_deposit_ratio is None
        assert s.texas_ratio is None
        assert s.solvency_ratio is None

    def test_market_intelligence_defaults(self):
        mi = MarketIntelligence()
        assert mi.insider_transactions == []
        assert mi.risk_warnings == []
        assert mi.disclaimers == []

    def test_finance_quality_defaults(self):
        fq = FinanceQualityIndicators()
        assert fq.quality_score is None
        assert fq.moat_assessment is None
        assert fq.capital_adequacy_assessment is None
        assert fq.asset_quality_assessment is None

    def test_financial_statement_finance_fields(self):
        s = FinancialStatement(period="2024")
        assert s.net_interest_income is None
        assert s.total_loans is None
        assert s.total_deposits is None
        assert s.cet1_capital is None
        assert s.earned_premium is None
        assert s.aum is None


class TestSeverityFormatting:
    def test_critical_severity_format(self):
        s = format_severity(Severity.CRITICAL)
        assert "***CRITICAL***" in s
        assert "bold red" in s

    def test_warning_severity_format(self):
        s = format_severity(Severity.WARNING)
        assert "*WARNING*" in s
        assert "#ff8800" in s

    def test_watch_severity_format(self):
        s = format_severity(Severity.WATCH)
        assert "[WATCH]" in s
        assert "yellow" in s

    def test_ok_severity_format(self):
        s = format_severity(Severity.OK)
        assert "[OK]" in s
        assert "green" in s

    def test_strong_severity_format(self):
        s = format_severity(Severity.STRONG)
        assert "[STRONG]" in s
        assert "grey" in s or "silver" in s.lower()


class TestImpactFormatting:
    def test_critical_impact_blinks(self):
        s = format_impact(Relevance.CRITICAL)
        assert "Critical" in s
        assert "blink" in s

    def test_important_impact_orange(self):
        s = format_impact(Relevance.IMPORTANT)
        assert "Important" in s
        assert "#ff8800" in s

    def test_relevant_impact_yellow(self):
        s = format_impact(Relevance.RELEVANT)
        assert "Relevant" in s
        assert "yellow" in s

    def test_contextual_impact_green(self):
        s = format_impact(Relevance.CONTEXTUAL)
        assert "Informational" in s
        assert "green" in s

    def test_irrelevant_impact_silver(self):
        s = format_impact(Relevance.IRRELEVANT)
        assert "Irrelevant" in s
        assert "grey" in s or "silver" in s.lower()
