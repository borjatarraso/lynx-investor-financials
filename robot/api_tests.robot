*** Settings ***
Documentation    Python API tests for Lynx Financials — exercises the core functions directly.
Library          Process
Library          BuiltIn
Library          Collections
Suite Setup      Log    Starting API Tests


*** Keywords ***
I Run Python Code
    [Arguments]    ${code}
    ${result}=    Run Process    python3    -c    ${code}    stderr=STDOUT    timeout=30s
    Set Test Variable    ${PY_OUTPUT}    ${result.stdout}
    Set Test Variable    ${PY_RC}    ${result.rc}

The Output Should Contain
    [Arguments]    ${snippet}
    Should Contain    ${PY_OUTPUT}    ${snippet}

The Process Should Succeed
    Should Be Equal As Integers    ${PY_RC}    0    msg=Expected success but got ${PY_RC}: ${PY_OUTPUT}


*** Test Cases ***
Package Imports Successfully
    [Documentation]    GIVEN the package WHEN I import core classes THEN they load
    When I Run Python Code    from lynx_finance.models import AnalysisReport, CompanyProfile, CompanyStage, CompanyTier, FinanceCategory, JurisdictionTier, Relevance, Severity, MarketIntelligence, InsiderTransaction; print('OK')
    Then The Output Should Contain    OK
    And The Process Should Succeed

Classify Tier Mega Cap
    [Documentation]    GIVEN a 300B market cap WHEN I classify THEN Mega Cap
    When I Run Python Code    from lynx_finance.models import classify_tier; print(classify_tier(300_000_000_000).value)
    Then The Output Should Contain    Mega Cap

Classify Tier Micro Cap
    [Documentation]    GIVEN 100M market cap WHEN I classify THEN Micro Cap
    When I Run Python Code    from lynx_finance.models import classify_tier; print(classify_tier(100_000_000).value)
    Then The Output Should Contain    Micro Cap

Classify Stage Platform
    [Documentation]    GIVEN a G-SIB description WHEN I classify THEN Systemic / Dominant Franchise
    When I Run Python Code    from lynx_finance.models import classify_stage; print(classify_stage('globally systemically important diversified global bank', 50_000_000_000, {'marketCap': 300_000_000_000}).value)
    Then The Output Should Contain    Systemic

Classify Stage Mature
    [Documentation]    GIVEN profitable mature bank WHEN I classify THEN Mature
    When I Run Python Code    from lynx_finance.models import classify_stage; print(classify_stage('mature established franchise', 10_000_000_000, {'marketCap': 50_000_000_000, 'profitMargins': 0.25}).value)
    Then The Output Should Contain    Mature

Classify Stage Growth
    [Documentation]    GIVEN expansion-stage description WHEN I classify THEN Expansion
    When I Run Python Code    from lynx_finance.models import classify_stage; print(classify_stage('rapid loan growth regional bank', 100_000_000, {'revenueGrowth': 0.40}).value)
    Then The Output Should Contain    Expansion

Classify Stage Startup
    [Documentation]    GIVEN de novo description WHEN I classify THEN De Novo
    When I Run Python Code    from lynx_finance.models import classify_stage; print(classify_stage('de novo neobank', 0).value)
    Then The Output Should Contain    De Novo

Classify Category Diversified Bank
    [Documentation]    GIVEN diversified bank description WHEN I classify THEN Diversified
    When I Run Python Code    from lynx_finance.models import classify_category; print(classify_category('diversified universal bank money center bank', 'Banks - Diversified').value)
    Then The Output Should Contain    Diversified

Classify Category Insurance PC
    [Documentation]    GIVEN P&C insurer description WHEN I classify THEN P&C Insurance
    When I Run Python Code    from lynx_finance.models import classify_category; print(classify_category('property and casualty insurer auto insurance', 'Insurance - Property & Casualty').value)
    Then The Output Should Contain    P&C Insurance

Classify Category Asset Manager
    [Documentation]    GIVEN asset mgr description WHEN I classify THEN Asset & Wealth Management
    When I Run Python Code    from lynx_finance.models import classify_category; print(classify_category('asset management wealth management', 'Asset Management').value)
    Then The Output Should Contain    Asset

Classify Jurisdiction Tier 1 US
    [Documentation]    GIVEN United States WHEN I classify THEN Tier 1
    When I Run Python Code    from lynx_finance.models import classify_jurisdiction; print(classify_jurisdiction('United States').value)
    Then The Output Should Contain    Tier 1

Classify Jurisdiction Tier 2 India
    [Documentation]    GIVEN India WHEN I classify THEN Tier 2
    When I Run Python Code    from lynx_finance.models import classify_jurisdiction; print(classify_jurisdiction('India').value)
    Then The Output Should Contain    Tier 2

Relevance Startup PE Irrelevant
    [Documentation]    GIVEN startup stage WHEN I check P/E THEN irrelevant
    When I Run Python Code    from lynx_finance.metrics.relevance import get_relevance; from lynx_finance.models import CompanyTier, CompanyStage, Relevance; print(get_relevance('pe_trailing', CompanyTier.MICRO, 'valuation', CompanyStage.STARTUP) == Relevance.IRRELEVANT)
    Then The Output Should Contain    True

Relevance CET1 Critical For All Banks
    [Documentation]    GIVEN any stage WHEN I check CET1 ratio THEN critical
    When I Run Python Code    from lynx_finance.metrics.relevance import get_relevance; from lynx_finance.models import CompanyTier, CompanyStage, Relevance; print(get_relevance('cet1_ratio', CompanyTier.MID, 'solvency', CompanyStage.MATURE) == Relevance.CRITICAL)
    Then The Output Should Contain    True

Relevance NPL Critical For Mature Banks
    [Documentation]    GIVEN mature stage WHEN I check NPL ratio THEN critical
    When I Run Python Code    from lynx_finance.metrics.relevance import get_relevance; from lynx_finance.models import CompanyTier, CompanyStage, Relevance; print(get_relevance('npl_ratio', CompanyTier.MID, 'solvency', CompanyStage.MATURE) == Relevance.CRITICAL)
    Then The Output Should Contain    True

Relevance Mature ROE Critical
    [Documentation]    GIVEN mature stage WHEN I check ROE THEN critical
    When I Run Python Code    from lynx_finance.metrics.relevance import get_relevance; from lynx_finance.models import CompanyTier, CompanyStage, Relevance; print(get_relevance('roe', CompanyTier.MID, 'profitability', CompanyStage.MATURE) == Relevance.CRITICAL)
    Then The Output Should Contain    True

Explanations CET1 Metric Present
    [Documentation]    GIVEN explanations WHEN I look up cet1_ratio THEN it exists
    When I Run Python Code    from lynx_finance.metrics.explanations import get_explanation; e = get_explanation('cet1_ratio'); print(e.category if e else 'NONE')
    Then The Output Should Contain    solvency

Explanations NIM Metric Present
    [Documentation]    GIVEN explanations WHEN I look up nim THEN it exists
    When I Run Python Code    from lynx_finance.metrics.explanations import get_explanation; e = get_explanation('nim'); print(e.category if e else 'NONE')
    Then The Output Should Contain    profitability

Explanations Combined Ratio Present
    [Documentation]    GIVEN explanations WHEN I look up combined_ratio THEN it exists
    When I Run Python Code    from lynx_finance.metrics.explanations import get_explanation; e = get_explanation('combined_ratio'); print(e.category if e else 'NONE')
    Then The Output Should Contain    profitability

Severity Format Critical Red Bold
    [Documentation]    GIVEN CRITICAL severity WHEN I format THEN red + bold + triple stars
    When I Run Python Code    from lynx_finance.models import format_severity, Severity; s = format_severity(Severity.CRITICAL); assert '***CRITICAL***' in s and 'bold red' in s; print('OK')
    Then The Output Should Contain    OK

Severity Format Strong Silver
    [Documentation]    GIVEN STRONG severity WHEN I format THEN silver/grey
    When I Run Python Code    from lynx_finance.models import format_severity, Severity; s = format_severity(Severity.STRONG); assert '[STRONG]' in s and 'grey' in s; print('OK')
    Then The Output Should Contain    OK

Impact Format Critical Blinks Red
    [Documentation]    GIVEN CRITICAL relevance WHEN I format impact THEN blink + red
    When I Run Python Code    from lynx_finance.models import format_impact, Relevance; s = format_impact(Relevance.CRITICAL); assert 'blink' in s and 'red' in s; print('OK')
    Then The Output Should Contain    OK

Impact Format Irrelevant Silver
    [Documentation]    GIVEN IRRELEVANT relevance WHEN I format impact THEN silver/grey
    When I Run Python Code    from lynx_finance.models import format_impact, Relevance; s = format_impact(Relevance.IRRELEVANT); assert 'grey' in s; print('OK')
    Then The Output Should Contain    OK

Sector Validation Allows Bank
    [Documentation]    GIVEN a bank company WHEN I validate THEN allowed
    When I Run Python Code    from lynx_finance.core.analyzer import _validate_sector; from lynx_finance.models import CompanyProfile; p = CompanyProfile(ticker='JPM', name='JPMorgan Chase', sector='Financial Services', industry='Banks - Diversified'); _validate_sector(p); print('ALLOWED')
    Then The Output Should Contain    ALLOWED

Sector Validation Blocks Tech
    [Documentation]    GIVEN a tech company WHEN I validate THEN blocked
    When I Run Python Code    from lynx_finance.core.analyzer import _validate_sector, SectorMismatchError; from lynx_finance.models import CompanyProfile; p = CompanyProfile(ticker='MSFT', name='Microsoft', sector='Technology', industry='Software - Infrastructure');\ntry:\n    _validate_sector(p)\n    print('FAIL')\nexcept SectorMismatchError:\n    print('BLOCKED')
    Then The Output Should Contain    BLOCKED

Conclusion Generation Returns Verdict
    [Documentation]    GIVEN a minimal report WHEN I generate conclusion THEN verdict is present
    When I Run Python Code    from lynx_finance.models import AnalysisReport, CompanyProfile; from lynx_finance.core.conclusion import generate_conclusion; r = AnalysisReport(profile=CompanyProfile(ticker='T', name='T')); c = generate_conclusion(r); print(c.verdict)
    Then The Output Should Contain    Hold

Finance Screening Checklist Present
    [Documentation]    GIVEN a report WHEN I screen THEN cet1_well_capitalized key exists
    When I Run Python Code    from lynx_finance.models import AnalysisReport, CompanyProfile; from lynx_finance.core.conclusion import generate_conclusion; r = AnalysisReport(profile=CompanyProfile(ticker='T', name='T')); c = generate_conclusion(r); print('cet1_well_capitalized' in c.screening_checklist)
    Then The Output Should Contain    True

Metric Explanations Finance Specific
    [Documentation]    GIVEN explanations WHEN I list THEN finance metrics present
    When I Run Python Code    from lynx_finance.metrics.explanations import list_metrics; keys = [m.key for m in list_metrics()]; print('cet1_ratio' in keys and 'nim' in keys and 'combined_ratio' in keys and 'cash_to_market_cap' in keys)
    Then The Output Should Contain    True
