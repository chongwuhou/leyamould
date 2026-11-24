"""Detailed cap-mould category pages for the LEYA MOULD public catalogue.

The reference site uses the same editorial rhythm on each category page: a
hero with production metrics, product cards, engineering advantages, process
evidence, samples, trials, quality checks, FAQs and a contact CTA.  This
module keeps that page-specific content outside the shared site header/footer
renderer so the catalogue can grow without changing the water-cup backend
contracts.
"""
from __future__ import annotations


REFERENCE_ORIGIN = "https://www.cap-molds.com"

# The reference catalogue uses a dedicated, short hero sentence on each
# category page. Keeping these strings in the page data preserves the target
# line rhythm without changing the shared header/footer renderer.
REFERENCE_HERO_DESCRIPTIONS = {
    "mineral-water-closure-cap-molds": "High‑precision cap moulds for mineral water, carbonated drinks, hot‑fill, sports, tamper‑evident, and lightweight closures. PCO 1881, 30/25, and custom neck finishes.",
    "oil-bottle-cap-mould": "High‑precision moulds for olive oil, sunflower oil, canola oil, and cooking oil bottles. Leak‑proof design, food‑grade compliance, multi‑cavity up to 72 cavities.",
    "engine-oil-cap-mould": "Heavy‑duty injection moulds engineered for motor oil, lubricant, ATF, and hydraulic fluid bottles. Superior chemical resistance, high‑torque seal integrity, and lifetime durability up to 5 million cycles.",
    "food-packaging-cap-mould": "Precision injection moulds for yogurt cups, sauce bottles, jam jars, and ready‑meal containers. FDA & EU compliant, leak‑proof, tamper‑evident, and built for high‑output lines.",
    "medical-cap-mould": "Precision injection moulds for pharmaceutical, diagnostic, and medical device caps. Cleanroom‑compatible, FDA & ISO 13485 compliant, and engineered for high‑purity production.",
    "flip-top-caps-mould": "High‑cycle flip‑top cap moulds engineered for smooth action, 50,000+ cycles tested, tailored for shampoo, lotion, and cosmetic packaging.",
    "personal-care-cap-mould": "Precision injection moulds for flip‑top, disc‑top, and pump caps used on shampoo, lotion, body wash, and cosmetic bottles. Soft‑touch, leak‑proof, and built for high‑speed filling lines.",
    "functional-cap-mould": "Precision injection moulds for sport caps, push‑pull closures, and complex combination caps. Leak‑proof, durable, and designed for high‑output assembly lines.",
    "plastic-handle-cap-mould": "Heavy‑duty injection moulds for plastic handles used on bottles, jerry cans, and containers. Engineered for high strength, wear resistance, and multi‑cavity production.",
}

REFERENCE_HERO_DESCRIPTIONS.update({
    "five-gallon-water-cap-mould": "Heavy-duty tooling for reusable 18.9L water bottles, cooler caps and dispenser closures. Seal, tear-band and sanitisation requirements reviewed together.",
    "wine-cap-mould": "Precision closure moulds for wine, spirits and specialty beverage bottles. Pourer, tamper evidence and decorative surfaces are matched to the bottle finish.",
    "pet-preform-mould": "Multi-cavity PET and PP preform moulds for beverage, edible-oil and specialty packaging. Neck finish, gram weight and stretch-blow targets stay connected.",
    "blow-bottle-mould": "Bottle blow moulds for PET containers, wide-mouth packs and custom shapes. Wall map, cooling, neck finish and machine envelope are reviewed before tooling.",
})


def _asset(path: str) -> str:
    if path.startswith(("http://", "https://", "/assets/")):
        return path
    return REFERENCE_ORIGIN + path


def _structured_text(item: dict, locale: str, key: str, fallback: str) -> str:
    """Read an owner-edited structured product field with a safe locale fallback."""
    localized = item.get(key + "Es") if locale == "es" else item.get(key)
    if isinstance(localized, str) and localized.strip():
        return localized.strip()
    value = item.get(key)
    return value.strip() if isinstance(value, str) and value.strip() else fallback


def _structured_faqs(item: dict, locale: str, fallback: list[tuple[str, str]]) -> list[tuple[str, str]]:
    raw = item.get("faqsEs") if locale == "es" else item.get("faqs")
    if not isinstance(raw, list) or not raw:
        raw = item.get("faqs") if isinstance(item.get("faqs"), list) else []
    rows = []
    for entry in raw[:12]:
        if not isinstance(entry, dict):
            continue
        question = str(entry.get("question") or "").strip()
        answer = str(entry.get("answer") or "").strip()
        if question and answer:
            rows.append((question, answer))
    return rows or fallback


def _structured_sections(item: dict, locale: str, fallback: list[tuple[str, str, str, list[str]]]) -> list[tuple[str, str, str, list[str]]]:
    """Read editable product sections while retaining the catalogue media layout."""
    raw = item.get("sectionsEs") if locale == "es" else item.get("sections")
    if not isinstance(raw, list) or not raw:
        raw = item.get("sections") if isinstance(item.get("sections"), list) else []
    rows = []
    for index, entry in enumerate(raw[:8]):
        if not isinstance(entry, dict):
            continue
        title = str(entry.get("title") or "").strip()
        body = str(entry.get("body") or "").strip()
        if not title or not body:
            continue
        previous = fallback[min(index, len(fallback) - 1)] if fallback else (title, body, "", [])
        bullets = entry.get("bullets")
        if not isinstance(bullets, list):
            bullets = previous[3] if len(previous) > 3 else []
        bullets = [str(value).strip() for value in bullets[:8] if str(value).strip()]
        rows.append((title, body, previous[2], bullets))
    return rows or fallback


def _spec(hero_title, accent, subtitle, image, stats, products, advantages,
          technology, samples, quality, faqs, testimonials, videos=None):
    return {
        "hero_title": hero_title,
        "hero_accent": accent,
        "hero_subtitle": subtitle,
        "hero_image": image,
        "stats": stats,
        "products": products,
        "advantages": advantages,
        "technology": technology,
        "samples": samples,
        "quality": quality,
        "faqs": faqs,
        "testimonials": testimonials,
        "videos": videos or [],
    }


DETAILS = {
    "mineral-water-closure-cap-molds": _spec(
        "Water & Beverage", "Cap Mould", "Solutions",
        "/upload/Banner/water-bev-hero.jpg",
        [("5s", "Cycle Time"), ("72", "Max Cavities"), ("6", "Mould Types"), ("5M+", "Mould Life")],
        [
            ("High Quality PCO 1881 Mineral Water Cap Injection Mould | 32/48/72 Cavity Available | Factory Direct", "/Upload/20231107/202311070817255253.jpg", "Ideal for screw caps for mineral water, purified water, spring water and other beverage PET bottles."),
            ("48 Cavity 38mm Neck Mineral Water Closure Cap Mould", "/Upload/20260617/202606171039475377.jpg", "A balanced high-output configuration for production efficiency and predictable mould cost."),
            ("Mineral Water Closure Cap Moulds | High-Precision Manufacturer", "/upload/product/month_2105/202105252222459511.jpg", "High-precision water bottle cap moulds with cavity options matched to the buyer's line."),
            ("32 Cavity Mineral Water Closure Cap Mould", "/upload/product/month_2105/202105252218052303.jpg", "High productivity, precision machining and hot-runner balance for beverage closures."),
            ("Custom Compression & Injection Moulds for PCO 1881 / 1810", "/upload/product/month_2105/202105252201289687.jpg", "Custom neck finishes and high-speed closure tooling for international packaging projects."),
            ("24 Cavity PCO 1881 Mineral Water Cap Injection Mould", "/upload/product/month_2105/202105252226261284.jpg", "Hot-runner tooling for still, sparkling and carbonated beverage production."),
        ],
        [("Ultra-Fast Cycles", "Optimized cooling and hot runners can achieve cycle times from 4.5 seconds."), ("Micron-Level Tolerances", "Cavity-to-cavity variation is controlled for consistent cap dimensions."), ("PCO & ISBT Standards", "Neck-finish options support international beverage packaging requirements."), ("Hot Runner Integration", "Balanced nozzle control reduces waste and protects fill consistency."), ("Corrosion-Resistant Steel", "S136 mirror steel supports long life in high-moisture production environments."), ("Quick Cavity Expansion", "Modular inserts make future cavity upgrades easier to plan.")],
        ("Inside Our Water Cap Mould Engineering", [("Hot Runner & Cooling Design", "Balanced hot-runner layouts and conformal cooling keep temperature uniform across cavities.", "/images/Hot-Runner-Cooling-Design.jpg", ["Valve-gate or open-gate options", "3D-printed conformal cooling inserts", "Thermal imaging verification before shipment"]), ("Stripper Plate & Ejection", "A guided stripper plate releases tamper-evident caps smoothly without deforming bridges.", "/images/Stripper-Plate-Ejection.jpg", ["Hardened H13 stripper plate", "Guided ejection with linear bearings", "Two-stage ejection for fragile bridges"])]),
        ["/upload/Water-Beverage-Cap/watercap-sample1.jpg", "/upload/Water-Beverage-Cap/watercap-sample2.jpg", "/upload/Water-Beverage-Cap/watercap-sample3.jpg", "/upload/Water-Beverage-Cap/watercap-sample4.jpg", "/upload/Water-Beverage-Cap/watercap-sample5.jpg", "/upload/Water-Beverage-Cap/watercap-sample6.jpg", "/upload/Water-Beverage-Cap/watercap-sample7.jpg", "/upload/Water-Beverage-Cap/watercap-sample8.jpg", "/upload/Water-Beverage-Cap/watercap-sample9.jpg", "/upload/Water-Beverage-Cap/watercap-sample10.jpg"],
        [("CMM Inspection", "Full dimensional reports for all cavities."), ("Cycle Time Verification", "On-machine trials confirm the output target."), ("Cap Weight Audit", "Material distribution is checked cavity by cavity."), ("ISO 9001 Certified", "Quality management evidence stays with the project file.")],
        [("What is the typical cycle time?", "A 48-cavity PCO 1881 mould commonly runs around 4.8–5.5 seconds, depending on the machine and resin."), ("Can one mould run PCO 1881 and 30/25?", "Interchangeable cavity sets can be reviewed for compatible neck finishes."), ("What is the mould life?", "With maintenance, premium steel cavity components are designed for more than 5 million cycles."), ("Do you provide installation support?", "Remote setup guidance and trial support are included in the technical handover.")],
        [("The 72-cavity PCO 1881 mould doubled our output while keeping cap quality consistent.", "Bottling plant manager", "Nigeria"), ("The lightweight cap design reduced material cost without changing the seal.", "Packaging engineer", "United Arab Emirates"), ("The trial report made approval straightforward for our production team.", "Operations director", "Philippines")],
        [("m7Hd7Uodb_Y", "PCO 1881 water cap mould trial"), ("x_AY9rMwvLw", "Sports cap mould trial")],
    ),
    "oil-bottle-cap-mould": _spec(
        "Edible Oil", "Cap Mould", "Solutions",
        "/upload/product/month_2105/202105262038349426.jpg",
        [("5s", "Cycle Time"), ("72", "Max Cavities"), ("5", "Mould Variants"), ("5M+", "Mould Life")],
        [("16 Cavity Edible Oil Flip Top Cap Mould", "/Upload/20260618/202606180755323692.jpg", "High-precision flip-cap tooling for cooking oil and food packaging lines."), ("8 Cavity Edible Oil Bottle Cap Mould", "/Upload/20260618/202606180741263964.jpg", "Stable production with hot-runner balance and long mould life."), ("6 Cavity Oil Pull Cap Mould", "/Upload/20260618/202606180733586664.jpg", "Leak-proof pull-top tooling for edible oil bottle packaging."), ("6 Cavity Oil Pull Cap Mould | Food Packaging", "/Upload/20260617/202606171717064343.jpg", "Precision machining and tamper-evident release for cooking oils."), ("16 Cavity Tamper-Evident Edible Oil Cap Mould", "/Upload/20260617/202606171704179997.jpg", "Anti-theft ring design with repeatable filling and sealing."), ("16 Cavity Tamper-Evident Pull Ring Cap Mould", "/Upload/20260617/202606171650511166.jpg", "Durable pull-ring tooling for high-output oil packaging." )],
        [("Leak-Proof Design", "Triple-point sealing geometry protects the package under hot-fill conditions."), ("Food-Grade Compliance", "Materials and polishing are selected around food-contact documentation."), ("Corrosion Resistant", "S136 or NAK80 steel resists acidic oils and cleaning chemicals."), ("Fast Cycle Times", "Conformal cooling and hot runners keep cycle targets stable."), ("Micron-Level Tolerances", "Cavity-to-cavity variation is controlled for seal integrity."), ("Modular Cavity Design", "Interchangeable inserts allow future cavity-count changes.")],
        ("Inside Our Edible Oil Cap Mould Engineering", [("Leak-Proof Seal & Conformal Cooling", "Moldflow-reviewed sealing rings and conformal cooling keep every cavity round and consistent.", "/images/Leak‑Proof-Seal-Conformal-Cooling.jpg", ["Optimized gate placement", "3D-printed cooling inserts", "Thermal imaging verification"]), ("Food-Grade Steel & Anti-Corrosion Treatment", "Mirror-polished stainless mould steel reduces bacterial adhesion and makes cleaning easier.", "/images/Food-Grade-Steel.jpg", ["ASSAB S136 or NAK80", "Vacuum heat treatment", "Full material traceability"]), ("Multi-Cavity Consistency & Quick Change", "Balanced inserts let the buyer expand output or replace a single cavity with less downtime.", "/images/Multi-Cavity-Quick-Change.jpg", ["24 to 72 cavity options", "Individual nozzle control", "Quick-change inserts"])]),
        ["/upload/Edible-Oil-Cap/oilcap-sample1.jpg", "/upload/Edible-Oil-Cap/oilcap-sample2.jpg", "/upload/Edible-Oil-Cap/oilcap-sample3.jpg", "/upload/Edible-Oil-Cap/oilcap-sample4.jpg", "/upload/Edible-Oil-Cap/oilcap-sample6.jpg", "/upload/Edible-Oil-Cap/oilcap-sample7.jpg", "/upload/Edible-Oil-Cap/oilcap-sample8.jpg", "/upload/Edible-Oil-Cap/oilcap-sample9.jpg", "/upload/Edible-Oil-Cap/oilcap-sample10.jpg"],
        [("CMM Inspection", "Dimensional reports cover every cavity."), ("Leak Test", "Oil-filling tests are performed at elevated temperature."), ("Cap Weight Audit", "Material distribution is checked before delivery."), ("ISO 9001 Certified", "Quality records remain attached to the mould project.")],
        [("What steel is best for edible oil moulds?", "ASSAB S136 or NAK80 with vacuum heat treatment provides corrosion resistance and cleanable surfaces."), ("How do you guarantee leak-proof caps?", "The sealing geometry is reviewed and every mould is trialled with actual oil filling."), ("Can you match an existing oil cap?", "Send a drawing or physical sample for a DFM review and design match."), ("What is the typical mould life?", "With planned maintenance, edible-oil moulds are designed to exceed 5 million cycles.")],
        [("The pull-ring tooling has run millions of cycles without a leak.", "Production director", "Spain"), ("The food-grade mould met our hygiene requirements and the DFM report improved the design.", "QA manager", "Turkey"), ("The 72-cavity mould produces consistent caps at a stable cycle.", "Operations manager", "Italy")],
        [("O81wopvbPrY", "Edible oil cap mould trial"), ("1wfR93CVe3s", "China flip-top caps mould manufacturers")],
    ),
    "flip-top-caps-mould": _spec(
        "Flip Top Cap Mould –", "Living Hinge", "Precision",
        "/upload/Banner/20210524213222103.jpg",
        [("50k+", "Hinge Cycles Tested"), ("±0.01mm", "Precision"), ("72", "Max Cavities")],
        [("Shampoo Flip-Top", "/images/Design/Flip-Top-Cap-Mold.png", "Living-hinge tooling for shampoo and conditioner bottles."), ("Lotion Disc Top", "/images/Design/Lotion-Disc-Top.jpg", "Smooth dispensing with a durable snap-fit closure."), ("Dual-Color Cap", "/images/Design/Dual‑Color-Cap.jpg", "Two-material visual differentiation for branded packaging."), ("Detergent Cap", "/images/Design/Detergent-Cap.jpg", "High-strength flip-top tooling for household liquids."), ("Travel Size Cap", "/images/Design/Travel-Size-Cap.jpg", "Compact closure geometry for personal-care packs."), ("Flip-Top with Tear Band", "/images/Design/Flip‑Top-with-Tear-Band.jpg", "Tamper-evident opening with controlled bridge breakage.")],
        [("Living Hinge Engineering", "Hinge geometry is tuned for repeatable opening and closing."), ("Leak-Proof Seal", "Seal surfaces are checked against the bottle finish and product viscosity."), ("Fast Cycle Times", "Cooling and balanced gating support high-volume cosmetic production."), ("Custom Orifice & Finish", "Dispensing openings and decorative surfaces are reviewed with the brand team."), ("Easy Demolding", "Ejection is designed around the hinge and cosmetic surfaces."), ("Durable Steel Selection", "Wear-resistant steel and polishing protect the hinge cavity.")],
        ("Inside Our Flip-Top Mould Engineering", [("Living Hinge Design", "The hinge radius, snap fit and opening force are verified before the mould is released.", "/images/Flip‑Top-Mould.png", ["Opening-cycle target review", "Controlled snap fit", "Orifice and seal inspection"]), ("Cooling & Steel Strategy", "Balanced cooling prevents warpage around thin hinge and cap-wall sections.", "/images/Cooling-Steel-Strategy.png", ["Conformal cooling options", "Polished cavity surfaces", "Wear-part replacement plan"])]),
        ["/upload/flip-samples/sample01.jpg", "/upload/flip-samples/sample02.jpg", "/upload/flip-samples/sample03.jpg", "/upload/flip-samples/sample04.jpg", "/upload/flip-samples/sample05.jpg", "/upload/flip-samples/sample06.jpg", "/upload/flip-samples/sample07.jpg", "/upload/flip-samples/sample08.jpg", "/upload/flip-samples/sample09.jpg", "/upload/flip-samples/sample10.jpg", "/upload/flip-samples/sample11.jpg", "/upload/flip-samples/sample12.jpg"],
        [("Hinge Fatigue Test", "Open-close cycles verify the living hinge."), ("Leak Test", "Seal performance is checked with the intended bottle finish."), ("Dimensional Report", "Critical orifice and hinge dimensions are recorded."), ("Material Certificate", "Resin and steel documentation stays with the handover file.")],
        [("How many cycles can the hinge run?", "The reference design is tested beyond 50,000 open-close cycles; the final target is confirmed with the buyer."), ("Can the cap use a custom orifice?", "Yes. Orifice diameter, flow and decorative finish can be reviewed together."), ("Can you match an existing cosmetic cap?", "Send the cap, bottle finish or drawing for a hinge and seal assessment."), ("Do you support dual-colour designs?", "Two-shot and insert strategies can be evaluated during DFM.")],
        [("The flip-top mould runs smoothly and the hinge action stays consistent.", "Packaging engineer", "Mexico"), ("The samples made approval easy for our cosmetic filling line.", "Technical manager", "Spain"), ("The polishing and ejection detail protected the visible surface.", "Brand operations", "France")],
        [("O81wopvbPrY", "China flip-top caps mould manufacturers"), ("1wfR93CVe3s", "Flip-top cap mould trial")],
    ),
    "engine-oil-cap-mould": _spec(
        "Engine Oil Cap Mould", "for Demanding", "Automotive Fluids",
        "/upload/Banner/Engine-Oil-Cap-Mould.jpg",
        [("4.8s", "Cycle Time"), ("72", "Max Cavities"), ("5", "Specialized Variants"), ("5M+", "Mould Life")],
        [("PCO 38mm Motor Oil Cap Mould", "/upload/Engine-Oil-Cap/PCO38-engine-oil-cap-mould.jpg", "Reliable thread and seal geometry for common automotive lubricant bottles."), ("5L Tamper-Evident Oil Cap Mould", "/upload/Engine-Oil-Cap/5L-engine-oil-cap-mould.jpg", "High-strength tooling for larger containers and visible tamper evidence."), ("Chemical-Resistant Cap Mould", "/upload/Engine-Oil-Cap/chemical-resistant-oil-cap-mould.jpg", "Steel and sealing choices that tolerate aggressive oil additives."), ("High-Torque Engine Oil Cap Mould", "/upload/Engine-Oil-Cap/high-torque-engine-oil-cap-mould.jpg", "Torque-stable threads protect the seal during filling and transport."), ("4-Cavity High-Output Mould", "/upload/Engine-Oil-Cap/engine-oil-cap-mould.jpg", "Balanced cavity production for demanding industrial lines."), ("Custom Engine Oil Cap Mould", "/upload/Engine-Oil-Cap/custom-engine-oil-cap-mould.jpg", "Custom pouring, grip and tamper features based on the buyer's package.")],
        [("Chemical Resistance", "Steel, coatings and resin assumptions are selected for lubricant contact."), ("Zero Leakage", "Seal geometry and trial checks protect against fluid loss."), ("High Torque Stability", "Thread and ejection design support repeatable application torque."), ("Ultra-Fast Cycles", "Cooling is planned around output and wall-thickness targets."), ("Precision Manufacturing", "CMM and fit checks keep cavity variation under control."), ("Modular Design", "Interchangeable components make service and upgrades easier.")],
        ("How We Build Tough Engine Oil Cap Moulds", [("Anti-Corrosion Steel & High-Temp Sealing", "The tooling brief connects steel selection, thermal stability and the seal lip around the fluid specification.", "/upload/Engine-Oil-Cap/sealing-cooling-design.jpg", ["S136 corrosion-resistant steel", "High-temperature seal review", "Thermal balance verification"]), ("Tamper-Evident Band & High-Torque Unscrewing", "Band bridges, threads and ejection are balanced for clean opening and reliable re-closing.", "/upload/Engine-Oil-Cap/tamper-evident-ejection.jpg", ["Controlled break force", "High-torque thread profile", "Guided unscrewing"]), ("Multi-Cavity Balance & Rapid Cavity Swap", "Balanced runners and replaceable inserts reduce downtime when a cavity needs service.", "/upload/Engine-Oil-Cap/multi-cavity-quick-change.jpg", ["Cavity-to-cavity balance", "Quick-change inserts", "Inspection after replacement"])]),
        ["/upload/Engine-Oil-Cap/sample1.jpg", "/upload/Engine-Oil-Cap/sample2.jpg", "/upload/Engine-Oil-Cap/sample3.jpg", "/upload/Engine-Oil-Cap/sample4.jpg", "/upload/Engine-Oil-Cap/sample5.jpg", "/upload/Engine-Oil-Cap/sample6.jpg", "/upload/Engine-Oil-Cap/sample7.jpg", "/upload/Engine-Oil-Cap/sample8.jpg", "/upload/Engine-Oil-Cap/sample9.jpg", "/upload/Engine-Oil-Cap/sample10.jpg"],
        [("CMM Inspection", "Dimensions and thread geometry are recorded."), ("Leak Test", "Actual fluid or controlled pressure tests confirm sealing."), ("Cap Weight Audit", "Material distribution is checked across cavities."), ("ISO 9001 Certified", "Quality records support production release.")],
        [("Which steel works for engine oil?", "Corrosion-resistant mould steel is selected against the fluid, resin and maintenance plan."), ("How is leakage controlled?", "The thread, plug and sealing lip are reviewed together and checked during trial."), ("Can you make 5L and 1L versions?", "Yes. The bottle finish, torque target and cavity plan are reviewed for each package."), ("What is the service life?", "The reference tooling direction is designed for millions of cycles with planned maintenance.")],
        [("The oil cap tooling held torque and seal performance across the production run.", "Plant manager", "Thailand"), ("The cavity swap plan reduced our planned maintenance downtime.", "Maintenance engineer", "Germany"), ("The trial report made the leak approval process clear.", "Quality manager", "Poland")],
        [("6j8loGkHg-E", "Engine oil cap mould trial"), ("O81wopvbPrY", "Oil cap mould production")],
    ),
    "food-packaging-cap-mould": _spec(
        "Food Packaging Cap Mould", "for Safe & Fresh", "Products",
        "/upload/Banner/food-packaging-hero.jpg",
        [("5.2s", "Cycle Time"), ("72", "Max Cavities"), ("4", "Cap Variants"), ("5M+", "Mould Life")],
        [("Yogurt & Dairy Cap Mould", "/upload/Food-Packaging-Cap/yogurt-cap-mould.jpg", "Food-grade closure tooling for dairy and drinkable-yogurt packages."), ("Sauce & Dressing Cap Mould", "/upload/Food-Packaging-Cap/sauce-cap-mould.jpg", "Leak-proof dispensing and tamper evidence for sauces and dressings."), ("Jar & Spread Cap Mould", "/upload/Food-Packaging-Cap/jar-cap-mould.jpg", "Screw-on and snap-on closures for jars, spreads and dry foods.")],
        [("FDA & EU Compliant", "The project brief records food-contact documentation and material traceability."), ("Leak-Proof Seal", "Seal surfaces are checked for product freshness and transport stability."), ("Hot-Fill Ready", "Cooling and steel choices are reviewed for hot-fill process conditions."), ("Precision Tolerances", "Critical dimensions are measured before production handover."), ("Fast Cycle Times", "Balanced gating and cooling support high-output lines."), ("Modular Design", "Insert strategies make future package changes easier.")],
        ("Cap Mould Manufacturing Advantages", [("High Precision Machining & Strict QC", "CNC, EDM, polishing and inspection are planned around the food-contact closure geometry.", "/upload/Food-Packaging-Cap/precision-machining.jpg", ["Cavity and thread inspection", "Polished sealing surfaces", "Trial sample approval"]), ("Premium Steel & Fast Delivery", "Steel traceability and a clear production brief reduce surprises before shipment.", "/upload/Food-Packaging-Cap/steel-fast-delivery.jpg", ["Material certificate", "Planned machining sequence", "Documented handover"])]),
        ["/upload/Food-Packaging-Cap/sample1.png", "/upload/Food-Packaging-Cap/sample2.png", "/upload/Food-Packaging-Cap/sample3.png", "/upload/Food-Packaging-Cap/sample4.png", "/upload/Food-Packaging-Cap/sample5.png", "/upload/Food-Packaging-Cap/sample6.png", "/upload/Food-Packaging-Cap/sample7.png", "/upload/Food-Packaging-Cap/sample8.png"],
        [("CMM Inspection", "Critical dimensions are recorded cavity by cavity."), ("Leak Test", "Seal performance is checked against the intended package."), ("Weight Audit", "Material distribution supports consistent filling."), ("ISO 9001 Certified", "Quality documents accompany the project handover.")],
        [("Can the mould run hot-fill packaging?", "Yes, when the cap, resin and process temperatures are included in the technical brief."), ("How do you protect food-contact surfaces?", "Steel traceability, polishing and cleaning expectations are recorded before machining."), ("Can you match a sauce cap?", "Send a sample or drawing and we will review the dispensing and sealing geometry."), ("Do you support tamper evidence?", "Snap-on, screw-on and tamper-band options can be reviewed during DFM.")],
        [("The sauce closure passed the filling-line leak checks on the first approved trial.", "Quality manager", "Italy"), ("The polished cavities made cleaning and inspection straightforward.", "Packaging director", "Spain"), ("The modular design gives us room for future pack sizes.", "Operations manager", "Chile")],
    ),
    "medical-cap-mould": _spec(
        "Medical Cap Mould", "for Sterile", "Healthcare Packaging",
        "/upload/Banner/medical-cap-hero.jpg",
        [("5.8s", "Cycle Time"), ("64", "Max Cavities"), ("3", "Cap Variants"), ("5M+", "Mould Life")],
        [("Pharmaceutical Screw Cap Mould", "/upload/Medical-Cap/pharma-cap-mould.png", "Controlled closure tooling for pharmaceutical bottles and syrups."), ("Child-Resistant Cap Mould", "/upload/Medical-Cap/child-resistant-cap-mould.png", "Push-turn and safety features with documented functional checks."), ("Diagnostic & Reagent Cap Mould", "/upload/Medical-Cap/diagnostic-cap-mould.png", "Burr-free, cleanable closures for diagnostic and reagent packaging.")],
        [("ISO 13485 Certified", "Quality records and validation expectations are included in the tooling brief."), ("Cleanroom-Ready", "Surface, cleanliness and packaging requirements are reviewed before trial."), ("Precision Tolerances", "Critical sealing and functional dimensions are measured and recorded."), ("Child-Resistant Design", "Opening force and user-safety functions are checked with the intended package."), ("Fast Cycle Times", "Balanced cavity and cooling design supports repeatable output."), ("100% Validation", "Trial, inspection and approval evidence stay connected to the project.")],
        ("Cap Mould Manufacturing Advantages", [("High Precision Machining & Strict QC", "CNC and EDM work is planned around critical medical closure dimensions.", "/upload/Medical-Cap/precision-machining.jpg", ["Burr-free parting surfaces", "Controlled polishing", "Dimensional inspection"]), ("Premium Steel & Fast Delivery", "Traceable steel and a staged inspection plan support a clean project handover.", "/upload/Medical-Cap/steel-fast-delivery.jpg", ["Material certificates", "Trial samples", "Validation records"])]),
        ["/upload/Medical-Cap/sample2.png", "/upload/Medical-Cap/sample3.png", "/upload/Medical-Cap/sample4.png", "/upload/Medical-Cap/sample5.png", "/upload/Medical-Cap/sample6.png", "/upload/Medical-Cap/sample7.png", "/upload/Medical-Cap/sample8.png", "/upload/Medical-Cap/sample9.png", "/upload/Medical-Cap/sample10.png"],
        [("CMM Inspection", "Critical dimensions are reported for each cavity."), ("Leak & Seal Test", "Seal function is verified against the bottle finish."), ("IQ/OQ/PQ", "Validation evidence is planned around the buyer's release process."), ("ISO 13485 Certified", "Quality documentation supports controlled production.")],
        [("Can you support cleanroom requirements?", "Yes. Cleanliness, packaging and validation expectations are included in the project review."), ("How are child-resistant functions checked?", "Opening force, reclose function and user-safety criteria are agreed before trial."), ("Can you match a pharmaceutical bottle?", "Send the drawing, sample and resin information for a controlled DFM review."), ("What documents are supplied?", "Dimensional reports, material records and trial evidence are packaged with the handover.")],
        [("The burr-free samples helped us complete our internal approval quickly.", "Validation manager", "United Kingdom"), ("The inspection records were clear enough for our regulated packaging file.", "Quality director", "Turkey"), ("The child-resistant mechanism remained consistent across cavities.", "Product manager", "Brazil")],
    ),
    "personal-care-cap-mould": _spec(
        "Personal Care Cap Mould", "for Beauty & Hygiene", "Brands",
        "/upload/Banner/personal-care-hero.jpg",
        [("5.5s", "Cycle Time"), ("48", "Max Cavities"), ("3", "Cap Variants"), ("5M+", "Mould Life")],
        [("Flip-Top Cap Mould", "/upload/Personal-Care-Cap/flip-top-cap-mould.jpg", "Living-hinge tooling for shampoo, conditioner and body wash."), ("Disc-Top Cap Mould", "/upload/Personal-Care-Cap/disc-top-cap-mould.jpg", "Smooth actuation and premium visible surfaces for lotions and creams."), ("Pump & Dispenser Cap Mould", "/upload/Personal-Care-Cap/pump-cap-mould.jpg", "Dispensing geometry matched to product viscosity and package finish.")],
        [("Soft-Touch Finish", "Surface texture and polishing are planned with the brand reference sample."), ("Leak-Proof Design", "Seal surfaces are matched to the bottle and filling process."), ("Durable Living Hinge", "Hinge geometry supports repeated consumer opening."), ("Precision Tolerances", "Critical fit and dispensing dimensions are recorded."), ("Fast Cycle Times", "Balanced cooling supports high-speed filling lines."), ("Custom Surface Finish", "Texture, gloss and decorative areas can be reviewed in DFM.")],
        ("Cap Mould Manufacturing Advantages", [("Specialized Cap Mould Engineering", "The project brief connects hinge, disc-top or pump geometry to the final package.", "/upload/Personal-Care-Cap/precision-machining.jpg", ["Hinge and seal review", "Cosmetic surface control", "Trial sample approval"]), ("Premium Steel & Reliable Delivery", "A clear mould plan and replacement-part strategy protect repeatable production.", "/upload/Personal-Care-Cap/steel-fast-delivery.jpg", ["Polished cavity surfaces", "Traceable steel", "Documented handover"])]),
        ["/upload/Personal-Care-Cap/sample1.png", "/upload/Personal-Care-Cap/sample2.png", "/upload/Personal-Care-Cap/sample3.png", "/upload/Personal-Care-Cap/sample4.png", "/upload/Personal-Care-Cap/sample5.png", "/upload/Personal-Care-Cap/sample6.png", "/upload/Personal-Care-Cap/sample7.png", "/upload/Personal-Care-Cap/sample8.png", "/upload/Personal-Care-Cap/sample9.png"],
        [("CMM Inspection", "Fit and dispensing dimensions are recorded."), ("Leak Test", "Seal performance is checked before release."), ("Hinge Cycle Test", "Opening and closing cycles verify the living hinge."), ("ISO 9001 Certified", "Quality records support repeatable delivery.")],
        [("Can you match a cosmetic finish?", "Yes. Send the cap, bottle or reference panel so gloss and texture can be reviewed."), ("Do you make pump and disc-top closures?", "Yes. The dispensing feature, resin and assembly interface are included in the review."), ("How is hinge life tested?", "The buyer's opening-cycle target is agreed and verified during trial."), ("Can the surface be decorated?", "Flat areas, hot foil and label zones can be considered during design review.")],
        [("The hinge and surface finish matched our brand sample closely.", "Brand engineering manager", "France"), ("The disc-top seal stayed stable through the filling-line trial.", "Production manager", "Poland"), ("The mould was easy to maintain because the wear parts were documented.", "Maintenance lead", "Italy")],
    ),
    "functional-cap-mould": _spec(
        "Functional Cap Mould", "for Multi-Component", "Closures",
        "/upload/Banner/functional-cap-hero.jpg",
        [("6.2s", "Cycle Time"), ("48", "Max Cavities"), ("3", "Cap Variants"), ("5M+", "Mould Life")],
        [("Sport & Push-Pull Cap Mould", "/upload/Functional-Cap/sport-cap-mould.jpg", "One-hand drinking closures with balanced valve and cap components."), ("Multi-Component Combination Mould", "/upload/Functional-Cap/combination-cap-mould.jpg", "Complex assemblies with insert and material-interface planning."), ("Functional Cap Mould", "/upload/Functional-Cap/Functional-Cap-Mould.jpg", "Custom functional mechanisms for household, sports and medical packaging.")],
        [("Multi-Component Precision", "Insert, overmould and assembly relationships are reviewed before steel is cut."), ("Leak-Proof Valve Design", "Valve and sealing surfaces are checked against product pressure and use."), ("Smooth Actuation", "User interaction, opening force and reclose action are part of the brief."), ("Precision Tolerances", "Critical interfaces are measured across all cavities."), ("Fast Cycle Times", "Cooling and runner balance protect repeatable output."), ("Modular Insert System", "Replaceable inserts make future mechanisms easier to maintain.")],
        ("Cap Mould Manufacturing Advantages", [("Specialized Engineering for Complex Closures", "The mould plan connects the mechanism, assembly sequence and inspection evidence.", "/upload/Functional-Cap/precision-engineering.jpg", ["Mechanism review", "Insert alignment", "Functional trial"]), ("Premium Materials & On-Time Delivery", "Material and steel traceability remain attached to the project from design to delivery.", "/upload/Functional-Cap/steel-delivery.jpg", ["Wear-part strategy", "Assembly check", "Documented handover"])]),
        ["/upload/Functional-Cap/sample1.jpg", "/upload/Functional-Cap/sample2.jpg", "/upload/Functional-Cap/sample3.jpg", "/upload/Functional-Cap/sample4.jpg", "/upload/Functional-Cap/sample5.jpg", "/upload/Functional-Cap/sample6.jpg", "/upload/Functional-Cap/sample7.jpg", "/upload/Functional-Cap/sample8.jpg", "/upload/Functional-Cap/sample9.jpg"],
        [("CMM Inspection", "Functional interfaces are checked cavity by cavity."), ("Leak & Valve Test", "Valve opening and seal performance are verified."), ("Actuation Cycle Test", "Repeated operation checks the user-facing mechanism."), ("ISO 9001 Certified", "Quality records accompany the final samples.")],
        [("Can you build a combination cap?", "Yes. Insert, overmould, assembly and functional requirements are reviewed as one project."), ("How are valves tested?", "The valve, seal and intended product pressure are tested with the buyer's package."), ("Can the mechanism be changed later?", "A modular insert strategy can make future variants easier to maintain."), ("Do you supply trial samples?", "Every project includes agreed samples and inspection evidence before handover.")],
        [("The push-pull cap opened smoothly and stayed leak-free in production.", "Process engineer", "United States"), ("The combination mould simplified our assembly line changeover.", "Operations manager", "Mexico"), ("The functional trial caught the last small adjustment before release.", "Quality manager", "South Korea")],
    ),
    "plastic-handle-cap-mould": _spec(
        "Handle Mould", "for Durable Bottle Carrying", "Solutions",
        "/upload/Banner/handle-hero.jpg",
        [("6s", "Cycle Time"), ("48", "Max Cavities"), ("4", "Handle Variants"), ("3M+", "Mould Life")],
        [("Plastic Handle Mould", "/upload/product/month_2105/202105281747478932.jpg", "Handle tooling for oil bottles, water bottles and large containers."), ("Plastic Handle Mould", "/upload/product/month_2105/202105281747284286.jpg", "Round and size-specific grip geometries for different bottle interfaces."), ("Plastic Handle Mould", "/upload/product/month_2105/202105262015364802.jpg", "Ergonomic handle design with a controlled bottle connection."), ("Plastic Handle Mould", "/upload/product/month_2105/202105262012138550.jpg", "High-strength moulding for reusable and chemical containers."), ("24 Cavity Plastic Handle Mould", "/upload/product/month_2105/202105262010194667.jpg", "Multi-cavity production for repeatable handle weight and fit."), ("24 Cavity Plastic Handle Mould", "/upload/product/month_2105/202105262002365573.jpg", "Custom neck dimensions and load targets reviewed before tooling.")],
        [("High Load-Bearing", "Rib geometry and bottle interface are reviewed against the carrying load."), ("Wear-Resistant Steel", "The mould is designed around repeatable grip and ejection surfaces."), ("Fast Cycle Times", "Balanced cooling supports high-volume handle production."), ("Precision Tolerances", "Bottle fit and assembly dimensions are measured."), ("Modular Design", "Replaceable inserts support different handle sizes."), ("100% Testing", "Trial fit, weight and load evidence are captured before delivery.")],
        ("Cap Mould Manufacturing Advantages", [("High Precision Machining & Strict QC", "CNC, EDM and inspection protect the bottle interface and load-bearing geometry.", "/upload/Handle-Mould/precision-machining.jpg", ["Interface measurement", "Grip surface check", "Trial-fit report"]), ("Premium Steel & Fast Delivery", "A staged machining plan and spare-part notes reduce later downtime.", "/upload/Handle-Mould/steel-fast-delivery.jpg", ["Steel certificate", "Cavity balance", "Documented handover"])]),
        ["/upload/Handle-Mould/sample1.jpg", "/upload/Handle-Mould/sample2.jpg", "/upload/Handle-Mould/sample3.jpg", "/upload/Handle-Mould/sample4.jpg", "/upload/Handle-Mould/sample5.jpg", "/upload/Handle-Mould/sample6.jpg", "/upload/Handle-Mould/sample7.jpg", "/upload/Handle-Mould/sample8.jpg"],
        [("CMM Inspection", "Bottle interface and handle dimensions are recorded."), ("Load Test", "The handle is checked against the intended carrying load."), ("Weight Audit", "Material distribution supports repeatable assembly."), ("ISO 9001 Certified", "Quality records accompany the production samples.")],
        [("What bottle sizes can the handle support?", "The handle is matched to the bottle interface and carrying load, from small packs to 20L containers."), ("Can the handle be custom-shaped?", "Yes. Send the bottle and grip requirements for a design and mould review."), ("How do you check strength?", "Trial fit, weight and load checks are agreed before final release."), ("Can one mould support multiple sizes?", "A modular insert strategy can be evaluated when the interfaces are related.")],
        [("The handle stayed comfortable and secure during the full load test.", "Packaging engineer", "Vietnam"), ("The multi-cavity mould kept handle weight and fit consistent.", "Plant director", "Malaysia"), ("The bottle-interface report helped us approve the tool quickly.", "Product manager", "Saudi Arabia")],
        [("P-G27RAJcxs", "Plastic handle mould trial"), ("DquWhXWBscE", "Handle mould production")],
    ),
}

DETAILS.update({
    "five-gallon-water-cap-mould": _spec(
        "5 Gallon Water", "Cap Mould", "Solutions",
        "/assets/catalog/five-gallon-hero.webp",
        [("18.9L", "Bottle Format"), ("24", "Max Cavities"), ("3", "Seal Options"), ("5M+", "Mould Life")],
        [
            ("5 Gallon Water Cap Mould", "/assets/catalog/five-gallon-01.webp", "Heavy-gauge tooling for reusable water-cooler bottles and dispenser caps."),
            ("Tamper-Evident 5 Gallon Cap", "/assets/catalog/five-gallon-02.webp", "Tear-band and inner-plug geometry reviewed for clean opening and reliable sealing."),
            ("High-Output 5 Gallon Closure Mould", "/assets/catalog/five-gallon-03.webp", "Balanced cavities for repeatable cap weight, fit and production output."),
        ],
        [("Reliable Plug Seal", "The plug, thread and bottle finish are checked together."), ("Sanitisation Ready", "Material and geometry are reviewed around repeated cleaning cycles."), ("Stable Cap Weight", "Cavity balance protects repeatable resin distribution."), ("Dispenser Compatibility", "The cap interface stays aligned with the intended cooler or filling line."), ("Serviceable Inserts", "Replaceable wear parts keep maintenance practical."), ("Documented Trials", "Leak, fit and opening evidence stay with the handover file.")],
        ("Inside Our 5 Gallon Cap Mould Engineering", [("Plug Seal & Tear Band", "Seal lands and bridge geometry are reviewed against the reusable bottle and opening force.", "/assets/catalog/five-gallon-01.webp", ["Bottle finish review", "Controlled break force", "Leak and fit checks"]), ("Cooling & Cavity Balance", "Cooling and runner balance support repeatable cap weight across the full cavity set.", "/assets/catalog/five-gallon-02.webp", ["Balanced filling", "Thermal review", "Cavity identification"])]),
        ["/assets/catalog/five-gallon-hero.webp", "/assets/catalog/five-gallon-01.webp", "/assets/catalog/five-gallon-02.webp", "/assets/catalog/five-gallon-03.webp"],
        [("CMM Inspection", "Bottle interface and sealing dimensions are recorded."), ("Leak Test", "The cap and plug are checked against the intended bottle."), ("Opening Force", "Tear-band behaviour is reviewed with the buyer."), ("ISO 9001 Records", "Quality evidence remains attached to the mould project.")],
        [("Can the mould support reusable water bottles?", "Yes. The bottle finish, plug seal and sanitisation conditions are included in the tooling brief."), ("How is the tear band checked?", "The bridge layout and opening force are agreed and verified during trial."), ("Can the cap fit a different dispenser?", "Send the dispenser and bottle interface for a compatibility review."), ("Do you provide trial samples?", "Agreed samples, fit checks and inspection evidence are included before handover.")],
        [("The cap stayed secure through repeated cooler handling.", "Packaging engineer", "Mexico"), ("The leak and opening checks made approval straightforward.", "Quality manager", "Chile"), ("Cavity weight stayed consistent across the run.", "Plant manager", "Brazil")],
    ),
    "wine-cap-mould": _spec(
        "Wine & Spirits", "Cap Mould", "Solutions",
        "/assets/catalog/wine-hero.webp",
        [("5s", "Cycle Target"), ("48", "Max Cavities"), ("4", "Closure Styles"), ("5M+", "Mould Life")],
        [
            ("Wine Cap Mould", "/assets/catalog/wine-01.webp", "Precision closure tooling for wine, spirits and specialty beverage packaging."),
            ("Decorative Wine Closure Mould", "/assets/catalog/wine-02.webp", "Surface and colour references are kept with the bottle and brand brief."),
            ("Pourer Wine Cap Mould", "/assets/catalog/wine-03.webp", "Pourer, tamper-evident and reclose features reviewed for the filling line."),
        ],
        [("Bottle-Finish Matching", "The cap, thread and bottle finish are reviewed as one interface."), ("Controlled Pouring", "A pourer or spout is checked for flow and reclose behaviour."), ("Decorative Surfaces", "Polishing, texture and visible surfaces are protected during ejection."), ("Tamper Evidence", "Opening evidence is designed around the buyer's package and market."), ("Balanced Cavities", "Runner and cooling balance protect consistent appearance."), ("Traceable Handover", "Approved samples and visual standards remain attached to the project.")],
        ("Inside Our Wine Cap Mould Engineering", [("Pourer & Seal Geometry", "The pourer, sealing land and bottle finish are reviewed for clean dispensing.", "/assets/catalog/wine-01.webp", ["Flow-path review", "Bottle fit check", "Reclose inspection"]), ("Surface Finish & Ejection", "Polished or textured cosmetic surfaces are protected through the ejection sequence.", "/assets/catalog/wine-02.webp", ["Texture reference", "Gate-mark control", "Visual approval sample"])]),
        ["/assets/catalog/wine-hero.webp", "/assets/catalog/wine-01.webp", "/assets/catalog/wine-02.webp", "/assets/catalog/wine-03.webp"],
        [("CMM Inspection", "Critical fit and pouring dimensions are recorded."), ("Fit & Leak Test", "The closure is checked on the intended bottle finish."), ("Visual Approval", "Colour, texture and gate-mark limits are agreed."), ("ISO 9001 Records", "Quality evidence stays with the tooling handover.")],
        [("Can you match an existing wine closure?", "Yes. Send the bottle, cap or drawing for a fit, pourer and surface review."), ("Can the cap include a pourer?", "Pourer geometry and flow requirements can be included in the DFM brief."), ("How are decorative surfaces protected?", "Gate, ejection and polishing decisions are reviewed around the approved visual sample."), ("Do you support small and large cavity counts?", "Cavity count is matched to the bottle format, output target and machine interface.")],
        [("The pourer and bottle fit were stable on the filling line.", "Packaging manager", "Italy"), ("The visual sample helped us approve the decorative finish.", "Brand engineer", "France"), ("The trial evidence made the closure decision easier.", "Operations director", "Portugal")],
    ),
    "pet-preform-mould": _spec(
        "PET Preform", "Injection", "Moulds",
        "/assets/catalog/preform-hero.webp",
        [("12–144", "Cavity Range"), ("PET / PP", "Resin Options"), ("±0.01mm", "Critical Fit"), ("5M+", "Mould Life")],
        [
            ("Multi-Cavity PET Preform Mould", "/assets/catalog/preform-01.webp", "Preform tooling for beverage neck finishes, stable gram weight and high output."),
            ("Valve-Type PET Preform Mould", "/assets/catalog/preform-02.webp", "Valve-gate layout and cooling are matched to the resin and machine interface."),
            ("Edible Oil Preform Mould", "/assets/catalog/preform-03.webp", "Preform tooling for oil and specialty packaging with controlled wall distribution."),
        ],
        [("Neck-Finish Accuracy", "Critical threads and sealing dimensions are checked cavity by cavity."), ("Gram-Weight Control", "Runner, gate and cooling choices protect repeatable preform weight."), ("PET & PP Options", "Material assumptions stay linked to shrinkage and stretch-blow targets."), ("Valve-Gate Balance", "Balanced filling supports clean gates and stable cycle behaviour."), ("Modular Cavities", "Cavity expansion and service decisions are considered early."), ("Machine Interface", "The mould brief includes the actual injection machine and hot-runner data.")],
        ("Inside Our Preform Mould Engineering", [("Neck Finish & Valve Gates", "Neck geometry and gate design are reviewed against the bottle and stretch-blow process.", "/assets/catalog/preform-01.webp", ["PCO and custom finishes", "Valve-gate review", "Cavity identification"]), ("Cooling & Wall Distribution", "Cooling layout and material data support predictable preform dimensions and weight.", "/assets/catalog/preform-02.webp", ["Thermal balance", "Wall-map review", "Dimensional sampling"])]),
        ["/assets/catalog/preform-hero.webp", "/assets/catalog/preform-01.webp", "/assets/catalog/preform-02.webp", "/assets/catalog/preform-03.webp"],
        [("CMM Inspection", "Neck finish and critical dimensions are recorded."), ("Weight Audit", "Preform weight is checked across the cavity set."), ("Gate Inspection", "Gate appearance and vestige limits are reviewed."), ("Material Traceability", "Resin and steel documentation accompany the handover.")],
        [("Which cavity counts are possible?", "The cavity plan is matched to the bottle, machine and output target, from pilot configurations to high-cavity production."), ("Can you make edible-oil preforms?", "Yes. The resin, neck finish, wall distribution and stretch-blow target are reviewed together."), ("How do you control preform weight?", "Runner balance, gate design, cooling and cavity-by-cavity weight checks are used."), ("Can a preform mould be upgraded?", "A modular insert and cavity strategy can be evaluated when the machine and geometry allow it.")],
        [("The neck finish stayed consistent across the complete cavity set.", "Process engineer", "Thailand"), ("The weight audit helped us stabilise the blowing process.", "Production manager", "Vietnam"), ("The DFM report clarified the machine interface before steel release.", "Tooling buyer", "Turkey")],
    ),
    "blow-bottle-mould": _spec(
        "Blow Bottle", "Mould", "Solutions",
        "/assets/catalog/blow-hero.webp",
        [("2–16", "Cavity Range"), ("PET", "Primary Resin"), ("360°", "Wall Review"), ("3M+", "Mould Life")],
        [
            ("PET Blow Bottle Mould", "/assets/catalog/blow-01.webp", "Bottle-blow tooling for repeatable shape, neck finish and wall distribution."),
            ("Wide-Mouth Bottle Mould", "/assets/catalog/blow-02.webp", "Wide-mouth and specialty container tooling with controlled cooling surfaces."),
            ("Custom Shape Blow Mould", "/assets/catalog/blow-03.webp", "Custom bottle geometry reviewed from drawing, preform and machine envelope."),
        ],
        [("Wall-Thickness Control", "The preform, stretch ratio and bottle wall map are reviewed together."), ("Cooling Balance", "Cooling surfaces support stable shape and cycle repeatability."), ("Neck-Finish Fit", "The bottle neck stays matched to the approved closure and cap."), ("Machine Envelope", "Opening, mould height and blow-machine data are confirmed early."), ("Custom Geometry", "Handles, panels and special shapes are checked against the drawing."), ("Trial Evidence", "Bottle samples, dimensions and visual limits guide handover.")],
        ("Inside Our Blow Bottle Mould Engineering", [("Preform & Stretch-Ratio Review", "The mould is developed from the preform, bottle drawing and intended stretch-blow process.", "/assets/catalog/blow-01.webp", ["Preform compatibility", "Stretch-ratio review", "Neck alignment"]), ("Cooling & Surface Quality", "Cooling and surface finish protect bottle appearance and dimensional stability.", "/assets/catalog/blow-02.webp", ["Cooling-channel review", "Parting-line control", "Visual approval sample"])]),
        ["/assets/catalog/blow-hero.webp", "/assets/catalog/blow-01.webp", "/assets/catalog/blow-02.webp", "/assets/catalog/blow-03.webp"],
        [("Dimensional Inspection", "Bottle height, neck and critical panels are recorded."), ("Wall Review", "Wall distribution is checked against the approved bottle brief."), ("Leak & Fit Test", "The bottle is checked with the intended closure and filling conditions."), ("Material Traceability", "Steel and process records accompany the final samples.")],
        [("Can you develop a custom bottle shape?", "Yes. Send the drawing, preform and machine envelope for a feasibility and DFM review."), ("How is wall thickness controlled?", "The preform, stretch ratio, cooling and bottle wall map are reviewed before trial."), ("Can you match an existing bottle?", "A bottle sample, drawing or scan can be used to review the neck, parting and key surfaces."), ("Do you supply trial bottles?", "Agreed trial samples and dimensional evidence are prepared before handover.")],
        [("The bottle shape and neck fit matched our approved drawing.", "Packaging engineer", "Indonesia"), ("Cooling changes improved repeatability across the run.", "Production director", "India"), ("The trial report made the custom bottle approval clear.", "Project manager", "Spain")],
    ),
})


def _lang(locale: str, key: str) -> str:
    values = {
        "en": {"our_products": "Our Products", "advantages": "Why Our Moulds", "technology": "Technology", "samples": "Samples", "videos": "Mould Trials", "quality": "Quality", "faq": "Common Questions", "feedback": "Client Feedback", "contact": "Start Your Mould Project", "learn": "Learn More →", "quote": "Request a Quote", "home": "Home", "cap_mould": "Cap Mould"},
        "es": {"our_products": "Nuestros productos", "advantages": "Por qué nuestros moldes", "technology": "Tecnología", "samples": "Muestras", "videos": "Pruebas del molde", "quality": "Calidad", "faq": "Preguntas frecuentes", "feedback": "Opiniones de clientes", "contact": "Inicie su proyecto", "learn": "Ver detalles →", "quote": "Solicitar cotización", "home": "Inicio", "cap_mould": "Moldes de tapas"},
    }
    return values.get(locale, values["en"]).get(key, values["en"].get(key, key))

def _catalog_text(item: dict, locale: str, key: str) -> str:
    if locale == "es":
        translated = item.get(key + "Es")
        if isinstance(translated, str) and translated.strip():
            return translated.strip()
    return str(item.get(key) or "")

def _model_text(item: dict, locale: str, key: str) -> str:
    """Read reviewed per-locale model copy, falling back to source English."""
    translations = item.get("translations") if isinstance(item.get("translations"), dict) else {}
    localized = translations.get(locale) if isinstance(translations.get(locale), dict) else {}
    value = localized.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return str(item.get(key) or "").strip()


def render_model_reference_section(locale: str, models: list[dict], helpers: dict, heading: str | None = None) -> str:
    """Render imported HMould model references inside the existing catalogue shell.

    The records are labelled as references so a catalogue image or model name
    never silently becomes an unverified LEYA production claim. Each card still
    feeds the existing enquiry route, preserving the site's current conversion
    and admin workflow.
    """
    if not models:
        return ""
    esc = helpers["esc"]
    href = helpers["localized_href"]
    image = helpers["image"]
    es = locale == "es"
    section_heading = heading or ("Referencias de modelos" if es else "Model References")
    section_copy = (
        "Modelos de referencia organizados para revisar geometría, cavidades, máquina y evidencia antes de cotizar."
        if es else
        "Imported model references organised for a technical review of geometry, cavities, machine interface and evidence before quotation."
    )
    inquire = "Consultar este modelo →" if es else "Discuss this model →"
    source_label = "Referencia HMould" if es else "HMould reference"
    cards = []
    for model in models:
        title = _model_text(model, locale, "title") or "Model reference"
        alt = _model_text(model, locale, "alt") or title
        model_url = href(locale, "/contact/?model=" + str(model.get("slug") or "") + "#inquiry")
        model_image = str(model.get("image") or "/assets/mould-placeholder.svg")
        description = _model_text(model, locale, "description")
        cards.append(
            '<article class="mould-model-card">'
            '<div class="mould-model-card__image">' + image(model_image, alt) + '</div>'
            '<div class="mould-model-card__body">'
            '<span class="mould-model-card__source">' + esc(source_label) + '</span>'
            '<h3>' + esc(title) + '</h3>'
            '<p>' + esc(description if not es else "Referencia de catálogo para revisar geometría, cavidades, máquina y requisitos de producción.") + '</p>'
            '<a href="' + esc(model_url) + '">' + esc(inquire) + '</a>'
            '</div></article>'
        )
    return (
        '<section class="mould-model-references" id="model-references">'
        '<div class="mould-detail-container">'
        '<div class="mould-section-heading"><span>' + esc(section_heading.upper()) + '</span>'
        '<h2>' + esc(section_heading) + '</h2><p>' + esc(section_copy) + '</p><i></i></div>'
        '<div class="mould-model-grid">' + ''.join(cards) + '</div>'
        '</div></section>'
    )


def render_category_page(locale: str, item: dict, helpers: dict) -> str:
    """Render a full reference-style page while reusing shared site helpers."""
    esc = helpers["esc"]
    href = helpers["localized_href"]
    details = DETAILS[item["slug"]]
    title = _catalog_text(item, locale, "title")
    description = _catalog_text(item, locale, "description")
    detail = _structured_text(item, locale, "body", _catalog_text(item, locale, "detail"))
    hero_title = esc(details["hero_title"]) + ' <span class="highlight">' + esc(details["hero_accent"]) + '</span> ' + esc(details["hero_subtitle"])
    hero = '<section class="mould-detail-hero" style="--mould-hero:url(\'' + esc(_asset(details["hero_image"])) + '\')"><div class="mould-detail-container"><h1>' + hero_title + '</h1><p class="mould-hero-subtitle">' + esc(description) + ' ' + esc(detail) + '</p><a href="#contact" class="mould-hero-cta">' + esc(_lang(locale, "quote")) + ' →</a><div class="mould-hero-stats">' + ''.join('<div class="mould-hero-stat"><div class="number">' + esc(number) + '</div><div class="label">' + esc(label) + '</div></div>' for number, label in details["stats"]) + '</div></div></section>'
    # Keep the hero copy to the same concise rhythm as the reference page.
    hero = hero.replace(esc(description) + ' ' + esc(detail), esc(description))
    reference_description = REFERENCE_HERO_DESCRIPTIONS.get(item["slug"], description)
    if locale == "es" and item.get("descriptionEs"):
        reference_description = description
    hero = hero.replace(esc(description), esc(reference_description))
    hero = hero.replace('class="mould-detail-hero"', 'class="mould-detail-hero mould-detail-hero--' + item["slug"] + '"', 1)
    crumb = '<nav class="mould-breadcrumb" aria-label="Breadcrumb"><div class="mould-detail-container"><a href="' + href(locale, "/") + '">' + esc(_lang(locale, "home")) + '</a><span>/</span><a href="' + href(locale, "/Plastic-cap-mold.html") + '">' + esc(_lang(locale, "cap_mould")) + '</a><span>/</span><span>' + esc(title) + '</span></div></nav>'

    products = '<section class="mould-products" id="products"><div class="mould-detail-container"><div class="mould-section-heading"><span>' + esc(_lang(locale, "our_products")) + '</span><h2>' + esc(details["hero_title"] + " " + details["hero_accent"]) + ' Types</h2><p>' + esc(detail) + '</p><i></i></div><div class="mould-products-grid">'
    for product_title, product_image, product_desc in details["products"]:
        products += '<a href="#contact" class="mould-product-card"><div class="mould-card-img">' + helpers["image"](_asset(product_image), product_title) + '</div><div class="mould-card-body"><h3>' + esc(product_title) + '</h3><p>' + esc(product_desc) + '</p><span>' + esc(_lang(locale, "learn")) + '</span></div></a>'
    products += '</div></div></section>'
    model_references = render_model_reference_section(
        locale,
        [row for row in helpers.get("hmould_models", []) if row.get("family") == item["slug"]],
        helpers,
    )

    advantages = '<section class="mould-advantages" id="advantages"><div class="mould-detail-container"><div class="mould-section-heading"><span>' + esc(_lang(locale, "advantages")) + '</span><h2>Key Advantages of Our ' + esc(title) + '</h2><p>Engineered for repeatable production, stable quality and a clear technical handover.</p><i></i></div><div class="mould-advantages-grid">'
    for adv_title, adv_text in details["advantages"]:
        advantages += '<article class="mould-advantage-card"><div class="mould-adv-icon">✓</div><h4>' + esc(adv_title) + '</h4><p>' + esc(adv_text) + '</p></article>'
    advantages += '</div></div></section>'

    structured_technology = _structured_sections(item, locale, details["technology"][1])
    tech = '<section class="mould-technology" id="technical"><div class="mould-detail-container"><div class="mould-section-heading"><span>' + esc(_lang(locale, "technology")) + '</span><h2>' + esc(details["technology"][0]) + '</h2><i></i></div>'
    for index, (tech_title, tech_text, tech_image, bullets) in enumerate(structured_technology):
        media = '<div class="mould-tech-image">' + helpers["image"](_asset(tech_image), tech_title) + '</div>'
        copy = '<div class="mould-tech-copy"><h3>' + esc(tech_title) + '</h3><p>' + esc(tech_text) + '</p><ul>' + ''.join('<li>✓ ' + esc(bullet) + '</li>' for bullet in bullets) + '</ul></div>'
        tech += '<div class="mould-tech-grid' + (' mould-tech-grid--reverse' if index % 2 else '') + '">' + (copy + media if index % 2 else media + copy) + '</div>'
    tech += '</div></section>'

    samples = '<section class="mould-samples" id="samples"><div class="mould-detail-container"><div class="mould-section-heading"><span>' + esc(_lang(locale, "samples")) + '</span><h2>' + esc(title) + ' Gallery</h2><p>Click any image to enlarge. Samples and reference parts are shown for technical discussion.</p><i></i></div><div class="mould-samples-grid">'
    for sample in details["samples"]:
        samples += '<button class="mould-sample" type="button" data-mould-lightbox="' + esc(_asset(sample)) + '">' + helpers["image"](_asset(sample), title + " sample") + '</button>'
    samples += '</div></div></section>'

    videos = ''
    if details["videos"]:
        videos = '<section class="mould-videos" id="videos"><div class="mould-detail-container"><div class="mould-section-heading"><span>' + esc(_lang(locale, "videos")) + '</span><h2>' + esc(title) + ' Trial Videos</h2><p>Watch the mould trial and production references in full screen.</p><i></i></div><div class="mould-videos-grid">'
        for video_id, video_title in details["videos"]:
            videos += '<button class="mould-video-card" type="button" data-mould-video="' + esc(video_id) + '"><div class="mould-video-thumb"><img src="https://img.youtube.com/vi/' + esc(video_id) + '/mqdefault.jpg" alt="' + esc(video_title) + '"><b>▶</b></div><span>' + esc(video_title) + '</span></button>'
        videos += '</div></div></section>'

    quality = '<section class="mould-quality" id="quality"><div class="mould-detail-container"><div class="mould-section-heading"><span>' + esc(_lang(locale, "quality")) + '</span><h2>Quality Control &amp; Inspection</h2><p>Every mould passes a documented inspection path before shipment.</p><i></i></div><div class="mould-quality-list">' + ''.join('<article><b>✓</b><h4>' + esc(q) + '</h4><p>' + esc(a) + '</p></article>' for q, a in details["quality"]) + '</div></div></section>'

    faq_pairs = _structured_faqs(item, locale, details["faqs"])
    faq_rows = ''.join('<details><summary>' + esc(q) + '</summary><p>' + esc(a) + '</p></details>' for q, a in faq_pairs)
    feedback = ''.join('<article class="mould-testimonial"><p>“' + esc(quote) + '”</p><b>' + esc(author) + '</b><span>' + esc(country) + '</span></article>' for quote, author, country in details["testimonials"])
    faq = '<section class="mould-faq" id="faq"><div class="mould-detail-container"><div class="mould-faq-grid"><div><div class="mould-section-heading mould-section-heading--left"><span>' + esc(_lang(locale, "faq")) + '</span><h2>' + esc(title) + ' FAQ</h2><i></i></div><div class="mould-faq-list">' + faq_rows + '</div></div><div><div class="mould-section-heading mould-section-heading--left"><span>' + esc(_lang(locale, "feedback")) + '</span><h2>What Buyers Say</h2><i></i></div><div class="mould-testimonials">' + feedback + '</div></div></div></div></section>'

    shared_cta = helpers.get("shared_cta")
    cta = shared_cta(locale, "category", element_id="contact") if shared_cta else '<section class="mould-cta" id="contact"><div class="mould-detail-container"><div class="mould-cta-box"><h2>' + esc(_lang(locale, "contact")) + '</h2><p>Send us your drawing, sample, target material, cavity plan and delivery market. We will reply with the next technical questions.</p><div class="mould-cta-row"><a href="mailto:amyhu@leyamould.com" class="mould-cta-item">✉ amyhu@leyamould.com</a><a href="https://wa.me/8613606727715" class="mould-cta-item" target="_blank" rel="noopener">WhatsApp +8613606727715</a><a href="' + href(locale, "/contact/#inquiry") + '" class="mould-cta-item mould-cta-item--accent">' + esc(_lang(locale, "quote")) + ' →</a></div></div></div></section>'

    lightbox = '<div class="mould-lightbox" id="mould-lightbox" aria-hidden="true"><button type="button" aria-label="Close" data-mould-close>×</button><img alt=""></div><div class="mould-video-lightbox" id="mould-video-lightbox" aria-hidden="true"><button type="button" aria-label="Close" data-mould-video-close>×</button><iframe title="Mould trial video" allow="autoplay; encrypted-media" allowfullscreen></iframe></div><script>(()=>{const l=document.getElementById("mould-lightbox"),li=l?.querySelector("img"),v=document.getElementById("mould-video-lightbox"),f=v?.querySelector("iframe");const close=()=>{l?.classList.remove("active");v?.classList.remove("active");if(f)f.src=""};document.addEventListener("click",e=>{const s=e.target.closest("[data-mould-lightbox]");if(s&&li){li.src=s.dataset.mouldLightbox;l.classList.add("active")};const b=e.target.closest("[data-mould-video]");if(b&&f){f.src="https://www.youtube.com/embed/"+b.dataset.mouldVideo+"?autoplay=1&rel=0";v.classList.add("active")};if(e.target.closest("[data-mould-close],[data-mould-video-close]")||e.target===l||e.target===v)close()});document.addEventListener("keydown",e=>{if(e.key==="Escape")close()})})();</script>'
    return '<div class="mould-detail-page mould-detail-page--' + item["slug"] + '">' + hero + crumb + products + model_references + advantages + tech + samples + videos + quality + faq + cta + lightbox + '</div>'
