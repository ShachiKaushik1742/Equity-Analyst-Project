# Lab 05 — Make the team yours

This tracker separates saved evidence from work reported by the students. Shachi confirms that the spoken reflection, three-person team formation, and her own final wording for the personas are complete.

## Completed work

- The CrewAI Flow implementation is in [`../week03_crewai_flow.py`](../week03_crewai_flow.py); the Streamlit page is [`../app.py`](../app.py).
- The Streamlit AppTest completed with zero exceptions. The partner's actual use of the page is not recorded.
- The offline verifier suite passes: `.venv-crewai/bin/python -m unittest tests/test_week03_verifier.py` (30 tests).
- The UBER run on the partner's chosen ticker and peers is [`../runs/UBER_20261108_184111/`](../runs/UBER_20261108_184111/). It saved the filings and facts for UBER, AMD, YUM, DUOL, and PLTR. The original Verifier marked 32/32 ledger claims correct.
- The three personas are in [`personas.md`](personas.md). Shachi confirms that the final wording she supplied is her own and complete.
- The spoken reflection and team formation are complete per Shachi.
- Gap-list item: the cash-flow analysis is in [`gap_list_work.md`](gap_list_work.md), based on UBER's 10-K lines 1086–1087 and cash-flow statement lines 1403–1423.
- Shachi reports that her partner completed the Lab 05 partner check. The local worksheet [`Lab05_partner_check.md`](Lab05_partner_check.md) and the copy on GitHub `main` still have blank marks, reviewer name, and signature. The partner's completed copy has not been saved here, so the claim is recorded as student-reported rather than file-verified.

## Manager repair status

The first Strategy Manager response failed and included unsupported targets. The one allowed repair request was recorded as `strategy_manager_attempt_2_input.json`, but the provider request timed out after 300 seconds and produced no output. A source-cited editorial fallback is saved at [`../runs/UBER_20261108_184111/nodes/manager_repair_fallback.md`](../runs/UBER_20261108_184111/nodes/manager_repair_fallback.md) and its section is in `report.md`. It is explicitly not recorded as a Strategy Manager node pass. The original verifier's 32/32 marks predate this report edit; the Manager subsection has not been re-verified by the Verifier node.

## Still to confirm

- Save the partner's completed worksheet in this folder. The GitHub `main` copy is blank, and there is no Lab 05 partner-review branch or pull request.
- Complete a successful Strategy Manager retry and run the Verifier again after the report update. The retry output and updated verifier result must be saved before calling this part complete.
- The gap-list write-up is complete here. The separate-chat class activity was not performed in a second chat, so this tracker does not claim that it was.
- Confirm whether the Checkpoint 2 commit was submitted in Brightspace; that status is not available in this workspace.

## Checkpoint 2 commit

The previously pushed commit is [7ba605f](https://github.com/ShachiKaushik1742/Equity-Analyst-Project/commit/7ba605f). Confirm the required commit permalink was submitted in Brightspace.
