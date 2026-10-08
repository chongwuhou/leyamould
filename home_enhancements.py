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
