"""Long-form, buyer-centered Why Us pages for plastic drinkware only.

Page content is editorial guidance. The site is not yet publicly indexed; factual
claims about machinery, certification, quantity and lead time require approval.
"""
from site_renderer import e,photo,FAQS
import json

BASE="https://leyamould.com"
RELATED=[
 ("OEM / ODM Support","/capabilities/oem-odm/","How model-based customization and custom development are evaluated"),
 ("Manufacturing Process","/manufacturing/","How specifications, samples, production and packing are coordinated"),
 ("Quality Assurance","/quality-control/","Which tests, records and compliance documents buyers should review"),
 ("Shipping & Logistics","/shipping-logistics/","How packing, Incoterms, documentation and dispatch are planned")
]

def _paragraphs(paragraphs):
 return "".join("<p>"+e(x)+"</p>" for x in paragraphs)
def _heading(eyebrow,title,summary=""):
 return '<div class="why-detail__heading"><span class="eyebrow">'+e(eyebrow)+'</span><h2>'+e(title)+'</h2>'+('<p>'+e(summary)+'</p>' if summary else '')+'</div>'
def _cards(items,css="why-detail__cards"):
 return '<div class="'+css+'">'+''.join('<article class="why-detail__card"><span class="why-detail__number">'+str(i).zfill(2)+'</span><h3>'+e(name)+'</h3><p>'+e(text)+'</p></article>' for i,(name,text) in enumerate(items,1))+'</div>'
def _list_block(items):
 return '<ul class="why-detail__bullets">'+''.join('<li>'+e(x)+'</li>' for x in items)+'</ul>'
def _table(headers,rows,summary):
 return '<div class="why-detail__table-wrap" role="region" aria-label="'+e(summary)+'" tabindex="0"><table class="why-detail__table"><thead><tr>'+''.join('<th scope="col">'+e(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(v)+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def _faqs(arr):
 return '<div class="why-detail__faq">'+''.join('<details><summary>'+e(q)+'</summary><p>'+e(a)+'</p></details>' for q,a in arr)+'</div>'
def render(data):
 slug=data["slug"]
 url='/'+slug+'/' if slug!="capabilities/oem-odm" else '/capabilities/oem-odm/'
 breadcrumb='<nav class="why-detail__crumb" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span><a href="/why-us/">Why Us</a><span>/</span><span>'+e(data["short"])+'</span></nav>'
 html='<div class="why-detail">'+ '<section class="why-detail__hero"><div class="shell">'+breadcrumb+'<div class="why-detail__hero-grid"><div><span class="eyebrow">'+e(data["eyebrow"])+'</span><h1>'+e(data["h1"])+'</h1><p class="why-detail__answer">'+e(data["answer"])+'</p><div class="why-detail__hero-actions"><a class="button" href="/contact/?type='+e(data["inquiry"])+'#inquiry">Discuss Your Project →</a><a class="button button--outline" href="/products/">Explore Plastic Bottles →</a></div><p class="why-detail__micro">Taizhou, Zhejiang, China · B2B plastic drinkware sourcing · Project-specific confirmation</p></div><div class="why-detail__hero-photo">'+photo(data["image"],data["image_alt"],"eager")+'<span>Original XUYI product catalog image · illustrative, not factory photography</span></div></div></div></section>'
 html+='<section class="why-detail__trust"><div class="shell"><div class="why-detail__trust-grid">'+''.join('<div><strong>'+e(t)+'</strong><span>'+e(d)+'</span></div>' for t,d in data["trust"])+'</div></div></section>'
 html+='<section class="why-detail__section"><div class="shell">'+_heading("THE PRACTICAL ANSWER",data["intro_title"],data["intro_summary"])+'<div class="why-detail__reading">'+_paragraphs(data["intro_paragraphs"])+'</div></div></section>'
 html+='<section class="why-detail__section why-detail__section--soft"><div class="shell">'+_heading(data["buyer_label"],data["buyer_title"],data["buyer_summary"])+_cards(data["buyer_cards"])+'</div></section>'
 html+='<section class="why-detail__section"><div class="shell">'+_heading("STEP BY STEP",data["steps_title"],data["steps_summary"])+'<div class="why-detail__steps">'+''.join('<article><span>'+str(i).zfill(2)+'</span><div><h3>'+e(t)+'</h3><p>'+e(desc)+'</p></div></article>' for i,(t,desc) in enumerate(data["steps"],1))+'</div></div></section>'
 html+='<section class="why-detail__section why-detail__section--soft"><div class="shell">'+_heading("BUYER REFERENCE",data["table_title"],data["table_summary"])+_table(data["table_headers"],data["table_rows"],data["table_title"])+'<p class="why-detail__fine">'+e(data["table_note"])+'</p></div></section>'
 html+='<section class="why-detail__section"><div class="shell"><div class="why-detail__columns"><div>'+_heading("BEFORE REQUESTING A QUOTE",data["checklist_title"],data["checklist_intro"])+_list_block(data["checklist"])+'</div><aside class="why-detail__decision"><span class="eyebrow">XUYI BUYER NOTE</span><h3>'+e(data["decision_title"])+'</h3>'+_paragraphs(data["decision_paragraphs"])+'<a href="/request-sample/">Sample request guidance ↗</a></aside></div></div></section>'
 html+='<section class="why-detail__section why-detail__section--faq"><div class="shell">'+_heading("FREQUENTLY ASKED QUESTIONS",data["faq_title"],data["faq_summary"])+_faqs(data["faqs"])+'</div></section>'
 html+='<section class="why-detail__section"><div class="shell">'+_heading("CONTINUE EXPLORING","Choose the Right Bottle & Supporting Service","Explore available models and practical buyer resources before requesting a tailored quotation.")+'<div class="why-detail__related-products">'+''.join('<a href="'+e(link)+'"><span>'+e(title)+'</span><strong>Explore collection ↗</strong></a>' for title,link in [("Plastic Sports Water Bottles","/collections/sports-water-bottles/"),("Kids Plastic Water Bottles","/collections/kids-water-bottles/"),("Large Capacity Water Jugs","/collections/large-capacity-water-jugs/"),("Protein Shaker Bottles","/collections/plastic-shaker-bottles/")])+'</div><div class="why-detail__related">'+''.join('<a href="'+uri+'"'+(' aria-current="page"' if uri==url else '')+'><strong>'+e(t)+'</strong><span>'+e(d)+'</span></a>' for t,uri,d in RELATED)+'</div></div></section>'
 html+='<section class="why-detail__end"><div class="shell"><span class="eyebrow">TELL US WHAT YOU NEED</span><h2>'+e(data["cta_title"])+'</h2><p>'+e(data["cta_paragraph"])+'</p><a class="button button--round" href="/contact/?type='+e(data["inquiry"])+'#inquiry">Prepare Your Enquiry →</a><p class="why-detail__fine">The preview enquiry form is currently disabled until approved company contact details and secure message delivery are available.</p></div></section></div>'
 return html

def schema_enhance(html, data):
 # JSON-LD mirrors on-page answers; it does not promise Google FAQ rich results.
 path='/'+data["slug"]+'/'
 url=BASE+path
 entity={"@context":"https://schema.org","@graph":[
  {"@type":"Organization","@id":BASE+"/#organization","name":"台州市旭一家居用品有限公司","alternateName":"XUYI Bottles","url":BASE+"/","address":{"@type":"PostalAddress","addressLocality":"Taizhou","addressRegion":"Zhejiang","addressCountry":"CN"}},
  {"@type":"WebPage","@id":url+"#webpage","url":url,"name":data["seo_title"],"description":data["description"],"inLanguage":"en","about":{"@id":BASE+"/#organization"},"isPartOf":{"@type":"WebSite","name":"XUYI Bottles","url":BASE+"/"}},
  {"@type":"BreadcrumbList","@id":url+"#breadcrumb","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":BASE+"/"},{"@type":"ListItem","position":2,"name":"Why Us","item":BASE+"/why-us/"},{"@type":"ListItem","position":3,"name":data["short"],"item":url}]},
  {"@type":"FAQPage","@id":url+"#faq","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in data["faqs"]]}
 ]}
 script='<script type="application/ld+json">'+json.dumps(entity,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')+'</script>'
 extras='<link rel="stylesheet" href="/assets/why-us-v2.css"><meta name="author" content="XUYI Bottles"><meta property="og:type" content="website"><meta property="og:title" content="'+e(data["seo_title"])+'"><meta property="og:description" content="'+e(data["description"])+'"><meta property="og:url" content="'+e(url)+'">'+script
 return html.replace('</head>',extras+'</head>',1)
