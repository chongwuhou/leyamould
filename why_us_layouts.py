"""Distinct visual storylines for XUYI's four Why Us pages.

Uses authorized group-reference photos in R2; group sites include some metal
drinkware examples and must be labeled as cross-material examples, not evidence
of plastic equipment or product capability. Keep XUYI catalog visuals separate.
"""
from site_renderer import e,photo
from why_us_content import _table,_faqs,_paragraphs,_list_block
GROUP="/media/group/"
ROOT_URLS=[
 ("OEM / ODM Support","/capabilities/oem-odm/"),
 ("Manufacturing Process","/manufacturing/"),
 ("Quality Assurance","/quality-control/"),
 ("Shipping & Logistics","/shipping-logistics/")
]
def img(k,alt):return photo(GROUP+k+".webp",alt)
def crumbs(d):
 return '<nav class="whyv2-crumb" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span><a href="/why-us/">Why Us</a><span>/</span><span>'+e(d["short"])+'</span></nav>'
def quick_links():
 return '<section class="whyv2-siblings"><div class="shell"><div class="whyv2-siblings__grid">'+''.join('<a href="'+u+'">'+e(t)+' <span>↗</span></a>' for t,u in ROOT_URLS)+'</div></div></section>'
def end(d):
 return '<section class="whyv2-end"><div class="shell"><span class="eyebrow">XUYI PLASTIC DRINKWARE</span><h2>'+e(d["cta_title"])+'</h2><p>'+e(d["cta_paragraph"])+'</p><a class="button" href="/contact/#inquiry">Discuss Your Order →</a><small>Inquiry submissions remain disabled on this preview until approved contact and delivery details are connected.</small></div></section>'
def faqs(d):
 return '<section class="whyv2-faq"><div class="shell"><div class="whyv2-faq__heading"><span class="eyebrow">BUYER FAQ</span><h2>'+e(d["faq_title"])+'</h2><p>'+e(d["faq_summary"])+'</p></div>'+_faqs(d["faqs"])+'</div></section>'
def real_source_note(extra=""):
 return '<p class="whyv2-source-note">Group-site photographs are provided as process or design references; material-specific capabilities and application to each XUYI plastic SKU require confirmation.'+((" "+e(extra)) if extra else "")+'</p>'
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
 h+='</div><div class="whyv2-oem-steps__sample">'+img("oem-sampling","Group sample briefing and quotation paperwork reference")+'<div><span class="eyebrow">SAMPLE & ARTWORK SIGNOFF</span><h3>A Real Sample Is the Point of Reference</h3><p>Confirm the lid, body shape, color, decoration and packing in writing. A digital rendering alone does not establish production suitability.</p><a href="/request-sample/">How to request a sample ↗</a></div></div></div></section>'
 h+='<section class="whyv2-buyer-brief"><div class="shell"><div><span class="eyebrow">READY FOR A QUOTE?</span><h2>'+e(d["checklist_title"])+'</h2><p>'+e(d["checklist_intro"])+'</p></div>'+_list_block(d["checklist"])+'</div></section>'
 return h+faqs(d)+quick_links()+end(d)+'</div>'
def render_factory(d):
 h='<div class="whyv2 whyv2--factory"><section class="whyv2-factory-hero"><div class="shell">'+crumbs(d)+'<div class="whyv2-factory-hero__grid"><div><span class="eyebrow">MANUFACTURING / COMPONENTS / PACKING</span><h1>Plastic Bottle <em>Manufacturing Process</em></h1><p>'+e(d["answer"])+'</p><a href="/contact/?type=manufacturing#inquiry" class="button">Discuss Production →</a></div><div class="whyv2-factory-hero__photo">'+img("factory-bottle-packing","Group packaging workshop staff preparing finished goods in plastic crates")+'<span>Group factory packing reference · plastic manufacturing line to be separately verified</span></div></div></div></section>'
 h+='<section class="whyv2-factory-map"><div class="shell"><div class="whyv2-lead"><span class="eyebrow">THE PROCESS, NOT JUST A PROMISE</span><h2>How Plastic Bottle Components Come Together</h2><p>Body molding, lid production and assembly are distinct tasks. Exact processes are selected by the bottle design and polymer, not a one-size-fits-all factory claim.</p></div><div class="whyv2-factory-map__steps">'
 stages=[("01","Specify","Body, closure, polymers and capacity"),("02","Produce","Suitable body and component manufacturing"),("03","Assemble","Fit lid, straw, seal and carry parts"),("04","Approve","Inspect, decorate and confirm samples"),("05","Pack","Protect goods and label cartons")]
 for number,title,desc in stages:h+='<div><span>'+number+'</span><strong>'+e(title)+'</strong><small>'+e(desc)+'</small></div>'
 h+='</div><p class="whyv2-note">Plastic bottle bodies may be produced by suitable blow-molding processes and caps by injection molding; exact machinery for XUYI SKUs must be verified separately. Group stainless-steel forming machinery is not presented as plastic equipment.</p></div></section>'
 h+='<section class="whyv2-factory-technical" aria-label="Plastic bottle forming methods"><div class="shell"><div class="whyv2-lead"><span class="eyebrow">PLASTIC BOTTLE TECHNICAL PROCESS</span><h2>Actual Plastic Molding Methods, Explained Visually</h2><p>These process reference diagrams and lid-handling photograph relate to plastic drinkware, rather than stainless-steel forming. They help buyers understand the production options; the method used for an XUYI SKU depends on its material and design.</p></div><div class="whyv2-factory-technical__grid">'
 technical=[('plastic-injection-blow','Injection Blow Molding','A preform is injection molded and then expanded in a blow mold. The precise sequence depends on the product and equipment.'),
 ('plastic-extrusion-blow','Extrusion Blow Molding','A molten tube is enclosed by a mold and expanded with air. Trimming, wall profile and geometry require process checks.'),
 ('plastic-lid-molding','Lids & Component Checks','A plastic bottle must match its cap, straw and seal. The reference photograph shows handling of plastic lid components.')]
 for k,title,desc in technical:
  h+='<figure><div>'+img(k,title+' source reference for plastic-bottle production')+'</div><figcaption><h3>'+e(title)+'</h3><p>'+e(desc)+'</p></figcaption></figure>'
 h+='</div><p class="whyv2-source-note">Plastic-specific reference diagrams and component photograph: <a href="https://www.everich.com/manufacturing-process-of-plastic-water-bottles-what-is-blow-moulding/" rel="noopener noreferrer" target="_blank">group technical article on blow molding ↗</a>. Reference images do not certify the equipment installed at XUYI.</p></div></section>'
 h+='<section class="whyv2-factory-gallery"><div class="shell"><div class="whyv2-lead"><span class="eyebrow">GROUP FACTORY PHOTOGRAPHY</span><h2>Real Packing and Warehouse Scenes</h2><p>Original group production and warehouse photographs, shown as supporting process references. They do not establish the particular plastic molding machine installed for any XUYI SKU.</p></div><div class="whyv2-factory-gallery__grid">'
 photos=[("factory-bottle-packing","Packing Work Area","Products are sorted and handled before final packing."),
 ("factory-final-pack","Finished Unit Protection","Packed components and products should meet the approved order specification."),
 ("factory-shipment","Warehouse & Dispatch Area","Carton identifiers and final quantities should match shipping documentation.")]
 for k,title,desc in photos:h+='<figure><div>'+img(k,"Group facility reference: "+title)+'</div><figcaption><strong>'+e(title)+'</strong><p>'+e(desc)+'</p></figcaption></figure>'
 h+='</div>'+real_source_note()+'</div></section>'
 h+='<section class="whyv2-factory-detail"><div class="shell"><div class="whyv2-factory-detail__image">'+photo("/media/ppt/slide-037.webp","XUYI catalog showcasing different plastic water bottle bodies and lids")+'</div><div class="whyv2-factory-detail__copy"><span class="eyebrow">PLASTIC BOTTLE DESIGN</span><h2>'+e(d["intro_title"])+'</h2>'+_paragraphs(d["intro_paragraphs"])+'<a href="/products/" class="button button--outline">Compare Source Models →</a></div></div></section>'
 h+='<section class="whyv2-factory-trace"><div class="shell"><div class="whyv2-lead"><span class="eyebrow">REAL PROCUREMENT CHECKPOINTS</span><h2>Six Steps from Drawing to Shipment</h2><p>'+e(d["steps_summary"])+'</p></div><div class="whyv2-factory-trace__list">'
 for i,(title,desc) in enumerate(d["steps"],1):h+='<article><span>'+str(i).zfill(2)+'</span><div><h3>'+e(title)+'</h3><p>'+e(desc)+'</p></div></article>'
 h+='</div><h3 class="whyv2-factory-trace__table-title">'+e(d["table_title"])+'</h3>'+_table(d["table_headers"],d["table_rows"],d["table_title"])+'</div></section>'
 return h+faqs(d)+quick_links()+end(d)+'</div>'
def render_quality(d):
 h='<div class="whyv2 whyv2--quality"><section class="whyv2-quality-hero"><div class="shell">'+crumbs(d)+'<div class="whyv2-quality-hero__grid"><div><span class="eyebrow">QUALITY / EQUIPMENT / APPROVAL</span><h1>Plastic Water Bottle <em>Quality Control</em></h1><p>'+e(d["answer"])+'</p><a class="button" href="/contact/?type=quality#inquiry">Review Quality Requirements →</a></div><div class="whyv2-quality-hero__instruments">'+img("qa-color-box","Group quality laboratory color assessment light box")+'</div></div></div></section>'
 h+='<section class="whyv2-quality-lab"><div class="shell"><div class="whyv2-lead"><span class="eyebrow">REAL GROUP QA EQUIPMENT PHOTOS</span><h2>Testing and Inspection Equipment</h2><p>Equipment photography from the group quality reference. These instruments illustrate possible checks; availability, methods and test results must be confirmed for the actual XUYI plastic bottle order.</p></div><div class="whyv2-quality-lab__grid">'
 tools=[("qa-color-box","Color Assessment","Compare print or molded color under controlled lighting."),
 ("qa-print-life","Print Wear","Discuss abrasion/rub durability of logo decoration, if applicable."),
 ("qa-temp-humidity","Climate Exposure","Assess relevant packaging or product exposure under agreed conditions."),
 ("qa-vibration","Transport Vibration","Illustrate shipment vibration screening where relevant."),
 ("qa-crush-edge","Carton Edge Crush","Check corrugated board strength for transport planning."),
 ("qa-bursting","Packaging Burst Strength","Assess packaging material strength under a defined method.")]
 for key,title,desc in tools:h+='<article><div>'+img(key,'Group quality equipment: '+title)+'</div><h3>'+e(title)+'</h3><p>'+e(desc)+'</p></article>'
 h+='</div>'+real_source_note('No test result, instrument model or accreditation is implied by these photos.')+'</div></section>'
 h+='<section class="whyv2-quality-plan"><div class="shell"><div class="whyv2-quality-plan__head"><span class="eyebrow">BUYER SPECIFICATION SHEET</span><h2>What to Test on a Plastic Bottle</h2><p>'+e(d["table_summary"])+'</p></div>'+_table(d["table_headers"],d["table_rows"],d["table_title"])+'<p class="whyv2-note">'+e(d["table_note"])+'</p></div></section>'
 h+='<section class="whyv2-quality-proof"><div class="shell"><div><span class="eyebrow">FOOD CONTACT / MATERIALS / APPROVAL</span><h2>Evidence Must Match the Exact SKU</h2>'+_paragraphs(d["intro_paragraphs"])+'</div><div class="whyv2-quality-proof__check"><h3>'+e(d["checklist_title"])+'</h3>'+_list_block(d["checklist"])+'</div></div></section>'
 h+='<section class="whyv2-quality-flow"><div class="shell"><div class="whyv2-lead"><span class="eyebrow">INSPECTION FLOW</span><h2>Six Quality Approval Checkpoints</h2><p>Agree acceptance criteria, testing responsibility and reference samples before bulk shipment.</p></div><div class="whyv2-quality-flow__list">'
 for i,(title,desc) in enumerate(d["steps"],1):h+='<div><span>'+str(i).zfill(2)+'</span><strong>'+e(title)+'</strong><p>'+e(desc)+'</p></div>'
 h+='</div></div></section>'
 return h+faqs(d)+quick_links()+end(d)+'</div>'
def render_shipping(d):
 h='<div class="whyv2 whyv2--shipping"><section class="whyv2-shipping-hero"><div class="shell">'+crumbs(d)+'<div class="whyv2-shipping-hero__grid"><div><span class="eyebrow">EXPORT PACKING & LOGISTICS</span><h1>Plastic Bottle <em>Shipping &amp; Logistics</em></h1><p>'+e(d["answer"])+'</p><a class="button" href="/contact/?type=shipping#inquiry">Discuss Freight & Packing →</a></div><div class="whyv2-shipping-hero__photo">'+img("factory-shipment","Group warehouse photo showing packed goods before dispatch")+'<span>Group warehouse image · shipment service options are quote-dependent</span></div></div></div></section>'
 h+='<section class="whyv2-shipping-options"><div class="shell"><div class="whyv2-lead"><span class="eyebrow">SHIPMENT ROUTES</span><h2>Choose a Suitable Shipping Plan</h2><p>These are transport scenarios rather than fixed services or delivery-time guarantees; cost, customs and responsibility depend on the actual order.</p></div><div class="whyv2-shipping-options__grid">'
 options=[("freight-express","Express / Samples","Useful to discuss for samples and low-volume urgent consignments; check dimensional weight."),
 ("freight-air-sea","Sea or Air Freight","Compare packed volume, lead time, local fees and freight mode for larger orders."),
 ("freight-door","Final-Mile Delivery","Confirm the named Incoterm place, local handling and customs responsibility.")]
 for key,title,desc in options:h+='<article><div>'+img(key,title+' reference image from group logistics content')+'</div><h3>'+e(title)+'</h3><p>'+e(desc)+'</p></article>'
 h+='</div>'+real_source_note('Images illustrate logistics scenarios, not proof of a fixed route or carrier agreement.')+'</div></section>'
 h+='<section class="whyv2-shipping-pack"><div class="shell"><div class="whyv2-shipping-pack__image">'+img("factory-final-pack","Group facility finished product protection and packing photograph")+'</div><div><span class="eyebrow">MASTER CARTON DATA</span><h2>Calculate Landed Costs with Real Packing Dimensions</h2>'+_paragraphs(d["intro_paragraphs"])+'<div class="whyv2-shipping-pack__fields">'+''.join('<span>'+e(x)+'</span>' for x in ['Model / color / quantity','Pieces per master carton','Carton L × W × H','Gross & net weight','Custom labels / barcode','Named destination / Incoterm'])+'</div></div></div></section>'
 h+='<section class="whyv2-shipping-matrix"><div class="shell"><div class="whyv2-lead"><span class="eyebrow">FREIGHT COMPARISON</span><h2>'+e(d["table_title"])+'</h2><p>'+e(d["table_summary"])+'</p></div>'+_table(d["table_headers"],d["table_rows"],d["table_title"])+'<p class="whyv2-note">'+e(d["table_note"])+'</p></div></section>'
 h+='<section class="whyv2-shipping-flow"><div class="shell"><div class="whyv2-lead"><span class="eyebrow">EXPORT CHECKLIST</span><h2>'+e(d["steps_title"])+'</h2><p>'+e(d["steps_summary"])+'</p></div><div class="whyv2-shipping-flow__grid">'+''.join('<article><strong>'+str(i).zfill(2)+'</strong><h3>'+e(t)+'</h3><p>'+e(desc)+'</p></article>' for i,(t,desc) in enumerate(d["steps"],1))+'</div></div></section>'
 h+='<section class="whyv2-shipping-paper"><div class="shell"><h2>'+e(d["checklist_title"])+'</h2>'+_list_block(d["checklist"])+'</div></section>'
 return h+faqs(d)+quick_links()+end(d)+'</div>'
def render(data):
 slug=data["slug"]
 return {"capabilities/oem-odm":render_oem,"manufacturing":render_factory,"quality-control":render_quality,"shipping-logistics":render_shipping}[slug](data)
