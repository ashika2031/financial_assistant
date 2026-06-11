"""SEC Filings — annual and quarterly financial reports."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import pandas as pd

st.set_page_config(page_title="SEC Filings · Prologis AI", page_icon="📄", layout="wide", initial_sidebar_state="expanded")

from app.ui_styles import apply_global_styles, hero_card, page_footer, sample_disclaimer
apply_global_styles()

from app.sec_edgar import get_company_info, get_filings, get_metric_history

company = get_company_info()

hero_card(
    "SEC EDGAR Filings",
    f"{company.get('company','')} · Ticker: {company.get('ticker','')} · CIK: {company.get('cik','')}",
    "📄",
)

st.markdown(
    "<div style='background:rgba(56,189,248,0.07);border:1px solid rgba(56,189,248,0.18);"
    "border-radius:8px;padding:0.6rem 1rem;font-size:0.79rem;color:#7dd3fc;margin-bottom:1rem;'>"
    "ℹ️ Data loaded from local SEC sample. Set <code>EDGAR_LIVE=1</code> in .env to fetch live from EDGAR API."
    "</div>",
    unsafe_allow_html=True,
)

# ── Filters ───────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    form_filter = st.selectbox("Filing Type", ["All", "10-K", "10-Q"])
with col2:
    year_filter = st.selectbox("Fiscal Year", ["All", 2024, 2023])

st.divider()

filings = get_filings(
    form=None if form_filter == "All" else form_filter,
    fiscal_year=None if year_filter == "All" else int(year_filter),
)

if not filings:
    st.warning("No filings match the selected filters.")
    st.stop()

st.markdown(
    f"<div style='font-size:1rem;font-weight:700;color:#cbd5e1;margin-bottom:0.75rem;'>"
    f"Filings <span style='font-size:0.8rem;color:#64748b;font-weight:500;'>({len(filings)} found)</span>"
    f"</div>",
    unsafe_allow_html=True,
)

# ── Filing expanders ──────────────────────────────────────────────────────────
for f in filings:
    with st.expander(f"{f['form']} — {f['period']}  ·  filed {f['filed']}", expanded=(f == filings[0])):
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Revenue",      f"${float(f['revenue'])/1e6:.1f}M")
        k2.metric("Net Income",   f"${float(f['net_income'])/1e6:.1f}M")
        k3.metric("Op. Expenses", f"${float(f['operating_expenses'])/1e6:.1f}M")
        k4.metric("EPS",          f"${f['eps']:.2f}")

        st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Assets",        f"${float(f['total_assets'])/1e9:.2f}B")
        c2.metric("Total Liabilities",   f"${float(f['total_liabilities'])/1e9:.2f}B")
        c3.metric("Shareholders Equity", f"${float(f['shareholders_equity'])/1e9:.2f}B")

        st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        cc1.metric("Properties Owned", f["properties_owned"])
        cc2.metric("Occupancy Rate",   f"{f['occupancy_rate']}%")

        st.markdown(
            "<div style='font-size:0.69rem;font-weight:700;color:#64748b;text-transform:uppercase;"
            "letter-spacing:0.08em;margin-top:1rem;margin-bottom:0.4rem;'>Key Highlights</div>",
            unsafe_allow_html=True,
        )
        for hl in f.get("highlights", []):
            st.markdown(
                f"<div style='font-size:0.82rem;color:#94a3b8;padding:2px 0;"
                f"overflow-wrap:break-word;'>▸ {hl}</div>",
                unsafe_allow_html=True,
            )

st.divider()

# ── Trend chart ───────────────────────────────────────────────────────────────
st.markdown("<div style='font-size:1rem;font-weight:700;color:#cbd5e1;margin-bottom:0.6rem;'>Metric Trends Across Filings</div>",
            unsafe_allow_html=True)

metric_opts = {
    "Revenue": "revenue", "Net Income": "net_income",
    "Op. Expenses": "operating_expenses", "EPS": "eps", "Occupancy Rate": "occupancy_rate",
}
chosen = st.selectbox("Select metric", list(metric_opts.keys()))
history = get_metric_history(metric_opts[chosen])
if history:
    hist_df = pd.DataFrame(history).set_index("period")
    st.line_chart(hist_df["value"], color="#38bdf8")

sample_disclaimer()
page_footer()
