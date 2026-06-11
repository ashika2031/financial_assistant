"""Chat Assistant — natural language interface to all data sources."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

st.set_page_config(page_title="Chat Assistant · Prologis AI", page_icon="💬", layout="wide", initial_sidebar_state="expanded")

from app.ui_styles import apply_global_styles, hero_card
apply_global_styles()

from app.chatbot import respond

hero_card(
    "Chat Assistant",
    "Ask questions in plain English — properties, financials, SEC filings, press releases",
    "💬",
)

# ── Data scope card ───────────────────────────────────────────────────────────
st.markdown("""
<div style="background:rgba(56,189,248,0.05);border:1px solid rgba(56,189,248,0.18);
  border-radius:10px;padding:0.7rem 1rem;margin-bottom:0.5rem;
  width:100%;max-width:100%;box-sizing:border-box;">
  <div style="font-size:0.63rem;font-weight:700;color:#38bdf8;text-transform:uppercase;
              letter-spacing:0.08em;margin-bottom:6px;">Data Scope</div>
  <div style="font-size:0.8rem;color:#94a3b8;line-height:1.55;">
    Prologis / Acme Realty Corp financials &nbsp;·&nbsp;
    25 property records across 5 metros &nbsp;·&nbsp;
    4 SEC filing reports (10-K / 10-Q) &nbsp;·&nbsp;
    8 press releases &nbsp;·&nbsp;
    Local ML prediction endpoints &nbsp;·&nbsp;
    <span style="color:#f59e0b;font-weight:600;">Local rule-based mode</span>
  </div>
</div>
<div class="fa-scope-grid" style="margin-bottom:0;">
  <div class="fa-scope-item">
    <div class="fa-section-label">Properties</div>
    <div style="font-size:0.85rem;font-weight:700;color:#e2e8f0;">25 in Portfolio</div>
  </div>
  <div class="fa-scope-item">
    <div class="fa-section-label">SEC Filings</div>
    <div style="font-size:0.85rem;font-weight:600;color:#e2e8f0;">4 Reports</div>
  </div>
  <div class="fa-scope-item">
    <div class="fa-section-label">Fiscal Years</div>
    <div style="font-size:0.85rem;font-weight:600;color:#e2e8f0;">2023 · 2024</div>
  </div>
  <div class="fa-scope-item">
    <div class="fa-section-label">AI Engine</div>
    <div style="font-size:0.85rem;font-weight:600;color:#f59e0b;">Local Rule-Based</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Example questions grid ────────────────────────────────────────────────────
st.markdown("<div class='fa-section-label' style='margin-bottom:0.5rem;'>Example Questions</div>",
            unsafe_allow_html=True)

EXAMPLES = [
    "What was net income in 2024?",
    "Show me office properties in New York",
    "Any recent acquisitions?",
    "Show the latest 10-K report",
    "Give me a portfolio summary for 2024",
    "What industrial properties are in Chicago?",
    "Show Q3 2024 earnings",
    "Were there any expansions announced recently?",
]

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 4 columns with fixed equal width — avoids uneven height from different label lengths
col_a, col_b, col_c, col_d = st.columns(4)
for i, ex in enumerate(EXAMPLES):
    target = [col_a, col_b, col_c, col_d][i % 4]
    if target.button(ex, key=f"ex_{i}"):
        st.session_state["messages"].append({"role": "user", "content": ex})
        with st.spinner("Thinking…"):
            result = respond(ex)
        st.session_state["messages"].append({
            "role": "assistant",
            "content": result["answer"],
            "meta": f"Source: {result['source']} · Intent: {result['intent']}",
        })
        st.rerun()

st.divider()

# ── Chat history ──────────────────────────────────────────────────────────────
if not st.session_state["messages"]:
    st.markdown(
        "<div style='text-align:center;padding:2rem 0;color:#334155;font-size:0.88rem;'>"
        "💬 Start a conversation using the input below or click an example question above."
        "</div>",
        unsafe_allow_html=True,
    )

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "meta" in msg:
            st.markdown(
                f"<div style='font-size:0.69rem;color:#475569;margin-top:5px;"
                f"border-top:1px solid #1e293b;padding-top:5px;'>{msg['meta']}</div>",
                unsafe_allow_html=True,
            )

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask about properties, financials, SEC filings, or press releases…"):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            result = respond(prompt)
        st.markdown(result["answer"])
        st.markdown(
            f"<div style='font-size:0.69rem;color:#475569;margin-top:5px;"
            f"border-top:1px solid #1e293b;padding-top:5px;'>"
            f"Source: {result['source']} · Intent: {result['intent']}</div>",
            unsafe_allow_html=True,
        )
    st.session_state["messages"].append({
        "role": "assistant",
        "content": result["answer"],
        "meta": f"Source: {result['source']} · Intent: {result['intent']}",
    })

with st.sidebar:
    if st.button("🗑 Clear conversation"):
        st.session_state["messages"] = []
        st.rerun()
