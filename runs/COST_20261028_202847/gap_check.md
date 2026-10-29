# Gap check: FY2026 COST revenue fact

**Question:** Does the selected XBRL revenue fact match Costco's FY2026 total revenue in the 10-K?

**Result:** Yes. `COST_facts.json` selects `RevenueFromContractWithCustomerExcludingAssessedTax` for 2025-09-01 through 2026-08-30, from 10-K accession `0000909832-26-000093`. The value is $303,154 million. The saved 10-K income statement reports $297,247 million in net sales plus $5,907 million in membership fees, for total revenue of $303,154 million. The prior-year total is $275,235 million.

**Period note:** Costco FY2026 is a 52-week fiscal year ending August 30, 2026. It is not a calendar year.

**Evidence:** `COST/COST_facts.json` and `COST/10K_0000909832-26-000093.txt` in this run folder.
