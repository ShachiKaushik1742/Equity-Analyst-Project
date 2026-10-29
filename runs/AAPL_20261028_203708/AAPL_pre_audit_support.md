# AAPL pre-audit evidence for student review

This note checks the report's numeric claims against the saved filing text and facts. It is an AI-assisted pre-audit. The `Mark (human)` column in `AAPL_human_audit.md` remains blank for the student's review, as required by that template.

All amounts below are USD millions unless noted. The 10-K statement labels Apple's sales as “Total net sales”; the release describes the figure as quarterly revenue.

| Checklist item | Report claim | Saved source evidence | Pre-audit result |
|---|---|---|---|
| 1. Annual revenue | $416,161 | 10-K lines 562–563: total net sales 416,161; XBRL tag `RevenueFromContractWithCustomerExcludingAssessedTax`, period ending 2025-09-27 | Matches. Use Apple's “total net sales” label. |
| 2. Revenue growth | 6.43% | 10-K line 562: 416,161 and 391,035; (416,161 / 391,035) − 1 = 6.43% | Matches. |
| 3. Operating income and margin | $133,050; 31.97% | 10-K line 572: operating income 133,050; total net sales 416,161 at line 562; 133,050 / 416,161 = 31.97% | Matches. |
| 4. Net income | $112,010 | 10-K line 576 | Matches. |
| 5. Diluted EPS | $7.46 | 10-K line 579 | Matches. |
| 6. Return on average equity | 171.42% | 10-K line 648: equity 73,733 for 2025 and 56,950 for 2024; net income 112,010 at line 576; 112,010 / ((73,733 + 56,950) / 2) = 171.42% | Matches the stated formula. |
| 7. Debt to equity | 1.3973 | 10-K lines 635 and 638: current debt 12,350 and non-current term debt 78,328; equity 73,733 at line 648; (78,328 + 12,350) / 73,733 = 1.3973 | Matches. |
| 8. Free cash flow | $98,767 | 10-K line 704: cash from operations 111,482; line 709: property/equipment additions 12,715; 111,482 − 12,715 = 98,767 | Matches. |
| 9. Latest-quarter revenue | $109,417; prior quarter $94,036 | 8-K exhibit lines 38–39: “Total net sales” 109,417 and 94,036 | Matches. |
| 10. Quarter revenue growth | 16.36% | 8-K exhibit lines 38–39; (109,417 / 94,036) − 1 = 16.36% | Matches. |
| 11. Latest-quarter diluted EPS | $2.02; prior year $1.57 | 8-K exhibit lines 62–66 | Matches. |
| Other: peer margin | MSFT 46.78% | `MSFT_facts.json`: revenue 331,839,000,000; operating income 155,237,000,000; 10-K accession `0001193125-26-323660`; ratio = 46.78% | Matches saved facts and arithmetic. |
| Other: P/E | 46.09 | Closing price $343.83 on 2026-10-28; FY2025 diluted EPS $7.46; 343.83 / 7.46 = 46.09 | Arithmetic matches. This uses latest annual EPS, not a forward or TTM EPS measure. |
| Template | Five required sections | All five headings are present in `AAPL_report.md` | Present. |
| Recommendation | Buy; deciding number is operating margin 31.97% | Recommendation section names operating margin 31.97% | The fact is supported; the Buy judgment is the student's decision to review. |

The official human audit still needs the student to compare the cited lines and enter the marks and counts. This note does not fill or certify those marks.
