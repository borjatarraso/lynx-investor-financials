"""Unit tests for the relevance system (Financials)."""

import pytest
from lynx_finance.models import CompanyStage, CompanyTier, Relevance
from lynx_finance.metrics.relevance import get_relevance


class TestStageOverrides:
    """Stage overrides take precedence over tier-based lookups."""

    def test_cet1_critical_at_all_stages(self):
        """CET1 ratio is the primary capital metric for banks at every stage."""
        for stage in CompanyStage:
            assert get_relevance("cet1_ratio", CompanyTier.LARGE, "solvency", stage) == Relevance.CRITICAL

    def test_npl_ratio_critical_at_all_stages(self):
        """NPL ratio is the primary asset-quality metric for banks."""
        for stage in CompanyStage:
            assert get_relevance("npl_ratio", CompanyTier.MID, "solvency", stage) == Relevance.CRITICAL

    def test_price_to_tangible_book_critical(self):
        """P/TBV is the core bank valuation anchor at every stage."""
        for stage in CompanyStage:
            assert get_relevance("price_to_tangible_book_value", CompanyTier.MEGA, "valuation", stage) == Relevance.CRITICAL

    def test_combined_ratio_critical(self):
        """Combined ratio is the insurance underwriting profitability gate."""
        for stage in CompanyStage:
            assert get_relevance("combined_ratio", CompanyTier.LARGE, "profitability", stage) == Relevance.CRITICAL

    def test_startup_pe_irrelevant(self):
        assert get_relevance("pe_trailing", CompanyTier.MEGA, "valuation", CompanyStage.STARTUP) == Relevance.IRRELEVANT

    def test_startup_traditional_irrelevant_metrics(self):
        for key in ["ev_ebitda", "debt_to_ebitda"]:
            assert get_relevance(key, CompanyTier.MICRO, "solvency", CompanyStage.STARTUP) == Relevance.IRRELEVANT

    def test_mature_dividend_yield_critical(self):
        assert get_relevance("dividend_yield", CompanyTier.LARGE, "valuation", CompanyStage.MATURE) == Relevance.CRITICAL

    def test_mature_pe_trailing_critical(self):
        assert get_relevance("pe_trailing", CompanyTier.LARGE, "valuation", CompanyStage.MATURE) == Relevance.CRITICAL

    def test_efficiency_ratio_critical_for_growth(self):
        assert get_relevance("efficiency_ratio", CompanyTier.MID, "profitability", CompanyStage.GROWTH) == Relevance.CRITICAL

    def test_loan_to_deposit_critical_for_banks(self):
        assert get_relevance("loan_to_deposit_ratio", CompanyTier.MID, "solvency", CompanyStage.MATURE) == Relevance.CRITICAL

    def test_texas_ratio_critical_for_growth(self):
        assert get_relevance("texas_ratio", CompanyTier.MID, "solvency", CompanyStage.GROWTH) == Relevance.CRITICAL

    def test_solvency_ratio_critical_for_insurers(self):
        for stage in CompanyStage:
            assert get_relevance("solvency_ratio", CompanyTier.LARGE, "solvency", stage) == Relevance.CRITICAL

    def test_aum_growth_critical_for_asset_managers(self):
        for stage in CompanyStage:
            assert get_relevance("aum_growth_yoy", CompanyTier.LARGE, "growth", stage) == Relevance.CRITICAL

    def test_tangible_book_growth_critical_for_banks(self):
        assert get_relevance("tangible_book_growth_yoy", CompanyTier.LARGE, "growth", CompanyStage.MATURE) == Relevance.CRITICAL

    def test_buyback_intensity_critical_for_mature(self):
        assert get_relevance("buyback_intensity", CompanyTier.LARGE, "share_structure", CompanyStage.MATURE) == Relevance.CRITICAL

    def test_mature_gross_margin_irrelevant(self):
        """Banks/insurers don't have meaningful gross margin."""
        assert get_relevance("gross_margin", CompanyTier.LARGE, "profitability", CompanyStage.MATURE) == Relevance.IRRELEVANT


class TestTierFallback:
    """When no stage override exists, tier-based lookup is used."""

    def test_unknown_metric_defaults_relevant(self):
        assert get_relevance("some_unknown_metric", CompanyTier.MID, "valuation", CompanyStage.MATURE) == Relevance.RELEVANT

    def test_quality_score_relevance(self):
        # Quality score should always be at least IMPORTANT
        rel = get_relevance("quality_score", CompanyTier.MEGA, "finance_quality", CompanyStage.MATURE)
        assert rel in (Relevance.IMPORTANT, Relevance.CRITICAL)
