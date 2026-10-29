# Human audit — AAPL

Report: `AAPL_report.md`

Errors (wrong + unsupported): TO BE COUNTED BY HUMAN
Missing claims: TO BE COUNTED BY HUMAN

Do not let an AI fill the Mark column. Compare each report claim with the named filing and write the filing's value/line.

| # | Claim | Report says | Filing says / source line | Mark (human) |
|---|---|---|---|---|
| 1 | Total revenue, latest fiscal year | $416,161m; `RevenueFromContractWithCustomerExcludingAssessedTax`; FY ended 2025-09-27 | 10-K statement, saved-text line 562; accession 0000320193-25-000079 |  |
| 2 | Revenue growth vs prior year | 6.43%; ($416,161m / $391,035m) - 1 | Same XBRL tag; latest FY 2025-09-27, prior FY 2024-09-28; accession 0000320193-25-000079 |  |
| 3 | Operating income and operating margin | $133,050m; 31.97% ($133,050m / $416,161m) | 10-K XBRL `OperatingIncomeLoss` and revenue tag, FY 2025-09-27; accession 0000320193-25-000079 |  |
| 4 | Net income attributable to company | $112,010m | 10-K XBRL `NetIncomeLoss`, FY 2025-09-27; accession 0000320193-25-000079 |  |
| 5 | Diluted earnings per share, GAAP | $7.46 | 10-K XBRL `EarningsPerShareDiluted`, FY 2025-09-27; accession 0000320193-25-000079 |  |
| 6 | Return on average equity | 171.42%; $112,010m / (($73,733m + $56,950m) / 2) | Net income and equity tags, current FY 2025-09-27; prior equity FY 2024-09-28, 10-K accession 0000320193-24-000123 |  |
| 7 | Debt to equity | 1.3973; ($90,678m + $12,350m) / $73,733m | 10-K tags `LongTermDebt`, `LongTermDebtCurrent`, `StockholdersEquity`, instant 2025-09-27; accession 0000320193-25-000079 |  |
| 8 | Free cash flow | $98,767m; $111,482m - $12,715m | 10-K tags `NetCashProvidedByUsedInOperatingActivities`, `PaymentsToAcquirePropertyPlantAndEquipment`, FY 2025-09-27; accession 0000320193-25-000079 |  |
| 9 | Latest quarter revenue | $109,417m | 8-K Exhibit 99.1 saved-text lines 38-39, total net sales; accession 0000320193-26-000018 |  |
| 10 | Quarter revenue growth vs same quarter last year | 16.36%; ($109,417m / $94,036m) - 1 | 8-K Exhibit 99.1 line 39, first two quarter columns; accession 0000320193-26-000018 |  |
| 11 | Quarter diluted EPS, GAAP | $2.02; prior-year quarter $1.57 | 8-K Exhibit 99.1 saved-text lines 65-66; accession 0000320193-26-000018 |  |
| Other | Every other Financial Analyst number (peers, P/E, extra ratios) | MSFT margin 46.78%; P/E 46.53 ($347.10 / $7.46) | MSFT 10-K accession 0001193125-26-323660, FY 2026-06-30; AAPL 10-K accession 0000320193-25-000079; price close 2026-10-27 |  |
| Template | All five report parts present | All five headings present | AAPL_report.md |  |
| Recommendation | Buy/Hold/Sell names a stated deciding number | Buy; deciding number: operating margin 31.97% | AAPL_report.md; human claim marks still pending |  |
