*** Settings ***
Documentation    Export workflow tests for lynx-finance (uses Python API to avoid network timeouts)
Library          Process

*** Variables ***
${PYTHON}        python3

*** Keywords ***
When I Run Python Code "${code}"
    ${result}=    Run Process    ${PYTHON}    -c    ${code}    timeout=30s
    Set Test Variable    ${OUTPUT}    ${result.stdout}${result.stderr}
    Set Test Variable    ${RC}    ${result.rc}

Then The Exit Code Should Be ${expected}
    Should Be Equal As Integers    ${RC}    ${expected}

Then The Output Should Contain "${text}"
    Should Contain    ${OUTPUT}    ${text}

*** Test Cases ***
Export TXT From Minimal Report
    [Documentation]    GIVEN a report WHEN I export as TXT THEN a readable file is created
    When I Run Python Code "from lynx_finance.models import AnalysisReport, CompanyProfile, CompanyTier, CompanyStage, ValuationMetrics, SolvencyMetrics; from lynx_finance.export import export_report, ExportFormat; from pathlib import Path; import tempfile; p = CompanyProfile(ticker='TEST', name='Test Regional Bank', sector='Financial Services', industry='Banks - Regional', country='United States', market_cap=1500000000); p.tier = CompanyTier.MID; p.stage = CompanyStage.MATURE; r = AnalysisReport(profile=p, valuation=ValuationMetrics(pb_ratio=1.3, price_to_tangible_book_value=1.4), solvency=SolvencyMetrics(cet1_ratio=0.13, npl_ratio=0.012)); f = tempfile.NamedTemporaryFile(suffix='.txt', delete=False); path = export_report(r, ExportFormat.TXT, Path(f.name)); content = path.read_text(); assert 'Test Regional Bank' in content; assert 'Mature' in content or 'Expansion' in content; assert len(content) > 500; print('OK', len(content), 'bytes')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Export HTML From Minimal Report
    [Documentation]    GIVEN a report WHEN I export as HTML THEN a styled file with white background
    When I Run Python Code "from lynx_finance.models import AnalysisReport, CompanyProfile, CompanyTier, CompanyStage, ValuationMetrics, SolvencyMetrics; from lynx_finance.export import export_report, ExportFormat; from pathlib import Path; import tempfile; p = CompanyProfile(ticker='TEST', name='Test Regional Bank', sector='Financial Services', industry='Banks - Regional', country='United States', market_cap=1500000000); p.tier = CompanyTier.MID; p.stage = CompanyStage.MATURE; r = AnalysisReport(profile=p, valuation=ValuationMetrics(pb_ratio=1.3, price_to_tangible_book_value=1.4), solvency=SolvencyMetrics(cet1_ratio=0.13, npl_ratio=0.012)); f = tempfile.NamedTemporaryFile(suffix='.html', delete=False); path = export_report(r, ExportFormat.HTML, Path(f.name)); content = path.read_text(); assert '#fff' in content or '#ffffff' in content, 'Missing white background'; assert 'word-wrap' in content, 'Missing word-wrap'; assert 'Test Regional Bank' in content; assert len(content) > 1000; print('OK', len(content), 'bytes')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

HTML Has No Text Truncation
    [Documentation]    GIVEN an HTML export WHEN I check table cells THEN word-wrap is enabled
    When I Run Python Code "from lynx_finance.models import AnalysisReport, CompanyProfile, CompanyTier, CompanyStage, ValuationMetrics; from lynx_finance.export import export_report, ExportFormat; from pathlib import Path; import tempfile; p = CompanyProfile(ticker='T', name='T Corp'); p.tier = CompanyTier.MICRO; p.stage = CompanyStage.GROWTH; r = AnalysisReport(profile=p, valuation=ValuationMetrics(pb_ratio=0.8, price_to_tangible_book_value=0.9)); f = tempfile.NamedTemporaryFile(suffix='.html', delete=False); path = export_report(r, ExportFormat.HTML, Path(f.name)); c = path.read_text(); assert 'overflow-wrap' in c and 'break-word' in c; assert 'table-layout' in c and 'fixed' in c; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

HTML Has Professional White Background
    [Documentation]    GIVEN an HTML export WHEN I check styling THEN it uses white background
    When I Run Python Code "from lynx_finance.models import AnalysisReport, CompanyProfile; from lynx_finance.export import export_report, ExportFormat; from pathlib import Path; import tempfile; r = AnalysisReport(profile=CompanyProfile(ticker='T', name='T')); f = tempfile.NamedTemporaryFile(suffix='.html', delete=False); path = export_report(r, ExportFormat.HTML, Path(f.name)); c = path.read_text(); assert '#fff' in c or '#ffffff' in c, 'No white bg'; assert 'color: #1a1a2e' in c or 'color:#1a1a2e' in c, 'No dark text'; assert '@media print' in c, 'No print styles'; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"
