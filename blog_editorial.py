"""XUYI editorial page rendering. Article copy lives in data/blog-guides.json."""
import json
import re
from site_renderer import ROOT, e, photo, intro, SITE_ORIGIN

GUIDES = {post["slug"]: post for post in json.loads((ROOT / "data/blog-guides.json").read_text(encoding="utf-8"))}
EVIDENCE=json.loads((ROOT / "data/editorial-evidence.json").read_text(encoding="utf-8"))
assert set(EVIDENCE).issubset(GUIDES)
LEGACY_GUIDES = {
    "wholesale-plastic-water-bottle-buying-guide",
    "plastic-bottle-material-selection",
    "custom-logo-water-bottle-checklist",
    "sports-bottle-vs-water-jug",
    "kids-water-bottle-procurement",
    "shaker-bottle-wholesale"
}

CONTEXT_LINKS = {
    "wholesale-plastic-water-bottle-buying-guide": [("Browse all bottle models", "/products/"), ("OEM/ODM services", "/capabilities/oem-odm/")],
    "plastic-bottle-material-selection": [("Browse plastic bottle models", "/products/"), ("Quality control approach", "/quality-control/")],
    "custom-logo-water-bottle-checklist": [("Custom logo service", "/capabilities/custom-logo/"), ("Custom packaging", "/capabilities/custom-packaging/")],
    "sports-bottle-vs-water-jug": [("Sports bottles", "/collections/sports-water-bottles/"), ("Large water jugs", "/collections/large-capacity-water-jugs/")],
    "kids-water-bottle-procurement": [("Kids bottles", "/collections/kids-water-bottles/"), ("Request samples", "/request-sample/")],
    "shaker-bottle-wholesale": [("Protein shaker bottles", "/collections/plastic-shaker-bottles/"), ("Custom logo options", "/capabilities/custom-logo/")],
    "tritan-vs-pp-petg-pc": [("Plastic bottle range", "/products/"), ("Quality requirements", "/quality-control/")],
    "bpa-free-plastic-water-bottle-sourcing": [("Plastic bottle range", "/products/"), ("Quality control", "/quality-control/")],
    "water-bottle-lid-leakproof-testing": [("Bottle feature range", "/features/flip-top/"), ("Quality control", "/quality-control/")],
    "custom-water-bottle-moq-pricing": [("Wholesale bottle models", "/products/"), ("Custom packaging", "/capabilities/custom-packaging/")],
    "oem-vs-odm-plastic-water-bottles": [("OEM & ODM", "/capabilities/oem-odm/"), ("Request a sample", "/request-sample/")],
    "water-bottle-quality-control-checklist": [("Quality control", "/quality-control/"), ("Sample approval", "/request-sample/")],
    "custom-water-bottle-export-packaging": [("Shipping and logistics", "/shipping-logistics/"), ("Custom packaging", "/capabilities/custom-packaging/")],
    "how-to-start-private-label-water-bottle-brand": [("All product models", "/products/"), ("OEM and ODM service", "/capabilities/oem-odm/")],
    "water-bottle-logo-printing-methods": [("Custom logo service", "/capabilities/custom-logo/"), ("Request a sample", "/request-sample/")],
    "sports-water-bottle-customization": [("Sports bottle collection", "/collections/sports-water-bottles/"), ("Custom bottle service", "/capabilities/custom-water-bottle/")]
}

def cover_path(slug):
    return "/media/ppt/" + GUIDES[slug]["cover"]

def anchor(heading):
    return re.sub(r"[^a-z0-9-]+", "-", heading.lower().replace("’", "").replace("'", "")).strip("-")[:90]

def render_primary_evidence(slug):
    evidence=EVIDENCE.get(slug)
    if not evidence:return ""
    h='<section class="blog-evidence" id="primary-sources" aria-labelledby="primary-sources-heading"><span class="eyebrow">SOURCE-CHECKED BUYER NOTES</span><h2 id="primary-sources-heading">'+e(evidence["title"])+'</h2>'
    h+='<p>'+e(evidence["insight"])+'</p><p><strong>Practical next step:</strong> '+e(evidence["next_step"])+'</p>'
    h+='<h3>Primary references</h3><ul>'
    for source in evidence["sources"]:
        assert source["url"].startswith(("https://www.fda.gov/","https://eur-lex.europa.eu/","https://www.iso.org/"))
        h+='<li><a href="'+e(source["url"])+'" target="_blank" rel="noopener noreferrer">'+e(source["label"])+' ↗</a></li>'
    h+='</ul><p class="blog-evidence__caveat">External regulations and standards are independent references, not product certification or proof of testing by XUYI. Confirm applicability and the latest rules for the exact product, destination and transaction date.</p></section>'
    return h

def render_article(slug):
    post=GUIDES[slug]
    related=[GUIDES[s] for s in post["related"]]
    h=intro("Blog / Buying Guide",post["title"],post["description"])
    h+='<section class="section blog-editorial"><div class="shell">'
    h+='<div class="blog-detail__cover">'+photo(cover_path(slug),post["title"]+" | XUYI plastic drinkware buyer guide")+'</div>'
    h+='<div class="blog-editorial__layout"><aside class="blog-editorial__aside"><div class="blog-toc"><span class="eyebrow">IN THIS GUIDE</span><nav aria-label="Article sections">'
    for item in post["sections"]:
        h+='<a href="#'+anchor(item["heading"])+'">'+e(item["heading"])+'</a>'
    h+='</nav><a class="blog-toc__quote" href="/contact/#inquiry">Discuss your project →</a></div></aside>'
    updated="2026-10-10" if slug in EVIDENCE else post["updated"]
    h+='<article class="article blog-editorial__body"><div class="blog-meta"><span>BUYER RESOURCES</span><span>Updated '+e(updated)+'</span></div>'
    h+='<p class="blog-lede">'+e(post["intro"])+'</p>'
    h+='<div class="blog-takeaway"><strong>Before requesting a quote</strong><ul>'
    for tip in post["checklist"][:3]:h+='<li>'+e(tip)+'</li>'
    h+='</ul></div>'
    for section in post["sections"]:
        h+='<section class="blog-section" id="'+anchor(section["heading"])+'"><h2>'+e(section["heading"])+'</h2><p>'+e(section["paragraph"])+'</p></section>'
    h+=render_primary_evidence(slug)
    h+='<section class="blog-checklist"><h2>Buyer checklist</h2><p>Use these points when comparing a factory sample, artwork approval and purchase quotation.</p><ul>'
    for tip in post["checklist"]:h+='<li>'+e(tip)+'</li>'
    h+='</ul></section><section class="blog-faq"><h2>Frequently asked questions</h2>'
    for qa in post["faqs"]:
        h+='<details><summary>'+e(qa["question"])+'</summary><p>'+e(qa["answer"])+'</p></details>'
    h+='</section><div class="blog-context-links"><h2>Explore XUYI products and services</h2>'
    for name,href in CONTEXT_LINKS.get(slug,[]):
        h+='<a href="'+e(href)+'">'+e(name)+' →</a>'
    h+='</div><div class="blog-editorial__cta"><h2>Need a quote for a specific model?</h2>'
    h+='<p>Send the intended model, material requirements, expected order quantity, artwork and destination market. We will review the options for that exact product rather than assume one specification fits every bottle.</p>'
    h+='<a class="button" href="/contact/#inquiry">Request a Plastic Bottle Quote →</a></div>'
    h+='</article></div></div></section>'
    h+='<section class="section section--soft blog-related"><div class="shell"><div class="section__head"><div><span class="eyebrow">CONTINUE READING</span><h2 class="section__title">Related Buying Guides</h2></div></div>'
    h+='<div class="blog-related__grid">'
    for item in related:
        h+='<article class="blog-related__item"><a href="/blog/'+e(item["slug"])+'/">'+photo(cover_path(item["slug"]),item["title"])+'<strong>'+e(item["title"])+'</strong></a><p>'+e(item["description"])+'</p></article>'
    h+='</div><p class="blog-related__all"><a href="/blog/">View all XUYI buyer guides →</a></p></div></section>'
    return h

def enrich_article_html(document, slug):
    post=GUIDES[slug]
    updated="2026-10-10" if slug in EVIDENCE else post["updated"]
    url=SITE_ORIGIN+"/blog/"+slug+"/"
    breadcrumb={"@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":1,"name":"Home","item":SITE_ORIGIN+"/"},
      {"@type":"ListItem","position":2,"name":"Blog","item":SITE_ORIGIN+"/blog/"},
      {"@type":"ListItem","position":3,"name":post["title"],"item":url}]}
    blogpost={"@type":"BlogPosting","@id":url+"#article","headline":post["title"],
      "description":post["description"],"mainEntityOfPage":{"@type":"WebPage","@id":url},
      "image":[SITE_ORIGIN+cover_path(slug)],
      "dateModified":updated,"inLanguage":"en","keywords":", ".join([post["primary_keyword"]]+post["secondary_keywords"]),
      "author":{"@type":"Organization","name":"XUYI Bottles","url":SITE_ORIGIN+"/"},
      "publisher":{"@type":"Organization","name":"XUYI Bottles","url":SITE_ORIGIN+"/"}}
    if slug in EVIDENCE:
        blogpost["citation"]=[{"@type":"CreativeWork","name":ref["label"],"url":ref["url"]} for ref in EVIDENCE[slug]["sources"]]
    if slug not in LEGACY_GUIDES:
        blogpost["datePublished"]=post["updated"]
    faq={"@type":"FAQPage","mainEntity":[{"@type":"Question","name":qa["question"],"acceptedAnswer":{"@type":"Answer","text":qa["answer"]}} for qa in post["faqs"]]}
    graph={"@context":"https://schema.org","@graph":[blogpost,breadcrumb,faq]}
    metadata='<meta property="og:type" content="article"><meta property="article:modified_time" content="'+e(updated)+'">'
    metadata+='<meta name="keywords" content="'+e(", ".join([post["primary_keyword"]]+post["secondary_keywords"]))+'">'
    metadata+='<meta property="og:image" content="'+e(SITE_ORIGIN+cover_path(slug))+'">'
    metadata+='<script type="application/ld+json">'+json.dumps(graph,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+'</script>'
    return document.replace("</head>",metadata+"</head>",1)