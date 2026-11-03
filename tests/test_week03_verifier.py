import json
import tempfile
import unittest
from pathlib import Path

import desk
from week03_audit_helpers import (calc_expected_ratio, code_verify_claims,
                                  cited_filing_evidence, financial_amount_audit, financial_period_audit,
                                  omit_report_part, percentage_claim_audit,
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


if __name__ == "__main__":
    unittest.main()
