import json
import tempfile
import unittest
from pathlib import Path

import desk
from week03_audit_helpers import (calc_expected_ratio, code_verify_claims,
                                  cited_filing_evidence, financial_amount_audit, financial_period_audit,
                                  analyst_insight_audit, enrich_insight_source_lines, insight_claims, insight_values_supported, omit_report_part,
                                  percentage_claim_audit, verifier_report_copy,
                                  save_verified_report)


class VerifierTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.run = Path(self.temp.name)
        (self.run / "COST").mkdir()
        (self.run / "COST" / "COST_facts.json").write_text(json.dumps({
            "facts": {"diluted_eps": {
                "value": 17.95, "tag": "EarningsPerShareDiluted",
                "period_end": "2026-08-30", "accession": "0000000000-26-000001"
            }}
        }))
        (self.run / "COST" / "8K_0000000000-26-000001.txt").write_text("Total revenue 92,279\n")

    def tearDown(self):
        self.temp.cleanup()

    def test_earnings_release_selector_handles_sec_truncated_filename(self):
        files = [
            {"name": "uber-20261104.htm", "type": "text.gif"},
            {"name": "uberq326earningspressrelea.htm", "type": "text.gif"},
            {"name": "uber-20261104.xsd", "type": "text.gif"},
        ]
        self.assertEqual(desk.earnings_release_document(files), "uberq326earningspressrelea.htm")

    def test_earnings_release_selector_accepts_exhibit_99_1_names(self):
        files = [{"name": "primary.htm"}, {"name": "exhibit_99_1.htm"}]
        self.assertEqual(desk.earnings_release_document(files), "exhibit_99_1.htm")

    def test_earnings_release_selector_accepts_numbered_exhibit_filename(self):
        files = [{"name": "amd-20261103.htm"}, {"name": "q32026991.htm"}]
        self.assertEqual(desk.earnings_release_document(files), "q32026991.htm")

    def test_earnings_release_selector_uses_sec_index_exhibit_type(self):
        files = [{"name": "primary.htm"}, {"name": "duolingo-release.htm"}]
        index_text = ("Seq Description Document Type Size\n"
                      "1 8-K duol-20261103.htm iXBRL 8-K 27254\n"
                      "2 EX-99.1 q3fy26duolingo9-30x26xpres.htm EX-99.1 10331")
        self.assertEqual(desk.earnings_release_document(files, index_text),
                         "q3fy26duolingo9-30x26xpres.htm")

    def test_quarter_metrics_ignores_revenue_narrative_and_orders_years(self):
        release = """Uber Announces Results for Third Quarter 2026
Revenue grew 10% YoY to $14.8 billion.
Financial and Operational Highlights
Three Months Ended September 30,
(In millions, except percentages and per share amounts) 2025 2026 % Change
Revenue $ 13,467 $ 14,766 10 %
GAAP Diluted EPS $ 3.11 $ 0.25 (92) %
"""
        quarter = desk.quarter_metrics(release)
        self.assertEqual(quarter["revenue_current"], 14766)
        self.assertEqual(quarter["revenue_prior_quarter"], 13467)
        self.assertEqual(quarter["revenue_release_line_number"], 6)
        self.assertEqual(quarter["diluted_eps_current"], 0.25)
        self.assertEqual(quarter["diluted_eps_prior_quarter"], 3.11)
        self.assertEqual(quarter["eps_release_line_number"], 7)

    def test_clean_xbrl_claim(self):
        claims = [{"id": "claim:cost_diluted_eps", "kind": "xbrl", "ticker": "COST",
                   "fact_key": "diluted_eps", "reported_value": 17.95, "expected_value": 17.95,
                   "tag": "EarningsPerShareDiluted", "period_end": "2026-08-30",
                   "accession": "0000000000-26-000001"}]
        marks = code_verify_claims(claims, self.run,
                                  "<!-- claim:cost_diluted_eps --> 17.95 EarningsPerShareDiluted 2026-08-30 0000000000-26-000001")
        self.assertEqual(marks[0]["mark"], "correct")

    def test_clean_report_has_eleven_core_claims(self):
        keys = {
            "revenue": 1000, "operating_income": 200, "net_income": 150,
            "diluted_eps": 2.5, "equity": 500, "long_term_debt": 50,
            "current_debt": 10, "cash_from_operations": 250, "capex": -40,
        }
        facts = {}
        claims = []
        report_rows = []
        for index, (key, value) in enumerate(keys.items()):
            tag = f"Tag{index}"
            facts[key] = {"value": value, "tag": tag, "period_end": "2026-08-30",
                          "accession": "0000000000-26-000001"}
            claim_id = f"claim:cost_{key}"
            claims.append({"id": claim_id, "kind": "xbrl", "ticker": "COST", "fact_key": key,
                           "reported_value": value, "expected_value": value, "tag": tag,
                           "period_end": "2026-08-30", "accession": "0000000000-26-000001"})
            report_rows.append(f"<!-- {claim_id} --> {value} {tag} 2026-08-30 0000000000-26-000001")
        (self.run / "COST" / "COST_facts.json").write_text(json.dumps({"facts": facts}))
        filing = "Total revenue 92,279\nDiluted 4.92\n"
        (self.run / "COST" / "8K_0000000000-26-000001.txt").write_text(filing)
        for name, value, line, excerpt in (("quarter_revenue", 92279, 1, "Total revenue 92,279"),
                                           ("quarter_eps", 4.92, 2, "Diluted 4.92")):
            claim_id = f"claim:cost_{name}"
            claims.append({"id": claim_id, "kind": "line", "ticker": "COST", "reported_value": value,
                           "expected_value": value, "filing": "8-K", "accession": "0000000000-26-000001",
                           "source_file": "COST/8K_0000000000-26-000001.txt", "source_line": line,
                           "source_excerpt": excerpt})
            report_rows.append(f"<!-- {claim_id} --> {value} 0000000000-26-000001 line {line} {excerpt}")
        marks = code_verify_claims(claims, self.run, "\n".join(report_rows))
        self.assertEqual(len(marks), 11)
        self.assertTrue(all(mark["mark"] == "correct" for mark in marks))

    def test_seeded_one_dollar_eps_error_is_wrong(self):
        claims = [{"id": "claim:cost_diluted_eps", "kind": "xbrl", "ticker": "COST",
                   "fact_key": "diluted_eps", "reported_value": 18.95, "expected_value": 17.95,
                   "tag": "EarningsPerShareDiluted", "period_end": "2026-08-30",
                   "accession": "0000000000-26-000001"}]
        marks = code_verify_claims(claims, self.run,
                                  "<!-- claim:cost_diluted_eps --> 18.95 EarningsPerShareDiluted 2026-08-30 0000000000-26-000001")
        self.assertEqual(marks[0]["mark"], "wrong")
        self.assertEqual(marks[0]["correction"], 17.95)

    def test_free_cash_flow_uses_reported_capex_input(self):
        claim = {"ratio": "free_cash_flow", "inputs": {
            "cash_from_operations": 200, "additions_to_property_and_equipment": 75}}
        self.assertEqual(calc_expected_ratio(claim), 125)

    def test_report_copy_omits_investment_thesis(self):
        text = "## Overview\nText\n## Investment Recommendation\nPrivate thesis\n## Claims\nEvidence"
        redacted = omit_report_part(text, "Investment Recommendation")
        self.assertNotIn("Private thesis", redacted)
        self.assertIn("## Claims", redacted)

    def test_verifier_gets_cited_line_windows_not_whole_filings(self):
        company = {"facts": {"ticker": "COST", "filings": {
            "10-K": {"accession": "0000000000-26-000001"}},
            }, "filing_texts": {"10-K": "one\ntwo\nthree\nfour\nfive\nsix\nseven"}}
        excerpts = cited_filing_evidence([
            {"ticker": "COST", "filing": "10-K", "accession": "0000000000-26-000001",
             "source_line": 4}
        ], [company], context_lines=1)
        excerpt = excerpts["COST"]["10-K"]
        self.assertIn("saved-text lines 3-5", excerpt)
        self.assertIn("4 | four", excerpt)
        self.assertNotIn("1 | one", excerpt)
        self.assertNotIn("7 | seven", excerpt)

    def test_verified_report_keeps_filings_as_first_line(self):
        path = self.run / "verified_report.md"
        save_verified_report(path, "Filings read: 10-K accession 123", "run-time", "## Overview\nText", [])
        lines = path.read_text().splitlines()
        self.assertEqual(lines[0], "Filings read: 10-K accession 123")
        self.assertEqual(lines[2], "## Verifier marks")

    def test_invented_growth_rate_is_wrong(self):
        claim = {"id": "claim:cost_ratio_revenue_growth", "kind": "ratio", "ticker": "COST", "ratio": "revenue_growth",
                 "reported_value": 0.26, "expected_value": 0.22,
                 "inputs": {"revenue": 122, "revenue_prior_year": 100},
                 "formula": "revenue / revenue_prior_year - 1"}
        marks = code_verify_claims([claim], self.run,
                                   "<!-- claim:cost_ratio_revenue_growth --> 0.26")
        self.assertEqual(marks[0]["mark"], "wrong")
        self.assertAlmostEqual(marks[0]["correction"], 0.22)

    def test_missing_source_is_unsupported(self):
        claim = {"id": "claim:cost_not_sourced", "kind": "line", "ticker": "COST",
                 "reported_value": 1, "expected_value": 1, "source_file": "COST/missing.txt",
                 "source_line": 1, "source_excerpt": "Total revenue 1"}
        marks = code_verify_claims([claim], self.run, "<!-- claim:cost_not_sourced --> 1")
        self.assertEqual(marks[0]["mark"], "unsupported")

    def test_release_parser_reads_same_line_diluted_eps(self):
        text = "\n".join([
            "CONSOLIDATED STATEMENTS OF INCOME",
            "NET INCOME PER COMMON SHARE:",
            "Basic $ 6.75 $ 5.88 $ 20.78 $ 18.24",
            "Diluted $ 6.75 $ 5.87 $ 20.76 $ 18.21",
            "Shares used in calculation (000's):",
            "Diluted 444,364 444,706 444,427 444,803",
        ])
        result = desk.quarter_metrics(text)
        self.assertEqual(result["diluted_eps_current"], 6.75)
        self.assertEqual(result["diluted_eps_prior_quarter"], 5.87)
        self.assertEqual(result["eps_release_line_number"], 4)

    def test_percentage_audit_flags_unsupported_finance_arithmetic(self):
        company = {"ratios": {"revenue_growth": 0.1014, "operating_margin": 0.0385,
                               "return_on_average_equity": 0.2840},
                   "quarter": {"revenue_growth": 0.1110}}
        self.assertEqual(percentage_claim_audit("EPS rose 11.5%; margin is 3.85%.", [company]),
                         ["Unsupported percentage 11.5%; use only percentages from the code-calculated evidence."])

    def test_percentage_audit_accepts_supplied_calculations(self):
        company = {"ratios": {"revenue_growth": 0.1014, "operating_margin": 0.0385,
                               "return_on_average_equity": 0.2840},
                   "quarter": {"revenue_growth": 0.1110}}
        self.assertEqual(percentage_claim_audit("Growth 10.14%, margin 3.85%, quarter 11.10%.", [company]), [])

    def test_amount_audit_flags_wrong_average_equity(self):
        company = {"facts": {"facts": {}}, "ratios": {"inputs": {
            "current_equity": 35_803_000_000, "prior_equity": 29_164_000_000
        }}}
        self.assertTrue(financial_amount_audit("Average equity was $32.433 B.", [company], None))
        self.assertEqual(financial_amount_audit("Average equity was $32.484 B.", [company], None), [])

    def test_period_audit_rejects_qoq_label_for_same_quarter_last_year(self):
        company = {"quarter": {"revenue_current": 95723, "revenue_prior_quarter": 86156}}
        self.assertTrue(financial_period_audit("Revenue rose 11.10% QoQ.", company))
        self.assertEqual(financial_period_audit("Revenue rose 11.10% YoY.", company), [])

    def test_insight_audit_requires_one_cited_line_per_role(self):
        outputs = {
            "Research Analyst": "**Insight:** Mix shifted (10-K accession 0000000000-26-000001, saved-text line 20).",
            "Financial Analyst": "Insight: Cash conversion was strong (10-K accession 0000000000-26-000001, saved-text line 21).",
            "Investment Advisor": "Insight: Margin supports the thesis (10-K accession 0000000000-26-000001, saved-text line 40).",
        }
        self.assertEqual(analyst_insight_audit(outputs), [])
        outputs["Financial Analyst"] = "No insight."
        issues = analyst_insight_audit(outputs)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["role"], "Financial Analyst")
        self.assertEqual(issues[0]["part"], "Valuation Insights")

    def test_insight_audit_rejects_missing_filing_citation(self):
        outputs = {"Research Analyst": "Insight: The business mix changed (line 20).",
                   "Financial Analyst": "Insight: Cash flow grew (10-K line 21).",
                   "Investment Advisor": "Insight: Margin is stable (10-K line 22)."}
        self.assertEqual(analyst_insight_audit(outputs)[0]["role"], "Research Analyst")

    def test_insight_audit_checks_form_accession_line_and_numbers_before_manager_pass(self):
        accession = "0000000000-26-000001"
        company = {"facts": {"ticker": "COST", "filings": {"10-K": {"accession": accession}}},
                   "filing_texts": {"10-K": "heading\nGasoline represented 11% of sales in 2026\nGasoline represented 11% of sales in 2026\nGasoline represented 11% of sales in 2026\n"}}
        outputs = {role: f"Insight: Gasoline was 11% of sales in 2026 (10-K accession {accession}, line {line})."
                   for role, line in zip(("Research Analyst", "Financial Analyst", "Investment Advisor"), (2, 3, 4))}
        outputs["Financial Analyst"] = f"Insight: The 2026 gasoline share was 11% (10-K accession {accession}, line 3)."
        outputs["Investment Advisor"] = f"Insight: Gasoline accounted for 11% in 2026 (10-K accession {accession}, line 4)."
        self.assertEqual(analyst_insight_audit(outputs, [company]), [])
        outputs["Research Analyst"] = outputs["Research Analyst"].replace("10-K accession", "8-K accession")
        issues = analyst_insight_audit(outputs, [company])
        self.assertTrue(any("filing form must match" in issue["issue"] for issue in issues))

    def test_insight_audit_rejects_duplicate_cited_filing_line(self):
        accession = "0000000000-26-000001"
        company = {"facts": {"ticker": "COST", "filings": {"10-K": {"accession": accession}}},
                   "filing_texts": {"10-K": "heading\nClaim is 11% here\n"}}
        citation = f"10-K accession {accession}, line 2"
        outputs = {"Research Analyst": f"Insight: Claim is 11% ({citation}).",
                   "Financial Analyst": f"Insight: It comes to 11% ({citation}).",
                   "Investment Advisor": f"Insight: 11% is material ({citation})."}
        issues = analyst_insight_audit(outputs, [company])
        self.assertEqual([item["role"] for item in issues], ["Financial Analyst", "Investment Advisor"])

    def test_insight_enrichment_adds_source_lines_and_statement_scale(self):
        accession = "0000000000-26-000001"
        company = {
            "facts": {"ticker": "UBER", "filings": {"10-K": {"accession": accession}},
                      "facts": {
                          "cash_from_operations": {"tag": "NetCashProvidedByUsedInOperatingActivities", "value": 10_099_000_000},
                          "diluted_eps": {"tag": "EarningsPerShareDiluted", "value": 4.73},
                      }},
            "filing_texts": {"10-K": "heading\nThere were 3 reportable segments\nConsolidated Statements of Cash Flows\n(In millions)\nCash flows from operating activities\nNet cash provided by operating activities 3,585 7,137 10,099\nNet income per share\nBasic $ 0.90 $ 4.71 $ 4.82\nDiluted $ 0.87 $ 4.56 $ 4.73\n"},
        }
        outputs = {
            "Research Analyst": f"Insight: There were 3 reportable segments (10-K accession {accession}, line 2).",
            "Financial Analyst": f"Insight: Cash from operations was $10,099,000,000 (10-K accession {accession}, NetCashProvidedByUsedInOperatingActivities).",
            "Investment Advisor": f"Insight: Diluted EPS was $4.73 (10-K accession {accession}, EarningsPerShareDiluted).",
        }
        enriched, changes = enrich_insight_source_lines(outputs, [company])
        self.assertEqual(len(changes), 2)
        self.assertIn("10,099 million", enriched["Financial Analyst"])
        self.assertIn("saved-text line 6", enriched["Financial Analyst"])
        self.assertIn("saved-text line 9", enriched["Investment Advisor"])
        self.assertEqual(analyst_insight_audit(enriched, [company]), [])

    def test_advisor_eps_insight_corrects_wrong_statement_line(self):
        accession = "0000000000-26-000001"
        company = {
            "facts": {"ticker": "UBER", "filings": {"10-K": {"accession": accession}},
                      "facts": {"diluted_eps": {"tag": "EarningsPerShareDiluted", "value": 4.73,
                                                "accession": accession, "filing": "10-K"}}},
            "filing_texts": {"10-K": "Consolidated Statements of Income\nNet income per share\nBasic $ 0.90 $ 4.71 $ 4.82\nDiluted $ 0.87 $ 4.56 $ 4.73\n"},
        }
        outputs = {"Investment Advisor":
                   f"Insight: Diluted EPS was $4.73 (EarningsPerShareDiluted tag; 10-K accession {accession}, period 2025, line 2)."}
        enriched, changes = enrich_insight_source_lines(outputs, [company])
        self.assertIn(f"10-K accession {accession}, saved-text line 4", enriched["Investment Advisor"])
        self.assertNotIn("line 2", enriched["Investment Advisor"])
        self.assertEqual(changes[0]["citation_corrected_from"], 2)

    def test_financial_insight_citation_puts_accession_before_line(self):
        accession = "0001543151-26-000015"
        cash_text = "Net cash provided by operating activities was $10.1 billion for the year ended December 31, 2025."
        company = {
            "facts": {"ticker": "UBER", "filings": {"10-K": {"accession": accession}},
                      "facts": {"cash_from_operations": {"tag": "NetCashProvidedByUsedInOperatingActivities",
                                                            "value": 10099000000, "period_end": "2025-12-31",
                                                            "filing": "10-K", "accession": accession}}},
            "filing_texts": {"10-K": "Consolidated Statements of Cash Flows\nNet cash provided by operating activities 7,137 10,099\nOperating Activities\n" + cash_text + "\n"},
        }
        output = {"Financial Analyst":
                  f"Insight: {cash_text} (saved-text line 4; 10-K accession {accession})."}
        enriched, changes = enrich_insight_source_lines(output, [company])
        self.assertIn(f"10-K accession {accession}, saved-text line 4", enriched["Financial Analyst"])
        self.assertNotIn("saved-text line 4; 10-K", enriched["Financial Analyst"])
        self.assertTrue(changes)

    def test_insight_enrichment_completes_earnings_release_citation_from_named_line(self):
        accession = "0001543151-26-000039"
        release = "\n".join(["header"] * 12 + [
            "Business model changes negatively impacted total revenue growth by 8 percentage points."])
        company = {"facts": {"ticker": "UBER", "filings": {"8-K": {"accession": accession}},
                             "facts": {}},
                   "filing_texts": {"8-K": release}}
        outputs = {"Research Analyst":
                   "Insight: Business model changes reduced revenue growth by 8 percentage points (earnings release line 13)."}
        enriched, changes = enrich_insight_source_lines(outputs, [company])
        self.assertIn(f"8-K accession {accession}, saved-text line 13", enriched["Research Analyst"])
        self.assertEqual(changes[0]["filing"], "8-K")

    def test_insight_claims_are_marked_against_saved_line_for_each_analyst(self):
        accession = "0000000000-26-000001"
        citation = f"(10-K accession {accession}, saved-text line 2)"
        outputs = {role: f"Insight: Gasoline represented 11% of sales in 2026 {citation}"
                   for role in ("Research Analyst", "Financial Analyst", "Investment Advisor")}
        outputs["Financial Analyst"] = f"Insight: In 2026, gasoline made up 11% of sales {citation}"
        outputs["Investment Advisor"] = f"Insight: The 2026 gasoline share was 11% {citation}"
        company = {"facts": {"ticker": "COST", "filings": {"10-K": {"accession": accession}}},
                   "filing_texts": {"10-K": "heading\nGasoline represented 11% of sales in 2026\n"}}
        (self.run / "COST" / f"10K_{accession}.txt").write_text(company["filing_texts"]["10-K"])
        claims = insight_claims(outputs, company)
        report_lines = [f"{claim['report_line']} <!-- {claim['id']} -->" for claim in claims]
        marks = code_verify_claims(claims, self.run, "\n".join(report_lines))
        self.assertEqual(len(marks), 3)
        self.assertTrue(all(mark["mark"] == "correct" for mark in marks))
        outputs["Financial Analyst"] = outputs["Financial Analyst"].replace("11%", "12%")
        changed_claims = insight_claims(outputs, company)
        changed_report = "\n".join(f"{c['report_line']} <!-- {c['id']} -->" for c in changed_claims)
        changed_marks = code_verify_claims(changed_claims, self.run, changed_report)
        self.assertEqual(changed_marks[1]["mark"], "wrong")

    def test_insight_claim_parser_handles_typographic_citations_without_counting_them(self):
        accession = "0000909832-26-000084"
        line = "Insight: Annual revenue was 303,154 (8‑K, accession 0000909832‑26‑000084, saved-text line 39)."
        company = {"facts": {"ticker": "COST", "filings": {"8-K": {"accession": accession}}},
                   "filing_texts": {"8-K": "\n" * 38 + "Total revenue 95,723 86,156 303,154 275,235\n"}}
        claim = next(c for c in insight_claims({"Financial Analyst": line}, company)
                     if c["role"] == "Financial Analyst")
        self.assertEqual(claim["filing"], "8-K")
        self.assertEqual(claim["source_line"], 39)
        self.assertEqual(claim["insight_numbers"], [(303154.0, False)])

    def test_insight_period_year_is_not_a_statement_amount(self):
        accession = "0000000000-26-000001"
        citation = f"(saved-text line 2, 10-K, accession {accession})"
        company = {"facts": {"ticker": "UBER", "filings": {"10-K": {"accession": accession}}},
                   "filing_texts": {"10-K": "heading\nNet cash provided by operating activities $ 7,137 $ 10,099\n"}}
        line = f"Insight: Cash from operations was $10,099 million in FY 2025 {citation}."
        claim = next(c for c in insight_claims({"Financial Analyst": line}, company)
                     if c["role"] == "Financial Analyst")
        self.assertEqual(claim["insight_numbers"], [(10099.0, False)])
        self.assertTrue(insight_values_supported(claim))

    def test_insight_parser_ignores_date_and_citation_numbers(self):
        accession = "0000000000-26-000001"
        line = (f"Insight: Net cash provided by operating activities was $10.1 billion for the year ended "
                f"December 31, 2025 (saved-text line 2, 10-K accession {accession}).")
        company = {"facts": {"ticker": "UBER", "filings": {"10-K": {"accession": accession}}},
                   "filing_texts": {"10-K": "heading\nNet cash provided by operating activities was $10.1 billion for the year ended December 31, 2025\n"}}
        claim = next(c for c in insight_claims({"Financial Analyst": line}, company)
                     if c["role"] == "Financial Analyst")
        self.assertEqual(claim["insight_numbers"], [(10.1, False)])

    def test_insight_can_cite_a_peer_filing_with_reported_millions_converted_to_usd(self):
        cost_accession = "0000909832-26-000093"
        wmt_accession = "0000104169-26-000055"
        company = {"facts": {"ticker": "COST", "filings": {"10-K": {"accession": cost_accession}}},
                   "filing_texts": {"10-K": "Costco line"}}
        peer = {"facts": {"ticker": "WMT", "filings": {"10-K": {"accession": wmt_accession}}},
                "filing_texts": {"10-K": "(Amounts in millions)\nTotal revenues 713,163"}}
        line = f"Insight: Walmart revenue was $713,163,000,000 (10-K {wmt_accession}, saved-text line 2)."
        claims = insight_claims({"Financial Analyst": line}, [company, peer])
        claim = next(c for c in claims if c["role"] == "Financial Analyst")
        self.assertEqual(claim["ticker"], "WMT")
        self.assertEqual(claim["source_excerpt"], "Total revenues 713,163")
        (self.run / "WMT").mkdir()
        (self.run / "WMT" / f"10K_{wmt_accession}.txt").write_text(peer["filing_texts"]["10-K"])
        claim["id"] = "claim:cost_insight_financial"
        report_line = f"{claim['report_line']} <!-- {claim['id']} -->"
        marks = code_verify_claims([claim], self.run, report_line)
        self.assertEqual(marks[0]["mark"], "correct")

    def test_verifier_copy_keeps_advisor_insight_but_omits_thesis(self):
        report = ("## Overview\nData\n## Investment Recommendation\nPrivate thesis text\n"
                  "Insight: 11% (10-K accession 0000000000-26-000001, line 2)\n## Verifiable claims\nClaims")
        copy = verifier_report_copy(report)
        self.assertNotIn("Private thesis text", copy)
        self.assertIn("Insight: 11%", copy)
        self.assertIn("## Verifiable claims", copy)


if __name__ == "__main__":
    unittest.main()
