"""Press Releases — company announcements and strategic news."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

st.set_page_config(page_title="Press Releases · Prologis AI", page_icon="📰", layout="wide", initial_sidebar_state="expanded")

from app.ui_styles import apply_global_styles, hero_card, pr_card
apply_global_styles()

from app.press_releases import get_all, get_categories

hero_card(
    "Press Releases",
    "Company announcements · Acquisitions · Earnings · Expansions · ESG updates",
    "📰",
)

# ── Filters ───────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    cats = ["All"] + get_categories()
    cat = st.selectbox("Category", cats)
with col2:
    keyword = st.text_input("Search keyword", placeholder="e.g. acquisition, Chicago, Q3…")

st.divider()

releases = get_all(
    category=None if cat == "All" else cat,
    keyword=keyword.strip() or None,
)

st.markdown(
    f"<div style='font-size:0.78rem;color:#64748b;font-weight:600;margin-bottom:1rem;'>"
    f"Showing <span style='color:#38bdf8;'>{len(releases)}</span> release(s)</div>",
    unsafe_allow_html=True,
)

if not releases:
    st.markdown(
        "<div style='text-align:center;padding:2rem;color:#334155;font-size:0.9rem;'>"
        "No press releases match your filters."
        "</div>",
        unsafe_allow_html=True,
    )
    st.stop()

_ICONS = {
    "Acquisition": "🟠", "Earnings": "🟢", "Expansion": "🔵",
    "Leasing": "🟣", "Disposition": "🔴", "ESG": "🌿",
}

for r in releases:
    pr_card(
        icon=_ICONS.get(r.get("category", ""), "⚪"),
        title=r["title"],
        date=r["date"],
        category=r["category"],
        summary=r["summary"],
        keywords=r.get("keywords", []),
        pr_id=r["id"],
    )
