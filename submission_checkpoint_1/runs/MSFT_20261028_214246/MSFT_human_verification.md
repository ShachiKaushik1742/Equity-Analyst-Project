# MSFT Human Verification Record

**Superseded record:** This blank verification record refers to the original model-generated `MSFT_report.md`. The checkpoint audit is now recorded in [`MSFT_partner_audit.md`](../../MSFT_partner_audit.md) for the corrected report, including the human marks, counts, and partner check.

Report verified: [`MSFT_report.md`](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT_report.md)  
Audit template reference: [`MSFT_human_audit.md`](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT_human_audit.md) (commit [`6681e91`](https://github.com/ShachiKaushik1742/Equity-Analyst-Project/commit/6681e91))  
Run directory: [`runs/MSFT_20261028_214246/`](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/)  
Date of verification: 2026-10-28  

This document records the human verification evidence for the MSFT equity research report. The evidence follows the audit template structure. As required by course guidelines, the **Mark (human)** column, the final error counts, and the partner checks are left open for the student and partner to complete by hand.

---

## Audit Summary Table

| # | Claim | Report says | Filing says / source line | Mark (human) |
|---|---|---|---|---|
| 1 | Total revenue, latest fiscal year | $331,839,000,000; report lines 23, 47, 66 | MSFT 10-K accession `0001193125-26-323660`, FY ended 2026-06-30: income statement lines 1376–1378 shows total revenue $331,839 million for FY2026 and $281,724 million for FY2025. XBRL tag `RevenueFromContractWithCustomerExcludingAssessedTax`, USD, FY 2026 period 2025-07-01 to 2026-06-30. |  |
| 2 | Revenue growth vs prior year | 17.79%; report line 33 | Same 10-K and revenue tag: $331,839 million (2026) and $281,724 million (2025), lines 1376–1378; both are annual periods. Arithmetic: (331,839 / 281,724) − 1 = 17.7887%, approximately 17.79%. |  |
| 3 | Operating income and operating margin | Operating income $155,237,000,000; margin 46.78%; report lines 25 and 34 | Same 10-K: operating income $155,237 million, lines 1409–1410; FY2026 revenue $331,839 million, lines 1376–1378. XBRL tag `OperatingIncomeLoss`, FY2026. Arithmetic: 155,237 / 331,839 = 46.7808%, approximately 46.78%. |  |
| 4 | Net income attributable to company | Net income $133,749,000,000; report line 26 | Same 10-K: net income $133,749 million, lines 1427–1429. XBRL tag `NetIncomeLoss`, FY2026. |  |
| 5 | Diluted earnings per share, GAAP | $17.95 per share; report line 27 | Same 10-K: “Earnings per share” at line 1434, “Diluted” at line 1442, and $17.95 at line 1444. XBRL tag `EarningsPerShareDiluted`, FY2026. |  |
| 6 | Return on average equity | 34.04%; inputs $442,387,000,000 and $343,479,000,000; report lines 28, 35, 39 | Same 10-K: net income $133,749 million, line 1429; total stockholders’ equity $442,387 million (2026) and $343,479 million (2025), lines 1618–1620. Arithmetic: 133,749 / ((442,387 + 343,479) / 2) = 34.0386%, approximately 34.04%. **Provenance issue:** report line 39 cites accession `0000950170-25-100235`; the $343,479 million comparative value is also in the current 10-K cited on line 1, accession `0001193125-26-323660`. Check why the report cites the other accession. |  |
| 7 | Debt to equity | 0.0911; debt $31,067,000,000 plus current portion $9,227,000,000; report lines 28–30, 36 | Same 10-K: current portion of long-term debt $9,227 million, lines 1566–1567; long-term debt $31,067 million, lines 1584–1585; total stockholders’ equity $442,387 million, lines 1618–1619. Tags: `LongTermDebtCurrent`, `LongTermDebtNoncurrent`, `StockholdersEquity`. Arithmetic: (31,067 + 9,227) / 442,387 = 0.091083, or 9.11%. |  |
| 8 | Free cash flow | $66,987,000,000; report lines 31–32, 37 | Same 10-K: net cash from operations $182,935 million, lines 1715–1716; additions to property and equipment $(115,948) million, lines 1769–1770. Tags: `NetCashProvidedByUsedInOperatingActivities` and `PaymentsToAcquirePropertyPlantAndEquipment`. Arithmetic using capex as a positive spend: 182,935 − 115,948 = $66,987 million. |  |
| 9 | Latest quarter revenue | $92,279 million; report lines 17 and 40 | MSFT 8-K accession `0001193125-26-436122`, Exhibit 99.1: income statement labels “In millions” at line 279 and “Three Months Ended” at line 280; “Total revenue” at line 291 and $92,279 at line 292 (quarter ended 2026-09-30). |  |
| 10 | Quarter revenue growth vs same quarter last year | 18.80%; report line 40 | Same 8-K Exhibit 99.1: comparative quarter columns for 2026 and 2025 at lines 281–283; total revenue $92,279 million and $77,673 million at lines 291–293. Arithmetic: (92,279 / 77,673) − 1 = 18.8045%, approximately 18.80%. |  |
| 11 | Quarter diluted EPS, GAAP | $4.92; prior-year quarter $3.72; report lines 18 and 41 | Same 8-K Exhibit 99.1: “Earnings per share” line 331; “Diluted” line 335; $4.92 and $3.72 on lines 336–337 for the 2026 and 2025 quarters. |  |
| Other | Every other Financial Analyst number (peers, P/E, extra ratios) | AAPL revenue $416.161bn, operating income $133.050bn, margin 31.97%; MSFT P/E 29.6134; quarter growth 18.80%; see report lines 33–43. | AAPL 10-K accession `0000320193-25-000079`, FY2025: net sales $416,161 million at saved-text line 562; operating income $133,050 million at line 572. Arithmetic: 133,050 / 416,161 = 31.9708%, approximately 31.97%. MSFT P/E: report price $531.56 (2026-10-28) / 10-K diluted EPS $17.95 = 29.6134; price source is listed in `Market_price_log.md`. **Citation issue:** report calls the AAPL top-line label “Net sales” at line 562, while line 562 is the value row “Total net sales”; “Net sales:” is the heading at line 559. Additional MSFT inputs are in the rows above. |  |
| Template | All five report parts present and complete | All five headings exist: report lines 8, 12, 20, 49, 63. | `Overview` (line 8) contains ticker, fiscal year, and filings. `Market Positioning and Growth Outlook` (line 12) contains business/release information. `Valuation Insights` (line 20) contains facts, but the Financial Analyst interpretation stops mid-sentence at line 47 (“..., a”). `Future Developments and Strategic Recommendations` (line 49) repeats Research Analyst material at lines 53–57 and has another incomplete fragment at line 61; it does not provide the requested future developments or strategic recommendations. `Investment Recommendation` is at line 63. Consider whether the five parts are substantively complete, not only whether headings exist. |  |
| Recommendation | Buy/Hold/Sell names a stated deciding number | “Buy”; deciding number is $331.839bn revenue; report line 66. | The 10-K supports FY2026 revenue of $331,839 million (lines 1376–1378). However, report line 47 truncates the Financial Analyst interpretation after “a,” so the report does not show that the Analyst supplied or endorsed this deciding number. The qualitative statements about a “competitive moat” and “sustainable margins” are not substantiated in the cited passage. Decide whether the stated decision number and recommendation meet the assignment standard. |  |

---

## Detailed Item Verification and Arithmetic

### Row 1: Total Revenue, Latest Fiscal Year
- **Report Claim**: `revenue: 331839000000 USD` (line 23), `Fiscal 2026 revenue reached **$331.839 bn**` (line 47), `Fiscal 2026 revenue hit **$331.839 bn**` (line 66).
- **Filing Source**: MSFT Form 10-K, accession `0001193125-26-323660`, period `2025-07-01` to `2026-06-30`.
- **Filing Evidence**: [10K_0001193125-26-323660.txt](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT/10K_0001193125-26-323660.txt#L1376-L1377), lines 1376–1377:
  - Line 1376: `Total revenue`
  - Line 1377: `331,839` (caption at line 1359 states *In millions*).
  - XBRL tag in [`MSFT_facts.json`](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT/MSFT_facts.json#L30-L40): `RevenueFromContractWithCustomerExcludingAssessedTax`, value `331839000000` USD.
- **Arithmetic**: $331,839 \times 1,000,000 = \$331,839,000,000\text{ USD}$ ($331.839\text{ bn}$).

### Row 2: Revenue Growth vs Prior Year
- **Report Claim**: `Revenue growth: 17.79%; arithmetic: (331839000000 / 281724000000) - 1.` (line 33).
- **Filing Source**: MSFT Form 10-K, accession `0001193125-26-323660`.
- **Filing Evidence**: [10K_0001193125-26-323660.txt](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT/10K_0001193125-26-323660.txt#L1376-L1378):
  - Line 1377 (FY 2026): `331,839` million.
  - Line 1378 (FY 2025): `281,724` million.
  - XBRL tag in [`MSFT_facts.json`](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT/MSFT_facts.json#L129-L139): `RevenueFromContractWithCustomerExcludingAssessedTax`.
- **Arithmetic**: $\frac{331,839,000,000}{281,724,000,000} - 1 = \frac{331,839}{281,724} - 1 = 1.177886868... - 1 \approx 17.79\%$.

### Row 3: Operating Income and Operating Margin
- **Report Claim**: `operating_income: 155237000000 USD` (line 25), `Operating margin: 46.78%` (line 34).
- **Filing Source**: MSFT Form 10-K, accession `0001193125-26-323660`, period `2025-07-01` to `2026-06-30`.
- **Filing Evidence**: [10K_0001193125-26-323660.txt](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT/10K_0001193125-26-323660.txt#L1409-L1410):
  - Line 1409: `Operating income`
  - Line 1410: `155,237` ($155,237 million = $155,237,000,000 USD).
  - XBRL tag in [`MSFT_facts.json`](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT/MSFT_facts.json#L41-L51): `OperatingIncomeLoss`.
- **Arithmetic**: $\frac{155,237,000,000}{331,839,000,000} = \frac{155,237}{331,839} = 0.467808184... \approx 46.78\%$.

### Row 4: Net Income Attributable to Company
- **Report Claim**: `net_income: 133749000000 USD` (line 26).
- **Filing Source**: MSFT Form 10-K, accession `0001193125-26-323660`, period `2025-07-01` to `2026-06-30`.
- **Filing Evidence**: [10K_0001193125-26-323660.txt](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT/10K_0001193125-26-323660.txt#L1427-L1429):
  - Line 1427: `Net income`
  - Line 1429: `133,749` ($133,749 million = $133,749,000,000 USD).
  - XBRL tag in [`MSFT_facts.json`](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT/MSFT_facts.json#L52-L62): `NetIncomeLoss`.
- **Arithmetic**: $133,749 \times 1,000,000 = \$133,749,000,000\text{ USD}$.

### Row 5: Diluted Earnings Per Share, GAAP
- **Report Claim**: `diluted_eps: 17.95 USD/shares` (line 27).
- **Filing Source**: MSFT Form 10-K, accession `0001193125-26-323660`, period `2025-07-01` to `2026-06-30`.
- **Filing Evidence**: [10K_0001193125-26-323660.txt](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT/10K_0001193125-26-323660.txt#L1434-L1444):
  - Line 1434: `Earnings per share:`
  - Line 1442: `Diluted`
  - Line 1444: `17.95` ($17.95 USD per share).
  - XBRL tag in [`MSFT_facts.json`](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT/MSFT_facts.json#L63-L73): `EarningsPerShareDiluted`.
- **Arithmetic**: Stated directly in filing.

### Row 6: Return on Average Equity
- **Report Claim**: `Return on average equity: 34.04%` (line 35).
- **Filing Source**: MSFT Form 10-K, accession `0001193125-26-323660`.
- **Filing Evidence**: [10K_0001193125-26-323660.txt](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT/10K_0001193125-26-323660.txt#L1618-L1620):
  - Net income: line 1429 = `133,749` million ($133,749,000,000 USD).
  - Current year equity (at 2026-06-30): line 1619 = `442,387` million ($442,387,000,000 USD).
  - Prior year equity (at 2025-06-30 comparative column): line 1620 = `343,479` million ($343,479,000,000 USD).
  - **Discrepancy Note**: Line 39 cites accession `0000950170-25-100235` for prior-year equity. That accession was not in the saved run folder and was not listed in line 1 ("Filings read"). The comparative balance sheet of the current 10-K (`0001193125-26-323660`, line 1620) contains this exact $343,479 million number.
- **Arithmetic**:
  - $\text{Average Equity} = \frac{442,387,000,000 + 343,479,000,000}{2} = 392,933,000,000\text{ USD}$.
  - $\text{ROAE} = \frac{133,749,000,000}{392,933,000,000} = 0.3403862... \approx 34.04\%$.

### Row 7: Debt to Equity
- **Report Claim**: `Debt to equity: 0.0911` (line 36).
- **Filing Source**: MSFT Form 10-K, accession `0001193125-26-323660`.
- **Filing Evidence**: [10K_0001193125-26-323660.txt](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT/10K_0001193125-26-323660.txt#L1566-L1619):
  - Current portion of long-term debt: line 1567 = `9,227` million ($9,227,000,000 USD). Tag: `LongTermDebtCurrent`.
  - Long-term debt: line 1585 = `31,067` million ($31,067,000,000 USD). Tag: `LongTermDebtNoncurrent`.
  - Total stockholders’ equity: line 1619 = `442,387` million ($442,387,000,000 USD). Tag: `StockholdersEquity`.
- **Arithmetic**:
  - $\text{Total Debt} = 31,067,000,000 + 9,227,000,000 = \$40,294,000,000\text{ USD}$.
  - $\text{Debt to Equity} = \frac{40,294,000,000}{442,387,000,000} = 0.09108314... \approx 0.0911$ (or $9.11\%$).

### Row 8: Free Cash Flow
- **Report Claim**: `Free cash flow: 66987000000.0` (line 37).
- **Filing Source**: MSFT Form 10-K, accession `0001193125-26-323660`, period `2025-07-01` to `2026-06-30`.
- **Filing Evidence**: [10K_0001193125-26-323660.txt](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT/10K_0001193125-26-323660.txt#L1715-L1771):
  - Cash from operations: line 1716 = `182,935` million ($182,935,000,000 USD). Tag: `NetCashProvidedByUsedInOperatingActivities`.
  - Capex / Additions to property and equipment: line 1770 = `( 115,948 )` million ($115,948,000,000 USD). Tag: `PaymentsToAcquirePropertyPlantAndEquipment`.
- **Arithmetic**: $182,935,000,000 - 115,948,000,000 = \$66,987,000,000\text{ USD}$ ($66.987\text{ bn}$).

### Row 9: Latest Quarter Revenue
- **Report Claim**: `total revenue: “Total revenue 92,279”` (line 17), `Latest-quarter revenue (dollars in millions): 92279.0` (line 40), `quarterly revenue of $92.3 bn` (line 66).
- **Filing Source**: MSFT Form 8-K, Exhibit 99.1, accession `0001193125-26-436122`.
- **Filing Evidence**: [8K_0001193125-26-436122.txt](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT/8K_0001193125-26-436122.txt#L279-L292):
  - Line 279: `(In millions, except per share amounts) (Unaudited)`
  - Line 280: `Three Months Ended`
  - Line 281: `September 30,`
  - Line 282: `2026`
  - Line 291: `Total revenue`
  - Line 292: `92,279` ($92,279 million = $92,279,000,000 USD).
- **Arithmetic**: $92,279 \text{ million} = \$92.279\text{ bn} \approx \$92.3\text{ bn}$.

### Row 10: Quarter Revenue Growth vs Same Quarter Last Year
- **Report Claim**: `growth: 18.80%, arithmetic (92279.0 / 77673.0) - 1` (line 40).
- **Filing Source**: MSFT Form 8-K, Exhibit 99.1, accession `0001193125-26-436122`.
- **Filing Evidence**: [8K_0001193125-26-436122.txt](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT/8K_0001193125-26-436122.txt#L281-L293):
  - Line 282: Column 1 `2026`
  - Line 283: Column 2 `2025`
  - Line 291: `Total revenue`
  - Line 292 (Three Months Ended Sep 30, 2026): `92,279` million
  - Line 293 (Three Months Ended Sep 30, 2025): `77,673` million
- **Arithmetic**: $\frac{92,279}{77,673} - 1 = 1.18804475... - 1 \approx 18.80\%$.

### Row 11: Quarter Diluted EPS, GAAP
- **Report Claim**: `diluted EPS: “Diluted $4.92 $3.72”` (line 18), `Latest-quarter diluted EPS, GAAP: 4.92; prior-year quarter: 3.72` (line 41), `EPS $4.92` (line 66).
- **Filing Source**: MSFT Form 8-K, Exhibit 99.1, accession `0001193125-26-436122`.
- **Filing Evidence**: [8K_0001193125-26-436122.txt](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT/8K_0001193125-26-436122.txt#L331-L337):
  - Line 331: `Earnings per share:`
  - Line 335: `Diluted`
  - Line 336 (Three Months Ended Sep 30, 2026): `$4.92`
  - Line 337 (Three Months Ended Sep 30, 2025): `$3.72`
- **Arithmetic**: Stated directly in filing.

### Row "Other": Peer Facts and P/E Input
1. **Peer AAPL Margin**:
   - **Report Claim** (line 42): Revenue $416,161,000,000, Operating Income $133,050,000,000, Operating Margin 31.97%.
   - **Filing Source**: AAPL Form 10-K, accession `0000320193-25-000079`, period `2024-09-29` to `2025-09-27`.
   - **Filing Evidence**: [10K_0000320193-25-000079.txt](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/AAPL/10K_0000320193-25-000079.txt#L559-L572):
     - Line 559: `Net sales:`
     - Line 562: `Total net sales 416,161 391,035 383,285` ($416,161 million). Tag: `RevenueFromContractWithCustomerExcludingAssessedTax`.
     - Line 572: `Operating income 133,050 123,216 114,301` ($133,050 million). Tag: `OperatingIncomeLoss`.
   - **Arithmetic**: $\frac{133,050,000,000}{416,161,000,000} = 0.31970799... \approx 31.97\%$.
   - **Discrepancy Note**: The report cites line 562 as statement top-line label `'Net sales'`. In the text file, line 559 is the section heading `'Net sales:'`, and line 562 is the total line `'Total net sales 416,161'`.
2. **P/E Ratio and Price Input**:
   - **Report Claim** (lines 6, 38, 43): Price $531.56 on 2026-10-28; P/E 29.613370473537604.
   - **Source Verification**: [Market_price_log.md line 8](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/Market_price_log.md#L8): `| MSFT | $531.56 | 2026-10-28 | [ChartExchange historical prices](https://chartexchange.com/symbol/nasdaq-msft/historical/) |`.
   - **Arithmetic**: $\frac{531.56}{17.95} = 29.613370473537604 \approx 29.61$.

### Row "Template": Five Required Report Sections
- `## Overview` (line 8): **Present**.
- `## Market Positioning and Growth Outlook` (line 12): **Present**.
- `## Valuation Insights` (line 20): **Defective / Truncated**. The subsection `Financial Analyst interpretation:` stops abruptly mid-sentence at line 47:
  `Fiscal 2026 revenue reached **$331.839 bn** (RevenueFromContractWithCustomerExcludingAssessedTax, 2025-07-01 to 2026-06-30, 10-K 0001193125-26-323660), a`
- `## Future Developments and Strategic Recommendations` (line 49): **Missing / Defective**.
  - The markdown heading exists, but it contains **no** future developments and **no** strategic recommendations.
  - Lines 51–58 literally duplicate the Research Analyst output from lines 13–18.
  - Lines 59–62 duplicate the incomplete fragment ending in `, a`.
- `## Investment Recommendation` (line 63): **Present**.

### Row "Recommendation": Buy/Hold/Sell and Deciding Number
- Recommendation: `Buy` (line 66).
- Stated Deciding Number: `**Deciding number**: $331.839 bn revenue (Financial Analyst).` (line 66).
- Verification: The deciding number is supported by 10-K line 1377. However, the Financial Analyst section truncated before giving its written analysis, so the narrative endorsement of this deciding number by that role was cut short.

---

## Narrative Claims and Attribution Checks

1. **Competition Citation Misattribution** (Report lines 14 and 53):
   - **Report Claim**: `Competitors “include software and global application vendors… We compete by providing secure, integrated… productivity and collaboration tools” (10‑K, *MD&A*, line 222‑223).`
   - **Filing Evidence**: [10K_0001193125-26-323660.txt lines 222–223](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT/10K_0001193125-26-323660.txt#L222-L223):
     - Line 222: `Competition`
     - Line 223: `Competitors to Office include software and global application vendors...`
   - **Discrepancy**: Lines 222–223 are located under **Item 1. Business** (under `Productivity and Business Processes`), not Item 7 MD&A (Item 7 starts at line 684). In addition, the text specifically states competitors "to Office".
2. **Business Description Quotes** (Report lines 14 and 53):
   - Line 149 quote matches [10K line 149](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT/10K_0001193125-26-323660.txt#L149) verbatim.
   - Lines 150 and 155 quotes change "We develop" / "We offer" to "develops" / "offers" inside quotation marks.
   - Line 156 quote accurately extracts items from [10K line 156](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT/10K_0001193125-26-323660.txt#L156).
   - Line 161 quotes accurately extract cloud integration and economies of scale from [10K line 161](file:///Users/shachi/Documents/FIN67110/runs/MSFT_20261028_214246/MSFT/10K_0001193125-26-323660.txt#L161).

---

## Student and Partner Verification Section

The marks and counts below must be decided and recorded by the student and partner:

- **Errors (wrong + unsupported)**: TO BE COUNTED BY STUDENT  
- **Missing claims**: TO BE COUNTED BY STUDENT  
- **Partner name/check**: ____________________  
- **Marks checked by partner**: ______ and ______  
- **Partner comments**: ____________________  
