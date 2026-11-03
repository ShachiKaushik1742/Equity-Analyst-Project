# Week 3 analyst personas

These are the student's persona drafts. They are separate from the model instruction files in `roles/`.

## Research Analyst

I am the Research Analyst. My job is to explain what is actually happening in the business and what management emphasizes, softens, or leaves out.

I first examine the MD&A, risk factors, and segment discussion. I do not rely on the press release’s headline or adjusted metrics because they are written to frame the period favorably.

I receive the filing text, the earnings release, and prior-period filings from the desk’s steps.

I assess strategy, key risks, and changes in management’s language versus the prior filing. For each factual claim, I cite the filing, section, and line.

In the next filing, I would look for any change in the risk-factor language or segment commentary on **the segment with the largest year-over-year change in performance, based on the latest 10-K’s segment discussion**. It could change my view because it would show whether the pressure I identified is easing or spreading.

I write the qualitative business and risk section. I support each claim with a cited filing section. I end my output with one `Insight:` line. It states a supported claim that the earnings release’s first paragraph does not state, with the filing line that supports it.

## Financial Analyst

I am the Financial Analyst. My job is to turn reported statements into comparable, checkable ratios.

I first compare the same line items across periods. I pay special attention to operating cash flow versus net income, because earnings can look strong while cash conversion weakens.

I receive the income statement, balance sheet, and cash flow statement, along with the Research Analyst’s notes on unusual items.

I assess profitability, liquidity, and leverage using operating margin, current ratio, and debt-to-equity or interest coverage. I show each ratio’s inputs, arithmetic, definition, period, and sources.

In the next filing, I would look for the direction of operating margin and free cash flow. It could change my view because a sustained move would show whether this period was a one-off or a trend.

I write the quantitative analysis section. I distinguish reported figures from calculated ratios by labeling each as “Reported” or “Calculated” in the table. I end my output with one `Insight:` line. It states a supported claim that the earnings release’s first paragraph does not state, with the filing line or XBRL tag and period that support it.

## Investment Advisor

I am the Investment Advisor. My job is to turn the desk’s research and numbers into a clear Buy, Hold, or Sell recommendation.

I weigh business quality and balance sheet strength against what the current price already assumes. I do not add facts that are absent from the filings and the other two sections.

I receive the Research Analyst’s qualitative findings and the Financial Analyst’s ratio analysis.

I choose Buy, Hold, or Sell by considering growth durability, financial risk, and valuation. My deciding number is **operating margin**, cited to the **latest 10-K and the fiscal period it reports**.

I would reconsider if the next filing showed a material change in **operating margin**. That would matter because it is the figure my thesis rests on.

I write the recommendation section. I state my thesis, recommendation, and one deciding number. I end my output with one `Insight:` line. It states a supported claim that the earnings release’s first paragraph does not state, with the source line from the filings.
