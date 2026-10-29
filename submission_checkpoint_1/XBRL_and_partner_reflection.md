# XBRL and partner reflection — COST FY2026

This note answers the Week 2 “The filings as data” and “Reflect” prompts. It uses the saved COST desk run and `COST_step_verification.md` as evidence. It is a prepared explanation; the partner discussion and partner check still need to happen.

## What XBRL is

XBRL is a format for reporting business facts in a way that software can read. A fact has a concept (the tag that says what it measures), a value, a unit, and a context. The context identifies the company and the time period. A fact can also have dimensions that give more detail, such as a business segment. A period can be a duration, such as revenue for a fiscal year, or an instant, such as equity on the last day of that year.

The SEC's Company Facts API provides a JSON file for a company. It groups facts that use standard taxonomies, including US-GAAP. It includes units and filing and period details. Company Facts does not include every custom company tag. Therefore, the filing remains the source to check when a fact is missing or unclear. See the [SEC description of EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) and the [SEC XBRL Guide](https://www.sec.gov/files/edgar/filer-information/specifications/xbrl-guide-2026-10-23.pdf).

## How the COST reader uses XBRL

For COST FY2026, the reader chose `RevenueFromContractWithCustomerExcludingAssessedTax` for revenue. The fact is **$303,154 million**, in USD, for the duration **2025-09-01 to 2026-08-30**, from 10-K accession `0000909832-26-000093`. It matches “Total revenue” on the 10-K income statement. The prior-year fact uses the same tag and the period **2024-09-02 to 2025-08-31**. The filing end date for FY2026 is **2026-08-30**.

The period matters because a tag name alone does not tell us which year a value describes. In this COST data, the alternative `Revenues` tag reaches only **2025-08-31**. The selected revenue tag reaches **2026-08-30**. The reader checks the period end and filing, then selects the newest candidate that matches the company's latest fiscal year. It also reads the other annual facts for that same fiscal year. This avoids dividing current-year operating income by older revenue, for example.

Facts use different period types. Revenue, income, and cash flow measure activity over a period. Equity and debt are balances at a date. The reader must preserve that difference when it prints facts and calculates ratios. For example, COST's FY2026 equity is an instant at **2026-08-30**, while revenue covers the year ending on that date.

## Partner explanation: why a tag can change

I would say: “A company can use a different XBRL tag in a later year because the taxonomy, the reported line item, or the company's mapping can change. A company can also use a custom tag when a standard tag does not fit its disclosure. So I should not assume that one tag name will contain every year's value. Our reader checks candidate tags and their filing periods. For COST, `RevenueFromContractWithCustomerExcludingAssessedTax` reaches the 2026 fiscal year end, while `Revenues` reaches only the 2025 year end. The date and filing show which year each number belongs to. I still check the selected value against the 10-K statement.”

## Reflection

**1. Step I would trust least on a company I have not seen:** Step 4, selecting XBRL facts. One company may have multiple candidate tags, custom tags, a different fiscal year end, or facts with different periods and units. The reader's selection can look plausible while using an older period or a different definition. I would check the tag, unit, period, accession, and corresponding filing statement before I trust the number.

**2. What the four roles need from these steps on Thursday:**

- **Research Analyst:** the 10-K, 10-Q, and earnings release text, with exact filing references and quoted lines for business, risks, recent developments, and quarterly claims.
- **Financial Analyst:** the selected facts with tags, values, units, periods, and accessions; prior-year facts; peer facts on matching definitions; and ratios with their inputs and arithmetic. P/E also needs the supplied share price and its date and source.
- **Investment Advisor:** the Research Analyst's and Financial Analyst's supported findings, plus one deciding number to use in the thesis and recommendation.
- **Strategy Manager:** all five report parts for the same company, with consistent periods and definitions. The manager checks completeness and contradictions. A human still checks whether each number is supported by a filing.

The four roles use the data gathered in these steps. They do not replace the filing checks or the human audit. The exact role prompts are in `desk.py`.

**Partner check:** not recorded yet. After the discussion, ask the partner to check two marks in `COST_step_verification.md` and record those marks there. Keep the human mark column in `COST_human_audit.md` for your own filing review.
