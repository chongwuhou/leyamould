"""Source-authored protein shaker wholesale buying guidance.

English collection source only; the shared collection layout remains unchanged.
Any D1/CMS body override in site_renderer.build_url retains owner priority.
Model links refer exclusively to real catalog product pages.
"""
from site_renderer import e

SECTIONS = [
    {
        "eyebrow": "SHAKER SELECTION",
        "title": "Compare Protein Shaker Bottle Models Before Requesting Bulk Pricing",
        "lead": (
            "Protein shaker bottles are purchased for different routines: gym membership kits, "
            "fitness retail programs, sports-club giveaways and private-label nutrition campaigns. "
            "A wholesale comparison should begin with an identifiable factory model rather than "
            "a generic photograph. Match the bottle's documented capacity and construction with "
            "the intended buyer, then inspect a physical sample before approving any functional claim."
        ),
        "items": [
            ("Use the catalog capacity as a starting point",
             "XUYI lists model 501 at 500 ml and model 502 at 700 ml, while model 509 is listed at 400 ml. "
             "Compare these source-listed options with the expected drink portion and available storage space. "
             "The catalog capacity is not a promise of usable fill volume below the rim; confirm the practical "
             "fill level and markings with the actual sample before printing a label or online size chart."),
            ("Check every mixing and drinking component",
             "A shaker listing should identify the body, lid, spout or drinking opening, sealing parts and any "
             "removable mixing accessory. Do not assume a whisk ball, mesh insert, carry loop or graduated scale "
             "is included merely because another shaker has one. Request the exact parts list and sample photos "
             "for each model and variant; pay particular attention to how easily the lid and gasket can be cleaned."),
            ("Compare model variants without assuming interchangeability",
             "The source catalog also carries shaker models 507 and 510 and separate references 5247 and 5248. "
             "Treat each identifier as its own quotation line. Different-looking lids or bottles do not establish "
             "that closures, seals or mixing inserts can be swapped between models. Check the real assembled "
             "sample, packing configuration and model-specific product page before consolidating a shortlist.")
        ]
    },
    {
        "eyebrow": "OEM & PRIVATE LABEL",
        "title": "Plan Logo Printing, Shaker Colors and Wholesale Packaging",
        "lead": (
            "For branded protein shaker bottles, decoration and fulfillment details can matter as much as the "
            "body shape. A quotation for a plain catalog model is not automatically comparable with a "
            "multi-color logo or retail-ready packaged program. Submit the same written brief to the "
            "supplier for every candidate SKU and record which options have actually been confirmed."
        ),
        "items": [
            ("Approve decoration on the real bottle",
             "Provide vector artwork, the proposed print dimensions, color references, placement and intended "
             "quantity per design. Printing feasibility depends on the selected polymer, curvature and surface "
             "finish, so a screen mockup alone should not be the final approval. Ask for a decorated sample and "
             "compare logo position, edge sharpness, appearance after normal handling and the agreed color reference."),
            ("Separate stock colors from custom production",
             "Ask which model and color combinations can be sourced as existing variants and which require "
             "a separate production run. A request for a new body color, changed closure or matching lid may "
             "alter sampling, minimum quantities and costing. None of these terms should be assumed across "
             "the whole shaker collection: obtain them in writing for the exact model and artwork revision."),
            ("Specify the sales channel and outer carton",
             "A gym giveaway may favor simple protective bulk packing; a retail or private-label launch may "
             "need a labeled unit pack, barcode, instructions and a consistent assortment by color. Specify "
             "the carton count, inner protection, unit-pack dimensions and destination so the supplier can "
             "review packing feasibility and freight space rather than quote from bottle weight alone.")
        ]
    },
    {
        "eyebrow": "QUALITY & PROCUREMENT",
        "title": "Use a Model-Specific Shaker Bottle Approval Checklist",
        "lead": (
            "A useful protein shaker wholesale quotation is more than a price per bottle. Attach the "
            "identified SKU, ordered quantities, sample reference, selected material and lid configuration, "
            "artwork version, packing requirements, requested delivery destination and any market-specific "
            "documents. Confirm the applicable inspection approach before production rather than discovering "
            "an unclear requirement when goods are already packed."
        ),
        "items": [
            ("Inspect fit, sealing and cleanability",
             "Check the actual body and lid fit, gasket seating, drinking closure, mixing components and "
             "surface condition against an approved sample. Any leakage, drop or dishwasher claims need a "
             "defined test method and evidence for the selected model; do not imply universal leakproof or "
             "dishwasher-safe performance from the category name. Document the agreed checks and acceptance "
             "criteria in the purchase specification."),
            ("Confirm materials and destination requirements",
             "A generic plastic name is not enough for food-contact assessment. Request identification of "
             "the actual body, lid, seal and accessory materials, the intended beverage and use conditions, "
             "and relevant documentation for the destination market. A statement about a polymer family is "
             "not a finished-product certificate; testing scope and product configuration must match."),
            ("Keep quote, sample and shipment details aligned",
             "Before placing the purchase order, reconcile model code, capacity, color split, approved print "
             "sample, quantities, outer carton markings, payment terms and delivery terms. For repeat orders, "
             "confirm whether any lid, resin, decoration or packaging revision has occurred. This creates "
             "a clearer basis for comparing wholesale offers and checking the shipment on arrival.")
        ]
    }
]

LINKS = (
    ("/products/501/", "Model 501 — source-listed 500 ml shaker"),
    ("/products/502/", "Model 502 — source-listed 700 ml shaker"),
    ("/products/509/", "Model 509 — source-listed 400 ml shaker"),
    ("/capabilities/custom-logo/", "Review custom logo options"),
    ("/request-sample/", "Plan a shaker bottle sample"),
    ("/faq/", "Read wholesale purchasing FAQs"),
)

def render():
    output = []
    for section in SECTIONS:
        output.append(
            '<section class="section shaker-wholesale-guide"><div class="shell">'
            '<div class="section__head"><div><span class="eyebrow">'+e(section["eyebrow"])+
            '</span><h2 class="section__title">'+e(section["title"])+
            '</h2><p class="copy-muted">'+e(section["lead"])+'</p></div></div>'
            '<div class="grid grid--3">'
        )
        for heading, description in section["items"]:
            output.append(
                '<article class="benefit"><h3>'+e(heading)+'</h3><p>'+e(description)+'</p></article>'
            )
        output.append('</div></div></section>')
    output.append(
        '<section class="section section--soft shaker-wholesale-links"><div class="shell">'
        '<div class="section__head"><div><span class="eyebrow">NEXT STEPS</span>'
        '<h2 class="section__title">Browse Real Shaker Models and Prepare Your Quote</h2>'
        '<p class="copy-muted">Use individual model pages for the correct sample reference, '
        'then send quantities, logo artwork and destination details for a comparable project quotation.</p>'
        '</div></div><div class="grid grid--3">'
    )
    for href, label in LINKS:
        output.append(
            '<a class="benefit" href="'+e(href)+'"><strong>'+e(label)+'</strong></a>'
        )
    output.append('</div></div></section>')
    return ''.join(output)