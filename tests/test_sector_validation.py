"""Tests for the sector validation gate (Financials)."""

import pytest
from lynx_finance.core.analyzer import _validate_sector, SectorMismatchError
from lynx_finance.models import CompanyProfile


class TestSectorValidation:
    """Sector validation blocks non-Financials companies."""

    def _profile(self, ticker="T", sector=None, industry=None, desc=None):
        return CompanyProfile(ticker=ticker, name=f"{ticker} Corp",
                              sector=sector, industry=industry, description=desc)

    # --- Should ALLOW ---
    def test_financial_services_diversified_bank(self):
        _validate_sector(self._profile(sector="Financial Services", industry="Banks - Diversified"))

    def test_financial_services_regional_bank(self):
        _validate_sector(self._profile(sector="Financial Services", industry="Banks - Regional"))

    def test_financial_services_capital_markets(self):
        _validate_sector(self._profile(sector="Financial Services", industry="Capital Markets"))

    def test_financial_services_insurance_pc(self):
        _validate_sector(self._profile(sector="Financial Services", industry="Insurance - Property & Casualty"))

    def test_financial_services_insurance_life(self):
        _validate_sector(self._profile(sector="Financial Services", industry="Insurance - Life"))

    def test_financial_services_reinsurance(self):
        _validate_sector(self._profile(sector="Financial Services", industry="Insurance - Reinsurance"))

    def test_financial_services_insurance_brokers(self):
        _validate_sector(self._profile(sector="Financial Services", industry="Insurance Brokers"))

    def test_financial_services_asset_management(self):
        _validate_sector(self._profile(sector="Financial Services", industry="Asset Management"))

    def test_financial_services_credit_services(self):
        _validate_sector(self._profile(sector="Financial Services", industry="Credit Services"))

    def test_financial_services_mortgage_finance(self):
        _validate_sector(self._profile(sector="Financial Services", industry="Mortgage Finance"))

    def test_financial_services_financial_data_exchanges(self):
        _validate_sector(self._profile(sector="Financial Services", industry="Financial Data & Stock Exchanges"))

    def test_financials_alias(self):
        """'Financials' is an alternate naming used by some data providers."""
        _validate_sector(self._profile(sector="Financials", industry="Banks"))

    def test_neobank_keyword_in_description(self):
        _validate_sector(self._profile(sector="Other", industry="Other",
                                       desc="Company operates a challenger neobank serving SMBs"))

    def test_payment_processor_keyword_in_description(self):
        _validate_sector(self._profile(sector="Other", industry="Other",
                                       desc="Global payment processor and payment network"))

    def test_investment_bank_keyword(self):
        _validate_sector(self._profile(sector="Other", industry="Other",
                                       desc="Universal bank with broker-dealer and prime brokerage"))

    # --- Should BLOCK ---
    def test_basic_materials_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="Basic Materials", industry="Gold"))

    def test_energy_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="Energy", industry="Uranium"))

    def test_technology_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="Technology", industry="Software - Application"))

    def test_healthcare_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="Healthcare", industry="Drug Manufacturers"))

    def test_consumer_cyclical_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="Consumer Cyclical", industry="Auto Manufacturers"))

    def test_real_estate_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="Real Estate", industry="REIT"))

    def test_communication_services_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="Communication Services",
                                           industry="Internet Content & Information"))

    def test_all_none_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile())

    def test_empty_strings_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="", industry="", desc=""))

    def test_mining_company_blocked(self):
        """A mining company with 'Other' sector should be blocked."""
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(
                sector="Basic Materials", industry="Gold",
                desc="Gold mining exploration and drill program"))

    def test_error_message_content(self):
        with pytest.raises(SectorMismatchError, match="outside the scope"):
            _validate_sector(self._profile(sector="Basic Materials", industry="Gold"))

    def test_error_suggests_another_agent(self):
        """Wrong-sector warning appends a 'use lynx-investor-*' line."""
        with pytest.raises(SectorMismatchError) as exc:
            _validate_sector(self._profile(
                sector="Healthcare", industry="Biotechnology"))
        message = str(exc.value)
        assert "Suggestion" in message
        assert "lynx-investor-healthcare" in message

    def test_error_never_suggests_self(self):
        with pytest.raises(SectorMismatchError) as exc:
            _validate_sector(self._profile(
                sector="Utilities", industry="Utilities—Regulated Electric"))
        message = str(exc.value)
        assert "use 'lynx-investor-financials'" not in message
