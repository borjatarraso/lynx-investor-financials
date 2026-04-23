#!/usr/bin/env python3
"""
Lynx Financials Analysis — entry point.
Run directly:   python3 lynx-investor-financials.py [args]
Or via pip:     lynx-finance [args]
"""
from lynx_finance.cli import run_cli

if __name__ == "__main__":
    run_cli()
