#!/usr/bin/env python3
"""P0: real sitemap dates, concise title, SKU-distinct H1 and source-based media ALT."""
from pathlib import Path
from html import unescape
from collections import Counter
import sys,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from site_renderer import SERIES
from product_source_identity import source_product_identity,main_image_alt,matches_owner_field
from sitemap_modification import source_lastmod,BASELINE
from scripts.source_catalog_capacity_oz import new_seo,catalog_volume_numbers,verified_source_material
DIST=ROOT/"dist"
ns="{http://www.sitemaps.org/schemas/sitemap/0.9}"
root=ET.parse(DIST/"sitemap.xml").getroot()
urls=list(root)
assert len(urls)>=755
dates=0
for item in urls:
    url=item.find(ns+"loc").text
    assert url.startswith("https://xuyibottles.com/")
    path=url.removeprefix("https://xuyibottles.com")
    date=item.find(ns+"lastmod")
    expected=source_lastmod(path)
    assert (date.text if date is not None else None)==expected,(path,expected)
    if date is not None:dates+=1
assert dates>=len(urls)-5,(dates,len(urls))
assert source_lastmod("/products/brand-new-model/") is None
assert source_lastmod("/privacy-policy/") is None
assert source_lastmod("/products/2095/")=="2026-10-20"

owners=Counter(row["images"][0] for row in SERIES.values())
seen_langs={}
for loc in ("en","es","pt","ru","tr"):
    path_prefix="" if loc=="en" else loc+"/"
    all_h1=[]
    all_main={}
    for row in SERIES.values():
        slug=row["slug"]
        route=DIST/path_prefix/"products"/slug/"index.html"
        assert route.is_file(),route
        doc=route.read_text(encoding="utf8")
        title=unescape(re.search(r"<title>(.*?)</title>",doc,re.S).group(1))
        # Newly reviewed verified-volume titles are concise. Existing owner
        # D1 titles for unknown-size products may be slightly longer; Google's
        # search title has no hard 60-character cutoff and should not be cut.
        from scripts.source_catalog_capacity_oz import catalog_volume_numbers
        assert len(title)<=(60 if catalog_volume_numbers(row) else 90),(loc,slug,len(title),title)
        h1=re.search(r"<h1[^>]*>(.*?)</h1>",doc,re.S)
        assert h1,(loc,slug,"missing H1")
        heading=unescape(re.sub(r"<[^>]+>"," ",h1.group(1))).strip()
        assert heading,(loc,slug,"empty H1")
        all_h1.append(heading)
        if loc=="en" and row["images"][0]=="/media/gallery/2095-01.webp":
            assert "2095" in heading
        image=re.search(r'<img\\b(?=[^>]*\\bid="main-photo")[^>]*>',doc,re.I)
        if image:
            src=re.search(r'\\bsrc="([^"]+)"',image.group(0))
            alt=re.search(r'\\balt="([^"]*)"',image.group(0))
            if src and alt:
                imgpath=src.group(1)
                description=unescape(alt.group(1))
                assert description,(loc,slug,"empty alt")
                all_main.setdefault(imgpath,set()).add(description)
                if owners.get(imgpath,0)>1 and imgpath in (r["images"][0] for r in SERIES.values()):
                    assert "product photograph" not in description or str(row["model"]) not in description,(loc,slug,description)
        if loc=="en" and slug=="2095":
            # Actual 500ml + reviewed 16.9 oz retail class now take precedence
            # over listing all component resins in the concise search title.
            assert '500ml' in title and "16.9 oz" in title and "2095" in title
            assert "PP/PC" in doc
    assert len(all_h1)==len(set(all_h1)),(loc,len(set(all_h1)),len(all_h1))
    seen_langs[loc]={"products":len(all_h1),"distinctH1":len(set(all_h1))}
assert seen_langs["en"]["products"]>=101
# A later CMS editor can replace both image alt and heading on a known D1
# product without a source fallback changing either of those fields.
row=SERIES["2095"]
custom='<h1>Owner selected product headline</h1><img id="main-photo" src="/media/gallery/2095-01.webp" alt="Owner describes the unique photograph" loading="eager">'
assert source_product_identity(custom,row,"es",owners)==custom
future={**row,"model":"FUTURE-995","slug":"future-model-995","images":["/media/gallery/future-model-995-01.webp"]}
source='<h1>500ml Plastic Sports Water Bottle</h1><img id="main-photo" src="/media/gallery/future-model-995-01.webp" alt="500ml Plastic Sports Water Bottle model FUTURE-995">'
changed=source_product_identity(source,future,"en",Counter({future["images"][0]:1}))
assert "FUTURE-995" in changed and "PP/PC" in changed and changed!=source
print("XUYI_SOURCE_SITEMAP_TITLES_H1_IMAGES_PASSED",dates,len(urls),seen_langs)
