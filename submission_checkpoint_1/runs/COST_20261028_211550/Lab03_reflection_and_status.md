# Lab 3 learning notes and status

## Human audit status

The COST report and source filings are saved in this run folder. The student's marks and counts are recorded in `COST_human_audit.md`: 7 wrong or unsupported claims and 1 missing claim. The report is a learning exercise and is not a human-verified investment recommendation beyond the stated audit marks.

## Learn on your own

XBRL is a structured format for reporting company facts. Each fact has a concept (tag), a value, a unit, and a period or date. EDGAR serves the company's facts in its company-facts file. The desk selected `RevenueFromContractWithCustomerExcludingAssessedTax` for COST revenue because its latest annual fact covers the latest fiscal year in the 10-K. The period matters: the start and end dates must match the fiscal year being compared. For COST, the latest period ends 2026-08-30; the prior-year revenue period ends 2025-08-31.

A filer can add, rename, or change how it reports a concept. A tag can also contain multiple periods. The reader therefore checks candidate tags and periods, chooses the newest fact that matches the revenue fiscal year, and records the tag, period, and filing. A human must still compare each fact with the statement in the filing. The audit's purpose is to catch a plausible but stale tag or a ratio whose inputs use different periods.

## Reflection to discuss with a partner

The step I would trust least on a company I have not seen is XBRL tag selection. A plausible tag can refer to net sales while another tag captures total revenue, or it can report an older period. For COST, the 10-K statement calls the selected $303,154 million figure **Total revenue**; net sales are a different subtotal. I would first improve the Financial Analyst role by requiring it to use the statement caption, preserve the tag and period, and flag any difference between total revenue and net sales. It must also describe P/E as the calculation on the stated FY diluted EPS, rather than call it forward P/E.

The four roles need the data steps in different ways: Research Analyst needs cited 10-K and release text; Financial Analyst needs verified facts, periods, arithmetic, quarter data, and peer comparisons; Investment Advisor needs the supported research and financial findings; Strategy Manager needs all role outputs and evidence to check and compile the report. Anthropic's financial-services repository says agent output is staged for human sign-off and agents do not make final investment recommendations or execute transactions ([README](https://github.com/anthropics/financial-services)). The model's recommendation in this learning report therefore needs human review.

The partner's MSFT company report and the partner's check of claims 1 and 9 are recorded in `../../MSFT_partner_audit.md`. The student records the spoken reflection discussion as completed in `../../XBRL_and_partner_reflection.md`. Aditi Nahane (AN) also checked COST known-answer Steps 2 and 4; see `../../COST_step_verification.md`.

## Reproduction

Tuesday, 2026-10-27 COST close used: **$992.13**, source: [YCharts COST historical price](https://ycharts.com/companies/COST/price).

```sh
./.venv/bin/python desk.py COST --peers WMT,TGT,BJ --price 992.13 --price-date 2026-10-27 --price-source https://ycharts.com/companies/COST/price --model
```

The project dependencies were already installed for this run. The project uses the OpenAI Python SDK with Purdue GenAI Studio configuration. The API key is read from `.env` and is not included in this folder or the report.
