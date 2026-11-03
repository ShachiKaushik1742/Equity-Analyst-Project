#!/usr/bin/env python3
"""Fixed Week 3 agent graph for the FIN 67110 SEC research desk."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import desk

ROOT = Path(__file__).resolve().parent
ROLES = ROOT / "roles"
RUNS = ROOT / "runs"
PARTS = [
    "Overview",
    "Market Positioning and Growth Outlook",
    "Valuation Insights",
    "Future Developments and Strategic Recommendations",
    "Investment Recommendation",
]


def save_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def model_name(env: dict[str, str], key: str, base_url: str) -> str:
    selected = env.get("GENAI_MODEL", "").strip()
    if selected:
        return selected
    from openai import OpenAI
    client = OpenAI(api_key=key, base_url=base_url, timeout=45.0, max_retries=0)
    try:
        models = [item.id for item in client.models.list().data]
    finally:
        client.close()
    selected = next((name for name in ("gpt-oss:120b", "qwen3.8:27b") if name in models),
                    models[0] if models else "")
    if not selected:
        raise RuntimeError("Purdue GenAI Studio returned no available models. Set GENAI_MODEL in .env.")
    return selected


def role_instructions(name: str) -> str:
    path = ROLES / f"{name.replace(' ', '_')}.md"
    return path.read_text(encoding="utf-8")


def call_node(name: str, task: str, context: dict[str, Any], expected: str,
              out: Path, model: str, key: str, base_url: str) -> str:
    """Use a role file from roles/ and save this node's exact JSON input/output."""
    from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
    from openai import AsyncOpenAI

    envelope = {"task": task, "context": context, "expected_output": expected}
    node_dir = out / "nodes"
    node_dir.mkdir(exist_ok=True)
    slug = name.lower().replace(" ", "_")
    attempt = 1
    while (node_dir / f"{slug}_attempt_{attempt}_input.json").exists():
        attempt += 1
    save_json(node_dir / f"{slug}_attempt_{attempt}_input.json", envelope)
    print(f"Running node: {name}", flush=True)
    set_tracing_disabled(True)
    client = AsyncOpenAI(api_key=key, base_url=base_url, timeout=180.0, max_retries=0)
    agent = Agent(
        name=name,
        instructions=role_instructions(name),
        model=OpenAIChatCompletionsModel(model=model, openai_client=client),
    )
    async def execute() -> str:
        try:
            result = await Runner.run(agent, json.dumps(envelope, ensure_ascii=False))
            return str(result.final_output).strip()
        finally:
            await client.close()

    output = asyncio.run(execute())
    if not output:
        raise RuntimeError(f"{name} returned an empty result")
    (node_dir / f"{slug}_attempt_{attempt}_output.md").write_text(output + "\n", encoding="utf-8")
    return output


def source_lines(company: dict[str, Any], key: str) -> tuple[int | None, str]:
    facts = company["facts"]["facts"]
    fact = facts.get(key)
    if not fact:
        return None, ""
    form = fact.get("filing", "10-K")
    text = company["filing_texts"].get(form, "")
    value = abs(float(fact["value"]))
    lines = text.splitlines()
    statement = {
        "revenue": (r"^(?:Consolidated|Condensed) Statements of (?:Income|Operations|Earnings)(?: and Comprehensive Income)?$", r"total revenues?|net sales"),
        "revenue_prior_year": (r"^(?:Consolidated|Condensed) Statements of (?:Income|Operations|Earnings)(?: and Comprehensive Income)?$", r"total revenues?|net sales"),
        "operating_income": (r"^(?:Consolidated|Condensed) Statements of (?:Income|Operations|Earnings)(?: and Comprehensive Income)?$", r"operating income"),
        "net_income": (r"^(?:Consolidated|Condensed) Statements of (?:Income|Operations|Earnings)(?: and Comprehensive Income)?$", r"net income"),
        "diluted_eps": (r"^(?:Consolidated|Condensed) Statements of (?:Income|Operations|Earnings)(?: and Comprehensive Income)?$", r"diluted"),
        "equity": (r"^Consolidated Balance Sheets$", r"total (?:stockholders.? equity|equity|walmart shareholders.? equity)"),
        "long_term_debt": (r"^Consolidated Balance Sheets$", r"long.term debt"),
        "current_debt": (r"^Consolidated Balance Sheets$", r"current portion of long.term debt"),
        "cash_from_operations": (r"^Consolidated Statements of Cash Flows$", r"net cash (?:provided by|used in) operating activities"),
        "capex": (r"^Consolidated Statements of Cash Flows$", r"(?:payments to acquire|additions to) property"),
    }
    heading_pattern, label_pattern = statement.get(key, (r"Consolidated Statements", r"."))
    starts = [i for i, line in enumerate(lines) if re.fullmatch(heading_pattern, line.strip(), re.I)]
    amounts = [value, value / 1_000, value / 1_000_000, value / 1_000_000_000]
    for start in starts:
        end = min(len(lines), start + 180)
        for index in range(start, end):
            numbers = re.findall(r"(?<![\w])\(?-?\$?\s*(\d[\d,]*(?:\.\d+)?)\)?", lines[index])
            parsed = [float(number.replace(",", "")) for number in numbers]
            if not any(any(abs(number - target) < 0.001 for target in amounts) for number in parsed):
                continue
            context = " ".join(lines[max(start, index - 4):min(end, index + 2)])
            if re.search(label_pattern, context, re.I):
                return index + 1, lines[index]
    return None, ""


def claim_ledger(companies: list[dict[str, Any]], price: float | None) -> list[dict[str, Any]]:
    """Build claims from deterministic SEC inputs and ratio calculations."""
    claims: list[dict[str, Any]] = []
    for company_index, company in enumerate(companies):
        symbol = company["facts"]["ticker"]
        facts = company["facts"]["facts"]
        filing_map = company["facts"]["filings"]
        for key, fact in facts.items():
            if not fact:
                continue
            if company_index > 0 and key not in {"revenue", "operating_income"}:
                continue
            marker = f"claim:{symbol.lower()}_{key}"
            line_no, excerpt = source_lines(company, key)
            claims.append({
                "id": marker, "kind": "xbrl", "ticker": symbol, "fact_key": key,
                "reported_value": fact["value"], "expected_value": fact["value"],
                "tag": fact["tag"], "period_end": fact.get("period_end"),
                "accession": fact.get("accession"), "filing": fact.get("filing"),
                "unit": fact.get("unit"), "source_line": line_no,
                "source_excerpt": excerpt,
            })
        ratios = company.get("ratios") or desk.calc_ratios(company, price if company_index == 0 else None)
        ratio_inputs = {
            "revenue": (facts.get("revenue") or {}).get("value"),
            "revenue_prior_year": (facts.get("revenue_prior_year") or {}).get("value"),
            "operating_income": (facts.get("operating_income") or {}).get("value"),
            "net_income": (facts.get("net_income") or {}).get("value"),
            **ratios.get("inputs", {}),
        }
        ratio_names = ("revenue_growth", "operating_margin", "return_on_average_equity", "debt_to_equity", "free_cash_flow", "pe") if company_index == 0 else ("operating_margin",)
        for name in ratio_names:
            value = ratios.get(name)
            if value is None:
                continue
            claims.append({
                "id": f"claim:{symbol.lower()}_ratio_{name}", "kind": "ratio",
                "ticker": symbol, "ratio": name, "reported_value": value,
                "expected_value": value, "inputs": ratio_inputs,
                "formula": {
                    "revenue_growth": "revenue / revenue_prior_year - 1",
                    "operating_margin": "operating_income / revenue",
                    "return_on_average_equity": "net_income / ((equity + prior_equity) / 2)",
                    "debt_to_equity": "(long_term_debt + current_debt) / equity",
                    "free_cash_flow": "cash_from_operations - capex",
                    "pe": "price / diluted_eps",
                }[name],
            })
        quarter = company.get("quarter", {})
        if company_index == 0 and quarter.get("revenue_current") is not None:
            for name, key in (("quarter_revenue", "revenue_release_line"), ("quarter_diluted_eps", "eps_release_line")):
                excerpt = quarter.get(key) or ""
                line = quarter.get("revenue_release_line_number" if name == "quarter_revenue" else "eps_release_line_number")
                value = quarter.get("revenue_current" if name == "quarter_revenue" else "diluted_eps_current")
                claims.append({
                    "id": f"claim:{symbol.lower()}_{name}", "kind": "line",
                    "ticker": symbol, "reported_value": value, "expected_value": value,
                    "filing": "8-K", "accession": filing_map["8-K"]["accession"],
                    "source_file": f"{symbol}/8K_{filing_map['8-K']['accession']}.txt",
                    "source_line": line, "source_excerpt": excerpt,
                })
    return claims


def calc_expected_ratio(claim: dict[str, Any]) -> float | None:
    i = claim.get("inputs", {})
    name = claim.get("ratio")
    formulas = {
        "revenue_growth": lambda: i["revenue"] / i["revenue_prior_year"] - 1,
        "operating_margin": lambda: i["operating_income"] / i["revenue"],
        "return_on_average_equity": lambda: i["net_income"] / ((i["current_equity"] + i["prior_equity"]) / 2),
        "debt_to_equity": lambda: (i["long_term_debt"] + i["current_portion_debt"]) / i["current_equity"],
        "free_cash_flow": lambda: i["cash_from_operations"] - i["additions_to_property_and_equipment"],
        "pe": lambda: i["price"] / i["diluted_eps"],
    }
    try:
        return float(formulas[name]())
    except (KeyError, TypeError, ZeroDivisionError):
        return None


def percentage_claim_audit(text: str, companies: list[dict[str, Any]]) -> list[str]:
    """Flag percentage values in Financial Analyst prose that code did not calculate."""
    allowed: list[float] = []
    for company in companies:
        ratios = company.get("ratios", {})
        for name in ("revenue_growth", "operating_margin", "return_on_average_equity"):
            value = ratios.get(name)
            if value is not None:
                allowed.append(float(value) * 100)
        quarter_growth = company.get("quarter", {}).get("revenue_growth")
        if quarter_growth is not None:
            allowed.append(float(quarter_growth) * 100)
    issues = []
    for match in re.finditer(r"(?<![\w.])(-?\d+(?:\.\d+)?)\s*%", text):
        value = float(match.group(1))
        if not any(abs(value - expected) <= 0.06 for expected in allowed):
            issues.append(f"Unsupported percentage {match.group(1)}%; use only percentages from the code-calculated evidence.")
    return issues


def code_verify_claims(claims: list[dict[str, Any]], run_dir: Path,
                       report_text: str) -> list[dict[str, Any]]:
    """Verify source existence, exact tags/periods, report values, and arithmetic."""
    marks = []
    for claim in claims:
        reason = ""
        corrected = claim.get("expected_value")
        marker = f"<!-- {claim['id']} -->"
        if marker not in report_text:
            mark = "unsupported"
            reason = "The claim marker is missing from the report."
        elif claim["kind"] == "xbrl":
            fact_file = run_dir / claim["ticker"] / f"{claim['ticker']}_facts.json"
            if not fact_file.exists():
                mark, reason = "unsupported", "The saved facts file is missing."
            else:
                facts = json.loads(fact_file.read_text(encoding="utf-8"))["facts"]
                saved = facts.get(claim["fact_key"])
                if not saved:
                    mark, reason = "unsupported", "The cited fact is absent from saved facts."
                elif (saved.get("value") != claim.get("reported_value") or saved.get("tag") != claim.get("tag")
                      or saved.get("period_end") != claim.get("period_end") or saved.get("accession") != claim.get("accession")):
                    mark, reason = "wrong", "The claim does not match the saved fact, tag, period, or filing."
                    corrected = saved.get("value")
                else:
                    report_line = next((line for line in report_text.splitlines() if marker in line), "")
                    cited = (str(claim["reported_value"]) in report_line
                             and str(claim["tag"]) in report_line
                             and str(claim["period_end"]) in report_line
                             and str(claim["accession"]) in report_line)
                    if claim.get("source_line"):
                        cited = cited and f"saved-text line {claim['source_line']}" in report_line
                    if not cited:
                        mark, reason = "wrong", "The report value or its tag, period, or accession differs from the cited XBRL fact."
                        corrected = saved.get("value")
                    else:
                        mark, reason = "correct", "Report value, tag, period, and accession match the saved XBRL fact."
        elif claim["kind"] == "ratio":
            expected = calc_expected_ratio(claim)
            report_line = next((line for line in report_text.splitlines() if marker in line), "")
            if expected is None:
                mark, reason = "unsupported", "The ratio inputs do not support the stated formula."
            elif abs(float(claim["reported_value"]) - expected) > max(1e-8, abs(expected) * 1e-8):
                mark, reason, corrected = "wrong", "Recalculation from the quoted inputs does not match the reported ratio.", expected
            elif (f"{expected:.8g}" not in report_line or claim.get("formula", "") not in report_line
                  or json.dumps(claim.get("inputs", {}), sort_keys=True) not in report_line):
                mark, reason, corrected = "wrong", "The report line does not state the recomputed ratio.", expected
            else:
                mark, reason = "correct", "Ratio recomputed from its saved inputs and formula."
        else:
            path = run_dir / claim["source_file"]
            if not path.exists():
                mark, reason = "unsupported", "The cited filing text is missing."
            else:
                text = path.read_text(encoding="utf-8")
                norm = lambda value: re.sub(r"\s+", " ", value).strip().casefold()
                report_line = next((line for line in report_text.splitlines() if marker in line), "")
                lines = text.splitlines()
                cited_line = claim.get("source_line")
                exact_line = (isinstance(cited_line, int) and 1 <= cited_line <= len(lines)
                              and norm(claim.get("source_excerpt", "")) in norm(lines[cited_line - 1]))
                if (exact_line and norm(claim["source_excerpt"]) in norm(text)
                        and str(claim["reported_value"]) in report_line
                        and str(claim["accession"]) in report_line
                        and f"line {cited_line}" in report_line):
                    mark, reason = "correct", "Quoted filing text and report value are present."
                else:
                    mark, reason, corrected = "wrong", "The quote or value does not match the saved filing text.", claim.get("expected_value")
        if claim["kind"] == "xbrl":
            source = f"{claim['ticker']} {claim.get('filing')} accession {claim.get('accession')}; tag {claim.get('tag')}, period ending {claim.get('period_end')}"
            if claim.get("source_line"):
                source += f", saved-text line {claim['source_line']}"
        elif claim["kind"] == "line":
            source = f"{claim['ticker']} {claim.get('filing')} accession {claim.get('accession')}, saved-text line {claim.get('source_line')}"
        else:
            source = f"{claim['ticker']} ratio formula {claim.get('formula')}"
        marks.append({"id": claim["id"], "mark": mark, "reason": reason,
                      "source": source, "correction": corrected})
    return marks


def report_claim_lines(claims: list[dict[str, Any]]) -> list[str]:
    lines = ["## Verifiable claims", ""]
    for c in claims:
        marker = f"<!-- {c['id']} -->"
        if c["kind"] == "xbrl":
            line = f" | saved-text line {c['source_line']}" if c.get("source_line") else ""
            detail = f"{c['reported_value']} {c['unit']} | {c['tag']} | period {c['period_end']} | {c['filing']} accession {c['accession']}{line}"
        elif c["kind"] == "ratio":
            detail = f"{float(c['reported_value']):.8g} | formula: {c['formula']} | inputs: {json.dumps(c['inputs'], sort_keys=True)}"
        else:
            detail = f"{c['reported_value']} | {c['filing']} accession {c['accession']} line {c['source_line']} | quote: {c['source_excerpt']}"
        lines.append(f"- {marker} {c['id'].split(':',1)[-1]}: {detail}")
    return lines


def verifier_node(report: str, claims: list[dict[str, Any]], out: Path,
                  company_data: list[dict[str, Any]], model: str, key: str, base_url: str) -> list[dict[str, Any]]:
    code_marks = code_verify_claims(claims, out, report)
    save_json(out / "code_verification.json", code_marks)
    # The semantic checker sees only the compiled report, saved filing text, and saved facts.
    filing_texts: dict[str, dict[str, str]] = {}
    company_by_ticker = {c["facts"]["ticker"]: c for c in company_data}
    for claim in claims:
        ticker = claim.get("ticker")
        if ticker not in company_by_ticker:
            continue
        form = claim.get("filing", "10-K")
        source = company_by_ticker[ticker]["filing_texts"].get(form, "")
        if not source:
            continue
        lines = source.splitlines()
        line_no = claim.get("source_line")
        if not isinstance(line_no, int):
            continue
        lo, hi = max(1, line_no - 2), min(len(lines), line_no + 2)
        filing_texts.setdefault(ticker, {})[f"{form} lines {lo}-{hi}"] = "\n".join(
            f"{i}: {lines[i - 1]}" for i in range(lo, hi + 1)
        )
    facts = {c["facts"]["ticker"]: c["facts"] for c in company_data}
    task = ("For each cited claim, check that the cited filing line or tag supports the value, period, and definition. "
            "Skip the Investment Advisor's thesis. Do not judge its recommendation. Return JSON array with id, mark, reason, correction.")
    semantic = call_node("Verifier", task,
                         {"compiled_report": report, "saved_filing_texts": filing_texts,
                          "saved_facts": facts},
                         "JSON array of marks: correct, wrong, or unsupported.", out, model, key, base_url)
    try:
        parsed = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", semantic, flags=re.I))
        if isinstance(parsed, dict):
            parsed = parsed.get("marks", [])
        semantic_map = {}
        for item in parsed:
            if not isinstance(item, dict) or not item.get("id"):
                continue
            claim_id = item["id"]
            semantic_map[claim_id] = item
            semantic_map.setdefault("claim:" + claim_id, item)
    except (json.JSONDecodeError, TypeError) as exc:
        raise RuntimeError("Verifier did not return the required JSON marks.") from exc
    # Deterministic failures take precedence. The model can downgrade a pass but cannot erase a code failure.
    for item in code_marks:
        model_mark = semantic_map.get(item["id"], {}).get("mark")
        if model_mark not in {"correct", "wrong", "unsupported"}:
            item["mark"] = "unsupported"
            item["reason"] = "Semantic verifier did not return a valid mark for this claim."
            continue
        if item["mark"] == "correct" and model_mark in {"wrong", "unsupported"}:
            item["mark"] = model_mark
            item["reason"] = "Semantic verifier: " + str(semantic_map[item["id"]].get("reason", "source meaning not confirmed"))
            item["correction"] = semantic_map[item["id"]].get("correction") or item["correction"]
    return code_marks


def save_verified_report(path: Path, first_line: str, timestamp: str, body: str,
                         marks: list[dict[str, Any]]) -> None:
    table = ["## Verifier marks", "", "| Claim | Mark | Reason | Source | Correction |", "|---|---|---|---|---|"]
    table.extend(f"| {m['id']} | {m['mark']} | {m['reason'].replace('|', '/')} | {m.get('source', '').replace('|', '/')} | {m.get('correction')} |" for m in marks)
    content = f"{first_line}\nRun time: {timestamp}\n\n" + "\n".join(table) + "\n\n" + body.strip() + "\n"
    path.write_text(content, encoding="utf-8")


def load_verification_run(run_dir: Path) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    report_path = run_dir / "report.md"
    if not report_path.exists():
        report_path = run_dir / "verified_report.md"
    if not report_path.exists():
        raise FileNotFoundError(f"No report.md or verified_report.md in {run_dir}")
    first = report_path.read_text(encoding="utf-8").splitlines()[0]
    report = report_path.read_text(encoding="utf-8")
    claims = json.loads((run_dir / "claims.json").read_text(encoding="utf-8"))
    companies = []
    for folder in sorted(p for p in run_dir.iterdir() if p.is_dir() and (p / f"{p.name}_facts.json").exists()):
        data = json.loads((folder / f"{folder.name}_facts.json").read_text(encoding="utf-8"))
        filings = {}
        for form, meta in data["filings"].items():
            txt_path = folder / (f"{form.replace('-', '')}_{meta['accession']}.txt")
            if txt_path.exists():
                filings[form] = txt_path.read_text(encoding="utf-8")
        companies.append({"facts": data, "filing_texts": filings})
    return first, claims, [{"report": report, "companies": companies}]


def verify_only(run_dir: Path, env: dict[str, str]) -> int:
    first, claims, payload = load_verification_run(run_dir)
    report, companies = payload[0]["report"], payload[0]["companies"]
    base_url = env.get("GENAI_API_BASE", desk.GENAI_API)
    key = env.get("API_KEY") or env.get("PURDUE_GENAI_API_KEY")
    if not key:
        raise RuntimeError("Set API_KEY in .env to run the Verifier node.")
    model = model_name(env, key, base_url)
    marks = verifier_node(report, claims, run_dir, companies, model, key, base_url)
    save_json(run_dir / "verification_marks.json", marks)
    save_verified_report(run_dir / "verified_report.md", first, datetime.now().astimezone().isoformat(timespec="seconds"), report, marks)
    print(f"Verified report: {run_dir / 'verified_report.md'}")
    return 0


def numbered_sections(company: dict[str, Any]) -> tuple[str, str, str]:
    tenk = company["filing_texts"]["10-K"]
    facts = company["facts"]
    business = re.search(r"ITEM\s+1\.?\s+BUSINESS", tenk, re.I)
    mda = re.search(r"ITEM\s+7\.?\s+MANAGEMENT.{0,30}DISCUSSION", tenk, re.I)
    rows = tenk.splitlines()

    def extract(match: re.Match[str] | None, limit: int) -> str:
        if not match:
            return "Section not found."
        start = tenk[:match.start()].count("\n")
        selected, size = [], 0
        for idx in range(start, len(rows)):
            row = f"10-K accession {facts['filings']['10-K']['accession']} line {idx + 1}: {rows[idx]}"
            if size + len(row) > limit:
                break
            selected.append(row)
            size += len(row)
        return "\n".join(selected)

    business_text = extract(business, 15000)
    mda_text = extract(mda, 17000)
    release = company["filing_texts"].get("8-K", "")
    relevant = "\n".join(desk.release_claims(release))
    return business_text, mda_text, relevant


def manager_check(parts: dict[str, str], company: dict[str, Any], out: Path,
                  model: str, key: str, base_url: str,
                  numeric_audit: list[str] | None = None) -> dict[str, Any]:
    raw = call_node("Strategy Manager", "Check the five required report parts for completeness and consistency. Return PASS or identify one part for a single repair.",
                    {"ticker": company["facts"]["ticker"], "parts": parts, "required_parts": PARTS,
                     "source_facts": company["facts"]["facts"],
                     "automatic_numeric_audit": numeric_audit or []},
                    '{"status":"PASS"|"FAIL","failing_part":string|null,"repair_request":string|null}',
                    out, model, key, base_url)
    try:
        result = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.I))
    except json.JSONDecodeError as exc:
        raise RuntimeError("Strategy Manager did not return valid JSON.") from exc
    if str(result.get("status", "")).upper() != "PASS" and result.get("failing_part") not in PARTS:
        raise RuntimeError("Strategy Manager failed without naming one valid report part.")
    return result


def run_team(ticker: str, peers: list[str], price: float | None,
             price_date: str | None, price_source: str | None,
             env: dict[str, str]) -> int:
    key = env.get("API_KEY") or env.get("PURDUE_GENAI_API_KEY")
    if not key:
        raise RuntimeError("Set API_KEY in .env before the agent run.")
    base_url = env.get("GENAI_API_BASE", desk.GENAI_API)
    model = model_name(env, key, base_url)
    print(f"Purdue GenAI Studio model: {model}")
    ua = env.get("SEC_USER_AGENT", "")
    if not ua:
        raise RuntimeError("Set SEC_USER_AGENT in .env before the data steps.")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RUNS / f"{ticker}_{stamp}"
    out.mkdir(parents=True, exist_ok=False)
    print(f"Run folder: {out}")
    print("Running node: Seven SEC data steps", flush=True)
    companies = []
    for symbol in [ticker, *peers]:
        company, _ = desk.facts_for_company(symbol, ua, out)
        companies.append(company)
    desk.print_calculations(companies, price)
    desk.print_release_and_peers(companies)
    for company in companies:
        company["ratios"] = desk.calc_ratios(company, price if company is companies[0] else None)
    save_json(out / "run_state.json", {"ticker": ticker, "peers": peers, "price": price,
                                      "run_time": datetime.now().astimezone().isoformat(timespec="seconds"),
                                      "filings": [c["facts"]["filings"] for c in companies]})
    nodes = out / "nodes"
    nodes.mkdir(exist_ok=True)
    save_json(nodes / "steps_input.json", {"tickers": [ticker, *peers], "price": price,
                                             "price_date": price_date, "price_source": price_source})
    save_json(nodes / "steps_output.json", [{"ticker": c["facts"]["ticker"], "facts": c["facts"],
                                              "ratios": c["ratios"], "quarter": c["quarter"]}
                                             for c in companies])
    main = companies[0]
    business, mda, release = numbered_sections(main)
    research = call_node("Research Analyst", "In no more than 220 words, describe business model, competitive position, catalysts, and recent developments. Every factual claim needs an exact quote with filing, section, accession, and saved-text line.",
                         {"10-K Item 1 Business": business, "10-K Item 7 MD&A": mda,
                          "earnings release relevant lines": release},
                         "Concise Markdown with source-supported claims and exact line references.", out, model, key, base_url)
    finance = call_node("Financial Analyst", "In no more than 100 words, interpret the code-calculated facts, ratios, quarter, and peers. Do not reproduce evidence tables or recalculate. Cite every number with its filing/tag, period, and accession. Show supplied ratio arithmetic and the selected revenue definition. End with CALCULATOR_REQUESTS: NONE.",
                        {"code_calculated_evidence": desk.financial_evidence(companies, price, price_date, price_source),
                         "available_calculator_requests": ["debt_to_revenue", "operating_cash_flow_margin", "capex_to_revenue"]},
                        "Concise Markdown with sourced numbers and supplied formulas.", out, model, key, base_url)
    advisor = call_node("Investment Advisor", "In no more than 120 words, write a thesis and choose Buy, Hold, or Sell. Name one deciding number. Use only the Research Analyst and Financial Analyst outputs.",
                        {"Research Analyst": research, "Financial Analyst": finance},
                        "A thesis, one supported deciding number, and one recommendation.", out, model, key, base_url)
    evidence = desk.financial_evidence(companies, price, price_date, price_source)
    parts = {
        "Overview": f"Ticker: {ticker}. Fiscal year ended {main['facts']['fiscal_year_end']}. Filings: " + "; ".join(f"{f} {main['facts']['filings'][f]['accession']}" for f in ("10-K", "10-Q", "8-K")),
        "Market Positioning and Growth Outlook": research,
        "Valuation Insights": evidence + "\n\nFinancial Analyst interpretation:\n\n" + finance,
        "Future Developments and Strategic Recommendations": "Research findings:\n\n" + research + "\n\nFinancial findings:\n\n" + finance,
        "Investment Recommendation": advisor,
    }
    numeric_audit = percentage_claim_audit(finance, companies)
    manager = manager_check(parts, main, out, model, key, base_url, numeric_audit)
    if str(manager.get("status", "")).upper() != "PASS":
        heading = manager["failing_part"]
        repair_role = ("Research Analyst" if heading == "Market Positioning and Growth Outlook" else
                       "Financial Analyst" if heading in {"Valuation Insights", "Future Developments and Strategic Recommendations"} else
                       "Investment Advisor" if heading == "Investment Recommendation" else "Strategy Manager")
        context = {"current_part": parts[heading], "manager_request": manager.get("repair_request"),
                   "evidence": business if repair_role == "Research Analyst" else evidence,
                   "role_outputs": {"Research Analyst": research, "Financial Analyst": finance},
                   "automatic_numeric_audit": numeric_audit}
        repaired = call_node(repair_role, f"Repair {heading} once, using only the evidence supplied.", context,
                             "The revised report part only.", out, model, key, base_url)
        if repair_role == "Financial Analyst":
            finance = repaired
            parts["Valuation Insights"] = evidence + "\n\nFinancial Analyst interpretation:\n\n" + finance
            parts["Future Developments and Strategic Recommendations"] = "Research findings:\n\n" + research + "\n\nFinancial findings:\n\n" + finance
        else:
            parts[heading] = repaired
        numeric_audit = percentage_claim_audit(finance, companies)
        if numeric_audit:
            parts["Valuation Insights"] += "\n\nManager note: Financial Analyst numeric check remains unresolved after the one permitted repair. " + "; ".join(numeric_audit)

    claims = claim_ledger(companies, price)
    save_json(out / "claims.json", claims)
    body = "\n\n".join(f"## {part}\n\n{text}" for part, text in parts.items())
    body += "\n\n" + "\n".join(report_claim_lines(claims))
    filing_line = "Filings read: " + "; ".join(f"{f} {main['facts']['filings'][f]['accession']}" for f in ("10-K", "10-Q", "8-K"))
    report_path = out / "report.md"
    report_path.write_text(f"{filing_line}\nRun time: {datetime.now().astimezone().isoformat(timespec='seconds')}\n\n{body}\n", encoding="utf-8")
    marks = verifier_node(report_path.read_text(encoding="utf-8"), claims, out, companies, model, key, base_url)
    save_json(out / "verification_marks.json", marks)
    save_verified_report(out / "verified_report.md", filing_line,
                         datetime.now().astimezone().isoformat(timespec="seconds"), body, marks)
    save_json(out / "node_order.json", ["Seven SEC data steps", "Research Analyst", "Financial Analyst",
                                       "Investment Advisor", "Strategy Manager", "Verifier"])
    print(f"Verified report: {out / 'verified_report.md'}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run or verify the fixed FIN 67110 agent team")
    parser.add_argument("ticker", nargs="?", help="SEC ticker symbol")
    parser.add_argument("--peers", default="", help="comma-separated SEC peer tickers")
    parser.add_argument("--price", type=float, help="share price for P/E")
    parser.add_argument("--price-date", help="date for the supplied price")
    parser.add_argument("--price-source", help="source for the supplied price")
    parser.add_argument("--verify-only", type=Path, help="verify a saved run folder, with no data or analyst rerun")
    args = parser.parse_args()
    env = desk.load_env()
    try:
        if args.verify_only:
            return verify_only(args.verify_only.resolve(), env)
        if not args.ticker:
            parser.error("ticker is required unless --verify-only is set")
        if not re.fullmatch(r"[A-Za-z0-9.-]+", args.ticker):
            parser.error("ticker must be a ticker symbol")
        peers = [item.strip().upper() for item in args.peers.split(",") if item.strip()]
        return run_team(args.ticker.upper(), peers, args.price, args.price_date, args.price_source, env)
    except Exception as exc:
        print(f"Agent team failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
