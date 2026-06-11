"""Property Explorer — browse and filter properties with financials."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Property Explorer · Prologis AI", page_icon="🏢", layout="wide", initial_sidebar_state="expanded")

from app.ui_styles import apply_global_styles, hero_card, page_footer, sample_disclaimer
apply_global_styles()

from app.queries import get_properties, get_financials, get_summary, get_metro_breakdown, get_type_breakdown

hero_card(
    "Property Explorer",
    "Filter and analyze the portfolio by metro area, property type, and fiscal year",
    "🏢",
)

# ── Filters ───────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    metro = st.selectbox("Metro Area", ["All", "Chicago", "Los Angeles", "New York", "Austin", "San Francisco"])
with col2:
    ptype = st.selectbox("Property Type", ["All", "Office", "Industrial", "Retail"])
with col3:
    year = st.selectbox("Fiscal Year", [2024, 2023])

metro_filter = None if metro == "All" else metro
type_filter  = None if ptype == "All" else ptype

st.divider()

# ── KPI row ───────────────────────────────────────────────────────────────────
summary = get_summary(fiscal_year=year)
if summary and summary.get("total_revenue"):
    rev = float(summary["total_revenue"])
    inc = float(summary["total_net_income"])
    exp = float(summary["total_expenses"])
    cnt = int(summary["property_count"])
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Properties",    cnt)
    k2.metric("Total Revenue", f"${rev/1e6:.1f}M")
    k3.metric("Net Income",    f"${inc/1e6:.1f}M")
    k4.metric("Net Margin",    f"{inc/rev*100:.1f}%")

st.divider()

# ── Properties table ──────────────────────────────────────────────────────────
props = get_properties(metro_area=metro_filter, property_type=type_filter)
if not props:
    st.warning("No properties found. Run `python setup_database.py --init` to seed data.")
    st.stop()

props_df = pd.DataFrame(props)
st.markdown(
    f"<div style='font-size:1rem;font-weight:700;color:#cbd5e1;margin-bottom:0.6rem;'>"
    f"Properties <span style='font-size:0.8rem;color:#64748b;font-weight:500;'>({len(props_df)} found)</span>"
    f"</div>",
    unsafe_allow_html=True,
)
st.dataframe(
    props_df[["property_id","address","metro_area","property_type","sq_footage"]].rename(columns={
        "property_id": "ID", "address": "Address", "metro_area": "Metro",
        "property_type": "Type", "sq_footage": "Sq Ft",
    }),
    use_container_width=True,
    hide_index=True,
)

st.divider()

# ── Financials table ──────────────────────────────────────────────────────────
st.markdown(
    f"<div style='font-size:1rem;font-weight:700;color:#cbd5e1;margin-bottom:0.6rem;'>"
    f"Financials <span style='font-size:0.8rem;color:#64748b;font-weight:500;'>FY{year}</span>"
    f"</div>",
    unsafe_allow_html=True,
)
fins = get_financials(fiscal_year=year)
if fins:
    if metro_filter:
        fins = [f for f in fins if metro_filter.lower() in f.get("metro_area", "").lower()]
    if type_filter:
        fins = [f for f in fins if f.get("property_type", "").lower() == type_filter.lower()]
    if fins:
        fin_df = pd.DataFrame(fins)
        for col in ["revenue", "net_income", "expenses"]:
            if col in fin_df.columns:
                fin_df[col] = fin_df[col].apply(lambda x: f"${float(x):,.0f}")
        st.dataframe(
            fin_df[["address","metro_area","property_type","sq_footage",
                    "revenue","net_income","expenses"]].rename(columns={
                "address": "Address", "metro_area": "Metro", "property_type": "Type",
                "sq_footage": "Sq Ft", "revenue": "Revenue",
                "net_income": "Net Income", "expenses": "Expenses",
            }),
            use_container_width=True,
            hide_index=True,
        )

st.divider()

# ── Revenue charts ────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)
with c1:
    st.markdown("<div style='font-size:0.95rem;font-weight:700;color:#cbd5e1;margin-bottom:0.4rem;'>Revenue by Metro Area</div>",
                unsafe_allow_html=True)
    metro_data = get_metro_breakdown(year)
    if metro_data:
        mdf = pd.DataFrame(metro_data)
        mdf["revenue"] = mdf["revenue"].astype(float)
        st.bar_chart(mdf.set_index("metro_area")["revenue"], color="#38bdf8")

with c2:
    st.markdown("<div style='font-size:0.95rem;font-weight:700;color:#cbd5e1;margin-bottom:0.4rem;'>Revenue by Property Type</div>",
                unsafe_allow_html=True)
    type_data = get_type_breakdown(year)
    if type_data:
        tdf = pd.DataFrame(type_data)
        tdf["revenue"] = tdf["revenue"].astype(float)
        st.bar_chart(tdf.set_index("property_type")["revenue"], color="#0ea5e9")

sample_disclaimer()
page_footer()
