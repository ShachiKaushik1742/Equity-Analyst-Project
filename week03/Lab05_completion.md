# Lab 05 — Make the team yours

This record tracks the local work for Lab 05. It does not claim that a partner completed the partner review or that in-class discussions took place.

## Completed locally

- The equity desk has a Streamlit page in the repository root. It accepts a ticker, optional peers, and optional price; it displays the node progress and the saved verified report. The page passed `AppTest`.
- The Insight verifier now makes a separate mark for each analyst, follows citations into peer filing folders, and accepts a USD conversion only when the cited statement context specifies the scale (for example, “Amounts in millions”). Typographic spaces and accession dashes in citations are normalized.
- The offline verifier suite passes 20 tests: `.venv-crewai/bin/python -m unittest tests/test_week03_verifier.py`.
- The desk was rerun on COST with peers WMT, TGT, and BJ, using the prior Lab 03 close of $992.13 dated 2026-10-27. The run folder is `../runs/COST_20261105_180611/`; the required Verifier ran and marked **30/30** claims correct, including each of the three Insight lines. The Strategy Manager passed without a repair. The saved report and marks are in `../runs/COST_20261105_180611/verified_report.md`.
- The partner-review worksheet is ready at [Lab05_partner_check.md](Lab05_partner_check.md). It has no marks entered.
- An AI-assisted ASD-STE100 prompt draft is saved at [lab-05-asd-ste100-draft.md](../prompts/lab-05-asd-ste100-draft.md). Lab 05 asks the student to rewrite the prompt; this draft is not represented as student-authored.

## Still needs student or partner work

- Run the desk on the company selected by the partner, after the ticker is confirmed. The partner must then select and check two claims against that run’s saved filing texts and facts, enter their own marks and corrections in the worksheet, and identify themselves.
- The student must rewrite and approve the ASD-STE100 prompt in their own words before using it.
- Complete and record any Lab 05 class activity that has not already been done, including the second-chat gap-list item and the spoken reflection/team discussion. This file does not mark those as complete.
- Submit the required Checkpoint 2 repository or folder permalink on Brightspace.
