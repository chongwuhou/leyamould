#!/usr/bin/env python3
"""P0 source template About: five languages, legal entity, owner edit immunity."""
from pathlib import Path
from html import unescape
import json,re,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from about_company_page import source,render,apply_body,baseline_body,metadata_unchanged,replace_head_if_original,ASSETS
DIST=ROOT/"dist"
logo_source=(ROOT/"data/customer-logos.json").read_bytes()
body_signatures=[]
for loc in ("en","es","pt","ru","tr"):
    d=source(loc)
    folder="" if loc=="en" else loc+"/"
    route="/" + folder + "about/"
    html=(DIST / folder / "about/index.html").read_text(encoding="utf8")
    head,body=html.split('<main id="main-content">',1)
    body=body.split("</main>",1)[0]
    assert body.count('id="xuyi-about-company"')==1,loc
    assert '<div id="xuyi-about-company"' in body,loc
    assert unescape(re.search(r"<title>(.*?)</title>",head).group(1))==d["title"],loc
    assert unescape(re.search(r'<meta name="description" content="([^"]+)"',head).group(1))==d["description"],loc
    assert d["h1"] in unescape(body),loc
    assert "台州市旭一家居用品有限公司" in body,loc
    assert "Taizhou Xuyi Household Goods Co., Ltd." in body,loc
    assert len(re.findall(r'class="xac-workflow"',body))==1,loc
    assert body.count('class="xac-quality"')==1
    assert body.count('<figure>')==4,loc
    assert body.count('class="xac-no-claims"')==1,loc
    assert '"/assets/about-company.css"' not in body
    assert '/assets/about-company.css' in head
    for url in ASSETS:assert body.count('src="'+url+'"')==1,(loc,url)
    for link in ["/products/","/request-sample/","/contact/#inquiry"]:
        pref="" if loc=="en" else "/"+loc
        assert 'href="'+pref+link+'"' in body,(loc,link)
    pref="" if loc=="en" else "/"+loc
    assert body.count('href="'+pref+'/manufacturing/"')==1
    assert body.count('href="'+pref+'/quality-control/"')==1
    text=unescape(re.sub(r"<[^>]+>"," ",body))
    for banned in ("leading manufacturer","world's best","#1","largest manufacturer","stock-photo factory image"):
        assert banned not in text.lower(),(loc,banned)
    assert not re.search(r"\b(?:founded|established)\s+in\s+\d{4}\b",text,re.I),loc
    graphs=[json.loads(m) for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>',head,re.S)]
    entities=[n for obj in graphs for n in (obj.get("@graph",[]) if "@graph" in obj else [obj])]
    legal=[x for x in entities if x.get("@type")=="Organization" and x.get("legalName")=="台州市旭一家居用品有限公司"]
    assert legal and legal[0]["address"]["addressLocality"]=="Taizhou",loc
    assert any(x.get("@type")=="WebPage" for x in entities),loc
    assert any(x.get("@type")=="BreadcrumbList" for x in entities),loc
    assert all(x.get("foundingDate") is None for x in entities),loc
    assert apply_body(body,loc)==body,loc
    assert not baseline_body('<p>A new independently written CMS company profile</p>',loc)
    assert apply_body('<p>A new independently written CMS company profile</p>',loc)=='<p>A new independently written CMS company profile</p>'
    assert render(loc).startswith('<div id="xuyi-about-company"'),loc
    assert len(d["glance"])==6 and len(d["workflow"])==5 and len(d["quality"])==6
    body_signatures.append(len(body))
assert (ROOT/"data/customer-logos.json").read_bytes()==logo_source
assert (DIST/"products/2095/index.html").exists()
assert (DIST/"products/g-02/index.html").exists()
assert (DIST/"sitemap.xml").read_text(encoding="utf8").count("<loc>")==755
print("XUYI_SOURCE_ABOUT_FIVE_LANGUAGES_PASSED",body_signatures)