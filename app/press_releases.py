"""Press release loader and search."""
import json
from pathlib import Path
from typing import List, Dict, Optional

_DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "press_releases.json"


def _load() -> List[Dict]:
    try:
        return json.loads(_DATA_FILE.read_text())
    except Exception:
        return []


def get_all(category: Optional[str] = None, keyword: Optional[str] = None) -> List[Dict]:
    releases = _load()
    if category:
        releases = [r for r in releases if r.get("category", "").lower() == category.lower()]
    if keyword:
        kw = keyword.lower()
        releases = [
            r for r in releases
            if kw in r.get("title", "").lower()
            or kw in r.get("summary", "").lower()
            or any(kw in k.lower() for k in r.get("keywords", []))
        ]
    return releases


def get_categories() -> List[str]:
    return sorted({r.get("category", "") for r in _load() if r.get("category")})


def get_recent(n: int = 5) -> List[Dict]:
    return sorted(_load(), key=lambda r: r.get("date", ""), reverse=True)[:n]
