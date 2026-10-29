# FIN 67110 — Week 2 prep and lab notes

Prepared: 2026-10-28

## What the desk does

Figure 1 is a **workflow**: code fixes the sequence, role prompts, hand-offs, and one retry. The model writes within each assigned role; it does not choose the next step or select tools.

EDGAR supplies the filing list, annual 10-K, quarterly 10-Q, current 8-K and its earnings-release exhibit, and XBRL company facts. The calculator is local code. XBRL records a concept/tag, period, unit, and filing, so a tag name alone is not enough to identify a comparable number.

The greatest source risk is Step 4: selecting a tag and period that match the filing's definition and fiscal year. Costco illustrates the definition trap: FY2026 total revenue is $303,154 million, consisting of $297,247 million net sales plus $5,907 million membership fees. The release's $297.2 billion headline is net sales, not total revenue. I would trust a number only after checking its XBRL tag, period, accession, and statement line.

The four roles need the same ticker-specific filing evidence, numeric facts and periods, arithmetic supplied by the calculator, release rows for quarterly revenue and GAAP diluted EPS, and peer facts on a named revenue definition. A partner's company must run through the same ticker argument without a company name fixed in the code.

## What the readings say

The course's Kim, Muhn, and Nikolaev prompt points to a 2024 working-paper version. That version reports 60.35% directional accuracy for its chain-of-thought GPT condition versus 52.71% for the one-month analyst benchmark. The paper used historical U.S. firm-year data and standardized financial statements. The apparent edge could shrink on unseen firms or years if industries, accounting, macro conditions, or the distribution of earnings changes differ from the historical sample.

**Version caveat:** arXiv currently marks the paper withdrawn. The authors' note says a co-author found inconsistencies in data and analyses during replication. Treat the reported performance as a result from the earlier draft, not a settled fact, until the authors resolve the issue. The course page and the earlier PDF remain the assigned materials.

Anthropic's Financial Services repository says its agents draft work for review. They do not make investment recommendations or execute trades, bind risk, post to a ledger, or approve onboarding. Its examples include named workflows, financial skills, and data connectors; this desk has a fixed SEC workflow and requires the human to audit the report.

## Lab results

- Costco pipeline: completed Steps 1–7 for COST and peers WMT, TGT, and BJ. It selected each latest 10-K, 10-Q, and 8-K with Item 2.02, saved the filing text and selected facts by company, calculated ratios in code, extracted the release's quarter revenue and diluted EPS rows, and calculated peer operating margins.
- WMT ticker-independence check: completed the same steps with COST, TGT, and BJ as peers. The code uses the ticker argument; its source does not hard-code Costco.
- Costco five-part report: generated with the four Purdue GenAI Studio roles and the $904.70 close on 2026-09-23, the close before Costco's 2026-09-24 earnings release. The Strategy Manager flagged the net-sales/total-revenue mismatch and triggered one Research Analyst repair. The final report now states the definition distinction.
- Purdue GenAI Studio key: authenticated successfully; `gpt-oss:120b` is available to this account.
- Human audit: the template is ready, but the report marks and the error/missing counts remain blank for the student's hand-check against the filing lines. No AI-filled marks are included.

## Re-run commands

```sh
.venv/bin/pip install -r requirements.txt
.venv/bin/python desk.py COST --peers WMT,TGT,BJ --price 904.70 --price-date 2026-09-23 --price-source https://stockanalysis.com/stocks/cost/history/ --model
```

## Sources and saved work

- [Week 2 course page](https://cinderzhang.github.io/FIN67110-Fall2026/week-02/index.html)
- [Lab 02](https://cinderzhang.github.io/FIN67110-Fall2026/week-02/lab-02-desk-on-one-page.html)
- [Lab 03](https://cinderzhang.github.io/FIN67110-Fall2026/week-02/lab-03-make-it-yours.html)
- [Report audit checklist](https://cinderzhang.github.io/FIN67110-Fall2026/reference/audit-checklist.html)
- [Kim et al. withdrawn arXiv record](https://arxiv.org/abs/2407.17866) and [version 2 PDF](https://arxiv.org/pdf/2407.17866v2)
- [Anthropic Financial Services repository](https://github.com/anthropics/financial-services)
- Costco report and human-audit template: `runs/COST_20261028_201235/`
- Walmart ticker check: `runs/WMT_20261028_201551/`
