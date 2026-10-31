"""D1/CMS-aware, pre-render blog descriptions for three Oct 31 articles.

Only normalize a known AI-authored duplicate baseline when the D1 value has
NOT changed. Future owner-edited D1 descriptions always win. This runs
before HTML rendering and never edits dist or post-generated markup.
"""
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "blog-descriptions-baseline-20261031.json"

@lru_cache(maxsize=1)
def reviewed_descriptions():
    data=json.loads(SOURCE.read_text(encoding="utf8"))
    assert data["site"]=="xuyi-drinkware-site" and data["schemaVersion"]==1
    out={(r["route"],r["locale"]):r for r in data["records"]}
    if len(out)!=12:raise RuntimeError("Reviewed baseline inventory must contain 12 distinct source entries")
    return out

def resolve_description(route,locale,description):
    baseline=reviewed_descriptions().get((route,locale))
    if baseline is None or description!=baseline["baseline"]:
        return description  # D1 owner edits, including future SEO descriptions, take precedence.
    return baseline["approved"]
