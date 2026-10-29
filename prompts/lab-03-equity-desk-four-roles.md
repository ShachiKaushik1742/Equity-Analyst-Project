# Week 3 prompt: add four analyst roles to the equity desk

Extend the Python equity-research desk in this project. Keep its seven data steps and add the four roles in Figure 1 of Francis and Zhang (2026), *Can AI Match Professional Analysts? Evidence from a Multi-Agent System*. The paper describes a role-based report workflow. Keep the roles separate and preserve the handoffs below. Do not replace the seven data steps with model-generated research.

Use the existing prompt `prompts/lab-02-equity-desk-data-pipeline.md` and the current desk code as the specification for the seven data steps. Keep their behavior, command-line options, filing checks, saved facts, and run folder. Do not name a company in the code.

## Provider setup

Use one official Python SDK: OpenAI, Anthropic, or Google GenAI. Use the provider that fits the project's existing Purdue GenAI Studio setup. State which provider and model the code uses. Read `API_KEY` from `.env` in this folder. Read any required provider or model setting from `.env`, or use a documented default. Do not print, log, save in a report, or commit the key. Do not put the key in source code. Load `.env` without changing existing SEC settings. If the chosen provider needs a compatible API base URL, read it from configuration and document it.

## Calls and role boundaries

Make a separate model call for each role. Give each role its own system instructions. A role can use only the information that the Strategy Manager includes in that role's input. Send each role input as JSON with exactly these top-level fields: `task`, `context`, and `expected_output`. Do not give a role the complete run folder or another role's private context.

The Strategy Manager controls the workflow. It selects the evidence and sends the role-specific JSON. The Research Analyst and Financial Analyst work from the filing data that the Strategy Manager sends them. The Investment Advisor receives only the Research Analyst and Financial Analyst outputs. The Strategy Manager receives the role outputs that it needs to check and compile the report. Keep the seven data steps and all source material available to the Strategy Manager so it can provide the right evidence to each role.

The four roles are:

1. **Research Analyst.** Describe the business model, competitive position, catalysts, and recent developments. Use the 10-K Business and MD&A sections and the earnings release. Support each factual claim with a short direct quote and its source. Give the filing, section, and line number from the saved plain-text filing. Preserve stable line numbers when the program creates the plain-text files. Do not invent a line number or a quote. If the source does not support a claim, say so.

2. **Financial Analyst.** Interpret the facts from Step 4, the code-calculated ratios from Step 5, the quarter facts from Step 6, and peer facts from Step 7. Give each number its filing and either its filing line or XBRL tag, unit, period, and accession. Show the arithmetic for each ratio. State the definition used when a filing offers two possible definitions, such as net sales and total revenue. Do not calculate arithmetic in the model. If the role requests an additional ratio, send a structured request to a deterministic code calculator. The code must calculate it from supplied inputs and return the formula and result. Never evaluate model-provided code or a free-form formula.

3. **Investment Advisor.** Write an investment thesis and choose Buy, Hold, or Sell. Name one deciding number. Use only the Research Analyst and Financial Analyst outputs sent by the Strategy Manager. Do not add facts, calculations, or claims from another source. If those outputs do not support a recommendation, say what evidence is missing.

4. **Strategy Manager.** Check that the report has all five parts: Overview; Market Positioning and Growth Outlook; Valuation Insights; Future Developments and Strategic Recommendations; Investment Recommendation. Check that all parts refer to the same company and do not contradict each other. Check that claims use the supplied evidence and that periods and definitions are clear. If a part fails, send that part back to its responsible role once, with a concise repair request and only the evidence needed for the repair. Then compile the report. Do not add unsupported facts. If a repaired part still fails, report the issue clearly instead of claiming that it passed.

Map the report parts to the role outputs as follows: use filing metadata and company facts for Overview; use Research Analyst output for Market Positioning and Growth Outlook; use Financial Analyst output for Valuation Insights; use supported research and financial findings for Future Developments and Strategic Recommendations; and use Investment Advisor output for Investment Recommendation. The Strategy Manager may edit for consistency and format, but it must preserve the evidence and meaning of the role outputs.

## Run behavior and report

Print each role's name when its call starts. Also print a clear error if provider setup or a model call fails. Do not print the API key or other secret values.

Save the final report as Markdown in the current run's folder. Its first line must list the filings read and their accession numbers. Its second line must show the run time. Print the report path when the run is complete. Preserve the existing output files and human-audit template.

Use the provider's official SDK. Add only the required dependencies to the install instructions. Keep provider and model configuration out of source code. Do not commit `.env` or secrets.

When the code is complete, give me:

- The exact command to install the required packages.
- The exact command to run the desk on a ticker with peers and a share price.
- A short note that says which provider and model configuration I must set in `.env`.

Include `--model` in the run command so that it runs the four roles after the seven data steps.

Paper reference: Francis, A., & Zhang, C. X. (2026). *Can AI match professional analysts? Evidence from a multi-agent system*. Finance Research Letters, 103, 110127. https://doi.org/10.1016/j.frl.2026.110127
