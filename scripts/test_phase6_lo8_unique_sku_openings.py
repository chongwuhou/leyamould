#!/usr/bin/env python3
"""LO source-photo buyer introductions: 8 real models x 5 locales, owner edits win."""
from pathlib import Path
import hashlib, html, json, re, sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from site_renderer import SERIES
from lo_catalog import LO_PRODUCTS, detail
from sku_unique_openings import editor_intro
from sku_unique_openings_phase2 import COPY, CATEGORY
from sku_factual_sections import FIFTH10, BASE as H2_BASE, section as native_h2_section
LANGS=("en","es","pt","ru","tr")
EN=json.loads((ROOT/"data/phase6-lo8-openings-en.json").read_text(encoding="utf8"))["groups"]
BASE=json.loads((ROOT/"data/phase6-lo8-template-baselines.json").read_text(encoding="utf8"))["hashes"]
LO={x["slug"]:x for x in LO_PRODUCTS}
MODEL_GROUP={sku:g for g,items in EN.items() for sku in items}
assert len(MODEL_GROUP)==8 and set(MODEL_GROUP).issubset(LO) and set(MODEL_GROUP)==set(BASE)
assert all(len(BASE[sku])==4 for sku in LO)
records=[]
for sku in MODEL_GROUP:
    source=LO[sku]
    product=SERIES[source["model"]]
    assert product["category"]==CATEGORY[MODEL_GROUP[sku]]
    assert product["loNew"] and product["slug"]==sku
    for lang in LANGS:
        paragraph=COPY[sku][lang]
        assert 100<=len(paragraph.split())<=150,(sku,lang,len(paragraph.split()))
        assert sku.casefold() in paragraph.casefold()
        initial=detail(product,lang)
        if lang!="en":
            if sku in FIFTH10:
                # The entire LO source HTML was a legacy phase6 fingerprint.
                # Phase13 upgrades only independently owned Design/FAQ blocks:
                # keep exact new native-source fingerprints without freezing
                # other owner-controlled sections or blocking true source edits.
                for kind in ("design","faq"):
                    found=native_h2_section(initial,kind)
                    assert found and hashlib.sha256(found[2].encode("utf8")).hexdigest()[:16]==H2_BASE[sku][lang][kind],(sku,lang,kind,"source H2 baseline drift")
            else:
                assert hashlib.sha256(initial.encode("utf8")).hexdigest()==BASE[sku][lang],(sku,lang,"source baseline drift")
        converted=editor_intro(initial,product,lang)
        assert converted!=initial,(sku,lang,"missing source-stage editorial replacement")
        assert paragraph in html.unescape(converted),(sku,lang,"wrong model's intro")
        assert editor_intro(converted,product,lang)==converted,(sku,lang,"duplicate")
        owner=initial.replace('<nav class="breadcrumb">','<nav class="breadcrumb" data-owner-change="yes">',1)
        assert owner!=initial
        if lang!="en":
            assert editor_intro(owner,product,lang)==owner,(sku,lang,"translated owner body overwritten")
        else:
            # The canonical English site_renderer bypasses intro on BODY_OVERRIDES.
            assert editor_intro(owner,product,lang,owner_edited=True)==owner
        assert editor_intro(initial,product,lang,owner_edited=True)==initial
        path=ROOT/"dist"/("" if lang=="en" else lang)/"products"/sku/"index.html"
        page=path.read_text(encoding="utf8")
        marker=re.findall(r'<p\b(?=[^>]*\bdata-pilot-intro="'+re.escape(sku)+r'")[^>]*>(.*?)</p>',page,re.S)
        assert len(marker)==1,(sku,lang,"rendered marker missing or duplicate")
        visible=html.unescape(re.sub(r"<[^>]*>","",marker[0]))
        assert visible==paragraph,(sku,lang,"localized content mismatch")
        records.append((sku,lang,paragraph))
for lang in LANGS:
    passages=[text for sku,l,text in records if l==lang]
    assert len(set(passages))==8,(lang,"duplicate intro")
    assert len(set(" ".join(x.split()[:15]).casefold() for x in passages))==8,(lang,"generic lead")
future={**SERIES[LO["lo-001"]["model"]],"slug":"lo-future-approved-model","model":"LO-FUTURE"}
original='<h1>Future source model</h1><p class="copy-muted">Original body</p>'
assert editor_intro(original,future,"en")==original
print("XUYI_LO8_NATIVE_SOURCE_FIVE_LANG_CMS_PROTECTION_PASSED",len(records),"localized routes")