"""Shared dark-enterprise CSS and layout helpers."""
from __future__ import annotations
from pathlib import Path
import streamlit as st

# Absolute paths — verified to work with Streamlit 1.32 page_link resolution
_APP_DIR = Path(__file__).resolve().parent

_SIDEBAR_BRAND = """
<div class="sidebar-brand">
  <div class="sidebar-title">Prologis AI</div>
  <div class="sidebar-subtitle">Financial Intelligence Platform</div>
</div>
"""

_CSS = """
<style>

/* ════════════════════════════════════════════════════════════════
   GLOBAL RESET  — must come first
   ════════════════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box !important; }

html, body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    overflow-x: hidden !important;
    background-color: #0f172a !important;
}

/* ════════════════════════════════════════════════════════════════
   MAIN BLOCK CONTAINER
   In Streamlit 1.32 the testid is "block-container" (confirmed from JS)
   ════════════════════════════════════════════════════════════════ */
[data-testid="block-container"],
.main .block-container {
    max-width: 1040px !important;
    width: 100% !important;
    padding-left:  1.5rem !important;
    padding-right: 1.5rem !important;
    padding-top:   1.75rem !important;
    padding-bottom: 4rem !important;
    margin-left:  auto !important;
    margin-right: auto !important;
    overflow-x: hidden !important;
    box-sizing: border-box !important;
}

/* Every Streamlit column must stay inside its grid cell */
[data-testid="column"] {
    min-width: 0 !important;
    max-width: 100% !important;
    overflow: hidden !important;
}

/* Tables inside HTML cards must not break out */
table {
    max-width: 100% !important;
    table-layout: auto !important;
    overflow-wrap: break-word !important;
    word-break: break-word !important;
}
td, th {
    max-width: 0 !important;
    overflow-wrap: break-word !important;
    word-break: break-word !important;
}

/* ════════════════════════════════════════════════════════════════
   SIDEBAR
   showSidebarNavigation=false in config.toml removes the auto-nav
   from the DOM entirely; no CSS hiding needed.
   ════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background-color: #0b1120 !important;
    border-right: 1px solid #1e293b !important;
    min-width: 220px !important;
    max-width: 260px !important;
    overflow-x: hidden !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
    overflow-x: hidden !important;
}

/* Brand block — rendered first in apply_global_styles */
.sidebar-brand {
    padding: 1.25rem 0.75rem 1rem 0.75rem;
    border-bottom: 1px solid rgba(148,163,184,0.22);
    margin-bottom: 0.5rem;
}
.sidebar-title {
    color: #38bdf8;
    font-size: 1.25rem;
    font-weight: 800;
    line-height: 1.2;
    letter-spacing: -0.01em;
}
.sidebar-subtitle {
    color: #94a3b8;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.3rem;
}

/* st.page_link links in sidebar */
section[data-testid="stSidebar"] [data-testid="stPageLink"] {
    margin: 1px 4px !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a {
    color: #94a3b8 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    text-decoration: none !important;
    padding: 0.38rem 0.65rem !important;
    border-radius: 6px !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.45rem !important;
    transition: background 0.15s, color 0.15s !important;
    width: 100% !important;
    overflow: hidden !important;
    white-space: nowrap !important;
    text-overflow: ellipsis !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
    background: rgba(56,189,248,0.08) !important;
    color: #38bdf8 !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
    background: rgba(56,189,248,0.12) !important;
    color: #38bdf8 !important;
    font-weight: 700 !important;
}

/* Sidebar buttons */
section[data-testid="stSidebar"] .stButton { width: 100% !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid #1e293b !important;
    color: #64748b !important;
    font-size: 0.78rem !important;
    min-height: 34px !important;
    width: 100% !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    border-color: #38bdf8 !important;
    color: #38bdf8 !important;
    background: rgba(56,189,248,0.07) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ════════════════════════════════════════════════════════════════
   TYPOGRAPHY
   ════════════════════════════════════════════════════════════════ */
h1 {
    color: #f1f5f9 !important; font-weight: 700 !important;
    font-size: 1.55rem !important; letter-spacing: -0.02em !important;
    line-height: 1.25 !important;
}
h2 { color: #e2e8f0 !important; font-size: 1.2rem !important; font-weight: 600 !important; }
h3 { color: #cbd5e1 !important; font-size: 1rem !important; font-weight: 600 !important; }
p, li { color: #cbd5e1 !important; line-height: 1.6 !important; }
label { color: #94a3b8 !important; font-size: 0.82rem !important; font-weight: 500 !important; }

/* ════════════════════════════════════════════════════════════════
   METRIC CARDS
   ════════════════════════════════════════════════════════════════ */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1e293b 0%, #162032 100%) !important;
    border: 1px solid #2d3f55 !important; border-radius: 12px !important;
    padding: 0.9rem 1rem !important; box-shadow: 0 4px 14px rgba(0,0,0,0.28) !important;
    width: 100% !important; max-width: 100% !important; overflow: hidden !important;
    transition: border-color 0.2s !important;
}
[data-testid="metric-container"]:hover { border-color: #38bdf8 !important; }
[data-testid="stMetricLabel"] p {
    color: #64748b !important; font-size: 0.65rem !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: 0.08em !important;
}
[data-testid="stMetricValue"] {
    color: #38bdf8 !important; font-size: 1.35rem !important; font-weight: 800 !important;
    line-height: 1.2 !important; overflow-wrap: break-word !important;
}
[data-testid="stMetricDelta"] { color: #4ade80 !important; }

/* ════════════════════════════════════════════════════════════════
   BUTTONS
   ════════════════════════════════════════════════════════════════ */
.stButton { width: 100% !important; }
.stButton > button {
    background: linear-gradient(135deg, #1e3a5f, #1d4ed8) !important;
    color: #f8fafc !important; border: 1px solid #3b82f6 !important;
    border-radius: 8px !important; font-weight: 600 !important; font-size: 0.78rem !important;
    padding: 0.4rem 0.75rem !important;
    min-height: 40px !important; width: 100% !important; max-width: 100% !important;
    white-space: normal !important; word-break: break-word !important;
    overflow-wrap: break-word !important; line-height: 1.35 !important;
    transition: all 0.18s !important; box-shadow: 0 2px 8px rgba(29,78,216,0.2) !important;
    overflow: hidden !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    border-color: #60a5fa !important;
    box-shadow: 0 4px 14px rgba(56,189,248,0.2) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0369a1, #0284c7) !important;
    border-color: #38bdf8 !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #0284c7, #0ea5e9) !important;
    box-shadow: 0 4px 18px rgba(56,189,248,0.35) !important;
}

/* ════════════════════════════════════════════════════════════════
   INPUTS / SELECT
   ════════════════════════════════════════════════════════════════ */
[data-baseweb="select"] > div {
    background-color: #1e293b !important; border: 1px solid #334155 !important;
    border-radius: 8px !important; color: #e2e8f0 !important; max-width: 100% !important;
}
[data-baseweb="select"] > div:focus-within { border-color: #38bdf8 !important; }
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background-color: #1e293b !important; border: 1px solid #334155 !important;
    border-radius: 8px !important; color: #e2e8f0 !important; max-width: 100% !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #38bdf8 !important; box-shadow: 0 0 0 2px rgba(56,189,248,0.12) !important;
}

/* ════════════════════════════════════════════════════════════════
   DATAFRAME / EXPANDER / TABS / BORDERED CONTAINERS / CHAT
   ════════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"],
[data-testid="stDataFrame"] > div {
    background-color: #1e293b !important; border: 1px solid #2d3f55 !important;
    border-radius: 10px !important; overflow: hidden !important;
    width: 100% !important; max-width: 100% !important;
}
[data-testid="stExpander"] {
    background-color: #1e293b !important; border: 1px solid #2d3f55 !important;
    border-radius: 10px !important; margin-bottom: 0.6rem !important;
    overflow: hidden !important; width: 100% !important; max-width: 100% !important;
}
[data-testid="stExpander"] summary {
    color: #e2e8f0 !important; font-weight: 600 !important; padding: 0.65rem 1rem !important;
}
[data-testid="stExpander"] summary:hover { color: #38bdf8 !important; }

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background-color: #1e293b !important; border-radius: 10px 10px 0 0 !important;
    padding: 0.25rem 0.4rem 0 !important; border-bottom: 1px solid #334155 !important;
    gap: 2px !important; max-width: 100% !important; overflow-x: hidden !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background-color: transparent !important; color: #64748b !important;
    border-radius: 7px 7px 0 0 !important; font-size: 0.8rem !important;
    padding: 0.4rem 0.85rem !important; border: none !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background-color: #0f172a !important; color: #38bdf8 !important;
    border-bottom: 2px solid #38bdf8 !important; font-weight: 700 !important;
}
[data-testid="stTabContent"] {
    background-color: #0f172a !important; border: 1px solid #334155 !important;
    border-top: none !important; border-radius: 0 0 10px 10px !important;
    padding: 1.1rem !important; max-width: 100% !important; overflow-x: hidden !important;
}
[data-testid="stVerticalBlockBorderWrapper"] > div {
    background-color: #1e293b !important; border: 1px solid #2d3f55 !important;
    border-radius: 12px !important; padding: 1rem 1.1rem !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.18) !important;
    width: 100% !important; max-width: 100% !important; overflow: hidden !important;
}
[data-testid="stChatMessage"] {
    background-color: #1e293b !important; border: 1px solid #2d3f55 !important;
    border-radius: 12px !important; padding: 0.8rem 1rem !important;
    margin-bottom: 0.5rem !important; max-width: 100% !important; overflow-wrap: break-word !important;
}
[data-testid="stChatInputContainer"] {
    background-color: #1e293b !important; border: 1px solid #334155 !important;
    border-radius: 12px !important; max-width: 100% !important;
}
[data-testid="stChatInputContainer"]:focus-within {
    border-color: #38bdf8 !important; box-shadow: 0 0 0 2px rgba(56,189,248,0.1) !important;
}
textarea[data-testid="stChatInputTextArea"] {
    background-color: transparent !important; color: #e2e8f0 !important;
}
[data-testid="stAlert"] {
    border-radius: 10px !important; max-width: 100% !important; overflow-wrap: break-word !important;
}
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #0ea5e9, #38bdf8) !important; border-radius: 99px !important;
}
[data-testid="stProgressBar"] > div {
    background-color: #1e293b !important; border-radius: 99px !important;
}

/* ════════════════════════════════════════════════════════════════
   CODE / HR / SCROLLBAR
   ════════════════════════════════════════════════════════════════ */
pre, code {
    background-color: #0d1829 !important; border: 1px solid #1e293b !important;
    border-radius: 6px !important; color: #7dd3fc !important;
    white-space: pre-wrap !important; word-break: break-all !important;
    max-width: 100% !important; overflow-x: auto !important;
}
hr { border-color: #1e293b !important; margin: 1.2rem 0 !important; }
::-webkit-scrollbar { width: 5px; height: 4px; }
::-webkit-scrollbar-track { background: #0f172a; }
::-webkit-scrollbar-thumb { background: #2d3f55; border-radius: 3px; }

/* ════════════════════════════════════════════════════════════════
   CUSTOM HTML LAYOUT CLASSES
   Rule: every class must have width:100%, max-width:100%,
         box-sizing:border-box, overflow:hidden
   ════════════════════════════════════════════════════════════════ */

/* KPI grid */
.fa-kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 0.8rem;
    width: 100%; max-width: 100%; box-sizing: border-box; overflow: hidden;
    margin: 0.75rem 0 1.2rem;
}
.fa-kpi-card {
    background: linear-gradient(135deg, #1e293b, #162032);
    border: 1px solid #2d3f55; border-radius: 12px; padding: 0.85rem 1rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    width: 100%; max-width: 100%; box-sizing: border-box; overflow: hidden;
    transition: border-color 0.2s;
}
.fa-kpi-card:hover { border-color: #38bdf8; }
.fa-kpi-label {
    font-size: 0.63rem; font-weight: 700; color: #64748b;
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px;
}
.fa-kpi-value {
    font-size: 1.3rem; font-weight: 800; color: #38bdf8;
    line-height: 1.2; overflow-wrap: break-word; word-break: break-word;
}
.fa-kpi-sub { font-size: 0.68rem; color: #4ade80; margin-top: 3px; }

/* Two-column grid */
.fa-two-col {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(300px, 100%), 1fr));
    gap: 1rem; align-items: start;
    width: 100%; max-width: 100%; box-sizing: border-box; overflow: hidden;
}

/* Generic card */
.fa-card {
    background: linear-gradient(135deg, #1e293b, #162032);
    border: 1px solid #2d3f55; border-radius: 12px; padding: 1rem 1.2rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    width: 100%; max-width: 100%; box-sizing: border-box; overflow: hidden;
    overflow-wrap: break-word; transition: border-color 0.2s;
}
.fa-card:hover { border-color: #38bdf8; }
.fa-card + .fa-card { margin-top: 0.75rem; }

/* Section label */
.fa-section-label {
    font-size: 0.63rem; font-weight: 700; color: #64748b;
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem;
}

/* Data scope strip */
.fa-scope-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(150px, 100%), 1fr));
    gap: 0.7rem;
    width: 100%; max-width: 100%; box-sizing: border-box; overflow: hidden;
}
.fa-scope-item {
    background: #162032; border: 1px solid #2d3f55; border-radius: 8px;
    padding: 0.6rem 0.85rem;
    max-width: 100%; box-sizing: border-box; overflow: hidden;
}

/* Cloud service cards — wraps to 1 col on narrow viewports */
.fa-cloud-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(280px, 100%), 1fr));
    gap: 0.9rem;
    width: 100%; max-width: 100%; box-sizing: border-box; overflow: hidden;
    margin: 0.75rem 0;
}
.fa-service-card {
    border-radius: 12px; padding: 1.1rem 1.2rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.22);
    width: 100%; max-width: 100%; box-sizing: border-box; overflow: hidden;
    overflow-wrap: break-word; word-break: break-word;
}
.fa-service-card table {
    width: 100%; max-width: 100%; table-layout: fixed;
    overflow-wrap: break-word; word-break: break-word;
}
.fa-service-card td, .fa-service-card th {
    overflow-wrap: break-word; word-break: break-word;
    white-space: normal !important;
}

/* Architecture flow — wraps on narrow screens */
.fa-flow {
    display: flex; flex-wrap: wrap; align-items: center; gap: 0.4rem;
    background: #0d1829; border: 1px solid #1e293b; border-radius: 12px;
    padding: 1rem 1.1rem;
    width: 100%; max-width: 100%; box-sizing: border-box; overflow: hidden;
    margin: 0.75rem 0;
}
.fa-flow-node {
    background: #1e293b; border: 1px solid #2d3f55; border-radius: 8px;
    padding: 0.35rem 0.7rem; font-size: 0.74rem; font-weight: 600; color: #e2e8f0;
    white-space: nowrap; flex-shrink: 0;
    max-width: calc(100% - 1rem); overflow: hidden; text-overflow: ellipsis;
}
.fa-flow-arrow { color: #38bdf8; font-size: 0.85rem; font-weight: 700; flex-shrink: 0; }

/* Press release cards */
.fa-pr-card {
    background: linear-gradient(135deg, #1e293b, #162032);
    border: 1px solid #2d3f55; border-left: 3px solid #38bdf8; border-radius: 12px;
    padding: 1rem 1.1rem; margin-bottom: 0.75rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.18);
    width: 100%; max-width: 100%; box-sizing: border-box; overflow: hidden;
    overflow-wrap: break-word; word-break: break-word;
}

/* ════════════════════════════════════════════════════════════════
   RESPONSIVE BREAKPOINT
   ════════════════════════════════════════════════════════════════ */
@media (max-width: 860px) {
    [data-testid="block-container"],
    .main .block-container {
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }
    .fa-two-col    { grid-template-columns: 1fr !important; }
    .fa-cloud-grid { grid-template-columns: 1fr !important; }
    .fa-kpi-grid   { grid-template-columns: repeat(2, 1fr) !important; }
}

</style>
"""


def apply_global_styles() -> None:
    """Inject CSS, then render sidebar brand + nav via page_link.

    showSidebarNavigation=false in .streamlit/config.toml removes the
    auto-nav from DOM. Brand is rendered first so it always appears at top.
    """
    st.markdown(_CSS, unsafe_allow_html=True)
    with st.sidebar:
        # Brand — first element in sidebar, always at top
        st.markdown(_SIDEBAR_BRAND, unsafe_allow_html=True)
        # Navigation
        st.page_link(str(_APP_DIR / "streamlit_app.py"),             label="Home Dashboard",    icon="🏦")
        st.page_link(str(_APP_DIR / "pages/1_Chat_Assistant.py"),    label="Chat Assistant",    icon="💬")
        st.page_link(str(_APP_DIR / "pages/2_Property_Explorer.py"), label="Property Explorer", icon="🏢")
        st.page_link(str(_APP_DIR / "pages/3_SEC_Filings.py"),       label="SEC Filings",       icon="📄")
        st.page_link(str(_APP_DIR / "pages/4_Press_Releases.py"),    label="Press Releases",    icon="📰")
        st.page_link(str(_APP_DIR / "pages/5_ML_Predictions.py"),    label="ML Predictions",    icon="🤖")
        st.page_link(str(_APP_DIR / "pages/6_Cloud_Services.py"),    label="Cloud Services",    icon="☁️")
        st.markdown(
            "<hr style='border-color:#1e293b;margin:0.6rem 0 0.4rem;'>",
            unsafe_allow_html=True,
        )


# ── Reusable HTML helpers ────────────────────────────────────────────────────

def hero_card(title: str, subtitle: str, icon: str = "") -> None:
    st.markdown(f"""
<div style="
  background:linear-gradient(135deg,#0c2340,#1e293b 60%,#162440 100%);
  border:1px solid #2d3f55;border-left:4px solid #38bdf8;
  border-radius:14px;padding:1.2rem 1.5rem;margin-bottom:1.2rem;
  box-shadow:0 8px 24px rgba(0,0,0,0.35);
  width:100%;max-width:100%;box-sizing:border-box;overflow:hidden;
  overflow-wrap:break-word;
">
  <div style="font-size:1.45rem;font-weight:800;color:#f1f5f9;
              letter-spacing:-0.02em;line-height:1.2;">
    {(icon + " ") if icon else ""}{title}
  </div>
  <div style="font-size:0.82rem;color:#64748b;margin-top:5px;line-height:1.5;
              overflow-wrap:break-word;">{subtitle}</div>
</div>
""", unsafe_allow_html=True)


def status_badge(label: str, active: bool) -> None:
    color  = "#4ade80" if active else "#f59e0b"
    bg     = "rgba(74,222,128,0.1)"  if active else "rgba(245,158,11,0.1)"
    border = "rgba(74,222,128,0.3)"  if active else "rgba(245,158,11,0.3)"
    dot    = "● Active" if active else "● Not configured"
    st.markdown(
        f'<span style="background:{bg};border:1px solid {border};border-radius:99px;'
        f'padding:3px 11px;font-size:0.69rem;font-weight:700;color:{color};'
        f'letter-spacing:0.04em;display:inline-block;margin-bottom:0.6rem;">'
        f'{dot} — {label}</span>',
        unsafe_allow_html=True,
    )


def section_label(text: str) -> None:
    st.markdown(f"<div class='fa-section-label'>{text}</div>", unsafe_allow_html=True)


def pr_card(icon: str, title: str, date: str, category: str,
            summary: str, keywords: list, pr_id: str) -> None:
    kw_html = "".join(
        f'<span style="background:rgba(56,189,248,0.08);border:1px solid rgba(56,189,248,0.2);'
        f'border-radius:4px;padding:1px 7px;font-size:0.67rem;color:#7dd3fc;'
        f'margin-right:3px;margin-bottom:3px;display:inline-block;">{k}</span>'
        for k in keywords
    )
    st.markdown(f"""
<div class="fa-pr-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;
              gap:0.75rem;flex-wrap:wrap;">
    <div style="flex:1;min-width:0;overflow:hidden;">
      <div style="font-size:0.9rem;font-weight:700;color:#e2e8f0;margin-bottom:4px;
                  overflow-wrap:break-word;">{icon} {title}</div>
      <div style="font-size:0.8rem;color:#94a3b8;line-height:1.5;margin-bottom:7px;
                  overflow-wrap:break-word;">{summary}</div>
      <div style="display:flex;flex-wrap:wrap;">{kw_html}</div>
    </div>
    <div style="min-width:100px;max-width:120px;text-align:right;flex-shrink:0;">
      <div style="font-size:0.69rem;color:#475569;font-weight:600;margin-bottom:4px;">{date}</div>
      <span style="background:rgba(56,189,248,0.09);border:1px solid rgba(56,189,248,0.25);
        border-radius:99px;padding:2px 8px;font-size:0.67rem;color:#38bdf8;font-weight:600;
        display:inline-block;">{category}</span>
      <div style="font-size:0.61rem;color:#334155;margin-top:4px;">{pr_id}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
