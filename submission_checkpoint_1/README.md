# Checkpoint 1 submission packet

**Status: prepared, pending required student and partner verification.** Do not submit this packet as complete until the open items below are finished.

## What Checkpoint 1 asks you to submit

Lab 03 says to submit in Brightspace a **permalink (commit link)** to the repository that contains the desk and a report on the partner's company. A fallback report counts if the desk or model provider does not run. The lab also calls for a hand audit of the COST report, and the partner must check two core claims of the partner-company report against its filings.

## Packet contents

- `desk.py`, `requirements.txt`, `.env.example`, and `SETUP.md`: the desk, dependencies, and setup instructions. The real `.env` and API key are intentionally excluded.
- `runs/COST_20261028_211550/`: COST four-role report, all filing and peer text/facts, human-audit worksheet, and reflection/status note.
- `COST_step_verification.md`: evidence for the seven data steps against the known Costco filings.
- `XBRL_and_partner_reflection.md`: prepared Week 2 XBRL explanation and reflection.
- `runs/WMT_20261028_201551/`: WMT data-side run and its filing evidence. The model roles were not run on WMT; this run is the Week 2 data-pipeline exercise.
- `runs/MSFT_20261028_214246/`: the original MSFT/AAPL run, source filings, facts, price log, and original model-generated report/audit evidence.
- `MSFT_partner_report.md`: a citation-corrected, completed report draft assembled from the MSFT model-role output and saved filing evidence. It fixes the truncated Analyst paragraphs and the competition-section attribution in the original draft. Review it against the source files before using it.
- `MSFT_partner_audit.md`: the filing-evidence worksheet for the corrected MSFT report. Its human marks and partner fields are blank.

## Still required before you submit

1. **Complete the COST hand audit.** Compare the 11 core claims, other Financial Analyst numbers, report sections, and recommendation in `runs/COST_20261028_211550/COST_report.md` with the source filings. Fill its human-mark column and count wrong/unsupported claims and missing claims.
2. **Confirm the partner's pick.** MSFT was used as the second company at your request, and its latest earnings 8-K was filed October 28, 2026. The lab says the partner picks the company. Ask your partner to confirm MSFT is their pick; if it is not, run their ticker instead.
3. **Audit the MSFT report yourself.** Use `MSFT_partner_audit.md` and the source files in `runs/MSFT_20261028_214246/`. Enter your marks and counts. Ask your partner to check two claims and record their check in the worksheet.
4. **Submit the repository commit permalink in Brightspace.** After the final verification is recorded and pushed, use the GitHub permalink for that commit. The packet's current commit permalink is provided with the handoff message; use the newest commit if you make more changes.

The audit worksheets leave marks blank on purpose. This packet does not claim that a student or partner performed those checks.
