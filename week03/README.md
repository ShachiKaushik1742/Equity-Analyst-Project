# Week 3 agent team

This folder records the Week 3 reading notes and the CrewAI implementation for the equity desk.

## Framework choice

The application uses CrewAI 1.15.34 with a typed `Flow` for the fixed process and `Process.sequential` inside each role crew. The Flow owns the order, run state, manager decision, one repair route, and final verifier. Current CrewAI requires Python below 3.14, so use Python 3.13.

## Install and run

From the repository root:

```sh
python3 -m pip install uv
uv python install 3.13
uv venv --python 3.13 .venv-crewai
uv pip install --python .venv-crewai/bin/python -r requirements.txt
```

Run a ticker and its peers with a price:

```sh
.venv-crewai/bin/python week03_crewai_flow.py COST --peers WMT,TGT,BJ --price 999.99
```

The `.env` file must contain `SEC_USER_AGENT` and your Purdue key as `API_KEY` (the existing `PURDUE_GENAI_API_KEY` name also works). You can set `GENAI_MODEL`; otherwise the program lists the available models and selects one. `GENAI_API_BASE` can set Purdue's OpenAI-compatible endpoint. Never commit `.env`.

## Flow and process

```mermaid
flowchart LR
  A[Seven SEC data steps] --> B[Research Analyst Crew]
  B --> C[Financial Analyst Crew]
  C --> D[Investment Advisor Crew]
  D --> E[Strategy Manager Crew]
  E -->|PASS| G[Verifier Crew]
  E -->|One repair| F[Repair Crew]
  F --> G
  G --> H[Verified report and marks]
```

Flow decorators control the end-to-end order and repair branch. Each role runs with its own JSON input envelope in an isolated Crew whose task process is `Process.sequential`. Each role receives only its assigned context. The Verifier always runs after the manager or the one repair.

## Persona work

The course says students must write the three analyst personas in their own words. The `roles/` files preserve the Lab 03 role boundaries as a starting contract. Replace their text with your own persona writing for Lab 05; this project does not claim that AI wrote your personal personas.

## Readings

See [readings.md](readings.md). The repository stores citations and short original notes, not copies of copyrighted articles or publisher PDFs.
