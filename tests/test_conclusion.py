"""Unit tests for the conclusion engine (Financials)."""

import pytest
from lynx_finance.models import (
    AnalysisReport, CompanyProfile, CompanyStage, CompanyTier,
    ValuationMetrics, SolvencyMetrics, GrowthMetrics, ProfitabilityMetrics,
    FinanceQualityIndicators, ShareStructure,
)
from lynx_finance.core.conclusion import generate_conclusion


@pytest.fixture
def minimal_report():
    return AnalysisReport(profile=CompanyProfile(ticker="TEST", name="Test Corp"))


@pytest.fixture
def regional_bank_report():
    p = CompanyProfile(ticker="RBNK", name="Regional Bank Corp",
                       market_cap=5_000_000_000)
    p.tier = CompanyTier.MID
    p.stage = CompanyStage.MATURE
    r = AnalysisReport(profile=p)
    r.valuation = ValuationMetrics(pe_trailing=10.5, pb_ratio=1.3,
                                   price_to_tangible_book_value=1.4,
                                   dividend_yield=0.04)
    r.profitability = ProfitabilityMetrics(roe=0.13, rotce=0.14, nim=0.032,
                                           efficiency_ratio=0.58, fee_income_ratio=0.30)
    r.solvency = SolvencyMetrics(cet1_ratio=0.13, npl_ratio=0.012,
                                 npl_coverage_ratio=1.4, loan_to_deposit_ratio=0.82,
                                 texas_ratio=0.06, tangible_book_value=4_000_000_000)
    r.growth = GrowthMetrics(revenue_growth_yoy=0.06, loan_growth_yoy=0.05,
                             tangible_book_growth_yoy=0.08, shares_growth_yoy=-0.02)
    r.finance_quality = FinanceQualityIndicators(quality_score=70.0,
                                                 competitive_position="Strong — High-Quality Business")
    r.share_structure = ShareStructure(fully_diluted_shares=200_000_000,
                                       insider_ownership_pct=0.04)
    return r


class TestGenerateConclusion:
    def test_minimal_report_produces_verdict(self, minimal_report):
        c = generate_conclusion(minimal_report)
        assert c.verdict in ["Strong Buy", "Buy", "Hold", "Caution", "Avoid"]
        assert 0 <= c.overall_score <= 100
        assert c.summary != ""

    def test_verdict_thresholds(self, minimal_report):
        c = generate_conclusion(minimal_report)
        if c.overall_score >= 75:
            assert c.verdict == "Strong Buy"
        elif c.overall_score >= 60:
            assert c.verdict == "Buy"
        elif c.overall_score >= 45:
            assert c.verdict == "Hold"
        elif c.overall_score >= 30:
            assert c.verdict == "Caution"
        else:
            assert c.verdict == "Avoid"

    def test_mature_has_stage_note(self, regional_bank_report):
        c = generate_conclusion(regional_bank_report)
        assert c.stage_note != ""
        assert "Mature" in c.stage_note or "DDM" in c.stage_note or "Excess Return" in c.stage_note

    def test_category_scores_present(self, regional_bank_report):
        c = generate_conclusion(regional_bank_report)
        assert "valuation" in c.category_scores
        assert "profitability" in c.category_scores
        assert "solvency" in c.category_scores
        assert "growth" in c.category_scores
        assert "finance_quality" in c.category_scores

    def test_screening_checklist_present(self, regional_bank_report):
        c = generate_conclusion(regional_bank_report)
        assert isinstance(c.screening_checklist, dict)
        assert "cet1_well_capitalized" in c.screening_checklist
        assert "asset_quality_healthy" in c.screening_checklist
        assert "high_returns" in c.screening_checklist
        assert "efficient_cost_base" in c.screening_checklist
        assert "no_distress_signal" in c.screening_checklist

    def test_quality_bank_passes_screening(self, regional_bank_report):
        c = generate_conclusion(regional_bank_report)
        assert c.screening_checklist.get("cet1_well_capitalized") is True
        assert c.screening_checklist.get("asset_quality_healthy") is True
        assert c.screening_checklist.get("high_returns") is True

    def test_quality_bank_scores_well(self, regional_bank_report):
        c = generate_conclusion(regional_bank_report)
        assert c.overall_score >= 60  # At least Buy

    def test_strengths_detected(self, regional_bank_report):
        c = generate_conclusion(regional_bank_report)
        assert len(c.strengths) >= 1

    def test_distressed_bank_flagged(self):
        """A bank with sub-buffer CET1 and high NPLs should score poorly."""
        p = CompanyProfile(ticker="STRESS", name="Stressed Bank Corp",
                           market_cap=500_000_000)
        p.tier = CompanyTier.SMALL
        p.stage = CompanyStage.SCALE
        r = AnalysisReport(profile=p)
        r.valuation = ValuationMetrics(price_to_tangible_book_value=0.6, pb_ratio=0.6)
        r.profitability = ProfitabilityMetrics(roe=0.03, nim=0.018, efficiency_ratio=0.78)
        r.solvency = SolvencyMetrics(cet1_ratio=0.085, npl_ratio=0.06,
                                     npl_coverage_ratio=0.5, loan_to_deposit_ratio=1.10,
                                     texas_ratio=0.65, tangible_book_value=400_000_000)
        r.growth = GrowthMetrics(revenue_growth_yoy=-0.05)
        r.finance_quality = FinanceQualityIndicators(quality_score=25.0,
                                                     competitive_position="Poor — Elevated Risk")
        c = generate_conclusion(r)
        assert c.verdict in ("Caution", "Avoid", "Hold")
        assert any("Texas" in risk or "NPL" in risk or "CET1" in risk for risk in c.risks)
