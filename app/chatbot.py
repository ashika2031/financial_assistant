"""Rule-based chatbot router.

Priority:
  1. Anthropic Claude (if ANTHROPIC_API_KEY set)
  2. Vertex AI ADK (if GCP configured)
  3. Local rule-based fallback (always works)

The router detects intent from the user message and fetches data from the
appropriate source (Postgres, SEC JSON, press releases JSON), then formats
a natural language response.
"""
from __future__ import annotations
import re
from typing import Dict, Any, Tuple

from app import queries, press_releases, sec_edgar
from app.cloud_stubs import AnthropicClient, VertexAIAgent

_anthropic = AnthropicClient()
_vertex    = VertexAIAgent()


# ── intent detection ──────────────────────────────────────────────────────────

def _detect_intent(msg: str) -> Tuple[str, Dict]:
    """Return (intent, params) from the user message."""
    m = msg.lower()

    # SEC / financial filings — highest priority when filing type is explicit
    if any(w in m for w in ["10-k", "10k", "annual report", "10-q", "10q", "quarterly report", "filing", "edgar"]):
        form = "10-K" if any(w in m for w in ["10-k", "10k", "annual"]) else "10-Q"
        return "sec_filing", {"form": form}

    # Press releases — check before financial summary to catch "acquisitions", "expansion" etc.
    if any(w in m for w in ["press release", "acquisition", "acqui", "expand", "expansion",
                             "announce", "announcement", "deal", "divest", "esg", "sustainability"]):
        kw = None
        for k in ["acquisition", "expansion", "leasing", "disposition", "esg", "earnings"]:
            if k in m:
                kw = k
                break
        return "press_releases", {"keyword": kw}

    # Property queries — check before generic financials to catch "properties in Chicago with revenue"
    metros = ["chicago", "los angeles", "new york", "austin", "san francisco"]
    types  = ["office", "industrial", "retail"]
    metro  = next((x for x in metros if x in m), None)
    ptype  = next((x for x in types  if x in m), None)

    if metro or ptype or any(w in m for w in ["propert", "address", "sq ft", "square", "building"]):
        return "properties", {"metro": metro, "type": ptype}

    # Portfolio summary — catches "summary", "overview", "portfolio performance"
    if any(w in m for w in ["summary", "overview", "performance", "fiscal", "portfolio"]):
        year = _extract_year(m)
        return "portfolio_summary", {"year": year or 2024}

    # Generic financial metrics
    if any(w in m for w in ["net income", "revenue", "earnings", "eps", "profit", "expense", "operating", "total"]):
        year = _extract_year(m)
        return "financials_summary", {"year": year}

    return "unknown", {}


def _extract_year(text: str) -> int | None:
    m = re.search(r"\b(20\d{2})\b", text)
    return int(m.group(1)) if m else None


# ── data fetchers ─────────────────────────────────────────────────────────────

def _handle_sec_filing(params: Dict) -> str:
    form = params.get("form", "10-K")
    filings = sec_edgar.get_filings(form=form)
    if not filings:
        return f"No {form} filings found in the sample data."
    f = sorted(filings, key=lambda x: x.get("filed", ""), reverse=True)[0]
    lines = [
        f"**{f['form']} — {f['period']}** (filed {f['filed']})",
        f"- Revenue: **${f['revenue']:,.0f}**",
        f"- Net Income: **${f['net_income']:,.0f}**",
        f"- Operating Expenses: **${f['operating_expenses']:,.0f}**",
        f"- EPS: **${f['eps']:.2f}**",
        f"- Properties Owned: **{f['properties_owned']}**",
        f"- Occupancy Rate: **{f['occupancy_rate']}%**",
        "",
        "**Key Highlights:**",
    ] + [f"  • {h}" for h in f.get("highlights", [])]
    return "\n".join(lines)


def _handle_financials_summary(params: Dict) -> str:
    year = params.get("year") or 2024
    data = queries.get_summary(fiscal_year=year)
    if not data or not data.get("total_revenue"):
        return f"No financial data found for fiscal year {year}."
    rev  = float(data["total_revenue"])
    inc  = float(data["total_net_income"])
    exp  = float(data["total_expenses"])
    cnt  = int(data["property_count"])
    margin = inc / rev * 100 if rev else 0
    return (
        f"**Portfolio Financial Summary — FY{year}**\n"
        f"- Properties: **{cnt}**\n"
        f"- Total Revenue: **${rev:,.0f}**\n"
        f"- Total Expenses: **${exp:,.0f}**\n"
        f"- Net Income: **${inc:,.0f}**\n"
        f"- Net Margin: **{margin:.1f}%**"
    )


def _handle_press_releases(params: Dict) -> str:
    kw = params.get("keyword")
    releases = press_releases.get_all(keyword=kw)[:5]
    if not releases:
        return "No press releases found matching your query."
    lines = [f"**Found {len(releases)} press release(s):**\n"]
    for r in releases:
        lines.append(f"**[{r['date']}] {r['title']}** _{r['category']}_")
        lines.append(r['summary'])
        lines.append("")
    return "\n".join(lines)


def _handle_properties(params: Dict) -> str:
    metro = params.get("metro")
    ptype = params.get("type")
    props = queries.get_properties(metro_area=metro, property_type=ptype)
    if not props:
        return "No properties found matching your query."
    lines = [f"**Found {len(props)} propert(ies):**\n"]
    for p in props[:10]:
        lines.append(f"- **{p['address']}** | {p['metro_area']} | {p['property_type']} | {p['sq_footage']:,} sq ft")
    if len(props) > 10:
        lines.append(f"_...and {len(props)-10} more_")
    return "\n".join(lines)


def _handle_portfolio_summary(params: Dict) -> str:
    year = params.get("year", 2024)
    summary = queries.get_summary(fiscal_year=year)
    metro   = queries.get_metro_breakdown(year)
    if not summary:
        return f"No data found for FY{year}."
    rev = float(summary.get("total_revenue") or 0)
    inc = float(summary.get("total_net_income") or 0)
    lines = [
        f"**Portfolio Overview — FY{year}**",
        f"- Properties: **{summary.get('property_count', 0)}**",
        f"- Total Revenue: **${rev:,.0f}**",
        f"- Net Income: **${inc:,.0f}**",
        f"- Net Margin: **{inc/rev*100:.1f}%**" if rev else "",
        "",
        "**Revenue by Metro Area:**",
    ]
    for m in metro:
        lines.append(f"  • {m['metro_area']}: ${float(m['revenue']):,.0f}")
    return "\n".join(l for l in lines if l is not None)


def _unknown_response(msg: str) -> str:
    return (
        "I can help you with:\n"
        "- **Property data**: 'Show me office properties in Chicago'\n"
        "- **Financial summaries**: 'What was net income in 2024?'\n"
        "- **SEC filings**: 'Show the latest 10-K report'\n"
        "- **Press releases**: 'Any recent acquisitions?'\n"
        "- **Portfolio overview**: 'Give me a portfolio summary for 2024'\n\n"
        f"_(Local rule-based mode — connect Anthropic or Vertex AI for natural language answers)_"
    )


# ── main entry point ──────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are a financial assistant for Prologis, a real estate investment company.
You help users query property data, financial summaries, SEC filings, and press releases.
Be concise, professional, and data-focused. Format numbers with commas. Use markdown."""


_OTHER_COMPANIES = {
    "google", "apple", "amazon", "microsoft", "meta", "facebook",
    "tesla", "nvidia", "netflix", "uber", "twitter", "alphabet",
    "walmart", "jpmorgan", "goldman sachs", "bank of america", "disney",
    "salesforce", "oracle", "ibm", "intel", "samsung",
}

_AVAILABLE_YEARS = {2023, 2024}


def respond(user_message: str) -> Dict[str, Any]:
    """Return {answer: str, source: str, intent: str}."""
    msg_lower = user_message.lower()

    # Company scope guard
    if any(co in msg_lower for co in _OTHER_COMPANIES):
        return {
            "answer": (
                "This assistant is configured for **Prologis** sample data only.\n\n"
                "I can't retrieve data for other companies. Try asking about:\n"
                "- Prologis properties and financials\n"
                "- SEC filings (10-K / 10-Q)\n"
                "- Press releases and acquisitions\n"
                "- Portfolio summary for FY2023 or FY2024"
            ),
            "source": "System",
            "intent": "out_of_scope",
        }

    # Year availability hint
    requested_year = _extract_year(msg_lower)
    if requested_year and requested_year not in _AVAILABLE_YEARS:
        return {
            "answer": (
                f"No data is available for **{requested_year}**.\n\n"
                f"Available fiscal years: **{', '.join(str(y) for y in sorted(_AVAILABLE_YEARS))}**\n\n"
                "Try: _'What was net income in 2024?'_ or _'Portfolio summary for 2023'_"
            ),
            "source": "System",
            "intent": "out_of_scope",
        }

    intent, params = _detect_intent(user_message)

    # Try Anthropic first if configured
    if _anthropic.configured:
        # build context string
        ctx = _build_context(intent, params)
        prompt = f"Context data:\n{ctx}\n\nUser question: {user_message}"
        answer = _anthropic.chat(_SYSTEM_PROMPT, prompt)
        if answer:
            return {"answer": answer, "source": "Claude (Anthropic)", "intent": intent}

    # Try Vertex AI
    if _vertex.configured:
        ctx = _build_context(intent, params)
        prompt = f"Context data:\n{ctx}\n\nUser question: {user_message}"
        answer = _vertex.chat(prompt)
        if answer:
            return {"answer": answer, "source": "Vertex AI (Gemini)", "intent": intent}

    # Local rule-based fallback
    answer = _local_answer(intent, params, user_message)
    return {"answer": answer, "source": "Local (rule-based)", "intent": intent}


def _build_context(intent: str, params: Dict) -> str:
    try:
        if intent == "sec_filing":
            return str(sec_edgar.get_filings(form=params.get("form", "10-K"))[:1])
        if intent == "financials_summary":
            return str(queries.get_summary(fiscal_year=params.get("year") or 2024))
        if intent == "press_releases":
            return str(press_releases.get_all(keyword=params.get("keyword"))[:3])
        if intent == "properties":
            return str(queries.get_properties(metro_area=params.get("metro"), property_type=params.get("type"))[:5])
        if intent == "portfolio_summary":
            return str(queries.get_summary(fiscal_year=params.get("year", 2024)))
    except Exception:
        pass
    return ""


def _local_answer(intent: str, params: Dict, original: str) -> str:
    handlers = {
        "sec_filing":         _handle_sec_filing,
        "financials_summary": _handle_financials_summary,
        "press_releases":     _handle_press_releases,
        "properties":         _handle_properties,
        "portfolio_summary":  _handle_portfolio_summary,
    }
    handler = handlers.get(intent)
    if handler:
        return handler(params)
    return _unknown_response(original)
