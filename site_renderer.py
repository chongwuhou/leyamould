from pathlib import Path
import json,html,re,collections
ROOT=Path(__file__).parent
RAW=json.loads((ROOT/"data/products.json").read_text(encoding="utf-8"))
IMAGES=json.loads((ROOT/"data/excel-images.json").read_text(encoding="utf-8"))
CAT={
"Plastic Sports Water Bottles":("Sports Water Bottles","sports-water-bottles","/media/ppt/slide-059.webp","Lightweight reusable plastic bottles for daily hydration and active lifestyles."),
"Large Capacity Water Jugs":("Large Capacity Water Jugs","large-capacity-water-jugs","/media/ppt/slide-055.webp","Carry-friendly larger volume plastic water bottles for fitness, outdoor and everyday use."),
"Kids Plastic Water Bottles":("Kids Water Bottles","kids-water-bottles","/media/ppt/slide-030.webp","Colorful children's plastic straw and carrying-strap bottle designs."),
"Plastic Shaker Bottles":("Protein Shaker Bottles","plastic-shaker-bottles","/media/ppt/slide-094.webp","Plastic shaker cups for gym, fitness and sports nutrition buyers.")
}
SERIES=collections.OrderedDict()
for i,p in enumerate(RAW):
 key=p["model"]
 if key not in SERIES:SERIES[key]={**p,"variants":[],"images":[]}
 obj=SERIES[key];obj["variants"].append(p)
 if i<76:
  media=IMAGES.get(str(i+3))
  if media and media['sku']==key:obj["images"].append("/media/excel/row-%03d.webp"%(i+3))
for model,slide in [('501',91),('502',92),('507',93),('509',94),('510',95),('5247',96),('5248',96)]:
 if model in SERIES:SERIES[model]["images"].append("/media/ppt/slide-%03d.webp"%slide)
for m,item in SERIES.items():item["images"]=list(dict.fromkeys(item["images"]))
assert len(SERIES)==79,(len(SERIES))
assert all(v["images"] for v in SERIES.values()),[(k,v["images"]) for k,v in SERIES.items() if not v["images"]]
def e(v):return html.escape(str(v or ""),quote=True)
def photo(src,alt,loading='lazy'):return f'<img src="{e(src)}" alt="{e(alt)}" loading="{loading}" decoding="async">'
def write(path,content):
 out=ROOT/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(content,encoding="utf-8")
URLS={}
def build_url(path,title,content):
 URLS[path]=title
 write(path,content)
ICONS={
"search":'<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m16 16 5 5"/></svg>',
"menu":'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg>',
"mail":'<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
"phone":'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3h5l1 5-2 2a15 15 0 0 0 4 4l2-2 5 1v5l-2 3C9 19 5 15 3 6z"/></svg>',
"top":'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 14 7-7 7 7"/></svg>',
"chevron":'<svg class="chevron" viewBox="0 0 24 24" aria-hidden="true"><path d="m5 9 7 7 7-7"/></svg>'
}
def category_links():
 return [(v[0],"/collections/"+v[1]+"/") for v in CAT.values()]
DROPS={
"Products":[("Categories",category_links()),("Find Bottles",[("All Plastic Drinkware","/products/"),("Sports Water Bottles","/collections/sports-water-bottles/"),("Kids Water Bottles","/collections/kids-water-bottles/")]),("Bulk Purchasing",[("Large Capacity Jugs","/collections/large-capacity-water-jugs/"),("Shaker Bottles","/collections/plastic-shaker-bottles/"),("Wholesale Buying FAQ","/faq/")])],
"Capabilities":[("Custom Branding",[("Custom Logo Printing","/capabilities/custom-logo/"),("Colors & Graphics","/capabilities/custom-graphics/")]),("Manufacturing",[("OEM / ODM Service","/capabilities/oem-odm/"),("Custom Manufacturing","/capabilities/custom-manufacturing/"),("Custom Packaging","/capabilities/custom-packaging/")]),("Buyer Services",[("Wholesale Quote","/contact/?type=wholesale#inquiry"),("Request Samples","/contact/?type=sample#inquiry"),("Buying FAQs","/faq/")])],
"About":[("XUYI Company",[("About XUYI","/about/"),("Our Factory","/manufacturing/"),("Quality Control","/quality-control/")]),("How We Work",[("Manufacturing Process","/manufacturing/"),("Shipping & Logistics","/shipping-logistics/")]),("Resources",[("FAQs","/faq/"),("Buying Guides","/blog/"),("Contact","/contact/")])]
}
def header():
 navitems=[]
 for name in ["Home","Products","Capabilities","About","Blog","Contact Us"]:
  if name not in DROPS:
   uri={"/Home":"/"}.get(name,{"Home":"/","Blog":"/blog/","Contact Us":"/contact/"}[name])
   navitems.append(f'<a class="nav__link" href="{uri}">{name}</a>')
   continue
  cols=DROPS[name]
  colhtml=''.join('<div class="mega__column"><strong>'+e(group)+'</strong>'+''.join(f'<a href="{e(uri)}">{e(label)}</a>' for label,uri in links)+'</div>' for group,links in cols)
  if name=="Products":colhtml+='<div class="mega__column">'+photo("/media/ppt/slide-059.webp","Plastic bottle collection image")+'<strong>Find your bottle</strong><a href="/products/">Browse all models →</a></div>'
  else:colhtml+='<div class="mega__column">'+photo("/media/ppt/slide-049.webp","XUYI catalog product photo")+'<strong>Wholesale inquiries</strong><a href="/contact/">Contact our team →</a></div>'
  navitems.append(f'<div class="nav__drop"><button class="nav__toggle" type="button" data-mega-toggle aria-expanded="false">{name}{ICONS["chevron"]}</button><div class="mega"><div class="shell mega__grid">{colhtml}</div></div></div>')
 mob='<a href="/">Home</a>'
 for name in ("Products","Capabilities","About"):
  mob+=f'<details><summary>{name}</summary>'
  for title,ls in DROPS[name]:
   mob+=''.join(f'<a href="{e(uri)}">{e(label)}</a>' for label,uri in ls)
  mob+='</details>'
 mob+='<a href="/blog/">Blog</a><a href="/faq/">FAQ</a><a href="/contact/">Contact Us</a><a href="/contact/#inquiry">Instant Quote →</a>'
 return '<div class="topbar"><div class="shell topbar__inner"><a href="/about/">Taizhou, China · Plastic Drinkware Manufacturer</a><a href="/contact/">Contact us →</a></div></div><header class="header"><div class="shell header__inner"><a href="/" class="logo" aria-label="XUYI Drinkware home">XUYI<small>PLASTIC DRINKWARE</small></a><nav class="nav" aria-label="Main navigation">'+''.join(navitems)+'</nav><div class="header__actions"><span class="language-label" title="English is the only published locale">EN</span><button class="icon-button" id="search-toggle" aria-label="Toggle product search" aria-expanded="false" type="button">'+ICONS["search"]+'</button><a class="button" href="/contact/#inquiry">Instant Quote →</a><button class="icon-button menu-button" id="mobile-menu" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-navigation" type="button">'+ICONS["menu"]+'</button></div></div><div id="search-panel" class="search-panel"><form class="shell search-panel__form" action="/products/" method="get"><input type="search" name="q" aria-label="Search product models" placeholder="Search by model, bottle type or capacity"><button class="button" type="submit">Search →</button></form></div><nav class="mobile-nav" id="mobile-navigation" aria-label="Mobile navigation">'+mob+'</nav></header>'
def footer():
 links=''.join('<p><a href="'+uri+'">'+e(label)+'</a></p>' for label,uri in category_links())
 return '<section class="cta-panel"><div class="shell"><span class="eyebrow">Wholesale & Custom Branding</span><h2>Ready to Build Your Bottle Collection?</h2><p>Share your model numbers, estimated quantity, colors, artwork and destination country.</p><a href="/contact/#inquiry" class="button button--round">Get an Instant Quote →</a></div></section><footer class="footer"><div class="shell"><div class="footer__cols"><div><a class="logo" href="/">XUYI<small>PLASTIC DRINKWARE</small></a><p>Factory-backed plastic water bottles for wholesale, branding and OEM/ODM projects.</p><p>Taizhou, Zhejiang, China</p></div><div><h3>Products</h3>'+links+'</div><div><h3>Capabilities</h3><p><a href="/capabilities/custom-logo/">Custom Logo</a></p><p><a href="/capabilities/oem-odm/">OEM / ODM</a></p><p><a href="/capabilities/custom-packaging/">Custom Packaging</a></p><p><a href="/quality-control/">Quality Control</a></p></div><div><h3>Quick Links</h3><p><a href="/about/">About Us</a></p><p><a href="/blog/">Blog</a></p><p><a href="/faq/">FAQ</a></p><p><a href="/contact/">Contact Us</a></p><p><a href="/privacy-policy/">Privacy Policy</a></p></div></div><div class="footer__bottom"><span>© XUYI Drinkware · Website preview · Specifications subject to verification</span><span>Factory-backed B2B plastic drinkware</span></div></div></footer><div class="sticky-inquiry"><span>Wholesale & OEM Enquiries</span><a class="button" href="/contact/#inquiry">Get Quote →</a></div>'
def page(title,description,body,canonical=None):
 # Internal preview. No index until the company info, media and claims have been verified.
 head='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="color-scheme" content="light"><meta name="theme-color" content="#ffffff"><title>'+e(title)+'</title><meta name="description" content="'+e(description)[:220]+'"><link rel="stylesheet" href="/assets/site.css"><script defer src="/assets/site.js"></script></head><body>'
 rail='<aside class="rail" aria-label="Quick contact"><a href="/contact/#inquiry" aria-label="Contact us">'+ICONS["mail"]+'</a><a href="/contact/?type=sample#inquiry" aria-label="Request a sample">'+ICONS["phone"]+'</a><a href="#" aria-label="Back to top" onclick="scrollTo({top:0,behavior:\'smooth\'});return false">'+ICONS["top"]+'</a></aside>'
 return head+header()+rail+'<main id="main-content">'+body+'</main>'+footer()+'</body></html>'
def intro(crumb,title,subtitle=""):
 return '<section class="page-intro"><div class="shell"><div class="breadcrumb"><a href="/">Home</a> / '+e(crumb)+'</div><span class="eyebrow">XUYI · PLASTIC DRINKWARE</span><h1>'+e(title)+'</h1><p>'+e(subtitle)+'</p></div></section>'
def category_card(cat):
 n,slug,im,desc=cat
 return '<a class="category" href="/collections/'+slug+'/"><div class="category__photo">'+photo(im,n)+'</div><div class="category__body"><h3>'+e(n)+'</h3><span>Explore Collection ↗</span></div></a>'
def product_card(item):
 img=item["images"][0]
 text=(item["name"]+" "+item["model"]+" "+item["capacity"]).lower()
 return '<a class="product-card" data-product-card data-category="'+e(CAT[item["category"]][1])+'" data-search="'+e(text)+'" href="/products/'+e(item["slug"])+'/"><div class="product-card__image">'+photo(img,item["name"]+" model "+item["model"])+'</div><div class="product-card__body"><span class="product-card__small">MODEL '+e(item["model"])+'</span><h3>'+e(item["name"])+'</h3><span class="product-card__link">View Product ↗</span></div></a>'
def product_grid(items):return '<div class="grid grid--4 product-grid">'+''.join(product_card(x) for x in items)+'</div>'
def filters(with_categories=True):
 options='<option value="">All product categories</option>'+''.join('<option value="'+x[1]+'">'+e(x[0])+'</option>' for x in CAT.values())
 return '<div class="filterbar"><input type="search" data-catalog-query aria-label="Search bottles" placeholder="Search model, capacity or bottle type…">' + ('<select aria-label="Filter category" data-catalog-category>'+options+'</select>' if with_categories else '') +'<span class="filter-count" id="filter-count"></span></div>'
def pagination():return '<div class="pagination"><button id="page-prev" type="button" aria-label="Previous page">← Prev</button><span id="page-status" aria-live="polite"></span><button id="page-next" type="button" aria-label="Next page">Next →</button></div>'
def faq_html(items=None):
 arr=items or FAQS
 return '<div class="faq-list">'+''.join('<details><summary>'+e(q)+'</summary><p>'+e(a)+'</p></details>' for q,a in arr)+'</div>'
FAQS=[
("Can you customize bottle colors and logos?","We can review logo artwork, colors and packaging for each selected model. Available decoration methods and order requirements are confirmed during quotation."),
("What is your MOQ for wholesale orders?","Minimum order quantity depends on bottle model, stock availability and customization. Send us the products and estimated volume to get an accurate answer."),
("Do you offer samples before bulk production?","Sample availability, lead time and cost are confirmed according to the product and destination. Please include your model number and required custom work."),
("What plastic materials are used?","Our source catalog lists PP, PE, PC and other component materials on different models. Material specifications and food-contact documentation need checking for each model and destination market."),
("Do you have your own factory?","XUYI operates its own manufacturing facility and may coordinate production through selected partner facilities for some products. We confirm project requirements and applicable quality controls."),
("How long does production and shipping take?","Production and shipping timelines depend on model, order quantity, materials, custom artwork and destination. We provide an order-specific timeline after reviewing requirements."),
("Can I send a product drawing or a similar product sample?","Yes, you can describe the target design and send artwork or specifications. Our team can evaluate what can be supplied or customized and whether tooling is needed."),
("Can we mix colors or different models in one order?","Possible combinations depend on the bottle series, packing process and order quantity. Include your requested color and model breakdown when asking for a quote."),
("Can you provide test reports for my export market?","Please specify the model, destination country and required standards. Any documents offered must match the actual product, material and valid test scope."),
("Are there online prices or a shopping cart?","No. This is a business-to-business quotation website. We quote based on model, quantity, customization and delivery terms.")
]
ARTICLES=[
("wholesale-plastic-water-bottle-buying-guide","Wholesale Plastic Water Bottle Buying Guide","How to compare models, capacity, packaging and production options before requesting a quote."),
("plastic-bottle-material-selection","How to Discuss Plastic Bottle Materials with Suppliers","Questions about material components, suitability and food-contact documentation."),
("custom-logo-water-bottle-checklist","Custom Logo Water Bottle Project Checklist","Artwork, colors, packaging and expected quantities to prepare for an OEM quote."),
("sports-bottle-vs-water-jug","Sports Water Bottle vs Large Water Jug","A practical comparison of small bottles and larger carrying-jug styles."),
("kids-water-bottle-procurement","Kids Water Bottle Wholesale Procurement Guide","Selection, lid formats, packaging and material documentation to ask about."),
("shaker-bottle-wholesale","Protein Shaker Bottle Wholesale Checklist","Choosing shaker bottle capacity, materials and decoration options.")
]
