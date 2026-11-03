# Reconstructed Week 3 request: CrewAI Flow desk

Use **CrewAI Flows** to rebuild the equity research desk as a Python agent team. Use `Flow` for the fixed graph. Use `Process.sequential` for each role call. Keep the seven data steps as deterministic tools. Keep the instructions for each role in its own file in `roles/`.

## Run order

Run these nodes in the same order on every normal run:

1. Run the seven data steps.
2. Run the Research Analyst.
3. Run the Financial Analyst.
4. Run the Investment Advisor.
5. Run the Strategy Manager. The Manager checks the report and compiles it.
6. Run the Verifier.

The code controls this order. A model must not select the next node. The Strategy Manager may request one repair to one failed report part. Run the role that owns that part one more time. Do not run any role more than twice. Then compile the report and run the Verifier. The Verifier must run on every normal run. Do not add an option that turns it off.

## Model calls and role instructions

Make one model call for each role run. Give the role its instructions from its own file. Give it only a JSON object with `task`, `context`, and `expected_output`. Do not give it other run state.

The Strategy Manager must check that all five report parts exist and agree with each other:

- Overview
- Market Positioning and Growth Outlook
- Valuation Insights
- Future Developments and Strategic Recommendations
- Investment Recommendation

If one part fails, send only that part to its role for one repair. Then compile the report.

## Verification

Run the Verifier after the Strategy Manager and report compilation. Give it only a copy of the compiled report with the Investment Advisor thesis removed, the saved filing texts, and the saved facts. Do not ask it to judge the thesis.

For each other number that has a source, check it in code:

- Check an XBRL number against its tag and period in the saved facts. The values must match exactly.
- Check a filing-line number against the cited line in the saved filing text. Allow differences in spaces and number formatting.
- Recalculate each ratio from the inputs and formula shown with the claim.
- Check that a ratio has a definition when a filing gives more than one definition.

Then use the model to check that the cited filing line supports the number, period, and definition. Mark each claim `correct`, `wrong`, or `unsupported`. A number with no source is unsupported. A ratio with no required definition is unsupported. For every wrong or unsupported claim, give the corrected value and its actual filing line or XBRL tag when the saved sources support a correction.

## Files and command line

Read `API_KEY` from the local `.env`. Do not print, save, or commit the key. Do not name a company in the code.

Take a ticker, optional `--peers`, optional `--price`, and optional `--verify-only PATH`. With `--verify-only`, run only the Verifier on the saved run at `PATH`.

For each run, create a new folder named with the company ticker, date, and time. Do not overwrite an earlier run. Save the filing texts, facts, each node's input and output, the report, and the verified report. Put the table of verifier marks below the first line of the verified report. Keep the filings line as that first line.

Print each node's name when it starts. Give the exact package install command, an example run command with a ticker, peers, and price, and an example verify-only command with a saved run path.

## Commands

From the project root, create the Python 3.13 environment and install the packages with:

```sh
python3 -m pip install uv
uv python install 3.13
uv venv --python 3.13 .venv-crewai
uv pip install --python .venv-crewai/bin/python -r requirements.txt
```

Run a ticker with peers and price:

```sh
.venv-crewai/bin/python week03_crewai_flow.py COST --peers WMT,TGT,BJ --price 999.99
```

Verify a saved run only:

```sh
.venv-crewai/bin/python week03_crewai_flow.py --verify-only runs/COST_YYYYMMDD_HHMMSS
```
