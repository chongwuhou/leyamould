"""Source-backed sitemap dates: changed primary content, never build timestamps.

Historical verified 2026-10-14 route reviews are version-controlled. Unknown
future CMS routes stay undated until an actual editor modification date exists.
"""
import json
import re
from datetime import date
from pathlib import Path

CONFIG=json.loads((Path(__file__).resolve().parent/"data/sitemap-reviewed-lastmod.json").read_text(encoding="utf8"))
BASELINE=CONFIG["routes"]
DATE_RE=re.compile(r"^\d{4}-\d{2}-\d{2}$")

def valid_date(value):
    if not isinstance(value,str) or not DATE_RE.fullmatch(value):return None
    try:
        result=date.fromisoformat(value)
        if result>date.today():return None
        return value
    except ValueError:return None

def source_lastmod(route,locale="en",revision=None):
    canonical=re.sub(r"^/(?:es|pt|ru|tr)(?=/)","",route)
    if not canonical.startswith("/"):return None
    if isinstance(revision,dict):
        for key in ("contentUpdatedAt","lastSignificantUpdate","modifiedAt","updatedAt"):
            approved=valid_date(str(revision.get(key) or "")[:10])
            if approved:return approved
    return valid_date(BASELINE.get(canonical))