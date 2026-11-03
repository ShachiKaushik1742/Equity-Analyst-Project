# Lab 04 — completion record

This file records saved work for Lab 04 and the student's confirmation of class work.

## Built and tested

- The desk now uses a CrewAI Flow and `Process.sequential`. The Flow fixes the node order in code and always runs the Verifier after the Strategy Manager.
- The Flow ran twice on COST with peers WMT, TGT, and BJ and the Lab 03 price of $992.13. The runs are `runs/COST_20261103_131437/` and `runs/COST_20261103_131635/`; both record the same node order and separate run folders.
- The clean COST report passed **27/27** checks. This includes all 11 core claims: nine fiscal-year facts and the two quarter claims. See `runs/COST_20261103_131635/verified_report.md`.
- The seeded EPS copy changed annual diluted EPS from $20.76 to $21.76. The Verifier marked that claim **wrong** and corrected it to **$20.76**, citing 10-K accession `0000909832-26-000093`, line 638. See `runs/COST_20261103_140000_seed_eps/verified_report.md`.
- The seeded growth copy states 14.14% using the correct quoted figures, $303,154 million and $275,235 million. The Verifier marked it **wrong** and recalculated `(303,154 / 275,235) - 1 = 10.14%`. See `runs/COST_20261103_140001_seed_growth/verified_report.md`.
- `--help` exposes `--verify-only` and has no flag to skip or disable the Verifier. Normal runs call the Verifier after report compilation. The deterministic test suite passes **14 tests**.
- The Verifier now sends cited line excerpts from the saved filings, plus the saved facts, to the model. Full filing texts remain in each run folder. This keeps the call within the selected model's context limit.

## Partner verification

**Complete — partner confirmed on 2026-11-03.** Mrunalini Pol (MP) confirmed in Teams that she checked COST revenue against Form 10-K line 625 and the seeded EPS correction against line 638, marked both checks RIGHT, and signed with her name and initials. Her separate completed worksheet was not in this folder and her message said it had not been sent to the repository. The local [partner check worksheet](Lab04_partner_check.md) records her reported marks and clearly identifies the Teams message as their source; it does not claim that a PR was merged.

## Student class work

**Complete — student confirmed on 2026-11-03.** The student reports completing the paired review, working on one gap-list item in a second AI chat, and discussing the Lab 04 reflection questions with their partner. These are recorded as student-completed based on that confirmation; the worksheet below remains for the partner's independent written marks.

## Before Session 5 preparation

**Complete — student confirmed on 2026-11-03.** The student reports completing the Week 3 preparation list linked from the Lab 04 page.
