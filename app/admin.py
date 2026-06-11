"""Admin / Debug page."""
import os
import streamlit as st
from app.db import health_check, reseed_2024_from_2023
from app.ui_styles import apply_global_styles, hero_card


def render():
    apply_global_styles()

    hero_card(
        "Admin / Debug",
        "Database health, diagnostics, and data management tools",
        "🔧",
    )

    # ── DB health ─────────────────────────────────────────────────────────────
    h = health_check()

    st.markdown("### Database Health")
    with st.container(border=True):
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Connection",   "✅ Live"    if h["connected"]           else "❌ Down")
        k2.metric("Properties",   f"{h['properties_count']} rows" if h["properties_exists"] else "—")
        k3.metric("Financials",   f"{h['financials_count']} rows" if h["financials_exists"] else "—")
        k4.metric("Fiscal Years", ", ".join(str(y) for y in h["fiscal_years"]) or "none")

        if h.get("error"):
            st.markdown(
                f"<div style='background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);"
                f"border-radius:8px;padding:0.6rem 1rem;font-size:0.8rem;color:#fca5a5;margin-top:0.75rem;'>"
                f"⚠️ {h['error']}</div>",
                unsafe_allow_html=True,
            )

        with st.expander("Raw health JSON"):
            st.json(h)

    # ── Sidebar summary ───────────────────────────────────────────────────────
    st.sidebar.markdown(
        f"<div style='padding:0.5rem 1rem;font-size:0.78rem;color:#64748b;'>"
        f"DB: <span style='color:{'#4ade80' if h['connected'] else '#f87171'};font-weight:700;'>"
        f"{'Connected' if h['connected'] else 'Disconnected'}</span><br>"
        f"Properties: {h['properties_count']} &nbsp;|&nbsp; Financials: {h['financials_count']}"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Reseed ────────────────────────────────────────────────────────────────
    st.markdown("### Reseed 2024 Sample Data")
    st.markdown(
        "<div style='font-size:0.82rem;color:#64748b;margin-bottom:0.75rem;'>"
        "Copies all financials from <code>fiscal_year=2023</code> into <code>fiscal_year=2024</code>. "
        "Requires <code>USE_SAMPLE_2024=1</code> in .env."
        "</div>",
        unsafe_allow_html=True,
    )

    use_sample = os.environ.get("USE_SAMPLE_2024", "0") in ("1", "true", "True")
    if not use_sample:
        st.markdown(
            "<div style='background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);"
            "border-radius:8px;padding:0.6rem 1rem;font-size:0.8rem;color:#fcd34d;margin-bottom:0.75rem;'>"
            "⚠️ <code>USE_SAMPLE_2024</code> is not set to 1 — reseed is blocked."
            "</div>",
            unsafe_allow_html=True,
        )

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Dry Run Reseed 2024"):
                res = reseed_2024_from_2023(dry_run=True)
                st.json(res)
        with col2:
            if st.button("Reseed 2024 Now", type="primary"):
                if not use_sample:
                    st.error("USE_SAMPLE_2024 is not enabled. Operation blocked.")
                else:
                    res = reseed_2024_from_2023(dry_run=False)
                    st.json(res)

    st.markdown(
        "<div style='font-size:0.72rem;color:#334155;margin-top:1rem;'>"
        "Health check shows live connection status, table existence, row counts, and available fiscal years."
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    render()
