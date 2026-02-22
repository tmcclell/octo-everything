"""Shared data source banner for dashboard pages."""

import os
import streamlit as st


def show_data_source_banner(data: dict = None):
    """Display a banner indicating whether data comes from live API or dummy data.

    Checks the data dict for a 'source' key (set by live collectors) and falls
    back to the USE_DUMMY_DATA env var.
    """
    source = _detect_source(data)

    if source == "live":
        enterprise = os.getenv("GITHUB_ENTERPRISE", "unknown")
        org = os.getenv("GITHUB_ORG", "")
        label = f"Enterprise: **{enterprise}**"
        if org:
            label += f" · Org: **{org}**"
        st.success(f"🟢 Live data — {label}")
    else:
        st.warning("🟡 Dummy data — generated locally for demo/testing purposes")


def _detect_source(data: dict = None) -> str:
    """Return 'live' or 'dummy'."""
    # Check if any loaded dataset has a 'source' field from the live collectors
    if data:
        for value in data.values():
            if isinstance(value, dict) and value.get("source"):
                return "live"

    # Fall back to env var
    if os.getenv("USE_DUMMY_DATA", "true").lower() in ("false", "0", "no"):
        return "live"

    return "dummy"
