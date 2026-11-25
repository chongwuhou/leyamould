"""Repair the locale placement of the catalogue support payload after migration."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "data" / "mould-page-structured.json"


class Pairs(list):
    pass


def pairs_hook(pairs):
    return Pairs(pairs)


def convert(value):
    if isinstance(value, Pairs):
        return {key: convert(item) for key, item in value}
    if isinstance(value, list):
        if value and all(isinstance(item, list) and len(item) == 2 and isinstance(item[0], str) for item in value):
            return {key: convert(item) for key, item in value}
        return [convert(item) for item in value]
    if isinstance(value, dict):
        return {key: convert(item) for key, item in value.items()}
    return value


def english_sections():
    sample_items = [{"title": f"Bottle cap sample {index:02d}", "image": f"/upload/caps/Bottle-cap-sample{index:02d}.jpg", "alt": f"Bottle cap sample {index:02d}"} for index in range(1, 22)]
    return [
        {"id": "advantages", "eyebrow": "WHY CHOOSE US", "title": "Core Advantages of LEYA MOULD", "body": "From mould design to trial delivery, we deliver value through engineering excellence and strict quality control.", "items": [{"title": title, "body": body} for title, body in [("Premium Steel", "ASSAB and DAIDO certified steel options support long service life and stable production."), ("Micron Precision", "CNC, EDM and measured fitting keep critical cap dimensions within the approved tooling brief."), ("Fast Cycles", "Balanced runners and cooling are reviewed against the output target before trial."), ("Custom Solutions", "The mould plan is matched to the closure geometry, resin, machine and cavity requirement."), ("Lifetime Support", "Remote guidance, maintenance notes and spare-part recommendations remain connected to the handover."), ("On-Time Delivery", "A staged production plan keeps design review, machining, trial and delivery visible.")]]},
        {"id": "samples", "eyebrow": "CAP SAMPLES", "title": "Bottle Cap Sample Gallery", "body": "Click any image to enlarge. Samples and reference parts are shown for technical discussion.", "items": sample_items},
        {"id": "technology", "eyebrow": "TECHNOLOGY", "title": "Technical Strength & Process", "body": "From initial 3D mould-flow review to final polishing, integrated manufacturing keeps quality consistent and lead times visible.", "items": [{"title": title, "body": body} for title, body in [("3D Design & Simulation", "Advanced CAD and CAE review gate location, parting and cooling before steel is cut."), ("Precision Machining", "High-speed CNC, wire EDM and jig grinding deliver the dimensional control required for cap tooling."), ("Heat Treatment", "Vacuum heat treatment is selected to maintain hardness, stability and wear resistance."), ("Conformal Cooling", "Cooling layouts are matched to wall thickness and cycle targets where the project requires it."), ("Automated Polishing", "Controlled polishing protects cosmetic surfaces and supports reliable part release."), ("Material Expertise", "PP, HDPE, LDPE, PET and specialty polymers are considered in the tooling brief.")]]},
        {"id": "quality", "eyebrow": "QUALITY", "title": "Quality Control & Inspection", "body": "Every mould passes a documented inspection path from raw steel to final trial before shipment.", "items": [{"label": label, "title": title, "body": body} for label, title, body in [("01", "Steel inspection", "Material certificates and heat-treatment records are checked before machining."), ("02", "In-process measurement", "Critical dimensions, cooling circuits and fitting points are measured during production."), ("03", "Pre-shipment trial", "Trial parts, cycle notes and agreed inspection points are reviewed before handover."), ("04", "Documented support", "Drawings, reports and approved revisions stay attached to the project for future service.")]]},
        {"id": "workflow", "eyebrow": "WORKFLOW", "title": "Cooperation Process", "body": "A transparent, step-by-step approach from initial inquiry to final delivery keeps your project on track.", "items": [{"label": label, "title": title, "body": body} for label, title, body in [("01", "Share Design", "Send your drawing or sample for an initial technical review."), ("02", "DFM Analysis", "Review mould flow, parting, cooling and optimisation opportunities."), ("03", "Manufacturing", "Coordinate precision machining, EDM, fitting and heat treatment."), ("04", "Trial & Inspection", "Complete trial runs, dimensional checks and agreed inspection evidence."), ("05", "Delivery & Support", "Keep approved files, delivery notes and technical support connected.")]]},
        {"id": "faq", "eyebrow": "FAQ", "title": "Common Questions", "body": "Quick answers about design, trials, lead times and support.", "items": [{"question": question, "answer": answer} for question, answer in [("What information should I send for a quotation?", "Please share the cap drawing or sample, material, cavity count, machine interface and target output."), ("Can you make a custom cap mould?", "Yes. We review the part geometry, sealing surfaces, cooling, ejection and trial requirements before confirming the design."), ("What is the normal lead time?", "A standard sample mould often takes 15–25 days; production tooling is normally 35–55 days depending on complexity."), ("Do you test samples before shipment?", "Yes. Trial parts, dimensional checks and approved revision notes are kept with the handover package."), ("Which steels are available?", "S136, NAK80, H13 and equivalent grades can be selected according to resin, cycle and service-life targets."), ("Do you support international buyers?", "Yes. We coordinate export packing, documentation and delivery for international projects."), ("Can you supply auxiliary machines?", "Yes. Lining, assembly, folding, slitting and other auxiliary equipment can be coordinated for a complete cell."), ("How do I start a project?", "Send the drawing, sample, resin, cavities, machine information and destination market by email or WhatsApp.")]]},
        {"id": "testimonials", "eyebrow": "CLIENT FEEDBACK", "title": "Client Feedback", "body": "Published customer feedback appears here after the source and publication review."},
        {"id": "videos", "eyebrow": "MOULD TRIALS", "title": "Cap Mould Trial Videos", "body": "Watch the latest mould trial videos managed from the YouTube video module."},
    ]


def main() -> None:
    root_pairs = json.loads(TARGET.read_text(encoding="utf-8"), object_pairs_hook=pairs_hook)
    en_pairs = next(value for key, value in root_pairs if key == "en")
    es_pairs = next(value for key, value in root_pairs if key == "es")
    en = convert(en_pairs)
    es = convert(es_pairs)
    # The Spanish payload was temporarily inserted under the English locale;
    # keep it under es and restore the complete reviewed English baseline.
    spanish = es.get("/Plastic-cap-mold.html") or en.get("/Plastic-cap-mold.html")
    en["/Plastic-cap-mold.html"] = {"sections": english_sections()}
    if spanish:
        es["/Plastic-cap-mold.html"] = spanish
    output = {"en": en, "es": es}
    TARGET.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
