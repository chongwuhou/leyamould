"""Preserve future user-edited CMS SEO fields during every source rebuild.

The source baseline contains only hashes of the CMS title and description
before historic one-time SEO curation. When an owner edits either field in
D1, later builds honor the edit instead of reapplying our older suggestion.
It never stores private form data or raw SEO copy in the repository.
"""
import hashlib
import json
from functools import lru_cache
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
BASELINE=ROOT/"data/seo_curation_cms_baseline_sha256.json"
SNAPSHOT=ROOT/"_local_ops/build-snapshot.json"

def fingerprint(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

@lru_cache(maxsize=1)
def baseline():
    data=json.loads(BASELINE.read_text(encoding="utf-8"))
    if data.get("site")!="xuyi-drinkware-site" or data.get("schemaVersion")!=1:
        raise ValueError("CMS curation baseline belongs to another site")
    return data["baseline"]

@lru_cache(maxsize=1)
def snapshot():
    if not SNAPSHOT.exists():
        return None
    data=json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    if data.get("site")!="xuyi-drinkware-site":
        raise ValueError("CMS snapshot belongs to another site")
    return data

def current_field(locale,route,field,snapshot_data=None):
    data=snapshot() if snapshot_data is None else snapshot_data
    if data is None:
        return None
    if locale=="en":
        row=next((x for x in data.get("pages",[]) if x.get("route")==route),None)
        if route.startswith("/products/"):
            sku=route.strip("/").split("/")[-1]
            product=next((x.get("content",{}) for x in data.get("products",[])
                          if str(x.get("model"))==sku),{})
            custom=product.get("seoTitle" if field=="title" else "seoDescription")
            if isinstance(custom,str) and custom.strip():
                return custom
        return (row or {}).get("seo_title" if field=="title" else "meta_description")
    row=next((x.get("content",{}) for x in data.get("translations",[])
              if x.get("locale")==locale and x.get("resourceId")=="page:"+route),{})
    return row.get(field)

def may_curate(locale,route,field,snapshot_data=None,baseline_data=None):
    """True only for unchanged original CMS copy; unknown edits are preserved."""
    data=snapshot() if snapshot_data is None else snapshot_data
    if data is None:
        return True  # No D1 snapshot, plain source template build.
    expected=(baseline() if baseline_data is None else baseline_data).get(locale+":"+route,{})
    hash_value=expected.get(field)
    if not hash_value:
        return False  # Newly published CMS entry, never auto-rewrite it.
    actual=current_field(locale,route,field,data)
    return isinstance(actual,str) and fingerprint(actual)==hash_value