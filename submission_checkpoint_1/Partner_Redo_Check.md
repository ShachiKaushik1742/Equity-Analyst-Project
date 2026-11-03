# Partner redo check — COST and MSFT

This completed partner check uses the saved filing evidence listed below. Aditi's accompanying message states that her AI assistant checked the cited claims and entered the marks. The results are therefore identified as AI-assisted partner work, not as a human-only source check.

**Reviewer / partner name:** Aditi Nahane  
**Initials:** AN  
**Date:** 2026-11-02

## A. COST — known-answer checks

Review the COST run at `runs/COST_20261028_211550/` and compare its output with the filings and facts. Record the mark only after checking the source.

| Check | What to verify | Filing evidence to open | Partner mark (RIGHT / WRONG) | Notes or correction |
|---|---|---|---|---|
| COST Step 2 — filing selection | Confirm the accession numbers and Accepted times. Confirm the selected 8-K reports Item 2.02 and includes Exhibit 99.1. Confirm newer non-earnings 8-Ks were skipped. | `COST/10K_0000909832-26-000093.txt`; `COST/10Q_0000909832-26-000051.txt`; `COST/8K_0000909832-26-000084.txt`; EDGAR index links in `COST_step_verification.md`. | RIGHT | Confirmed 10-K `0000909832-26-000093` accepted 2026-10-06 21:13:15 ET, 10-Q `0000909832-26-000051` accepted 2026-06-03 16:43:00 ET, and earnings 8-K `0000909832-26-000084` accepted 2026-09-24 16:17:37 ET. Item 2.02 and Exhibit 99.1 confirmed. Newer 8-Ks on Oct 14 and Oct 16 skipped correctly. |
| COST Step 4 — latest-year facts | Confirm the FY2026 period end is 2026-08-30 and check the selected revenue tag and key facts against the 10-K statements. Make sure comparators are not mistaken for the latest-year values. | COST 10-K accession `0000909832-26-000093`, especially saved-text lines 625, 629, 635, 638, 687, 691, 704, 766, 768; `COST/COST_facts.json`. | RIGHT | Period ended 2026-08-30 confirmed. Revenue tag `RevenueFromContractWithCustomerExcludingAssessedTax` with value $303,154 million confirmed. Operating income $11,685 million confirmed. Prior-year comparators separated properly. |

## B. MSFT — partner-company report claims

Review `MSFT_partner_report.md` and check these two core claims against the MSFT filings. The partner must independently make and initial the marks.

| Claim | Report value to check | Filing evidence to open | Partner mark (RIGHT / WRONG) | Notes or correction |
|---|---|---|---|---|
| MSFT Claim 1 — latest fiscal-year revenue | $331.839 billion for FY2026 | 10-K accession `0001193125-26-323660`; saved text lines 1376–1378 (amounts in millions); XBRL tag `RevenueFromContractWithCustomerExcludingAssessedTax`, period ending 2026-06-30. | RIGHT | Verified against lines 1376–1378 of `10K_0001193125-26-323660.txt` and `MSFT_facts.json`. Line 1376 reports "Total revenue", line 1377 reports 331,839 ($331,839 million = $331.839B). Period is 2025-07-01 to 2026-06-30. |
| MSFT Claim 9 — latest-quarter revenue | $92.279 billion for the quarter ended 2026-09-30 | 8-K accession `0001193125-26-436122`, Exhibit 99.1; saved text lines 279–292 (amounts in millions). | RIGHT | Verified against lines 279 and 291–292 of `8K_0001193125-26-436122.txt`. Line 279 confirms amounts in millions. Line 291 reports "Total revenue" and line 292 reports 92,279 ($92,279 million = $92.279B) for the quarter ended September 30, 2026. |

**Partner's two MSFT claim numbers checked:** 1 and 9  
**Partner initials:** AN  
**Comments:** Both Claim 1 and Claim 9 match the cited local 10-K and 8-K Exhibit 99.1 filings and XBRL facts. Values, periods, and line numbers are confirmed accurate.

## Completion record

| Review | Completed by | Initials | Date |
|---|---|---|---|
| COST Steps 2 and 4 | Aditi Nahane | AN | 2026-11-02 |
| MSFT two-claim check | Aditi Nahane | AN | 2026-11-02 |

Keep this completed sheet with the audit records.
