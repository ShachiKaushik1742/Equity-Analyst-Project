# Week 2 prompt: equity research desk data pipeline

Build the data part of an equity research desk in Python. Use Section 3.1 of Francis and Zhang (2026) as a guide. Do not add model roles yet.

Read `SEC_USER_AGENT` from the `.env` file in this folder. Send this value with every SEC request.

The program must accept:

- A ticker as a required argument.
- `--peers` as an optional list of ticker symbols.
- `--price` as an optional share price.
- `--step` as an optional number from 1 to 7. When this option is set, run that step only.

Do not name a specific company in the code.

Print each of these seven steps as it runs:

1. **Resolve the ticker.** Read SEC’s `company_tickers.json` file. Find the company’s CIK.

2. **Select the filings.** Use the EDGAR submissions API to list the company’s filings. Select the latest 10-K, the latest 10-Q, and the latest 8-K that reports Item 2.02, the earnings release. For each filing, print its accession number and the “Accepted” time from its EDGAR index page.

3. **Save the filing text.** Download the three selected documents. For the 8-K, use Exhibit 99.1 for the earnings release. Convert each document to plain text. Save the text files in a folder named with the company, date, and run time.

4. **Read and save the XBRL facts.** Fetch the company’s XBRL facts. For the latest fiscal year, print:
   - Total revenue
   - Operating income
   - Net income
   - Diluted EPS
   - Stockholders’ equity
   - Long-term debt and its current portion
   - Cash from operations
   - Additions to property and equipment

   For each fact, print its tag, period end, and filing. Select the candidate tag with the newest latest-year period. Use the same fiscal year as revenue for every concept. Show the prior-year value beside each latest-year value.

5. **Calculate the ratios.** Write the calculations in code. Print the formula and result for each item:
   - Revenue growth
   - Operating margin
   - Return on average equity
   - Debt to equity, including the current portion of debt
   - Free cash flow: cash from operations minus additions to property and equipment
   - P/E, using `--price`

6. **Read the earnings release.** From the release text, print the lines that report quarterly total revenue and diluted EPS.

7. **Read peer facts.** For each ticker in `--peers`, print the same facts and calculate operating margin using the same definition.

Save the facts beside the filing text files.

When the program is complete, provide:

- The exact command to install any required packages.
- The exact command to run the program with a ticker, peers, and share price.
