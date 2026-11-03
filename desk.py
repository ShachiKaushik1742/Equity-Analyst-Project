#!/usr/bin/env python3
"""Ticker-driven SEC research desk for FIN 67110 Labs 02 and 03.

The data steps use SEC filings and XBRL facts. Model calls are optional and
use Purdue GenAI Studio's OpenAI-compatible chat-completions API.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import ssl
import sys
import time
from datetime import datetime
from http.client import RemoteDisconnected
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


SEC = "https://www.sec.gov"
DATA_SEC = "https://data.sec.gov"
GENAI_API = "https://genai.rcac.purdue.edu/api"
ROOT = Path(__file__).resolve().parent


def sec_ssl_context() -> ssl.SSLContext:
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def load_env() -> dict[str, str]:
    values = dict(os.environ)
    path = ROOT / ".env"
    if path.exists():
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            value = value.strip().strip("\"'")
            values.setdefault(key.strip(), value)
    return values


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_d = dict(attrs)
        if tag in {"script", "style", "ix:header"} or attrs_d.get("aria-hidden") == "true":
            self.hidden += 1
        if tag in {"p", "div", "tr", "br", "li", "h1", "h2", "h3", "table"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "ix:header"} and self.hidden:
            self.hidden -= 1
        if tag in {"p", "div", "tr", "li", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            text = re.sub(r"\s+", " ", data).strip()
            if text:
                self.parts.append(text + " ")


def plain_text(document: bytes) -> str:
    decoded = document.decode("utf-8", errors="replace")
    parser = TextExtractor()
    parser.feed(decoded)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in "".join(parser.parts).splitlines()]
    return "\n".join(line for line in lines if line)


def get_json(url: str, ua: str) -> Any:
    req = Request(url, headers={"User-Agent": ua, "Accept-Encoding": "gzip, deflate", "Host": url.split("/")[2]})
    payload = request_bytes(req, 45)
    if payload[:2] == b"\x1f\x8b":
        import gzip
        payload = gzip.decompress(payload)
    return json.loads(payload)


def get_bytes(url: str, ua: str) -> bytes:
    req = Request(url, headers={"User-Agent": ua, "Accept-Encoding": "gzip, deflate"})
    payload = request_bytes(req, 60)
    if payload[:2] == b"\x1f\x8b":
        import gzip
        payload = gzip.decompress(payload)
    return payload


def request_bytes(req: Request, timeout: int) -> bytes:
    for attempt in range(3):
        try:
            with urlopen(req, timeout=timeout, context=sec_ssl_context()) as response:
                return response.read()
        except HTTPError as exc:
            if exc.code not in {429, 500, 502, 503, 504} or attempt == 2:
                raise
        except (URLError, RemoteDisconnected, TimeoutError, ConnectionResetError):
            if attempt == 2:
                raise
        time.sleep(0.5 * (attempt + 1))
    raise RuntimeError("SEC request failed after retries")


def accession_folder(accession: str) -> str:
    return accession.replace("-", "")


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def resolve_ticker(ticker: str, ua: str) -> tuple[int, str]:
    records = get_json(f"{SEC}/files/company_tickers.json", ua)
    target = ticker.upper()
    for row in records.values():
        if row["ticker"].upper() == target:
            return int(row["cik_str"]), row["title"]
    raise ValueError(f"Ticker not found in SEC company_tickers.json: {target}")


def submissions(cik: int, ua: str) -> dict[str, Any]:
    return get_json(f"{DATA_SEC}/submissions/CIK{cik:010}.json", ua)


def recent_rows(subs: dict[str, Any]) -> list[dict[str, str]]:
    recent = subs["filings"]["recent"]
    rows = []
    for i, form in enumerate(recent["form"]):
        rows.append({key: str(recent[key][i]) for key in recent if i < len(recent[key])})
    return rows


def filing_url(cik: int, row: dict[str, str], filename: str | None = None) -> str:
    base = f"{SEC}/Archives/edgar/data/{cik}/{accession_folder(row['accessionNumber'])}"
    return f"{base}/{quote(filename)}" if filename else f"{base}/index.json"


def index_for(cik: int, row: dict[str, str], ua: str) -> dict[str, Any]:
    return get_json(filing_url(cik, row), ua)


def is_earnings_8k(cik: int, row: dict[str, str], ua: str) -> tuple[bool, dict[str, Any]]:
    index = index_for(cik, row, ua)
    items = index.get("directory", {}).get("item", [])
    primary = row.get("primaryDocument", "")
    candidates = [item["name"] for item in items if item.get("type") == "8-K" or item.get("name") == primary]
    if primary and primary not in candidates:
        candidates.insert(0, primary)
    for name in candidates[:4]:
        if not name.lower().endswith((".htm", ".html")):
            continue
        try:
            text = plain_text(get_bytes(filing_url(cik, row, name), ua))
        except (HTTPError, URLError):
            continue
        if re.search(r"ITEM\s+2\.02\b", text, re.IGNORECASE):
            return True, index
    return False, index


def choose_filings(cik: int, subs: dict[str, Any], ua: str) -> tuple[dict[str, str], dict[str, Any]]:
    rows = recent_rows(subs)
    annual = next((r for r in rows if r["form"] == "10-K"), None)
    quarterly = next((r for r in rows if r["form"] == "10-Q"), None)
    earnings = None
    earnings_index = None
    for row in rows:
        if row["form"] == "8-K":
            yes, idx = is_earnings_8k(cik, row, ua)
            if yes:
                earnings, earnings_index = row, idx
                break
            time.sleep(0.12)
    if not annual or not quarterly or not earnings:
        raise RuntimeError("Could not identify latest 10-K, 10-Q, and 8-K reporting Item 2.02.")
    selected = {"10-K": annual, "10-Q": quarterly, "8-K": earnings}
    for form, row in selected.items():
        idx = earnings_index if form == "8-K" else index_for(cik, row, ua)
        row["accepted"] = idx.get("acceptanceDateTime", row.get("acceptanceDateTime", ""))
        row["filingDate"] = idx.get("filingDate", row.get("filingDate", ""))
        row["indexFiles"] = idx.get("directory", {}).get("item", [])
    return selected, {"earnings_index": earnings_index}


def candidate_facts(company_facts: dict[str, Any], tags: list[str], form: str = "10-K") -> dict[str, list[dict[str, Any]]]:
    units = company_facts.get("facts", {}).get("us-gaap", {})
    found: dict[str, list[dict[str, Any]]] = {}
    for tag in tags:
        block = units.get(tag)
        if not block:
            continue
        all_values: list[dict[str, Any]] = []
        for unit, entries in block.get("units", {}).items():
            for entry in entries:
                if entry.get("form") == form and entry.get("fp") == "FY" and entry.get("val") is not None:
                    all_values.append({**entry, "unit": unit, "tag": tag})
        if all_values:
            found[tag] = all_values
    return found


def pick_fact(facts: dict[str, Any], tags: list[str], fy_end: str, accession: str | None = None,
              instant: bool = False) -> dict[str, Any] | None:
    options = candidate_facts(facts, tags)
    candidates = [x for rows in options.values() for x in rows]
    candidates = [x for x in candidates if x.get("end") == fy_end]
    if accession:
        exact = [x for x in candidates if x.get("accn") == accession]
        if exact:
            candidates = exact
    if not candidates:
        # Include 10-K amendment and facts without fp=FY only as an explicit fallback.
        units = facts.get("facts", {}).get("us-gaap", {})
        for tag in tags:
            for unit, entries in units.get(tag, {}).get("units", {}).items():
                for entry in entries:
                    if entry.get("form") == "10-K" and entry.get("end") == fy_end and entry.get("val") is not None:
                        candidates.append({**entry, "unit": unit, "tag": tag})
        if accession:
            exact = [x for x in candidates if x.get("accn") == accession]
            if exact:
                candidates = exact
    if not candidates:
        return None
    # Prefer the candidate tag with the newest reported period, then latest filed.
    candidates.sort(key=lambda x: (x.get("filed", ""), x.get("accn", "")), reverse=True)
    return candidates[0]


CONCEPTS = {
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"],
    "operating_income": ["OperatingIncomeLoss"],
    "net_income": ["NetIncomeLossAttributableToParent", "NetIncomeLoss"],
    "diluted_eps": ["EarningsPerShareDiluted"],
    "equity": ["StockholdersEquity"],
    # Prefer the non-current balance-sheet concept. Some filers also tag total
    # term debt as LongTermDebt; adding its current portion would double-count it.
    "long_term_debt": ["LongTermDebtNoncurrent", "LongTermDebtAndFinanceLeaseObligationsNoncurrent", "LongTermDebt"],
    "current_debt": ["LongTermDebtCurrent", "LongTermDebtAndFinanceLeaseObligationsCurrent", "LongTermDebtAndCapitalLeaseObligationsCurrent", "OtherLongTermDebtCurrent"],
    "cash_from_operations": ["NetCashProvidedByUsedInOperatingActivities"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"],
}


def fact_value(facts: dict[str, Any], concept: str, fy_end: str, accession: str | None = None) -> dict[str, Any] | None:
    return pick_fact(facts, CONCEPTS[concept], fy_end, accession)


def report_fact(label: str, fact: dict[str, Any] | None) -> dict[str, Any] | None:
    if not fact:
        return None
    return {"label": label, "value": fact["val"], "unit": fact["unit"], "tag": fact["tag"],
            "period_start": fact.get("start"), "period_end": fact.get("end"),
            "filing": fact.get("form"), "filed": fact.get("filed"), "accession": fact.get("accn")}


def revenue_statement_source(company: dict[str, Any]) -> tuple[str, int] | None:
    """Find the income-statement label and line that contains the selected top-line value."""
    fact = company.get("facts", {}).get("facts", {}).get("revenue")
    text = company.get("filing_texts", {}).get("10-K", "")
    if not fact or not text:
        return None
    amount = f"{int(round(float(fact['value']) / 1_000_000)):,}"
    rows = text.splitlines()
    statement_headings = [i for i, row in enumerate(rows)
                         if re.fullmatch(r"\s*Consolidated Statements of (?:Income|Operations|Earnings)(?: and Comprehensive Income)?\s*", row, re.IGNORECASE)]
    candidates: list[tuple[int, str, int]] = []
    for index, row in enumerate(rows):
        if amount not in row:
            continue
        previous_headings = [i for i in statement_headings if i <= index]
        if not previous_headings:
            continue
        heading = previous_headings[-1]
        if index - heading > 160:
            continue
        context = rows[max(heading + 1, index - 5):index + 1]
        labels = [re.match(r"^(Total revenues?|Net sales)\b", x.strip(), re.IGNORECASE).group(1)
                  for x in context if re.match(r"^(?:Total revenues?|Net sales)\b", x.strip(), re.IGNORECASE)]
        if labels:
            candidates.append((index - heading, labels[-1], index + 1))
    if candidates:
        _, label, line_number = min(candidates, key=lambda x: x[0])
        return label, line_number
    return None


def earnings_release_quotes(company: dict[str, Any]) -> str:
    """Return exact revenue and diluted-EPS lines with stable saved-text line numbers."""
    lines = company.get("filing_texts", {}).get("8-K", "").splitlines()
    quarter = company.get("quarter", {})
    accession = company.get("facts", {}).get("filings", {}).get("8-K", {}).get("accession", "")
    quotes = []
    for label, label_key, value_key in (
        ("total revenue", "revenue_release_line_number", "revenue_number_line_number"),
        ("diluted EPS", "eps_release_line_number", "eps_number_line_number"),
    ):
        start = quarter.get(label_key)
        end = quarter.get(value_key) or start
        if isinstance(start, int) and isinstance(end, int) and 1 <= start <= end <= len(lines):
            exact_text = " ".join(line.strip() for line in lines[start - 1:end] if line.strip())
            cited_lines = f"line {start}" if start == end else f"lines {start}-{end}"
            quotes.append(f'{label}: “{exact_text}” (8-K accession {accession}, Exhibit 99.1, saved-text {cited_lines}).')
    return "\n".join(quotes)


def duration_fact(facts: dict[str, Any], tags: list[str], period_start: str, period_end: str,
                  accession: str | None = None, forms: tuple[str, ...] = ("10-K",)) -> dict[str, Any] | None:
    usgaap = facts.get("facts", {}).get("us-gaap", {})
    results = []
    for tag in tags:
        for unit, entries in usgaap.get(tag, {}).get("units", {}).items():
            for e in entries:
                if e.get("form") in forms and e.get("start") == period_start and e.get("end") == period_end:
                    results.append({**e, "tag": tag, "unit": unit})
    if accession:
        exact = [x for x in results if x.get("accn") == accession]
        if exact:
            results = exact
    results.sort(key=lambda x: x.get("filed", ""), reverse=True)
    return results[0] if results else None


def facts_for_company(ticker: str, ua: str, out: Path, peers: list[str] | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    company_out = out / ticker.upper()
    company_out.mkdir(parents=True, exist_ok=True)
    cik, title = resolve_ticker(ticker, ua)
    print(f"\n[{ticker.upper()}] Step 1 — CIK {cik:010}: {title}")
    subs = submissions(cik, ua)
    filings, _ = choose_filings(cik, subs, ua)
    print(f"[{ticker.upper()}] Step 2 — filings")
    for form, row in filings.items():
        print(f"  {form}: accession {row['accessionNumber']} | Accepted {row.get('accepted') or 'see filing index'}")

    filing_texts: dict[str, str] = {}
    metadata: dict[str, Any] = {"ticker": ticker.upper(), "title": title, "cik": f"{cik:010}", "filings": {}}
    for form, row in filings.items():
        index_files = row.get("indexFiles", [])
        if form == "8-K":
            docs = [f["name"] for f in index_files if f.get("name", "").lower().endswith((".htm", ".html"))
                    and re.search(r"earnings.?release|99[-.]?1|ex[-.]?99", f.get("name", ""), re.IGNORECASE)]
            if not docs:
                docs = [f["name"] for f in index_files if "EX-99.1" in f.get("type", "") or "EX-99" in f.get("type", "")]
        else:
            docs = [row.get("primaryDocument", "")]
        if not docs or not docs[0]:
            raise RuntimeError(f"No document found for {ticker} {form} accession {row['accessionNumber']}")
        doc = docs[0]
        raw = get_bytes(filing_url(cik, row, doc), ua)
        filing_texts[form] = plain_text(raw)
        (company_out / f"{form.replace('-', '')}_{row['accessionNumber']}.txt").write_text(filing_texts[form], encoding="utf-8")
        metadata["filings"][form] = {"accession": row["accessionNumber"], "accepted": row.get("accepted"),
                                       "filing_date": row.get("filingDate"), "document": doc,
                                       "index_url": filing_url(cik, row)}
        print(f"[{ticker.upper()}] Step 3 — saved plain text for {form}: {doc}")

    facts = get_json(f"{DATA_SEC}/api/xbrl/companyfacts/CIK{cik:010}.json", ua)
    annual = filings["10-K"]
    fy_end = annual.get("reportDate") or annual.get("periodOfReport") or annual.get("filingDate")
    if fy_end and len(fy_end) > 10:
        fy_end = fy_end[:10]
    # SEC submissions often omit reportDate in the recent array. Find it from the matching filing.
    recent = recent_rows(subs)
    match = next((r for r in recent if r.get("accessionNumber") == annual["accessionNumber"]), {})
    fy_end = match.get("reportDate") or fy_end
    if not fy_end:
        fy_end = max((entry.get("end", "") for rows in candidate_facts(facts, CONCEPTS["revenue"]).values() for entry in rows), default="")
    if not fy_end:
        raise RuntimeError(f"Could not determine fiscal year end for {ticker}")
    accession = annual["accessionNumber"]
    numeric: dict[str, Any] = {"ticker": ticker.upper(), "title": title, "cik": f"{cik:010}", "fiscal_year_end": fy_end,
                               "filings": metadata["filings"], "facts": {}}
    for name, tags in CONCEPTS.items():
        f = pick_fact(facts, tags, fy_end, accession)
        numeric["facts"][name] = report_fact(name, f)
    # Pick the two most recent annual revenue values on the same concept/tag.
    rev = numeric["facts"].get("revenue")
    if rev:
        fact_set = facts["facts"]["us-gaap"][rev["tag"]]["units"][rev["unit"]]
        annual_values = [e for e in fact_set if e.get("form") == "10-K" and e.get("end", "") <= fy_end and e.get("val") is not None]
        by_end: dict[str, dict[str, Any]] = {}
        for item in annual_values:
            if item.get("start") and item.get("end"):
                days = (datetime.fromisoformat(item["end"]) - datetime.fromisoformat(item["start"])).days
                if 300 <= days <= 400:
                    by_end[item["end"]] = item
        sorted_ends = sorted(by_end, reverse=True)
        previous = ({**by_end[sorted_ends[1]], "tag": rev["tag"], "unit": rev["unit"]}
                    if len(sorted_ends) > 1 else None)
        numeric["facts"]["revenue_prior_year"] = report_fact("revenue_prior_year", previous)
    numeric["quarter"] = quarter_metrics(filing_texts.get("8-K", ""))
    save_json(company_out / f"{ticker.upper()}_facts.json", numeric)
    print(f"[{ticker.upper()}] Step 4 — XBRL facts for FY ending {fy_end}")
    for key, fact in numeric["facts"].items():
        if fact:
            print(f"  {fact['label']}: {fact['value']} {fact['unit']} | {fact['tag']} | {fact.get('period_end')} | {fact.get('accession')}")
        else:
            print(f"  {key}: not found in company facts")
    return {"filing_texts": filing_texts, "metadata": metadata, "facts": numeric,
            "quarter": numeric["quarter"], "company_facts": facts}, filing_texts.get("8-K", "")


def calc_ratios(company: dict[str, Any], price: float | None) -> dict[str, Any]:
    f = company["facts"]["facts"]
    def value(name: str) -> float | None:
        v = f.get(name)
        return float(v["value"]) if v else None
    revenue, prior = value("revenue"), value("revenue_prior_year")
    op, net, eq = value("operating_income"), value("net_income"), value("equity")
    long_debt, curr_debt = value("long_term_debt"), value("current_debt")
    cfo, capex, eps = value("cash_from_operations"), value("capex"), value("diluted_eps")
    # SEC presents capex as a cash outflow (negative); normalize to positive additions.
    if capex is not None:
        capex = abs(capex)
    prior_eq = None
    prior_eq_fact = None
    if eq is not None:
        facts = company.get("company_facts")
        if not facts:
            cik = int(company["facts"]["cik"])
            facts = get_json(f"{DATA_SEC}/api/xbrl/companyfacts/CIK{cik:010}.json", os.environ.get("_FIN67110_SEC_UA", "FIN 67110 course research contact@example.edu"))
        eq_entries = candidate_facts(facts, CONCEPTS["equity"])
        rows = sorted((e for es in eq_entries.values() for e in es if e.get("end", "") < company["facts"]["fiscal_year_end"]), key=lambda e:e.get("end", ""), reverse=True)
        if rows:
            prior_eq = float(rows[0]["val"])
            prior_eq_fact = report_fact("prior_equity", rows[0])
    return {
        "revenue_growth": (revenue / prior - 1) if revenue is not None and prior else None,
        "operating_margin": op / revenue if op is not None and revenue else None,
        "return_on_average_equity": net / ((eq + prior_eq) / 2) if net is not None and eq is not None and prior_eq is not None else None,
        "debt_to_equity": ((long_debt or 0) + (curr_debt or 0)) / eq if eq else None,
        "free_cash_flow": cfo - capex if cfo is not None and capex is not None else None,
        "pe": price / eps if price is not None and eps else None,
        "inputs": {"price": price, "diluted_eps": eps, "current_equity": eq, "prior_equity": prior_eq,
                   "prior_equity_fact": prior_eq_fact,
                   "current_portion_debt": curr_debt, "long_term_debt": long_debt,
                   "cash_from_operations": cfo, "additions_to_property_and_equipment": capex},
    }


def print_calculations(companies: list[dict[str, Any]], price: float | None) -> None:
    print("\nStep 5 — calculator (ratios and arithmetic)")
    for c in companies:
        r = calc_ratios(c, price if c["facts"]["ticker"] == companies[0]["facts"]["ticker"] else None)
        c["ratios"] = r
        f = c["facts"]["facts"]
        def raw(name: str) -> Any:
            return f.get(name, {}).get("value") if f.get(name) else None
        print(f"  {c['facts']['ticker']}: revenue growth = ({raw('revenue')} / {raw('revenue_prior_year')}) - 1 = {r['revenue_growth']}")
        print(f"    operating margin = {raw('operating_income')} / {raw('revenue')} = {r['operating_margin']}")
        print(f"    return on average equity = {raw('net_income')} / (({r['inputs']['current_equity']} + {r['inputs']['prior_equity']}) / 2) = {r['return_on_average_equity']}")
        print(f"    debt/equity = ({r['inputs']['long_term_debt']} + {r['inputs']['current_portion_debt']}) / {r['inputs']['current_equity']} = {r['debt_to_equity']}")
        print(f"    free cash flow = {r['inputs']['cash_from_operations']} - {r['inputs']['additions_to_property_and_equipment']} = {r['free_cash_flow']}")
        if price is not None and c["facts"]["ticker"] == companies[0]["facts"]["ticker"]:
            print(f"    P/E = {price} / {raw('diluted_eps')} = {r['pe']}")
        else:
            print("    P/E = not calculated (no price supplied)")


def print_release_and_peers(companies: list[dict[str, Any]]) -> None:
    main = companies[0]
    print("\nStep 6 — earnings-release lines about revenue/EPS")
    for line in release_claims(main["filing_texts"]["8-K"]):
        print("  " + line[:300])
    print("\nStep 7 — peer facts and margins")
    for company in companies[1:]:
        facts = company["facts"]["facts"]
        print(f"  {company['facts']['ticker']}: revenue={facts.get('revenue')}; operating income={facts.get('operating_income')}; margin={company.get('ratios', {}).get('operating_margin')}")


def extra_ratio_calculator(company: dict[str, Any], requested: list[str]) -> list[str]:
    """Calculate only named, code-defined ratios. Never evaluate model text."""
    facts = company["facts"]["facts"]
    def val(key: str) -> float | None:
        item = facts.get(key)
        return float(item["value"]) if item else None
    revenue, op, cfo = val("revenue"), val("operating_income"), val("cash_from_operations")
    long_debt, current_debt, capex = val("long_term_debt"), val("current_debt"), val("capex")
    ratios: dict[str, tuple[float | None, str]] = {
        "debt_to_revenue": (((long_debt or 0) + (current_debt or 0)) / revenue if revenue else None,
                            f"({long_debt} + {current_debt}) / {revenue}"),
        "operating_cash_flow_margin": (cfo / revenue if cfo is not None and revenue else None,
                                       f"{cfo} / {revenue}"),
        "capex_to_revenue": (abs(capex) / revenue if capex is not None and revenue else None,
                             f"{abs(capex) if capex is not None else None} / {revenue}"),
    }
    output = []
    for name in dict.fromkeys(requested):
        if name not in ratios:
            output.append(f"- Calculator request `{name}` rejected: not an approved ratio name.")
            continue
        value, formula = ratios[name]
        shown = f"{value:.2%}" if value is not None else "not calculable"
        output.append(f"- Additional ratio {name}: {shown}; arithmetic: {formula}.")
    return output


def release_claims(release_text: str) -> list[str]:
    lines = release_text.splitlines()
    matched: list[str] = []
    for i, line in enumerate(lines):
        if re.search(r"revenue|net sales|diluted earnings per share|diluted EPS|per share|^diluted\b|earnings per share", line, re.IGNORECASE):
            context = " | ".join(f"[Exhibit 99.1 line {j + 1}] {x}"
                                 for j, x in enumerate(lines[max(0, i-1):min(len(lines), i+2)], start=max(0, i-1)) if x)
            if context not in matched:
                matched.append(f"Exhibit 99.1 line {i + 1}: {context[:600]}")
    return matched[:50]


def quarter_metrics(release_text: str) -> dict[str, Any]:
    lines = release_text.splitlines()
    revenue_line = ""
    revenue_line_number: int | None = None
    revenue_number_line_number: int | None = None
    revenue_numbers: list[float] = []
    for i, line in enumerate(lines):
        match = re.search(r"\btotal\s+(?:net\s+)?(?:revenues?|sales)\b", line, re.IGNORECASE)
        if not match:
            continue
        revenue_line = line
        revenue_line_number = i + 1
        revenue_context = re.sub(r"\(\d+\)", "", " ".join(lines[i:min(len(lines), i + 3)]))
        revenue_display_lines = [re.sub(r"\(\d+\)", "", item).strip() for item in lines[i:min(len(lines), i + 3)]]
        number_offset = next((offset for offset, item in enumerate(revenue_display_lines) if re.search(r"\d", item)), 0)
        number_line = revenue_display_lines[number_offset] if revenue_display_lines else ""
        revenue_number_line_number = i + number_offset + 1
        label_line = re.sub(r"\(\d+\)", "", line).strip()
        revenue_line = label_line if number_line == label_line or not number_line else f"{label_line} {number_line}"
        revenue_tail = revenue_context[match.end():]
        revenue_numbers = [float(x.replace(",", "")) for x in re.findall(
            r"(?<![\w.])\$?\s*(\d{1,3}(?:,\d{3})+|\d+)(?![\w.])", revenue_tail)]
        if len(revenue_numbers) >= 2:
            break
    eps_line = ""
    eps_line_number: int | None = None
    eps_number_line_number: int | None = None
    eps_numbers: list[float] = []
    heading = next((i for i, line in enumerate(lines) if re.search(
        r"(?:NET INCOME PER COMMON SHARE|EARNINGS PER SHARE)", line, re.IGNORECASE)), -1)
    eps_start = max(0, heading + 1) if heading >= 0 else 0
    for i in range(eps_start, min(len(lines), eps_start + 20)):
        # Require an Earnings per share heading first. Otherwise the later
        # diluted weighted-share-count row can be mistaken for diluted EPS.
        if heading < 0 or not re.match(r"\s*Diluted(?:\s|$)", lines[i], re.IGNORECASE):
            continue
        values: list[tuple[int, float]] = []
        for j in range(i, min(len(lines), i + 4)):
            found = re.findall(r"(?<![\w.])\$?\s*(\d+\.\d+)(?![\w.])", lines[j])
            if found:
                values.extend((j, float(item)) for item in found)
                if len(values) >= 2:
                    break
            elif j > i and lines[j].strip() and not re.fullmatch(r"\s*(?:\$?\s*)", lines[j]):
                break
        if len(values) == 2:
            eps_line_number = i + 1
            eps_number_line_number = values[-1][0] + 1
            eps_line = " ".join(lines[i:values[-1][0] + 1])
            eps_numbers = [value for _, value in values]
            break
        if len(values) > 2:
            eps_line_number = i + 1
            eps_number_line_number = values[-1][0] + 1
            eps_line = " ".join(lines[i:values[-1][0] + 1])
            eps_numbers = [value for _, value in values[:2]]
            break
    revenue = revenue_numbers[:2] if len(revenue_numbers) >= 2 else []
    return {
        "revenue_current": revenue[0] if revenue else None,
        "revenue_prior_quarter": revenue[1] if len(revenue) > 1 else None,
        "revenue_growth": revenue[0] / revenue[1] - 1 if len(revenue) > 1 and revenue[1] else None,
        "revenue_release_line": revenue_line,
        "revenue_release_line_number": revenue_line_number,
        "revenue_number_line_number": revenue_number_line_number,
        "diluted_eps_current": eps_numbers[0] if eps_numbers else None,
        "diluted_eps_prior_quarter": eps_numbers[1] if len(eps_numbers) > 1 else None,
        "eps_release_line": eps_line,
        "eps_release_line_number": eps_line_number,
        "eps_number_line_number": eps_number_line_number,
        "release_units": "Dollars in millions except per-share data, as captioned in the release; quarter comparison uses the first two columns.",
    }


def financial_evidence(companies: list[dict[str, Any]], price: float | None,
                       price_date: str | None, price_source: str | None) -> str:
    main = companies[0]
    f = main["facts"]["facts"]
    lines = ["Code-calculated figures and filing evidence (use these values; do not recompute in the model):"]
    for key in ("revenue", "revenue_prior_year", "operating_income", "net_income", "diluted_eps", "equity", "long_term_debt", "current_debt", "cash_from_operations", "capex"):
        item = f.get(key)
        if item:
            lines.append(f"- {item['label']}: {item['value']} {item['unit']}; tag {item['tag']}; period {item.get('period_start') or 'instant'} to {item['period_end']}; {item['filing']} accession {item['accession']}.")
        else:
            lines.append(f"- {key}: not found in supplied XBRL facts; do not infer a value.")
    statement_source = revenue_statement_source(main)
    revenue_fact = f.get("revenue")
    if statement_source and revenue_fact:
        label, line_number = statement_source
        lines.append(f"- {main['facts']['ticker']} top-line definition: its latest 10-K calls the selected figure '{label}' on saved-text line {line_number}; tag {revenue_fact['tag']}; this is the caption for the top-line measure used in the ratios.")
    ratios = main.get("ratios", {})
    for label, name in (("Revenue growth", "revenue_growth"), ("Operating margin", "operating_margin"),
                        ("Return on average equity", "return_on_average_equity"), ("Debt to equity", "debt_to_equity"),
                        ("Free cash flow", "free_cash_flow"), ("P/E", "pe")):
        inputs = ratios.get("inputs", {})
        formulas = {
            "revenue_growth": f"({f.get('revenue', {}).get('value')} / {f.get('revenue_prior_year', {}).get('value')}) - 1",
            "operating_margin": f"{f.get('operating_income', {}).get('value')} / {f.get('revenue', {}).get('value')}",
            "return_on_average_equity": f"{f.get('net_income', {}).get('value')} / (({inputs.get('current_equity')} + {inputs.get('prior_equity')}) / 2)",
            "debt_to_equity": f"({inputs.get('long_term_debt')} + {inputs.get('current_portion_debt')}) / {inputs.get('current_equity')}",
            "free_cash_flow": f"{inputs.get('cash_from_operations')} - {inputs.get('additions_to_property_and_equipment')}",
            "pe": f"{inputs.get('price')} / {inputs.get('diluted_eps')}",
        }
        val = ratios.get(name)
        shown = f"{val:.2%}" if name in {"revenue_growth", "operating_margin", "return_on_average_equity"} and val is not None else f"{val:.4f}" if val is not None and name == "debt_to_equity" else val
        period = f" (using FY ended {main['facts']['fiscal_year_end']} diluted EPS)" if name == "pe" and val is not None else ""
        lines.append(f"- {label}{period}: {shown}; arithmetic: {formulas[name]}.")
    prior_equity_fact = ratios.get("inputs", {}).get("prior_equity_fact")
    if prior_equity_fact:
        lines.append(f"- Prior-year equity for ROAE: {prior_equity_fact['value']} {prior_equity_fact['unit']}; tag {prior_equity_fact['tag']}; period instant at {prior_equity_fact['period_end']}; {prior_equity_fact['filing']} accession {prior_equity_fact['accession']}.")
    q = main.get("quarter", {})
    qgrowth = q.get("revenue_growth")
    qgrowth_text = f"{qgrowth:.2%}" if qgrowth is not None else "not calculable from supplied release text"
    eight_k_accession = main["facts"]["filings"]["8-K"]["accession"]
    lines.append(f"- Latest-quarter revenue (dollars in millions): {q.get('revenue_current')}; same quarter prior year: {q.get('revenue_prior_quarter')}; growth: {qgrowth_text}, arithmetic ({q.get('revenue_current')} / {q.get('revenue_prior_quarter')}) - 1; 8-K accession {eight_k_accession}, Exhibit 99.1 label line {q.get('revenue_release_line_number')}, value line {q.get('revenue_number_line_number')}: {q.get('revenue_release_line')}")
    lines.append(f"- Latest-quarter diluted EPS, GAAP: {q.get('diluted_eps_current')}; prior-year quarter: {q.get('diluted_eps_prior_quarter')}; 8-K accession {eight_k_accession}, Exhibit 99.1 line {q.get('eps_release_line_number')}: {q.get('eps_release_line')}")
    for peer in companies[1:]:
        pf = peer["facts"]["facts"]
        rev, op = pf.get("revenue"), pf.get("operating_income")
        margin = peer.get("ratios", {}).get("operating_margin")
        if rev and op:
            peer_label = revenue_statement_source(peer)
            label_text = f"; statement top-line label '{peer_label[0]}' at saved-text line {peer_label[1]}" if peer_label else ""
            lines.append(f"- Peer {peer['facts']['ticker']}: revenue ${rev['value']:,} USD ({rev['tag']}, {rev.get('period_start')} to {rev['period_end']}, 10-K {rev['accession']}{label_text}); operating income ${op['value']:,} {op['unit']} ({op['tag']}, {op.get('period_start')} to {op['period_end']}, 10-K {op['accession']}); operating margin = {op['value']:,} / {rev['value']:,} = {margin:.2%}.")
        else:
            lines.append(f"- Peer {peer['facts']['ticker']}: revenue or operating income not found in supplied facts; margin not calculated.")
    if price is not None:
        lines.append(f"- P/E price input: ${price:.2f}, date {price_date}; source {price_source}.")
    return "\n".join(lines)


ROLE_INSTRUCTIONS = {
    "Research Analyst": (
        "You are the Research Analyst. Use only the supplied JSON context. Cover business model, competitive position, catalysts, and recent developments. "
        "Every factual claim must include a short exact quote and cite the filing, section, accession, and saved-text line number. "
        "Do not invent quotes or line numbers. If evidence is absent, say so. Distinguish net sales from total revenue. Return concise Markdown."
    ),
    "Financial Analyst": (
        "You are the Financial Analyst. Use only the supplied JSON context. Interpret the supplied code-calculated facts, ratios, quarter, and peers. "
        "Do not calculate or change any arithmetic. For every number, cite its filing and either its income-statement line or XBRL tag, unit, period, and accession. "
        "Show supplied ratio formulas. State the chosen definition if the filing has alternatives. Do not invent values or sources. "
        "Return concise Markdown. End with one machine-readable line: CALCULATOR_REQUESTS: NONE or a comma-separated list of approved ratio names."
    ),
    "Investment Advisor": (
        "You are the Investment Advisor. Use only the Research Analyst and Financial Analyst outputs in the supplied JSON context. "
        "Write a thesis and choose Buy, Hold, or Sell. Always choose one of the three. If the evidence is limited, choose Hold and state the limit. "
        "Name one deciding number and cite it to the Financial Analyst output. Do not add facts or calculations. Return concise Markdown."
    ),
    "Strategy Manager": (
        "You are the Strategy Manager. Use only the supplied JSON context. Check that all five report parts are present, refer to the same company, "
        "and are consistent with the supplied evidence. Do not create facts. Follow the requested output format exactly."
    ),
}


def call_model(client: Any, model: str, role: str, task: str, context: dict[str, Any], expected: str,
               system_instruction: str | None = None, max_tokens: int = 1800) -> str:
    for attempt in range(2):
        print(f"Running role: {role}" + (" (retry)" if attempt else ""))
        response = client.chat.completions.create(
            model=model,
            temperature=0.1,
            max_tokens=max(max_tokens, 1800) if attempt else max_tokens,
            messages=[
                {"role": "system", "content": system_instruction or ROLE_INSTRUCTIONS[role]},
                {"role": "user", "content": json.dumps({"task": task, "context": context, "expected_output": expected}, ensure_ascii=False)},
            ],
        )
        content = response.choices[0].message.content
        if content and content.strip():
            return content.strip()
    raise RuntimeError(f"{role} returned no text after one retry.")


def complete_sentences_within_word_limit(text: str, limit: int) -> str:
    """Keep only complete model sentences within a hard report word limit."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    kept: list[str] = []
    count = 0
    for sentence in sentences:
        words = re.findall(r"\S+", sentence)
        if not sentence.strip() or not words:
            continue
        if count + len(words) > limit:
            break
        kept.append(sentence.strip())
        count += len(words)
    if kept:
        return " ".join(kept)
    words = re.findall(r"\S+", text.strip())
    return " ".join(words[:limit])


def clean_model_section(text: str, word_limit: int) -> str:
    text = "\n".join(line for line in text.splitlines() if not re.match(r"^\s*#{1,4}\s+", line))
    return complete_sentences_within_word_limit(text, word_limit).strip()


def normalize_financial_definition(text: str, company: dict[str, Any]) -> str:
    text = re.sub(r"(?im)^\*?Revenue definition:[^.\n]*(?:\.|$)\s*", "", text).strip()
    source = revenue_statement_source(company)
    fact = company.get("facts", {}).get("facts", {}).get("revenue")
    if source and fact:
        label, line_number = source
        text += (f"\nRevenue definition: {label}, per the 10-K saved-text line {line_number} "
                 f"and XBRL tag {fact['tag']}.")
    return text


def build_report(companies: list[dict[str, Any]], ticker: str, price: float | None, out: Path,
                 env: dict[str, str], with_model: bool, price_date: str | None = None,
                 price_source: str | None = None) -> Path:
    main = companies[0]
    if with_model:
        key = env.get("API_KEY") or env.get("PURDUE_GENAI_API_KEY")
        if not key:
            raise RuntimeError("Set API_KEY in .env (PURDUE_GENAI_API_KEY is also accepted for the existing Purdue setup).")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install dependencies with: python3 -m pip install -r requirements.txt") from exc
        model = env.get("GENAI_MODEL", "")
        client = OpenAI(api_key=key, base_url=env.get("GENAI_API_BASE", GENAI_API), timeout=150.0, max_retries=0)
        if not model:
            available = client.models.list().data
            ids = [x.id for x in available]
            model = next((x for x in ("gpt-oss:120b", "qwen3.8:27b") if x in ids), ids[0] if ids else "")
        if not model:
            raise RuntimeError("No models are available to this GenAI Studio account.")
        print(f"Purdue GenAI Studio model: {model}")
        facts = main["facts"]
        tenk = main["filing_texts"]["10-K"]
        business = re.search(r"ITEM\s+1\.?\s+BUSINESS", tenk, re.IGNORECASE)
        mda = re.search(r"ITEM\s+7\.?\s+MANAGEMENT.{0,30}DISCUSSION", tenk, re.IGNORECASE)
        tenk_lines = tenk.splitlines()
        def numbered_section(start_match: re.Match[str] | None, max_chars: int) -> str:
            if not start_match:
                return "Section not found in the supplied 10-K text."
            start_line = tenk[:start_match.start()].count("\n")
            selected: list[str] = []
            size = 0
            for index in range(start_line, len(tenk_lines)):
                row = f"10-K accession {facts['filings']['10-K']['accession']} line {index + 1}: {tenk_lines[index]}"
                if size + len(row) > max_chars:
                    break
                selected.append(row)
                size += len(row)
            return "\n".join(selected)
        business_text = numbered_section(business, 18000)
        mda_text = numbered_section(mda, 22000)
        release_text = (f"8-K accession {facts['filings']['8-K']['accession']}; "
                        + "\n".join(release_claims(main["filing_texts"]["8-K"])))
        research = call_model(client, model, "Research Analyst",
                              "In no more than 220 words, describe the business model, competitive position, catalysts, and recent developments. Use the 10-K Business and MD&A sections and the earnings release. Support every factual claim with a short exact quote and its source section and line. Do not use a table.",
                              {"10-K Item 1 Business": business_text, "10-K Item 7 MD&A": mda_text,
                               "earnings release relevant lines": release_text},
                              "No more than 220 words. Every factual claim has a quote and filing, section, accession, and saved-text line.")
        research = clean_model_section(research, 195)
        release_quotes = earnings_release_quotes(main)
        if release_quotes:
            research = research.rstrip() + "\n\nRecent earnings release:\n" + release_quotes
        finance = call_model(client, model, "Financial Analyst",
                             "Write no more than 100 words of financial interpretation. Use only the supplied evidence. Do not repeat the tables; the code adds them to the report. Include each number you use with its filing or XBRL tag and period. Restate supplied arithmetic; do not calculate. State the revenue definition shown in the evidence. End with CALCULATOR_REQUESTS: NONE or approved ratio names.",
                             {"code_calculated_evidence": financial_evidence(companies, price, price_date, price_source),
                              "available_calculator_requests": ["debt_to_revenue", "operating_cash_flow_margin", "capex_to_revenue"]},
                             "Concise Markdown followed by the exact line CALCULATOR_REQUESTS: NONE or a comma-separated list of approved ratio names. Do not calculate any ratio.",
                             max_tokens=1200)
        request_match = re.search(r"(?im)^CALCULATOR_REQUESTS:\s*(.*)$", finance)
        requested_ratios = ([item.strip() for item in request_match.group(1).split(",") if item.strip() and item.strip().upper() != "NONE"]
                            if request_match else [])
        finance_analysis = finance[:request_match.start()].strip() if request_match else finance
        finance_analysis = clean_model_section(finance_analysis, 100)
        finance_analysis = normalize_financial_definition(finance_analysis, main)
        extra_calculations = extra_ratio_calculator(main, requested_ratios)
        finance = finance_analysis + ("\n\n" + "\n".join(extra_calculations) if extra_calculations else "")
        advisor = call_model(client, model, "Investment Advisor",
                             "In no more than 120 words, synthesize a thesis and choose Buy, Hold, or Sell. Name one deciding number, cite it to the supplied Financial Analyst output, and use only the two role outputs below.",
                             {"Research Analyst": research, "Financial Analyst": finance}, "Thesis, one deciding number, and one recommendation; maximum 120 words.")
        advisor = clean_model_section(advisor, 120)
        parts = {
            "Overview": f"Ticker: {ticker.upper()}. Fiscal year ended {facts['fiscal_year_end']}. Filings: 10-K {facts['filings']['10-K']['accession']}; 10-Q {facts['filings']['10-Q']['accession']}; earnings 8-K {facts['filings']['8-K']['accession']}.",
            "Market Positioning and Growth Outlook": research,
            "Valuation Insights": financial_evidence(companies, price, price_date, price_source) + "\n\nAnalyst interpretation:\n\n" + finance,
            "Future Developments and Strategic Recommendations": (
                "Key developments and strategic actions from the filing review:\n\n" + research[:3500]
                + "\n\nFinancial implications:\n\n" + finance[:1800]),
            "Investment Recommendation": advisor,
        }
        # Manager completeness/consistency check, one repair pass only.
        manager_input = {heading: text[:2800] for heading, text in parts.items()}
        manager = call_model(client, model, "Strategy Manager",
                             "Check all five parts. Confirm that each Research Analyst factual claim has an exact quote and saved-text line; every Financial Analyst number has its filing or XBRL tag and period; each ratio has code-supplied arithmetic; the revenue definition matches the 10-K statement label; and the Investment Advisor chooses Buy, Hold, or Sell with one number from Financial Analyst output. Check that parts are present, use the same company, and do not contradict. Human filing audit is separate. Return JSON only with keys status, failing_part, repair_request. Use PASS only if every check passes. Otherwise name one failing part and a concise repair request.",
                             {"five_parts": manager_input, "required_parts": list(parts),
                              "source_facts": financial_evidence(companies, price, price_date, price_source)},
                             'JSON: {"status":"PASS"|"FAIL","failing_part":string|null,"repair_request":string|null}')
        try:
            manager_result = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", manager.strip(), flags=re.IGNORECASE))
        except json.JSONDecodeError as exc:
            raise RuntimeError("Strategy Manager returned invalid check JSON.") from exc
        advisor_repair_used = False
        if str(manager_result.get("status", "")).upper() != "PASS":
            heading = manager_result.get("failing_part")
            if heading not in parts:
                raise RuntimeError("Strategy Manager did not name a valid failing report part.")
            repair_role = ("Financial Analyst" if heading in {"Valuation Insights", "Future Developments and Strategic Recommendations"} else
                           "Investment Advisor" if heading == "Investment Recommendation" else
                           "Research Analyst" if heading == "Market Positioning and Growth Outlook" else "Strategy Manager")
            evidence = {"Financial Analyst": financial_evidence(companies, price, price_date, price_source),
                        "Investment Advisor": {"Research Analyst": research, "Financial Analyst": finance},
                        "Research Analyst": {"10-K Item 1 Business": business_text, "10-K Item 7 MD&A": mda_text,
                                             "earnings release relevant lines": release_text},
                        "Strategy Manager": {"source_filing_metadata": facts["filings"],
                                             "source_facts_and_calculations": financial_evidence(companies, price, price_date, price_source),
                                             "required_sections": list(parts)}}[repair_role]
            repaired = call_model(client, model, f"{repair_role} (single repair pass)",
                                  f"Repair the {heading} part once according to the manager's request. Use only the evidence supplied. Return only the revised section.",
                                  {"manager_request": manager_result.get("repair_request"), "part_heading": heading,
                                   "current_part": parts[heading][:3500], "evidence": evidence},
                                  "The revised text for this report section.",
                                  system_instruction=ROLE_INSTRUCTIONS.get(repair_role, ROLE_INSTRUCTIONS["Strategy Manager"]))
            if repair_role == "Financial Analyst":
                try:
                    repaired_json = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", repaired.strip(), flags=re.IGNORECASE))
                    repaired = str(repaired_json.get("analysis", repaired))
                except (json.JSONDecodeError, AttributeError):
                    pass
            if repair_role == "Research Analyst":
                research = clean_model_section(repaired, 195)
                release_quotes = earnings_release_quotes(main)
                if release_quotes:
                    research = research.rstrip() + "\n\nRecent earnings release:\n" + release_quotes
            elif repair_role == "Financial Analyst":
                finance = normalize_financial_definition(clean_model_section(repaired, 100), main)
            elif repair_role == "Investment Advisor":
                advisor = clean_model_section(repaired, 120)
            else:
                parts[heading] = clean_model_section(repaired, 120)
            advisor_repair_used = repair_role == "Investment Advisor"
        if not re.search(r"\b(?:Buy|Hold|Sell)\b", advisor, re.IGNORECASE) or not re.search(r"\d", advisor):
            if advisor_repair_used:
                raise RuntimeError("Investment Advisor did not meet the recommendation requirement after its one repair pass.")
            repaired = call_model(client, model, "Investment Advisor (single repair pass)",
                                  "The manager found that your prior recommendation did not meet the task. Choose Buy, Hold, or Sell. Name one deciding number from the Financial Analyst output. If the evidence is limited, choose Hold and name the limit. Do not add facts.",
                                  {"Research Analyst": research, "Financial Analyst": finance},
                                  "A concise thesis, exactly one Buy/Hold/Sell choice, and one cited deciding number.",
                                  system_instruction=ROLE_INSTRUCTIONS["Investment Advisor"])
            advisor = clean_model_section(repaired, 120)
            if not re.search(r"\b(?:Buy|Hold|Sell)\b", repaired, re.IGNORECASE) or not re.search(r"\d", repaired):
                raise RuntimeError("Investment Advisor did not meet the recommendation requirement after one repair pass.")
        # Rebuild all five sections from the final, checked role outputs. This
        # preserves the code-calculated evidence if the manager asks for a repair.
        evidence = financial_evidence(companies, price, price_date, price_source)
        parts = {
            "Overview": f"Ticker: {ticker.upper()}. Fiscal year ended {facts['fiscal_year_end']}. Filings: 10-K {facts['filings']['10-K']['accession']}; 10-Q {facts['filings']['10-Q']['accession']}; earnings 8-K {facts['filings']['8-K']['accession']}.",
            "Market Positioning and Growth Outlook": research,
            "Valuation Insights": evidence + "\n\nFinancial Analyst interpretation:\n\n" + finance,
            "Future Developments and Strategic Recommendations": "Research findings:\n\n" + research + "\n\nFinancial findings:\n\n" + finance,
            "Investment Recommendation": advisor,
        }
        for heading, text in parts.items():
            parts[heading] = re.sub(r"\bforward P/E\b", f"P/E based on FY ended {facts['fiscal_year_end']} diluted EPS", text, flags=re.IGNORECASE)
        if not re.search(r"\b(?:Buy|Hold|Sell)\b", advisor, re.IGNORECASE) or not re.search(r"\d", advisor):
            raise RuntimeError("Investment Advisor did not return a choice and a deciding number.")
        # Strategy Manager has checked the section content. The code assembles the
        # checked role outputs so a generation limit cannot cut off a report section.
    else:
        parts = {}

    filing_line = "; ".join(f"{form} {main['facts']['filings'][form]['accession']}" for form in ("10-K", "10-Q", "8-K"))
    report = out / f"{ticker.upper()}_report.md"
    if with_model:
        body = "\n\n".join(f"## {heading}\n\n{text}" for heading, text in parts.items()).strip()
        price_note = f"Price used for P/E: ${price:.2f} on {price_date or 'date not recorded'}; source: {price_source or 'not recorded'}.\n\n" if price is not None else "Price not supplied; P/E is omitted.\n\n"
        content = f"Filings read: {filing_line}\nRun time: {datetime.now().astimezone().isoformat(timespec='seconds')}\n\n# {ticker.upper()} Equity Research Report\n\n{price_note}{body}\n\n---\n\nThis is a learning exercise, not financial advice. AI assistance: Purdue GenAI Studio. Student verification and judgment are still required.\n"
    else:
        content = f"Filings read: {filing_line}\nRun time: {datetime.now().astimezone().isoformat(timespec='seconds')}\n\n# {ticker.upper()} Equity Research Report\n\nModel roles were not run. Re-run with `--model` to create the five-part report.\n"
    revenue_fact = main["facts"]["facts"].get("revenue")
    if with_model and revenue_fact:
        content = content.replace("RevenueFromContractWithCustomerExcludingTax", revenue_fact["tag"])
    report.write_text(content, encoding="utf-8")
    print(f"Report saved: {report}")
    return report


def write_audit_template(ticker: str, out: Path, report: Path) -> Path:
    path = out / f"{ticker.upper()}_human_audit.md"
    rows = [
        ("1", "Total revenue, latest fiscal year", "10-K income statement and XBRL tag"),
        ("2", "Revenue growth vs prior year", "Same revenue tag and periods; show arithmetic"),
        ("3", "Operating income and operating margin", "10-K income statement; operating income / total revenue"),
        ("4", "Net income attributable to company", "10-K income statement"),
        ("5", "Diluted earnings per share, GAAP", "10-K per-share section"),
        ("6", "Return on average equity", "Net income / average of current and prior year equity"),
        ("7", "Debt to equity", "Long-term debt plus current portion / equity"),
        ("8", "Free cash flow", "Cash from operations minus additions to property and equipment"),
        ("9", "Latest quarter revenue", "Earnings release"),
        ("10", "Quarter revenue growth vs same quarter last year", "Earnings release; two columns"),
        ("11", "Quarter diluted EPS, GAAP", "Earnings release per-share section"),
        ("Other", "Every other Financial Analyst number (peers, P/E, extra ratios)", "Named filing/tag/period and arithmetic"),
        ("Template", "All five report parts present", "Overview; Market Positioning and Growth Outlook; Valuation Insights; Future Developments and Strategic Recommendations; Investment Recommendation"),
        ("Recommendation", "Buy/Hold/Sell names a stated deciding number", "Thesis uses claims marked correct"),
    ]
    lines = [f"# Human audit — {ticker.upper()}", "", f"Report: `{report.name}`", "", "Errors (wrong + unsupported): TO BE COUNTED BY HUMAN", "Missing claims: TO BE COUNTED BY HUMAN", "", "Do not let an AI fill the Mark column. Compare each report claim with the named filing and write the filing's value/line.", "", "| # | Claim | Report says | Filing says / source line | Mark (human) |", "|---|---|---|---|---|"]
    for n, claim, source in rows:
        lines.append(f"| {n} | {claim} |  | {source} |  |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the FIN 67110 SEC research desk")
    parser.add_argument("ticker", help="SEC ticker symbol")
    parser.add_argument("--peers", default="", help="comma-separated peer ticker symbols")
    parser.add_argument("--price", type=float, help="share price for P/E calculation")
    parser.add_argument("--price-date", help="date of supplied closing price (YYYY-MM-DD)")
    parser.add_argument("--price-source", help="URL or source for supplied closing price")
    parser.add_argument("--step", type=int, choices=range(1, 8), help="run one step (currently runs the full verified pipeline through that step)")
    parser.add_argument("--model", action="store_true", help="run four Purdue GenAI Studio roles")
    args = parser.parse_args()
    env = load_env()
    ua = env.get("SEC_USER_AGENT", "")
    if not ua or "Your Name" in ua:
        print("Error: set SEC_USER_AGENT in .env to your name and email.", file=sys.stderr)
        return 2
    os.environ["_FIN67110_SEC_UA"] = ua
    peers = [p.strip().upper() for p in args.peers.split(",") if p.strip()]
    ticker = args.ticker.upper()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = ROOT / "runs" / f"{ticker}_{stamp}"
    out.mkdir(parents=True, exist_ok=False)
    print(f"Run folder: {out}")
    companies = []
    try:
        for symbol in [ticker, *peers]:
            company, _release = facts_for_company(symbol, ua, out)
            companies.append(company)
        print_calculations(companies, args.price)
        print_release_and_peers(companies)
        report = build_report(companies, ticker, args.price, out, env, args.model, args.price_date, args.price_source)
        audit = write_audit_template(ticker, out, report)
        print(f"Human audit template: {audit}")
        return 0
    except (HTTPError, URLError) as exc:
        detail = getattr(exc, "code", "network error")
        print(f"SEC/network request failed ({detail}). Retry later; no API key was printed.", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Desk run failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
