#!/usr/bin/env python3
"""Source-of-truth acceptance: shaker wholesale landing depth + 16 FAQ rewrites.

Does not mutate dist/ or D1. D1 owner edits must replace fallback source bodies.
"""
import json
import re
import sys
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from site_renderer import SERIES
from shaker_category_editorial import SECTIONS, LINKS
from resource_pages import DATA, faq_page, schema_add
import build
import site_renderer as site

class Text(HTMLParser):
    def __init__(self):
        super().__init__();self.words=[]
    def handle_data(self,data):
        self.words.append(data)

def word_count(text):
    parser=Text();parser.feed(text)
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?"," ".join(parser.words)))

def answer_words(text):
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?",text))

REVIEWED_16={
 "Is this website able to receive a live inquiry right now?",
 "How long does delivery to the United States or Europe take?",
 "How can a distributor avoid mixing model revisions in warehouse stock?",
 "Can my design files be treated as confidential?",
 "What happens if the prototype does not meet our requirements?",
 "Why can shipping cost be high for an empty large-capacity jug?",
 "Can a plastic bottle be used for boiling water or hot drinks?",
 "Does a custom water bottle require a new mold?",
 "Can I send a competitor-style reference bottle or design sketch?",
 "Can I appoint a third-party inspector?",
 "What shipping documents should accompany a bulk order?",
 "Can I reorder the same printed bottle design later?",
 "Can we source sports bottles, kids bottles, jugs and shakers together?",
 "What is the difference between a stock sample and a pre-production sample?",
 "What quality checks matter most for plastic drinking bottles?",
 "How are express, air freight and sea freight different?",
}
assert len(REVIEWED_16)==16
faq={q:(a,url) for c in DATA["categories"] for q,a,url in c["questions"]}
assert len(faq)>=54
for question in REVIEWED_16:
    assert question in faq,("missing FAQ",question)
    size=answer_words(faq[question][0])
    assert 40<=size<=65,(question,size)
assert len(SECTIONS)>=3 and all(len(x["items"])==3 for x in SECTIONS)
assert {x["slug"] for x in SERIES.values() if x["category"]=="Plastic Shaker Bottles"}
actual=build.catalog("Plastic Shaker Bottles")
assert word_count(actual)>=900,("Shaker landing still thin",word_count(actual))
for section in SECTIONS:
    assert '<h2 class="section__title">'+section["title"]+"</h2>" in actual
for url,label in LINKS:
    assert 'href="'+url+'"' in actual,(url,"missing contextual source link")
    if url.startswith("/products/"):
        slug=url.split("/")[2]
        assert any(x["slug"]==slug and x["category"]=="Plastic Shaker Bottles" for x in SERIES.values())
assert "Compare Protein Shaker Bottle Models Before Requesting Bulk Pricing" not in build.catalog("Plastic Sports Water Bottles")
faq_source=faq_page()
for question in REVIEWED_16:
    assert faq_source.count(question)==1
    assert unescape(faq[question][0]) in unescape(faq_source)
faq_document=schema_add("<html><head></head><body></body></html>","faq","FAQ procurement answers",DATA["categories"])
assert '"@type":"FAQPage"' in faq_document
for question in REVIEWED_16:
    assert json.dumps(faq[question][0],ensure_ascii=False)[1:-1] in faq_document

# Emulate a later D1/CMS editor replacing the English body, rather than
# letting an old shaker source module or old FAQ dataset override their text.
source_write=site.write
original=dict(site.BODY_OVERRIDES)
captured={}
try:
    site.write=lambda path,html:captured.__setitem__(path,html)
    for route in ("/collections/plastic-shaker-bottles/","/faq/"):
        owner='<section class="cms-approved"><h1>Edited in D1</h1><p>'+(
              "A site owner replaced the page with approved material, including "
              "new sales terms and precise product facts, which must survive "
              "any future complete source rebuild without old editorial copying."
              )+'</p></section>'
        site.BODY_OVERRIDES[route]=owner
        shell='<html><head><title>CMS page</title></head><body><main id="main-content">'+(
            actual if route.startswith("/collections/") else faq_source
        )+'</main></body></html>'
        path=route.lstrip("/")+"index.html"
        site.build_url(path,"CMS page",shell)
        html=captured[path]
        assert owner in html,(route,"CMS owner body lost")
        assert "Compare Protein Shaker Bottle Models Before Requesting Bulk Pricing" not in html,(route,"shaker source overwrote D1")
        if route=="/faq/":
            assert "How long does delivery to the United States or Europe take?" not in html
finally:
    site.write=source_write
    site.BODY_OVERRIDES.clear()
    site.BODY_OVERRIDES.update(original)

if (ROOT/"dist/collections/plastic-shaker-bottles/index.html").is_file():
    release=(ROOT/"dist/collections/plastic-shaker-bottles/index.html").read_text(encoding="utf8")
    main=release.split('<main id="main-content">',1)[1].split('</main>',1)[0]
    assert word_count(main)>=900
    assert "Compare Protein Shaker Bottle Models Before Requesting Bulk Pricing" in main
if (ROOT/"dist/faq/index.html").is_file():
    release=(ROOT/"dist/faq/index.html").read_text(encoding="utf8")
    for question in REVIEWED_16:
        assert question in release
        assert unescape(faq[question][0]) in unescape(release)
print("XUYI_SHAKER_900_WORDS_AND_16_FAQ_40_TO_65_WORDS_CMS_OWNER_FIRST_PASSED",
      "shaker_source_words",word_count(actual),"updated_answers",len(REVIEWED_16))