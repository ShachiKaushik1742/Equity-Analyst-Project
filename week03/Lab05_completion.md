# Lab 05 — Make the team yours

This tracker separates saved evidence from partner work and student activities. Shachi confirms that the spoken reflection and three-person team formation are complete. Those two activities are recorded from her report.

## Saved work

- The CrewAI Flow implementation is in [`../week03_crewai_flow.py`](../week03_crewai_flow.py); the Streamlit page is [`../app.py`](../app.py).
- The Streamlit AppTest completed with zero exceptions. The partner's actual use of the page is not recorded.
- The offline verifier tests pass: `.venv-crewai/bin/python -m unittest tests/test_week03_verifier.py` (30 tests).
- The completed UBER run on the partner's ticker and peers is [`../runs/UBER_20261108_184111/`](../runs/UBER_20261108_184111/). It saved all three filings and facts for UBER, AMD, YUM, DUOL, and PLTR. The final Verifier marked 32/32 ledger claims correct. Its Manager initially returned `FAIL` for Future Developments and Strategic Recommendations. The run retried the Financial Analyst, but an earlier routing bug did not also retry the Manager. Therefore, this run is evidence of the data and verifier checks, but it does not prove that the Manager passed after its one retry.
- The routing bug is fixed in the local Flow code. A later UBER test attempt stopped during the Research Analyst call. It produced no report or verified report.
- The three role personas are in [`personas.md`](personas.md), revised from Shachi's draft. The course says the student must write these in their own words, so Shachi must review and make the final wording choices.
- The ASD-STE100 request scaffold is [`../prompts/lab-05-asd-ste100-draft.md`](../prompts/lab-05-asd-ste100-draft.md). It is labeled AI-assisted. Shachi must personalize the final prompt in her own words before use.
- The partner worksheet is [`Lab05_partner_check.md`](Lab05_partner_check.md). It has two claims and their saved filing sources. The partner must enter their own marks, corrections, name, initials, and date.
- Shachi confirms that the spoken reflection and team formation are complete. No team member names are recorded here.

## Work still needed

- Run UBER with AMD, YUM, DUOL, and PLTR after the local Manager retry fix. Confirm the Manager retries every failing part once, passes, and the final Verifier runs on all claims.
- Have the partner use the Streamlit page for the UBER run and open one Insight source line in the saved filing.
- Have the partner check the two prepared claims in [`Lab05_partner_check.md`](Lab05_partner_check.md). The partner must enter the marks and sign their own work.
- Review and personalize the personas and ASD-STE100 request. The course requires these in the student's own words.
- Work one item from the gap list in a second AI chat while the run is active. This is not collected, but it is a class activity. A useful gap to investigate is what drove the change in Uber's operating cash flow and whether it came from recurring operations or working capital.
- Confirm whether the Checkpoint 2 commit was submitted in Brightspace. GitHub main has the team and seeded-error evidence at commit `8ff0fca36410352088ae11a59466d178c046fec5`; Brightspace status is not available here.

## Checkpoint 2 commit

If it has not already been submitted, use this commit permalink in Brightspace: <https://github.com/ShachiKaushik1742/Equity-Analyst-Project/commit/8ff0fca36410352088ae11a59466d178c046fec5>.
