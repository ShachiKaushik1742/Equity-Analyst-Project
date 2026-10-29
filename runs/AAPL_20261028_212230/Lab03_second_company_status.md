# Lab 3 second-company run: AAPL with MSFT peer

The user selected AAPL as the second company and MSFT as its peer. The run completed all seven data steps and the four model roles. The filing texts, facts, report, and human audit sheet are in this folder.

AAPL's latest available 10-K in this run is for the fiscal year ended 2025-09-27. The report uses the 2026-10-27 close of $347.10 for P/E. The saved earnings release is Exhibit 99.1 to 8-K accession 0000320193-26-000018. Its net-sales figures are on lines 38-39, and diluted EPS is on lines 65-66.

The AAPL report's audit sheet includes the claim values and source locations. A student must still compare each claim with the filing and enter the human marks and error/missing counts. A partner conversation and the two partner checks have not been recorded here.

Command used:

```sh
./.venv/bin/python desk.py AAPL --peers MSFT --price 347.10 --price-date 2026-10-27 --price-source https://chartexchange.com/symbol/nasdaq-aapl/historical/ --model
```
