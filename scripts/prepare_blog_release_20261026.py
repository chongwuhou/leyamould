#!/usr/bin/env python3
"""Prepare three reviewed, five-language 2026-10-26 B2B articles as D1 CMS source.
No HTML/dist mutation, no external writes; owner edits stay authoritative.
"""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import scripts.prepare_blog_release_20261020 as base

ROOT=Path(__file__).resolve().parent.parent
DATE="2026-10-26"
base.DATE=DATE  # shared locale renderer must display this batch publication day
OUT=ROOT/"_local_ops"/"blog-batch-20261026"
OUT.mkdir(parents=True,exist_ok=True)
POSTS=json.loads((ROOT/"data/blog-guides-20261026.json").read_text("utf8"))
LOCAL={}
for i,p in enumerate(POSTS):
    copies=json.loads((ROOT/f"data/blog-localized-copy-20261026-{i+1}.json").read_text("utf8"))
    LOCAL[p["slug"]]={loc:{**copy,"product_notes":[(n["label"][loc],n["text"][loc]) for n in p["product_notes"]]} for loc,copy in copies.items()}
MATRICES=json.loads((ROOT/"data/blog-buyer-decision-tables-20261026.json").read_text("utf8"))["articles"]
LANGS=("es","pt","ru","tr")
for day in ("20261021","20261022","20261023","20261024"):
    base.GUIDES.update({p["slug"]:p for p in json.loads((ROOT/f"data/blog-guides-{day}.json").read_text("utf8"))})
    base.MATRICES.update(json.loads((ROOT/f"data/blog-buyer-decision-tables-{day}.json").read_text("utf8"))["articles"])
assert len(POSTS)==3
assert len({p["slug"] for p in POSTS})==3
assert set(LOCAL)==set(MATRICES)=={p["slug"] for p in POSTS}
assert all(p["updated"]==DATE for p in POSTS)

def flatten(copy,model,locale):
    assert len(copy["sections"])==len(model["sections"])==7
    assert len(copy["checklist"])==len(model["checklist"])==10
    assert len(copy["faqs"])==len(model["faqs"])==4
    assert len(copy["product_notes"])==len(model["product_notes"])==3
    result={"title":copy["title"],"description":copy["description"],"intro":copy["intro"]}
    for i,(heading,paragraph) in enumerate(copy["sections"]):
        assert len(heading)>10 and len(paragraph)>230,(model["slug"],locale,i)
        result[f"sections.{i}.heading"]=heading
        result[f"sections.{i}.paragraph"]=paragraph
    for i,value in enumerate(copy["checklist"]):result[f"checklist.{i}"]=value
    for i,(question,answer) in enumerate(copy["faqs"]):
        result[f"faqs.{i}.question"]=question
        result[f"faqs.{i}.answer"]=answer
    matrix=copy["matrix"]
    assert len(matrix["head"])==3 and len(matrix["rows"])==len(model["buyerDecisionTable"]["rows"])==6
    result["matrix.title"]=matrix["title"]
    result["matrix.intro"]=matrix["intro"]
    for i,value in enumerate(matrix["head"]):result[f"matrix.head.{i}"]=value
    for i,row in enumerate(matrix["rows"]):
        assert len(row)==3
        for j,value in enumerate(row):result[f"matrix.rows.{i}.{j}"]=value
    assert len(matrix["links"])==len(model["buyerDecisionTable"]["links"])==2
    for i,value in enumerate(matrix["links"]):result[f"matrix.links.{i}"]=value
    assert len(copy["inline"])==len(model["inline_links"])==2
    for i,value in enumerate(copy["inline"]):result[f"inline.{i}"]=value
    return result

base.GUIDES.update({p["slug"]:p for p in POSTS})
base.MATRICES.update(MATRICES)
base.TRANS.update({p["slug"]:{loc:flatten(LOCAL[p["slug"]][loc],p,loc) for loc in LANGS} for p in POSTS})
def prepare():
    slugs={p["slug"] for p in POSTS}
    assert len(slugs)==3
    assert all(len(p["sections"])==7 and len(p["checklist"])==10 and len(p["faqs"])==4 and len(p["related"])==3 for p in POSTS)
    known=set(base.GUIDES)
    existing_models={str(row["sku"]) for p in POSTS for row in p["product_notes"]}
    assert len(existing_models)>=5,existing_models
    from site_renderer import SERIES
    assert all(any(obj["slug"]==sku for obj in SERIES.values()) for sku in existing_models)
    for p in POSTS:
        assert all(x in known and x != p["slug"] for x in p["related"])
        assert len(set(x["sku"] for x in p["product_notes"]))==3
        assert sorted(x["section"] for x in p["product_notes"])==sorted(set(x["section"] for x in p["product_notes"]))
        for loc in LANGS:
            for note in p["product_notes"]:
                assert note["text"][loc].count("{product}")==1
    posts=[{"slug":p["slug"],"post":p,"publishedAt":DATE+"T00:00:00Z"} for p in POSTS]
    translations=[]
    cards=[]
    for p in POSTS:
        for loc in LANGS:
            body=base.local_main(p,loc)
            assert len(body)>5000,(p["slug"],loc,len(body))
            assert body.count('class="blog-editorial__product-link"')==3
            assert body.count('class="blog-related__item"')==3
            assert body.count('class="blog-buyer-matrix"')==1
            assert body.count('class="blog-section"')==7
            assert body.count("<details>")==4
            assert f'<time datetime="{DATE}">' in body
            assert all(f'href="/{loc}/products/{note["sku"]}/"' in body for note in p["product_notes"])
            assert all(f'href="/{loc}/blog/{slug}/"' in body for slug in p["related"])
            t=base.TRANS[p["slug"]][loc]
            translations.append({"route":"/blog/"+p["slug"]+"/","locale":loc,"title":t["title"],"description":t["description"],"mainHtml":body})
            cards.append({"slug":p["slug"],"locale":loc,"html":base.localized_card(p,loc)})
    assert len(translations)==12 and len(cards)==12
    payload={"posts":posts,"translations":translations,"indexCards":cards}
    (OUT/"payload.json").write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":")),encoding="utf8")
    print("20261026_B2B_CMS_READY",len(posts),"POSTS",len(translations),"TRANSLATIONS",len(cards),"CARDS")
if __name__=="__main__":prepare()