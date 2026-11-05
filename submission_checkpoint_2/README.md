# Checkpoint 2 submission index

This repository contains the Week 3 agent team, student-provided analyst personas, and verifier evidence. The application uses CrewAI Flow with `Process.sequential`; the graph fixes the order, and the Verifier always runs after the Strategy Manager.

## Required evidence

- [Agent-team implementation](../week03_crewai_flow.py)
- [Deterministic and SEC audit checks](../week03_audit_helpers.py)
- [Three student-provided analyst personas](../week03/personas.md)
- [Role instruction files](../roles/)
- [Framework, graph, commands, and evidence map](../week03/README.md)
- [Week 3 completion record](../week03/Lab04_completion.md)
- [Clean COST report: all three insight lines; one Manager repair; 27/27 claims correct](../runs/COST_20261104_151441/verified_report.md)
- [Seeded EPS error: marked wrong and corrected to $20.76](../runs/COST_20261103_140000_seed_eps/verified_report.md)
- [Seeded growth error: marked wrong and recalculated to 10.14%](../runs/COST_20261103_140001_seed_growth/verified_report.md)
- [Invented number: marked unsupported](../runs/COST_20261103_185432_seed_invented/verified_report.md)
- [Offline verifier tests](../tests/test_week03_verifier.py)

## Lab 05 work in progress

- [Lab 05 completion and outstanding partner/student actions](../week03/Lab05_completion.md)
- [Local Streamlit interface](../app.py)
- [COST Lab 05 run with three sourced insights and 30/30 verifier marks](../runs/COST_20261105_180611/verified_report.md)
- [Blank partner review worksheet](../week03/Lab05_partner_check.md)
- [AI-assisted ASD-STE100 prompt draft, awaiting the student's own rewrite](../prompts/lab-05-asd-ste100-draft.md)

The complete saved runs include filing texts, facts, node inputs and outputs, claims, verifier marks, and reports. The repository excludes `.env` and API keys. Lab 05 is not fully partner-complete: the partner-selected ticker and their two manual claim checks must be added before the partner review can be marked complete.

## Brightspace

Submit the permalink to this repository's `submission_checkpoint_2` folder or the repository itself, according to the course submission field. The repository's `main` branch must contain the files above before you submit the link.
