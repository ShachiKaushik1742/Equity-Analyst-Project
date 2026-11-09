# Lab 05 — Make the team yours

This tracker records saved evidence and student-reported activities separately. Shachi confirms that her spoken reflection, team formation, and own final wording for the personas are complete.

## Completed work

- The CrewAI Flow implementation is in [`../week03_crewai_flow.py`](../week03_crewai_flow.py); the Streamlit page is [`../app.py`](../app.py).
- The Streamlit AppTest completed with zero exceptions. The partner's actual use of the page is not recorded here.
- The offline verifier suite passes: `.venv-crewai/bin/python -m unittest tests.test_week03_verifier.py` (33 tests).
- The final UBER run on the partner-selected ticker and peers is [`../runs/UBER_20261108_202611/`](../runs/UBER_20261108_202611/). It saved filings and facts for UBER, AMD, YUM, DUOL, and PLTR.
- The Strategy Manager returned `PASS`; the code router selected `approve_report`, so no role retry was needed. See [`choose_manager_path_input.json`](../runs/UBER_20261108_202611/nodes/choose_manager_path_input.json) and [`choose_manager_path_output.json`](../runs/UBER_20261108_202611/nodes/choose_manager_path_output.json).
- The Verifier ran automatically after the Manager and marked all 32 claims correct. See [`verified_report.md`](../runs/UBER_20261108_202611/verified_report.md) and [`verification_marks.json`](../runs/UBER_20261108_202611/verification_marks.json).
- The three student-authored personas are in [`personas.md`](personas.md). Shachi confirms that her final wording is her own and complete.
- The spoken reflection and three-person team formation are complete per Shachi.
- The written gap-list answer is in [`gap_list_work.md`](gap_list_work.md), using UBER's 10-K evidence. It analyzes operating cash flow, net income, and working capital.

## Still to confirm or complete

- The local partner worksheet [`Lab05_partner_check.md`](Lab05_partner_check.md) still has blank review marks and reviewer signature. Shachi said she will handle the partner check; save the completed copy here when received.
- The written gap-list answer is saved, but the separate-chat activity is not independently evidenced in this workspace.
- Confirm whether the Checkpoint 2 commit permalink was submitted in Brightspace; that submission status is not available here.

## Checkpoint 2 commit

The previously pushed commit is [7ba605f](https://github.com/ShachiKaushik1742/Equity-Analyst-Project/commit/7ba605f). Confirm the required commit permalink was submitted in Brightspace.
