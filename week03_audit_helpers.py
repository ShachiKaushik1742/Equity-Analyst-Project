from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import desk

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
PARTS = ["Overview", "Market Positioning and Growth Outlook", "Valuation Insights", "Future Developments and Strategic Recommendations", "Investment Recommendation"]

def analyst_insight_audit(outputs: dict[str, str]) -> list[dict[str, str]]:
    """Check analyst outputs for one sourced insight line each."""
    required = {
        "Research Analyst": "Market Positioning and Growth Outlook",
        "Financial Analyst": "Valuation Insights",
        "Investment Advisor": "Investment Recommendation",
    }
    issues: list[dict[str, str]] = []
    for role, part in required.items():
        text = outputs.get(role, "") or ""
        lines = [line.strip() for line in text.splitlines()
                 if re.match(r"(?i)^\*{0,2}Insight\s*:\*{0,2}", line.strip())]
        issue = None
        if len(lines) != 1:
            issue = f"{role} output must contain exactly one Insight: line; found {len(lines)}."
        else:
            insight = re.sub(r"(?i)^\*{0,2}Insight\s*:\*{0,2}", "", lines[0]).strip()
            if not insight:
                issue = f"{role} Insight: line is empty."
            elif not re.search(r"(?i)\b(?:10[-‐‑–—]K|10[-‐‑–—]Q|8[-‐‑–—]K)\b", insight) or not re.search(
                    r"(?i)\b(?:saved-text\s+)?line\s+\d+\b|\btag\s+[A-Za-z][A-Za-z0-9]+", insight):
                issue = f"{role} Insight: line must cite a filing and exact saved-text line or XBRL tag."
        if issue:
            issues.append({"role": role, "part": part, "issue": issue})
    return issues

def save_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def save_node_record(run_dir: Path, name: str, node_input: Any, node_output: Any) -> None:
    """Save input and output for a deterministic Flow node."""
    node_dir = run_dir / "nodes"
    node_dir.mkdir(exist_ok=True)
    save_json(node_dir / f"{name}_input.json", node_input)
    save_json(node_dir / f"{name}_output.json", node_output)


def omit_report_part(report: str, heading: str) -> str:
    """Remove one Markdown section before sending a report copy to the Verifier."""
    lines = report.splitlines()
    target = f"## {heading}".casefold()
    start = next((i for i, line in enumerate(lines) if line.strip().casefold() == target), None)
    if start is None:
        return report
    end = next((i for i in range(start + 1, len(lines))
                if re.match(r"^##\s+", lines[i])), len(lines))
    return "\n".join(lines[:start] + ["## Investment Advisor thesis omitted for verification."] + lines[end:])


def cited_filing_evidence(claims: list[dict[str, Any]],
                          companies: list[dict[str, Any]],
                          context_lines: int = 2) -> dict[str, dict[str, str]]:
    """Return numbered excerpts around cited lines from the saved filings.

    Keep the Verifier's input focused on evidence already cited in the report.
    This avoids sending full 10-Ks to a model with a finite context window.
    The filing files themselves remain unchanged in the run folder.
    """
    by_ticker = {company["facts"]["ticker"]: company for company in companies}
    excerpts: dict[str, dict[str, list[str]]] = {}
    seen: dict[tuple[str, str], set[int]] = {}
    for claim in claims:
        ticker = claim.get("ticker")
        company = by_ticker.get(ticker)
        filing = claim.get("filing")
        line_number = claim.get("source_line")
        if not company or not filing or not isinstance(line_number, int):
            continue
        source = company.get("filing_texts", {}).get(filing, "")
        lines = source.splitlines()
        if not (1 <= line_number <= len(lines)):
            continue
        key = (ticker, filing)
        included = seen.setdefault(key, set())
        start, end = max(1, line_number - context_lines), min(len(lines), line_number + context_lines)
        new_lines = [n for n in range(start, end + 1) if n not in included]
        if not new_lines:
            continue
        meta = company["facts"].get("filings", {}).get(filing, {})
        accession = claim.get("accession") or meta.get("accession", "unknown accession")
        bucket = excerpts.setdefault(ticker, {}).setdefault(filing, [])
        bucket.append(f"{filing} accession {accession}; saved-text lines {start}-{end}:")
        bucket.extend(f"{number} | {lines[number - 1]}" for number in new_lines)
        included.update(new_lines)
    return {ticker: {filing: "\n".join(chunks)
                     for filing, chunks in filings.items()}
            for ticker, filings in excerpts.items()}

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
                    "return_on_average_equity": "net_income / ((current_equity + prior_equity) / 2)",
                    "debt_to_equity": "(long_term_debt + current_portion_debt) / current_equity",
                    "free_cash_flow": "cash_from_operations - additions_to_property_and_equipment",
                    "pe": "price / diluted_eps",
                }[name],
                "definition": {
                    "revenue_growth": "(latest fiscal-year revenue / prior fiscal-year revenue) - 1",
                    "operating_margin": "operating income / latest fiscal-year revenue",
                    "return_on_average_equity": "net income / average of current and prior year-end equity",
                    "debt_to_equity": "(long-term debt + current portion of long-term debt) / current year-end equity",
                    "free_cash_flow": "cash from operations - additions to property and equipment",
                    "pe": "supplied share price / diluted EPS for the selected fiscal year",
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


def financial_amount_audit(text: str, companies: list[dict[str, Any]], price: float | None) -> list[str]:
    """Flag dollar amounts in finance prose that are not facts or code outputs."""
    known: list[float] = []

    def add(value: Any) -> None:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return
        if number >= 0:
            known.append(number)

    for company_index, company in enumerate(companies):
        facts = company.get("facts", {}).get("facts", {})
        for fact in facts.values():
            if fact:
                add(fact.get("value"))
        ratios = company.get("ratios", {})
        for value in ratios.values():
            if isinstance(value, (int, float)):
                add(value)
        inputs = ratios.get("inputs", {})
        for value in inputs.values():
            if isinstance(value, (int, float)):
                add(value)
        if company_index == 0:
            current_equity = inputs.get("current_equity")
            prior_equity = inputs.get("prior_equity")
            if current_equity is not None and prior_equity is not None:
                add((float(current_equity) + float(prior_equity)) / 2)
            quarter = company.get("quarter", {})
            for key in ("revenue_current", "revenue_prior_quarter"):
                if quarter.get(key) is not None:
                    add(float(quarter[key]) * 1_000_000)
            for key in ("diluted_eps_current", "diluted_eps_prior_quarter"):
                add(quarter.get(key))
    if price is not None:
        add(price)

    scale_for = {"": 1.0, "k": 1_000.0, "thousand": 1_000.0,
                 "m": 1_000_000.0, "million": 1_000_000.0,
                 "b": 1_000_000_000.0, "bn": 1_000_000_000.0, "billion": 1_000_000_000.0}
    issues = []
    pattern = r"(?<![\w.])\$\s*([\d,]+(?:\.\d+)?)\s*(billion|million|thousand|bn|[bmk])?\b"
    for match in re.finditer(pattern, text, flags=re.I):
        displayed = float(match.group(1).replace(",", ""))
        scale = scale_for[(match.group(2) or "").lower()]
        actual = displayed * scale
        decimals = len(match.group(1).partition(".")[2])
        tolerance = 0.5 * scale * (10 ** -decimals) + 1e-6
        if not any(abs(actual - expected) <= tolerance for expected in known):
            issues.append(f"Unsupported dollar amount {match.group(0).strip()}; use only filing facts or code-calculated amounts.")
    return issues


def financial_period_audit(text: str, company: dict[str, Any]) -> list[str]:
    """Catch quarter growth mislabeled as sequential-quarter growth."""
    quarter = company.get("quarter", {})
    if quarter.get("revenue_current") is None or quarter.get("revenue_prior_quarter") is None:
        return []
    if re.search(r"\b(?:QoQ|Q/Q|quarter[- ]over[- ]quarter|quarter on quarter)\b", text, re.I):
        return ["Quarter revenue growth compares the same quarter last year; label it YoY, not QoQ."]
    return []

def code_verify_claims(claims: list[dict[str, Any]], run_dir: Path,
                       report_text: str) -> list[dict[str, Any]]:
    """Verify source existence, exact tags/periods, report values, and arithmetic."""
    marks = []
    for claim in claims:
        reason = ""
        corrected = None
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
                  or claim.get("definition", claim.get("formula", "")) not in report_line
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
                norm = lambda value: re.sub(r"[^a-z0-9.$%-]", "", value.casefold())
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
            detail = f"{float(c['reported_value']):.8g} | definition: {c.get('definition', c['formula'])} | formula: {c['formula']} | inputs: {json.dumps(c['inputs'], sort_keys=True)}"
        else:
            detail = f"{c['reported_value']} | {c['filing']} accession {c['accession']} line {c['source_line']} | quote: {c['source_excerpt']}"
        lines.append(f"- {marker} {c['id'].split(':',1)[-1]}: {detail}")
    return lines


def source_lines(company: dict[str, Any], key: str) -> tuple[int | None, str]:
    """Find the statement row that supports one saved XBRL fact."""
    fact = company["facts"]["facts"].get(key)
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

def save_verified_report(path: Path, first_line: str, timestamp: str, body: str,
                         marks: list[dict[str, Any]]) -> None:
    table = ["## Verifier marks", "", "| Claim | Mark | Reason | Source | Correction |", "|---|---|---|---|---|"]
    table.extend(f"| {m['id']} | {m['mark']} | {m['reason'].replace('|', '/')} | {m.get('source', '').replace('|', '/')} | {m.get('correction')} |" for m in marks)
    content = f"{first_line}\n\n" + "\n".join(table) + f"\n\nRun time: {timestamp}\n\n" + body.strip() + "\n"
    path.write_text(content, encoding="utf-8")

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
