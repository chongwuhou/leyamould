"""Six distinctly structured, service-specific continuation areas for XUYI."""
from site_renderer import e,photo,SERIES

def product_link(model,label,note):
    item=SERIES[model]
    picture=item["images"][0]
    return ('<a class="svc-model" href="/products/'+e(item["slug"])+'/">'
            +photo(picture,"XUYI bottle model "+model)
            +'<span class="svc-model__text"><strong>'+e(label)+'</strong><small>MODEL '+e(model)+'</small>'
            +'<span>'+e(note)+'</span></span><span aria-hidden="true" class="svc-model__arrow">↗</span></a>')

def link(url,title):
    return '<a href="'+e(url)+'">'+e(title)+' <span aria-hidden="true">↗</span></a>'

def faqs(data,style="open",title=""):
    h='<section class="section svc-questions svc-questions--'+e(style)+'"><div class="shell">'
    h+='<div class="section__head"><div><span class="eyebrow">BUYER QUESTIONS</span><h2 class="section__title">'+e(title)+'</h2></div></div>'
    h+='<div class="svc-questions__grid">'
    for n,item in enumerate(data["faqs"],1):
        if style in ("numbered","tiles"):
            h+='<article class="svc-answer"><div class="svc-answer__num">'+str(n).zfill(2)+'</div><h3>'+e(item["question"])+'</h3><p>'+e(item["answer"])+'</p></article>'
        else:
            h+='<details class="svc-answer"><summary>'+e(item["question"])+'</summary><p>'+e(item["answer"])+'</p></details>'
    return h+'</div></div></section>'

def resources(title,items,intro="",style="strip"):
    h='<section class="section svc-reading svc-reading--'+e(style)+'"><div class="shell"><div class="section__head"><div>'
    h+='<span class="eyebrow">TECHNICAL READING</span><h2 class="section__title">'+e(title)+'</h2>'
    if intro:h+='<p>'+e(intro)+'</p>'
    h+='</div></div><div class="svc-reading__items">'
    for label,url,summary in items:
        h+='<a href="'+e(url)+'"><span><strong>'+e(label)+'</strong><small>'+e(summary)+'</small></span><span aria-hidden="true">↗</span></a>'
    return h+'</div></div></section>'

def custom_water_bottle(d):
    h='<section class="section svc-models"><div class="shell"><div class="section__head"><div><span class="eyebrow">CHOOSE A STARTING SKU</span>'
    h+='<h2 class="section__title">Three Bottle Formats to Discuss with Your Buyer</h2><p>These are model references, not claims that every shape or material is interchangeable.</p></div></div><div class="svc-models__grid">'
    h+=product_link("2095","500 mL Sports Bottle","Compact capacity for branded everyday collections; confirm current color and material options.")
    h+=product_link("5299","550 mL Gradient Bottle","A visual reference for color-led retail ranges; sample the final graphic and lid together.")
    h+=product_link("2501","550 mL Catalog Style","Use the existing body and cap as an initial reference before changing decoration.")
    h+='</div></div></section>'
    h+=faqs(d,"open","Private-Label Decisions, Answered")
    h+='<section class="section section--soft svc-next"><div class="shell"><div class="section__head"><div><span class="eyebrow">BUILD YOUR PRODUCT LINE</span><h2 class="section__title">Three Customization Decisions After Model Selection</h2></div></div><div class="svc-next__three">'
    for number,title,desc,url in [
        ("01","Choose a decoration method","Set the logo area, artwork version and actual substrate before choosing a print method.","/capabilities/custom-logo/"),
        ("02","Approve the finished color","Compare a molded color and a decorated sample; keep a signed physical reference.","/capabilities/custom-graphics/"),
        ("03","Define the retail pack","The cap and accessories must fit the box and the carton quote.","/capabilities/custom-packaging/")]:
        h+='<article><span>'+number+'</span><h3>'+title+'</h3><p>'+desc+'</p>'+link(url,"Review this capability")+'</article>'
    h+='</div></div></section>'
    h+=resources("Private-Label Procurement Toolkit",[
        ("Wholesale Bottle Buying Guide","/blog/wholesale-plastic-water-bottle-buying-guide/","Build a model-specific sourcing and quotation checklist."),
        ("Select the Right Plastic","/blog/plastic-bottle-material-selection/","Compare component materials and intended use.")
    ],style="strip")
    return h

def custom_molding(d):
    h='<section class="section svc-decision"><div class="shell"><div class="section__head"><div><span class="eyebrow">TOOLING DECISION</span><h2 class="section__title">Does Your Design Really Need a New Mold?</h2><p>One of the most expensive purchasing mistakes is commissioning tooling for a change that existing components can support.</p></div></div>'
    h+='<div class="svc-decision__table"><div class="svc-decision__row svc-decision__row--head"><strong>Requested change</strong><strong>Likely route to evaluate</strong><strong>What the factory needs</strong></div>'
    for left,middle,right in [
        ("Different printed logo","Start from a standard bottle","Artwork file, printable dimensions and surface/material details"),
        ("Alternative lid / carry handle","Check existing component compatibility first","Thread and gasket dimensions, assembly sample and test criteria"),
        ("New body profile or unique closure","Engineering review and possible new tooling","CAD, material grade, volume target, tolerances and project budget"),
        ("Integrated embossed brand","Mold-surface modification assessment","3D lettering definition, rights and future mold reuse")]:
        h+='<div class="svc-decision__row"><strong>'+e(left)+'</strong><span>'+e(middle)+'</span><span>'+e(right)+'</span></div>'
    h+='</div><p class="svc-note">Product models such as <a href="/products/2095/">2095</a> and <a href="/products/5340/">5340</a> show existing bottle forms. Their appearance alone does not establish the feasibility or cost of modifying a mold.</p></div></section>'
    h+=faqs(d,"numbered","Questions to Resolve Before Paying a Tooling Deposit")
    h+='<section class="section section--soft svc-next"><div class="shell"><div class="svc-next__split"><div><span class="eyebrow">AFTER MOLD DESIGN</span><h2 class="section__title">Tool Trials Need a Production and Inspection Plan</h2><p>Acceptance should cover neck fit, lid operation, wall quality and material—not just first-shot appearance. Put drawing control and sample testing in the tooling agreement before bulk production is booked.</p>'+link("/capabilities/custom-manufacturing/","Manufacturing and inspection route")+'</div><div class="svc-next__docs"><h3>Request these files</h3><ul><li>Signed part drawing and revision</li><li>Component material grade</li><li>Tool ownership and change rights</li><li>Trial sample acceptance record</li></ul></div></div></div></section>'
    h+=resources("Engineering Notes for Custom Tooling",[
        ("OEM vs ODM Bottle Development","/blog/oem-vs-odm-plastic-water-bottles/","Decide who defines, owns and approves the design."),
        ("Production Quality Control","/blog/water-bottle-quality-control-checklist/","Plan tolerances and acceptance around the finished bottle.")
    ],style="lines")
    return h

def custom_logo(d):
    h='<section class="section svc-models svc-models--logo"><div class="shell"><div class="section__head"><div><span class="eyebrow">REAL PRINT SURFACES</span><h2 class="section__title">The Same Logo Behaves Differently on Two Bottles</h2><p>Artwork width and placement must be approved on each surface—not copied from a computer mockup.</p></div></div><div class="svc-models__grid">'
    h+=product_link("2501","Body and Lid Geometry","Check ribs, seams, curvature and clearance from the drinking area.")
    h+=product_link("5299","Clear / Gradient Appearance","Request printed proofs across your selected body colors to evaluate contrast.")
    h+='</div></div></section>'
    h+=faqs(d,"tiles","Four Print-Production Questions Worth Settling Early")
    h+='<section class="section section--soft svc-next"><div class="shell"><div class="svc-next__split"><div><span class="eyebrow">BEYOND THE LOGO FILE</span><h2 class="section__title">One Brand, Two Further Approvals</h2><p>A logo proof does not approve the bottle color or the retail pack. Keep those as separate sign-off points so product and carton revisions remain traceable.</p></div><div class="svc-next__links">'
    h+=link("/capabilities/custom-graphics/","Approve plastic color and surface")
    h+=link("/capabilities/custom-packaging/","Approve box artwork and barcode")
    h+='</div></div></div></section>'
    h+=resources("Artwork and Decoration Resources",[
        ("Vector Logo & Artwork Checklist","/blog/custom-logo-water-bottle-checklist/","Prepare usable files and identify printing areas."),
        ("Logo Printing Methods","/blog/water-bottle-logo-printing-methods/","Compare screen, pad and other compatible processes.")
    ],style="strips")
    return h

def custom_graphics(d):
    h='<section class="section svc-models svc-models--color"><div class="shell"><div class="section__head"><div><span class="eyebrow">COLOR SAMPLE REFERENCES</span><h2 class="section__title">Compare Finishes on the Actual Molded Shape</h2><p>These models are design references. Confirm whether a specific finish is molded, transferred or otherwise decorated.</p></div></div><div class="svc-models__grid">'
    h+=product_link("2095","Multicolor Look","Ask whether the visual effect shown is available for your intended volume and resin.")
    h+=product_link("5299","Gradient Reference","Check design continuity around a curved transparent body.")
    h+=product_link("2501","Solid Color Reference","Use the body and lid separately in a color approval matrix.")
    h+='</div></div></section>'
    h+=faqs(d,"tiles","Color-Approval Questions Before Bulk Production")
    h+='<section class="section section--soft svc-next"><div class="shell"><div class="section__head"><div><span class="eyebrow">NEXT DECISIONS</span><h2 class="section__title">When Color Becomes a Branding or Packaging Job</h2></div></div><div class="svc-next__two">'
    h+='<div><h3>Color + Logo Contrast</h3><p>Transparent walls and dark graphics may need underprinting and a different proof for each key colorway.</p>'+link("/capabilities/custom-logo/","Review logo compatibility")+'</div>'
    h+='<div><h3>Color + Retail Presentation</h3><p>Packaging artwork should depict the approved body/cap colors, not a speculative render.</p>'+link("/capabilities/custom-packaging/","Review packaging artwork")+'</div>'
    h+='</div><p class="svc-note">Technical reference: '+link("/blog/tritan-vs-pp-petg-pc/","How plastic resin selection affects appearance")+'</p></div></section>'
    return h

def custom_manufacturing(d):
    h='<section class="section svc-quality"><div class="shell"><div class="section__head"><div><span class="eyebrow">APPROVED-PRODUCT CHECKS</span><h2 class="section__title">What a Practical Bottle Inspection Actually Looks At</h2><p>Model references help define the right checks; they are not claims that a model has passed an undisclosed test.</p></div></div><div class="svc-quality__grid">'
    for model,title,checks in [
        ("5340","1,000 mL bottle: carry and closure",["Verify capacity and neck/cap geometry","Inspect full-bottle grip and handling","Check the specified seal and packing"]),
        ("5299","550 mL bottle: decoration and fit",["Inspect body finish and graphic registration","Confirm compatible lid and gasket","Check print scuffing and carton protection"])]:
        h+='<article class="svc-quality__item"><div>'+photo(SERIES[model]["images"][0],"Model "+model+" inspection reference")+'</div><div><span class="eyebrow">MODEL '+model+'</span><h3>'+e(title)+'</h3><ul>'
        for x in checks:h+='<li>'+e(x)+'</li>'
        h+='</ul>'+link("/products/"+model+"/","View reference SKU")+'</div></article>'
    h+='</div></div></section>'
    h+=faqs(d,"numbered","Production Responsibilities and Inspection Evidence")
    h+='<section class="section section--soft svc-next"><div class="shell"><div class="section__head"><div><span class="eyebrow">RELEASE DOCUMENTATION</span><h2 class="section__title">Three Records to Lock Before Dispatch</h2></div></div><div class="svc-next__three">'
    for no,title,copy,url,label in [
        ("A","Inspection Criteria","Which dimensions, appearance defects, missing parts and assembly checks are acceptable?","/quality-control/","QC process"),
        ("B","Packing Configuration","How many pieces per carton, which components, and which SKU/color labels are agreed?","/capabilities/custom-packaging/","Packing control"),
        ("C","Shipment Handover","Which carton marks, product documents and delivery terms apply to this shipment?","/shipping-logistics/","Shipping plan")]:
        h+='<article><span>'+no+'</span><h3>'+title+'</h3><p>'+copy+'</p>'+link(url,label)+'</article>'
    h+='</div><div class="svc-inline-reading">Buyer references: '+link("/blog/water-bottle-quality-control-checklist/","Quality Control Checklist")+' '+link("/blog/water-bottle-lid-leakproof-testing/","Lid Leak Testing")+'</div></div></section>'
    return h

def custom_packaging(d):
    h='<section class="section svc-decision svc-decision--pack"><div class="shell"><div class="section__head"><div><span class="eyebrow">CARTON PLANNING</span><h2 class="section__title">Begin with Real Catalog Carton Figures</h2><p>Reference figures from the product list; dimensions and case counts still require confirmation for the finished packaging configuration.</p></div></div><div class="svc-decision__table"><div class="svc-decision__row svc-decision__row--head"><strong>Plastic bottle</strong><strong>Catalog carton reference</strong><strong>Before sign-off</strong></div>'
    for model in ("8563","5340"):
        row=SERIES[model]
        h+='<div class="svc-decision__row"><strong><a href="/products/'+model+'/">Model '+model+' ('+e(row["capacity"])+')</a></strong><span>'+e(row["carton_quantity"])+' pcs · '+e(row["carton_size"])+' cm</span><span>Check packed dimensions, lid height, inserts, gross weight and color labels</span></div>'
    h+='</div><p class="svc-note">Not a final transport quote. Use the approved retail pack, master carton measurements, destination and Incoterm to compare freight costs.</p></div></section>'
    h+=faqs(d,"tiles","Packaging Details Buyers Often Miss")
    h+='<section class="section section--soft svc-next"><div class="shell"><div class="section__head"><div><span class="eyebrow">CROSS-TEAM APPROVALS</span><h2 class="section__title">Where Packaging Meets Production and Artwork</h2></div></div><div class="svc-next__two">'
    h+='<div><span class="eyebrow">BRAND ARTWORK</span><h2>Confirm Box Print Files</h2><p>Approve dielines, text, country of origin, color proof and barcode before the first printed carton run.</p>'+link("/capabilities/custom-logo/","Brand artwork workflow")+'</div>'
    h+='<div><span class="eyebrow">WAREHOUSE HANDOVER</span><h2>Confirm Packing at Production</h2><p>Match case quantity, carton marks and actual product mix against the shipping list.</p>'+link("/capabilities/custom-manufacturing/","Packing inspection route")+'</div>'
    h+='</div><div class="svc-inline-reading">Packing references: '+link("/blog/custom-water-bottle-export-packaging/","Export Carton Guide")+' '+link("/blog/custom-water-bottle-moq-pricing/","MOQ & Pricing")+'</div></div></section>'
    return h

RENDERS={
 "custom-water-bottle":custom_water_bottle,
 "custom-molding":custom_molding,
 "custom-logo":custom_logo,
 "custom-graphics":custom_graphics,
 "custom-manufacturing":custom_manufacturing,
 "custom-packaging":custom_packaging
}

def render_distinct_sections(slug,data):
    return RENDERS[slug](data)
