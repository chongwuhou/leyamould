from site_renderer import *
from capability_editorial import CAPABILITY_DATA, render_capability, enrich_capability
from product_content import details as structured_product_details, add_schema as product_schema
from blog_editorial import cover_path, render_article, enrich_article_html
from why_us_layouts import render as render_why
from why_us_content import schema_enhance
WHY_DATA=json.loads((ROOT/"data/why-us-content.json").read_text(encoding="utf-8"))
from resource_pages import (faq_page as faq_expanded, about_page as about_expanded, why_us_page as why_us_expanded, sample_page as sample_expanded, capabilities_page as capabilities_expanded, schema_add as resources_schema, DATA as RESOURCE_DATA)
from home_enhancements import interactive_bottle_customization, dark_buyer_faq, company_strength_section, customer_logo_section, target_why_choose, target_production_capacity
import json
def sec(title,desc="",eyebrow="XUYI BOTTLES"):
 return render_template("section-heading",EYEBROW=e(eyebrow),TITLE=e(title),DESCRIPTION=e(desc))
def features():
 return '<div class="grid grid--4">'+''.join(render_template("product-benefit",HEADING=e(t),DESCRIPTION=e(d)) for t,d in [
 ("Factory-backed Supply","We operate our own manufacturing facility and coordinate additional products through selected production partners."),
 ("Custom Branding","Discuss logo artwork, product color, decoration method and brand packaging for compatible models."),
 ("Detailed Product Data","Ask us about capacity, size, material components and packing configuration for each selected model."),
 ("Order Coordination","One B2B inquiry process for product selection, quotation, sampling, quality checks and shipment.")
 ])+'</div>'
def steps():
 return '<div class="steps">'+''.join(render_template("process-step",NUMBER='0'+str(i),TITLE=e(t),DESCRIPTION=e(d)) for i,(t,d) in enumerate([
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
 hero=(
  '<section class="hero" data-hero aria-roledescription="carousel" aria-label="Featured XUYI bottle collections">'
  '<button class="hero__arrow hero__arrow--prev" data-hero-nav="-1" type="button" aria-label="Previous slide">‹</button>'
  '<div class="hero__watermark" aria-hidden="true">XUYI</div><div class="hero__inner">'
  '<div class="hero__copy"><span class="eyebrow">CUSTOM PLASTIC BOTTLES · OEM & WHOLESALE</span>'
  '<h1 id="hero-title">Custom Water Bottles <span>Built for Your Brand.</span></h1>'
  '<p id="hero-description">Explore sports, kids, large capacity and shaker bottles with factory-backed supply and project-specific branding options.</p>'
  '<a class="button button--round" id="hero-cta" href="/products/">Explore Our Products →</a>'
  '<p class="hero__note">Taizhou, China · Plastic drinkware · OEM/ODM inquiries</p></div>'
  '<div class="hero__art"><img src="/assets/curated-hd/gradient-sports.webp" id="hero-image" alt="XUYI colorful plastic water bottle collection" loading="eager" decoding="async"></div>'
  '<div class="hero__controls" role="group" aria-label="Select a banner slide">'
  '<button class="hero__dot active" data-hero-go="0" type="button" aria-label="Show slide 1 of 3" aria-pressed="true">01</button>'
  '<button class="hero__dot" data-hero-go="1" type="button" aria-label="Show slide 2 of 3" aria-pressed="false">02</button>'
  '<button class="hero__dot" data-hero-go="2" type="button" aria-label="Show slide 3 of 3" aria-pressed="false">03</button></div>'
  '<span class="sr-only" id="hero-status" role="status" aria-live="polite" aria-atomic="true"></span>'
  '</div><button class="hero__arrow hero__arrow--next" data-hero-nav="1" type="button" aria-label="Next slide">›</button></section>'
 )
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
 buyer='<section class="section"><div class="shell">'+sec("Built for Business Buyers","Product sourcing and customization for global trade.","Buyer Applications")+'<div class="grid grid--4">'+''.join(render_template("product-benefit",HEADING=e(t),DESCRIPTION=e(d)) for t,d in [("Importers","Select models and shipping configurations for your market."),("Wholesale Distributors","Browse reusable bottles by capacity, lid and material."),("Brands & Private Label","Explore custom logo, color and branded packaging options."),("Sports & Gift Buyers","Find sports, kids and shaker bottle designs for bulk projects.")])+'</div></div></section>'
 faq='<section class="section section--soft"><div class="shell">'+sec("Frequently Asked Questions","Answers to common questions from international purchasing teams.","FAQ")+faq_html(FAQS[:6])+'<p style="margin-top:25px"><a class="text-link" href="/faq/">Read All FAQs →</a></p></div></section>'
 blog=target_news_and_blogs()
 return hero+factory_intro_module()+bottle_collection_tabs()+new_drinkware_collections()+buyer_project_paths()+target_why_choose()+interactive_bottle_customization()+materials_responsibility_module()+target_production_capacity()+dark_buyer_faq()+customer_logo_section()+blog
def new_drinkware_collections():
 names=["Spray Water Bottles","Two-Way Drinking Cups","Titanium Vacuum Cups"]
 cards=''.join(category_card(CAT[name]) for name in names if any(item.get("category")==name for item in SERIES.values()))
 if not cards:return ""
 return '<section class="section section--soft"><div class="shell">'+sec("Additional Drinkware Collections","The latest factory catalog adds spray water bottles, two-way drinking cups and titanium vacuum cups. Review model-level specifications and confirm materials, variants and packaging before ordering.","NEW PRODUCT SERIES")+'<div class="grid grid--3">'+cards+'</div></div></section>'
def buyer_project_paths():
 options=[
  ("01","Browse Existing Models","Compare real catalog styles by capacity, shape, closure and intended market before requesting bulk pricing.","/products/","Explore Bottle Models →"),
  ("02","Plan Custom Branding","Share the bottle model, expected quantity, logo artwork, color references and packaging brief so we can review feasible options.","/capabilities/custom-logo/","Review Branding Options →"),
  ("03","Discuss Samples & Supply","Ask about a specific model and agree the sample, component materials, carton configuration and shipping destination before ordering.","/request-sample/","Plan a Sample Request →")
 ]
 cards=''.join('<a class="buyer-path" href="'+url+'"><span class="buyer-path__number">'+number+'</span><h3>'+e(title)+'</h3><p>'+e(desc)+'</p><span class="buyer-path__link">'+e(cta)+'</span></a>' for number,title,desc,url,cta in options)
 return '<section class="section buyer-paths-section"><div class="shell">'+sec("Start with Your Buying Requirements","Choose the shortest route from product selection to a model-specific wholesale inquiry.","WHOLESALE BUYER GUIDE")+'<div class="buyer-paths">'+cards+'</div></div></section>'
def catalog_buying_guide(category=None):
 guides={
  "Plastic Sports Water Bottles":[
   ("Compare Closure Styles","Ask whether the exact model uses a straw, flip-top or direct-drink lid, and confirm included parts."),
   ("Match Capacity & Handling","Compare the catalog-listed volume, overall dimensions, carry loop and target use."),
   ("Plan Your Branding","Provide artwork, target colors and quantity; printing positions and feasibility depend on the chosen bottle.")],
  "Large Capacity Water Jugs":[
   ("Consider Filled Handling","Review the actual jug capacity, handle arrangement, cap fit and balance when filled."),
   ("Confirm Outer Cartons","Ask for carton quantity, packing dimensions and delivery destination before comparing landed costs."),
   ("Specify the Exact Variant","Check the mouthpiece, straw or lid configuration, which may differ between catalog photographs."),
   ("Review Material and Closure","Confirm the body, cap and seal materials for the exact jug model.")],
  "Kids Plastic Water Bottles":[
   ("Check Intended Age & Market","Confirm the target market, intended age range and relevant product requirements for the finished SKU."),
   ("Review Removable Components","Ask about straw, gasket, cap and carrying-strap components and cleaning instructions."),
   ("Confirm Materials & Evidence","Request model-specific body/lid material details and any required food-contact or children's product documents.")],
  "Plastic Shaker Bottles":[
   ("Verify Mixing Accessories","Ask if the selected SKU includes a mixing ball, mesh insert or other accessory."),
   ("Compare Capacity & Markings","Check usable fill volume, lid design, measurement scale and cleaning access for the actual model."),
   ("Prepare an OEM Brief","Share your logo artwork, order volume, colors and carton requirements to confirm custom options.")],
  "Spray Water Bottles":[
   ("Check the Spray Assembly","Confirm the nozzle, trigger action, spray pattern and included components for the exact model."),
   ("Review Seals and Cleaning","Check cap seals, internal tubes and cleaning access; request a sample before making leakage claims."),
   ("Confirm Branding and Packing","Verify decoration area, spare parts, carton quantity and retail packaging for the selected SKU.")],
  "Two-Way Drinking Cups":[
   ("Verify Both Drinking Modes","Confirm the two drinking options and the lid assembly supplied with the exact model."),
   ("Review Seal and Cleaning","Check removable parts, seals and cleaning access; test a sample before making leak-resistance claims."),
   ("Confirm Materials and Performance","Request the exact body/lid material details and any relevant thermal-performance evidence.")],
  "Titanium Vacuum Cups":[
   ("Verify Titanium Grade","Request grade and composition documents for the exact SKU; do not rely on a series-level purity statement alone."),
   ("Check Vacuum Construction","Confirm capacity, vacuum structure and the thermal test method for the selected model."),
   ("Review Finish and Packing","Approve surface finish, lid components, protective packaging and carton details against a sample.")]
  }
 rows=guides.get(category) if category else [
  ("Find Your Product Family","Explore sports bottles, large-capacity jugs, shaker bottles, spray bottles, two-way cups and titanium vacuum cups."),
  ("Identify the Exact Model","Use the model number to verify catalog-listed capacity, lid design, materials, dimensions and matching product images."),
  ("Request a Comparable Quote","Include expected quantity, destination, customization and packaging so different options can be assessed.")]
 cards=''.join(render_template("product-benefit",HEADING=e(title),DESCRIPTION=e(desc)) for title,desc in rows)
 return '<section class="section section--soft catalog-buyer-guide"><div class="shell">'+sec("How to Choose Before You Order","These are buying checkpoints, not claims that every model has the same features or approvals.","B2B SOURCING NOTES")+'<div class="grid grid--3">'+cards+'</div><p class="catalog-buyer-guide__cta"><a class="button" href="/contact/#inquiry">Send Your Model & Requirements →</a><a class="text-link" href="/faq/">Read Wholesale Buying FAQs →</a></p></div></section>'
def catalog(cat_name=None):
 if cat_name:
  title,slug,im,desc=CAT[cat_name]
  arr=[x for x in SERIES.values() if x["category"]==cat_name]
  arr.sort(key=lambda item:item.get("sourceDocument")!="puyunsm(1).pdf")
  heading=title;subtitle=desc+' Explore model-specific specifications, colors and wholesale quotation options.'
 else:
  arr=list(SERIES.values())
  arr.sort(key=lambda item:item.get("sourceDocument")!="puyunsm(1).pdf");heading="Explore All Drinkware Products";subtitle="Browse sports water bottles, large-capacity jugs, shaker bottles, spray bottles, two-way drinking cups and titanium vacuum cups."
 pagehtml=intro("Products" if not cat_name else "Products / "+CAT[cat_name][0],heading,subtitle)
 pagehtml+='<section class="section"><div class="shell"><div class="catalog-layout">'+catnav(CAT[cat_name][1] if cat_name else None)+'<div>'+filters(not cat_name)+product_grid(arr)+pagination(len(arr) if not cat_name else None)+'</div></div></div></section>'
 pagehtml+=catalog_buying_guide(cat_name)
 if cat_name=="Plastic Shaker Bottles":
  # Source-authored, model-verified wholesale guidance; never patch dist HTML.
  from shaker_category_editorial import render as shaker_wholesale_editorial
  pagehtml+=shaker_wholesale_editorial()
 pagehtml+='<section class="section section--soft"><div class="shell">'+sec("Wholesale & Custom Bottle Solutions","Ask about available colors, custom printing, branding and packing for the models that interest you.","OEM & CUSTOMIZATION")+features()+'</div></section>'
 pagehtml+='<section class="section"><div class="shell">'+sec("Wholesale Buying Questions","Contact XUYI with model number, quantity and destination.","Product FAQ")+faq_html(FAQS[:6])+'</div></section>'
 return pagehtml
def detail(obj):
 if obj.get("loNew"):
  from lo_catalog import detail as lo_detail
  return lo_detail(obj,"en")
 if obj.get("galleryReference"):
  from gallery_catalog import detail as gallery_detail
  return gallery_detail(obj,"en")
 return structured_product_details(obj)

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
 return capabilities_expanded()

def capability_detail(item):
 title,slug,desc,stepslist,im=item
 if slug=="oem-odm":return render_why(WHY_DATA["capabilities/oem-odm"])
 if slug in CAPABILITY_DATA:return render_capability(slug)
 h=intro("Capabilities / "+title,title,desc)
 h+='<section class="section"><div class="shell"><div class="split"><div>'+photo(im,title+' source catalog imagery')+'</div><div><span class="eyebrow">BRAND & MANUFACTURING SERVICES</span><h2 class="section__title">Plan Your '+e(title)+' Project.</h2><p class="copy-muted">'+e(desc)+'</p><p class="copy-muted">Actual techniques, order quantity and testing depend on the selected bottle and materials. XUYI will confirm feasibility when preparing a quotation.</p><a href="/contact/?type='+slug+'#inquiry" class="button">Discuss This Service →</a></div></div></div></section>'
 h+='<section class="section section--soft"><div class="shell">'+sec("What We Need from Buyers","A clear brief helps us check the correct manufacturing and custom options.","Project Checklist")+'<div class="grid grid--4">'+''.join('<article class="benefit"><h3>0'+str(i+1)+' · '+e(t.split(' ')[0])+'</h3><p>'+e(t)+'</p></article>' for i,t in enumerate(stepslist))+'</div></div></section>'
 h+='<section class="section"><div class="shell">'+sec("Explore Related Capabilities","Combine products, branding and packaging requirements in one inquiry.","Explore More")+'<div class="grid grid--3">'+''.join('<article class="article-card"><h3>'+e(t)+'</h3><p>'+e(d)+'</p><a href="/capabilities/'+sid+'/">Learn More →</a></article>' for t,sid,d,*_ in CAPABILITIES if sid!=slug)+'</div></div></section>'
 h+='<section class="section section--soft"><div class="shell">'+sec("Questions About Custom Orders","Common questions from international importers.","FAQ")+faq_html(FAQS[:6])+'</div></section>'
 return h
def about():
 return about_expanded()

def manufacturing():
 return render_why(WHY_DATA["manufacturing"])

def quality():
 return render_why(WHY_DATA["quality-control"])

def shipping():
 return render_why(WHY_DATA["shipping-logistics"])

def faq_page():
 return faq_expanded()

def contact():
 h=intro("Contact Us","Contact XUYI Bottles","Bulk plastic bottle sourcing, OEM/ODM projects, custom branding and samples.")
 h+='<section class="section"><div class="shell"><div class="contact-layout"><div><span class="eyebrow">BUSINESS ENQUIRIES</span><h2 class="section__title">Let’s Talk About Your Project.</h2><p class="copy-muted">Tell us the model, material, quantity, desired customization and destination market.</p><div class="benefit"><h3>What to include</h3><p>Model or photo, capacity, preferred PC / Tritan / PP / PETG material, BPA-free requirements, logo, quantity and shipping details.</p></div><div class="benefit"><h3>Company</h3><p>台州市旭一家居用品有限公司<br>Taizhou, Zhejiang, China</p><p><a data-site-email href="mailto:Janey@xuyibottles.com">Janey@xuyibottles.com</a></p><p><a data-site-whatsapp data-site-whatsapp-number href="https://wa.me/8615395897937" target="_blank" rel="noopener noreferrer">WhatsApp: '+e(whatsapp_display_number())+' · Chat →</a></p></div></div>' + render_template("contact-form") + '</div></div></section>'
 return h

# Illustrations use XUYI's own approved product imagery.
def news_cover(slug,title,alt_suffix=""):
 return photo(cover_path(slug),title+" | XUYI bottle sourcing guide"+alt_suffix,aspect_ratio="4/3")

# Keep the homepage's eight editorial slots intentionally curated. New blog
# posts still appear first on /blog/, but must not silently replace approved
# homepage imagery each time the editorial catalog grows.
HOME_ARTICLE_SLUGS = [
 "replacement-water-bottle-lids-bulk",
 "water-bottle-capacity-sizes-wholesale",
 "water-bottle-sample-approval-checklist",
 "bottle-factory-rfq-template",
 "water-bottle-cap-types-bulk-guide",
 "tritan-bottle-yellowing-causes-prevention",
 "sports-water-bottle-customization",
 "water-bottle-logo-printing-methods",
]
HOME_ARTICLES = [next(item for item in ARTICLES if item[0] == slug) for slug in HOME_ARTICLE_SLUGS]

def target_news_and_blogs():
 intro='<section class="news-section" id="news-and-blogs" aria-labelledby="news-title"><div class="shell">'
 intro+='<div class="news-section__head"><h2 id="news-title">News <span class="news-section__symbol" aria-hidden="true"><svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg"><rect width="64" height="64" rx="32" fill="#f31927"/><g transform="rotate(11 32 32)"><rect x="17" y="13" width="32" height="39" rx="2" fill="#fff"/><rect x="21" y="19" width="23" height="5" fill="#1d1d1d"/><path stroke="#8d8d8d" stroke-width="2" d="M21 29h23M21 34h23M21 39h23M21 44h17"/></g></svg></span> and Blogs</h2><p>Discover helpful plastic bottle buying guides on materials, customization, lid styles and wholesale sourcing. Compare options and plan your next brand project.</p></div>'
 intro+='<div class="news-section__layout"><div class="news-section__aside"><div class="news-section__counter" aria-live="polite"><strong id="news-active-count">01</strong><span>/ '+str(len(HOME_ARTICLES[:8])).zfill(2)+'</span></div><div class="news-section__label">Buying Guides<br>&amp; Resources</div><div class="news-section__arrows"><button type="button" id="news-prev" aria-label="Previous article" disabled>←</button><button type="button" id="news-next" aria-label="Next article">→</button></div><a class="news-section__all" href="/blog/">View All Articles ↗</a></div><div class="news-section__slider" aria-label="Featured XUYI buying guides" id="news-slider" tabindex="0">'
 for slug,title,desc in HOME_ARTICLES[:8]:
  intro+='<article class="news-card"><a href="/blog/'+e(slug)+'/" class="news-card__image">'+news_cover(slug,title)+'</a><div class="news-card__info"><span class="news-card__category">BUYING GUIDE</span><h3><a href="/blog/'+e(slug)+'/">'+e(title)+'</a></h3><p>'+e(desc)+'</p><a class="news-card__read" href="/blog/'+e(slug)+'/">Read Article →</a></div></article>'
 intro+='</div></div></div></section>'
 return intro

def blog_index():
 h=intro("Blog","Water Bottle Buying Guides","Practical plastic water bottle buying guides for material selection, customization, quality control and wholesale procurement.")
 # The page intro is the single Blog listing heading; render cards below it.
 h+='<section class="section blog-listing"><div class="shell">'
 h+='<div class="blog-listing__grid">'
 for slug,title,description in ARTICLES:
  post=BLOG_POSTS[slug]
  h+='<article class="news-card"><a class="news-card__image" href="/blog/'+e(slug)+'/">'+news_cover(slug,title)+'</a><div class="news-card__info"><span class="news-card__category">'+e(post["group"]).upper()+'</span><h3><a href="/blog/'+e(slug)+'/">'+e(title)+'</a></h3><p>'+e(description)+'</p><a class="news-card__read" href="/blog/'+e(slug)+'/">Read Article →</a></div></article>'
 h+='</div></div></section>'
 return h

def blog_article(slug,title,desc):
 return render_article(slug)

def privacy():
 h=intro("Privacy Policy","Privacy & Inquiry Data","How XUYI handles business enquiries and contact details.")
 h+='<section class="section"><div class="shell"><article class="article"><p>台州市旭一家居用品有限公司 (XUYI Bottles) uses your contact details, company information, bottle models, expected quantities and requirements to respond to enquiries and prepare quotations or sample proposals.</p><h2>Business enquiries</h2><p>When submitted through the online form, enquiry data is stored with Cloudflare D1 and may be forwarded to the designated sales representative. We may process limited technical data for protection from spam and abuse.</p><h2>Data management</h2><p>Access is limited to authorized personnel. Retention is based on relevant business needs and applicable laws. You may request correction or deletion, subject to legal obligations.</p><h2>Contact</h2><p>Contact <a data-site-email href="mailto:Janey@xuyibottles.com">Janey@xuyibottles.com</a> for privacy questions and data requests.</p></article></div></section>'
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
 from why_us_source import augment
 return augment(why_us_expanded(),"en")

def sample_page():
 return sample_expanded()

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
 # KREAT ordering: concise heading, compact category navigation, two rows of four square cards.
 from pathlib import Path
 import hashlib
 names=[
  ("Sports Water Bottles","Plastic Sports Water Bottles"),
  ("Kids Water Bottles","Kids Plastic Water Bottles"),
  ("Large Capacity Jugs","Large Capacity Water Jugs"),
  ("Shaker Bottles","Plastic Shaker Bottles")
 ]
 def curated(category):
  values=[v for v in SERIES.values() if v["category"]==category]
  chosen=[];seen=set();spare=[]
  for item in values:
   path=item["images"][0]
   file=ROOT/('assets/catalog/excel/'+Path(path).name if path.startswith('/media/excel/') else '_local_ops/ppt-media-staging/'+Path(path).name)
   digest=hashlib.sha256(file.read_bytes()).hexdigest() if file.exists() else path
   if digest not in seen:
    chosen.append(item);seen.add(digest)
   else:spare.append(item)
  return (chosen+spare)[:8]
 content='<section class="kreat-collections" id="product-collections"><div class="shell">'
 content+='<div class="kreat-collections__heading"><span class="eyebrow">PLASTIC DRINKWARE · SOURCE CATALOG</span><h2>Explore Plastic Bottles <span>for Your Market</span></h2><p>Compare sports, kids, large-capacity and shaker bottle models. Open any model to review its catalog details and request a product-specific wholesale quote.</p></div>'
 content+='<div class="kreat-collections__tabs" role="tablist" aria-label="Browse plastic bottle collections">'
 for i,(name,cat) in enumerate(names):
  content+='<button type="button" class="bottle-tab kreat-collections__tab'+(' active' if i==0 else '')+'" role="tab" id="bottle-tab-'+str(i)+'" aria-controls="bottle-panel-'+str(i)+'" aria-selected="'+('true' if i==0 else 'false')+'">'+e(name)+'</button>'
 content+='</div>'
 for i,(name,category) in enumerate(names):
  products=curated(category)
  content+='<div class="bottle-tabpanel" role="tabpanel" id="bottle-panel-'+str(i)+'" aria-labelledby="bottle-tab-'+str(i)+'"'+(' hidden' if i else '')+'>'
  content+='<div class="kreat-collections__grid">'
  for item in products:
   content+='<a class="kreat-collections__item" href="/products/'+e(item["slug"])+'/"><span class="kreat-collections__photo">'+photo(item["images"][0],item["name"]+' Model '+item["model"])+'</span><strong>'+e(item["name"])+'</strong><span class="kreat-collections__model">Model '+e(item["model"])+'</span></a>'
  if len(products)<8:
   img=CAT[category][2]
   content+='<a class="kreat-collections__item kreat-collections__item--more" href="/collections/'+CAT[category][1]+'/"><span class="kreat-collections__photo">'+photo(img,'Explore more '+name)+'</span><strong>Explore More '+e(name)+'</strong><span class="kreat-collections__model">View all products →</span></a>'
  content+='</div><div class="kreat-collections__more"><a href="/collections/'+CAT[category][1]+'/" class="text-link">View All '+e(name)+' →</a></div></div>'
 content+='</div></section>'
 return content

def materials_responsibility_module():
 return '<section class="section section--dark"><div class="shell"><div class="split"><div><span class="eyebrow">MATERIAL RESPONSIBILITY</span><h2 class="section__title">Better Reusable Bottle Projects Start with the Right Material.</h2><p class="copy-muted">Our source catalog lists PC and PP combinations on selected bottles. Body, lid, straw and gasket materials may differ. Tell us the exact model and destination market so the component specifications and any additional resin or food-contact requirements can be checked.</p><div class="material-options"><span>PC · Catalog Reference</span><span>PP · Catalog Reference</span><span>Component-Level Review</span><span class="bpa">Testing Upon Verification</span></div><div class="actions"><a class="button button--white" href="/quality-control/">Quality & Material Guidance →</a><a class="button button--outline" href="/blog/plastic-bottle-material-selection/">Read Material Guide ↗</a></div><p class="copy-muted" style="font-size:12px">Tritan, PETG, BPA-free and market-specific compliance claims must be confirmed for the actual model and materials; they are not assumed from a catalog photograph.</p></div><div class="responsible-media">'+photo('/media/ppt/slide-066.webp','Reusable plastic drinking bottles from the original XUYI catalog')+'<div class="responsible-media__caption"><b>Reusable plastic drinkware</b><span>Review materials by model and component</span></div></div></div></div></section>'

def production_capability_module():
 points=[
 ("Own Facility","XUYI operates a Taizhou manufacturing facility for its plastic drinkware business."),
 ("Project Matching","Select the model and identify whether work is handled in-house or by an approved partner."),
 ("Sample Confirmation","Document fit, finish, closures, sample acceptance and artwork before full production."),
 ("Quality & Dispatch","Review agreed checkpoints, packaging, cartons and shipment requirements.")
 ]
 cards=''.join('<article class="production-proof"><span class="production-proof__num">0'+str(i)+'</span><h3>'+e(title)+'</h3><p>'+e(desc)+'</p></article>' for i,(title,desc) in enumerate(points,1))
 return '<section class="section production-capacity"><div class="shell"><div class="section__head"><div><span class="eyebrow">MANUFACTURING SUPPORT</span><h2 class="section__title">XUYI Production & Order Capabilities.</h2><p class="copy-muted">Project-specific manufacturing, production and shipment information. Machine counts and output figures will be shown only after factory verification.</p></div><a class="text-link" href="/manufacturing/">Explore Our Process →</a></div><div class="production-proof-grid">'+cards+'</div><div class="production-footer"><p>Need a custom color, print or packaging design? Send your actual model, artwork, order quantity and destination.</p><a class="button" href="/request-sample/">Discuss a Sample →</a></div></div></section>'

RESOURCE_SEO={
 'faq':('Wholesale Plastic Bottle FAQ: MOQ & OEM | XUYI','Answers to 54 wholesale plastic bottle questions covering MOQ, custom logos, component materials, samples, inspection, cartons, shipping and reorders.'),
 'about':('About XUYI | Taizhou Plastic Water Bottle Supplier','Meet XUYI in Taizhou, China. Explore the original plastic sports, kids, jug and shaker bottle catalog, sourcing approach and manufacturing coordination.'),
 'why-us':('Why Choose XUYI for Wholesale Plastic Bottles | Factory & OEM','Explore the buyer support, sourcing workflow, group factory references, brand customization, quality review and logistics behind XUYI plastic drinkware.'),
 'request-sample':('Plastic Water Bottle Sample Request Guide | XUYI Bottles','Learn how to request plastic bottle samples, approve logo artwork, compare prototypes, review components and prepare for wholesale production.'),
 'capabilities':('Custom Plastic Water Bottle OEM & Branding | XUYI','Explore custom logo printing, lid and color options, OEM bottle development and custom packaging. Feasibility is confirmed by model and order brief.')
}

def generate():
 build_url('index.html','Homepage',page('Custom Plastic Water Bottle Manufacturer in China | XUYI Bottles','Factory-backed plastic sports, kids and shaker bottles for wholesale and OEM/ODM sourcing.',front()))
 build_url('products/index.html','All Products',page('Plastic Water Bottle Catalog | XUYI Bottles','Explore plastic sports water bottles, large capacity water jugs, kids bottles and shaker bottles.',catalog()))
 for cat,(title,slug,im,desc) in CAT.items():
  build_url('collections/'+slug+'/index.html',title,page(title+' Wholesale | XUYI Bottles',desc,catalog(cat)))
 for product in SERIES.values():
  model=str(product['model'])
  public_name=public_display_name(product)
  # Every real model has its own SEO title and description, as in Demalong's
  # evidence-backed model pages. Do not invent MOQ, certification or capacity.
  # Some catalog names already end in Model N: never append N twice.
  existing_model=public_name.casefold().endswith(('model '+model).casefold())
  seo_name=public_name if existing_model else public_name+' — Model '+model
  description_name=public_name if existing_model else public_name+' model '+model
  if product.get("loNew"):
   from lo_catalog import LO_PRODUCTS
   meta=next(row["locales"]["en"] for row in LO_PRODUCTS if row["model"]==model)
   seo_name,seo_desc=meta["seoTitle"],meta["seoDescription"]
  elif product.get("galleryReference"):
   # Factory G-series identifier is a concise differentiator; a long
   # generic prefix adds no buyer value and gets truncated in search.
   seo_name=(public_name+" | "+model+" | XUYI")
   if len(seo_name)>60:
    seo_name=("Gradient Sports Bottle " if "Gradient" in public_name else "Plastic Sports Bottle ")+model+" | XUYI"
   seo_desc="Explore XUYI G-series factory model "+model+": "+public_name+". Confirm capacity, material, components and packing for the exact model before placing a wholesale order."
  elif product.get("manualNew"):
   seo_name=product.get("seoTitle") or (seo_name+' | XUYI Bottles')
   seo_desc=product.get("seoDescription") or (description_name+': compare catalog specifications, material, color and packing options; request a product-specific wholesale quotation.')
  else:
   seo_name=seo_name+' | XUYI Bottles'
   seo_desc=description_name+': compare catalog specifications, material, color and packing options; request a product-specific wholesale quotation.'
  product_markup=page(seo_name,seo_desc,detail(product))
  build_url('products/'+product['slug']+'/index.html','Model '+product['slug'],product_schema(product_markup,product))
 build_url('capabilities/index.html','Capabilities',resources_schema(page(*RESOURCE_SEO['capabilities'],capabilities_page()),'capabilities',RESOURCE_SEO['capabilities'][1]))
 for cap in CAPABILITIES:
  title,slug,desc,*_=cap
  cap_markup=page((WHY_DATA["capabilities/oem-odm"]["seo_title"] if slug=="oem-odm" else title+' | XUYI Bottles'),(WHY_DATA["capabilities/oem-odm"]["description"] if slug=="oem-odm" else desc),capability_detail(cap))
  if slug=="oem-odm":cap_markup=schema_enhance(cap_markup,WHY_DATA["capabilities/oem-odm"])
  elif slug in CAPABILITY_DATA:
   cap_markup=page(CAPABILITY_DATA[slug]["title"]+' | XUYI Bottles',CAPABILITY_DATA[slug]["lead"],capability_detail(cap))
   cap_markup=enrich_capability(cap_markup,slug)
  build_url('capabilities/'+slug+'/index.html',title,cap_markup)
 for slug,title,description,fn in [
 ('about','About', 'Learn about XUYI’s factory-backed plastic water bottle business.',about),
 ('manufacturing','Manufacturing','Our factory and selected partner supply process for plastic drinkware.',manufacturing),
 ('quality-control','Quality Control','Quality checks and documentation for plastic water bottle sourcing.',quality),
 ('shipping-logistics','Shipping & Logistics','Packing and shipment planning for bulk plastic water bottle orders.',shipping),
 ('faq','FAQ','Frequently asked questions about B2B bottle purchasing.',faq_page),
 ('contact','Contact Us','Contact XUYI about plastic bottle wholesale, samples and OEM projects.',contact),
 ('blog','Blog','Plastic drinkware sourcing guides for brands and importers.',blog_index),
 ('privacy-policy','Privacy Policy','Privacy practices for business enquiries and customer contact information.',privacy)
 ]:
  if slug in ("manufacturing","quality-control","shipping-logistics"):
   data=WHY_DATA[slug]
   body_markup=schema_enhance(page(data["seo_title"],data["description"],fn()),data)
  elif slug in ('faq','about'):
   meta=RESOURCE_SEO[slug]
   body_markup=resources_schema(page(meta[0],meta[1],fn()),slug,meta[1],RESOURCE_DATA['categories'] if slug=='faq' else None)
  else:
   body_markup=page(title+' | XUYI Bottles',description,fn(),blog_pager=(slug=="blog"))
  build_url(slug+'/index.html',title,body_markup)
 build_url('why-us/index.html','Why Us',resources_schema(page(*RESOURCE_SEO['why-us'],why_us()),'why-us',RESOURCE_SEO['why-us'][1]))
 build_url('request-sample/index.html','Request a Sample',resources_schema(page(*RESOURCE_SEO['request-sample'],sample_page()),'request-sample',RESOURCE_SEO['request-sample'][1],[c for c in RESOURCE_DATA['categories'] if c['id']=='samples']))
 for row in FEATURES:
  slug,title,description,*rest=row
  build_url('features/'+slug+'/index.html',title,page(title+' | XUYI Bottles',description,topic_page('features',row)))
 for row in APPLICATIONS:
  slug,title,description,*rest=row
  build_url('applications/'+slug+'/index.html',title,page(title+' | XUYI Bottles',description,topic_page('applications',row)))
 for slug,title,desc in ARTICLES:
  article_html=page(title,desc,blog_article(slug,title,desc))
  build_url('blog/'+slug+'/index.html',title,enrich_article_html(article_html,slug))
 notfound=page('Page Not Found | XUYI Bottles','Page not found.',intro('404','Page Not Found','The requested page could not be found.')+'<section class="section"><div class="shell"><a class="button" href="/">Back to Homepage →</a></div></section>')
 notfound=notfound.replace('<meta name="robots" content="index,follow">','<meta name="robots" content="noindex,follow">',1)
 build_url('404.html','404',notfound)
 # A fully accurate domain and multilingual sitemap will be generated after domain verification, translation and product approval.
 if INDEXING_APPROVED:
  # Never publish a public indexed site while robots.txt still blocks crawling.
  # /admin/ stays out of search; its authorization gate is independent.
  write('robots.txt','User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: '+SITE_ORIGIN+'/sitemap.xml\n')
 else:
  write('robots.txt','User-agent: *\nDisallow: /\n')
 # Maintain the current English URL inventory even while indexing is withheld.
 # This stays ready for the later approved SEO launch without publishing
 # unreviewed multilingual paths.
 sitemap=['<?xml version="1.0" encoding="utf-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
 from sitemap_modification import source_lastmod,review_change_dates
 from product_image_sitemap import xml_image_for_product
 reviewed_date_changes=review_change_dates(SERIES,BUILD_STATE.get("productReviews",[]))
 for file_path in sorted(path for path in URLS if path.endswith('index.html')):
  route='/'+file_path[:-len('index.html')]
  lastmod=source_lastmod(route,'en',next((x for x in BUILD_STATE.get('pages',[]) if x.get('route')==route),None),
                         review_dates=reviewed_date_changes)
  # Published canonical main image is selected from the shared catalog
  # and the active D1 product/page body, not a guessed filename or R2 rename.
  body_owner=BODY_OVERRIDES.get(route) if route in BODY_OVERRIDES else None
  image_xml=xml_image_for_product(route,SERIES,body_owner,SITE_ORIGIN)
  sitemap.append(' <url><loc>'+e(SITE_ORIGIN+route)+'</loc>'
                 +('<lastmod>'+e(lastmod)+'</lastmod>' if lastmod else '')
                 +image_xml+'</url>')
 sitemap.append('</urlset>')
 write('sitemap.xml','\n'.join(sitemap)+'\n')
 write('data/route-manifest.json',json.dumps([{'path':'/'+x.replace('index.html',''),'title':title} for x,title in sorted(URLS.items()) if x.endswith('index.html')],ensure_ascii=False,indent=2))
 print('BUILD_OK','HTML_FILES',len(URLS),'PRODUCT_PAGES',len(SERIES),'CAT_PAGES',len(CAT),'CAPABILITY_PAGES',len(CAPABILITIES),'ARTICLES',len(ARTICLES))
if __name__=='__main__':generate()