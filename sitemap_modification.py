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
def _load_d1_dates(field):
    snapshot=Path(__file__).resolve().parent/"_local_ops"/"build-snapshot.json"
    if not snapshot.is_file():return {}
    try:data=json.loads(snapshot.read_text(encoding="utf8"))
    except (OSError,ValueError):return {}
    result={}
    for row in data.get(field,[]):
        if not isinstance(row,dict):continue
        if field=="blogPosts":
            if row.get("status")!="published":continue
            slug=str(row.get("slug") or "")
            route="/blog/"+slug+"/"
            raw=str(row.get("updated_at") or row.get("updated") or row.get("published_at") or "")
        else:
            slug=str(row.get("slug") or "")
            route="/products/"+slug+"/"
            raw=str(row.get("updatedAt") or row.get("updated_at") or "")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9-]*)*",slug):continue
        match=re.match(r"(\d{4}-\d{2}-\d{2})",raw)
        if not match:continue
        value=valid_date(match.group(1))
        if value and value>result.get(route,""):result[route]=value
    return result

_D1_BLOG_DATES=_load_d1_dates("blogPosts")
_D1_PRODUCT_SEO_DATES=_load_d1_dates("productSeo")

DATE_RE=re.compile(r"^\d{4}-\d{2}-\d{2}$")

def valid_date(value):
    if not isinstance(value,str) or not DATE_RE.fullmatch(value):return None
    try:
        result=date.fromisoformat(value)
        # Publication dates use the site editorial timezone, not UTC runner dates.
        if result>datetime.now(ZoneInfo("Asia/Shanghai")).date():return None
        return value
    except ValueError:return None


def _load_d1_blog_dates():
    snapshot=Path(__file__).resolve().parent/"_local_ops"/"build-snapshot.json"
    if not snapshot.is_file():return {}
    try:data=json.loads(snapshot.read_text(encoding="utf8"))
    except (OSError,ValueError):return {}
    result={}
    for post in data.get("blogPosts",[]):
        if not isinstance(post,dict) or post.get("status")!="published":continue
        slug=str(post.get("slug") or "")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",slug):continue
        raw=str(post.get("updated") or post.get("updated_at") or post.get("published_at") or "")
        candidate=re.match(r"(\d{4}-\d{2}-\d{2})",raw)
        if not candidate:
            parsed=re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})",raw)
            if parsed:candidate=re.match(r"(.*)",f"{parsed.group(3)}-{int(parsed.group(1)):02d}-{int(parsed.group(2)):02d}")
        if candidate:
            value=valid_date(candidate.group(1))
            if value:result["/blog/"+slug+"/"]=value
    return result

_D1_BLOG_DATES=_load_d1_blog_dates()

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
    candidates=[valid_date(BASELINE.get(canonical)),
                valid_date(_D1_PRODUCT_SEO_DATES.get(canonical)),
                valid_date(_D1_BLOG_DATES.get(canonical))]
    baseline=max((value for value in candidates if value),default=None)
    feedback=valid_date((review_dates or {}).get(canonical))
    dates=[v for v in (edited or baseline, feedback) if v]
    return max(dates) if dates else None