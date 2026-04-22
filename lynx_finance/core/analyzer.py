"""Main analysis orchestrator for Financials companies."""

from __future__ import annotations

import dataclasses
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Optional

from rich.console import Console

from lynx_finance.core.fetcher import fetch_company_profile, fetch_financial_statements, fetch_info
from lynx_finance.core.news import fetch_all_news
from lynx_finance.core.reports import download_top_filings, fetch_sec_filings
from lynx_finance.core.storage import get_cache_age_hours, has_cache, load_cached_report, save_analysis_report
from lynx_finance.core.ticker import resolve_identifier
from lynx_finance.metrics.calculator import (
    calc_efficiency, calc_growth, calc_intrinsic_value, calc_market_intelligence,
    calc_finance_quality, calc_profitability, calc_share_structure, calc_solvency,
    calc_valuation,
)
from lynx_finance.models import (
    AnalysisReport, CompanyProfile, CompanyStage, CompanyTier,
    EfficiencyMetrics, Filing, FinancialStatement, GrowthMetrics,
    InsiderTransaction, IntrinsicValue, MarketIntelligence,
    FinanceQualityIndicators, NewsArticle,
    ProfitabilityMetrics, ShareStructure, SolvencyMetrics, ValuationMetrics,
    classify_category, classify_jurisdiction, classify_stage, classify_tier,
)

console = Console(stderr=True)

# Sectors and industries that this tool is designed for
_ALLOWED_SECTORS = {"financial services", "financials", "financial"}
_ALLOWED_INDUSTRIES = {
    "banks", "banks - diversified", "banks - regional", "banks—regional",
    "savings & cooperative banks", "savings and cooperative banks",
    "capital markets", "asset management", "asset management - global",
    "credit services", "consumer finance", "mortgage finance",
    "insurance", "insurance - diversified", "insurance brokers",
    "insurance - life", "insurance - property & casualty",
    "insurance - reinsurance", "insurance - specialty",
    "financial conglomerates", "financial data & stock exchanges",
    "shell companies", "investment banking & brokerage",
    "software - financial",
}


class SectorMismatchError(Exception):
    """Raised when a company does not belong to the Financials sector."""
    pass


def _validate_sector(profile: CompanyProfile) -> None:
    """Check if the company belongs to the Financials sector or a financials-adjacent industry.

    Raises SectorMismatchError if the company is outside scope.
    """
    sector = (profile.sector or "").lower().strip()
    industry = (profile.industry or "").lower().strip()

    if sector in _ALLOWED_SECTORS:
        return

    if industry:
        for allowed in _ALLOWED_INDUSTRIES:
            if allowed in industry or industry in allowed:
                return

    import re
    desc = (profile.description or "").lower()
    # Financials-specific terms (word-boundary matched) used to detect financials when sector is mislabeled
    finance_specific = [
        r"\bcommercial bank\b", r"\bdiversified bank\b", r"\binvestment bank\b",
        r"\bregional bank\b", r"\bcommunity bank\b", r"\buniversal bank\b",
        r"\bsavings bank\b", r"\bdeposit-taking institution\b",
        r"\bproperty and casualty insurer\b", r"\bp&c insurer\b",
        r"\blife insurer\b", r"\blife insurance company\b", r"\breinsurer\b",
        r"\bannuit(y|ies) provider\b", r"\binsurance broker(age)?\b",
        r"\basset manager\b", r"\bwealth manager\b", r"\bfund manager\b",
        r"\bbroker.dealer\b", r"\bmarket maker\b", r"\bclearing house\b",
        r"\bstock exchange operator\b", r"\bcredit card issuer\b",
        r"\bconsumer finance\b", r"\bmortgage originator\b",
        r"\bmortgage reit\b", r"\bpayment processor\b", r"\bpayment network\b",
        r"\bfintech\b", r"\bneobank\b", r"\bchallenger bank\b",
        r"\binsurtech\b", r"\bcapital markets infrastructure\b",
    ]
    if any(re.search(pattern, desc) for pattern in finance_specific):
        return

    from lynx_investor_core.sector_registry import format_agent_suggestion
    message = (
        f"{profile.name} ({profile.ticker}) is in the "
        f"'{profile.sector or 'Unknown'}' / '{profile.industry or 'Unknown'}' "
        f"sector, which is outside the scope of this tool.\n\n"
        f"Lynx Financials Analysis is specialized exclusively for:\n"
        f"  - Financial Services / Financials\n"
        f"  - Banks (Diversified / Regional / Investment / Community)\n"
        f"  - Insurance (P&C, Life, Reinsurance, Brokers, Specialty)\n"
        f"  - Asset & Wealth Management, Capital Markets Infrastructure\n"
        f"  - Consumer Finance, Mortgage Finance, Mortgage REITs\n"
        f"  - Fintech, Payments & Neobanks\n\n"
        f"For other sectors, use the matching Lynx specialist "
        f"(Information Technology, Basic Materials, Energy, Healthcare, etc.)."
    )
    message += format_agent_suggestion(
        profile, current_agent="lynx-investor-financials",
    )
    raise SectorMismatchError(message)


ProgressCallback = Callable[[str, AnalysisReport], None]


def run_full_analysis(identifier: str, download_reports: bool = True, download_news: bool = True,
                      max_filings: int = 10, verbose: bool = False, refresh: bool = False) -> AnalysisReport:
    return run_progressive_analysis(identifier=identifier, download_reports=download_reports,
        download_news=download_news, max_filings=max_filings, verbose=verbose, refresh=refresh, on_progress=None)


def run_progressive_analysis(
    identifier: str, download_reports: bool = True, download_news: bool = True,
    max_filings: int = 10, verbose: bool = False, refresh: bool = False,
    on_progress: Optional[ProgressCallback] = None,
) -> AnalysisReport:
    def _notify(stage: str, report: AnalysisReport) -> None:
        if on_progress is not None:
            on_progress(stage, report)

    console.print(f"[bold cyan]Resolving identifier:[/] {identifier}")
    ticker, isin = resolve_identifier(identifier)
    console.print(f"[green]Ticker:[/] {ticker}" + (f"  [dim]ISIN: {isin}[/dim]" if isin else ""))

    if not refresh and has_cache(ticker):
        age = get_cache_age_hours(ticker)
        age_str = f"{age:.1f}h ago" if age is not None else "unknown age"
        console.print(f"[bold green]Using cached data[/] [dim](fetched {age_str})[/]")
        cached = load_cached_report(ticker)
        if cached:
            try:
                report = _dict_to_report(cached)
            except Exception as exc:
                console.print(f"[yellow]Cached data is corrupt ({exc}), re-fetching...[/]")
            else:
                if isin and report.profile.isin is None:
                    report.profile.isin = isin
                console.print(
                    f"[green]{report.profile.name}[/] -- "
                    f"{report.profile.tier.value}  {report.profile.stage.value}"
                )
                _notify("complete", report)
                return report

    if refresh:
        console.print("[yellow]Refreshing data from network...[/]")

    console.print("[cyan]Fetching company profile...[/]")
    info = fetch_info(ticker)
    profile = fetch_company_profile(ticker, info=info)
    profile.isin = isin

    if not profile.isin:
        try:
            import yfinance as yf
            fetched_isin = yf.Ticker(ticker).isin
            if fetched_isin and fetched_isin != "-":
                profile.isin = fetched_isin
        except Exception:
            pass

    tier = classify_tier(profile.market_cap)
    profile.tier = tier
    stage = classify_stage(profile.description, info.get("totalRevenue"), info)
    profile.stage = stage
    profile.finance_category = classify_category(profile.description, profile.industry)
    profile.jurisdiction_tier = classify_jurisdiction(profile.country, profile.description)
    if profile.country:
        profile.jurisdiction_country = profile.country

    console.print(
        f"[green]{profile.name}[/] -- {profile.sector or 'N/A'} / {profile.industry or 'N/A'}"
        f"  [bold][{_tier_color(tier)}]{tier.value}[/]"
        f"  [{_stage_color(stage)}]{stage.value}[/]"
    )

    # Validate sector — refuse to analyze non-Financials companies
    _validate_sector(profile)

    if profile.finance_category.value != "Other Financials":
        console.print(f"[cyan]Finance Category:[/] {profile.finance_category.value}")
    console.print(f"[cyan]Jurisdiction Risk:[/] {profile.jurisdiction_tier.value}")

    report = AnalysisReport(profile=profile)
    _notify("profile", report)

    console.print("[cyan]Fetching financial statements...[/]")
    statements = fetch_financial_statements(ticker)
    console.print(f"[green]Retrieved {len(statements)} annual periods[/]")
    report.financials = statements
    _notify("financials", report)

    console.print("[cyan]Calculating metrics...[/]")
    report.valuation = calc_valuation(info, statements, tier, stage)
    _notify("valuation", report)
    report.profitability = calc_profitability(info, statements, tier, stage)
    _notify("profitability", report)
    report.solvency = calc_solvency(info, statements, tier, stage)
    _notify("solvency", report)
    report.growth = calc_growth(statements, tier, stage, info)
    _notify("growth", report)
    report.efficiency = calc_efficiency(info, statements, tier)
    report.share_structure = calc_share_structure(info, statements, report.growth, tier, stage)
    _notify("share_structure", report)
    report.finance_quality = calc_finance_quality(
        report.profitability, report.growth, report.solvency,
        report.share_structure, statements, info, tier, stage,
    )
    _notify("finance_quality", report)
    report.intrinsic_value = calc_intrinsic_value(info, statements, report.growth, report.solvency, tier, stage)
    _notify("intrinsic_value", report)

    console.print("[cyan]Gathering market intelligence...[/]")
    try:
        import yfinance as yf
        ticker_obj = yf.Ticker(ticker)
        report.market_intelligence = calc_market_intelligence(
            info, ticker_obj, report.solvency, report.share_structure,
            report.growth, tier, stage,
        )
        _notify("market_intelligence", report)
    except Exception as exc:
        console.print(f"[yellow]Market intelligence failed: {exc}[/]")

    _ticker, _max = ticker, max_filings
    with ThreadPoolExecutor(max_workers=2) as pool:
        filings_future = pool.submit(lambda: fetch_sec_filings(_ticker)) if download_reports else None
        news_future = pool.submit(lambda: fetch_all_news(_ticker, profile.name)) if download_news else None

        if download_reports:
            console.print("[cyan]Fetching SEC filings...[/]")
        if download_news:
            console.print("[cyan]Fetching news...[/]")

        if filings_future is not None:
            try:
                fl = filings_future.result()
                console.print(f"[green]Found {len(fl)} filings[/]")
                if fl:
                    console.print(f"[cyan]Downloading top {_max} filings...[/]")
                    download_top_filings(_ticker, fl, max_count=_max)
                report.filings = fl
                _notify("filings", report)
            except Exception as exc:
                console.print(f"[yellow]Filings fetch failed: {exc}[/]")
        if news_future is not None:
            try:
                nw = news_future.result()
                console.print(f"[green]Found {len(nw)} articles[/]")
                report.news = nw
                _notify("news", report)
            except Exception as exc:
                console.print(f"[yellow]News fetch failed: {exc}[/]")

    _notify("conclusion", report)

    console.print("[cyan]Saving analysis...[/]")
    path = save_analysis_report(ticker, _report_to_dict(report))
    console.print(f"[bold green]Analysis saved to:[/] {path}")
    _notify("complete", report)
    return report


def _report_to_dict(report: AnalysisReport) -> dict:
    def _dc(obj):
        if obj is None:
            return None
        if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
            return {k: _dc(v) for k, v in dataclasses.asdict(obj).items()}
        if isinstance(obj, list):
            return [_dc(i) for i in obj]
        return obj
    return _dc(report)


def _dict_to_report(d: dict) -> AnalysisReport:
    profile = _build_dc(CompanyProfile, d.get("profile", {}))
    profile.tier = _parse_tier(d.get("profile", {}).get("tier", ""))
    profile.stage = _parse_stage(d.get("profile", {}).get("stage", ""))

    def _maybe(cls, key):
        raw = d.get(key)
        return _build_dc(cls, raw) if raw is not None else None

    return AnalysisReport(
        profile=profile,
        valuation=_maybe(ValuationMetrics, "valuation"),
        profitability=_maybe(ProfitabilityMetrics, "profitability"),
        solvency=_maybe(SolvencyMetrics, "solvency"),
        growth=_maybe(GrowthMetrics, "growth"),
        efficiency=_maybe(EfficiencyMetrics, "efficiency"),
        finance_quality=_maybe(FinanceQualityIndicators, "finance_quality"),
        intrinsic_value=_maybe(IntrinsicValue, "intrinsic_value"),
        share_structure=_maybe(ShareStructure, "share_structure"),
        market_intelligence=_maybe(MarketIntelligence, "market_intelligence"),
        financials=[_build_dc(FinancialStatement, s) for s in d.get("financials", [])],
        filings=[_build_dc(Filing, f) for f in d.get("filings", [])],
        news=[_build_dc(NewsArticle, n) for n in d.get("news", [])],
        fetched_at=d.get("fetched_at", ""),
    )


def _build_dc(cls, data: dict):
    import dataclasses as dc
    field_names = {f.name for f in dc.fields(cls)}
    return cls(**{k: v for k, v in data.items() if k in field_names})


def _parse_tier(raw) -> CompanyTier:
    if isinstance(raw, CompanyTier):
        return raw
    for t in CompanyTier:
        if t.value == str(raw) or t.name == str(raw):
            return t
    return CompanyTier.NANO


def _parse_stage(raw) -> CompanyStage:
    if isinstance(raw, CompanyStage):
        return raw
    for s in CompanyStage:
        if s.value == str(raw) or s.name == str(raw):
            return s
    return CompanyStage.STARTUP


def _tier_color(tier) -> str:
    return {CompanyTier.MEGA: "bold green", CompanyTier.LARGE: "green", CompanyTier.MID: "cyan",
            CompanyTier.SMALL: "yellow", CompanyTier.MICRO: "#ff8800", CompanyTier.NANO: "bold red"}.get(tier, "white")


def _stage_color(stage) -> str:
    return {CompanyStage.PLATFORM: "bold green", CompanyStage.MATURE: "green",
            CompanyStage.SCALE: "cyan", CompanyStage.GROWTH: "yellow",
            CompanyStage.STARTUP: "#ff8800"}.get(stage, "white")
