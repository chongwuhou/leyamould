"""Evidence-based supplementary sections appended after D1-managed page bodies.

The original editable page remains authoritative. These distinct, verifiable
buyer resources are source-controlled additions, never D1 replacements.
"""
from site_renderer import e,SERIES

def quality():
 return """<section class="section quality-buyer-evidence"><div class="shell"><div class="section__head"><div><span class="eyebrow">SOURCE-CHECKED QUALITY GUIDANCE</span><h2 class="section__title">Which Quality Documents Actually Matter for Your Bottle?</h2><p>Reference the intended destination and exact material assembly. A regulatory reference does not certify an XUYI model.</p></div></div><div class="quality-reference-cards">
 <article><h3>United States: every contacting component counts</h3><p>FDA explains that the status of food-contact articles depends on the regulatory status of constituent substances and their intended conditions of use. Request separate specifications for the bottle body, cap, straw, seal and colorants.</p><a href="https://www.fda.gov/food/packaging-food-contact-substances-fcs/determining-regulatory-status-components-food-contact-material" target="_blank" rel="noopener noreferrer">FDA food-contact component guidance ↗</a></article>
 <article><h3>European Union: relevant legal text and documents</h3><p>EU plastic food-contact requirements include amendments under Regulation (EU) 2025/351; rules for BPA and other bisphenols are covered by Regulation (EU) 2024/3190, updated in 2026. Check the finished SKU, use conditions and applicable transitional provisions.</p><a href="https://eur-lex.europa.eu/eli/reg/2024/3190" target="_blank" rel="noopener noreferrer">EU Regulation 2024/3190 ↗</a><a href="https://eur-lex.europa.eu/eli/reg/2025/351/oj/eng" target="_blank" rel="noopener noreferrer">EU Regulation 2025/351 ↗</a></article>
 <article><h3>Sampling is not zero-defect certification</h3><p>ISO 2859-1:2026 describes schemes for lot-by-lot inspection by attributes. Agree lot definition, defect severity, inspection level, sample plan and actual lid / seal tests in writing. Never imply that citing ISO makes the factory certified.</p><a href="https://www.iso.org/cms/live/live/en/sites/isoorg/contents/data/standard/08/54/85464.html" target="_blank" rel="noopener noreferrer">ISO 2859-1:2026 overview ↗</a></article>
 </div><p class="quality-buyer-evidence__note">Independent primary sources, not test reports for XUYI products. Verify current legal applicability with the buyer's compliance team and obtain product-specific evidence.</p></div></section>"""

def manufacturing():
 return """<section class="section production-buyer-evidence"><div class="shell"><div class="section__head"><div><span class="eyebrow">PRODUCTION HANDOFF</span><h2 class="section__title">What to Approve Before Plastic Bottle Production</h2><p>Three different records should describe the same SKU, not a generic factory capability.</p></div></div><div class="grid grid--3">
 <article class="benefit"><h3>Part and Material Record</h3><p>List the body, lid, straw, flexible seal and contact materials for the exact finished bottle. Mark the material grade and purchase revision for each component.</p></article>
 <article class="benefit"><h3>Approved Sample and Artwork</h3><p>Keep the model photo, functional cap version, color master, print location, artwork revision and sample sign-off together. Identify changes requiring a new approval.</p></article>
 <article class="benefit"><h3>Packing and Inspection Release</h3><p>Record actual units per carton, measured dimensions and weight, outer labels, inspection checkpoints and shipment terms before booking freight.</p></article>
 </div><p class="production-buyer-evidence__note">Buyer-request checklist only: no unprovided equipment counts, capacity figures or passed inspections are claimed.</p><a class="button" href="/contact/#inquiry">Discuss This Production Brief →</a></div></section>"""

def about():
 examples=[("2501","550 mL sports bottle"),("2292","3,800 mL large jug"),("2508","600 mL kids bottle"),("501","500 mL shaker bottle")]
 cards=[]
 for model,title in examples:
  row=SERIES.get(model)
  if row:
   cards.append('<a class="rs-model-proof__card" href="/products/'+e(row["slug"])+'/"><span class="eyebrow">CATALOG MODEL '+e(model)+'</span><strong>'+e(title)+'</strong><span>Review model-specific source specifications ↗</span></a>')
 if len(cards)!=4:return ""
 return '<section class="rs-section rs-section--soft rs-model-proof-section"><div class="shell"><div class="rs-heading"><span class="eyebrow">XUYI SOURCE CATALOG</span><h2>Four Traceable Model References</h2><p>Examples from the company catalog, not claims about production volume, stock, certifications or exclusive factory ownership.</p></div><div class="rs-model-proof">'+''.join(cards)+'</div><p class="rs-model-proof__note">Confirm model/variant specification, manufacturing route and sample evidence with XUYI for each order.</p></div></section>'

ROUTES={"/about/":("rs-model-proof-section",about),
        "/manufacturing/":("production-buyer-evidence",manufacturing),
        "/quality-control/":("quality-buyer-evidence",quality)}

def for_route(route,main):
 item=ROUTES.get(route)
 if not item or item[0] in main:return ""
 return item[1]()
