# Lab 04 — completion record

This file records saved work for Lab 04. It does not mark the partner check or spoken class work as complete.

## Built and tested

- The desk now uses a CrewAI Flow and `Process.sequential`. The Flow fixes the node order in code and always runs the Verifier after the Strategy Manager.
- The Flow ran twice on COST with peers WMT, TGT, and BJ and the Lab 03 price of $992.13. The runs are `runs/COST_20261103_131437/` and `runs/COST_20261103_131635/`; both record the same node order and separate run folders.
- The clean COST report passed **27/27** checks. This includes all 11 core claims: nine fiscal-year facts and the two quarter claims. See `runs/COST_20261103_131635/verified_report.md`.
- The seeded EPS copy changed annual diluted EPS from $20.76 to $21.76. The Verifier marked that claim **wrong** and corrected it to **$20.76**, citing 10-K accession `0000909832-26-000093`, line 638. See `runs/COST_20261103_140000_seed_eps/verified_report.md`.
- The seeded growth copy states 14.14% using the correct quoted figures, $303,154 million and $275,235 million. The Verifier marked it **wrong** and recalculated `(303,154 / 275,235) - 1 = 10.14%`. See `runs/COST_20261103_140001_seed_growth/verified_report.md`.
- `--help` exposes `--verify-only` and has no flag to skip or disable the Verifier. Normal runs call the Verifier after report compilation. The deterministic test suite passes **14 tests**.
- The Verifier now sends cited line excerpts from the saved filings, plus the saved facts, to the model. Full filing texts remain in each run folder. This keeps the call within the selected model's context limit.

## Partner action still required

Please send [Lab04_partner_check.md](Lab04_partner_check.md) to your partner. They must open the seeded EPS verified report and the COST 10-K at line 638, independently check the Verifier's mark, and fill in the name, mark, evidence, initials, and date in that worksheet. The worksheet is intentionally unsigned and blank for the partner.

## Student class work still required

These items require your own participation or explanation. I have not recorded them as completed:

- In the paired review, show your partner the source for one number and let them find it in the filing.
- Use the second AI chat to work on one item from your gap list.
- Explain to your partner what code now decides about role order and one thing the Verifier cannot check by design (the Investment Advisor's thesis is omitted).
- Discuss which Anthropic patterns fit the Manager and Verifier, what the Verifier receives, and why it does not receive role instructions.

The last topic is discussion work; the saved runs and worksheets do not prove that the conversation happened.
