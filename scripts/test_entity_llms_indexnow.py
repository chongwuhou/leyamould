#!/usr/bin/env python3
"""Verified entity signals and FAQ summaries; no fictional SearchAction."""
from pathlib import Path
import sys,re,json,hashlib
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from organization_source_schema import SUBJECTS,enrich_organization
from scripts.search_submission import new_or_changed,HOST,INDEXNOW,key_file
D=ROOT/"dist"
faq=json.loads((ROOT/"data/faq-expanded.json").read_text(encoding="utf8"))
facts=json.loads((ROOT/"data/llms-verified-facts.json").read_text(encoding="utf8"))
text=(D/"llms.txt").read_text(encoding="utf8")
assert text.count("**Q: ")==len(facts["questionRefs"]) and 5<=len(facts["questionRefs"])<=8
assert facts["legalName"] in text and facts["base"] in text and facts["scope"] in text
assert facts["lastSubstantiveReview"] in text and "No AI search engine is guaranteed" in text
for group,num in facts["questionRefs"]:
    entry=next(g for g in faq["categories"] if g["id"]==group)["questions"][num]
    q,a,url=entry
    assert "**Q: "+q+"**" in text
    assert a.split(". ")[0]+"." in text
assert "https://leyamould.com/faq/" in text

for lang in ("","es/","pt/","ru/","tr/"):
 for route in ("","about/","faq/"):
    page=(D/lang/route/"index.html").read_text(encoding="utf8")
    graphs=[json.loads(v) for v in re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>',page)]
    organizations=[v for graph in graphs for v in graph.get("@graph",[]) if v.get("@type")=="Organization"]
    assert len(organizations)==1,(lang,route,len(organizations))
    org=organizations[0]
    assert org["legalName"]==facts["legalName"],(lang,route)
    assert org["contactPoint"]["contactType"]=="sales",(lang,route)
    assert org["contactPoint"]["url"]=="https://leyamould.com/contact/",(lang,route)
    assert set(SUBJECTS)<=set(org["knowsAbout"]),(lang,route)
# The source helper must never replace owner-supplied verified contact points.
edited={"@type":"Organization","contactPoint":{"@type":"ContactPoint","contactType":"sales","email":"owner-verified@example.com"},"knowsAbout":["owner approved polymer"]}
updated=enrich_organization(edited)
assert updated["contactPoint"]==edited["contactPoint"] and updated["knowsAbout"]==edited["knowsAbout"]
assert updated==enrich_organization(updated)

# SearchAction is intentionally absent because XUYI has no sitewide
# searchable result URL; Google stopped showing sitelinks searchbox in 2024.
site=(D/"index.html").read_text(encoding="utf8")
assert "SearchAction" not in site
# The notifications are a subset of changed canonical URLs, never images.
start={"site":"leyamould","urls":{"https://leyamould.com/":"a","https://leyamould.com/products/2095/":"a"}}
end={"site":"leyamould","urls":{"https://leyamould.com/":"a","https://leyamould.com/products/2095/":"b","https://leyamould.com/products/new/":"c"}}
assert new_or_changed(start,end)==["https://leyamould.com/products/2095/","https://leyamould.com/products/new/"]
assert new_or_changed(end,end)==[]
workflow=(ROOT/".github/workflows/publish-leyamould.yml").read_text(encoding="utf8")
assert workflow.index("Verify XUYI live deployment")<workflow.index("Notify IndexNow of verified changed URLs")
assert "python scripts/search_submission.py --submit" in workflow
assert "XUYI_INDEXNOW_KEY" in workflow
assert "Prepare stable IndexNow ownership key" in workflow
assert "::add-mask::$derived" in workflow
assert "hmac.new(" in workflow and "indexnow:xuyibottles.com:v2" in workflow
assert workflow.index("Prepare stable IndexNow ownership key")<workflow.index("Build from shared templates and source data")
print("XUYI_ENTITY_LLM_GUIDE_INDEXNOW_GUARDS_PASSED",len(facts["questionRefs"]),"FAQs",15,"page schemas")
