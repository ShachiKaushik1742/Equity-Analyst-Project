#!/usr/bin/env python3
"""FIN 67110 equity desk implemented with CrewAI Flow and Process."""

from __future__ import annotations

import argparse
from importlib.metadata import version as package_version
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import desk
import week03_audit_helpers as audit

ROOT = Path(__file__).resolve().parent
PARTS = audit.PARTS
ROLE_CALL_COUNTS: dict[str, int] = {}


def _read_role(name: str) -> str:
    return (ROOT / "roles" / f"{name.replace(' ', '_')}.md").read_text(encoding="utf-8")


def _call_role(name: str, task: str, context: dict[str, Any], expected: str,
               out: Path, model: str, key: str, base_url: str) -> str:
    """Run one isolated role task in a sequential CrewAI crew."""
    from crewai import Agent, Crew, LLM, Process, Task

    node_dir = out / "nodes"
    node_dir.mkdir(exist_ok=True)
    slug = name.lower().replace(" ", "_")
    attempt = 1
    while (node_dir / f"{slug}_attempt_{attempt}_input.json").exists():
        attempt += 1
    calls = ROLE_CALL_COUNTS.get(name, 0) + 1
    if calls > 2:
        raise RuntimeError(f"{name} exceeded the limit of two model calls in this run.")
    ROLE_CALL_COUNTS[name] = calls
    envelope = {"task": task, "context": context, "expected_output": expected}
    audit.save_json(node_dir / f"{slug}_attempt_{attempt}_input.json", envelope)
    print(f"Running CrewAI node: {name}", flush=True)

    llm = LLM(model=model, api_key=key, base_url=base_url,
              custom_openai=True, temperature=0, max_tokens=5000, timeout=180)
    agent = Agent(role=name, goal=task, backstory=_read_role(name), llm=llm,
                  allow_delegation=False, max_iter=1, verbose=False)
    role_task = Task(description=json.dumps(envelope, ensure_ascii=False),
                     expected_output=expected, agent=agent)
    crew = Crew(agents=[agent], tasks=[role_task], process=Process.sequential,
                memory=False, verbose=False)
    output = crew.kickoff(inputs={}).raw.strip()
    if not output:
        raise RuntimeError(f"{name} returned an empty result")
    (node_dir / f"{slug}_attempt_{attempt}_output.md").write_text(output + "\n", encoding="utf-8")
    return output


def _verify_with_crew(report: str, claims: list[dict[str, Any]], out: Path,
                      companies: list[dict[str, Any]], model: str, key: str,
                      base_url: str) -> list[dict[str, Any]]:
    """Run deterministic checks first, then a CrewAI semantic verifier."""
    code_marks = audit.code_verify_claims(claims, out, report)
    audit.save_json(out / "code_verification.json", code_marks)
    filing_texts = audit.cited_filing_evidence(claims, companies)
    facts = {c["facts"]["ticker"]: c["facts"] for c in companies}
    verifier_report = audit.omit_report_part(report, "Investment Recommendation")
    raw = _call_role(
        "Verifier",
        "Check every numbered claim in the report copy. The Investment Advisor thesis is omitted. "
        "Use only the report, saved filing texts, and saved facts. For each claim, check its value, period, "
        "definition, and source. Check XBRL values against the saved tag and period. Check line claims "
        "against the cited filing line. Check ratios from their stated formula and inputs. Mark each claim "
        "correct, wrong, or unsupported. For a wrong or unsupported claim, give its corrected value and "
        "the filing line or XBRL tag that supports the correction. Return JSON only.",
        {"compiled_report_without_investment_thesis": verifier_report,
         "cited_excerpts_from_saved_filing_texts": filing_texts, "saved_facts": facts},
        'JSON array: [{"id":"claim:ticker_revenue","mark":"correct|wrong|unsupported","correction":"value and source or null","reason":"short reason"}].',
        out, model, key, base_url)
    try:
        parsed = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.I))
        if isinstance(parsed, dict):
            parsed = parsed.get("marks", [])
        semantic = {}
        for item in parsed:
            if not isinstance(item, dict) or not item.get("id"):
                continue
            semantic[item["id"]] = item
            semantic.setdefault("claim:" + item["id"], item)
    except (json.JSONDecodeError, TypeError) as exc:
        raise RuntimeError("Verifier did not return the required JSON marks.") from exc
    for mark in code_marks:
        model_mark = semantic.get(mark["id"], {}).get("mark")
        if model_mark not in {"correct", "wrong", "unsupported"}:
            mark["mark"] = "unsupported"
            mark["reason"] = "Semantic verifier did not return a valid mark for this claim."
        elif mark["mark"] == "correct" and model_mark in {"wrong", "unsupported"}:
            model_item = semantic[mark["id"]]
            mark["mark"] = model_mark
            mark["reason"] = "Semantic verifier: " + str(model_item.get("reason", "source meaning not confirmed"))
            mark["correction"] = model_item.get("correction") or mark["correction"]
        elif mark["mark"] in {"wrong", "unsupported"}:
            # Keep a code-derived correction when available; add the model's source-based correction otherwise.
            mark["correction"] = mark.get("correction") or semantic[mark["id"]].get("correction")
            mark["reason"] = (mark.get("reason", "") + " Semantic verifier: " +
                              str(semantic[mark["id"]].get("reason", "source meaning checked"))).strip()
    return code_marks


try:
    from pydantic import BaseModel, Field
    from crewai.flow import Flow, and_, listen, or_, router, start
except ImportError:  # Keep --help and offline audit imports usable without CrewAI installed.
    Flow = object  # type: ignore[assignment,misc]
    BaseModel = object  # type: ignore[assignment,misc]
    Field = None  # type: ignore[assignment]
    and_ = listen = or_ = router = start = None  # type: ignore[assignment]


if isinstance(Flow, type) and Flow is not object:
    class EquityDeskState(BaseModel):
        ticker: str = ""
        peers: list[str] = Field(default_factory=list)
        price: float | None = None
        price_date: str = ""
        price_source: str = ""
        run_dir: str = ""
        model: str = ""
        api_key: str = ""
        base_url: str = ""
        companies: list[dict[str, Any]] = Field(default_factory=list)
        research: str = ""
        finance: str = ""
        advisor: str = ""
        parts: dict[str, str] = Field(default_factory=dict)
        manager_result: dict[str, Any] = Field(default_factory=dict)
        repair_used: bool = False
        repair_outcome: str = ""
        final_report: str = ""
        verification_marks: list[dict[str, Any]] = Field(default_factory=list)


    class EquityDeskFlow(Flow[EquityDeskState]):
        @start()
        def collect_sec_data(self) -> str:
            print("Running node: Steps (1-7)", flush=True)
            env = desk.load_env()
            key = env.get("API_KEY") or env.get("PURDUE_GENAI_API_KEY")
            user_agent = env.get("SEC_USER_AGENT", "")
            if not key or not user_agent:
                raise RuntimeError("Set API_KEY and SEC_USER_AGENT in .env before the run.")
            self.state.api_key = key
            self.state.base_url = env.get("GENAI_API_BASE", desk.GENAI_API)
            self.state.model = audit.model_name(env, key, self.state.base_url)
            print(f"Purdue GenAI Studio model: {self.state.model}")
            out = audit.RUNS / f"{self.state.ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            out.mkdir(parents=True, exist_ok=False)
            self.state.run_dir = str(out)
            print(f"Run folder: {out}")
            companies = []
            for symbol in [self.state.ticker, *self.state.peers]:
                company, _ = desk.facts_for_company(symbol, user_agent, out)
                companies.append(company)
            desk.print_calculations(companies, self.state.price)
            desk.print_release_and_peers(companies)
            for company in companies:
                company["ratios"] = desk.calc_ratios(company, self.state.price if company is companies[0] else None)
            self.state.companies = companies
            run_time = datetime.now().astimezone().isoformat(timespec="seconds")
            audit.save_json(out / "run_state.json", {
                "ticker": self.state.ticker, "peers": self.state.peers, "price": self.state.price,
                "price_date": self.state.price_date, "price_source": self.state.price_source,
                "run_time": run_time, "framework": "CrewAI Flow + Process.sequential",
                "framework_version": package_version("crewai"),
                "filings": [c["facts"]["filings"] for c in companies],
            })
            nodes = out / "nodes"
            nodes.mkdir(exist_ok=True)
            audit.save_json(nodes / "steps_input.json", {
                "tickers": [self.state.ticker, *self.state.peers], "price": self.state.price,
                "price_date": self.state.price_date, "price_source": self.state.price_source,
            })
            audit.save_json(nodes / "steps_output.json", [
                {"ticker": c["facts"]["ticker"], "facts": c["facts"], "ratios": c["ratios"], "quarter": c["quarter"]}
                for c in companies
            ])
            audit.save_json(out / "node_order.json", ["Seven SEC data steps", "Research Analyst",
                "Financial Analyst", "Investment Advisor", "Strategy Manager", "Verifier"])
            return "data_ready"

        @listen(collect_sec_data)
        def research_analyst(self, _: str) -> str:
            main = self.state.companies[0]
            business, mda, release = audit.numbered_sections(main)
            self.state.research = _call_role(
                "Research Analyst",
                "In no more than 220 words, describe business model, competitive position, catalysts, and recent developments. Every factual claim needs an exact quote with filing, section, accession, and saved-text line.",
                {"10-K Item 1 Business": business, "10-K Item 7 MD&A": mda,
                 "earnings release relevant lines": release},
                "Concise Markdown with source-supported claims and exact line references.",
                Path(self.state.run_dir), self.state.model, self.state.api_key, self.state.base_url)
            return self.state.research

        @listen(research_analyst)
        def financial_analyst(self, _: str) -> str:
            evidence = desk.financial_evidence(self.state.companies, self.state.price,
                                               self.state.price_date or None,
                                               self.state.price_source or None)
            self.state.finance = _call_role(
                "Financial Analyst",
                "In no more than 100 words, interpret the code-calculated facts, ratios, quarter, and peers. Do not reproduce evidence tables. Do not calculate or introduce intermediate values. Use only dollar amounts and percentages printed in the supplied evidence; omit unlisted numbers. Do not calculate average equity or EPS growth. Cite every number with filing/tag, period, and accession. State the selected revenue definition. End with CALCULATOR_REQUESTS: NONE.",
                {"code_calculated_evidence": evidence,
                 "available_calculator_requests": ["debt_to_revenue", "operating_cash_flow_margin", "capex_to_revenue"]},
                "Concise Markdown with sourced numbers and supplied formulas.",
                Path(self.state.run_dir), self.state.model, self.state.api_key, self.state.base_url)
            return self.state.finance

        @listen(financial_analyst)
        def investment_advisor(self, _: str) -> str:
            self.state.advisor = _call_role(
                "Investment Advisor",
                "In no more than 120 words, write a thesis and choose Buy, Hold, or Sell. Name one deciding number. Use only the Research Analyst and Financial Analyst outputs.",
                {"Research Analyst": self.state.research, "Financial Analyst": self.state.finance},
                "A thesis, one supported deciding number, and one recommendation.",
                Path(self.state.run_dir), self.state.model, self.state.api_key, self.state.base_url)
            return self.state.advisor

        @listen(investment_advisor)
        def strategy_manager(self, _: str) -> dict[str, Any]:
            main = self.state.companies[0]
            evidence = desk.financial_evidence(self.state.companies, self.state.price,
                                               self.state.price_date or None,
                                               self.state.price_source or None)
            self.state.parts = {
                "Overview": f"Ticker: {self.state.ticker}. Fiscal year ended {main['facts']['fiscal_year_end']}. Filings: " +
                    "; ".join(f"{f} {main['facts']['filings'][f]['accession']}" for f in ("10-K", "10-Q", "8-K")),
                "Market Positioning and Growth Outlook": self.state.research,
                "Valuation Insights": evidence + "\n\nFinancial Analyst interpretation:\n\n" + self.state.finance,
                "Future Developments and Strategic Recommendations": "Research findings:\n\n" + self.state.research +
                    "\n\nFinancial findings:\n\n" + self.state.finance,
                "Investment Recommendation": self.state.advisor,
            }
            numeric_audit = audit.percentage_claim_audit(self.state.finance, self.state.companies)
            numeric_audit += audit.financial_amount_audit(self.state.finance, self.state.companies, self.state.price)
            numeric_audit += audit.financial_period_audit(self.state.finance, main)
            raw = _call_role(
                "Strategy Manager",
                "Check the five required report parts for completeness and consistency. If automatic_numeric_audit is non-empty, fail Valuation Insights. Return JSON PASS or identify one failing part for its single repair.",
                {"ticker": self.state.ticker, "parts": self.state.parts, "required_parts": PARTS,
                 "source_facts": main["facts"]["facts"], "automatic_numeric_audit": numeric_audit},
                '{"status":"PASS"|"FAIL","failing_part":string|null,"repair_request":string|null}',
                Path(self.state.run_dir), self.state.model, self.state.api_key, self.state.base_url)
            try:
                self.state.manager_result = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.I))
            except json.JSONDecodeError as exc:
                raise RuntimeError("Strategy Manager did not return valid JSON.") from exc
            if numeric_audit:
                self.state.manager_result.update({
                    "status": "FAIL",
                    "failing_part": "Valuation Insights",
                    "repair_request": "Correct the financial language flagged by the automatic audit: " + "; ".join(numeric_audit),
                })
            if str(self.state.manager_result.get("status", "")).upper() != "PASS" and self.state.manager_result.get("failing_part") not in PARTS:
                raise RuntimeError("Strategy Manager failed without naming one valid report part.")
            self.state.manager_result["numeric_audit"] = numeric_audit
            return self.state.manager_result

        @router(strategy_manager)
        def choose_manager_path(self) -> Literal["approve_report", "perform_one_repair"]:
            print("Running Flow router: Strategy Manager repair decision", flush=True)
            if str(self.state.manager_result.get("status", "")).upper() == "PASS" and not self.state.manager_result.get("numeric_audit"):
                decision = "approve_report"
            else:
                decision = "perform_one_repair"
            audit.save_node_record(Path(self.state.run_dir), "choose_manager_path",
                                   {"manager_result": self.state.manager_result}, {"next_node": decision})
            return decision

        @listen("approve_report")
        def compile_approved_report(self) -> str:
            return self._compile_report()

        @listen("perform_one_repair")
        def repair_once(self) -> str:
            heading = self.state.manager_result["failing_part"]
            role = ("Research Analyst" if heading == "Market Positioning and Growth Outlook" else
                    "Financial Analyst" if heading in {"Valuation Insights", "Future Developments and Strategic Recommendations"} else
                    "Investment Advisor" if heading == "Investment Recommendation" else "Strategy Manager")
            main = self.state.companies[0]
            evidence = desk.financial_evidence(self.state.companies, self.state.price,
                                               self.state.price_date or None,
                                               self.state.price_source or None)
            current = self.state.parts[heading]
            repair_input = {"part": heading, "role": role, "manager_request": self.state.manager_result.get("repair_request"),
                            "current_part": current}
            repaired = _call_role(
                role, (f"Repair {heading} once. Follow the manager request and use only the supplied evidence. "
                      "Do not calculate any values; remove every unsupported dollar amount or percentage. "
                      "Quarter revenue growth compares the same quarter last year: call it YoY, never QoQ."),
                {"current_part": current, "manager_request": self.state.manager_result.get("repair_request"),
                 "evidence": evidence if role != "Research Analyst" else audit.numbered_sections(main),
                 "role_outputs": {"Research Analyst": self.state.research, "Financial Analyst": self.state.finance},
                 "automatic_numeric_audit": self.state.manager_result.get("numeric_audit", [])},
                "The revised report part only.", Path(self.state.run_dir), self.state.model,
                self.state.api_key, self.state.base_url)
            audit.save_node_record(Path(self.state.run_dir), "repair_once", repair_input,
                                   {"role": role, "repaired_part": repaired})
            if role == "Financial Analyst":
                self.state.finance = repaired
                evidence = desk.financial_evidence(self.state.companies, self.state.price,
                                                   self.state.price_date or None,
                                                   self.state.price_source or None)
                self.state.parts["Valuation Insights"] = evidence + "\n\nFinancial Analyst interpretation:\n\n" + repaired
                self.state.parts["Future Developments and Strategic Recommendations"] = (
                    "Research findings:\n\n" + self.state.research + "\n\nFinancial findings:\n\n" + repaired)
            elif role == "Research Analyst":
                self.state.research = repaired
                self.state.parts[heading] = repaired
            elif role == "Investment Advisor":
                self.state.advisor = repaired
                self.state.parts[heading] = repaired
            unresolved = audit.percentage_claim_audit(self.state.finance, self.state.companies)
            unresolved += audit.financial_amount_audit(self.state.finance, self.state.companies, self.state.price)
            unresolved += audit.financial_period_audit(self.state.finance, self.state.companies[0])
            self.state.repair_used = True
            self.state.repair_outcome = "unresolved" if unresolved else "passed_after_repair"
            if unresolved:
                self.state.parts["Valuation Insights"] += "\n\nManager note: Numeric audit remains unresolved after the one permitted repair. " + "; ".join(unresolved)
            return self._compile_report()

        @listen(or_(compile_approved_report, repair_once))
        def verify_final_report(self, report: str) -> str:
            out = Path(self.state.run_dir)
            claims = audit.claim_ledger(self.state.companies, self.state.price)
            audit.save_json(out / "claims.json", claims)
            marks = _verify_with_crew(report, claims, out, self.state.companies,
                                      self.state.model, self.state.api_key, self.state.base_url)
            self.state.verification_marks = marks
            audit.save_json(out / "verification_marks.json", marks)
            filing_line = "Filings read: " + "; ".join(
                f"{f} {self.state.companies[0]['facts']['filings'][f]['accession']}" for f in ("10-K", "10-Q", "8-K"))
            timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
            audit.save_verified_report(out / "verified_report.md", filing_line, timestamp, report, marks)
            audit.save_json(out / "flow_state.json", {
                "ticker": self.state.ticker,
                "manager_initial_status": self.state.manager_result.get("status"),
                "manager_status": ("PASS_AFTER_REPAIR" if self.state.repair_outcome == "passed_after_repair"
                                   else "FAIL_UNRESOLVED" if self.state.repair_outcome == "unresolved"
                                   else self.state.manager_result.get("status")),
                "repair_used": self.state.repair_used,
                "repair_outcome": self.state.repair_outcome or None,
                "framework": "CrewAI Flow + Process.sequential",
                "framework_version": package_version("crewai"),
                "verification_total": len(marks),
                "verification_correct": sum(m["mark"] == "correct" for m in marks),
                "verification_other": sum(m["mark"] != "correct" for m in marks),
            })
            print(f"Verified report: {out / 'verified_report.md'}")
            return str(out / "verified_report.md")

        def _compile_report(self) -> str:
            print("Strategy Manager: compiling report", flush=True)
            claims = audit.claim_ledger(self.state.companies, self.state.price)
            body = "\n\n".join(f"## {part}\n\n{text}" for part, text in self.state.parts.items())
            body += "\n\n" + "\n".join(audit.report_claim_lines(claims))
            main = self.state.companies[0]
            filing_line = "Filings read: " + "; ".join(
                f"{f} {main['facts']['filings'][f]['accession']}" for f in ("10-K", "10-Q", "8-K"))
            timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
            out = Path(self.state.run_dir)
            (out / "report.md").write_text(f"{filing_line}\nRun time: {timestamp}\n\n{body}\n", encoding="utf-8")
            audit.save_node_record(out, "compile_report", {"parts": self.state.parts},
                                   {"report_path": str(out / "report.md"), "report_body": body})
            return body


def run_flow(ticker: str, peers: list[str], price: float | None,
             price_date: str | None, price_source: str | None) -> int:
    ROLE_CALL_COUNTS.clear()
    if Flow is object:
        raise RuntimeError("Install requirements.txt with Python 3.13 to use the CrewAI Flow implementation.")
    flow = EquityDeskFlow()
    result = flow.kickoff(inputs={"ticker": ticker, "peers": peers, "price": price,
                                  "price_date": price_date or "", "price_source": price_source or ""})
    marks = flow.state.verification_marks
    print(f"Verifier: {sum(m['mark'] == 'correct' for m in marks)}/{len(marks)} correct")
    return 0 if marks and all(m["mark"] == "correct" for m in marks) else 1


def verify_saved_run(run_dir: Path, env: dict[str, str]) -> int:
    ROLE_CALL_COUNTS.clear()
    run_dir = run_dir.resolve()
    report_path = run_dir / "report.md"
    if not report_path.exists():
        raise FileNotFoundError(f"No report.md in {run_dir}")
    report = report_path.read_text(encoding="utf-8")
    first_line = report.splitlines()[0]
    claims = json.loads((run_dir / "claims.json").read_text(encoding="utf-8"))
    companies = []
    for folder in sorted(p for p in run_dir.iterdir() if p.is_dir()):
        facts_path = folder / f"{folder.name}_facts.json"
        if not facts_path.exists():
            continue
        facts = json.loads(facts_path.read_text(encoding="utf-8"))
        filing_texts = {}
        for form, meta in facts.get("filings", {}).items():
            path = folder / f"{form.replace('-', '')}_{meta['accession']}.txt"
            if path.exists():
                filing_texts[form] = path.read_text(encoding="utf-8")
        companies.append({"facts": facts, "filing_texts": filing_texts})
    key = env.get("API_KEY") or env.get("PURDUE_GENAI_API_KEY")
    if not key:
        raise RuntimeError("Set API_KEY in .env to run the Verifier node.")
    base_url = env.get("GENAI_API_BASE", desk.GENAI_API)
    model = audit.model_name(env, key, base_url)
    marks = _verify_with_crew(report, claims, run_dir, companies, model, key, base_url)
    audit.save_json(run_dir / "verification_marks.json", marks)
    audit.save_verified_report(run_dir / "verified_report.md", first_line,
                               datetime.now().astimezone().isoformat(timespec="seconds"), report, marks)
    print(f"Verified report: {run_dir / 'verified_report.md'}")
    print(f"Verifier: {sum(m['mark'] == 'correct' for m in marks)}/{len(marks)} correct")
    return 0 if marks and all(m["mark"] == "correct" for m in marks) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the CrewAI Flow equity research desk")
    parser.add_argument("ticker", nargs="?", help="SEC ticker symbol")
    parser.add_argument("--peers", default="", help="comma-separated SEC peer tickers")
    parser.add_argument("--price", type=float, help="share price for P/E")
    parser.add_argument("--price-date", help="date for the supplied close")
    parser.add_argument("--price-source", help="source for the supplied close")
    parser.add_argument("--verify-only", type=Path, help="verify a saved run without rerunning data steps or analyst roles")
    args = parser.parse_args()
    env = desk.load_env()
    if args.verify_only:
        try:
            return verify_saved_run(args.verify_only, env)
        except Exception as exc:
            print(f"CrewAI Verifier failed: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 1
    if not args.ticker:
        parser.error("ticker is required unless --verify-only is set")
    if not re.fullmatch(r"[A-Za-z0-9.-]+", args.ticker):
        parser.error("ticker must be a ticker symbol")
    peers = [item.strip().upper() for item in args.peers.split(",") if item.strip()]
    try:
        return run_flow(args.ticker.upper(), peers, args.price, args.price_date, args.price_source)
    except Exception as exc:
        print(f"CrewAI Flow failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
