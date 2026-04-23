"""SEC EDGAR and regulatory report fetching."""

from __future__ import annotations

import time
from typing import Optional

import requests
import yfinance as yf

from lynx_finance import USER_AGENT_PRODUCT
from lynx_finance.core.storage import get_reports_dir, save_binary, save_json, save_text
from lynx_finance.models import Filing

DOWNLOAD_HEADERS = {"User-Agent": f"Mozilla/5.0 (compatible; {USER_AGENT_PRODUCT})", "Accept-Encoding": "gzip, deflate"}
EDGAR_HEADERS = {"User-Agent": f"{USER_AGENT_PRODUCT} lynx-finance-research@example.com", "Accept-Encoding": "gzip, deflate"}
EDGAR_BASE = "https://data.sec.gov"
TARGET_FORMS = {"10-K", "10-Q", "20-F", "6-K", "8-K", "10-K/A", "10-Q/A"}


def fetch_sec_filings(ticker: str) -> list[Filing]:
    filings = _fetch_via_yfinance(ticker)
    if not filings:
        filings = _fetch_via_edgar(ticker)
    if filings:
        rdir = get_reports_dir(ticker)
        save_json(rdir / "filings_index.json", [
            {"form": f.form_type, "date": f.filing_date, "period": f.period, "url": f.url}
            for f in filings
        ])
    return filings


def _fetch_via_yfinance(ticker: str) -> list[Filing]:
    filings: list[Filing] = []
    try:
        t = yf.Ticker(ticker)
        sec_filings = t.sec_filings
        if not sec_filings:
            return filings
        for item in sec_filings:
            form_type = item.get("type", "")
            if form_type not in TARGET_FORMS:
                continue
            filing_date = str(item.get("date", ""))
            url = ""
            exhibits = item.get("exhibits", {})
            for key in [form_type, form_type.replace("/", ""), "htm", "html"]:
                if key in exhibits:
                    url = exhibits[key]
                    break
            if not url and exhibits:
                url = next(iter(exhibits.values()), "")
            if not url:
                url = item.get("edgarUrl", "")
            filings.append(Filing(form_type=form_type, filing_date=filing_date, period=filing_date, url=url,
                                  description=item.get("title", f"{form_type} filed {filing_date}")))
    except Exception:
        pass
    return filings


def _fetch_via_edgar(ticker: str) -> list[Filing]:
    cik = _resolve_cik(ticker)
    if not cik:
        return []
    cik_padded = cik.zfill(10)
    try:
        resp = requests.get(f"{EDGAR_BASE}/submissions/CIK{cik_padded}.json", headers=EDGAR_HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []
    filings: list[Filing] = []
    recent = data.get("filings", {}).get("recent", {})
    if not recent:
        return filings
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accessions = recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])
    periods = recent.get("reportDate", [])
    for i, form in enumerate(forms):
        if form not in TARGET_FORMS or i >= len(accessions):
            continue
        accession = accessions[i].replace("-", "")
        doc = primary_docs[i] if i < len(primary_docs) else ""
        filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{doc}"
        filings.append(Filing(form_type=form, filing_date=dates[i] if i < len(dates) else "",
                              period=periods[i] if i < len(periods) else "", url=filing_url,
                              description=f"{form} filed {dates[i] if i < len(dates) else 'N/A'}"))
    return filings


def download_filing(ticker: str, filing: Filing, max_size_mb: int = 20) -> Optional[str]:
    if not filing.url:
        return None
    rdir = get_reports_dir(ticker)
    safe_date = (filing.filing_date or "unknown").replace("-", "")
    filename = f"{filing.form_type.replace('/', '_')}_{safe_date}"
    try:
        resp = requests.get(filing.url, headers=DOWNLOAD_HEADERS, timeout=60)
        resp.raise_for_status()
        content = resp.content
        if len(content) > max_size_mb * 1024 * 1024:
            return None
        content_type = resp.headers.get("content-type", "")
        if "pdf" in content_type or filing.url.endswith(".pdf"):
            path = rdir / f"{filename}.pdf"
            save_binary(path, content)
        else:
            path = rdir / f"{filename}.html"
            save_text(path, content.decode("utf-8", errors="replace"))
        filing.local_path = str(path)
        return str(path)
    except Exception:
        return None


def download_top_filings(ticker: str, filings: list[Filing], max_count: int = 10) -> list[Filing]:
    downloaded = []
    for filing in filings[:max_count]:
        path = download_filing(ticker, filing)
        if path:
            filing.local_path = path
            downloaded.append(filing)
        time.sleep(0.15)
    return downloaded


def _resolve_cik(ticker: str) -> Optional[str]:
    try:
        resp = requests.get("https://www.sec.gov/files/company_tickers.json", headers=EDGAR_HEADERS, timeout=15)
        if resp.status_code == 200:
            for entry in resp.json().values():
                if entry.get("ticker", "").upper() == ticker.upper():
                    return str(entry["cik_str"])
    except Exception:
        pass
    return None
