"""Tests for export functionality."""

import pytest
import tempfile
from pathlib import Path

from lynx_finance.models import (
    AnalysisReport, CompanyProfile, CompanyTier, CompanyStage,
    ValuationMetrics, SolvencyMetrics, GrowthMetrics,
    FinanceQualityIndicators, ShareStructure, MarketIntelligence,
)
from lynx_finance.export import export_report, ExportFormat


@pytest.fixture
def sample_report():
    p = CompanyProfile(ticker="TEST", name="Test Regional Bank Corp",
                       sector="Financial Services", industry="Banks - Regional",
                       country="United States", market_cap=2_500_000_000)
    p.tier = CompanyTier.MID
    p.stage = CompanyStage.MATURE
    r = AnalysisReport(
        profile=p,
        valuation=ValuationMetrics(pb_ratio=1.3, price_to_tangible_book_value=1.4,
                                   pe_trailing=11.0, dividend_yield=0.04),
        solvency=SolvencyMetrics(cet1_ratio=0.13, npl_ratio=0.012,
                                 npl_coverage_ratio=1.4, loan_to_deposit_ratio=0.82,
                                 texas_ratio=0.06, tangible_book_value=2_000_000_000),
        growth=GrowthMetrics(shares_growth_yoy=-0.02, revenue_growth_yoy=0.06,
                             loan_growth_yoy=0.05, tangible_book_growth_yoy=0.08),
        finance_quality=FinanceQualityIndicators(quality_score=72.0,
                                                 competitive_position="Strong — High-Quality Business"),
        share_structure=ShareStructure(shares_outstanding=200_000_000,
                                       insider_ownership_pct=0.05),
    )
    return r


class TestExportFormat:
    def test_accepts_enum(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            p = export_report(sample_report, ExportFormat.TXT, Path(f.name))
            assert p.exists()
            assert p.stat().st_size > 0

    def test_accepts_string(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            p = export_report(sample_report, "txt", Path(f.name))
            assert p.exists()

    def test_accepts_enum_constructed_from_string(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            p = export_report(sample_report, ExportFormat("html"), Path(f.name))
            assert p.exists()

    def test_invalid_format_raises(self, sample_report):
        with pytest.raises(ValueError):
            export_report(sample_report, "xyz")


class TestTxtExport:
    def test_contains_company_name(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            p = export_report(sample_report, "txt", Path(f.name))
            content = p.read_text()
            assert "Test Regional Bank Corp" in content

    def test_contains_stage(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            content = export_report(sample_report, "txt", Path(f.name)).read_text()
            assert "Mature" in content

    def test_no_truncation(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            content = export_report(sample_report, "txt", Path(f.name)).read_text()
            assert len(content) > 500

    def test_contains_conclusion(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            content = export_report(sample_report, "txt", Path(f.name)).read_text()
            assert "CONCLUSION" in content


class TestHtmlExport:
    def test_white_background(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            content = export_report(sample_report, "html", Path(f.name)).read_text()
            assert "#fff" in content or "#ffffff" in content

    def test_word_wrap(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            content = export_report(sample_report, "html", Path(f.name)).read_text()
            assert "word-wrap" in content or "overflow-wrap" in content

    def test_print_media(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            content = export_report(sample_report, "html", Path(f.name)).read_text()
            assert "@media print" in content

    def test_xss_prevention(self):
        r = AnalysisReport(profile=CompanyProfile(
            ticker="XSS", name='<script>alert("xss")</script>'))
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            content = export_report(r, "html", Path(f.name)).read_text()
            assert "<script>" not in content

    def test_contains_footer(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            content = export_report(sample_report, "html", Path(f.name)).read_text()
            assert "Lince Investor Suite" in content

    def test_valid_html(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            content = export_report(sample_report, "html", Path(f.name)).read_text()
            assert content.startswith("<!DOCTYPE html>")
            assert "</html>" in content


class TestExportWithEmptyReport:
    def test_txt_empty(self):
        r = AnalysisReport(profile=CompanyProfile(ticker="MT", name="MT"))
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            p = export_report(r, "txt", Path(f.name))
            assert p.exists()

    def test_html_empty(self):
        r = AnalysisReport(profile=CompanyProfile(ticker="MT", name="MT"))
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            p = export_report(r, "html", Path(f.name))
            assert p.exists()
