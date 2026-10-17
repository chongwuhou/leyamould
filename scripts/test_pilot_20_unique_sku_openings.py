#!/usr/bin/env python3
"""Proof: twenty genuinely SKU-specific 100-150 word source introductions.

Four product collections x five reviewed catalog models x five languages.
Owner-edited D1 copy wins, untouched SKUs stay untouched, rerenders do not
duplicate and the next catalog SKU isn't trapped by a historic page count.
"""
from pathlib import Path
from collections import Counter
from html import unescape
from hashlib import sha256
import sys,re,json
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from sku_unique_openings import COPY,EN,CATEGORY,LOCALES,OWNER,editor_intro
from sku_unique_openings_phase2 import COPY as PHASE2_COPY
from site_renderer import SERIES
DIST=ROOT/"dist"
from scripts.ci_current_owner_assertions import check_product_page
langs=("en","es","pt","ru","tr")
assert len(EN)==4
assert all(len(items)==5 for items in EN.values()),{k:len(v) for k,v in EN.items()}
assert len(COPY)==20
assert len(OWNER)==20
assert all(len(fields)==4 for fields in OWNER.values())
assert len(SERIES)>20

snapshot=json.loads((ROOT/"_local_ops/build-snapshot.json").read_text(encoding="utf8"))
D1={(v["resourceId"][5:],v["locale"]):v["content"]["mainHtml"]
    for v in snapshot["translations"]
    if v.get("resourceId","").startswith("page:") and v["locale"] in langs[1:]}
for slug,contents in COPY.items():
    row=next((r for r in SERIES.values() if r["slug"]==slug),None)
    assert row is not None and row["category"] in CATEGORY.values(),slug
    assert set(contents)==set(langs),slug
    for lang in langs:
        copy=contents[lang]
        assert 100<=len(copy.split())<=150,(slug,lang,len(copy.split()))
        assert str(row["model"]) in copy,(slug,lang)
        if lang=="tr":assert "spor şapkalar" not in copy,slug
        doc=(DIST/("" if lang=="en" else lang)/"products"/slug/"index.html").read_text(encoding="utf8")
        excerpts=re.findall(r'<p\b(?=[^>]*data-pilot-intro="([^"]+)")[^>]*>(.*?)</p>',doc,re.S)
        # The owner can revise the page after the legacy intro was authored.
        # Validate real rendered model content, never demand an obsolete marker.
        baseline=(lang!="en" and sha256(D1[("/products/"+slug+"/",lang)].encode("utf8")).hexdigest()==OWNER[slug][lang])
        check_product_page(DIST/("" if lang=="en" else lang)/"products"/slug/"index.html",slug,copy,requires_old_marker=bool(baseline))
        if lang!="en":
            source=D1[("/products/"+slug+"/",lang)]
            if sha256(source.encode("utf8")).hexdigest()==OWNER[slug][lang]:
                expected=editor_intro(source,row,lang)
                assert expected!=source and copy in unescape(expected)
                assert editor_intro(expected,row,lang)==expected,(slug,lang,"double injection")
            else:
                # Genuine current D1 copy wins; never require the old hash.
                assert editor_intro(source,row,lang)==source,(slug,lang,"CMS owner edit overwritten")
            # Any subsequent D1 owner change, including one unrelated to the
            # first paragraph, must block the entire historic source injection.
            edited=source.replace("<nav class=", '<nav data-owner-revised="yes" class=',1)
            assert edited!=source
            assert editor_intro(edited,row,lang)==edited,(slug,lang,"CMS override lost")
            assert editor_intro(source,row,"en",owner_edited=True)==source

# All twenty prose introductions must be genuinely different, not a
# one-paragraph category template with a substituted model code.
for lang in langs:
    paragraphs=[COPY[slug][lang] for slug in COPY]
    assert len(paragraphs)==len(set(paragraphs))
    # First 24 words must vary for every model within the same collection.
    for category,items in EN.items():
        starts=[" ".join(COPY[slug][lang].split()[:24]).lower() for slug in items]
        assert len(starts)==len(set(starts)),(category,lang)

others=[r for r in SERIES.values() if r["slug"] not in COPY and r["slug"] not in PHASE2_COPY]
for row in others[:7]:
    sample=(DIST/"products"/row["slug"]/"index.html").read_text(encoding="utf8")
    assert 'data-pilot-intro="' not in sample,row["slug"]
    assert editor_intro('<h1>Another SKU</h1><p class="copy-muted">Owner text</p>',
                        row,"en")=='<h1>Another SKU</h1><p class="copy-muted">Owner text</p>'
# New models don't require changing a historical 20/101/505 URL count.
new_model={**SERIES["2501"],"slug":"new-factory-sku-2027","model":"NEW-SKU-2027"}
assert editor_intro('<h1>Future</h1><p class="copy-muted">Future copy</p>',new_model,'en')=='<h1>Future</h1><p class="copy-muted">Future copy</p>'

print("XUYI_TWENTY_UNIQUE_SKU_OPENINGS_PASSED",len(COPY),"models",len(COPY)*len(langs),"localized", "words",{
  lang:(min(len(COPY[s][lang].split()) for s in COPY),
        max(len(COPY[s][lang].split()) for s in COPY)) for lang in langs})