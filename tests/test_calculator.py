"""Unit tests for the metrics calculator (Financials)."""

import pytest
from lynx_finance.models import (
    CompanyStage, CompanyTier, FinancialStatement,
    GrowthMetrics, ProfitabilityMetrics, ShareStructure, SolvencyMetrics,
)
from lynx_finance.metrics.calculator import (
    calc_valuation, calc_profitability, calc_solvency, calc_growth,
    calc_efficiency, calc_share_structure, calc_finance_quality,
    calc_intrinsic_value,
)


@pytest.fixture
def sample_info():
    return {
        "currentPrice": 50.0, "marketCap": 50_000_000_000,
        "sharesOutstanding": 1_000_000_000, "totalCash": 10_000_000_000,
        "totalDebt": 5_000_000_000, "priceToBook": 1.5,
        "trailingPE": 11.0, "enterpriseValue": 45_000_000_000,
        "enterpriseToEbitda": 7.5, "returnOnEquity": 0.13,
        "returnOnAssets": 0.012,
        "grossMargins": 0.55, "profitMargins": 0.27,
        "currentRatio": 1.2, "debtToEquity": 50.0,
        "heldPercentInsiders": 0.05,
        "heldPercentInstitutions": 0.65,
        "floatShares": 950_000_000,
        "fullTimeEmployees": 50_000,
    }


@pytest.fixture
def sample_statements():
    """Mid-cap regional bank financials."""
    return [
        FinancialStatement(period="2025", revenue=8_000_000_000, net_income=2_000_000_000,
                           total_assets=180_000_000_000, total_equity=20_000_000_000,
                           total_cash=10_000_000_000, total_liabilities=160_000_000_000,
                           current_assets=80_000_000_000, current_liabilities=20_000_000_000,
                           operating_cash_flow=2_500_000_000, free_cash_flow=2_300_000_000,
                           shares_outstanding=1_000_000_000, eps=2.0,
                           book_value_per_share=20.0, operating_income=2_700_000_000,
                           net_interest_income=5_000_000_000, non_interest_income=3_000_000_000,
                           non_interest_expense=4_400_000_000,
                           interest_income=7_500_000_000, interest_expense=2_500_000_000,
                           total_loans=110_000_000_000, total_deposits=140_000_000_000,
                           earning_assets=160_000_000_000, interest_bearing_liabilities=130_000_000_000,
                           allowance_for_loan_losses=1_500_000_000, non_performing_loans=900_000_000,
                           cet1_capital=18_000_000_000, risk_weighted_assets=130_000_000_000,
                           tangible_common_equity=18_000_000_000,
                           goodwill=1_500_000_000, intangibles=500_000_000),
        FinancialStatement(period="2024", revenue=7_400_000_000, net_income=1_900_000_000,
                           total_assets=170_000_000_000, total_equity=19_000_000_000,
                           total_cash=9_000_000_000, total_loans=104_000_000_000,
                           total_deposits=135_000_000_000, net_interest_income=4_700_000_000,
                           non_interest_income=2_700_000_000, non_interest_expense=4_100_000_000,
                           operating_cash_flow=2_300_000_000, free_cash_flow=2_100_000_000,
                           shares_outstanding=1_020_000_000, allowance_for_loan_losses=1_400_000_000,
                           non_performing_loans=850_000_000, cet1_capital=17_000_000_000,
                           risk_weighted_assets=125_000_000_000, goodwill=1_500_000_000,
                           intangibles=500_000_000),
    ]


class TestCalcValuation:
    def test_basic_valuation(self, sample_info, sample_statements):
        v = calc_valuation(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.MATURE)
        assert v.pe_trailing == 11.0
        assert v.pb_ratio == 1.5
        assert v.market_cap == 50_000_000_000

    def test_price_to_tangible_book_value(self, sample_info, sample_statements):
        v = calc_valuation(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.MATURE)
        # TBV = 20B - 1.5B - 0.5B = 18B; TBV/share = 18; price 50 → P/TBV ≈ 2.78
        assert v.price_to_tangible_book_value is not None
        assert v.price_to_tangible_book_value == pytest.approx(2.78, abs=0.05)

    def test_excess_capital_pct_market_cap(self, sample_info, sample_statements):
        v = calc_valuation(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.MATURE)
        # CET1 = 18B, RWA = 130B, required = 130 × 12% = 15.6B, excess = 2.4B
        # Market cap = 50B, so excess/MC = ~4.8%
        assert v.excess_capital_pct_market_cap is not None
        assert v.excess_capital_pct_market_cap == pytest.approx(0.048, abs=0.005)

    def test_empty_info(self):
        v = calc_valuation({}, [], CompanyTier.NANO, CompanyStage.STARTUP)
        assert v.pe_trailing is None
        assert v.cash_to_market_cap is None


class TestCalcProfitability:
    def test_nim_calculated(self, sample_info, sample_statements):
        p = calc_profitability(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.MATURE)
        assert p.nim is not None
        # NIM = NII / earning_assets = 5B / 160B = 3.125%
        assert p.nim == pytest.approx(0.03125, abs=0.001)

    def test_efficiency_ratio_calculated(self, sample_info, sample_statements):
        p = calc_profitability(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.MATURE)
        assert p.efficiency_ratio is not None
        # 4.4B / 8B = 55%
        assert p.efficiency_ratio == pytest.approx(0.55, abs=0.005)

    def test_fee_income_ratio(self, sample_info, sample_statements):
        p = calc_profitability(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.MATURE)
        assert p.fee_income_ratio is not None
        # 3B / 8B = 37.5%
        assert p.fee_income_ratio == pytest.approx(0.375, abs=0.005)

    def test_rotce_calculated(self, sample_info, sample_statements):
        p = calc_profitability(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.MATURE)
        assert p.rotce is not None
        # NI / TCE = 2B / 18B = ~11.1%
        assert p.rotce == pytest.approx(0.111, abs=0.005)


class TestCalcSolvency:
    def test_cet1_ratio(self, sample_info, sample_statements):
        s = calc_solvency(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.MATURE)
        # CET1 / RWA = 18B / 130B = 13.85%
        assert s.cet1_ratio == pytest.approx(0.1385, abs=0.005)

    def test_loan_to_deposit_ratio(self, sample_info, sample_statements):
        s = calc_solvency(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.MATURE)
        # 110 / 140 = 78.6%
        assert s.loan_to_deposit_ratio == pytest.approx(0.786, abs=0.01)

    def test_npl_ratio_and_coverage(self, sample_info, sample_statements):
        s = calc_solvency(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.MATURE)
        # NPL / loans = 0.9 / 110 = 0.82%
        assert s.npl_ratio == pytest.approx(0.0082, abs=0.001)
        # Coverage = 1.5B / 0.9B = 167%
        assert s.npl_coverage_ratio == pytest.approx(1.667, abs=0.05)

    def test_texas_ratio(self, sample_info, sample_statements):
        s = calc_solvency(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.MATURE)
        assert s.texas_ratio is not None
        # NPL / (TCE + Reserves) = 0.9 / (18 + 1.5) = ~4.6%
        assert s.texas_ratio == pytest.approx(0.046, abs=0.005)


class TestCalcGrowth:
    def test_revenue_growth(self, sample_statements):
        g = calc_growth(sample_statements, CompanyTier.LARGE, CompanyStage.MATURE)
        assert g.revenue_growth_yoy is not None
        # (8 - 7.4) / 7.4 ≈ 8.1%
        assert g.revenue_growth_yoy == pytest.approx(0.081, abs=0.005)

    def test_loan_growth(self, sample_statements):
        g = calc_growth(sample_statements, CompanyTier.LARGE, CompanyStage.MATURE)
        # (110 - 104) / 104 ≈ 5.77%
        assert g.loan_growth_yoy == pytest.approx(0.0577, abs=0.005)

    def test_deposit_growth(self, sample_statements):
        g = calc_growth(sample_statements, CompanyTier.LARGE, CompanyStage.MATURE)
        # (140 - 135) / 135 ≈ 3.7%
        assert g.deposit_growth_yoy == pytest.approx(0.037, abs=0.005)

    def test_share_buybacks_negative_growth(self, sample_statements):
        g = calc_growth(sample_statements, CompanyTier.LARGE, CompanyStage.MATURE)
        # 1000 vs 1020 = -1.96% → buybacks
        assert g.shares_growth_yoy is not None
        assert g.shares_growth_yoy < 0

    def test_empty_statements(self):
        g = calc_growth([], CompanyTier.NANO, CompanyStage.STARTUP)
        assert g.revenue_growth_yoy is None

    def test_single_statement(self):
        g = calc_growth([FinancialStatement(period="2025")], CompanyTier.NANO, CompanyStage.STARTUP)
        assert g.revenue_growth_yoy is None


class TestCalcShareStructure:
    def test_share_assessment(self, sample_info, sample_statements):
        g = GrowthMetrics()
        ss = calc_share_structure(sample_info, sample_statements, g, CompanyTier.LARGE, CompanyStage.MATURE)
        assert ss.shares_outstanding == 1_000_000_000
        assert ss.insider_ownership_pct == 0.05
        assert ss.share_structure_assessment is not None
        assert "Large Float" in ss.share_structure_assessment or "Mega Float" in ss.share_structure_assessment

    def test_buyback_intensity_detected(self, sample_info, sample_statements):
        g = GrowthMetrics(shares_growth_yoy=-0.04)
        ss = calc_share_structure(sample_info, sample_statements, g, CompanyTier.LARGE, CompanyStage.MATURE)
        assert ss.buyback_intensity is not None
        assert "buyback" in ss.buyback_intensity.lower()


class TestCalcFinanceQuality:
    def test_quality_score_range(self, sample_info, sample_statements):
        g = GrowthMetrics(shares_growth_yoy=-0.02, revenue_growth_yoy=0.08,
                          loan_growth_yoy=0.06, tangible_book_growth_yoy=0.10)
        s = SolvencyMetrics(cet1_ratio=0.135, npl_ratio=0.008,
                            npl_coverage_ratio=1.5, loan_to_deposit_ratio=0.78,
                            tangible_book_value=18_000_000_000, texas_ratio=0.05)
        ss = ShareStructure(insider_ownership_pct=0.05,
                            share_structure_assessment="Mega Float (2-10B shares)")
        p = ProfitabilityMetrics(roe=0.13, rotce=0.15, nim=0.031,
                                 efficiency_ratio=0.55, fee_income_ratio=0.37)
        m = calc_finance_quality(p, g, s, ss, sample_statements, sample_info,
                                 CompanyTier.LARGE, CompanyStage.MATURE)
        assert 0 <= m.quality_score <= 100
        assert m.competitive_position is not None
        assert m.capital_adequacy_assessment is not None
        assert m.asset_quality_assessment is not None
        assert m.profitability_assessment is not None

    def test_excellent_bank_scores_high(self, sample_info, sample_statements):
        """A bank with elite metrics should score above 70."""
        g = GrowthMetrics(shares_growth_yoy=-0.04, revenue_growth_yoy=0.10,
                          tangible_book_growth_yoy=0.13)
        s = SolvencyMetrics(cet1_ratio=0.16, npl_ratio=0.005,
                            npl_coverage_ratio=2.0, loan_to_deposit_ratio=0.80,
                            tangible_book_value=20_000_000_000, texas_ratio=0.03)
        ss = ShareStructure(insider_ownership_pct=0.10,
                            share_structure_assessment="Mega Float (2-10B shares)")
        p = ProfitabilityMetrics(roe=0.18, rotce=0.20, nim=0.04,
                                 efficiency_ratio=0.48, fee_income_ratio=0.45)
        m = calc_finance_quality(p, g, s, ss, sample_statements, sample_info,
                                 CompanyTier.MEGA, CompanyStage.PLATFORM)
        assert m.quality_score >= 70

    def test_empty_inputs(self):
        m = calc_finance_quality(ProfitabilityMetrics(), GrowthMetrics(), SolvencyMetrics(),
                                 ShareStructure(), [], {}, CompanyTier.NANO, CompanyStage.STARTUP)
        assert m.quality_score is not None


class TestCalcIntrinsicValue:
    def test_method_selection_mature(self, sample_info, sample_statements):
        iv = calc_intrinsic_value(sample_info, sample_statements, GrowthMetrics(),
                                  SolvencyMetrics(), CompanyTier.LARGE, CompanyStage.MATURE)
        # Mature financials default to Excess Return Model
        assert "Excess Return" in (iv.primary_method or "")

    def test_method_selection_growth(self, sample_info, sample_statements):
        iv = calc_intrinsic_value(sample_info, sample_statements, GrowthMetrics(),
                                  SolvencyMetrics(), CompanyTier.MID, CompanyStage.GROWTH)
        assert "TBV" in (iv.primary_method or "")

    def test_method_selection_startup(self, sample_info, sample_statements):
        iv = calc_intrinsic_value(sample_info, sample_statements, GrowthMetrics(),
                                  SolvencyMetrics(), CompanyTier.NANO, CompanyStage.STARTUP)
        assert "Tangible Book" in (iv.primary_method or "")

    def test_excess_return_value_calculated(self, sample_info, sample_statements):
        iv = calc_intrinsic_value(sample_info, sample_statements, GrowthMetrics(),
                                  SolvencyMetrics(), CompanyTier.LARGE, CompanyStage.MATURE)
        assert iv.excess_return_value is not None
        assert iv.excess_return_value > 0

    def test_p_tbv_implied_price(self, sample_info, sample_statements):
        iv = calc_intrinsic_value(sample_info, sample_statements, GrowthMetrics(),
                                  SolvencyMetrics(), CompanyTier.LARGE, CompanyStage.MATURE)
        assert iv.p_tbv_implied_price is not None
        assert iv.p_tbv_implied_price > 0
