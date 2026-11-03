# FIN 67110 equity research desk

The repository contains the SEC data desk and the Week 3 agent-team implementation. The data pipeline reads SEC filings and XBRL facts. The agent team uses the OpenAI Agents SDK and a fixed Python sequence; the Verifier always runs after the Strategy Manager.

## Setup

Use Python 3.14 or newer supported by the project dependencies, then install:

```sh
python3 -m pip install -r requirements.txt
```

Set `SEC_USER_AGENT` and the Purdue GenAI Studio key (`API_KEY`, or the existing `PURDUE_GENAI_API_KEY`) in the local `.env` file. The program discovers an available model when `GENAI_MODEL` is not set. Never commit `.env`.

## Run the agent team

```sh
python3 week03_agent_team.py COST --peers WMT,TGT,BJ --price 999.99
```

Replace `999.99` with the closing price from the Lab 03 run. The program saves a new timestamped run folder under `runs/`. To verify a saved run without rerunning the data steps or analyst roles:

```sh
python3 week03_agent_team.py --verify-only runs/COST_YYYYMMDD_HHMMSS
```

See [Week 3 notes and design](week03/README.md), [reading sources](week03/readings.md), and the role contracts in [`roles/`](roles/).
