#!/usr/bin/env python3
"""Prepare the three 2026-11-07 XUYI Blog articles and all four reviewed locale variants.

The output is an offline CMS schedule payload. It does not publish or mutate dist.
"""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import scripts.prepare_blog_release_20261020 as base

ROOT=Path(__file__).resolve().parent.parent
DATE="2026-11-07"
base.DATE=DATE
OUT=ROOT/"_local_ops"/"blog-batch-20261107"
OUT.mkdir(parents=True,exist_ok=True)
POSTS=[json.loads((ROOT/f"data/blog-guides-20261107-{i}.json").read_text(encoding="utf-8")) for i in (1,2,3)]
LOCAL=[json.loads((ROOT/f"data/blog-localized-copy-20261107-{i}.json").read_text(encoding="utf-8")) for i in (1,2,3)]
LANGS=("es","pt","ru","tr")
assert len(POSTS)==3 and len({p["slug"] for p in POSTS})==3
assert len(LOCAL)==3

# Add approved earlier articles so the localized related cards can use their
# reviewed titles/descriptions from the build snapshot when available.
for day in ("20261021","20261022","20261023","20261024","20261025","20261026","20261027","20261028","20261029","20261030","20261031","20261101","20261102","20261103"):
    for path in sorted(list((ROOT/"data").glob(f"blog-guides-{day}*.json"))+list((ROOT/"data").glob(f"blog-scheduled-{day}*.json"))):
        loaded=json.loads(path.read_text(encoding="utf-8"))
        rows=loaded if isinstance(loaded,list) else loaded.get("articles",loaded.get("guides",[])) if isinstance(loaded,dict) and not loaded.get("slug") else [loaded]
        for prior in rows:
            if isinstance(prior,dict) and prior.get("slug"):
                base.GUIDES[prior["slug"]]=prior
for p in POSTS:
    base.GUIDES[p["slug"]]=p
    base.MATRICES[p["slug"]]=p["buyerDecisionTable"]

def flatten(copy,post,locale):
    assert len(copy["sections"])==len(post["sections"])==7
    assert len(copy["checklist"])==len(post["checklist"])==10
    assert len(copy["faqs"])==len(post["faqs"])==4
    assert len(post["product_notes"])==3
    assert len(copy["inline"])==len(post["inline_links"])==2
    assert len(copy["matrix"]["head"])==3
    assert len(copy["matrix"]["rows"])==len(post["buyerDecisionTable"]["rows"])==6
    assert len(copy["matrix"]["links"])==len(post["buyerDecisionTable"]["links"])==2
    assert len(copy["coverAlt"])>=40
    result={"title":copy["title"],"description":copy["description"],"intro":copy["intro"],"coverAlt":copy["coverAlt"]}
    for i,(heading,paragraph) in enumerate(copy["sections"]):
        assert len(heading)>10 and len(paragraph)>230,(post["slug"],locale,i,len(paragraph))
        result[f"sections.{i}.heading"]=heading
        result[f"sections.{i}.paragraph"]=paragraph
    for i,value in enumerate(copy["checklist"]):result[f"checklist.{i}"]=value
    for i,(question,answer) in enumerate(copy["faqs"]):
        assert len(question)>12 and len(answer)>80
        result[f"faqs.{i}.question"]=question
        result[f"faqs.{i}.answer"]=answer
    matrix=copy["matrix"]
    assert len(matrix["rows"])==6 and all(len(row)==3 for row in matrix["rows"])
    result["matrix.title"]=matrix["title"]
    result["matrix.intro"]=matrix["intro"]
    for i,value in enumerate(matrix["head"]):result[f"matrix.head.{i}"]=value
    for i,row in enumerate(matrix["rows"]):
        for j,value in enumerate(row):result[f"matrix.rows.{i}.{j}"]=value
    for i,value in enumerate(matrix["links"]):
        result[f"matrix.links.{i}"]=value[0] if isinstance(value,list) else value
    for i,value in enumerate(copy["inline"]):result[f"inline.{i}"]=value
    return result

TRANS={}
for post,copies in zip(POSTS,LOCAL):
    slug=post["slug"]
    assert set(copies)==set(LANGS),(slug,set(copies))
    assert post["updated"]==DATE
    assert len(post["sections"])==7 and len(post["checklist"])==10 and len(post["faqs"])==4 and len(post["related"])==3
    assert len(set(post["related"]))==3 and slug not in post["related"]
    assert len(post["product_notes"])==3 and len({n["sku"] for n in post["product_notes"]})==3
    assert len({n["section"] for n in post["product_notes"]})==3 and all(0<=n["section"]<7 for n in post["product_notes"])
    assert len(post["inline_links"])==2
    assert len(post["buyerDecisionTable"]["head"])==3 and len(post["buyerDecisionTable"]["rows"])==6
    assert len(post["buyerDecisionTable"]["links"])==2
    for loc in LANGS:
        for note in post["product_notes"]:
            assert note["text"][loc].count("{product}")==1
            assert len(note["label"][loc])>=3
        TRANS.setdefault(slug,{})[loc]=flatten(copies[loc],post,loc)

base.TRANS.update(TRANS)
from site_renderer import SERIES
from PIL import Image
digests=set()
for post in POSTS:
    models={str(x["sku"]) for x in post["product_notes"]}
    assert len(models)==3 and all(any(obj["slug"]==sku for obj in SERIES.values()) for sku in models),models
    cover=ROOT/"assets"/"blog"/post["cover"].split("/")[-1]
    assert cover.is_file() and cover.stat().st_size>30000,(post["slug"],cover)
    with Image.open(cover) as im:
        assert im.format=="WEBP" and im.size==(1200,800),(post["slug"],im.format,im.size)
    digests.add(hashlib.sha256(cover.read_bytes()).hexdigest())
    assert all(slug in base.GUIDES and slug!=post["slug"] for slug in post["related"])
assert len(digests)==3,"Each article requires its own distinct approved cover."

translations=[]
cards=[]
for post in POSTS:
    slug=post["slug"]
    for loc in LANGS:
        body=base.local_main(post,loc)
        assert len(body)>5000,(slug,loc,len(body))
        assert 'src="'+post["cover"]+'"' in body,(slug,loc,"hero cover")
        assert 'alt="'+TRANS[slug][loc]["coverAlt"]+'"' in body,(slug,loc,"translated hero alt")
        assert body.count('class="blog-editorial__product-link"')==3,(slug,loc,"model links")
        assert body.count('class="blog-related__item"')==3,(slug,loc,"related links")
        assert body.count('class="blog-buyer-matrix"')==1,(slug,loc,"buyer matrix")
        assert body.count('class="blog-section"')==7,(slug,loc,"sections")
        assert body.count("<details>")==4,(slug,loc,"FAQs")
        assert f'<time datetime="{DATE}">' in body,(slug,loc,"publication date")
        for note in post["product_notes"]:
            assert f'href="/{loc}/products/{note["sku"]}/"' in body,(slug,loc,note["sku"])
        for related in post["related"]:
            assert f'href="/{loc}/blog/{related}/"' in body,(slug,loc,related)
        copy=LOCAL[POSTS.index(post)][loc]
        translations.append({"slug":slug,"route":"/blog/"+slug+"/","locale":loc,"title":copy["title"],"description":copy["description"],"mainHtml":body})
        card=base.localized_card(post,loc)
        assert 'src="'+post["cover"]+'"' in card
        assert 'alt="'+copy["coverAlt"]+'"' in card
        assert 'href="/blog/'+slug+'/"' in card
        cards.append({"slug":slug,"locale":loc,"html":card})

assert len(translations)==12 and len(cards)==12
payload={"posts":[{"slug":p["slug"],"post":p,"publishedAt":DATE+"T00:00:00Z"} for p in POSTS],
         "translations":translations,"indexCards":cards}
target=OUT/"payload.json"
target.write_text(json.dumps(payload,ensure_ascii=True,separators=(",",":")),encoding="utf-8")
print("XUYI_20261107_FIVE_LANGUAGE_PAYLOAD_READY",
      "posts",len(POSTS),"translations",len(translations),"index_cards",len(cards),
      "bytes",target.stat().st_size)