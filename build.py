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
 hero='<section class="hero"><div class="hero__watermark" aria-hidden="true">XUYI</div><div class="hero__inner"><div class="hero__copy"><span class="eyebrow">CUSTOM PLASTIC BOTTLES · OEM & WHOLESALE</span><h1>Custom Water Bottles <span>Built for Your Brand.</span></h1><p>Explore plastic sports bottles, kids’ bottles, large water jugs and shakers from XUYI. Factory-backed supply, custom branding and practical wholesale support.</p><a class="button button--round" href="/products/">Explore Our Products →</a><p class="hero__note">Taizhou, China · Plastic drinkware · OEM/ODM inquiries</p></div><div class="hero__art">'+photo("/media/ppt/slide-059.webp","XUYI catalog gradient plastic sports water bottles","eager")+'</div><div class="hero__controls"><span>01</span> / 01</div></div></section>'
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
 return hero+cat+why+items+caps+fac+process+buyer+faq+blog
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
 for slug,title,desc in ARTICLES:
  build_url('blog/'+slug+'/index.html',title,page(title+' | XUYI Buying Guide',desc,blog_article(slug,title,desc)))
 build_url('404.html','404',page('Page Not Found | XUYI Drinkware','Page not found.',intro('404','Page Not Found','The requested page could not be found.')+'<section class="section"><div class="shell"><a class="button" href="/">Back to Homepage →</a></div></section>'))
 # A fully accurate domain and multilingual sitemap will be generated after domain verification, translation and product approval.
 write('robots.txt','User-agent: *\nDisallow: /\n')
 write('data/route-manifest.json',json.dumps([{'path':'/'+x.replace('index.html',''),'title':title} for x,title in sorted(URLS.items()) if x.endswith('index.html')],ensure_ascii=False,indent=2))
 print('BUILD_OK','HTML_FILES',len(URLS),'PRODUCT_PAGES',len(SERIES),'CAT_PAGES',len(CAT),'CAPABILITY_PAGES',len(CAPABILITIES),'ARTICLES',len(ARTICLES))
if __name__=='__main__':generate()
