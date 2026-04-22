"""Financial data fetching via yfinance — Financials-sector flavour."""

from __future__ import annotations

from typing import Optional

import pandas as pd
import yfinance as yf

from lynx_finance.core.storage import get_financials_dir, save_json
from lynx_finance.models import CompanyProfile, FinancialStatement


def fetch_company_profile(ticker: str, info: dict | None = None) -> CompanyProfile:
    if info is None:
        info = fetch_info(ticker)
    return CompanyProfile(
        ticker=ticker.upper(),
        name=info.get("longName") or info.get("shortName", ticker),
        sector=info.get("sector"),
        industry=info.get("industry"),
        country=info.get("country"),
        exchange=info.get("exchange"),
        currency=info.get("currency", "USD"),
        market_cap=info.get("marketCap"),
        description=info.get("longBusinessSummary"),
        website=info.get("website"),
        employees=info.get("fullTimeEmployees"),
    )


def fetch_info(ticker: str) -> dict:
    try:
        t = yf.Ticker(ticker)
        return t.info or {}
    except Exception:
        return {}


def fetch_financial_statements(ticker: str) -> list[FinancialStatement]:
    try:
        t = yf.Ticker(ticker)
    except Exception:
        return []
    statements: list[FinancialStatement] = []

    try:
        income = _safe_df(t.financials)
    except Exception:
        income = None
    try:
        balance = _safe_df(t.balance_sheet)
    except Exception:
        balance = None
    try:
        cashflow = _safe_df(t.cashflow)
    except Exception:
        cashflow = None

    fdir = get_financials_dir(ticker)
    for name, df in [("income_annual", income), ("balance_annual", balance), ("cashflow_annual", cashflow)]:
        if df is not None and not df.empty:
            save_json(fdir / f"{name}.json", _df_to_dict(df))

    if income is not None and not income.empty:
        for col in income.columns:
            period = col.strftime("%Y") if hasattr(col, "strftime") else str(col)
            stmt = FinancialStatement(period=period)
            stmt.revenue = _get(income, col, "Total Revenue")
            stmt.cost_of_revenue = _get(income, col, "Cost Of Revenue")
            stmt.gross_profit = _get(income, col, "Gross Profit")
            stmt.operating_income = _get(income, col, "Operating Income")
            stmt.net_income = _get(income, col, "Net Income")
            stmt.ebitda = _get(income, col, "EBITDA")
            stmt.interest_expense = _get(income, col, "Interest Expense", "Interest Expense Non Operating")
            stmt.eps = _get(income, col, "Basic EPS")
            # Financials-specific income-statement items
            stmt.interest_income = _get(income, col, "Interest Income", "Interest Income Non Operating")
            stmt.net_interest_income = _get(income, col, "Net Interest Income")
            stmt.non_interest_income = _get(income, col, "Non Interest Income", "Other Non Interest Income")
            stmt.non_interest_expense = _get(income, col, "Non Interest Expense", "Operating Expense")
            stmt.provision_for_credit_losses = _get(income, col, "Provision For Loan Lease And Other Losses",
                                                    "Credit Losses Provision", "Provision For Credit Losses")
            # Insurance line items
            stmt.earned_premium = _get(income, col, "Premiums Earned", "Earned Premium",
                                       "Net Premiums Earned")
            stmt.losses_incurred = _get(income, col, "Net Policyholder Benefits And Claims",
                                        "Total Policyholder Benefits", "Losses And Loss Adjustment Expense")
            stmt.underwriting_expenses = _get(income, col, "Underwriting Expense",
                                              "Policy Acquisition Expense")
            stmt.net_investment_income = _get(income, col, "Net Investment Income",
                                              "Investment Income Net")
            # Asset managers
            stmt.management_fees = _get(income, col, "Investment Banking Profit",
                                        "Service Charge Fee Income", "Asset Management Fees")
            stmt.performance_fees = _get(income, col, "Performance Fees")

            if balance is not None and col in balance.columns:
                stmt.total_assets = _get(balance, col, "Total Assets")
                stmt.total_liabilities = _get(balance, col, "Total Liabilities Net Minority Interest")
                stmt.total_equity = _get(balance, col, "Stockholders Equity",
                                         "Total Equity Gross Minority Interest", "Common Stock Equity")
                stmt.total_debt = _get(balance, col, "Total Debt", "Long Term Debt")
                stmt.total_cash = _get(balance, col, "Cash And Cash Equivalents",
                                       "Cash Cash Equivalents And Short Term Investments")
                stmt.current_assets = _get(balance, col, "Current Assets")
                stmt.current_liabilities = _get(balance, col, "Current Liabilities")
                stmt.shares_outstanding = _get(balance, col, "Ordinary Shares Number", "Share Issued")
                # Financials balance-sheet items
                stmt.total_loans = _get(balance, col, "Net Loans", "Total Loans",
                                        "Loans Held For Investment", "Net Loan Receivables")
                stmt.total_deposits = _get(balance, col, "Total Deposits",
                                           "Customer Accounts", "Bank Indebtedness")
                stmt.allowance_for_loan_losses = _get(balance, col, "Allowance For Loans And Lease Losses",
                                                      "Loan Loss Allowance")
                stmt.non_performing_loans = _get(balance, col, "Non Performing Loans",
                                                 "Non Accruing Loans")
                stmt.invested_assets = _get(balance, col, "Investments And Advances",
                                            "Long Term Investments", "Investmentsinsecurities")
                stmt.insurance_reserves = _get(balance, col, "Insurance Reserves",
                                               "Reserves For Losses And Loss Adjustment Expense",
                                               "Future Policy Benefits Liability")
                stmt.goodwill = _get(balance, col, "Goodwill")
                stmt.intangibles = _get(balance, col, "Other Intangible Assets",
                                        "Intangible Assets Net Excluding Goodwill")
                if stmt.total_equity is not None and stmt.shares_outstanding and stmt.shares_outstanding > 0:
                    stmt.book_value_per_share = stmt.total_equity / stmt.shares_outstanding
                # Tangible Common Equity
                if stmt.total_equity is not None:
                    stmt.tangible_common_equity = stmt.total_equity - (stmt.goodwill or 0) - (stmt.intangibles or 0)
                # Earning assets proxy = total assets - cash - goodwill (rough)
                if stmt.total_assets:
                    stmt.earning_assets = stmt.total_assets - (stmt.total_cash or 0) - (stmt.goodwill or 0)
                # Interest-bearing liabilities proxy
                if stmt.total_liabilities:
                    stmt.interest_bearing_liabilities = (stmt.total_deposits or 0) + (stmt.total_debt or 0)
                    if stmt.interest_bearing_liabilities == 0:
                        stmt.interest_bearing_liabilities = stmt.total_liabilities

            if cashflow is not None and col in cashflow.columns:
                stmt.operating_cash_flow = _get(cashflow, col, "Operating Cash Flow")
                stmt.capital_expenditure = _get(cashflow, col, "Capital Expenditure")
                stmt.free_cash_flow = _get(cashflow, col, "Free Cash Flow")
                stmt.dividends_paid = _get(cashflow, col, "Common Stock Dividend Paid")
                # Net charge-offs proxy from cash flow if available
                stmt.net_charge_offs = _get(cashflow, col, "Net Charge Offs", "Loan Charge Offs")
                if stmt.free_cash_flow is None and stmt.operating_cash_flow is not None:
                    capex = stmt.capital_expenditure or 0
                    stmt.free_cash_flow = stmt.operating_cash_flow + capex

            # Derive net interest income if both sides are present
            if stmt.net_interest_income is None and stmt.interest_income is not None and stmt.interest_expense is not None:
                stmt.net_interest_income = stmt.interest_income - abs(stmt.interest_expense)

            statements.append(stmt)

    return statements


def _safe_df(df) -> Optional[pd.DataFrame]:
    if df is None:
        return None
    if isinstance(df, pd.DataFrame) and not df.empty:
        return df
    return None


def _get(df: pd.DataFrame, col, *row_names) -> Optional[float]:
    for name in row_names:
        if name in df.index:
            val = df.loc[name, col]
            if pd.notna(val):
                return float(val)
    return None


def _df_to_dict(df: pd.DataFrame) -> dict:
    result = {}
    for col in df.columns:
        key = col.isoformat() if hasattr(col, "isoformat") else str(col)
        result[key] = {}
        for idx in df.index:
            val = df.loc[idx, col]
            result[key][str(idx)] = None if pd.isna(val) else float(val)
    return result
