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
_BLOG_20261023={
    "/blog/"+post["slug"]+"/":post["updated"]
    for post in json.loads((Path(__file__).resolve().parent/"data/blog-guides-20261023.json").read_text(encoding="utf8"))
}
_BLOG_20261024={
    "/blog/"+post["slug"]+"/":post["updated"]
    for post in json.loads((Path(__file__).resolve().parent/"data/blog-guides-20261024.json").read_text(encoding="utf8"))
}
_BLOG_20261025={
    "/blog/"+post["slug"]+"/":post["updated"]
    for post in json.loads((Path(__file__).resolve().parent/"data/blog-guides-20261025.json").read_text(encoding="utf8"))
}
_BLOG_20261026={
    "/blog/"+post["slug"]+"/":post["updated"]
    for post in json.loads((Path(__file__).resolve().parent/"data/blog-guides-20261026.json").read_text(encoding="utf8"))
}
_BLOG_20261027={
    "/blog/"+post["slug"]+"/":post["updated"]
    for post in json.loads((Path(__file__).resolve().parent/"data/blog-guides-20261027.json").read_text(encoding="utf8"))
}
_BLOG_20261028={
    "/blog/"+post["slug"]+"/":post["updated"]
    for post in json.loads((Path(__file__).resolve().parent/"data/blog-guides-20261028.json").read_text(encoding="utf8"))
}
_BLOG_20261029={
    "/blog/"+post["slug"]+"/":post["updated"]
    for i in (1,2,3)
    for post in [json.loads((Path(__file__).resolve().parent/f"data/blog-guides-20261029-{i}.json").read_text(encoding="utf8"))]
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

def review_change_dates(series, product_reviews):
    """Actual source-dated reviews may meaningfully change product pages.

    Records come from the authenticated, read-only D1 build snapshot.
    Never invent or update a review or its publication timestamp here.
    """
    by_model={
        str(row.get("model")):"/products/"+row["slug"]+"/"
        for row in series.values()
        if isinstance(row,dict) and row.get("model") and row.get("slug")
    }
    result={}
    for review in product_reviews or []:
        if not isinstance(review,dict) or review.get("status")!="published":
            continue
        url=by_model.get(str(review.get("model") or ""))
        actual=valid_date(str(review.get("reviewDate") or ""))
        if url and actual and actual>result.get(url,""):
            result[url]=actual
    return result


def source_lastmod(route,locale="en",revision=None,review_dates=None):
    canonical=re.sub(r"^/(?:es|pt|ru|tr)(?=/)","",route)
    if not canonical.startswith("/"):return None
    edited=None
    if isinstance(revision,dict):
        for key in ("contentUpdatedAt","lastSignificantUpdate","modifiedAt","updatedAt"):
            approved=valid_date(str(revision.get(key) or "")[:10])
            if approved:
                edited=approved
                break
    # Use reviewed content dates and genuine D1 publication dates, not
    # deployment timestamps. A rebuild alone must never change lastmod.
    baseline=valid_date(_SEO_TITLE_20261020.get(canonical) or BASELINE.get(canonical)
                        or _BLOG_20261020.get(canonical) or _BLOG_20261021.get(canonical) or _BLOG_20261022.get(canonical) or _BLOG_20261023.get(canonical) or _BLOG_20261024.get(canonical) or _BLOG_20261025.get(canonical) or _BLOG_20261026.get(canonical) or _BLOG_20261027.get(canonical) or _BLOG_20261028.get(canonical) or _BLOG_20261029.get(canonical))
    feedback=valid_date((review_dates or {}).get(canonical))
    dates=[v for v in (edited or baseline, feedback) if v]
    return max(dates) if dates else None
