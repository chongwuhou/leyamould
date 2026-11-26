"""Build the reviewed bilingual product-family content pack.

This produces a draft only.  It is intentionally not a D1 client: the formal
admin endpoint remains the only production write path.  Each family has its
own scenario, buyer-input list, engineering review, quotation checklist and
FAQ copy in both locales.
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "mould-product-content-draft.json"

SOURCES = {
    "cetie": {"label": "CETIE GME 32.04 · PCO 1881 finish", "url": "https://cetie-standard.com/206-document-gme3204-pet-pco-finish-28-22-17-1-27", "note": "Finish terminology and interface reference; confirm the buyer drawing."},
    "husky": {"label": "Husky PET tooling reference", "url": "https://www.husky.co/en/solutions/pet-tooling/", "note": "Industry context for PET preform tooling; not a LEYA performance claim."},
    "uddeholm": {"label": "Uddeholm · Steel for moulds", "url": "https://www.uddeholm.com/app/uploads/sites/242/2024/05/Tech-Uddeholm-Steel-for-moulds-EN.pdf", "note": "Steel-selection factors such as wear, corrosion and hardness."},
    "cap": {"label": "CAP Moulds category reference", "url": "https://www.cap-molds.com/Plastic-cap-mold.html", "note": "Product-family vocabulary only; project requirements still govern."},
    "hmould": {"label": "HMould product catalogue", "url": "https://www.hmould.com/products/", "note": "Model-family reference for enquiry scoping; not a LEYA specification."},
}


def brief(scenarios, parameters, checklist, source_keys, note, locale):
    return {
        "scenarios": [{"title": title, "body": body} for title, body in scenarios],
        "parameters": [{"title": title, "body": body} for title, body in parameters],
        "quoteChecklist": list(checklist),
        "sources": [SOURCES[key] for key in source_keys],
        "evidenceNote": note,
    }


def section(rows):
    return [{"title": title, "body": body, "bullets": bullets} for title, body, bullets in rows]


def faq(rows):
    return [{"question": question, "answer": answer} for question, answer in rows]


FAMILIES = {
    "mineral-water-closure-cap-molds": {
        "en": {
            "title": "Mineral Water Closure Cap Moulds", "description": "Closure tooling for still, sparkling and treated-water bottles where the neck finish, seal and tamper evidence must remain aligned.",
            "scenarios": [("Still and sparkling water", "Match a beverage neck finish, cap seal and tamper band to the approved bottle and filling line."), ("Lightweight closure development", "Review material distribution, opening torque and bridge behaviour before selecting a cavity plan.")],
            "parameters": [("Neck finish", "Provide the finish drawing or standard reference, such as PCO 1881, including thread, bead and sealing surfaces."), ("Resin and cap weight", "State the resin grade, target weight, colour and any recycled-content requirement."), ("Line interface", "Share the machine, hot-runner preference, target output and inspection points.")],
            "checklist": ["Approved neck and cap drawings", "Resin, colour and target weight", "Machine and cavity/output target", "Trial, inspection and packaging requirements"],
            "process": [("Finish and seal review", "LEYA checks the neck drawing, sealing lands, thread release and tamper-band geometry before steel is released.", ["Drawing revision recorded", "Material and weight assumptions listed", "Critical dimensions marked"]), ("Trial and evidence plan", "The agreed mould trial links cap samples, dimensional checks and the buyer's acceptance limits.", ["Machine information confirmed", "Sample quantity agreed", "Final result follows the approved drawing and trial record"])],
            "faqs": [("Which neck-finish information is needed?", "Send the neck drawing or named finish, plus the bottle drawing if the closure and container are being developed together."), ("Can the cap be lightweighted?", "Yes, lightweighting can be reviewed through the cap drawing, resin, target weight, seal load and trial criteria."), ("Do you quote a cavity number without a drawing?", "We can give a preliminary range, but the formal quotation follows review of the part, machine and output brief."), ("What proves the final result?", "Approved drawings, trial samples and the agreed inspection record are the basis for project confirmation.")],
            "sources": ["cetie", "cap"], "note": "Industry references guide the discussion; the final closure design is subject to drawings, mould trial and project confirmation.",
        },
        "es": {
            "title": "Moldes de tapas para agua mineral", "description": "Moldes para tapas de botellas de agua sin gas, con gas y tratada, manteniendo alineados el cuello, el sellado y la banda de inviolabilidad.",
            "scenarios": [("Agua sin gas y con gas", "Ajustar el acabado del cuello, el sellado y la banda de inviolabilidad al envase y a la línea aprobados."), ("Desarrollo de tapas ligeras", "Revisar la distribución del material, el par de apertura y los puentes antes de definir las cavidades.")],
            "parameters": [("Acabado del cuello", "Enviar el plano o la referencia del estándar, por ejemplo PCO 1881, con rosca, anillo y superficies de sellado."), ("Resina y peso", "Indicar resina, peso objetivo, color y cualquier requisito de material reciclado."), ("Interfaz de línea", "Compartir máquina, opción de canal caliente, producción objetivo y puntos de inspección.")],
            "checklist": ["Planos aprobados de cuello y tapa", "Resina, color y peso objetivo", "Máquina y objetivo de cavidades/producción", "Requisitos de prueba, inspección y embalaje"],
            "process": [("Revisión de acabado y sellado", "LEYA revisa el plano del cuello, las superficies de sellado, la salida de rosca y la banda antes de liberar el acero.", ["Revisión del plano registrada", "Supuestos de material y peso listados", "Cotas críticas marcadas"]), ("Plan de prueba y evidencias", "La prueba acordada relaciona muestras, controles dimensionales y límites de aceptación del comprador.", ["Datos de la máquina confirmados", "Cantidad de muestras acordada", "El resultado final sigue el plano y el acta de prueba"])],
            "faqs": [("¿Qué datos del cuello son necesarios?", "Envíe el plano o acabado nominal y, si se desarrollan juntos, también el plano de la botella."), ("¿Se puede aligerar la tapa?", "Sí. Se revisan plano, resina, peso objetivo, carga de sellado y criterios de prueba."), ("¿Cotizan las cavidades sin plano?", "Podemos dar una orientación inicial; la cotización formal requiere revisar pieza, máquina y producción."), ("¿Qué confirma el resultado final?", "Los planos aprobados, las muestras de prueba y el registro de inspección acordado.")],
            "sources": ["cetie", "cap"], "note": "Las referencias orientan la conversación; el diseño final depende de planos, prueba del molde y confirmación del proyecto.",
        },
    },
    "oil-bottle-cap-mould": {
        "en": {
            "title": "Edible Oil Bottle Cap Moulds", "description": "Closure tooling for edible-oil bottles, with the sealing path, pull ring or flip top and filling-line handling reviewed as one package.",
            "scenarios": [("Cooking-oil bottles", "Develop pull-ring, tamper-evident or flip-top closures for edible-oil brands and contract packers."), ("Existing cap replacement", "Use an approved sample and bottle finish to review fit, opening behaviour and repeatability.")],
            "parameters": [("Seal and opening", "Share the sealing land, liner or plug details, opening torque and tamper-band requirement."), ("Food-contact brief", "Identify the resin, additives, colour and documentation the buyer expects from the part supplier."), ("Filling conditions", "Provide temperature, line speed, bottle finish, cap weight and leak-test method.")],
            "checklist": ["Cap and bottle drawings or samples", "Resin, colour and food-contact documentation", "Opening/sealing targets and leak-test method", "Machine, output and trial sample plan"],
            "process": [("Seal-path DFM", "LEYA reviews the sealing land, plug, bridge and parting line against the bottle finish and opening requirement.", ["Critical seal surfaces identified", "Bridge and ring release checked", "Draft and ejection risks recorded"]), ("Filling-line trial", "Samples are checked under the agreed oil, temperature and handling conditions before the buyer signs the project record.", ["Actual cap and bottle used where available", "Leak and fit checks recorded", "Result tied to approved revision"])],
            "faqs": [("Can an existing oil cap be copied?", "A drawing or physical sample can be reviewed for a compatible replacement; the bottle finish remains essential."), ("How should leakage be evaluated?", "Agree the oil, temperature, dwell time and pressure method before the trial so the evidence is comparable."), ("Which steel should be considered?", "Steel is selected after reviewing wear, corrosion, polishing and maintenance needs rather than by a fixed promise."), ("What should accompany a quote request?", "Send the cap/bottle geometry, resin, weight, line data, target output and acceptance method.")],
            "sources": ["cetie", "uddeholm"], "note": "Food-contact and leak performance must be confirmed with the buyer's materials, process and trial evidence.",
        },
        "es": {
            "title": "Moldes de tapas para botellas de aceite", "description": "Moldes para botellas de aceite comestible, revisando juntos el sellado, el anillo de seguridad o la tapa abatible y la manipulación en línea.",
            "scenarios": [("Botellas de aceite", "Desarrollar tapas de anillo, inviolables o abatibles para marcas de aceite y envasadores."), ("Sustitución de una tapa existente", "Usar muestra y acabado del cuello aprobados para revisar ajuste, apertura y repetibilidad.")],
            "parameters": [("Sellado y apertura", "Compartir superficies de sellado, liner o tapón, par de apertura y requisito de inviolabilidad."), ("Ficha de contacto alimentario", "Indicar resina, aditivos, color y documentación esperada del proveedor de piezas."), ("Condiciones de llenado", "Facilitar temperatura, velocidad, acabado de botella, peso y método de prueba de fugas.")],
            "checklist": ["Planos o muestras de tapa y botella", "Resina, color y documentación de contacto alimentario", "Objetivos de apertura/sellado y prueba de fugas", "Máquina, producción y plan de muestras"],
            "process": [("DFM del sellado", "LEYA revisa superficies de sellado, tapón, puentes y línea de partición respecto al cuello y la apertura.", ["Superficies críticas identificadas", "Salida del anillo revisada", "Riesgos de desmoldeo registrados"]), ("Prueba en línea", "Las muestras se comprueban con el aceite, temperatura y manipulación acordados antes de cerrar el acta.", ["Tapa y botella reales cuando sea posible", "Controles de fuga y ajuste registrados", "Resultado ligado a la revisión aprobada"])],
            "faqs": [("¿Se puede copiar una tapa de aceite existente?", "Sí, se puede revisar una muestra o plano para un reemplazo compatible; el cuello de la botella es imprescindible."), ("¿Cómo se evalúan las fugas?", "Se acuerdan aceite, temperatura, tiempo y método de presión antes de la prueba."), ("¿Qué acero se debe elegir?", "Se selecciona tras revisar desgaste, corrosión, pulido y mantenimiento, no mediante una promesa fija."), ("¿Qué debe incluir la solicitud?", "Geometría, resina, peso, datos de línea, producción objetivo y método de aceptación.")],
            "sources": ["cetie", "uddeholm"], "note": "El contacto alimentario y la estanqueidad se confirman con materiales, proceso y evidencias de prueba del comprador.",
        },
    },
    "flip-top-caps-mould": {
        "en": {
            "title": "Flip-Top Cap Moulds", "description": "Living-hinge and disc-top tooling for personal-care, household and travel packs where opening feel, hinge alignment and closure fit matter.",
            "scenarios": [("Shampoo and lotion packs", "Balance hinge feel, dispensing opening and snap closure for repeated consumer use."), ("Two-colour or decorated caps", "Separate cosmetic surfaces and functional interfaces while keeping the assembly repeatable.")],
            "parameters": [("Hinge geometry", "Provide the open angle, hinge thickness, expected flexing and resin grade."), ("Dispensing path", "State opening size, plug fit, wall thickness and the bottle neck interface."), ("Appearance limits", "Mark gate, weld-line, texture, colour and parting-line expectations on the sample or drawing.")],
            "checklist": ["Cap, bottle and hinge drawings", "Resin, colour and decoration limits", "Open/close force or user-feel target", "Machine, cycle objective and sample plan"],
            "process": [("Living-hinge DFM", "LEYA reviews hinge thickness, radii, gate position and ejection so the cap opens without damaging the hinge.", ["Flexing zone marked", "Parting and ejection reviewed", "Resin shrinkage assumptions recorded"]), ("Functional sample review", "Trial caps are checked for open angle, snap fit, dispensing and visual limits against the approved sample.", ["Open/close checks agreed", "Bottle fit confirmed", "Approved revision retained"])],
            "faqs": [("Which resin is suitable for a living hinge?", "The resin must be confirmed with the buyer because flow, fatigue behaviour, colour and process conditions affect the hinge."), ("Can you match an existing flip-top?", "Yes, send a sample, bottle finish and any force or angle requirement for a DFM review."), ("How is the hinge approved?", "The buyer and LEYA agree open/close checks, bottle fit, appearance limits and the trial record."), ("Can the cap be made in two colours?", "Two-colour feasibility depends on the parting, material pairing, machine and visual boundary defined in the brief.")],
            "sources": ["cap", "uddeholm"], "note": "Hinge life and user feel are confirmed by the specified resin, mould trial and approved project record.",
        },
        "es": {
            "title": "Moldes para tapas abatibles", "description": "Moldes para bisagras vivas y tapas disc-top de envases de cuidado personal, hogar y viaje, priorizando apertura, alineación y ajuste.",
            "scenarios": [("Envases de champú y loción", "Equilibrar sensación de bisagra, abertura de dispensación y cierre a presión."), ("Tapas bicolor o decoradas", "Separar superficies estéticas e interfaces funcionales manteniendo un montaje repetible.")],
            "parameters": [("Geometría de bisagra", "Indicar ángulo abierto, espesor, flexiones esperadas y resina."), ("Canal de dispensación", "Definir abertura, ajuste del tapón, pared y unión con el cuello."), ("Límites visuales", "Marcar entrada, líneas de soldadura, textura, color y línea de partición en plano o muestra.")],
            "checklist": ["Planos de tapa, botella y bisagra", "Resina, color y límites decorativos", "Objetivo de fuerza o sensación de apertura", "Máquina, ciclo y plan de muestras"],
            "process": [("DFM de la bisagra", "LEYA revisa espesor, radios, entrada y expulsión para evitar daños durante la apertura.", ["Zona flexible marcada", "Partición y expulsión revisadas", "Supuestos de contracción registrados"]), ("Revisión de muestra funcional", "Las tapas de prueba se comprueban por ángulo, ajuste, dispensación y límites visuales.", ["Controles de apertura acordados", "Ajuste en botella confirmado", "Revisión aprobada conservada"])],
            "faqs": [("¿Qué resina sirve para una bisagra viva?", "Debe confirmarse con el comprador porque flujo, fatiga, color y proceso afectan la bisagra."), ("¿Pueden igualar una tapa abatible existente?", "Sí, envíe muestra, acabado del cuello y requisito de fuerza o ángulo."), ("¿Cómo se aprueba la bisagra?", "Se acuerdan controles de apertura/cierre, ajuste, aspecto y registro de prueba."), ("¿Se puede fabricar en dos colores?", "Depende de partición, combinación de materiales, máquina y límite visual del proyecto.")],
            "sources": ["cap", "uddeholm"], "note": "La vida de la bisagra y la sensación de uso se confirman con resina, prueba del molde y registro aprobado.",
        },
    },
    "engine-oil-cap-mould": {
        "en": {
            "title": "Engine Oil Cap Moulds", "description": "Industrial closure tooling for engine oil, lubricant and fluid containers where chemical exposure, torque and seal geometry must be reviewed together.",
            "scenarios": [("Lubricant and ATF packs", "Develop threaded or tethered closures for bottles exposed to oils and workshop handling."), ("High-torque service caps", "Review grip, tamper evidence and seal compression for repeated opening in the field.")],
            "parameters": [("Fluid and exposure", "Name the fluid, temperature range, storage time and cleaning chemicals that contact the part."), ("Torque and seal", "Provide thread, plug, gasket and opening-torque targets, if already specified."), ("Handling and line", "Share cap weight, machine, output, automation and inspection method.")],
            "checklist": ["Cap/bottle drawing or sample", "Fluid, temperature and exposure brief", "Torque, seal and tamper requirements", "Machine, output and inspection plan"],
            "process": [("Chemical-service review", "LEYA reviews the closure geometry, material assumptions, draft and steel selection around the declared fluid exposure.", ["Contact areas marked", "Seal and thread risks listed", "Maintenance assumptions recorded"]), ("Torque and fit trial", "Trial parts are checked on the intended bottle with the agreed torque, fit and visual limits.", ["Bottle interface confirmed", "Torque method agreed", "Approval linked to the project record"])],
            "faqs": [("Can one cap fit several lubricant bottles?", "Only if the neck finish, seal and torque windows are compatible; provide each bottle reference for review."), ("Do you promise a fixed mould life?", "No. Service life depends on steel, resin, maintenance, process and the approved usage profile."), ("How is chemical resistance assessed?", "The buyer should provide the fluid and exposure conditions; part material and mould steel are then reviewed accordingly."), ("What does a useful first enquiry contain?", "Send drawings or samples, fluid conditions, resin, torque, machine and output requirements.")],
            "sources": ["uddeholm", "cap"], "note": "Chemical compatibility, torque and durability are confirmed only against the declared fluid, drawings and trial evidence.",
        },
        "es": {
            "title": "Moldes para tapas de aceite de motor", "description": "Moldes industriales para envases de aceite y fluidos, revisando exposición química, par y sellado en conjunto.",
            "scenarios": [("Envases de lubricante y ATF", "Desarrollar cierres roscados o unidos para botellas expuestas a aceites y manipulación de taller."), ("Tapas de alto par", "Revisar agarre, inviolabilidad y compresión del sellado para aperturas repetidas.")],
            "parameters": [("Fluido y exposición", "Indicar fluido, temperatura, almacenamiento y químicos de limpieza en contacto con la pieza."), ("Par y sellado", "Facilitar rosca, tapón, junta y objetivo de par si ya existe."), ("Manipulación y línea", "Compartir peso, máquina, producción, automatización e inspección.")],
            "checklist": ["Plano o muestra de tapa y botella", "Ficha de fluido, temperatura y exposición", "Requisitos de par, sellado e inviolabilidad", "Máquina, producción y plan de inspección"],
            "process": [("Revisión de servicio químico", "LEYA revisa geometría, material, desmoldeo y acero considerando el fluido declarado.", ["Zonas de contacto marcadas", "Riesgos de rosca y sellado listados", "Mantenimiento registrado"]), ("Prueba de par y ajuste", "Las piezas se prueban en la botella prevista con los límites acordados de par, ajuste y aspecto.", ["Interfaz confirmada", "Método de par acordado", "Aprobación ligada al registro"])],
            "faqs": [("¿Una tapa puede servir para varias botellas?", "Solo si acabados, sellado y ventanas de par son compatibles; envíe cada referencia."), ("¿Prometen una vida fija del molde?", "No. Depende de acero, resina, mantenimiento, proceso y uso aprobado."), ("¿Cómo se revisa la resistencia química?", "El comprador aporta fluido y exposición; después se revisan material y acero."), ("¿Qué debe incluir la primera consulta?", "Planos o muestras, condiciones del fluido, resina, par, máquina y producción.")],
            "sources": ["uddeholm", "cap"], "note": "La compatibilidad química, el par y la durabilidad se confirman con fluido, planos y evidencias de prueba.",
        },
    },
    "food-packaging-cap-mould": {
        "en": {
            "title": "Food Packaging Cap Moulds", "description": "Closure moulds for sauces, dairy, condiments and ready-meal packaging, with hygiene, sealing and consumer opening requirements defined up front.",
            "scenarios": [("Sauce and condiment bottles", "Coordinate tamper evidence, dispensing control and clean appearance for filled food packs."), ("Dairy and ready-meal containers", "Review snap fit, lid flatness and filling-line handling around the container rim.")],
            "parameters": [("Food-contact materials", "State resin, additives, colour and the documentation route used by the part supplier."), ("Seal and opening", "Provide the rim/neck drawing, liner or plug details and opening method."), ("Hygiene and line", "Share filling temperature, cleaning practice, output and visual inspection limits.")],
            "checklist": ["Container and closure drawings", "Resin, additives and food-contact documents", "Seal/opening and tamper requirements", "Filling, cleaning and inspection conditions"],
            "process": [("Hygiene-oriented DFM", "LEYA reviews parting, polish, venting, ejection and material assumptions around the food-contact surfaces.", ["Contact surfaces identified", "Cleanability risks discussed", "Critical appearance areas marked"]), ("Fit and sealing trial", "The agreed container and filling conditions are used to check fit, opening and leakage evidence.", ["Actual container used where possible", "Inspection method recorded", "Final result follows approved evidence"])],
            "faqs": [("Do you certify the finished package?", "No. LEYA can review mould and trial requirements; food-contact and package approval remain with the buyer and material suppliers."), ("Can you match a sauce-cap sample?", "Yes, provide the sample, bottle drawing, resin and opening/seal target for review."), ("How should hygiene be specified?", "Describe contact surfaces, cleaning practice, material documents and the visual/parting limits expected."), ("What is needed before pricing?", "Send the container and cap geometry, resin, line data, target output and trial acceptance method.")],
            "sources": ["cap", "uddeholm"], "note": "Food-contact suitability and package performance require the buyer's material documents, process conditions and acceptance record.",
        },
        "es": {
            "title": "Moldes de tapas para envases alimentarios", "description": "Moldes para salsas, lácteos, condimentos y platos preparados, definiendo higiene, sellado y apertura del consumidor desde el inicio.",
            "scenarios": [("Botellas de salsas y condimentos", "Coordinar inviolabilidad, dosificación y aspecto limpio en envases llenos."), ("Envases lácteos y preparados", "Revisar encaje, planitud de tapa y manipulación alrededor del borde.")],
            "parameters": [("Materiales de contacto", "Indicar resina, aditivos, color y documentación del proveedor de piezas."), ("Sellado y apertura", "Facilitar plano del cuello/borde, liner o tapón y método de apertura."), ("Higiene y línea", "Compartir temperatura de llenado, limpieza, producción y límites visuales.")],
            "checklist": ["Planos de envase y tapa", "Resina, aditivos y documentos de contacto", "Sellado, apertura e inviolabilidad", "Condiciones de llenado, limpieza e inspección"],
            "process": [("DFM orientado a higiene", "LEYA revisa partición, pulido, ventilación, expulsión y material en superficies de contacto.", ["Superficies de contacto identificadas", "Riesgos de limpieza comentados", "Zonas visuales marcadas"]), ("Prueba de ajuste y sellado", "Se usan envase y condiciones acordadas para comprobar ajuste, apertura y evidencias de fuga.", ["Envase real cuando sea posible", "Método registrado", "Resultado según evidencia aprobada"])],
            "faqs": [("¿Certifican el envase terminado?", "No. LEYA revisa molde y pruebas; la aprobación de contacto alimentario corresponde al comprador y proveedores."), ("¿Pueden igualar una tapa de salsa?", "Sí, envíe muestra, plano, resina y objetivo de apertura/sellado."), ("¿Cómo se define la higiene?", "Describa superficies, limpieza, documentos de material y límites de partición/aspecto."), ("¿Qué hace falta antes del precio?", "Geometría, resina, datos de línea, producción y método de aceptación de prueba.")],
            "sources": ["cap", "uddeholm"], "note": "La aptitud para contacto alimentario y el envase se confirman con documentos, proceso y registro de aceptación.",
        },
    },
    "medical-cap-mould": {
        "en": {
            "title": "Medical and Diagnostic Cap Moulds", "description": "Precision tooling for diagnostic, pharmaceutical and medical packaging parts where traceability, cleanable surfaces and controlled approval records are essential.",
            "scenarios": [("Diagnostic containers", "Review small closures, plugs or caps around the container, filling and inspection process."), ("Pharmaceutical packaging", "Define surface, material and documentation expectations before committing to a mould design.")],
            "parameters": [("Part and material", "Provide the drawing, resin grade, additives, colour and any controlled-environment requirements."), ("Critical features", "Mark sealing, snap, thread, burr, flash and cosmetic limits on the drawing."), ("Traceability", "State revision control, inspection records, sampling and approval sign-off needed by the buyer.")],
            "checklist": ["Controlled part drawing and revision", "Material and environment requirements", "Critical defect and inspection limits", "Approval, sampling and traceability plan"],
            "process": [("Risk-led part review", "LEYA maps critical sealing, burr, flash and ejection features to the drawing and inspection plan.", ["Revision frozen for review", "Critical-to-function features listed", "Material assumptions separated from evidence"]), ("Documented trial handover", "Trial samples and dimensional records are packaged with the approved revision so the buyer can complete its own release.", ["Sampling plan agreed", "Inspection record attached", "Buyer approval remains the release decision"])],
            "faqs": [("Can LEYA claim a medical certification for the mould?", "No. Any regulatory or cleanroom claim must be confirmed by the buyer's quality system and project documents."), ("What controls flash and burrs?", "Parting, venting, steel condition, ejection and the agreed inspection limit are reviewed together."), ("Can you work from a diagnostic sample?", "Yes, but a controlled drawing or scan and the intended material are needed before design release."), ("What records should be requested?", "Agree revision, material traceability, dimensional report, samples and approval signatures before the trial.")],
            "sources": ["uddeholm", "cap"], "note": "Regulatory suitability is never inferred from a mould page; final release follows the buyer's controlled documents and trial record.",
        },
        "es": {
            "title": "Moldes para tapas médicas y de diagnóstico", "description": "Moldes de precisión para envases de diagnóstico, farmacéuticos y médicos, con trazabilidad, superficies limpiables y registros controlados.",
            "scenarios": [("Envases de diagnóstico", "Revisar tapas, tapones o cierres pequeños junto con llenado e inspección."), ("Envases farmacéuticos", "Definir superficie, material y documentación antes de aprobar el diseño.")],
            "parameters": [("Pieza y material", "Enviar plano, resina, aditivos, color y requisitos de entorno controlado."), ("Características críticas", "Marcar sellado, encaje, rosca, rebaba, flash y límites cosméticos."), ("Trazabilidad", "Indicar revisiones, informes, muestreo y firmas de aprobación.")],
            "checklist": ["Plano controlado y revisión", "Requisitos de material y entorno", "Límites de defectos e inspección", "Plan de aprobación, muestras y trazabilidad"],
            "process": [("Revisión de riesgos", "LEYA relaciona sellado, rebabas, flash y expulsión con el plano y el plan de inspección.", ["Revisión congelada", "Funciones críticas listadas", "Supuestos separados de evidencias"]), ("Entrega documentada de prueba", "Las muestras y registros dimensionales acompañan la revisión aprobada para que el comprador complete su liberación.", ["Plan de muestreo acordado", "Informe adjunto", "La liberación corresponde al comprador"])],
            "faqs": [("¿LEYA puede afirmar una certificación médica?", "No. Las afirmaciones regulatorias o de sala limpia dependen del sistema de calidad y documentos del comprador."), ("¿Cómo se controlan rebabas y flash?", "Se revisan partición, ventilación, acero, expulsión y límite de inspección."), ("¿Pueden trabajar desde una muestra?", "Sí, pero se necesita plano o escaneo controlado y material previsto."), ("¿Qué registros solicitar?", "Revisiones, trazabilidad, informe dimensional, muestras y firmas antes de la prueba.")],
            "sources": ["uddeholm", "cap"], "note": "La aptitud regulatoria no se deduce de una página; la liberación depende de documentos controlados y pruebas.",
        },
    },
    "personal-care-cap-mould": {
        "en": {
            "title": "Personal Care Cap Moulds", "description": "Cap tooling for shampoo, body wash, lotion and cosmetic bottles, balancing dispensing, appearance, grip and line handling.",
            "scenarios": [("Shampoo and body wash", "Develop flip-top, disc-top or pump interfaces for filled personal-care bottles."), ("Premium cosmetic packs", "Coordinate texture, colour split, decoration area and clean parting lines with the brand sample.")],
            "parameters": [("Dispensing function", "Provide the opening, plug, pump interface, closure force and bottle finish."), ("Appearance and decoration", "Mark texture, gloss, colour, logo area, gate witness and acceptable weld lines."), ("Resin and process", "State resin, colour masterbatch, machine, output and automation details.")],
            "checklist": ["Cap, bottle and dispenser drawings", "Resin, colour and appearance sample", "Opening/closing and dispensing target", "Machine, output and decoration limits"],
            "process": [("Appearance and function DFM", "LEYA separates cosmetic surfaces from sealing and ejection features so the sample can be judged fairly.", ["Appearance zones marked", "Dispensing path reviewed", "Gate and parting risks recorded"]), ("Brand sample comparison", "The trial review checks colour, texture, fit, opening feel and approved visual limits.", ["Reference sample retained", "Bottle fit checked", "Changes logged by revision"])],
            "faqs": [("Can you make a cap for an existing bottle?", "Yes, send the bottle finish, cap sample and dispensing requirements so fit and function can be reviewed."), ("How are cosmetic surfaces protected?", "Gate, parting, venting, polish, texture and ejection are planned around the marked appearance zones."), ("Can a pump interface be integrated?", "Feasibility depends on the pump drawing, neck finish, sealing and assembly method."), ("What helps an accurate quotation?", "A drawing, sample, resin, colour/texture reference, machine data and target output.")],
            "sources": ["cap", "uddeholm"], "note": "Appearance and dispensing are approved against the buyer's sample, drawings and trial record, not a generic catalogue promise.",
        },
        "es": {
            "title": "Moldes para tapas de cuidado personal", "description": "Moldes para champú, gel, loción y cosmética, equilibrando dispensación, aspecto, agarre y manipulación en línea.",
            "scenarios": [("Champú y gel corporal", "Desarrollar interfaces abatibles, disc-top o de bomba para botellas de cuidado personal."), ("Cosmética premium", "Coordinar textura, color, decoración y líneas limpias con la muestra de marca.")],
            "parameters": [("Función de dispensación", "Facilitar abertura, tapón, interfaz de bomba, fuerza y acabado del cuello."), ("Aspecto y decoración", "Marcar textura, brillo, color, logo, marca de entrada y soldaduras aceptables."), ("Resina y proceso", "Indicar resina, masterbatch, máquina, producción y automatización.")],
            "checklist": ["Planos de tapa, botella y dispensador", "Resina, color y muestra visual", "Objetivo de apertura/cierre y dispensación", "Máquina, producción y límites decorativos"],
            "process": [("DFM de aspecto y función", "LEYA separa superficies cosméticas de sellado y expulsión para valorar la muestra correctamente.", ["Zonas visuales marcadas", "Ruta de dispensación revisada", "Riesgos de entrada y partición registrados"]), ("Comparación con muestra", "La prueba comprueba color, textura, ajuste, sensación de apertura y límites visuales.", ["Muestra conservada", "Ajuste en botella comprobado", "Cambios registrados por revisión"])],
            "faqs": [("¿Pueden hacer una tapa para una botella existente?", "Sí, envíe acabado del cuello, muestra y requisitos de dispensación."), ("¿Cómo se protegen las superficies cosméticas?", "Entrada, partición, ventilación, pulido, textura y expulsión se planifican con las zonas marcadas."), ("¿Se puede integrar una bomba?", "Depende de plano de bomba, cuello, sellado y método de montaje."), ("¿Qué permite cotizar mejor?", "Plano, muestra, resina, referencia de color/textura, máquina y producción.")],
            "sources": ["cap", "uddeholm"], "note": "El aspecto y la dispensación se aprueban con muestra, planos y prueba del comprador, no con una promesa genérica.",
        },
    },
    "functional-cap-mould": {
        "en": {
            "title": "Functional and Combination Cap Moulds", "description": "Tooling for sport, push-pull, tethered and multi-feature closures where several functions must work in one compact part.",
            "scenarios": [("Sports and on-the-go closures", "Coordinate drinking aperture, tether, grip and leak-control features for active-use packs."), ("Combination mechanisms", "Review several moving or sealing features together before choosing the mould split and ejection sequence.")],
            "parameters": [("Functional sequence", "Describe how the user opens, drinks, closes, pulls or locks the part."), ("Interface geometry", "Provide neck finish, seal, hinge/tether, insert and assembly drawings."), ("Use conditions", "State resin, temperature, force, drop/handling expectations and output target.")],
            "checklist": ["Functional sequence and approved sample", "Neck, seal, tether and assembly drawings", "Resin, forces and use conditions", "Machine, automation and trial acceptance"],
            "process": [("Mechanism mapping", "LEYA maps each moving, sealing and ejection feature to a mould action before layout is fixed.", ["User sequence documented", "Interference risks listed", "Assembly interfaces marked"]), ("Function-first trial", "Trial parts are checked in the actual opening/closing sequence with the agreed fit and leak criteria.", ["Sequence demonstrated", "Critical forces recorded", "Changes linked to revision"])],
            "faqs": [("Can one mould combine several functions?", "Often, but feasibility depends on the parting, sliders/inserts, machine and assembly sequence."), ("How do you review a sport-cap leak path?", "Provide the neck, seal, drinking opening and use conditions; the trial criteria are agreed before testing."), ("Can a tether be added later?", "Only if the drawing, material and mould architecture leave a controlled route; review it before steel release."), ("What should be sent first?", "A sample or 3D/drawing plus the user sequence, resin, machine and output target.")],
            "sources": ["cap", "hmould"], "note": "Combination functions are confirmed by geometry, assembly sequence and trial evidence for the specified use.",
        },
        "es": {
            "title": "Moldes para tapas funcionales y combinadas", "description": "Moldes para tapas deportivas, push-pull, unidas y multifunción, donde varias funciones deben convivir en una pieza compacta.",
            "scenarios": [("Tapas deportivas y de uso móvil", "Coordinar abertura, unión, agarre y control de fugas para envases activos."), ("Mecanismos combinados", "Revisar funciones móviles y de sellado antes de fijar partición y expulsión.")],
            "parameters": [("Secuencia funcional", "Describir cómo el usuario abre, bebe, cierra, tira o bloquea la pieza."), ("Geometría de interfaz", "Facilitar cuello, sellado, bisagra/unión, insertos y montaje."), ("Condiciones de uso", "Indicar resina, temperatura, fuerzas, manipulación y producción.")],
            "checklist": ["Secuencia y muestra aprobada", "Planos de cuello, sellado, unión y montaje", "Resina, fuerzas y uso", "Máquina, automatización y aceptación"],
            "process": [("Mapa del mecanismo", "LEYA relaciona funciones móviles, sellado y expulsión con acciones del molde antes de fijar el diseño.", ["Secuencia documentada", "Interferencias listadas", "Interfaces de montaje marcadas"]), ("Prueba orientada a función", "Las piezas se prueban en la secuencia real de apertura y cierre con criterios de ajuste y fuga acordados.", ["Secuencia demostrada", "Fuerzas críticas registradas", "Cambios ligados a revisión"])],
            "faqs": [("¿Un molde puede combinar varias funciones?", "A menudo sí; depende de partición, correderas/insertos, máquina y montaje."), ("¿Cómo se revisa una tapa deportiva?", "Facilite cuello, sellado, abertura y condiciones de uso para acordar la prueba."), ("¿Se puede añadir una unión después?", "Solo si geometría, material y arquitectura dejan una ruta controlada; se revisa antes del acero."), ("¿Qué enviar primero?", "Muestra o plano 3D con secuencia de uso, resina, máquina y producción.")],
            "sources": ["cap", "hmould"], "note": "Las funciones combinadas se confirman mediante geometría, montaje y evidencias de prueba del uso definido.",
        },
    },
    "plastic-handle-cap-mould": {
        "en": {
            "title": "Plastic Handle Moulds", "description": "Handle and grip tooling for bottles, jerry cans and containers where ergonomics, attachment strength and mould release must stay aligned.",
            "scenarios": [("Jerry-can and container handles", "Develop an integrated or separate handle for carrying, stacking and filling operations."), ("Bottle carrying grips", "Review finger clearance, attachment points and cosmetic surfaces for repeated handling.")],
            "parameters": [("Load and ergonomics", "Provide user load, grip dimensions, finger clearance and any drop or handling requirement."), ("Attachment design", "Share the container interface, weld/snap details and assembly method."), ("Part and machine", "State resin, wall thickness, texture, machine and output target.")],
            "checklist": ["Handle and container drawings or sample", "Load, grip and attachment requirements", "Resin, texture and wall targets", "Machine, assembly and trial plan"],
            "process": [("Load-path DFM", "LEYA reviews the load path, ribs, attachment and ejection direction against the drawing and intended use.", ["Load points marked", "Shrinkage and warpage risks listed", "Assembly interface checked"]), ("Fit and handling trial", "Samples are assembled with the container and checked for fit, grip and agreed visual limits.", ["Container used where possible", "Handling checks recorded", "Approved revision retained"])],
            "faqs": [("Can the handle be moulded with the container?", "Feasibility depends on the container process, parting, machine and assembly requirement; send the full interface."), ("How is handle strength checked?", "Agree load direction, fixture, duration and acceptance before the trial."), ("Can a textured grip be added?", "Yes, if texture, draft, ejection and appearance zones are defined on the drawing or sample."), ("What information is needed for a quote?", "Send handle/container geometry, resin, load, machine, output and assembly method.")],
            "sources": ["hmould", "uddeholm"], "note": "Strength and ergonomics are confirmed by the buyer's load case, assembly method and trial record.",
        },
        "es": {
            "title": "Moldes para asas de plástico", "description": "Moldes de asas y agarres para botellas, garrafas y envases, alineando ergonomía, resistencia de unión y desmoldeo.",
            "scenarios": [("Asas para garrafas y envases", "Desarrollar un asa integrada o separada para transporte, apilado y llenado."), ("Agarres de botellas", "Revisar espacio para dedos, uniones y superficies cosméticas para uso repetido.")],
            "parameters": [("Carga y ergonomía", "Facilitar carga, dimensiones de agarre, espacio para dedos y golpes o manipulación."), ("Unión", "Compartir interfaz con el envase, soldadura/encaje y montaje."), ("Pieza y máquina", "Indicar resina, pared, textura, máquina y producción.")],
            "checklist": ["Planos o muestras de asa y envase", "Carga, agarre y unión", "Resina, textura y pared", "Máquina, montaje y prueba"],
            "process": [("DFM del camino de carga", "LEYA revisa carga, nervios, unión y dirección de expulsión respecto al uso previsto.", ["Puntos de carga marcados", "Riesgos de contracción listados", "Interfaz comprobada"]), ("Prueba de ajuste y manipulación", "Las muestras se montan en el envase y se comprueban ajuste, agarre y límites visuales.", ["Envase real cuando sea posible", "Controles registrados", "Revisión aprobada conservada"])],
            "faqs": [("¿El asa puede moldearse con el envase?", "Depende de proceso, partición, máquina y montaje; envíe la interfaz completa."), ("¿Cómo se comprueba la resistencia?", "Se acuerdan dirección, útil, duración y aceptación antes de probar."), ("¿Se puede añadir textura?", "Sí, si textura, desmoldeo y zonas visuales aparecen en plano o muestra."), ("¿Qué hace falta para cotizar?", "Geometría, resina, carga, máquina, producción y montaje.")],
            "sources": ["hmould", "uddeholm"], "note": "La resistencia y la ergonomía se confirman con la carga, el montaje y el registro de prueba del comprador.",
        },
    },
    "five-gallon-water-cap-mould": {
        "en": {
            "title": "5 Gallon Water Cap Moulds", "description": "Closure tooling for reusable large-format water bottles and dispenser packs, with seal, handling and sanitation requirements reviewed together.",
            "scenarios": [("Returnable 18.9 L bottles", "Match the cap and neck to repeated filling, washing, transport and dispenser use."), ("Cooler and dispenser closures", "Review pull tabs, plugs, seals and operator handling around a large closure.")],
            "parameters": [("Bottle neck and seal", "Provide the large-format neck drawing, sealing surfaces, plug or gasket details."), ("Reuse and cleaning", "State washing temperature, chemical exposure, return cycles and handling conditions."), ("Line and closure", "Share cap weight, resin, filling equipment, output and leak-test method.")],
            "checklist": ["Large-bottle neck and cap drawings", "Reuse, washing and chemical conditions", "Resin, seal and opening requirements", "Filling, leak test and sample plan"],
            "process": [("Reuse-service review", "LEYA maps neck, seal, grip and cleaning exposure to the mould and material assumptions.", ["Seal surfaces marked", "Cleaning exposure listed", "Handling risks recorded"]), ("Fit and leak trial", "The cap is checked on the intended bottle with the agreed filling, cleaning and leak criteria.", ["Bottle interface confirmed", "Test method recorded", "Acceptance tied to revision"])],
            "faqs": [("What makes a 5-gallon cap different?", "The larger neck, handling load, reuse and cleaning conditions must be reviewed with the cap and bottle drawings."), ("Can you use an existing dispenser finish?", "Yes, send the finish drawing or cap/bottle sample so fit and seal can be checked."), ("How should reuse be described?", "State wash temperature, chemical, return cycle and handling conditions; these affect material and trial planning."), ("What should be included before pricing?", "Provide drawings, resin, seal/opening target, machine or filling data and leak-test method.")],
            "sources": ["hmould", "uddeholm"], "note": "Reusable-bottle performance is confirmed against the buyer's cleaning, handling and leak-test conditions.",
        },
        "es": {
            "title": "Moldes para tapas de garrafón de 5 galones", "description": "Moldes para botellas grandes reutilizables y dispensadores, revisando sellado, manipulación y sanitización en conjunto.",
            "scenarios": [("Botellas retornables de 18,9 L", "Ajustar tapa y cuello a llenado, lavado, transporte y uso en dispensador."), ("Cierres de enfriadores", "Revisar pestañas, tapones, juntas y manipulación alrededor de una tapa grande.")],
            "parameters": [("Cuello y sellado", "Facilitar plano del cuello grande, superficies, tapón o junta."), ("Reutilización y limpieza", "Indicar temperatura de lavado, químicos, retornos y manipulación."), ("Línea y cierre", "Compartir peso, resina, equipo de llenado, producción y prueba de fugas.")],
            "checklist": ["Planos de cuello y tapa grande", "Condiciones de lavado y químicos", "Resina, sellado y apertura", "Llenado, fugas y plan de muestras"],
            "process": [("Revisión de servicio reutilizable", "LEYA relaciona cuello, sellado, agarre y limpieza con material y diseño del molde.", ["Superficies de sellado marcadas", "Limpieza listada", "Riesgos de manipulación registrados"]), ("Prueba de ajuste y fuga", "La tapa se comprueba en la botella prevista con criterios de llenado, limpieza y fugas acordados.", ["Interfaz confirmada", "Método registrado", "Aceptación ligada a revisión"])],
            "faqs": [("¿Qué diferencia una tapa de 5 galones?", "El cuello grande, carga de manipulación, reutilización y limpieza deben revisarse con planos."), ("¿Pueden usar un acabado de dispensador existente?", "Sí, envíe plano o muestra de tapa y botella para revisar ajuste y sellado."), ("¿Cómo describir la reutilización?", "Indique temperatura, químicos, retornos y manipulación; afectan material y prueba."), ("¿Qué incluir antes del precio?", "Planos, resina, objetivo de sellado/apertura, datos de llenado y prueba de fugas.")],
            "sources": ["hmould", "uddeholm"], "note": "El uso de botella reutilizable se confirma con limpieza, manipulación y condiciones de fuga del comprador.",
        },
    },
    "wine-cap-mould": {
        "en": {
            "title": "Wine and Specialty Beverage Cap Moulds", "description": "Closure tooling for wine, spirits and specialty beverages where pour control, tamper evidence and decorative surfaces must fit the bottle finish.",
            "scenarios": [("Wine and spirits closures", "Coordinate pourer, plug or threaded closure with a glass or PET bottle neck."), ("Decorative beverage caps", "Protect visible surfaces while preserving fit, opening and tamper features.")],
            "parameters": [("Bottle finish", "Provide the neck drawing, material and tolerance information for the bottle."), ("Pour and seal", "Describe pour rate, plug/gasket, opening torque and tamper requirement."), ("Decoration", "Mark colour, texture, gloss, logo area and acceptable marks on the sample.")],
            "checklist": ["Bottle finish and cap drawings", "Pour, seal and tamper targets", "Resin, colour and decoration sample", "Machine, output and trial acceptance"],
            "process": [("Finish and pour review", "LEYA checks neck fit, pour path, seal surfaces, parting and ejection before tool layout.", ["Bottle interface frozen", "Pour features marked", "Visual surfaces separated"]), ("Bottle-and-cap trial", "Samples are fitted to the intended bottle and checked for pour, opening and appearance evidence.", ["Actual bottle used where possible", "Opening method agreed", "Final result follows the approved record"])],
            "faqs": [("Can the mould follow a glass-bottle finish?", "Yes, provide the controlled neck drawing and cap sample; the bottle tolerance is part of the review."), ("How are decorative surfaces protected?", "Texture, parting, gate, venting and ejection are arranged around the visible zones."), ("Can a pourer be built into the cap?", "Feasibility depends on the pourer drawing, seal, assembly and bottle neck."), ("What is needed for a quotation?", "Send bottle/cap drawings, pour and opening targets, resin, appearance sample and line data.")],
            "sources": ["cetie", "cap"], "note": "Pour, seal and decoration are confirmed with the intended bottle, approved sample and mould trial.",
        },
        "es": {
            "title": "Moldes para tapas de vino y bebidas especiales", "description": "Moldes para vino, licores y bebidas especiales, ajustando vertido, inviolabilidad y superficies decorativas al cuello de la botella.",
            "scenarios": [("Cierres de vino y licores", "Coordinar vertedor, tapón o rosca con un cuello de vidrio o PET."), ("Tapas decorativas", "Proteger superficies visibles manteniendo ajuste, apertura e inviolabilidad.")],
            "parameters": [("Acabado de botella", "Facilitar plano de cuello, material y tolerancias de la botella."), ("Vertido y sellado", "Describir caudal, tapón/junta, par de apertura e inviolabilidad."), ("Decoración", "Marcar color, textura, brillo, logo y marcas aceptables.")],
            "checklist": ["Planos de cuello y tapa", "Objetivos de vertido, sellado e inviolabilidad", "Resina, color y muestra decorativa", "Máquina, producción y aceptación"],
            "process": [("Revisión de cuello y vertido", "LEYA revisa ajuste, ruta de vertido, sellado, partición y expulsión antes del diseño.", ["Interfaz congelada", "Funciones de vertido marcadas", "Superficies visibles separadas"]), ("Prueba botella-tapa", "Las muestras se montan en la botella prevista y se comprueban vertido, apertura y aspecto.", ["Botella real cuando sea posible", "Método de apertura acordado", "Resultado según registro aprobado"])],
            "faqs": [("¿El molde puede seguir un cuello de vidrio?", "Sí, envíe plano controlado y muestra; la tolerancia de la botella forma parte de la revisión."), ("¿Cómo se protegen superficies decorativas?", "Textura, partición, entrada, ventilación y expulsión se organizan alrededor de zonas visibles."), ("¿Se puede integrar un vertedor?", "Depende del plano del vertedor, sellado, montaje y cuello."), ("¿Qué hace falta para cotizar?", "Planos, objetivos de vertido/apertura, resina, muestra visual y datos de línea.")],
            "sources": ["cetie", "cap"], "note": "Vertido, sellado y decoración se confirman con botella, muestra aprobada y prueba del molde.",
        },
    },
    "pet-preform-mould": {
        "en": {
            "title": "PET Preform Moulds", "description": "Preform tooling for beverage, edible-oil and specialty PET packaging, linking neck finish, gram weight, stretch ratio and blow process.",
            "scenarios": [("Beverage preforms", "Develop a preform that matches the neck finish, bottle volume and stretch-blow process."), ("Oil and specialty packs", "Review resin, colour, weight distribution and barrier or shape requirements before tool layout.")],
            "parameters": [("Neck and gram weight", "Provide finish drawing, preform weight, length, wall map and target bottle."), ("Resin and process", "State PET grade, IV, colour, drying and intended blow-machine information."), ("Cavity and output", "Share output target, machine interface, hot-runner preference and sampling plan.")],
            "checklist": ["Preform and bottle drawings", "PET grade, IV, colour and weight", "Blow machine and output target", "Trial bottle, dimensions and acceptance plan"],
            "process": [("Preform-to-bottle review", "LEYA maps neck, gram weight, stretch ratio and bottle wall targets before defining the cavity layout.", ["Finish drawing controlled", "Weight and wall targets listed", "Blow process assumptions separated"]), ("Preform and bottle trial", "The trial connects preform dimensions to blown-bottle fit, wall distribution and agreed inspection points.", ["Machine data confirmed", "Bottle checks agreed", "Result follows approved drawings"])],
            "faqs": [("What makes a preform quote accurate?", "The finish drawing, weight, length, PET grade, bottle drawing and blow-machine data are the starting set."), ("Can you design for a new bottle shape?", "Yes, provide the bottle, preform and stretch-blow targets for a feasibility review."), ("How is cavity balance checked?", "Cavity dimensions, weight and trial samples are compared against the agreed inspection plan."), ("Can a bottle wall map be confirmed before trial?", "The target can be reviewed, but wall distribution depends on resin, preform, machine and process and is confirmed with trial evidence.")],
            "sources": ["husky", "cetie"], "note": "Preform and bottle performance are confirmed by the buyer's resin, machine, drawings and trial data.",
        },
        "es": {
            "title": "Moldes para preformas PET", "description": "Moldes de preformas para envases PET de bebidas, aceites y formatos especiales, conectando cuello, peso, estirado y soplado.",
            "scenarios": [("Preformas para bebidas", "Desarrollar una preforma compatible con acabado, volumen y proceso de estirado-soplado."), ("Envases de aceite y especiales", "Revisar resina, color, distribución de peso y forma antes del diseño.")],
            "parameters": [("Cuello y peso", "Facilitar acabado, peso, longitud, mapa de pared y botella objetivo."), ("Resina y proceso", "Indicar PET, IV, color, secado y máquina de soplado."), ("Cavidades y producción", "Compartir producción, interfaz, canal caliente y plan de muestras.")],
            "checklist": ["Planos de preforma y botella", "PET, IV, color y peso", "Máquina de soplado y producción", "Botella de prueba, cotas y aceptación"],
            "process": [("Revisión preforma-botella", "LEYA relaciona cuello, peso, estirado y pared antes de definir las cavidades.", ["Acabado controlado", "Peso y pared listados", "Supuestos de soplado separados"]), ("Prueba de preforma y botella", "La prueba relaciona cotas de preforma con ajuste, pared y controles de botella.", ["Datos de máquina confirmados", "Controles acordados", "Resultado según planos aprobados"])],
            "faqs": [("¿Qué hace precisa una cotización de preforma?", "Acabado, peso, longitud, PET, botella y máquina de soplado son la base."), ("¿Pueden diseñar una botella nueva?", "Sí, envíe botella, preforma y objetivos de estirado-soplado."), ("¿Cómo se revisa el equilibrio de cavidades?", "Se comparan cotas, pesos y muestras con el plan de inspección."), ("¿Garantizan el mapa de pared?", "No. Depende de resina, preforma, máquina y proceso; se confirma con prueba.")],
            "sources": ["husky", "cetie"], "note": "La preforma y la botella se confirman con resina, máquina, planos y datos de prueba del comprador.",
        },
    },
    "blow-bottle-mould": {
        "en": {
            "title": "Blow Bottle Moulds", "description": "Bottle blow moulds for PET and specialty containers, linking bottle geometry, wall distribution, cooling and machine envelope before manufacture.",
            "scenarios": [("Standard PET bottles", "Develop a bottle around the approved preform, neck and filling/label requirements."), ("Wide-mouth and custom shapes", "Review handles, panels, grip, cooling and demoulding for a non-standard container.")],
            "parameters": [("Bottle and preform", "Provide 3D/2D bottle, preform, neck finish, volume, weight and stretch targets."), ("Machine envelope", "Share blow-machine make, mould height, opening, tie-bar and cooling interface."), ("Quality limits", "State wall map, appearance, leak, panel and dimensional acceptance criteria.")],
            "checklist": ["Bottle and preform drawings", "Machine and cooling interface", "Weight/wall/appearance targets", "Trial bottle and inspection method"],
            "process": [("Geometry and stretch review", "LEYA maps preform stretch, panels, ribs, neck and parting to the bottle drawing.", ["Critical surfaces marked", "Stretch assumptions listed", "Machine envelope checked"]), ("Blow trial and inspection", "Trial bottles are checked for dimensions, fit, appearance, leakage and agreed wall evidence.", ["Cooling and machine data recorded", "Bottle checks agreed", "Final result follows approved revision"])],
            "faqs": [("Can you develop a custom bottle shape?", "Yes, provide bottle/preform drawings and machine data for a feasibility and DFM review."), ("How is wall distribution discussed?", "The buyer's preform, stretch ratio, process and acceptance method must be defined before trial."), ("Can an existing bottle be matched?", "A sample, scan or controlled drawing can be reviewed for neck, parting and critical panels."), ("What is needed before a quote?", "Send bottle/preform geometry, machine envelope, resin/weight target and inspection criteria.")],
            "sources": ["husky", "hmould"], "note": "Bottle geometry, wall distribution and cooling are confirmed by the buyer's preform, machine and trial evidence.",
        },
        "es": {
            "title": "Moldes de soplado para botellas", "description": "Moldes de soplado para envases PET y especiales, conectando geometría, pared, refrigeración y envolvente de máquina.",
            "scenarios": [("Botellas PET estándar", "Desarrollar una botella con preforma, cuello, llenado y etiquetado aprobados."), ("Formatos de boca ancha o especiales", "Revisar asas, paneles, agarre, refrigeración y desmoldeo del envase.")],
            "parameters": [("Botella y preforma", "Facilitar planos 2D/3D, preforma, cuello, volumen, peso y estirado."), ("Envolvente de máquina", "Compartir fabricante, altura, apertura, columnas e interfaz de refrigeración."), ("Límites de calidad", "Indicar pared, aspecto, fugas, paneles y cotas de aceptación.")],
            "checklist": ["Planos de botella y preforma", "Máquina e interfaz de refrigeración", "Peso/pared/aspecto objetivo", "Botella de prueba y método"],
            "process": [("Revisión de geometría y estirado", "LEYA relaciona estirado, paneles, nervios, cuello y partición con el plano.", ["Superficies críticas marcadas", "Supuestos de estirado listados", "Envolvente comprobada"]), ("Prueba de soplado e inspección", "Las botellas de prueba se comprueban en cotas, ajuste, aspecto, fugas y pared acordada.", ["Datos de máquina y refrigeración registrados", "Controles acordados", "Resultado según revisión aprobada"])],
            "faqs": [("¿Pueden desarrollar una forma personalizada?", "Sí, envíe planos de botella/preforma y datos de máquina para revisar viabilidad y DFM."), ("¿Cómo se trata la distribución de pared?", "Se definen preforma, estirado, proceso y aceptación antes de probar."), ("¿Pueden igualar una botella existente?", "Se puede revisar muestra, escaneo o plano para cuello, partición y paneles."), ("¿Qué hace falta antes del precio?", "Geometría, máquina, resina/peso y criterios de inspección.")],
            "sources": ["husky", "hmould"], "note": "La geometría, pared y refrigeración se confirman con preforma, máquina y evidencias de prueba del comprador.",
        },
    },
}


def build():
    out = {}
    for slug, locales in FAMILIES.items():
        row = {"slug": slug}
        for locale, data in locales.items():
            suffix = "Es" if locale == "es" else ""
            row["title" + suffix] = data["title"]
            row["description" + suffix] = data["description"]
            row["body" + suffix] = data["description"]
            row["sections" + suffix] = section(data["process"])
            row["faqs" + suffix] = faq(data["faqs"])
            row["projectBrief" + suffix] = brief(data["scenarios"], data["parameters"], data["checklist"], data["sources"], data["note"], locale)
        out[slug] = row
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(out)} product families to {OUT}")


if __name__ == "__main__":
    build()

