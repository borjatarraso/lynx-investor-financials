"""Unit tests for metric explanations (Financials)."""

import pytest
from lynx_finance.metrics.explanations import (
    get_explanation, list_metrics, get_section_explanation,
    get_conclusion_explanation, SECTION_EXPLANATIONS, CONCLUSION_METHODOLOGY,
)


class TestGetExplanation:
    def test_known_metric(self):
        e = get_explanation("cash_to_market_cap")
        assert e is not None
        assert "Cash" in e.full_name
        assert e.category == "valuation"

    def test_finance_metric_cet1_ratio(self):
        e = get_explanation("cet1_ratio")
        assert e is not None
        assert e.category == "solvency"
        # Basel may appear in any of the explanation fields
        assert "Basel" in (e.full_name + " " + e.description + " " + e.why_used)

    def test_finance_metric_nim(self):
        e = get_explanation("nim")
        assert e is not None
        assert e.category == "profitability"
        assert "interest" in e.description.lower()

    def test_finance_metric_combined_ratio(self):
        e = get_explanation("combined_ratio")
        assert e is not None
        assert e.category == "profitability"

    def test_finance_metric_efficiency_ratio(self):
        e = get_explanation("efficiency_ratio")
        assert e is not None
        assert e.category == "profitability"

    def test_finance_metric_npl_ratio(self):
        e = get_explanation("npl_ratio")
        assert e is not None
        assert e.category == "solvency"

    def test_unknown_metric(self):
        assert get_explanation("nonexistent") is None

    def test_all_metrics_have_required_fields(self):
        for m in list_metrics():
            assert m.key != ""
            assert m.full_name != ""
            assert m.description != ""
            assert m.formula != ""
            assert m.category != ""

    def test_finance_specific_metrics_exist(self):
        keys = [m.key for m in list_metrics()]
        assert "cash_to_market_cap" in keys
        assert "quality_score" in keys
        assert "shares_growth_yoy" in keys
        assert "cet1_ratio" in keys
        assert "nim" in keys
        assert "loan_to_deposit_ratio" in keys
        assert "combined_ratio" in keys
        assert "rotce" in keys
        assert "texas_ratio" in keys
        assert "price_to_tangible_book_value" in keys

    def test_list_by_category(self):
        valuation = list_metrics("valuation")
        assert len(valuation) > 0
        assert all(m.category == "valuation" for m in valuation)


class TestSectionExplanations:
    def test_all_sections_have_title(self):
        for key, sec in SECTION_EXPLANATIONS.items():
            assert "title" in sec
            assert "description" in sec

    def test_finance_quality_section_exists(self):
        sec = get_section_explanation("finance_quality")
        assert sec is not None
        assert "Financials Quality" in sec["title"]

    def test_share_structure_section_exists(self):
        sec = get_section_explanation("share_structure")
        assert sec is not None

    def test_solvency_section_exists(self):
        sec = get_section_explanation("solvency")
        assert sec is not None
        assert "Capital" in sec["title"] or "Solvency" in sec["title"]

    def test_unknown_section(self):
        assert get_section_explanation("nonexistent") is None


class TestConclusionMethodology:
    def test_overall_exists(self):
        ce = get_conclusion_explanation("overall")
        assert ce is not None
        assert "finance quality" in ce["description"].lower() or "financials" in ce["description"].lower()

    def test_solvency_methodology_exists(self):
        ce = get_conclusion_explanation("solvency")
        assert ce is not None
        assert "CET1" in ce["description"]

    def test_unknown_category(self):
        assert get_conclusion_explanation("nonexistent") is None
