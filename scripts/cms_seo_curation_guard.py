"""Preserve future user-edited CMS SEO fields during every source rebuild.

The source baseline contains only hashes of the CMS title and description
before historic one-time SEO curation. When an owner edits either field in
D1, later builds honor the edit instead of reapplying our older suggestion.
It never stores private form data or raw SEO copy in the repository.
"""
import hashlib
import json
import sys
from functools import lru_cache
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
BASELINE=ROOT/"data/seo_curation_cms_baseline_sha256.json"
SNAPSHOT=ROOT/"_local_ops/build-snapshot.json"

def fingerprint(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

@lru_cache(maxsize=1)
def baseline():
    data=json.loads(BASELINE.read_text(encoding="utf-8"))
    if data.get("site")!="leyamould" or data.get("schemaVersion")!=1:
        raise ValueError("CMS curation baseline belongs to another site")
    return data["baseline"]

@lru_cache(maxsize=1)
def snapshot():
    if not SNAPSHOT.exists():
        return None
    data=json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    if data.get("site")!="leyamould":
        raise ValueError("CMS snapshot belongs to another site")
    return data

def current_field(locale,route,field,snapshot_data=None):
    data=snapshot() if snapshot_data is None else snapshot_data
    if data is None:
        return None
    seo_key="seoTitle" if field=="title" else "metaDescription"

    def product_seo_value(product_route):
        if not product_route.startswith("/products/"):
            return None
        sku=product_route.strip("/").split("/")[-1]
        seo_row=next((x for x in data.get("productSeo",[])
                      if x.get("slug")==sku and x.get("locale")==locale),None)
        value=(seo_row or {}).get(seo_key)
        return value if isinstance(value,str) and value.strip() else None

    # The exact canonical productSeo key is authoritative before any legacy
    # slug fallback. A canonical D1 row can exist before its old page alias is
    # removed; resolving the alias first would compare a different SKU's SEO.
    if route.startswith("/products/"):
        exact=product_seo_value(route)
        if exact is not None:
            return exact

    # Five catalog variants were published with malformed legacy slugs.
    # Keep their D1 SEO under the old key only when no exact canonical product
    # SEO row or direct CMS page/translation exists.
    from product_slug_fix import REVERSE
    if route.startswith("/products/"):
        clean_slug=route.removeprefix("/products/").strip("/")
        legacy=REVERSE.get(clean_slug)
        if legacy:
            if locale=="en":
                direct=any(x.get("route")==route for x in data.get("pages",[]))
            else:
                direct=any(x.get("locale")==locale and
                           x.get("resourceId")=="page:"+route
                           for x in data.get("translations",[]))
            if not direct:
                legacy_route="/products/"+legacy+"/"
                legacy_value=product_seo_value(legacy_route)
                if legacy_value is not None:
                    return legacy_value
                route=legacy_route

    if locale=="en":
        row=next((x for x in data.get("pages",[]) if x.get("route")==route),None)
        if route.startswith("/products/"):
            sku=route.strip("/").split("/")[-1]
            product=next((x.get("content",{}) for x in data.get("products",[])
                          if str(x.get("model"))==sku),{})
            field_name="seoTitle" if field=="title" else "seoDescription"
            custom=product.get(field_name)
            if isinstance(custom,str) and custom.strip():
                from catalog_extensions import is_factory_catalog_source_default
                if not is_factory_catalog_source_default(sku,product,field_name):
                    return custom
                # An unchanged import default is not owner-authored product SEO.
                # Fall through so a separately edited page-level title is retained.
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
