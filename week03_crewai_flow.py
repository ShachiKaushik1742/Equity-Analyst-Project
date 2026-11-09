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
    execution_contract = (ROOT / "roles" / f"{name.replace(' ', '_')}.md").read_text(encoding="utf-8")
    if name not in {"Research Analyst", "Financial Analyst", "Investment Advisor"}:
        return execution_contract
    persona_text = (ROOT / "week03" / "personas.md").read_text(encoding="utf-8")
    match = re.search(
        rf"(?ms)^## {re.escape(name)}\s*\n(.*?)(?=^## |\Z)", persona_text
    )
    if not match:
        raise RuntimeError(f"No student persona found for {name} in week03/personas.md")
    return "Student-authored persona:\n" + match.group(1).strip() + "\n\nExecution contract:\n" + execution_contract


def _release_opening(company: dict[str, Any], limit: int = 10) -> str:
    """Return a short, line-numbered release opening for insight comparisons."""
    facts = company["facts"]
    accession = facts["filings"]["8-K"]["accession"]
    text = company.get("filing_texts", {}).get("8-K", "")
    rows = text.splitlines()
    return "\n".join(
        f"8-K accession {accession} saved-text line {index + 1}: {row}"
        for index, row in enumerate(rows[:limit]) if row.strip()
    )


def _segment_comparison(company: dict[str, Any]) -> str:
    """Find a 10-K line that compares segment performance year over year."""
    accession = company["facts"]["filings"]["10-K"]["accession"]
    rows = company.get("filing_texts", {}).get("10-K", "").splitlines()
    patterns = {
        "Mobility": re.compile(r"Mobility Gross Bookings grew\s+(\d+(?:\.\d+)?)%", re.I),
        "Delivery": re.compile(r"Delivery Gross Bookings grew\s+(\d+(?:\.\d+)?)%", re.I),
        "Freight": re.compile(r"Freight Gross Bookings (?:declined|grew)\s+(\d+(?:\.\d+)?)%", re.I),
    }
    found = []
    for line_no, line in enumerate(rows, 1):
        if not all(pattern.search(line) for pattern in patterns.values()):
            continue
        for segment, pattern in patterns.items():
            match = pattern.search(line)
            if match:
                found.append((abs(float(match.group(1))), segment, match.group(1), line_no, line))
        break
    if not found:
        return "No single 10-K line compares all segment performance measures year over year. Do not invent a segment comparison."
    _, segment, rate, line_no, line = max(found)
    return (f"Largest segment year-over-year change: {segment}, {rate}% (absolute change). "
            f"10-K accession {accession}, saved-text line {line_no}: {line}")


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
    # Markdown bold is common in model output, but the assignment requires the
    # final line to begin with the literal `Insight:` label.
    output = re.sub(r"(?im)^\*\*Insight:\*\*", "Insight:", output)
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
    verifier_report = audit.verifier_report_copy(report)
    raw = _call_role(
        "Verifier",
        "Check every numbered claim in the report copy, including all three separately marked Insight claims. "
        "The Investment Advisor thesis is omitted, but keep and check the Advisor's Insight line. "
        "Use only the report, saved filing texts, and saved facts. For each claim, check its value, period, "
        "definition, and source. Check XBRL values against the saved tag and period. Check line claims "
        "against the cited filing line. Check ratios from their stated formula and inputs. Mark each claim "
        "correct, wrong, or unsupported. For a wrong or unsupported claim, give its corrected value and "
        "the filing line or XBRL tag that supports the correction. Use exact claim ids. Return one compact "
        "JSON array on one line. For correct claims include only id and mark. For wrong or unsupported "
        "claims include a short correction. Do not include reasons or explanations. Return JSON only.",
        {"compiled_report_without_investment_thesis": verifier_report,
         "cited_excerpts_from_saved_filing_texts": filing_texts, "saved_facts": facts},
        'JSON array: [{"id":"claim:ticker_revenue","mark":"correct|wrong|unsupported"}].',
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
            segment_evidence = _segment_comparison(main)
            self.state.research = _call_role(
                "Research Analyst",
                "In no more than 220 words, describe business model, competitive position, catalysts, and recent developments. Every factual claim needs an exact quote with filing, section, accession, and saved-text line. Use the accession shown for that same filing form in the supplied context; do not cite a 10-K accession for an 8-K line. End with exactly one line that begins 'Insight:'. Use the supplied largest segment year-over-year comparison as the Insight. State the segment, reported percentage, and comparison; cite the exact 10-K accession and saved-text line from that supplied evidence. Do not substitute another metric or source, calculate, or invent numbers or sources. The claim must not appear in the earnings release opening excerpt.",
                {"10-K Item 1 Business": business, "10-K Item 7 MD&A": mda,
                 "earnings release relevant lines": release,
                 "persona segment performance evidence": segment_evidence,
                 "earnings release opening excerpt": _release_opening(main)},
                "Concise Markdown with source-supported claims and exact line references, ending in one sourced Insight line.",
                Path(self.state.run_dir), self.state.model, self.state.api_key, self.state.base_url)
            return self.state.research

        @listen(research_analyst)
        def financial_analyst(self, _: str) -> str:
            evidence = desk.financial_evidence(self.state.companies, self.state.price,
                                               self.state.price_date or None,
                                               self.state.price_source or None)
            eps_line, eps_text = audit.source_lines(self.state.companies[0], "diluted_eps")
            eps_fact = self.state.companies[0]["facts"].get("facts", {}).get("diluted_eps", {})
            if eps_line and eps_text and eps_fact:
                evidence += (f"\n- Latest 10-K diluted EPS statement line for Advisor citation: "
                            f"{eps_fact.get('value')} {eps_fact.get('unit')}; 10-K accession "
                            f"{eps_fact.get('accession')}, saved-text line {eps_line}: {eps_text}")
            cash_line, cash_text = audit.cash_operations_narrative_line(self.state.companies[0])
            if cash_line and cash_text:
                evidence += f"\n- Direct 10-K operating-cash-flow narrative: saved-text line {cash_line}: {cash_text}"
            self.state.finance = _call_role(
                "Financial Analyst",
                "In no more than 100 words, interpret the code-calculated facts, ratios, quarter, and peers. Do not reproduce evidence tables. Do not calculate or introduce intermediate values. Use only dollar amounts and percentages printed in the supplied evidence; omit unlisted numbers. Copy each amount's numeric scale and unit exactly as the evidence prints it; do not change, infer, or convert units. Do not calculate average equity or EPS growth. Cite every number with filing/tag or saved-text line, period, and accession. Include diluted EPS with the exact 10-K statement line, accession, and period so the Advisor can cite it. State the selected revenue definition. Put CALCULATOR_REQUESTS: NONE before the final line. End with exactly one line that begins 'Insight:'. Use the direct 10-K operating-cash-flow narrative sentence supplied in the evidence, not the multi-year table. Make the Insight one short sentence with only the $10.1 billion operating-cash-flow amount, the fiscal period, and its exact filing, full accession, and saved-text line. Do not quote or restate the other dollar figures in that narrative sentence. The Insight must make a filing-supported claim not stated in the earnings release opening excerpt. Do not use a calculated ratio, growth rate, or quarter figure for the Insight. Do not cite a 10-K accession for an 8-K line. Do not calculate or invent numbers or sources.",
                {"code_calculated_evidence": evidence,
                 "earnings release opening excerpt": _release_opening(self.state.companies[0]),
                 "available_calculator_requests": ["debt_to_revenue", "operating_cash_flow_margin", "capex_to_revenue"]},
                "Concise Markdown with sourced numbers and supplied formulas, ending in one sourced Insight line.",
                Path(self.state.run_dir), self.state.model, self.state.api_key, self.state.base_url)
            return self.state.finance

        @listen(financial_analyst)
        def investment_advisor(self, _: str) -> str:
            self.state.advisor = _call_role(
                "Investment Advisor",
                "In no more than 120 words, write a thesis and choose Buy, Hold, or Sell. Name one deciding number. Use only the Research Analyst and Financial Analyst outputs. End with exactly one line that begins 'Insight:'. For the Insight, use the latest 10-K diluted EPS statement line cited by the Financial Analyst. Copy its value, period, filing form, full accession, and exact saved-text line. This must differ from the Research Analyst's segment Insight and the Financial Analyst's cash-flow Insight. The claim must be absent from the earnings release opening. Do not claim that revenue declined unless the cited filing explicitly reports a decline in revenue; a negative impact on the growth rate is not a revenue decline. Do not add a fact or an uncited number.",
                {"Research Analyst": self.state.research, "Financial Analyst": self.state.finance},
                "A thesis, one supported deciding number, one recommendation, and a sourced Insight line.",
                Path(self.state.run_dir), self.state.model, self.state.api_key, self.state.base_url)
            return self.state.advisor

        @listen(investment_advisor)
        def strategy_manager(self, _: str) -> dict[str, Any]:
            main = self.state.companies[0]
            raw_roles = {"Research Analyst": self.state.research,
                         "Financial Analyst": self.state.finance,
                         "Investment Advisor": self.state.advisor}
            enriched_roles, enrichment_changes = audit.enrich_insight_source_lines(
                raw_roles, self.state.companies)
            self.state.research = enriched_roles["Research Analyst"]
            self.state.finance = enriched_roles["Financial Analyst"]
            self.state.advisor = enriched_roles["Investment Advisor"]
            audit.save_node_record(Path(self.state.run_dir), "insight_line_enrichment",
                                   {"role_outputs": raw_roles},
                                   {"role_outputs": enriched_roles, "changes": enrichment_changes})
            evidence = desk.financial_evidence(self.state.companies, self.state.price,
                                               self.state.price_date or None,
                                               self.state.price_source or None)
            self.state.parts = {
                "Overview": f"Ticker: {self.state.ticker}. Fiscal year ended {main['facts']['fiscal_year_end']}. Filings: " +
                    "; ".join(f"{f} {main['facts']['filings'][f]['accession']}" for f in ("10-K", "10-Q", "8-K")),
                "Market Positioning and Growth Outlook": self.state.research,
                "Valuation Insights": evidence + "\n\nFinancial Analyst interpretation:\n\n" + self.state.finance,
                "Future Developments and Strategic Recommendations": "",
                "Investment Recommendation": self.state.advisor,
            }
            numeric_audit = audit.percentage_claim_audit(self.state.finance, self.state.companies)
            numeric_audit += audit.financial_amount_audit(self.state.finance, self.state.companies, self.state.price)
            numeric_audit += audit.financial_period_audit(self.state.finance, main)
            insight_issues = audit.analyst_insight_audit({
                "Research Analyst": self.state.research,
                "Financial Analyst": self.state.finance,
                "Investment Advisor": self.state.advisor,
            }, self.state.companies)
            raw = _call_role(
                "Strategy Manager",
                "Check the five required report parts for completeness and consistency. Check every analyst output for exactly one sourced and distinct Insight line. Each insight must make a filing-supported claim that the supplied earnings release opening excerpt does not state. Reject duplicate insight claims, an insight that restates the release headline, or an insight without a source citation. If automatic_numeric_audit is non-empty, fail Valuation Insights. If automatic_insight_audit is non-empty, fail the part owned by the first listed role. Write a concise, substantive future_developments_and_recommendations section with specific next-period indicators and recommendations that follow from the analysts' evidence. Use only the analyst parts. For a factual statement, copy the complete citation from the analyst part that supports it, character for character, including filing form, complete accession, and line or tag. Do not use a citation that appears in another filing or was not supplied for the specific claim. Copy every accession in full, including leading zeroes; never shorten an accession. If no supported forecast or recommendation is given, state what evidence the desk should monitor next period, without adding numerical estimates, targets, or forecasts. Do not copy analyst sections into it. Return JSON with status, failing_part, repair_request, and future_developments_and_recommendations, or identify one failing part for its single repair.",
                {"ticker": self.state.ticker, "parts": self.state.parts, "required_parts": PARTS,
                 "source_facts": main["facts"]["facts"], "automatic_numeric_audit": numeric_audit,
                 "automatic_insight_audit": insight_issues,
                 "earnings_release_opening_excerpt": _release_opening(main)},
                '{"status":"PASS"|"FAIL","failing_part":string|null,"repair_request":string|null,"future_developments_and_recommendations":string}',
                Path(self.state.run_dir), self.state.model, self.state.api_key, self.state.base_url)
            try:
                self.state.manager_result = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.I))
            except json.JSONDecodeError as exc:
                raise RuntimeError("Strategy Manager did not return valid JSON.") from exc
            future_section = str(self.state.manager_result.get("future_developments_and_recommendations", "")).strip()
            repair_requests = []
            if len(future_section) < 80 or "Research findings:" in future_section:
                repair_requests = [{
                    "role": "Strategy Manager", "part": "Future Developments and Strategic Recommendations",
                    "request": "Write a substantive, evidence-based section with next-period indicators and recommendations. Do not copy or repeat the analyst sections.",
                }]
            else:
                self.state.parts["Future Developments and Strategic Recommendations"] = future_section
            if numeric_audit:
                repair_requests.append({
                    "role": "Financial Analyst", "part": "Valuation Insights",
                    "request": "Correct the financial language flagged by the automatic audit: " + "; ".join(numeric_audit),
                })
            role_for_part = {
                "Market Positioning and Growth Outlook": "Research Analyst",
                "Valuation Insights": "Financial Analyst",
                "Future Developments and Strategic Recommendations": "Strategy Manager",
                "Investment Recommendation": "Investment Advisor",
                "Overview": "Strategy Manager",
            }
            for issue in insight_issues:
                request = {"role": issue["role"], "part": issue["part"], "request": issue["issue"]}
                if not any(item["role"] == request["role"] for item in repair_requests):
                    repair_requests.append(request)
                else:
                    existing = next(item for item in repair_requests if item["role"] == request["role"])
                    existing["request"] += "; " + request["request"]
            if str(self.state.manager_result.get("status", "")).upper() != "PASS":
                failing_part = self.state.manager_result.get("failing_part")
                if failing_part in PARTS:
                    manager_role = role_for_part[failing_part]
                    if not any(item["role"] == manager_role for item in repair_requests):
                        repair_requests.append({
                            "role": manager_role, "part": failing_part,
                            "request": self.state.manager_result.get("repair_request") or "Revise the failing report part.",
                        })
            if repair_requests:
                self.state.manager_result.update({
                    "status": "FAIL", "failing_part": repair_requests[0]["part"],
                    "repair_request": repair_requests[0]["request"],
                    "repair_requests": repair_requests,
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
            main = self.state.companies[0]
            evidence = desk.financial_evidence(self.state.companies, self.state.price,
                                               self.state.price_date or None,
                                               self.state.price_source or None)
            cash_line, cash_text = audit.cash_operations_narrative_line(main)
            if cash_line and cash_text:
                evidence += f"\n- Direct 10-K operating-cash-flow narrative: saved-text line {cash_line}: {cash_text}"
            requests = self.state.manager_result.get("repair_requests") or [{
                "part": self.state.manager_result["failing_part"],
                "role": "Financial Analyst", "request": self.state.manager_result.get("repair_request", "Revise the failing part."),
            }]
            # Retry each failing role at most once, in a fixed code-defined order.
            requests_by_role = {item["role"]: item for item in requests}
            repair_results = {}
            for role in ("Research Analyst", "Financial Analyst", "Investment Advisor", "Strategy Manager"):
                if role not in requests_by_role:
                    continue
                request = requests_by_role[role]
                heading = request["part"]
                current = self.state.parts[heading]
                repair_input = {"part": heading, "role": role, "manager_request": request["request"],
                                "current_part": current}
                repair_task = (
                    f"Repair {heading} once. Follow the manager request and use only the supplied evidence. "
                    "Do not calculate any values; remove every unsupported dollar amount or percentage. "
                    "Quarter revenue growth compares the same quarter last year: call it YoY, never QoQ. "
                    "Preserve exactly one final Insight: line when repairing an analyst part. It must state a supported claim absent from the earnings release opening and cite the correct filing form, its matching accession, and exact saved-text line or XBRL tag. Copy the number and scale from the evidence. When repairing a Strategy Manager section, return only that section's prose, with specific indicators and recommendations. Use only facts and periods in the analyst outputs. Cite each factual claim with its filing, accession, and saved-text line or tag. Do not add forecasts, targets, or numerical claims that the supplied evidence does not state. Do not return JSON or copy analyst sections."
                )
                if role == "Financial Analyst":
                    repair_task += (" For the Insight, use the direct 10-K operating-cash-flow narrative sentence in the supplied evidence, not the multi-year table. "
                                    "Copy its amount, period, matching 10-K accession, and exact saved-text line. Do not state a growth rate in the Insight.")
                elif role == "Investment Advisor":
                    repair_task += (" For the Insight, you must use the latest 10-K diluted EPS statement row supplied in the evidence. State its exact value and cite the full 10-K accession and exact saved-text line. "
                                    "This is distinct from the Research Analyst's segment change and the Financial Analyst's operating-cash-flow claim. Do not select another claim or source.")
                role_evidence = evidence if role != "Research Analyst" else "\n\n".join(audit.numbered_sections(main))
                if role == "Research Analyst":
                    role_evidence += "\n\nPersona segment performance evidence for the required Insight: " + _segment_comparison(main)
                    cited_release_line = re.search(r"(?i)(?:earnings\s+release|8-K)[^\n]*?line\s+(\d+)", current)
                    if cited_release_line:
                        line_no = int(cited_release_line.group(1))
                        release_text = main.get("filing_texts", {}).get("8-K", "").splitlines()
                        if 1 <= line_no <= len(release_text):
                            release_accession = main["facts"]["filings"]["8-K"]["accession"]
                            role_evidence += (f"\n\nExact source line already selected for the Research Analyst Insight: "
                                             f"8-K accession {release_accession}, saved-text line {line_no}: "
                                             f"{release_text[line_no - 1]}")
                elif role == "Investment Advisor":
                    eps_line, eps_text = audit.source_lines(main, "diluted_eps")
                    eps_fact = main["facts"].get("facts", {}).get("diluted_eps", {})
                    if eps_line and eps_text and eps_fact:
                        role_evidence += (f"\n\nA separate, directly reported value that may support the Advisor Insight: "
                                          f"{eps_fact.get('value')} {eps_fact.get('unit')}; tag {eps_fact.get('tag')}; "
                                          f"10-K accession {eps_fact.get('accession')}, saved-text line {eps_line}: {eps_text}")
                repaired = _call_role(
                    role, repair_task,
                    {"current_part": current, "manager_request": request["request"],
                     "evidence": role_evidence,
                     "earnings_release_opening_excerpt": _release_opening(main),
                     "role_outputs": {"Research Analyst": self.state.research, "Financial Analyst": self.state.finance},
                     "automatic_numeric_audit": self.state.manager_result.get("numeric_audit", [])},
                    "The revised report part only.", Path(self.state.run_dir), self.state.model,
                    self.state.api_key, self.state.base_url)
                repair_results[role] = repaired
                slug = role.lower().replace(" ", "_")
                audit.save_node_record(Path(self.state.run_dir), f"repair_{slug}", repair_input,
                                       {"role": role, "repaired_part": repaired})
                if role == "Financial Analyst":
                    self.state.finance = repaired
                    self.state.parts["Valuation Insights"] = evidence + "\n\nFinancial Analyst interpretation:\n\n" + repaired
                elif role == "Research Analyst":
                    self.state.research = repaired
                    self.state.parts[heading] = repaired
                elif role == "Investment Advisor":
                    self.state.advisor = repaired
                    self.state.parts[heading] = repaired
                elif role == "Strategy Manager":
                    self.state.parts[heading] = repaired.strip()
            # A repair can add or change an Insight citation. Enrich repaired
            # role outputs before the final audit and report compilation.
            repaired_roles = {"Research Analyst": self.state.research,
                              "Financial Analyst": self.state.finance,
                              "Investment Advisor": self.state.advisor}
            enriched_roles, enrichment_changes = audit.enrich_insight_source_lines(
                repaired_roles, self.state.companies)
            self.state.research = enriched_roles["Research Analyst"]
            self.state.finance = enriched_roles["Financial Analyst"]
            self.state.advisor = enriched_roles["Investment Advisor"]
            self.state.parts["Market Positioning and Growth Outlook"] = self.state.research
            self.state.parts["Valuation Insights"] = evidence + "\n\nFinancial Analyst interpretation:\n\n" + self.state.finance
            self.state.parts["Investment Recommendation"] = self.state.advisor
            audit.save_node_record(Path(self.state.run_dir), "repair_insight_line_enrichment",
                                   {"role_outputs": repaired_roles},
                                   {"role_outputs": enriched_roles, "changes": enrichment_changes})
            unresolved = audit.percentage_claim_audit(self.state.finance, self.state.companies)
            unresolved += audit.financial_amount_audit(self.state.finance, self.state.companies, self.state.price)
            unresolved += audit.financial_period_audit(self.state.finance, self.state.companies[0])
            unresolved_insights = audit.analyst_insight_audit({
                "Research Analyst": self.state.research,
                "Financial Analyst": self.state.finance,
                "Investment Advisor": self.state.advisor,
            }, self.state.companies)
            if (len(self.state.parts["Future Developments and Strategic Recommendations"].strip()) < 80 or
                    "Research findings:" in self.state.parts["Future Developments and Strategic Recommendations"]):
                unresolved_insights.append({"role": "Strategy Manager",
                                            "part": "Future Developments and Strategic Recommendations",
                                            "issue": "The Manager did not produce a substantive, distinct future developments section."})
            self.state.repair_used = bool(repair_results)
            self.state.repair_outcome = "unresolved" if unresolved or unresolved_insights else "passed_after_repair"
            if unresolved:
                self.state.parts["Valuation Insights"] += "\n\nManager note: Numeric audit remains unresolved after the one permitted repair. " + "; ".join(unresolved)
            for part in sorted({item["part"] for item in unresolved_insights}):
                part_issues = [item["issue"] for item in unresolved_insights if item["part"] == part]
                self.state.parts[part] += "\n\nManager note: Insight requirement remains unresolved after the permitted repair. " + "; ".join(part_issues)
            return self._compile_report()

        @listen(or_(compile_approved_report, repair_once))
        def verify_final_report(self, report: str) -> str:
            out = Path(self.state.run_dir)
            claims = json.loads((out / "claims.json").read_text(encoding="utf-8"))
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
            role_outputs = {"Research Analyst": self.state.research,
                            "Financial Analyst": self.state.finance,
                            "Investment Advisor": self.state.advisor}
            claims = audit.claim_ledger(self.state.companies, self.state.price, role_outputs)
            for claim in claims:
                if claim["kind"] != "insight":
                    continue
                part = {"Research Analyst": "Market Positioning and Growth Outlook",
                        "Financial Analyst": "Valuation Insights",
                        "Investment Advisor": "Investment Recommendation"}[claim["role"]]
                self.state.parts[part] = re.sub(
                    r"(?im)^(Insight:.*)$",
                    lambda match: match.group(1) + f" <!-- {claim['id']} -->",
                    self.state.parts[part], count=1)
            audit.save_json(Path(self.state.run_dir) / "claims.json", claims)
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
