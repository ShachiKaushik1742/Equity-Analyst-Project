#!/usr/bin/env python3
"""Local Streamlit interface for the FIN 67110 equity desk."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parent


def main() -> None:
    st.set_page_config(page_title="Equity Research Desk", page_icon="📊", layout="wide")
    st.title("Equity Research Desk")
    st.write("Enter a ticker, optional peers, and an optional share price. The page shows the team’s progress and the verified report.")

    with st.form("desk_inputs"):
        ticker = st.text_input("Ticker", placeholder="COST").strip().upper()
        peers = st.text_input("Peers (comma separated, optional)", placeholder="WMT,TGT,BJ")
        price = st.number_input("Share price (optional; enter 0 to skip P/E)", min_value=0.0,
                                value=0.0, step=0.01, format="%.2f")
        submitted = st.form_submit_button("Run and verify")

    if not submitted:
        st.caption("The app reads SEC_USER_AGENT and API_KEY from the project .env file. It does not display either value.")
        return
    if not re.fullmatch(r"[A-Z0-9.-]+", ticker):
        st.error("Enter a valid ticker symbol.")
        return

    command = [sys.executable, "-u", str(ROOT / "week03_crewai_flow.py"), ticker]
    peer_list = [item.strip().upper() for item in peers.split(",") if item.strip()]
    if peer_list:
        command.extend(["--peers", ",".join(peer_list)])
    if price > 0:
        command.extend(["--price", f"{price:.2f}"])

    log_lines: list[str] = []
    report_path: Path | None = None
    current_node = "Starting the desk"
    output_box = st.empty()
    with st.status(current_node, expanded=True) as status:
        try:
            process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, text=True, bufsize=1)
            assert process.stdout is not None
            for line in process.stdout:
                clean = line.rstrip("\n")
                log_lines.append(clean)
                node = re.search(r"Running (?:node|CrewAI node):\s*(.+)", clean)
                if node:
                    current_node = node.group(1).strip()
                    status.update(label=f"Running: {current_node}", state="running")
                saved = re.search(r"Verified report:\s*(.+verified_report\.md)\s*$", clean)
                if saved:
                    report_path = Path(saved.group(1).strip()).resolve()
                output_box.code("\n".join(log_lines[-35:]), language="text")
            return_code = process.wait()
        except Exception as exc:
            status.update(label="Run failed", state="error")
            st.error(f"Could not run the desk: {type(exc).__name__}: {exc}")
            return

        if return_code != 0:
            status.update(label="Run finished with verifier errors", state="error")
            st.error("The run did not pass every verifier mark. Review the verifier table below or in the saved run.")
        else:
            status.update(label="Verified report is ready", state="complete")

    if report_path and report_path.is_file() and report_path.is_relative_to(ROOT / "runs"):
        st.subheader("Verified report")
        st.caption(f"Saved at `{report_path.relative_to(ROOT)}`")
        st.markdown(report_path.read_text(encoding="utf-8"))
    else:
        st.warning("The run did not print a saved verified-report path. Check the run output above.")


if __name__ == "__main__":
    main()
