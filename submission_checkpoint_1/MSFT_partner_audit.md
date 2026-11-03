# MSFT partner-report audit worksheet

Report under review: [`MSFT_partner_report.md`](MSFT_partner_report.md)  
Source files: `runs/MSFT_20261028_214246/MSFT/` and `runs/MSFT_20261028_214246/AAPL/`

The report under review is the corrected MSFT draft. The student reports that the partner is doing MSFT. The human review marks and partner check are recorded below.

Human review — wrong or unsupported claims: **0**  
Human review — missing claims: **0**


| #              | Claim                                        | Report says                                  | Filing evidence reviewed                                                                                                                                                                 | Human Check |
| -------------- | -------------------------------------------- | -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| 1              | Total revenue, latest fiscal year            | $331.839bn                                   | MSFT FY2026 10-K `0001193125-26-323660`; `RevenueFromContractWithCustomerExcludingAssessedTax`; 2025-07-01 to 2026-06-30; saved-text lines 1376–1378.                                    | **Correct** |
| 2              | Revenue growth vs prior year                 | 17.79%; (331.839 / 281.724) − 1              | Same XBRL tag and 10-K; $331,839m FY2026,$281,724m FY2025, lines 1376–1378. Recalculate.                                                                                                 | **Correct** |
| 3              | Operating income and margin                  | $155.237bn; 46.78%                           | Same 10-K, `OperatingIncomeLoss`, FY2026; lines 1409–1410. Divide by $331.839bn revenue.                                                                                                 | **Correct** |
| 4              | Net income                                   | $133.749bn                                   | Same 10-K, `NetIncomeLoss`, FY2026; lines 1427–1429.                                                                                                                                     | **Correct** |
| 5              | Diluted EPS, GAAP                            | $17.95                                       | Same 10-K, `EarningsPerShareDiluted`, FY2026; label at line 1442, value at line 1444.                                                                                                    | **Correct** |
| 6              | Return on average equity                     | 34.04%                                       | Same 10-K: net income line 1429; equity $442,387m at 2026-06-30 and$343,479m at 2025-06-30, lines 1618–1620. Check arithmetic and period alignment.                                      | **Correct** |
| 7              | Debt to equity                               | 0.0911                                       | Same 10-K: current portion $9,227m lines 1566–1567; noncurrent debt$31,067m lines 1584–1585; equity $442,387m lines 1618–1619.                                                           | **Correct** |
| 8              | Free cash flow                               | $66.987bn                                    | Same 10-K: operating cash flow $182,935m lines 1715–1716; additions to property/equipment$(115,948)m lines 1769–1770.                                                                    | **Correct** |
| 9              | Latest-quarter revenue                       | $92.279bn                                    | MSFT earnings 8-K `0001193125-26-436122`, Exhibit 99.1; “In millions” line 279; total revenue lines 291–292.                                                                             | **Correct** |
| 10             | Quarter revenue growth vs prior-year quarter | 18.80%                                       | Same exhibit: 2026/2025 columns lines 281–283; revenues $92,279m/$77,673m lines 291–293. Recalculate.                                                                                    | **Correct** |
| 11             | Latest-quarter diluted EPS, GAAP             | $4.92; prior-year$3.72                       | Same exhibit: “Earnings per share” line 331; “Diluted” lines 335–337.                                                                                                                    | **Correct** |
| Other          | Peer margin and P/E                          | AAPL operating margin 31.97%; MSFT P/E 29.61 | AAPL FY2025 10-K `0000320193-25-000079`: revenue $416,161m line 562; operating income$133,050m line 572. Price log records MSFT close $531.56 on 2026-10-28; divide by FY2026 EPS$17.95. | **Correct** |
| Template       | Five parts complete                          | Five required headings and body content      | Check every heading and whether the report supplies substantive evidence. Verify that recommendations and future-development content are supported.                                      | **Correct** |
| Recommendation | Buy/Hold/Sell with one deciding number       | Buy; deciding number 46.78% operating margin | Check the thesis against report claims you marked correct. Verify the stated number and arithmetic above.                                                                                | **Correct** |


## Partner review

Partner company: **MSFT**.

Partner: **Aditi Nahane (AN)**; claims checked: **1 and 9**.

| Claim | Report claim | Filing evidence | Partner result | Notes |
|---|---|---|---|---|
| 1 | FY2026 revenue of $331.839 billion | MSFT 10-K `0001193125-26-323660`, lines 1376–1378; tag `RevenueFromContractWithCustomerExcludingAssessedTax`; period ending 2026-06-30. | **RIGHT** | Line 1376 labels total revenue; line 1377 reports 331,839 in millions ($331.839 billion). The period is 2025-07-01 to 2026-06-30. |
| 9 | Q1 FY2027 revenue of $92.279 billion for the quarter ended 2026-09-30 | MSFT 8-K `0001193125-26-436122`, Exhibit 99.1, lines 279–292. | **RIGHT** | Line 279 states amounts are in millions; lines 291–292 show total revenue of 92,279 ($92.279 billion) for the quarter ended September 30, 2026. |

**Comments:** Both values, periods, and cited lines match the saved sources.
**Method disclosure:** Aditi's accompanying message states that her AI assistant checked these two claims and entered the marks. This is an AI-assisted partner check, not a human-only verification.
