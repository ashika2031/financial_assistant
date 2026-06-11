"""SEC EDGAR data loader.

Loads from local JSON sample. If EDGAR_LIVE=1 in .env, attempts live fetch
from the public EDGAR full-text search API (no key required).
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Optional

_DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "sec_filings.json"
_LIVE = os.environ.get("EDGAR_LIVE", "0") == "1"


def _load_local() -> Dict:
    try:
        return json.loads(_DATA_FILE.read_text())
    except Exception:
        return {}


def get_company_info() -> Dict:
    data = _load_local()
    return {k: v for k, v in data.items() if k != "filings"}


def get_filings(form: Optional[str] = None, fiscal_year: Optional[int] = None) -> List[Dict]:
    data = _load_local()
    filings = data.get("filings", [])
    if form:
        filings = [f for f in filings if f.get("form") == form]
    if fiscal_year:
        filings = [f for f in filings if f.get("fiscal_year") == fiscal_year]
    return filings


def get_latest_10k() -> Optional[Dict]:
    filings = get_filings(form="10-K")
    return filings[0] if filings else None


def get_latest_10q() -> Optional[Dict]:
    filings = get_filings(form="10-Q")
    return sorted(filings, key=lambda f: f.get("filed", ""), reverse=True)[0] if filings else None


def get_metric_history(metric: str) -> List[Dict]:
    """Return [{period, value}] for a given metric across all filings."""
    results = []
    for f in _load_local().get("filings", []):
        if metric in f:
            results.append({"period": f["period"], "filed": f["filed"], "value": f[metric]})
    return sorted(results, key=lambda x: x["filed"])
