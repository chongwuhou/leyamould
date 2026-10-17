#!/usr/bin/env python3
"""P0 authoritative 16-guide research and customizable G-series release gate."""
from pathlib import Path
from html import unescape
import sys,re,json,hashlib
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"scripts"))
from blog_editorial import GUIDES,BLOG_DEPTH,render_depth_evidence,owner_safe_depth
from site_renderer import SERIES
from g_series_material_options import render_g_material_options
D=ROOT/"dist"
completed=set()
all_titles=set()
all_body_paragraphs=set()
official_domains=("www.fda.gov","www.cpsc.gov","www.iso.org","www.ftc.gov","www.ista.org","www.eastman.com",
 "food.ec.europa.eu","eur-lex.europa.eu","echa.europa.eu","iccwbo.org","www.uspto.gov")
for batch in (1,2,3):
    data=json.loads((ROOT/f"data/blog-deep-research-part{batch}.json").read_text(encoding="utf8"))
    assert data["schemaVersion"]==1
    for slug,row in data["articles"].items():
        assert slug in GUIDES and slug not in completed and slug not in all_titles
        completed.add(slug)
        assert row["title"] not in all_titles
        all_titles.add(row["title"])
        assert len(row["sections"])>=5 and len(row["sources"])>=2,slug
        for sec in row["sections"]:
            content=sec["paragraph"]
            assert len(content.split())>=120,(slug,sec["heading"])
            assert content not in all_body_paragraphs
            all_body_paragraphs.add(content)
        for s in row["sources"]:
            from urllib.parse import urlparse
            url=urlparse(s["url"])
            assert url.scheme=="https" and url.netloc in official_domains,(slug,s)
        assert render_depth_evidence(slug).count('class="blog-deep-dive__section"')==len(row["sections"])
        # When the operator changed the intro or chose their own article,
        # the generated baseline expansion must not be reinserted.
        baseline=GUIDES[slug]["intro"]
        standard='<p class="blog-lede">'+baseline+'</p>'
        changed='<p class="blog-lede">D1 owner rewrote this introduction after publication.</p>'
        assert 'source-reviewed-deep-dive' in owner_safe_depth("/blog/"+slug+"/",standard)
        assert not owner_safe_depth("/blog/"+slug+"/",changed)
        assert not owner_safe_depth("/blog/"+slug+"/",standard+'<div id="source-reviewed-deep-dive"></div>')
assert len(completed)==15 and len(BLOG_DEPTH)>=16,(len(completed),len(BLOG_DEPTH))
assert set(GUIDES).issuperset(BLOG_DEPTH)
counts={}
for slug in GUIDES:
    page=(D/"blog"/slug/"index.html").read_text(encoding="utf8")
    body=page.split('<main id="main-content">',1)[1].split('</main>',1)[0]
    words=len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*",unescape(re.sub(r"<[^>]*>"," ",body))))
    assert 1800<=words<=2500,(slug,words)
    assert body.count('id="source-reviewed-deep-dive"')==1
    assert body.count('id="buyer-decision-table"')==1
    if slug in completed:
        assert body.count('class="blog-deep-dive__sources"')==1
    counts[slug]=words
g_models=[row for row in SERIES.values() if re.fullmatch(r"G-[0-9]+",str(row["model"]))]
assert len(g_models)>=8
for loc in ("en","es","pt","ru","tr"):
    prefix="" if loc=="en" else loc+"/"
    for row in g_models:
        route="/products/"+row["slug"]+"/"
        page=(D/prefix/route.lstrip("/")/"index.html").read_text(encoding="utf8")
        assert page.count('id="g-series-custom-material-options"')==1,(loc,route)
        assert "Tritan" in page and "PETG" in page and "PP" in page,(loc,route)
        assert render_g_material_options(route,loc,page)=="",(loc,route)
        # Unsupported stock resin, capacity and certifications remain unclaimed.
        if loc=="en":
            assert "does not identify a standard stock resin" in page
assert "id" in render_g_material_options("/products/g-99/","en","")
assert not render_g_material_options("/products/2095/","en","")
print("XUYI_P0_RESEARCH_GUIDES_G_SERIES_PASSED",json.dumps({
 "deepArticles":len(BLOG_DEPTH),"newGuides":len(completed),
 "wordRange":[min(counts.values()),max(counts.values())],
 "Gmodels":len(g_models),"GlocalePages":len(g_models)*5,
 "realSources":sum(len(json.loads((ROOT/f"data/blog-deep-research-part{i}.json").read_text(encoding="utf8"))["articles"][s]["sources"])
     for i in (1,2,3) for s in json.loads((ROOT/f"data/blog-deep-research-part{i}.json").read_text(encoding="utf8"))["articles"])
},sort_keys=True))
