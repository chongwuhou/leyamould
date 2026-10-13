#!/usr/bin/env python3
"""Simulate future D1 edits and verify old SEO copy cannot overwrite them."""
from copy import deepcopy
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from cms_seo_curation_guard import snapshot,baseline,may_curate

current=snapshot()
assert current is not None and current.get("site")=="xuyi-drinkware-site"
old=baseline()
assert len(old)>=380
cases=[
    ("en","/about/","title"),
    ("es","/capabilities/","description"),
    ("pt","/collections/sports-water-bottles/","description"),
    ("ru","/collections/kids-water-bottles/","description"),
    ("tr","/products/2501/","title"),
    ("es","/products/501/","description"),
]
edited=deepcopy(current)
for lang,route,field in cases:
    # A real owner change may already exist when CI runs: it must not fail
    # merely because the older curation is no longer eligible.
    if lang=="en":
        entry=next(p for p in edited["pages"] if p.get("route")==route)
        entry["seo_title" if field=="title" else "meta_description"]="Owner-updated "+field+" on "+route
    else:
        entry=next(p["content"] for p in edited["translations"]
                   if p.get("locale")==lang and p.get("resourceId")=="page:"+route)
        entry[field]="Owner-updated "+field+" on "+route
    assert not may_curate(lang,route,field,edited),("Owner edit would be overwritten",lang,route,field)
    # The original snapshot's own eligibility is intentionally allowed to
    # vary; future owner changes should not require touching this test.

# A new SKU or article is not automatically rewritten based on older models.
assert not may_curate("es","/products/new-approved-model/","title",edited)
assert not may_curate("en","/about/","title",edited,baseline_data={})
print("XUYI_CMS_FUTURE_EDITS_PROTECTED",len(cases),"simulated edits, unknown routes excluded")