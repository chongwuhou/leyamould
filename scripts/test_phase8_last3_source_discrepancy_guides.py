#!/usr/bin/env python3
"""Last three SKU buyer guides: correct uncertainty + CMS precedence, no fake product specifications."""
from pathlib import Path
from hashlib import sha256
from html import unescape
import json,re,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from sku_unique_openings import editor_intro
from sku_unique_openings_phase2 import COPY,CATEGORY,SELECTED_GROUP
from site_renderer import SERIES
LANGS=("en","es","pt","ru","tr")
GROUPS=json.loads((ROOT/"data/phase8-last3-buyer-intros-en.json").read_text(encoding="utf8"))["groups"]
BASE=json.loads((ROOT/"data/phase8-last3-d1-baselines.json").read_text(encoding="utf8"))["hashes"]
SELECTED={sku:group for group,items in GROUPS.items() for sku in items}
assert SELECTED=={"2506":"sports","5247":"shakers","5248":"shakers"}
assert set(BASE)==set(SELECTED) and all(set(value)==set(LANGS[1:]) for value in BASE.values())
snapshot=json.loads((ROOT/"_local_ops/build-snapshot.json").read_text(encoding="utf8"))
d1={(r["resourceId"][5:],r["locale"]):r["content"]["mainHtml"]
    for r in snapshot["translations"] if r.get("resourceId","").startswith("page:")}
from scripts.ci_current_owner_assertions import check_product_page
records=[]
for sku,group in SELECTED.items():
    row=next(r for r in SERIES.values() if r["slug"]==sku)
    assert row["category"]==CATEGORY[group] and row["model"]==sku
    if sku=="2506":
        assert row["capacity"]=="60ml" # disputed source value, never verified as actual capacity
        assert row["dimensions"]=="8.3*26.8"
    else:
        assert row["material"]=="PP"
        assert "450" in row["capacity"] and "700" in row["capacity"]
        assert row["images"][0]=="/media/ppt/slide-096.webp"
    assert set(COPY[sku])==set(LANGS)
    for lang in LANGS:
        text=COPY[sku][lang]
        assert sku in text and 100<=len(text.split())<=150,(sku,lang,len(text.split()))
        source=d1.get(("/products/"+sku+"/",lang)) if lang!="en" else None
        if lang!="en":
            assert isinstance(source,str),(sku,lang,"source translation missing")
            digest=sha256(source.encode("utf8")).hexdigest()
            if digest==BASE[sku][lang]:
                updated=editor_intro(source,row,lang)
                assert updated!=source and text in unescape(updated),(sku,lang,"missing")
                assert editor_intro(updated,row,lang)==updated,(sku,lang,"not idempotent")
                owner_edit=source.replace("<nav class=",'<nav data-owner-change="yes" class=',1)
                assert owner_edit!=source
                assert editor_intro(owner_edit,row,lang)==owner_edit,(sku,lang,"owner text overwritten")
                assert editor_intro(source,row,lang,owner_edited=True)==source
            else:
                # New CMS edits win, even if the old template baseline was altered.
                assert editor_intro(source,row,lang)==source,(sku,lang,"unexpected owner override")
        html_path=ROOT/"dist"/("" if lang=="en" else lang)/"products"/sku/"index.html"
        page=html_path.read_text(encoding="utf8")
        results=re.findall(r'<p\b(?=[^>]*data-pilot-intro="'+re.escape(sku)+r'")[^>]*>(.*?)</p>',page,re.S)
        baseline=lang!="en" and source and sha256(source.encode("utf8")).hexdigest()==BASE[sku][lang]
        check_product_page(html_path,sku,text,requires_old_marker=bool(baseline))
        # HTML must retain the factory discrepancy / shared-source distinction.
        if sku=="2506":
            assert "60ml" in page and "catalog discrepancy" in page if lang=="en" else True
        else:
            assert ("450ml" in page or "450 ml" in page)
            assert ("700ml" in page or "700 ml" in page)
        records.append((sku,lang,text))
for lang in LANGS:
    sentences=[v for sku,l,v in records if l==lang]
    assert len(set(sentences))==3
    assert len(set(" ".join(t.split()[:16]).casefold() for t in sentences))==3
new={**next(r for r in SERIES.values() if r["slug"]=="2506"),"slug":"new-approved-sku-2027","model":"NEW-2027"}
test='<h1>Future approved</h1><p class="copy-muted">Keep source</p>'
assert editor_intro(test,new,"en")==test
from scripts.audit_product_body_similarity import audit,median_or_none
assert median_or_none([]) is None
assert median_or_none([0.1,0.3])==0.2
sim=audit()
assert len(sim["rows"])==5*len(SERIES)
assert all(row["count"]>0 or (row["median_nearest_main"] is None and row["median_nearest_intro"] is None) for row in sim["summary"])
from scripts.prepare_product_copy_queue import write_queue
from tempfile import TemporaryDirectory
import csv
with TemporaryDirectory() as d:
    p=Path(d)/"editorial-queue.csv"
    write_queue([],p)
    with p.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        assert "sku" in reader.fieldnames and list(reader)==[], "zero remaining must be valid"
flags=json.loads((ROOT/"data/phase8-factory-fact-verification-pending.json").read_text(encoding="utf8"))["items"]
assert set(x["sku"] for x in flags)==set(SELECTED)
assert all(x["verificationStatus"]=="pending_factory" and x["requestedEvidence"] for x in flags)
print("XUYI_LAST3_FACTUALLY_QUALIFIED_15_LOCALE_CMS_PASSED",len(records),"model/locale pages")