from site_renderer import *
import json
def sec(title,desc="",eyebrow="XUYI DRINKWARE"):
 return f'<div class="section__head"><div><span class="eyebrow">{e(eyebrow)}</span><h2 class="section__title">{e(title)}</h2><p class="copy-muted">{e(desc)}</p></div></div>'
def features():
 return '<div class="grid grid--4">'+''.join('<article class="benefit"><h3>'+e(t)+'</h3><p>'+e(d)+'</p></article>' for t,d in [
 ("Factory-backed Supply","We operate our own manufacturing facility and coordinate additional products through selected production partners."),
 ("Custom Branding","Discuss logo artwork, product color, decoration method and brand packaging for compatible models."),
 ("Detailed Product Data","Ask us about capacity, size, material components and packing configuration for each selected model."),
 ("Order Coordination","One B2B inquiry process for product selection, quotation, sampling, quality checks and shipment.")
 ])+'</div>'
def steps():
 return '<div class="steps">'+''.join(f'<div class="step"><strong>0{i}</strong><h3>{e(t)}</h3><p>{e(d)}</p></div>' for i,(t,d) in enumerate([
 ("Inquiry","Share the model, order volume, artwork, destination and special requirements."),
 ("Quotation","Confirm product specifications, feasible options, MOQ and terms."),
 ("Sample Review","Review product samples and artwork where required."),
 ("Production & QC","Produce to agreed specifications and perform relevant quality checks."),
 ("Packing & Dispatch","Confirm carton details, shipment method and shipping documents.")
 ],1))+'</div>'
def catnav(active=None):
 return '<aside class="catalog-side"><strong>Products</strong><a href="/products/"'+(' class="active"' if not active else '')+'>All products</a>'+''.join('<a '+('class="active"' if slug==active else '')+' href="/collections/'+slug+'/">'+e(title)+'</a>' for title,slug,*_ in CAT.values())+'</aside>'
def featured_items():
 out=[];seen=collections.Counter()
 for x in SERIES.values():
  if seen[x["category"]]>=2:continue
  out.append(x);seen[x["category"]]+=1
 return out
def front():
 hero='<section class="hero" data-hero><button class="hero__arrow hero__arrow--prev" data-hero-nav="-1" type="button" aria-label="Previous slide">‹</button><div class="hero__watermark" aria-hidden="true">XUYI</div><div class="hero__inner"><div class="hero__copy"><span class="eyebrow">CUSTOM PLASTIC BOTTLES · OEM & WHOLESALE</span><h1 id="hero-title">Custom Water Bottles <span>Built for Your Brand.</span></h1><p id="hero-description">Explore sports, kids, large capacity and shaker bottles with factory-backed supply and project-specific branding options.</p><a class="button button--round" id="hero-cta" href="/products/">Explore Our Products →</a><p class="hero__note">Taizhou, China · Plastic drinkware · OEM/ODM inquiries</p></div><div class="hero__art"><img src="/media/ppt/slide-059.webp" id="hero-image" alt="XUYI colorful plastic water bottle collection" loading="eager" decoding="async"></div><div class="hero__controls"><span id="hero-counter">01</span> / 03</div></div><button class="hero__arrow hero__arrow--next" data-hero-nav="1" type="button" aria-label="Next slide">›</button></section>'
 cat='<section class="section"><div class="shell">'+sec("Explore Our Plastic Drinkware","Browse four focused product lines. All first-phase photos and models come from the supplied XUYI catalog.","Product Categories")+'<div class="grid grid--4">'+''.join(category_card(v) for v in CAT.values())+'</div></div></section>'
 why='<section class="section section--soft"><div class="shell"><div class="split"><div>'+photo("/media/ppt/slide-049.webp","Plastic sports water bottle catalog photography", 'lazy')+'</div><div><span class="eyebrow">WHY XUYI</span><h2 class="section__title">A Plastic Bottle Partner for B2B Buyers.</h2><p class="copy-muted">We combine our own manufacturing facility with selected production partners for additional requirements. Focus on the right bottle design, custom branding and an organized purchasing process.</p><div class="why-bullets">'+''.join('<article><h3>'+e(t)+'</h3><p>'+e(d)+'</p></article>' for t,d in [("Own Manufacturing","Real production capability, with facility media to be verified."),("Flexible Bottle Range","Sports, kids, large capacity and fitness shaker collections."),("Branding Support","Logo, color, artwork and packaging requirements reviewed by model."),("Wholesale Service","Specification, sample and order coordination for importers.")])+'</div><a class="text-link" href="/about/">Discover XUYI →</a></div></div></div></section>'
 items='<section class="section"><div class="shell">'+sec("Explore Featured Models","A selection from our current source catalog. Model-specific photos and final specifications require review.","Our Products")+product_grid(featured_items())+'<p style="margin-top:26px"><a class="button button--outline" href="/products/">View All Models →</a></p></div></section>'
 caps='<section class="section section--soft"><div class="shell">'+sec("Make Every Bottle Your Brand","Review options with our team. Availability, techniques and MOQ depend on the actual bottle and order.","Capabilities")+'<div class="grid grid--3">'+''.join('<a class="category" href="'+link+'"><div class="category__photo">'+photo(im,alt)+'</div><div class="category__body"><h3>'+e(title)+'</h3><span>View Capability ↗</span></div></a>' for title,link,im,alt in [
  ("Custom Logo & Graphics","/capabilities/custom-logo/","/media/ppt/slide-061.webp","Custom colorful plastic sports bottle designs"),
  ("Custom Manufacturing","/capabilities/custom-manufacturing/","/media/ppt/slide-037.webp","Plastic water bottles with different caps"),
  ("Custom Packaging","/capabilities/custom-packaging/","/media/ppt/slide-065.webp","Bottle packaging and accessories source image")
 ])+'</div></div></section>'
 fac='<section class="section"><div class="shell"><div class="split"><div><span class="eyebrow">FACTORY & QUALITY</span><h2 class="section__title">Manufacturing with a Clear Process.</h2><p class="copy-muted">XUYI has its own production facility. For some products, selected partner factories support the supply process. We keep specifications, sample confirmation, quality checks and delivery coordination part of the project.</p><p class="copy-muted">We will add verified factory, equipment and inspection photos when they are approved for public use.</p><a class="button button--outline" href="/manufacturing/">Explore Manufacturing →</a></div><div class="split__placeholder"><div><strong>REAL FACTORY PHOTOS RESERVED</strong><p>Only verified XUYI production images will appear here.</p></div></div></div></div></section>'
 process='<section class="section section--soft"><div class="shell">'+sec("From Your Idea to Shipment","A straightforward process designed for business buyers.","How We Work")+steps()+'</div></section>'
 buyer='<section class="section"><div class="shell">'+sec("Built for Business Buyers","Product sourcing and customization for global trade.","Buyer Applications")+'<div class="grid grid--4">'+''.join('<article class="benefit"><h3>'+e(t)+'</h3><p>'+e(d)+'</p></article>' for t,d in [("Importers","Select models and shipping configurations for your market."),("Wholesale Distributors","Browse reusable bottles by capacity, lid and material."),("Brands & Private Label","Explore custom logo, color and branded packaging options."),("Sports & Gift Buyers","Find sports, kids and shaker bottle designs for bulk projects.")])+'</div></div></section>'
 faq='<section class="section section--soft"><div class="shell">'+sec("Frequently Asked Questions","Answers to common questions from international purchasing teams.","FAQ")+faq_html(FAQS[:6])+'<p style="margin-top:25px"><a class="text-link" href="/faq/">Read All FAQs →</a></p></div></section>'
 blog='<section class="section"><div class="shell">'+sec("Resources for Wholesale Buyers","Practical guides to comparing products, branding and bulk purchasing.","Resources")+'<div class="article-list">'+''.join('<article class="article-card"><span class="article-card__num">BUYING GUIDE</span><h3>'+e(t)+'</h3><p>'+e(d)+'</p><a href="/blog/'+s+'/">Read Article →</a></article>' for s,t,d in ARTICLES[:3])+'</div></div></section>'
 return hero+factory_intro_module()+cat+bottle_collection_tabs()+why+caps+customization_gallery_module()+fac+process+buyer+faq+blog
def catalog(cat_name=None):
 if cat_name:
  title,slug,im,desc=CAT[cat_name]
  arr=[x for x in SERIES.values() if x["category"]==cat_name]
  heading=title;subtitle=desc+' Explore model-specific specifications, colors and wholesale quotation options.'
 else:
  arr=list(SERIES.values());heading="Explore All Plastic Water Bottles";subtitle="Browse sports water bottles, large capacity water jugs, kids bottles and shaker bottles."
 pagehtml=intro("Products" if not cat_name else "Products / "+CAT[cat_name][0],heading,subtitle)
 pagehtml+='<section class="section"><div class="shell"><div class="catalog-layout">'+catnav(CAT[cat_name][1] if cat_name else None)+'<div>'+filters(not cat_name)+product_grid(arr)+pagination()+'</div></div></div></section>'
 pagehtml+='<section class="section section--soft"><div class="shell">'+sec("Wholesale & Custom Bottle Solutions","Ask about available colors, custom printing, branding and packing for the models that interest you.","OEM & CUSTOMIZATION")+features()+'</div></section>'
 pagehtml+='<section class="section"><div class="shell">'+sec("Wholesale Buying Questions","Contact XUYI with model number, quantity and destination.","Product FAQ")+faq_html(FAQS[:6])+'</div></section>'
 return pagehtml
def detail(obj):
 photos=obj['images'];category=obj['category'];variants=obj['variants']
 fields=[("Model",obj['model']),("Product Type",CAT[category][0]),("Catalog Capacity",", ".join(dict.fromkeys(x['capacity'] for x in variants)))]
 for name,key in [("Source Material","material"),("Dimensions","dimensions"),("Source Colors","colors"),("Packaging","packing"),("Carton Quantity","carton_quantity"),("Carton Dimensions","carton_size")]:
  vals=[str(x.get(key)) for x in variants if x.get(key)]
  if vals:fields.append((name,", ".join(list(dict.fromkeys(vals))[:3])))
 specs='<table class="spec">'+''.join('<tr><td>'+e(name)+'</td><td>'+e(value)+'</td></tr>' for name,value in fields)+'</table>'
 thumbs='<div class="product-detail__thumbs">'+''.join('<button class="product-detail__thumb" data-main-photo="'+e(img)+'" type="button" aria-label="View product catalog image '+str(i+1)+'">'+photo(img,obj['name'])+'</button>' for i,img in enumerate(photos))+'</div>'
 bcrumb='<div class="breadcrumb"><a href="/">Home</a> / <a href="/products/">Products</a> / <a href="/collections/'+CAT[category][1]+'/">'+e(CAT[category][0])+'</a> / '+e(obj['model'])+'</div>'
 h='<section class="section"><div class="shell">'+bcrumb+'<div class="product-detail"><div class="product-detail__photos"><div class="product-detail__main">'+photo(photos[0],obj['name']+' Model '+obj['model'],'eager').replace('<img ','<img id="main-photo" ',1)+'</div>'+thumbs+'<p class="copy-muted" style="font-size:12px">Source: original XUYI Excel / PPT catalog. Photography and specifications require final approval.</p></div><div><span class="eyebrow">PLASTIC DRINKWARE / MODEL '+e(obj['model'])+'</span><h1>'+e(obj['name'])+'</h1><p class="copy-muted">B2B wholesale supply and custom branding inquiries. Please confirm product specifications, quantity, colors and required materials before ordering.</p>'+specs+'<div class="actions"><a class="button" href="/contact/?model='+e(obj['model'])+'#inquiry">Request a Quote →</a><a class="button button--outline" href="/contact/?model='+e(obj['model'])+'&type=sample#inquiry">Request Sample ↗</a></div><p class="notice"><b>Catalog preview:</b> Confirm material by component, correct capacity, target-market food-contact testing, MOQ and lead time before listing as available for sale.</p><div><span class="badge">OEM inquiry</span> <span class="badge">Bulk order</span> <span class="badge">Sample confirmation</span></div></div></div></div></section>'
 h+='<section class="section section--soft"><div class="shell">'+sec("Product Details & Customization","Discuss logo printing, color combinations, packing and any project-specific drawings.","Product Information")+'<div class="grid grid--3">'+''.join('<article class="benefit"><h3>'+e(t)+'</h3><p>'+e(d)+'</p></article>' for t,d in [("Material & Specifications","Use the source figures as a starting point. We verify component materials, dimensions and capacity."),("Colors & Branding","Ask which colors, logo placements and branding methods are available for this exact model."),("Packing & Shipment","Carton details, volume, sample policies and production schedule are confirmed against the order.")])+'</div></div></section>'
 rel=[x for x in SERIES.values() if x['category']==category and x['model']!=obj['model']][:4]
 if rel:h+='<section class="section"><div class="shell">'+sec("Related Water Bottle Models","Compare other sizes and styles from this series.","Related Products")+product_grid(rel)+'</div></section>'
 h+='<section class="section section--soft"><div class="shell">'+sec("Frequently Asked Questions","Answers about wholesale supply and customizing bottle model "+obj['model']+".","Model FAQ")+faq_html(FAQS[:5])+'</div></section>'
 return h

CAPABILITIES=[
("Custom Water Bottle","custom-water-bottle","Explore OEM designs and decoration options for selected plastic drinkware models.",["Select model, capacity and lid format.","Provide any logo, color or branding brief.","Review source material, test requirements and packaging.","Confirm samples, production route and project terms."],"/media/ppt/slide-059.webp"),
("Custom Molding","custom-molding","Discuss whether custom injection molded components or new plastic bottle tooling is feasible.",["Provide technical drawings or physical reference.","Identify lid/body components and applicable materials.","Confirm tooling feasibility and cost before approval.","Test and approve actual samples before mass production."],"/media/ppt/slide-037.webp"),
("Custom Logo & Branding","custom-logo","Turn your selected bottle model into branded merchandise.",["Choose the bottle model and expected capacity.","Send a vector logo or clear artwork where possible.","Confirm suitable print position, color and decoration technique.","Review artwork placement or a physical sample before bulk production."],"/media/ppt/slide-061.webp"),
("Custom Graphics & Colors","custom-graphics","Discuss color combinations, gradient finishes and artwork options for compatible styles.",["Select a source model and reference colors.","Ask about available stock versus custom colors.","Review printed or molded effects on the selected substrate.","Check sample appearance before approving a larger order."],"/media/ppt/slide-060.webp"),
("OEM / ODM Services","oem-odm","Discuss existing designs, modified components and suitable manufacturing paths.",["Share model numbers, drawings or application requirements.","Confirm whether an existing design is suitable or new tooling is needed.","Agree sample and testing requirements before production.","Document specifications, packing, inspection and shipping requirements."],"/media/ppt/slide-037.webp"),
("Custom Manufacturing","custom-manufacturing","Factory-backed production and coordinated partner manufacturing for approved bottle projects.",["Confirm product specifications and source materials.","Clarify whether the selected product is produced in-house or through a vetted partner.","Approve samples, tooling or production specifications as appropriate.","Apply the agreed project quality-check and packing process."],"/media/ppt/slide-045.webp"),
("Custom Packaging","custom-packaging","Match packaging to your brand presentation and logistics requirements.",["Specify retail box or bulk carton preferences.","Confirm label, barcode and artwork requirements.","Review carton quantities, weights and outer carton marking.","Approve the actual packing method before shipping."],"/media/ppt/slide-065.webp")
]
def capabilities_page():
 h=intro("Capabilities","Custom Water Bottle Capabilities","Branding, packaging, production and project support for B2B plastic drinkware sourcing.")
 h+='<section class="section"><div class="shell">'+sec("Create a Product That Fits Your Market","From logo artwork to production details, every customization is evaluated by product model.","Capabilities")
 for title,slug,desc,stepslist,im in CAPABILITIES:
  h+='<div class="split" style="margin:48px 0 65px"><div>'+photo(im,title+' sample from catalog')+'</div><div><span class="eyebrow">CUSTOMIZATION</span><h2 class="section__title">'+e(title)+'</h2><p class="copy-muted">'+e(desc)+'</p><p><a class="button button--outline" href="/capabilities/'+slug+'/">Learn More →</a></p></div></div>'
 h+='</div></section><section class="section section--soft"><div class="shell">'+sec("How Our Custom Projects Work","Share your requirements, review feasible options, approve samples and confirm details before manufacture.")+steps()+'</div></section>'
 return h
def capability_detail(item):
 title,slug,desc,stepslist,im=item
 h=intro("Capabilities / "+title,title,desc)
 h+='<section class="section"><div class="shell"><div class="split"><div>'+photo(im,title+' source catalog imagery')+'</div><div><span class="eyebrow">BRAND & MANUFACTURING SERVICES</span><h2 class="section__title">Plan Your '+e(title)+' Project.</h2><p class="copy-muted">'+e(desc)+'</p><p class="copy-muted">Actual techniques, order quantity and testing depend on the selected bottle and materials. XUYI will confirm feasibility when preparing a quotation.</p><a href="/contact/?type='+slug+'#inquiry" class="button">Discuss This Service →</a></div></div></div></section>'
 h+='<section class="section section--soft"><div class="shell">'+sec("What We Need from Buyers","A clear brief helps us check the correct manufacturing and custom options.","Project Checklist")+'<div class="grid grid--4">'+''.join('<article class="benefit"><h3>0'+str(i+1)+' · '+e(t.split(' ')[0])+'</h3><p>'+e(t)+'</p></article>' for i,t in enumerate(stepslist))+'</div></div></section>'
 h+='<section class="section"><div class="shell">'+sec("Explore Related Capabilities","Combine products, branding and packaging requirements in one inquiry.","Explore More")+'<div class="grid grid--3">'+''.join('<article class="article-card"><h3>'+e(t)+'</h3><p>'+e(d)+'</p><a href="/capabilities/'+sid+'/">Learn More →</a></article>' for t,sid,d,*_ in CAPABILITIES if sid!=slug)+'</div></div></section>'
 h+='<section class="section section--soft"><div class="shell">'+sec("Questions About Custom Orders","Common questions from international importers.","FAQ")+faq_html(FAQS[:6])+'</div></section>'
 return h
def about():
 h=intro("About Us","About XUYI Drinkware","A Taizhou-based producer and supplier specializing in plastic sports bottles, kids bottles, large capacity jugs and shaker bottles.")
 h+='<section class="section"><div class="shell"><div class="split"><div><span class="eyebrow">OUR COMPANY</span><h2 class="section__title">Focused on Plastic Water Bottles for B2B Trade.</h2><p class="copy-muted">Our company is 台州市旭一家居用品有限公司, based in Taizhou, Zhejiang, China. XUYI has its own manufacturing facility and also works with selected production partners when projects require additional styles or processes.</p><p class="copy-muted">We work with brand teams, wholesale buyers, importers and distributors to discuss products, customization, packaging and order requirements.</p><p class="notice">The official registered English legal company name, certifications and factory capacity figures will be added after document verification.</p></div><div>'+photo("/media/ppt/slide-049.webp","Original sports water bottle catalog source image")+'</div></div></div></section>'
 h+='<section class="section section--soft"><div class="shell">'+sec("What We Focus On","A clear product offer and practical B2B service instead of a retail shopping cart.","Why XUYI")+features()+'</div></section>'
 h+='<section class="section"><div class="shell">'+sec("Our Plastic Bottle Collections","Choose from four primary product lines.","Products")+'<div class="grid grid--4">'+''.join(category_card(v) for v in CAT.values())+'</div></div></section>'
 h+='<section class="section section--soft"><div class="shell">'+sec("Meet Our Manufacturing Process","See how project details move from product selection to shipping.","Our Process")+steps()+'</div></section>'
 return h
def manufacturing():
 h=intro("About / Manufacturing","Factory & Manufacturing","Our own factory is at the core of our operation, with selected partner support for some products and processes.")
 h+='<section class="section"><div class="shell"><div class="split"><div><span class="eyebrow">PRODUCTION</span><h2 class="section__title">Real Factory Capacity. Clearly Explained.</h2><p class="copy-muted">XUYI operates its own manufacturing facility in Taizhou. Some orders may involve carefully selected partner facilities. We coordinate each approved project requirements for materials, samples, inspection and packing.</p><p class="copy-muted">Precise workshop photos, equipment images and capacity data will be published only after XUYI verifies them.</p><a class="button button--outline" href="/quality-control/">How We Handle Quality →</a></div><div class="split__placeholder"><div><h3>Actual Factory Media Pending</h3><p>Reserved for verified XUYI equipment, workshop, staff and inspection imagery.</p></div></div></div></div></section>'
 h+='<section class="section section--soft"><div class="shell">'+sec("From Specification to Delivery","An organized manufacturing workflow is essential for bulk purchasing.","Production Process")+steps()+'</div></section>'
 return h
def quality():
 h=intro("About / Quality Control","Quality Control & Documentation","Quality processes and supporting material documents must match the specific model and destination market.")
 h+='<section class="section"><div class="shell">'+sec("Product Quality Depends on the Details","We confirm project-specific information before making material or certification claims.","Quality Focus")+'<div class="grid grid--3">'+''.join('<article class="benefit"><h3>'+e(t)+'</h3><p>'+e(d)+'</p></article>' for t,d in [
 ("Material Identification","Verify the actual components and plastic material of the selected bottle. A multi-material entry is not evidence of BPA-free status."),
 ("Sample Confirmation","Review lid function, capacity, colors, printing and packing against the agreed sample."),
 ("Production & Packing Checks","Agree on measurable inspection points, carton configuration and product condition prior to shipment."),
 ("Testing Scope","Request reports for the actual SKU, materials and applicable destination-market requirements."),
 ("Supplier Coordination","For relevant partner-made styles, confirm how requirements and acceptance checks are handled."),
 ("Traceable Order Details","Maintain clear records of model number, variant, artwork and final approved specification.")
 ])+'</div><div class="notice" style="margin-top:36px">We do not publish an unverified FDA, LFGB, BPA-free, Tritan, food-safe or other compliance claim. Ask us about specific documentation for your selected models.</div></div></section>'
 h+='<section class="section section--soft"><div class="shell">'+sec("Quality FAQs","Key compliance questions to include in your sourcing brief.","Buyer Questions")+faq_html(FAQS[3:9])+'</div></section>'
 return h
def shipping():
 h=intro("About / Shipping","Packing, Shipping & Logistics","Confirm practical carton information and the required delivery terms before production.")
 h+='<section class="section"><div class="shell">'+sec("Prepare Bottles for International Wholesale Orders","Packaging options and shipment requirements vary by model, order size and destination.","Shipping & Packing")+'<div class="grid grid--3">'+''.join('<article class="benefit"><h3>'+e(t)+'</h3><p>'+e(d)+'</p></article>' for t,d in [
 ("Carton Specifications","Use model-specific quantity, carton dimensions and gross weight after reconfirmation."),
 ("Packing Options","Discuss bulk bags, individual boxes, labels and customized cartons as available."),
 ("Destination & Documentation","Provide destination, preferred shipping method and any necessary labeling or documents.")
 ])+'</div><div style="margin-top:40px"><a href="/contact/#inquiry" class="button">Request Packing Details →</a></div></div></section>'
 return h
def faq_page():
 h=intro("FAQ","Frequently Asked Questions","The most common questions about buying, customizing and importing plastic water bottles.")
 h+='<section class="section"><div class="shell">'+sec("Wholesale, Customization & Product Questions","Answers are general guidance. Actual MOQ, materials, lead time and certification depend on the model.","B2B FAQ")+faq_html(FAQS)+'</div></section>'
 h+='<section class="section section--soft"><div class="shell">'+sec("Explore the Buying Guides","More information on bottle choice, logos and packaging.","Resources")+'<div class="article-list">'+''.join('<article class="article-card"><h3>'+e(t)+'</h3><p>'+e(d)+'</p><a href="/blog/'+slug+'/">Read Article →</a></article>' for slug,t,d in ARTICLES[:3])+'</div></div></section>'
 return h
def contact():
 h=intro("Contact Us","Contact XUYI Drinkware","For bulk plastic bottle sourcing, OEM/ODM questions, product samples and private-label enquiries.")
 h+='<section class="section"><div class="shell"><div class="contact-layout"><div><span class="eyebrow">BUSINESS ENQUIRIES</span><h2 class="section__title">Let’s Talk About Your Project.</h2><p class="copy-muted">Tell us what models you need, how many units you plan to order and whether you require logo printing, different colors or special packaging.</p><div class="benefit"><h3>What to include</h3><p>Product model or catalog reference, estimated quantity, target market, logo/artwork, carton details and preferred delivery terms.</p></div><div class="benefit"><h3>Company</h3><p>台州市旭一家居用品有限公司<br>Taizhou, Zhejiang, China</p></div><p class="notice">Contact email, phone, WhatsApp and form delivery service must be verified before public launch. This prototype deliberately does not accept live inquiries yet.</p></div><form class="form" id="inquiry" aria-label="Wholesale inquiry preview form" onsubmit="return false"><div class="form__row"><label>Company Name<input placeholder="Your company" autocomplete="organization" required></label><label>Work Email<input type="email" placeholder="name@company.com" autocomplete="email" required></label></div><div class="form__row"><label>Product Model<input name="model" id="inquiry-model" placeholder="e.g. 2501"></label><label>Estimated Quantity<input name="quantity" inputmode="numeric" placeholder="e.g. 3000 pcs"></label></div><div class="form__row"><label>Destination Country<input name="country" placeholder="Destination country"></label><label>Inquiry Type<select name="type"><option>Wholesale Quote</option><option>Custom Logo / Branding</option><option>Samples</option><option>OEM / ODM</option></select></label></div><label>Your Requirements<textarea rows="5" placeholder="Bottle design, size, colors, logo, artwork, packing and shipping details"></textarea></label><label><input type="checkbox" style="width:auto" disabled> I agree to the privacy notice (enabled after privacy review)</label><button class="button" type="button" disabled>Inquiry Form Coming Soon</button><p class="copy-muted" style="font-size:12px;margin:0">No information is submitted by this preview form.</p></form></div></div></section>'
 return h
def blog_index():
 h=intro("Blog","Water Bottle Buying Guides","Practical wholesale buying guides, customization checklists and answers for sourcing teams.")
 h+='<section class="section"><div class="shell">'+sec("Procurement & Customization Guides","Research-oriented resources based on the actual bottle categories we supply.","Buyer Resources")+'<div class="article-list">'+''.join('<article class="article-card"><span class="article-card__num">B2B SOURCING GUIDE</span><h3>'+e(t)+'</h3><p>'+e(d)+'</p><a href="/blog/'+slug+'/">Read Guide →</a></article>' for slug,t,d in ARTICLES)+'</div></div></section>'
 return h
CONTENT={
 "wholesale-plastic-water-bottle-buying-guide":[("Start with the buyer’s use case","Sports bottle, children’s bottle, large capacity jug and shaker cup have different handling and carton needs. Choose the product line before comparing colors."),("Confirm the exact model","Ask for the model code, accurate capacity, individual size, material by component and images of the actual item. Avoid mixing variants with the same short model number."),("Prepare a detailed quote request","Include planned order quantity, colors, preferred lid, logo artwork, individual packing and destination country. Also ask for sample and inspection terms."),("Compare total sourcing requirements","The lowest product price is not the whole order cost. Review carton size, breakage or damage risk, labeling, shipment terms and required test documents.")],
 "plastic-bottle-material-selection":[("Materials can vary by component","A single bottle may have a body, cap, seal, straw, handle and other separate parts. Material labels such as PC, PP, PE or ABS should identify which part is made from what."),("Match documentation to the destination","Food-contact materials are regulated differently by market. Request documents that match the exact SKU, materials and intended food contact usage."),("Do not assume equivalence","PC, Tritan, PP and other polymers are not interchangeable labels. Do not advertise BPA-free or a certificate based solely on appearance or supplier assumptions."),("Confirm materials before production","Lock down the material composition, colors, finish, printing and sample properties before approving a larger order.")],
 "custom-logo-water-bottle-checklist":[("Select the model and location","Choose the bottle body material and logo area. Curved, textured or translucent surfaces can affect decoration choices."),("Provide usable artwork","Vector logo files and a preferred color reference speed up feasibility review. For multiple colors, specify how the artwork should appear."),("Confirm method and quantity","Artwork setup, decoration method, sample cost and MOQ may differ by model. Get an itemized answer before committing."),("Review a sample","Check size, location, colors and durability expectations against a real sample. Agree on packaging and carton markings.")],
 "sports-bottle-vs-water-jug":[("Consider where it is carried","A compact sports bottle is easier to carry daily; a large jug may prioritize grip, handles, shoulder strap and hydration volume."),("Capacity affects shipping","Different bottle sizes change unit dimensions, carton density and shipment planning. Confirm actual capacity and carton pack per SKU."),("Pay attention to lids","Straight-drink caps, spouts, straw lids and seals are not identical. Ask for close photos and operating instructions where applicable."),("Fit the sales channel","Sports, gym, outdoor, school and promotional channels may require different designs and packaging.")],
 "kids-water-bottle-procurement":[("Bottle use and age suitability","Children’s designs often use straw lids, flip caps and carry straps. Do not assume every kids’ cup is suitable for all ages."),("Ask about every component","Material declarations should cover drinking contact surfaces, straw and lid as applicable. Market requirements for children's articles can be stricter."),("Verify cleaning and sealing","Ask suppliers for instructions and sample tests that match the exact bottle design and intended use."),("Prepare compliant packaging","Country-specific labeling, warnings and reports need review before launch.")],
 "shaker-bottle-wholesale":[("Distinguish shaker styles","A shaker bottle is not necessarily supplied with a whisk ball, mesh or special mixing component. Confirm the physical components."),("Check capacity and graduation","Source catalogs may show several capacities within a series. Verify fill volume, printed measurement scale and lid closure."),("Review plastic and branding","Ask for verified body and lid materials as well as available decoration methods."),("Match packaging to the order","Carton quantity, sample policy and production time should be confirmed for the chosen shaker and order volume.")]
}
def blog_article(slug,title,desc):
 body=intro("Blog / Buying Guide",title,desc)
 body+='<section class="section"><div class="shell"><article class="article"><p>'+e(desc)+'</p>'
 for t,p in CONTENT[slug]:body+='<h2>'+e(t)+'</h2><p>'+e(p)+'</p>'
 body+='<h2>Need a specific product recommendation?</h2><p>Send the models and expected quantity. Our team can confirm actual material, capacity, available customization and relevant project details.</p><a class="button" href="/contact/#inquiry">Discuss Your Requirements →</a></article></div></section>'
 return body
def privacy():
 h=intro("Privacy Policy","Privacy & Inquiry Data","Preview policy describing planned use of customer inquiry information.")
 h+='<section class="section"><div class="shell"><article class="article"><p>This site is currently a non-transactional preview. The contact form is disabled, and no inquiries are accepted through it.</p><h2>Planned inquiry processing</h2><p>Once enabled, the form will request business contact details, model numbers, quantities and requirements to respond to B2B inquiries. Information must be collected with appropriate notice, kept securely and not repurposed beyond the relevant commercial communications without a lawful basis.</p><h2>Third-party services</h2><p>Hosting, security and storage services may be supplied by Cloudflare. Final privacy and retention terms will be reviewed before activating live submissions.</p><h2>Contact</h2><p>Verified company email and privacy contact details will be added before public launch.</p></article></div></section>'
 return h

# Extended buyer-facing page family: follows target navigation without importing non-plastic products.
FEATURES=[
 ('straw-lid','Straw Lid Bottle Styles','Explore sports and kids bottle formats pictured with straws. Confirm the lid supplied with each exact model.',('/collections/kids-water-bottles/','/collections/sports-water-bottles/'),'/media/ppt/slide-066.webp'),
 ('flip-top','Flip-Top Bottle Styles','Browse handy flip-top cap styles. Closure and sealing features require model-by-model confirmation.',('/collections/sports-water-bottles/','/collections/kids-water-bottles/'),'/media/ppt/slide-037.webp'),
 ('carry-handle','Carry-Handle Bottle Styles','Browse bottles with carry loops, handles and carrying straps. Confirm the pictured component per SKU.',('/collections/large-capacity-water-jugs/','/collections/sports-water-bottles/'),'/media/ppt/slide-059.webp'),
 ('large-capacity','Large Capacity Plastic Bottles','Find larger-volume drinkware and plastic water jugs for gym and outdoor sourcing.',('/collections/large-capacity-water-jugs/',),'/media/ppt/slide-055.webp'),
 ('gradient-colors','Gradient Color Plastic Bottles','Compare multicolor gradient catalog finishes and discuss applicable branding and color options.',('/collections/sports-water-bottles/','/collections/kids-water-bottles/'),'/media/ppt/slide-060.webp')
]
APPLICATIONS=[
 ('gym-sports','Gym & Sports Water Bottles','Hydration bottle and shaker choices for gyms and sports product buyers.',('/collections/sports-water-bottles/','/collections/plastic-shaker-bottles/'),'/media/ppt/slide-037.webp'),
 ('outdoor-travel','Outdoor & Travel Drinkware','Carry-friendly bottles and large plastic water jugs for outdoor and travel collections.',('/collections/sports-water-bottles/','/collections/large-capacity-water-jugs/'),'/media/ppt/slide-055.webp'),
 ('kids-school','Kids & School Bottles','Colorful kids and straw-bottle styles. Verify age suitability and component materials for the target market.',('/collections/kids-water-bottles/',),'/media/ppt/slide-030.webp'),
 ('everyday-hydration','Everyday Water Bottles','Practical drinkware for everyday use, reusable bottle programs and routine carry.',('/collections/sports-water-bottles/',),'/media/ppt/slide-066.webp'),
 ('promotional-gifts','Custom Promotional Bottles','B2B promotional drinkware projects with model-dependent printing and branded packing.',('/collections/sports-water-bottles/','/collections/plastic-shaker-bottles/'),'/media/ppt/slide-061.webp')
]
def topic_page(kind,entry):
 slug,title,description,links,photo_src=entry
 allowed=[cat for cat,v in CAT.items() if '/collections/'+v[1]+'/' in links]
 selected=[x for x in SERIES.values() if x['category'] in allowed][:12]
 body=intro(('Bottle by Feature' if kind=='features' else 'Bottle by Use')+' / '+title,title,description)
 body+='<section class="section"><div class="shell"><div class="split"><div><span class="eyebrow">XUYI BOTTLE COLLECTIONS</span><h2 class="section__title">Select the Right Bottle for Your Market.</h2><p class="copy-muted">'+e(description)+'</p><p class="notice">Catalog photos illustrate possible styles. Verify the exact SKU, lid parts, material and available finish before purchasing or promoting a product.</p><a class="button" href="/contact/#inquiry">Discuss Your Requirements →</a></div><div>'+photo(photo_src,title+' XUYI bottle catalog source image')+'</div></div></div></section>'
 body+='<section class="section section--soft"><div class="shell">'+sec('Explore Related Bottle Models','A starting selection from XUYI product source materials.','PLASTIC BOTTLE COLLECTION')+product_grid(selected)+'</div></section>'
 body+='<section class="section"><div class="shell">'+sec('Browse More Categories','Compare other plastic bottle styles by product family.','PRODUCT TYPES')+'<div class="grid grid--4">'+''.join(category_card(v) for v in CAT.values())+'</div></div></section>'
 body+='<section class="section section--soft"><div class="shell">'+sec('Questions for Wholesale Buyers','Check model-specific availability, decoration, materials and destination requirements.','SOURCING FAQ')+faq_html(FAQS[:6])+'</div></section>'
 return body
def why_us():
 body=intro('Why Us','Why Work with XUYI?','Factory-backed plastic water bottle sourcing with customization, product selection and clear project communication.')
 body+='<section class="section"><div class="shell"><div class="split"><div><span class="eyebrow">WHY XUYI</span><h2 class="section__title">One Project. The Right Bottle. A Clear Process.</h2><p class="copy-muted">XUYI operates its own manufacturing facility and may work with selected production partners for particular drinkware designs. We clarify materials, model numbers, samples, branding and shipment specifications for every project.</p><a class="button" href="/contact/#inquiry">Send Your Brief →</a></div><div>'+photo('/media/ppt/slide-037.webp','XUYI plastic sports bottle catalog assortment')+'</div></div></div></section>'
 body+='<section class="section section--soft"><div class="shell">'+sec('What You Can Check With Us','These are process commitments, not unverified numerical promises or certification claims.','BUYER ADVANTAGES')+'<div class="proof-grid">'+''.join('<article><span>'+e(icon)+'</span><h3>'+e(title)+'</h3><p>'+e(text)+'</p></article>' for icon,title,text in [('01','Factory-backed Supply','Our own facility plus selected partner manufacturing where needed.'),('02','Model-specific Sourcing','Choose using original model numbers and photos.'),('03','OEM & Customization','Discuss logo, graphics, colors and packing against a selected SKU.'),('04','Order Coordination','Confirm samples, specifications, quality checks and delivery terms.')])+'</div></div></section>'
 body+='<section class="section"><div class="shell">'+sec('See How We Work','Explore our manufacturing, quality and shipment process pages.','SUPPORT')+'<div class="grid grid--3">'+''.join('<a class="category" href="'+uri+'"><div class="category__photo">'+photo(im,title)+'</div><div class="category__body"><h3>'+e(title)+'</h3><span>Learn More ↗</span></div></a>' for title,uri,im in [('OEM & ODM','/capabilities/oem-odm/','/media/ppt/slide-060.webp'),('Manufacturing Process','/manufacturing/','/media/ppt/slide-037.webp'),('Quality Assurance','/quality-control/','/media/ppt/slide-066.webp')])+'</div></div></section>'
 body+='<section class="section section--soft"><div class="shell">'+sec('Buyer Questions','What to know before sending your first wholesale quote request.','FAQ')+faq_html(FAQS[:6])+'</div></section>'
 return body
SAMPLE_STEPS=[
 ('Share a Model & Brief','Send a bottle model, desired capacity, estimated quantity, customization requirements and country.'),
 ('Confirm Available Options','We check source design details, available samples, artwork needs and any special requirements.'),
 ('Agree Sample Details','Sample lead time, fee, delivery cost and documentation are confirmed for the actual selected product.'),
 ('Prepare or Source Samples','The appropriate production or sourcing team prepares the agreed sample as feasible.'),
 ('Check Sample & Artwork','Inspect the sample’s dimensions, lid function, appearance and decoration against the agreed brief.'),
 ('Arrange Dispatch & Feedback','Confirm shipping details and review buyer feedback before discussing any bulk production.')
]
def sample_page():
 body=intro('Sample Request','Request a Plastic Bottle Sample','Review models and branding options before a wholesale order. Sample availability and fee vary by design.')
 body+='<section class="section"><div class="shell">'+sec('How to Request a Bottle Sample','A six-step buyer workflow inspired by established B2B sample processes, adapted to XUYI’s project-specific verification.','SAMPLE PROCESS')+'<div class="sample-flow">'+''.join('<article><span>'+str(i).zfill(2)+'</span><h3>'+e(title)+'</h3><p>'+e(desc)+'</p></article>' for i,(title,desc) in enumerate(SAMPLE_STEPS,1))+'</div></div></section>'
 body+='<section class="section section--soft"><div class="shell"><div class="split"><div>'+photo('/media/ppt/slide-059.webp','XUYI plastic bottle styles for sample inquiry')+'</div><div><span class="eyebrow">SAMPLE INQUIRY</span><h2 class="section__title">Tell Us What You Would Like to Test.</h2><p class="copy-muted">Include the exact bottle code, reference photo, target quantity, logo requirements and country. We will only quote verified sample options.</p><p class="notice">The contact form is still a non-submitting preview. We will enable actual delivery after a company email and privacy terms are confirmed.</p><a href="/contact/?type=sample#inquiry" class="button">Prepare Sample Request →</a></div></div></div></section>'
 body+='<section class="section"><div class="shell">'+sec('Sample FAQs','Pre-production sample costs and logistics depend on the requested bottle.','BUYER QUESTIONS')+faq_html(FAQS[:6])+'</div></section>'
 return body
def factory_intro_module():
 return '<section class="section"><div class="shell"><div class="kreat-intro"><div class="kreat-intro__copy"><span class="eyebrow">WELCOME TO XUYI</span><h2>Reliable <em>Plastic Bottle</em> Manufacturing Partner.</h2><p class="copy-muted">We focus on plastic water bottles for brands, importers and wholesalers. XUYI operates its own factory and may coordinate selected partner-made products, depending on model and project requirements.</p><p class="copy-muted">Our goal is clear product specifications, practical customization options and carefully planned purchasing and delivery.</p><a class="button button--outline button--round" href="/about/">Learn More About XUYI →</a></div><div class="kreat-intro__media">'+photo('/media/ppt/slide-037.webp','Original XUYI sports bottle collection photography')+'</div></div></div></section>'
def customization_gallery_module():
 options=[
 ('Custom Bottle Shapes','Discuss existing plastic designs and potential structural changes.','/media/ppt/slide-055.webp','/capabilities/custom-molding/'),
 ('Bottle Lids & Carry Options','Browse straw, flip-top and handle styles from our source catalog.','/media/ppt/slide-066.webp','/features/flip-top/'),
 ('Custom Graphics & Colors','Choose brand colors, artwork and printing options by model.','/media/ppt/slide-060.webp','/capabilities/custom-graphics/'),
 ('Logo Decoration','Review possible printing positions and branding feasibility.','/media/ppt/slide-061.webp','/capabilities/custom-logo/'),
 ('Capacity & Volume','Compare available bottle sizes and packaging implications.','/media/ppt/slide-055.webp','/features/large-capacity/'),
 ('Custom Packaging','Request cartons, labels and project-specific branded packing.','/media/ppt/slide-065.webp','/capabilities/custom-packaging/')
 ]
 return '<section class="section"><div class="shell">'+sec('Custom Unique Bottles for Your Brand','Explore model-dependent options for caps, shapes, artwork, capacity and packaging. Final feasibility is confirmed by sample and quotation.','CUSTOM BOTTLES')+'<div class="custom-grid">'+''.join('<a class="custom-tile" href="'+uri+'"><div class="custom-tile__photo">'+photo(im,title)+'</div><div class="custom-tile__copy"><h3>'+e(title)+'</h3><p>'+e(desc)+'</p><span>Explore Options →</span></div></a>' for title,desc,im,uri in options)+'</div></div></section>'


def bottle_collection_tabs():
 names=[("Sports Bottles","Plastic Sports Water Bottles"),("Kids Bottles","Kids Plastic Water Bottles"),("Water Jugs","Large Capacity Water Jugs"),("Shaker Bottles","Plastic Shaker Bottles")]
 content='<section class="section section--soft"><div class="shell">'+sec("Rocket Your Brand with XUYI Plastic Bottles","Pick a product line to preview the relevant catalog models and discuss private-label sourcing.","OUR COLLECTIONS")
 content+='<div class="bottle-tabs" role="tablist" aria-label="Browse bottle collections">'
 for i,(label,cat) in enumerate(names):
  content+='<button class="bottle-tab'+(' active' if i==0 else '')+'" role="tab" id="bottle-tab-'+str(i)+'" aria-controls="bottle-panel-'+str(i)+'" aria-selected="'+('true' if i==0 else 'false')+'" type="button">'+e(label)+'</button>'
 content+='</div>'
 for i,(label,cat) in enumerate(names):
  items=[x for x in SERIES.values() if x['category']==cat][:6]
  content+='<div class="bottle-tabpanel" role="tabpanel" id="bottle-panel-'+str(i)+'" aria-labelledby="bottle-tab-'+str(i)+'" '+('hidden' if i else '')+'>'+product_grid(items)+'<p style="margin-top:24px"><a href="/collections/'+CAT[cat][1]+'/" class="button button--outline">Explore '+e(label)+' →</a></p></div>'
 content+='</div></section>'
 return content

def generate():
 build_url('index.html','Homepage',page('Custom Plastic Water Bottle Manufacturer in China | XUYI Drinkware','Factory-backed plastic sports, kids and shaker bottles for wholesale and OEM/ODM sourcing.',front()))
 build_url('products/index.html','All Products',page('Plastic Water Bottle Catalog | XUYI Drinkware','Explore plastic sports water bottles, large capacity water jugs, kids bottles and shaker bottles.',catalog()))
 for cat,(title,slug,im,desc) in CAT.items():
  build_url('collections/'+slug+'/index.html',title,page(title+' Wholesale | XUYI Drinkware',desc,catalog(cat)))
 for product in SERIES.values():
  build_url('products/'+product['slug']+'/index.html','Model '+product['model'],page(product['name']+' — Model '+product['model']+' | XUYI',product['name']+' B2B plastic water bottle product specifications and wholesale inquiry.',detail(product)))
 build_url('capabilities/index.html','Capabilities',page('Plastic Bottle OEM & Customization | XUYI','Logo, graphics, OEM/ODM and custom packing options for bulk plastic drinkware.',capabilities_page()))
 for cap in CAPABILITIES:
  title,slug,desc,*_=cap
  build_url('capabilities/'+slug+'/index.html',title,page(title+' | XUYI Drinkware',desc,capability_detail(cap)))
 for slug,title,description,fn in [
 ('about','About', 'Learn about XUYI’s factory-backed plastic water bottle business.',about),
 ('manufacturing','Manufacturing','Our factory and selected partner supply process for plastic drinkware.',manufacturing),
 ('quality-control','Quality Control','Quality checks and documentation for plastic water bottle sourcing.',quality),
 ('shipping-logistics','Shipping & Logistics','Packing and shipment planning for bulk plastic water bottle orders.',shipping),
 ('faq','FAQ','Frequently asked questions about B2B bottle purchasing.',faq_page),
 ('contact','Contact Us','Contact XUYI about plastic bottle wholesale, samples and OEM projects.',contact),
 ('blog','Blog','Plastic drinkware sourcing guides for brands and importers.',blog_index),
 ('privacy-policy','Privacy Policy','Preview of inquiry processing and business contact data protections.',privacy)
 ]:
  build_url(slug+'/index.html',title,page(title+' | XUYI Drinkware',description,fn()))
 build_url('why-us/index.html','Why Us',page('Why Work with XUYI Drinkware | Factory-backed Plastic Water Bottles','How XUYI supports custom bottle buyers, product development, quality and supply.',why_us()))
 build_url('request-sample/index.html','Request a Sample',page('Request a Plastic Water Bottle Sample | XUYI','Sample request steps for sports, kids, jug and shaker bottle models.',sample_page()))
 for row in FEATURES:
  slug,title,description,*rest=row
  build_url('features/'+slug+'/index.html',title,page(title+' | XUYI Drinkware',description,topic_page('features',row)))
 for row in APPLICATIONS:
  slug,title,description,*rest=row
  build_url('applications/'+slug+'/index.html',title,page(title+' | XUYI Drinkware',description,topic_page('applications',row)))
 for slug,title,desc in ARTICLES:
  build_url('blog/'+slug+'/index.html',title,page(title+' | XUYI Buying Guide',desc,blog_article(slug,title,desc)))
 build_url('404.html','404',page('Page Not Found | XUYI Drinkware','Page not found.',intro('404','Page Not Found','The requested page could not be found.')+'<section class="section"><div class="shell"><a class="button" href="/">Back to Homepage →</a></div></section>'))
 # A fully accurate domain and multilingual sitemap will be generated after domain verification, translation and product approval.
 write('robots.txt','User-agent: *\nDisallow: /\n')
 write('data/route-manifest.json',json.dumps([{'path':'/'+x.replace('index.html',''),'title':title} for x,title in sorted(URLS.items()) if x.endswith('index.html')],ensure_ascii=False,indent=2))
 print('BUILD_OK','HTML_FILES',len(URLS),'PRODUCT_PAGES',len(SERIES),'CAT_PAGES',len(CAT),'CAPABILITY_PAGES',len(CAPABILITIES),'ARTICLES',len(ARTICLES))
if __name__=='__main__':generate()
