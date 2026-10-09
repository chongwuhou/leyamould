"""Distinct visual storylines for XUYI's four Why Us pages.

Uses authorized group-reference photos in R2; group sites include some metal
drinkware examples and must be labeled as cross-material examples, not evidence
of plastic equipment or product capability. Keep XUYI catalog visuals separate.
"""
from site_renderer import e,photo
from why_us_content import _table,_faqs,_paragraphs,_list_block
ROOT_URLS=[
 ("OEM / ODM Support","/capabilities/oem-odm/"),
 ("Manufacturing Process","/manufacturing/"),
 ("Quality Assurance","/quality-control/"),
 ("Shipping & Logistics","/shipping-logistics/")
]
def crumbs(d):
 return '<nav class="whyv2-crumb" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span><a href="/why-us/">Why Us</a><span>/</span><span>'+e(d["short"])+'</span></nav>'
def quick_links():
 return '<section class="whyv2-siblings"><div class="shell"><div class="whyv2-siblings__grid">'+''.join('<a href="'+u+'">'+e(t)+' <span>↗</span></a>' for t,u in ROOT_URLS)+'</div></div></section>'
def end(d):
 return '<section class="whyv2-end"><div class="shell"><span class="eyebrow">XUYI PLASTIC DRINKWARE</span><h2>'+e(d["cta_title"])+'</h2><p>'+e(d["cta_paragraph"])+'</p><a class="button" href="/contact/#inquiry">Discuss Your Order →</a></div></section>'
def faqs(d):
 return '<section class="whyv2-faq"><div class="shell"><div class="whyv2-faq__heading"><span class="eyebrow">BUYER FAQ</span><h2>'+e(d["faq_title"])+'</h2><p>'+e(d["faq_summary"])+'</p></div>'+_faqs(d["faqs"])+'</div></section>'
def render_oem(d):
 h='<div class="whyv2 whyv2--oem"><section class="whyv2-oem-hero"><div class="shell">'+crumbs(d)+'<div class="whyv2-oem-hero__grid"><div><span class="eyebrow">OEM / ODM · PRIVATE LABEL · TAIZHOU</span><h1>Plastic Water Bottle <em>OEM &amp; ODM</em></h1><p>'+e(d["answer"])+'</p><div class="whyv2-actions"><a class="button" href="/contact/?type=oem-odm#inquiry">Start an OEM Project →</a><a class="button button--outline" href="/products/">See Bottle Models →</a></div></div><div class="whyv2-oem-hero__image">'+photo("/media/ppt/slide-059.webp","Original XUYI plastic water bottle styles that can be discussed for private-label sourcing","eager")+'<span>XUYI plastic catalog · Select a model before design approval</span></div></div></div></section>'
 h+='<section class="whyv2-oem-tech"><div class="shell"><div class="whyv2-lead"><span class="eyebrow">XUYI PLASTIC DRINKWARE CATALOG</span><h2>Explore Plastic Bottle Branding &amp; Design Options</h2><p>These are genuine XUYI plastic bottle catalog photographs: printed bottles, color combinations, illustrated graphics, closure styles and retail packing examples. They are references for discussing customization, not a claim that every pictured feature can be changed on every model.</p></div><div class="whyv2-oem-tech__grid">'
 tech=[
  ("/media/ppt/slide-020.webp","Custom Logo &amp; Text","Plastic sports bottles with visible printed lettering. Confirm logo dimensions and print suitability for the chosen model.","XUYI plastic water bottles with printed words and colored bottle bodies"),
  ("/media/ppt/slide-049.webp","Bottle &amp; Lid Colors","Existing plastic bottles in contrasting gradient colors. Match proposed body and cap colors against a physical sample.","Three gradient-colored XUYI plastic water bottles with carrying handles"),
  ("/media/ppt/slide-007.webp","Printed Illustrations","Cartoon-print plastic bottles show how graphic decoration may look on a transparent body. Artwork needs approval.","XUYI transparent plastic kids bottles featuring cartoon artwork"),
  ("/media/ppt/slide-038.webp","Lid &amp; Carry Styles","Compare plastic body shapes, drinking lids and carrying features, then confirm compatible component combinations.","XUYI plastic drinking bottles showing multiple flip lids and carry handles"),
  ("/media/ppt/slide-030.webp","Retail Pack Presentation","A children's plastic drinking bottle displayed beside its printed retail carton; discuss box layout and packing per SKU.","XUYI plastic kids water bottles photographed with a matching illustrated packaging box")
 ]
 for path,title,desc,alt in tech:
  h+='<article class="whyv2-oem-tech__card"><div>'+photo(path,alt)+'</div><h3>'+title+'</h3><p>'+e(desc)+'</p></article>'
 h+='</div><p class="whyv2-source-note">All five product photographs are from the XUYI plastic bottle source catalog. Please confirm model, decoration method, components and packaging with a physical sample before ordering.</p></div></section>'
 h+='<section class="whyv2-oem-route"><div class="shell"><div class="whyv2-oem-route__head"><span class="eyebrow">PROJECT DECISION</span><h2>OEM Branding or ODM Development?</h2><p>'+e(d["intro_summary"])+'</p></div>'+_table(d["table_headers"],d["table_rows"],d["table_title"])+'<p class="whyv2-note">'+e(d["table_note"])+'</p></div></section>'
 h+='<section class="whyv2-oem-steps"><div class="shell"><div class="whyv2-lead"><span class="eyebrow">FROM IDEAS TO PRODUCTION</span><h2>Six Project Approval Milestones</h2><p>Each step has a deliverable the buyer can check before moving to the next.</p></div><div class="whyv2-oem-steps__grid">'
 for i,(title,desc) in enumerate(d["steps"],1):
  h+='<article><span>'+str(i).zfill(2)+'</span><h3>'+e(title)+'</h3><p>'+e(desc)+'</p></article>'
 h+='</div><div class="whyv2-oem-steps__sample">'+photo("/media/group/oem-sampling.webp","Team reviewing sample requirements and paperwork")+'<div><span class="eyebrow">SAMPLE & ARTWORK SIGNOFF</span><h3>A Real Sample Is the Point of Reference</h3><p>Confirm the lid, body shape, color, decoration and packing in writing. A digital rendering alone does not establish production suitability.</p><a href="/request-sample/">How to request a sample ↗</a></div></div></div></section>'
 h+='<section class="whyv2-buyer-brief"><div class="shell"><div><span class="eyebrow">READY FOR A QUOTE?</span><h2>'+e(d["checklist_title"])+'</h2><p>'+e(d["checklist_intro"])+'</p></div>'+_list_block(d["checklist"])+'</div></section>'
 return h+faqs(d)+quick_links()+end(d)+'</div>'
def render_factory(d):
 h='<div class="whyv2 whyv2--factory"><section class="whyv2-factory-hero"><div class="shell">'+crumbs(d)+'<div class="whyv2-factory-hero__grid"><div><span class="eyebrow">MANUFACTURING / COMPONENTS / PACKING</span><h1>Plastic Bottle <em>Manufacturing Process</em></h1><p>'+e(d["answer"])+'</p><a href="/contact/?type=manufacturing#inquiry" class="button">Discuss Production →</a></div><div class="whyv2-factory-hero__photo">'+photo("/media/group/factory-bottle-packing.webp","Packaging preparation within the production workflow")+'<span>Packing and production workflow</span></div></div></div></section>'
 h+='<section class="whyv2-factory-map"><div class="shell"><div class="whyv2-lead"><span class="eyebrow">THE PROCESS, NOT JUST A PROMISE</span><h2>How Plastic Bottle Components Come Together</h2><p>Body molding, lid production and assembly are distinct tasks. Exact processes are selected by the bottle design and polymer, not a one-size-fits-all factory claim.</p></div><div class="whyv2-factory-map__steps">'
 stages=[("01","Specify","Body, closure, polymers and capacity"),("02","Produce","Suitable body and component manufacturing"),("03","Assemble","Fit lid, straw, seal and carry parts"),("04","Approve","Inspect, decorate and confirm samples"),("05","Pack","Protect goods and label cartons")]
 for number,title,desc in stages:h+='<div><span>'+number+'</span><strong>'+e(title)+'</strong><small>'+e(desc)+'</small></div>'
 h+='</div><p class="whyv2-note">Plastic bottle bodies may be produced by suitable blow-molding processes and caps by injection molding; exact machinery for XUYI SKUs must be verified separately. </p></div></section>'
 h+='<section class="whyv2-factory-gallery"><div class="shell"><div class="whyv2-lead"><span class="eyebrow">PACKING &amp; WAREHOUSE</span><h2>From Packing to Dispatch</h2><p>Handling and packing practices are planned against each order specification.</p></div><div class="whyv2-factory-gallery__grid">'
 photos=[("factory-bottle-packing","Packing Work Area","Products are organized for order preparation."),("factory-final-pack","Finished Goods Protection","Products are protected ahead of packing and shipment."),("factory-shipment","Warehouse Handling","Packing quantities and dispatch details are checked.")]
 for k,t,description in photos:h+='<figure><div>'+photo('/media/group/'+k+'.webp',t)+'</div><figcaption><strong>'+e(t)+'</strong><p>'+e(description)+'</p></figcaption></figure>'
 h+='</div></div></section>'
 h+='<section class="whyv2-factory-detail"><div class="shell"><div class="whyv2-factory-detail__image">'+photo("/media/ppt/slide-037.webp","XUYI catalog showcasing different plastic water bottle bodies and lids")+'</div><div class="whyv2-factory-detail__copy"><span class="eyebrow">PLASTIC BOTTLE DESIGN</span><h2>'+e(d["intro_title"])+'</h2>'+_paragraphs(d["intro_paragraphs"])+'<a href="/products/" class="button button--outline">Compare Source Models →</a></div></div></section>'
 h+='<section class="whyv2-factory-trace"><div class="shell"><div class="whyv2-lead"><span class="eyebrow">REAL PROCUREMENT CHECKPOINTS</span><h2>Six Steps from Drawing to Shipment</h2><p>'+e(d["steps_summary"])+'</p></div><div class="whyv2-factory-trace__list">'
 for i,(title,desc) in enumerate(d["steps"],1):h+='<article><span>'+str(i).zfill(2)+'</span><div><h3>'+e(title)+'</h3><p>'+e(desc)+'</p></div></article>'
 h+='</div><h3 class="whyv2-factory-trace__table-title">'+e(d["table_title"])+'</h3>'+_table(d["table_headers"],d["table_rows"],d["table_title"])+'</div></section>'
 return h+faqs(d)+quick_links()+end(d)+'</div>'
def render_quality(d):
 h='<div class="whyv2 whyv2--quality"><section class="whyv2-quality-hero"><div class="shell">'+crumbs(d)+'<div class="whyv2-quality-hero__grid"><div><span class="eyebrow">QUALITY / EQUIPMENT / APPROVAL</span><h1>Plastic Water Bottle <em>Quality Control</em></h1><p>'+e(d["answer"])+'</p><a class="button" href="/contact/?type=quality#inquiry">Review Quality Requirements →</a></div><div class="whyv2-quality-hero__instruments">'+photo("/media/group/qa-color-box.webp","Color assessment light box used during quality inspection")+'</div></div></div></section>'
 h+='<section class="whyv2-quality-lab"><div class="shell"><div class="whyv2-lead"><span class="eyebrow">QUALITY INSPECTION</span><h2>Inspection Equipment &amp; Methods</h2><p>Depending on the bottle and packaging requirements, relevant quality and durability checks can be specified and confirmed for each order.</p></div><div class="whyv2-quality-lab__grid">'
 equipment=[("qa-color-box","Color Assessment","Compare molded and printed colors against references."),("qa-print-life","Print Wear","Evaluate print and decoration durability where specified."),("qa-temp-humidity","Temperature &amp; Humidity","Discuss environmental exposure checks for the order."),("qa-vibration","Transport Vibration","Review handling and shipping protection."),("qa-crush-edge","Carton Edge Crush","Check carton material strength when applicable."),("qa-bursting","Packaging Burst Strength","Assess packaging performance under agreed conditions.")]
 for key,title,desc in equipment:h+='<article><div>'+photo('/media/group/'+key+'.webp',title)+'</div><h3>'+title+'</h3><p>'+desc+'</p></article>'
 h+='</div></div></section>'
 h+='<section class="whyv2-quality-plan"><div class="shell"><div class="whyv2-quality-plan__head"><span class="eyebrow">BUYER SPECIFICATION SHEET</span><h2>What to Test on a Plastic Bottle</h2><p>'+e(d["table_summary"])+'</p></div>'+_table(d["table_headers"],d["table_rows"],d["table_title"])+'<p class="whyv2-note">'+e(d["table_note"])+'</p></div></section>'
 h+='<section class="whyv2-quality-proof"><div class="shell"><div><span class="eyebrow">FOOD CONTACT / MATERIALS / APPROVAL</span><h2>Evidence Must Match the Exact SKU</h2>'+_paragraphs(d["intro_paragraphs"])+'</div><div class="whyv2-quality-proof__check"><h3>'+e(d["checklist_title"])+'</h3>'+_list_block(d["checklist"])+'</div></div></section>'
 h+='<section class="whyv2-quality-flow"><div class="shell"><div class="whyv2-lead"><span class="eyebrow">INSPECTION FLOW</span><h2>Six Quality Approval Checkpoints</h2><p>Agree acceptance criteria, testing responsibility and reference samples before bulk shipment.</p></div><div class="whyv2-quality-flow__list">'
 for i,(title,desc) in enumerate(d["steps"],1):h+='<div><span>'+str(i).zfill(2)+'</span><strong>'+e(title)+'</strong><p>'+e(desc)+'</p></div>'
 h+='</div></div></section>'
 return h+faqs(d)+quick_links()+end(d)+'</div>'
def render_shipping(d):
 h='<div class="whyv2 whyv2--shipping"><section class="whyv2-shipping-hero"><div class="shell">'+crumbs(d)+'<div class="whyv2-shipping-hero__grid"><div><span class="eyebrow">EXPORT PACKING & LOGISTICS</span><h1>Plastic Bottle <em>Shipping &amp; Logistics</em></h1><p>'+e(d["answer"])+'</p><a class="button" href="/contact/?type=shipping#inquiry">Discuss Freight & Packing →</a></div><div class="whyv2-shipping-hero__photo">'+photo("/media/group/factory-shipment.webp","Warehouse shelving and prepared shipping goods")+'<span>Shipping arrangements depend on the order and destination</span></div></div></div></section>'
 h+='<section class="whyv2-shipping-options"><div class="shell"><div class="whyv2-lead"><span class="eyebrow">SHIPMENT ROUTES</span><h2>Choose a Suitable Shipping Plan</h2><p>These are transport scenarios rather than fixed services or delivery-time guarantees; cost, customs and responsibility depend on the actual order.</p></div><div class="whyv2-shipping-options__grid">'
 options=[("freight-express","Express / Samples","Useful to discuss for samples and low-volume urgent consignments; check dimensional weight."),
 ("freight-air-sea","Sea or Air Freight","Compare packed volume, lead time, local fees and freight mode for larger orders."),
 ("freight-door","Final-Mile Delivery","Confirm the named Incoterm place, local handling and customs responsibility.")]
 for key,title,desc in options:h+='<article><div>'+photo('/media/group/'+key+'.webp',title)+'</div><h3>'+e(title)+'</h3><p>'+e(desc)+'</p></article>'
 h+='</div></div></section>'
 h+='<section class="whyv2-shipping-pack"><div class="shell"><div class="whyv2-shipping-pack__image">'+photo("/media/group/factory-final-pack.webp","Finished goods protective packaging before shipping")+'</div><div><span class="eyebrow">MASTER CARTON DATA</span><h2>Calculate Landed Costs with Real Packing Dimensions</h2>'+_paragraphs(d["intro_paragraphs"])+'<div class="whyv2-shipping-pack__fields">'+''.join('<span>'+e(x)+'</span>' for x in ['Model / color / quantity','Pieces per master carton','Carton L × W × H','Gross & net weight','Custom labels / barcode','Named destination / Incoterm'])+'</div></div></div></section>'
 h+='<section class="whyv2-shipping-matrix"><div class="shell"><div class="whyv2-lead"><span class="eyebrow">FREIGHT COMPARISON</span><h2>'+e(d["table_title"])+'</h2><p>'+e(d["table_summary"])+'</p></div>'+_table(d["table_headers"],d["table_rows"],d["table_title"])+'<p class="whyv2-note">'+e(d["table_note"])+'</p></div></section>'
 h+='<section class="whyv2-shipping-flow"><div class="shell"><div class="whyv2-lead"><span class="eyebrow">EXPORT CHECKLIST</span><h2>'+e(d["steps_title"])+'</h2><p>'+e(d["steps_summary"])+'</p></div><div class="whyv2-shipping-flow__grid">'+''.join('<article><strong>'+str(i).zfill(2)+'</strong><h3>'+e(t)+'</h3><p>'+e(desc)+'</p></article>' for i,(t,desc) in enumerate(d["steps"],1))+'</div></div></section>'
 h+='<section class="whyv2-shipping-paper"><div class="shell"><h2>'+e(d["checklist_title"])+'</h2>'+_list_block(d["checklist"])+'</div></section>'
 return h+faqs(d)+quick_links()+end(d)+'</div>'
def render(data):
 slug=data["slug"]
 return {"capabilities/oem-odm":render_oem,"manufacturing":render_factory,"quality-control":render_quality,"shipping-logistics":render_shipping}[slug](data)