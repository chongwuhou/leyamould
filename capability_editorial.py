"""Source-controlled B2B service guides, grounded in XUYI's plastic bottle scope."""
import json
from site_renderer import ROOT,e,photo,SERIES,SITE_ORIGIN,product_grid
from capability_modules import render_distinct_sections

CAPABILITY_DATA=json.loads((ROOT/"data/capability-guides.json").read_text(encoding="utf-8"))
SERVICE_NAMES={
 "custom-water-bottle":"Custom Water Bottles",
 "custom-molding":"Custom Molding & Tooling",
 "custom-logo":"Custom Logo & Branding",
 "custom-graphics":"Custom Graphics & Colors",
 "custom-manufacturing":"Custom Manufacturing",
 "custom-packaging":"Custom Packaging"
}
BUYING_GUIDES={
 "custom-water-bottle":[("Wholesale Plastic Bottle Buying Guide","wholesale-plastic-water-bottle-buying-guide"),("PC, Tritan, PP & PETG Materials","plastic-bottle-material-selection")],
 "custom-molding":[("OEM vs ODM Plastic Bottle Development","oem-vs-odm-plastic-water-bottles"),("Plastic Bottle Quality Control","water-bottle-quality-control-checklist")],
 "custom-logo":[("Custom Logo Artwork Checklist","custom-logo-water-bottle-checklist"),("Bottle Logo Printing Methods","water-bottle-logo-printing-methods")],
 "custom-graphics":[("Bottle Logo Printing Methods","water-bottle-logo-printing-methods"),("Plastic Bottle Material Comparison","tritan-vs-pp-petg-pc")],
 "custom-manufacturing":[("Plastic Bottle QC Checklist","water-bottle-quality-control-checklist"),("Leakproof Lid Testing","water-bottle-lid-leakproof-testing")],
 "custom-packaging":[("Export Packaging for Custom Bottles","custom-water-bottle-export-packaging"),("MOQ & Wholesale Pricing","custom-water-bottle-moq-pricing")]
}

def render_capability(slug):
 d=CAPABILITY_DATA[slug]
 service=SERVICE_NAMES[slug]
 quote='/contact/?type='+e(slug)+'#inquiry'
 h='<section class="page-intro capability-intro"><div class="shell"><div class="breadcrumb"><a href="/">Home</a> / <a href="/capabilities/">Capabilities</a> / '+e(service)+'</div>'
 h+='<span class="eyebrow">XUYI / '+e(d["kicker"])+'</span><h1>'+e(d["title"])+'</h1><p>'+e(d["lead"])+'</p>'
 h+='<div class="cap-intro__actions"><a class="button" href="'+quote+'">Discuss Your Project →</a><a class="button button--outline" href="/products/">Browse Bottle Models ↗</a></div></div></section>'
 h+='<section class="section cap-intro-image"><div class="shell"><div class="cap-hero">'+photo(d["hero"],d["title"]+" – plastic drinkware selection","eager")+'</div></div></section>'
 h+='<section class="section"><div class="shell"><div class="cap-overview"><div><span class="eyebrow">WHAT THIS SERVICE COVERS</span><h2 class="section__title">From Idea to an Approved Specification</h2></div><p>'+e(d["overview"])+'</p></div></div></section>'
 h+='<section class="section section--soft cap-options"><div class="shell"><div class="section__head"><div><span class="eyebrow">YOUR OPTIONS</span><h2 class="section__title">Choose a Feasible Customization Route</h2><p>Evaluate exact bottle, plastic material and order scope before accepting a final quote.</p></div></div><div class="cap-options__grid">'
 for opt in d["options"]:
  h+='<article class="cap-option"><h3>'+e(opt["name"])+'</h3><p>'+e(opt["fit"])+'</p><div class="cap-option__verify"><strong>What to confirm</strong><span>'+e(opt["verify"])+'</span></div></article>'
 h+='</div></div></section>'
 h+='<section class="section cap-knowledge"><div class="shell"><div class="section__head"><div><span class="eyebrow">BUYER KNOWLEDGE</span><h2 class="section__title">Key Decisions Before Production</h2></div></div>'
 h+='<div class="cap-knowledge__layout"><aside class="cap-knowledge__aside"><div class="cap-knowledge__toc"><span class="eyebrow">IN THIS GUIDE</span><nav aria-label="Service guide sections">'
 for i,item in enumerate(d["sections"]):
  h+='<a href="#'+e(slug)+'-'+str(i+1)+'">'+str(i+1).zfill(2)+' · '+e(item["heading"])+'</a>'
 h+='</nav><a href="'+quote+'">Send an inquiry →</a></div></aside><div class="cap-knowledge__content">'
 for i,item in enumerate(d["sections"]):
  h+='<article class="cap-chapter" id="'+e(slug)+'-'+str(i+1)+'"><span class="cap-chapter__num">'+str(i+1).zfill(2)+'</span>'
  h+='<h2>'+e(item["heading"])+'</h2><p>'+e(item["body"])+'</p><div class="cap-chapter__checks"><strong>Buyer checkpoints</strong><ul>'
  for point in item["checks"]:h+='<li>'+e(point)+'</li>'
  h+='</ul></div></article>'
  if i==1:
   h+='<figure class="cap-detail-figure">'+photo(d["detail"],"Plastic drinkware customization option – "+service)
   h+='<figcaption>Design or manufacturing reference; the actual process is confirmed for the selected model.</figcaption></figure>'
  if i==3 and slug=="custom-water-bottle":
   h+='<figure class="cap-detail-figure">'+photo("/media/capability/gox-kids-custom-bottle.webp?v=20261009","Plastic straw-lid bottle design reference")
   h+='<figcaption>Reference for a children’s straw-lid design. Select the actual XUYI model and confirm component suitability before ordering.</figcaption></figure>'
 h+='</div></div></div></section>'
 h+='<section class="section section--soft cap-process"><div class="shell"><div class="section__head"><div><span class="eyebrow">WORKFLOW</span><h2 class="section__title">Five Steps from Brief to Production</h2><p>Each stage has an approval point, so production does not rely on assumptions.</p></div></div><ol class="cap-process__list">'
 for i,item in enumerate(d["steps"]):
  h+='<li><span>'+str(i+1).zfill(2)+'</span><div><h3>'+e(item["name"])+'</h3><p>'+e(item["detail"])+'</p></div></li>'
 h+='</ol></div></section>'
 h+='<section class="section cap-brief"><div class="shell"><div class="cap-brief__layout"><div><span class="eyebrow">QUOTE CHECKLIST</span><h2 class="section__title">Information to Send with Your RFQ</h2>'
 h+='<p>Providing the correct details helps evaluate materials, prices, MOQ, samples and tooling without premature promises.</p><a href="'+quote+'" class="button">Request Project Quote →</a></div><div class="cap-brief__list"><ul>'
 for item in d["brief"]:h+='<li><span aria-hidden="true">✓</span>'+e(item)+'</li>'
 h+='</ul></div></div></div></section>'
 # Each capability needs useful domain-specific sections, not four generic
 # shared bottom modules (product grid / FAQ / services / buying guides).
 h+=render_distinct_sections(slug,d)
 closing={
  "custom-water-bottle":("Build a Bottle Range Around an Actual SKU","Send capacity, closure, resin preference, target quantity and branding direction.","Discuss Your Bottle Range"),
  "custom-molding":("Validate the Design Before Paying for Tooling","Share part geometry, material targets, tolerance requirements and expected production volume.","Request a Tooling Review"),
  "custom-logo":("Check Your Artwork on a Real Plastic Surface","Send a vector logo, selected bottle SKU, brand colors and proposed print locations.","Request a Logo Feasibility Review"),
  "custom-graphics":("Move from Color Inspiration to an Approved Sample","Send your selected model, color references, transparency target and artwork concept.","Discuss Your Color Sample"),
  "custom-manufacturing":("Set Quality Expectations Before Your Order","Provide the exact model, materials, quantity, acceptance criteria and destination.","Plan Production and Inspection"),
  "custom-packaging":("Get Packaging Costed Against the Finished Bottle","Share the model, retail presentation, dieline or artwork, carton quantities and destination.","Request a Packaging Review")
 }[slug]
 h+='<section class="section cap-end"><div class="shell"><div class="cap-end__body"><div><span class="eyebrow">DISCUSS THE NEXT STEP</span><h2>'+e(closing[0])+'</h2><p>'+e(closing[1])+'</p></div><a class="button" href="'+quote+'">'+e(closing[2])+' →</a></div></div></section>'
 return h

def enrich_capability(doc,slug):
 d=CAPABILITY_DATA[slug];url=SITE_ORIGIN+'/capabilities/'+slug+'/'
 service={"@type":"Service","@id":url+"#service","name":d["title"],"description":d["overview"],"serviceType":SERVICE_NAMES[slug],"provider":{"@type":"Organization","name":"XUYI Bottles","url":SITE_ORIGIN+"/"},"url":url}
 crumbs={"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":SITE_ORIGIN+"/"},{"@type":"ListItem","position":2,"name":"Capabilities","item":SITE_ORIGIN+"/capabilities/"},{"@type":"ListItem","position":3,"name":SERVICE_NAMES[slug],"item":url}]}
 faq={"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q["question"],"acceptedAnswer":{"@type":"Answer","text":q["answer"]}} for q in d["faqs"]]}
 graph={"@context":"https://schema.org","@graph":[service,crumbs,faq]}
 schema='<script type="application/ld+json">'+json.dumps(graph,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+'</script>'
 meta='<meta name="keywords" content="'+e(d["seo"])+'"><meta property="og:image" content="'+e(SITE_ORIGIN+d["hero"])+'">'
 return doc.replace('href="/assets/site.css"','href="/assets/site.css?v=cap-modules-20261009"',1).replace('</head>',meta+schema+'</head>',1)
