"""Original XUYI homepage merchandising widgets; no external images or invented certifications."""
from site_renderer import e

def interactive_bottle_customization():
 return """<section class="custom-experience" id="custom-options">
 <div class="shell custom-experience__grid">
 <div class="custom-experience__intro"><span class="eyebrow">OEM · PRIVATE LABEL</span>
 <h2>Custom Unique Bottles <span>For Your Brand.</span></h2>
 <p>Start with an existing bottle model and tell us about your artwork, colors, lids and packing needs. We confirm options and requirements individually for each project.</p>
 <p class="custom-experience__hint">Interactive buying brief · reference photos only</p>
 <a href="/capabilities/" class="text-link">Explore All Customization Services →</a></div>
 <div class="custom-experience__preview"><div class="custom-experience__preview-ring"></div>
 <img id="configurator-photo" src="/media/excel/row-003.webp" alt="XUYI sports bottle reference model 2501" loading="lazy">
 <div class="custom-experience__photo-caption" id="configurator-model">Source catalog reference: Model 2501</div></div>
 <div class="custom-experience__choices"><div class="configurator__group"><strong>01 / BOTTLE TYPE</strong>
 <div class="configurator__choices" role="group" aria-label="Choose bottle product type">
 <button class="configurator__option active" type="button" data-config-kind="sports" aria-pressed="true">Sports</button>
 <button class="configurator__option" type="button" data-config-kind="kids" aria-pressed="false">Kids</button>
 <button class="configurator__option" type="button" data-config-kind="jug" aria-pressed="false">Jugs</button>
 <button class="configurator__option" type="button" data-config-kind="shaker" aria-pressed="false">Shakers</button></div></div>
 <div class="configurator__group"><strong>02 / PROJECT REQUIREMENTS</strong>
 <div class="configurator__choices" role="group" aria-label="Choose inquiry focus">
 <button class="configurator__option active" type="button" data-config-request="logo" aria-pressed="true">Logo</button>
 <button class="configurator__option" type="button" data-config-request="colors" aria-pressed="false">Colors</button>
 <button class="configurator__option" type="button" data-config-request="packaging" aria-pressed="false">Packaging</button></div></div>
 <p class="configurator__note">Options are enquiry preferences, not promises of availability. Feasibility, MOQ and material documentation are confirmed against the model.</p>
 <a id="configurator-cta" class="button button--round" href="/contact/?model=2501&amp;type=logo#inquiry">Customize This Bottle →</a>
 </div></div></section>"""

def dark_buyer_faq():
 qa=[
 ("Which plastics are used in your bottles?","Materials vary by product component. We verify the actual SKU and relevant destination-market requirements before making material or food-contact claims."),
 ("Do you offer samples before production?","Please give the model, destination and customization needs. We can then discuss sample availability, cost and shipping."),
 ("Can you make a custom bottle design?","We can review artwork, existing designs and the feasibility of new tooling or component changes. Each proposal needs technical confirmation."),
 ("Can I request custom colors or packaging?","Describe your brand colors, logo, labels and packaging. Feasibility depends on the selected model and order."),
 ("How do you handle factory quality checks?","XUYI has its own facility and may coordinate selected partners. We agree project-specific samples, specifications and checkpoints."),
 ]
 form='<div class="inquiry-preview"><span class="eyebrow">SEND YOUR PROJECT DETAILS</span><h2>Tell Us About<br>Your Bottle Project.</h2><div class="inquiry-preview__form"><div class="inquiry-preview__line">Company name</div><div class="inquiry-preview__line">Email address</div><div class="inquiry-preview__line">Bottle model or design</div><div class="inquiry-preview__line">Quantity and customization requirements</div><p>Inquiry submissions are currently disabled on this preview site. Verified contact details and secure delivery are pending.</p><a class="button" href="/contact/#inquiry">Prepare Your Inquiry →</a></div></div>'
 faqs='<div class="dark-faq"><span class="eyebrow">FREQUENTLY ASKED QUESTIONS</span><h2>We’re Here to Answer<br>All Your Questions.</h2>'+''.join('<details><summary>'+e(q)+'</summary><p>'+e(a)+'</p></details>' for q,a in qa)+'<p class="dark-faq__more"><a href="/faq/">See All Questions →</a></p></div>'
 return '<section class="dark-buyer-faq"><div class="shell dark-buyer-faq__grid">'+form+faqs+'</div></section>'

def company_strength_section():
 return """<section class="strengths section" id="why-xuyi"><div class="shell">
 <div class="strengths__top"><div><span class="eyebrow">OUR MANUFACTURING STRENGTHS</span><h2>Built Around Real Products.<br><span>Backed by a Manufacturing Team.</span></h2></div>
 <div><p>XUYI operates its own factory and coordinates selected partner production where required. For each approved project, we work from the actual bottle design, product specifications, branding and buyer requirements.</p>
 <a class="text-link" href="/manufacturing/">Explore Our Manufacturing Process →</a></div></div>
 <div class="strengths__body"><div class="strengths__visual"><img src="/media/ppt/slide-037.webp" alt="Original XUYI plastic water bottle catalog assortment" loading="lazy">
 <div class="strengths__visual-foot"><span>ORIGINAL XUYI BOTTLE CATALOG</span><strong>04<span>Focused Product Lines</span></strong></div></div>
 <div class="strengths__list">
 <a class="strengths__item" href="/manufacturing/"><span>01</span><div><h3>Our Own Production Facility</h3><p>Factory-backed operations, with selected production partners for some product styles. Each project’s manufacturing path is confirmed.</p></div><b>↗</b></a>
 <a class="strengths__item" href="/capabilities/oem-odm/"><span>02</span><div><h3>OEM &amp; Brand Customization</h3><p>Explore logo decoration, colors, packaging and potential product changes using real model references.</p></div><b>↗</b></a>
 <a class="strengths__item" href="/quality-control/"><span>03</span><div><h3>Specification &amp; Quality Review</h3><p>Confirm actual material components, samples, required documentation and agreed quality checkpoints.</p></div><b>↗</b></a>
 <a class="strengths__item" href="/shipping-logistics/"><span>04</span><div><h3>Order &amp; Delivery Coordination</h3><p>Plan model selection, carton packing, shipment details and project-specific delivery terms.</p></div><b>↗</b></a>
 </div></div>
 <p class="strengths__disclaimer">Production quantities, machinery images and certifications will be displayed after verification. Catalog photography is not presented as factory photography.</p>
 </div></section>"""

def customer_logo_section():
 import json
 from site_renderer import ROOT,photo,e
 file=ROOT/'data/customer-logos.json'
 entries=json.loads(file.read_text(encoding='utf-8')).get('group_brand_marks',[]) if file.exists() else []
 marks=[]
 for brand in entries:
  name=brand.get('name','').strip()
  logo=brand.get('logo_path','')
  auth=brand.get('authorization','')
  if not name or not logo.startswith('/assets/customer-logos/') or not auth or not (ROOT/logo.lstrip('/')).is_file():continue
  marks.append('<div class="client-logo__cell">'+photo(logo,name+' logo shown in the Kreat group website brand carousel','eager')+'</div>')
 if not marks:
  marks=['<div class="client-logo__cell client-logo__cell--pending">Brand images unavailable</div>']
 first='<div class="client-logo__set">'+''.join(marks)+'</div>'
 second='<div class="client-logo__set" aria-hidden="true">'+''.join(marks)+'</div>'
 html='<section class="client-logo section" id="customer-brands"><div class="shell"><div class="client-logo__heading"><div><span class="eyebrow">GROUP WEBSITE BRAND REFERENCES</span><h2>Brands &amp; Customers<span class="client-logo__red">.</span></h2></div><p>Brand marks presented in the Kreat group website carousel, displayed here with the original imagery and colors.</p></div><div class="client-logo__viewport" aria-label="Group website brand carousel"><div class="client-logo__track">'+first+second+'</div></div><p class="client-logo__note">Source: <a href="https://kreat.com/" target="_blank" rel="noopener noreferrer">Kreat group website</a>. Logos reproduce the group-site display, not evidence of a separate direct customer or endorsement relationship with XUYI.</p></div></section>'
 return html


def target_why_choose():
 # KREAT's position and layout: left statement and CTA, right OEM / ODM / quantity support.
 return """<section class="target-why"><div class="shell target-why__grid">
 <div class="target-why__intro"><span class="eyebrow">WHY XUYI</span><h2>Why Choose XUYI</h2>
 <p>XUYI supplies a focused range of plastic bottles for wholesale and custom projects. We operate our own facility and may coordinate selected partner production for specific designs. Bottle details, materials, samples and quality requirements are confirmed by project.</p>
 <a class="button button--round" href="/contact/#inquiry">Send Your Inquiry Now →</a></div>
 <div class="target-why__services">
 <article><h3>OEM Bottle Manufacturing</h3><p>Discuss production of your selected source model, custom branding, artwork and packing requirements.</p><a href="/capabilities/oem-odm/">Start Your Project ↗</a></article>
 <article><h3>ODM &amp; Design Support</h3><p>Share designs, requested lids or drawings for feasibility evaluation before making any tooling commitments.</p><a href="/capabilities/custom-molding/">Explore Custom Designs ↗</a></article>
 <article><h3>Wholesale Quantity Planning</h3><p>We review MOQ, samples, order size and packing by model. No fixed minimum is promised without confirmation.</p><a href="/contact/#inquiry">Request a Quote ↗</a></article>
 </div></div></section>"""

def target_production_capacity():
 # KREAT's placement: after material responsibility, before FAQ, with wide media/space on left
 # and manufacturing presentation on right. Do not invent numerical factory output.
 return """<section class="target-capacity" id="manufacturing-capability"><div class="shell target-capacity__layout">
 <div class="target-capacity__visual">
  <div class="target-capacity__media"><img src="/media/ppt/slide-049.webp" loading="lazy" alt="XUYI catalog plastic drinkware models">
  <span>ORIGINAL PRODUCT CATALOG IMAGE · NOT FACTORY FOOTAGE</span></div>
  <a href="/manufacturing/" class="target-capacity__media-link">Explore manufacturing process →</a>
 </div>
 <div class="target-capacity__copy">
  <span class="eyebrow">PRODUCTION &amp; QUALITY</span><h2>XUYI Manufacturing Capability</h2>
  <p>Our own facility supports our plastic drinkware business, while selected partner suppliers may support specific product types. We confirm the manufacturing route, samples, quality checks, packing and shipping requirements for each project.</p>
  <div class="target-capacity__facts">
   <article><strong>Own Factory</strong><span>Production facility in Taizhou</span></article>
   <article><strong>OEM / ODM</strong><span>Model-dependent options</span></article>
   <article><strong>Quality Checks</strong><span>Agreed for each order</span></article>
   <article><strong>Shipment</strong><span>Packing and logistics coordination</span></article>
  </div>
  <p class="target-capacity__note">Equipment counts, capacity, factory photos and certificates will be added only after document verification.</p>
 </div></div></section>"""
