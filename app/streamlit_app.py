"""Home dashboard — Prologis AI Financial Intelligence Platform."""
import sys
from pathlib import Path
_proj_root = Path(__file__).resolve().parents[1]
if str(_proj_root) not in sys.path:
    sys.path.insert(0, str(_proj_root))

import streamlit as st

st.set_page_config(
    page_title="Prologis AI — Financial Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.ui_styles import apply_global_styles, hero_card
apply_global_styles()

from app.db import health_check
from app.queries import get_summary, get_metro_breakdown
from app.sec_edgar import get_latest_10q
from app.press_releases import get_recent
import pandas as pd

# ── DB guard ──────────────────────────────────────────────────────────────────
h = health_check()
if not h["connected"]:
    st.error("⚠️ Database not connected. Start PostgreSQL and run: `python setup_database.py --init`")
    st.stop()

if not h["properties_exists"] or h["properties_count"] == 0:
    st.warning("Database connected but tables are empty. Initializing…")
    from app.init_db import init_db
    result = init_db()
    if result.get("error"):
        st.error(f"Setup failed: {result['error']}")
    else:
        st.success(f"Initialized: {result['properties_inserted']} properties, "
                   f"{result['financials_inserted']} financial records.")
    st.rerun()

# ── Hero ──────────────────────────────────────────────────────────────────────
hero_card(
    "Financial Intelligence Platform",
    "Real-time property analytics · SEC filings · Press releases · ML predictions",
    "🏦",
)

# ── KPI row ───────────────────────────────────────────────────────────────────
summary = get_summary(fiscal_year=2024)
if summary and summary.get("total_revenue"):
    rev = float(summary["total_revenue"])
    inc = float(summary["total_net_income"])
    exp = float(summary["total_expenses"])
    cnt = int(summary["property_count"])

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Properties",    cnt)
    k2.metric("FY2024 Revenue", f"${rev/1e6:.1f}M")
    k3.metric("Net Income",    f"${inc/1e6:.1f}M")
    k4.metric("Net Margin",    f"{inc/rev*100:.1f}%")
    k5.metric("Total Expenses", f"${exp/1e6:.1f}M")

st.divider()

# ── Latest SEC Filing + Recent Press Releases ─────────────────────────────────
q = get_latest_10q()
recent_prs = get_recent(3)

# Build HTML for both panels to avoid nested st.container border artifacts
sec_metrics_html = ""
if q:
    sec_metrics_html = f"""
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.75rem;margin:0.85rem 0;">
  <div class="fa-kpi-card">
    <div class="fa-kpi-label">Revenue</div>
    <div class="fa-kpi-value" style="font-size:1.2rem;">${float(q['revenue'])/1e6:.1f}M</div>
  </div>
  <div class="fa-kpi-card">
    <div class="fa-kpi-label">Net Income</div>
    <div class="fa-kpi-value" style="font-size:1.2rem;">${float(q['net_income'])/1e6:.1f}M</div>
  </div>
  <div class="fa-kpi-card">
    <div class="fa-kpi-label">Occupancy</div>
    <div class="fa-kpi-value" style="font-size:1.2rem;">{q['occupancy_rate']}%</div>
  </div>
</div>
"""
    highlights_html = "".join(
        f"<div style='font-size:0.8rem;color:#94a3b8;padding:3px 0;overflow-wrap:break-word;'>▸ {hl}</div>"
        for hl in q.get("highlights", [])[:3]
    )
    sec_content = f"""
<div style="font-size:0.95rem;font-weight:700;color:#e2e8f0;margin-bottom:4px;">
  {q['form']} — {q['period']}
</div>
<div style="font-size:0.72rem;color:#64748b;margin-bottom:6px;">Filed {q['filed']}</div>
{sec_metrics_html}
<div style="margin-top:4px;">{highlights_html}</div>
"""
else:
    sec_content = "<div style='color:#64748b;font-size:0.85rem;'>No 10-Q data available.</div>"

pr_items_html = ""
for r in recent_prs:
    pr_items_html += f"""
<div style="border-bottom:1px solid #1e293b;padding:0.75rem 0;overflow:hidden;">
  <div style="font-size:0.85rem;font-weight:700;color:#e2e8f0;overflow-wrap:break-word;
              line-height:1.35;margin-bottom:3px;">{r['title']}</div>
  <div style="font-size:0.7rem;color:#64748b;margin-bottom:5px;">{r['date']} · {r['category']}</div>
  <div style="font-size:0.79rem;color:#94a3b8;line-height:1.5;overflow-wrap:break-word;">
    {r['summary'][:115]}…
  </div>
</div>
"""

st.markdown(f"""
<div class="fa-two-col">
  <div class="fa-card">
    <div class="fa-section-label">📄 Latest SEC Filing</div>
    {sec_content}
  </div>
  <div class="fa-card">
    <div class="fa-section-label">📰 Recent Press Releases</div>
    {pr_items_html}
  </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Revenue chart ─────────────────────────────────────────────────────────────
metro_data = get_metro_breakdown(2024)
if metro_data:
    st.markdown("### Revenue by Metro Area — FY2024")
    metro_df = pd.DataFrame(metro_data)
    metro_df["revenue"] = metro_df["revenue"].astype(float)
    st.bar_chart(metro_df.set_index("metro_area")["revenue"], color="#38bdf8")

st.divider()

# ── Nav cards ─────────────────────────────────────────────────────────────────
st.markdown("### Navigate to")
n1, n2, n3, n4, n5 = st.columns(5)
n1.page_link("pages/1_Chat_Assistant.py",    label="💬 Chat Assistant",   icon="💬")
n2.page_link("pages/2_Property_Explorer.py", label="🏢 Property Explorer", icon="🏢")
n3.page_link("pages/3_SEC_Filings.py",       label="📄 SEC Filings",       icon="📄")
n4.page_link("pages/4_Press_Releases.py",    label="📰 Press Releases",    icon="📰")
n5.page_link("pages/5_ML_Predictions.py",    label="🤖 ML Predictions",    icon="🤖")
