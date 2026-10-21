"""Source-backed sitemap dates: changed primary content, never build timestamps.

Historical verified 2026-10-14 route reviews are version-controlled. Unknown
future CMS routes stay undated until an actual editor modification date exists.
"""
import json
import re
from datetime import date,datetime
from zoneinfo import ZoneInfo
from pathlib import Path

CONFIG=json.loads((Path(__file__).resolve().parent/"data/sitemap-reviewed-lastmod.json").read_text(encoding="utf8"))
BASELINE=CONFIG["routes"]
_BLOG_20261020={
    "/blog/"+post["slug"]+"/":post["updated"]
    for post in json.loads((Path(__file__).resolve().parent/"data/blog-guides-20261020.json").read_text(encoding="utf8"))
}
_BLOG_20261021={
    "/blog/"+post["slug"]+"/":post["updated"]
    for post in json.loads((Path(__file__).resolve().parent/"data/blog-guides-20261021.json").read_text(encoding="utf8"))
}
_BLOG_20261022={
    "/blog/"+post["slug"]+"/":post["updated"]
    for post in json.loads((Path(__file__).resolve().parent/"data/blog-guides-20261022.json").read_text(encoding="utf8"))
}
_SEO_TITLE_RELEASE=json.loads((Path(__file__).resolve().parent/"data/product-seo-title-refresh-20261020.json").read_text(encoding="utf8"))
if _SEO_TITLE_RELEASE.get("schemaVersion")!=1 or len(_SEO_TITLE_RELEASE.get("slugs",[]))!=92:
    raise ValueError("Product SEO change-set is not the reviewed 92-model release")
_SEO_TITLE_20261020={"/products/"+slug+"/":_SEO_TITLE_RELEASE["significantChangeDate"]
                      for slug in _SEO_TITLE_RELEASE["slugs"]}
DATE_RE=re.compile(r"^\d{4}-\d{2}-\d{2}$")

def valid_date(value):
    if not isinstance(value,str) or not DATE_RE.fullmatch(value):return None
    try:
        result=date.fromisoformat(value)
        # Publication dates use the site editorial timezone, not UTC runner dates.
        if result>datetime.now(ZoneInfo("Asia/Shanghai")).date():return None
        return value
    except ValueError:return None

def source_lastmod(route,locale="en",revision=None):
    canonical=re.sub(r"^/(?:es|pt|ru|tr)(?=/)","",route)
    if not canonical.startswith("/"):return None
    if isinstance(revision,dict):
        for key in ("contentUpdatedAt","lastSignificantUpdate","modifiedAt","updatedAt"):
            approved=valid_date(str(revision.get(key) or "")[:10])
            if approved:return approved
    # One actual, source-reviewed SEO title update for 92 verified-capacity
    # model pages × five locales. Never change lastmod on every rebuild.
    return valid_date(_SEO_TITLE_20261020.get(canonical) or BASELINE.get(canonical)
                      or _BLOG_20261020.get(canonical) or _BLOG_20261021.get(canonical) or _BLOG_20261022.get(canonical))
