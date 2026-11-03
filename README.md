# FIN 67110 equity research desk

The repository contains the SEC data desk and its Week 3 CrewAI implementation. A CrewAI Flow controls the fixed application process. Each specialist runs in a Crew with `Process.sequential`; the Strategy Manager can request one repair, and the Verifier always runs last.

## Setup

CrewAI 1.15.34 supports Python 3.10 through 3.13. Create an isolated Python 3.13 environment with `uv`:

```sh
python3 -m pip install uv
uv python install 3.13
uv venv --python 3.13 .venv-crewai
uv pip install --python .venv-crewai/bin/python -r requirements.txt
```

Set `SEC_USER_AGENT` and the Purdue GenAI Studio key (`API_KEY`, or the existing `PURDUE_GENAI_API_KEY`) in the local `.env` file. Set `GENAI_MODEL` to a model available in Purdue GenAI Studio if automatic model discovery is not available. Never commit `.env`.

## Run the agent team

```sh
.venv-crewai/bin/python week03_crewai_flow.py COST --peers WMT,TGT,BJ --price 999.99
```

Replace `999.99` with the closing price from the Lab 03 run. The program saves a timestamped run folder under `runs/`. Run offline verification tests with:

```sh
.venv-crewai/bin/python -m unittest tests/test_week03_verifier.py
```

See [Week 3 notes and design](week03/README.md), [reading sources](week03/readings.md), and the role contracts in [`roles/`](roles/).
