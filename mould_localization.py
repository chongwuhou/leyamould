"""Small, deterministic Spanish language layer for the LEYA MOULD renderer.

The public site has only two publish-ready locales (English and Spanish).  This
module contains reviewed Spanish labels and a conservative glossary for the
legacy HMould model/article records.  It never invents specifications: model
numbers and source facts are retained and only the surrounding language is
localized.
"""
from __future__ import annotations

import copy
import re
from typing import Any


ES_COMMON_COPY = {
    "advantages": [
        ("Revisión del diseño", "Se comprueban la geometría, la línea de partición, la refrigeración y la expulsión según el proceso previsto."),
        ("Ajuste del proyecto", "El documento técnico registra la familia del molde, el material, la interfaz de máquina y la producción objetivo indicados por el comprador."),
        ("Decisiones basadas en muestras", "Las piezas de prueba y los puntos de inspección acordados guían la optimización antes de la entrega para producción."),
        ("Comunicación clara", "Los planos, PDF, fotografías y notas de revisión permanecen adjuntos a la consulta."),
    ],
    "process_eyebrow": "CÓMO TRABAJAMOS",
    "process_title": "Del plano a una entrega de utillaje controlada.",
    "process_steps": [
        ("01", "Compartir el diseño", "Envíe su plano o muestra para una revisión técnica inicial."),
        ("02", "Análisis DFM", "Revisamos el flujo del molde, la partición, la refrigeración y las oportunidades de optimización."),
        ("03", "Fabricación", "Coordinamos el mecanizado de precisión, EDM, ajuste y tratamiento térmico."),
        ("04", "Prueba e inspección", "Completamos las pruebas, las comprobaciones dimensionales y la evidencia de inspección acordada."),
        ("05", "Entrega y soporte", "Mantenemos conectados los archivos aprobados, las notas de entrega y el soporte técnico."),
    ],
    "footer_quick_links": "Enlaces rápidos",
    "footer_sitemap": "Mapa del sitio",
    "form_required": "Son obligatorios el nombre de la empresa, el correo de trabajo y los requisitos del proyecto. Los planos, muestras y documentos técnicos pueden adjuntarse después por correo electrónico o WhatsApp.",
    "form_company": "Nombre de la empresa",
    "form_email": "Correo de trabajo",
    "form_category": "Tipo de molde",
    "form_quantity": "Cantidad estimada",
    "form_country": "País de destino",
    "form_type": "Tipo de consulta",
    "form_quote": "Solicitar una cotización",
    "form_new": "Nuevo diseño de molde",
    "form_review": "Revisión de un molde existente",
    "form_tech": "Consulta técnica",
    "form_material": "Material previsto",
    "form_advise": "Solicitar asesoramiento",
    "form_other": "Otro / por confirmar",
    "form_requirements": "Requisitos del proyecto",
    "form_consent": "Acepto la",
    "form_privacy": "política de privacidad",
    "form_submit": "Enviar consulta del proyecto →",
    "form_aria": "Formulario de consulta de moldes",
    "back": "Volver al inicio →",
    "learn": "Ver más →",
    "view": "Ver categoría →",
    "category_note": "Las especificaciones técnicas, imágenes y referencias PDF se añaden después de revisar el proyecto.",
    "hero_note": "LEYA MOULD · Huangyan, Taizhou, Zhejiang, China",
}

ES_SHARED_CTA = {
    "catalog": {"title": "Inicie su proyecto de moldes", "description": "Envíenos su plano, muestra o requisitos de producción. Responderemos con las siguientes preguntas técnicas y un camino claro.", "note": "Contáctenos para una cotización y una consulta técnica; responderemos en 24 horas.", "eyebrow": "LEYA MOULD · INGENIERÍA · SOPORTE", "quoteLabel": "Solicitar cotización", "phoneLabel": "Teléfono / WhatsApp", "emailLabel": "Correo electrónico", "whatsappLabel": "WhatsApp"},
    "samples": {"title": "¿Quiere ver más muestras o solicitar una cotización?", "description": "Contacte hoy con LEYA MOULD. Le enviaremos las muestras adecuadas y una propuesta práctica para su proyecto.", "note": "Cuéntenos sobre su molde", "eyebrow": "LEYA MOULD · INGENIERÍA · SOPORTE", "quoteLabel": "Solicitar cotización", "phoneLabel": "Teléfono / WhatsApp", "emailLabel": "Correo electrónico", "whatsappLabel": "WhatsApp"},
    "auxiliary": {"title": "¿Necesita equipos auxiliares para su línea de tapas?", "description": "Contacte con LEYA MOULD para hablar del tamaño de la tapa, el volumen de producción y las operaciones auxiliares que necesita. Le recomendaremos una configuración práctica.", "note": "Cuéntenos sobre su línea", "eyebrow": "LEYA MOULD · INGENIERÍA · SOPORTE", "quoteLabel": "Solicitar cotización", "phoneLabel": "Teléfono / WhatsApp", "emailLabel": "Correo electrónico", "whatsappLabel": "WhatsApp"},
    "about": {"title": "Trabajemos juntos", "description": "Comparta su plano, muestra o requisitos de producción y le ayudaremos a definir el siguiente paso técnico.", "note": "Hable con LEYA MOULD", "eyebrow": "LEYA MOULD · INGENIERÍA · SOPORTE", "quoteLabel": "Solicitar cotización", "phoneLabel": "Teléfono / WhatsApp", "emailLabel": "Correo electrónico", "whatsappLabel": "WhatsApp"},
    "faq": {"title": "¿Todavía tiene preguntas?", "description": "Nuestro equipo está listo para ayudarle. Escríbanos y responderemos en un plazo de 24 horas.", "note": "Consulte su proyecto", "eyebrow": "LEYA MOULD · INGENIERÍA · SOPORTE", "quoteLabel": "Solicitar cotización", "phoneLabel": "Teléfono / WhatsApp", "emailLabel": "Correo electrónico", "whatsappLabel": "WhatsApp"},
    "category": {"title": "Inicie su proyecto de moldes", "description": "Envíenos el plano, la muestra, el material, las cavidades y el mercado de destino. Responderemos con las siguientes preguntas técnicas.", "note": "Cuéntenos sobre su molde", "eyebrow": "LEYA MOULD · INGENIERÍA · SOPORTE", "quoteLabel": "Solicitar cotización", "phoneLabel": "Teléfono / WhatsApp", "emailLabel": "Correo electrónico", "whatsappLabel": "WhatsApp"},
}

ES_SEO = {
    "/": ("Fabricante de moldes de plástico en China | LEYA MOULD", "Moldes de inyección y soluciones de utillaje para botellas, tapones, preformas y envases personalizados."),
    "/about/": ("Sobre LEYA MOULD | Fabricante de moldes de precisión", "Conozca el enfoque de ingeniería de LEYA MOULD para proyectos de moldes de botellas, tapones, preformas y productos personalizados."),
    "/products/": ("Categorías de moldes de plástico | LEYA MOULD", "Explore las familias de moldes de tapas, botellas, preformas y soluciones de utillaje para envases."),
    "/Plastic-cap-mold.html": ("Fabricante de moldes para tapas de plástico | LEYA MOULD", "Revise las familias de moldes para tapas de plástico, sus aplicaciones y la información necesaria para el proyecto."),
    "/capabilities/": ("Máquinas auxiliares y capacidades de moldes | LEYA MOULD", "Explore equipos auxiliares, ingeniería de moldes, fabricación y soporte de pruebas para la producción de tapas."),
    "/manufacturing/": ("Proceso de fabricación de moldes de plástico | LEYA MOULD", "Un recorrido claro desde la revisión del plano y DFM hasta el mecanizado, la prueba, la inspección y la entrega técnica."),
    "/quality-control/": ("Control de calidad e inspección de moldes | LEYA MOULD", "Controles de calidad, evidencias de inspección y control de cambios para proyectos de moldes de tapas y envases."),
    "/request-sample/": ("Solicitar una muestra de molde de plástico | LEYA MOULD", "Comparta su plano, muestra y objetivo de producción para una revisión de molde específica para su proyecto."),
    "/contact/": ("Contacto LEYA MOULD | Proyectos de moldes de plástico", "Envíe a LEYA MOULD el plano de la pieza, el material, las cavidades, la máquina y el mercado de destino."),
    "/samples/": ("Muestras de moldes para tapas de plástico | LEYA MOULD", "Explore muestras de tapas de plástico y las soluciones de moldes utilizadas en aplicaciones de envases."),
    "/news/": ("Noticias y novedades sobre moldes de tapas | LEYA MOULD", "Noticias técnicas, notas para compradores y conocimientos de ingeniería sobre proyectos de moldes para tapas de plástico."),
    "/news/Bottle-cap-molds.html": ("Noticias sobre moldes para tapas de botella | LEYA MOULD", "Artículos de ingeniería y orientación para compradores sobre el diseño y la producción de moldes para tapas."),
    "/Bottle-Cap-Machine/Bottle-Cap-Machine.html": ("Máquinas para tapas de botella y equipos auxiliares | LEYA MOULD", "Equipos auxiliares y soporte de producción para el montaje, revestimiento y manipulación de tapas de botella."),
    "/video/": ("Vídeos de pruebas de moldes | LEYA MOULD", "Vea vídeos de pruebas de moldes, utillaje y equipos auxiliares de LEYA MOULD."),
    "/faq/": ("Preguntas frecuentes sobre proyectos de moldes | LEYA MOULD", "Respuestas a preguntas sobre planos, materiales, cavidades, pruebas y entrega de proyectos de moldes."),
    "/blog/": ("Recursos sobre proyectos de moldes | LEYA MOULD", "Recursos técnicos revisados para compradores que planifican proyectos de moldes y utillaje de plástico."),
    "/privacy-policy/": ("Política de privacidad | LEYA MOULD", "Cómo LEYA MOULD gestiona la información enviada en consultas y proyectos."),
}

_MODEL_REPLACEMENTS = (
    ("wide mouth", "boca ancha"), ("hot runner", "canal caliente"), ("cold runner", "canal frío"),
    ("pull top", "pull-top"), ("flip top", "flip-top"), ("valve type", "tipo válvula"),
    ("self lock", "autobloqueo"), ("justable", "ajustable"), ("without tail", "sin cola"),
    ("edible oil", "aceite comestible"), ("personal care", "cuidado personal"),
    ("food packaging", "envase alimentario"), ("medical", "médico"), ("engine oil", "aceite de motor"),
    ("plastic handle", "asa de plástico"), ("wine", "vino"), ("jar", "tarro"),
    ("cavities", "cavidades"), ("cavity", "cavidad"), ("preform", "preforma"),
    ("bottle", "botella"), ("water", "agua"), ("cap", "tapón"), ("mould", "molde"), ("mold", "molde"),
    ("pneumatic", "neumático"), ("closure", "cierre"), ("custom", "personalizado"),
)

_EDITORIAL_REPLACEMENTS = (
    ("beverage packaging engineering and sourcing teams", "equipos de ingeniería y compras de envases para bebidas"),
    ("packaging manufacturers planning regional supply", "fabricantes de envases que planifican el suministro regional"),
    ("closure product owners and tooling procurement managers", "responsables de cierres y compras de utillaje"),
    ("tooling engineers and process owners", "ingenieros de utillaje y responsables de proceso"),
    ("packaging teams developing lightweight closures", "equipos de envases que desarrollan cierres ligeros"),
    ("controlled tooling brief", "documento técnico controlado"), ("multi-market closure specification", "especificación de cierres para varios mercados"),
    ("lightweighting change with seal-risk controls", "cambio de aligeramiento con controles de riesgo de sellado"),
    ("cooling design decision, not an automatic upgrade", "decisión de diseño de refrigeración, no una mejora automática"),
    ("high-sensitivity geometry review", "revisión de geometría sensible"), ("planned replacement and traceable fit", "sustitución planificada y ajuste trazable"),
    ("expanding beverage line", "línea de bebidas en expansión"), ("line-expansion brief", "documento de ampliación de línea"),
    ("drawing revision", "revisión del plano"), ("neck finish", "acabado del cuello"), ("resin family", "familia de resina"),
    ("cavity target", "objetivo de cavidades"), ("press interface", "interfaz de la máquina"), ("trial parts", "piezas de prueba"),
    ("acceptance points", "puntos de aceptación"), ("production evidence", "evidencia de producción"), ("production result", "resultado de producción"),
    ("packaging", "envases"), ("engineering", "ingeniería"), ("sourcing", "compras"), ("tooling", "utillaje"),
    ("buyer", "comprador"), ("machine", "máquina"), ("cooling", "refrigeración"), ("ejection", "expulsión"),
    ("inspection", "inspección"), ("quality", "calidad"), ("confirmed", "confirmado"), ("project", "proyecto"),
    ("process", "proceso"), ("trial", "prueba"), ("production", "producción"), ("cavities", "cavidades"),
    ("cavity", "cavidad"), ("sealing", "sellado"), ("spare parts", "repuestos"), ("change-control", "control de cambios"),
    ("decision point", "punto de decisión"), ("confirm before order", "confirmar antes del pedido"), ("evidence at trial", "evidencia en la prueba"),
    ("part function", "función de la pieza"), ("material", "material"), ("tooling support", "soporte del utillaje"),
    ("Sources and disclosure", "Fuentes y transparencia"), ("LEYA MOULD engineering editorial review", "Revisión editorial de ingeniería de LEYA MOULD"),
    ("a defect investigation with evidence", "una investigación de defectos con evidencia"), ("defect investigation with evidence", "investigación de defectos con evidencia"),
    ("quality engineers and process technicians", "ingenieros de calidad y técnicos de proceso"), ("quality engineers", "ingenieros de calidad"),
    ("process technicians", "técnicos de proceso"), ("defect location", "ubicación del defecto"), ("section thickness", "espesor de sección"),
    ("gate/pack behaviour", "comportamiento de compuerta y compactación"), ("resin lot", "lote de resina"), ("visual limit sample", "muestra límite visual"),
    ("sink-mark troubleshooting for cap moulds", "diagnóstico de marcas de hundimiento en moldes de tapas"), ("controlled DOE or trial record", "registro DOE o de prueba controlado"),
    ("The article does not prescribe a single pressure or time", "El artículo no prescribe una presión o un tiempo únicos"),
    ("The article", "El artículo"), ("before the design", "antes del diseño"), ("before shipment", "antes del envío"),
    ("Buyer checklist", "Lista de comprobación del comprador"), ("Decision matrix", "Matriz de decisión"), ("Related reading", "Lecturas relacionadas"),
    ("Approved buyer drawing and trial data required for project-specific claims", "Se requieren el plano aprobado del comprador y los datos de prueba para las afirmaciones específicas del proyecto"),
    ("project-specific claims", "afirmaciones específicas del proyecto"), ("brief", "documento técnico"), ("Factory", "Fábrica"),
    ("Trial samples", "Muestras de prueba"), ("dimensional checks", "comprobaciones dimensionales"), ("agreed changes", "cambios acordados"), ("final handover", "entrega final"),
    ("Quality Assurance", "Garantía de calidad"), ("sample approval", "aprobación de muestras"), ("Quality evidence", "Evidencia de calidad"), ("production references", "referencias de producción"),
    ("sample-review work", "trabajo de revisión de muestras"), ("For sustainability, process and quality teams", "Para los equipos de sostenibilidad, proceso y calidad"),
    ("sustainability", "sostenibilidad"), ("recycled-resin", "resina reciclada"), ("with boundary conditions", "con condiciones límite"), ("PCR percentage", "porcentaje de PCR"),
    ("supplier data", "datos del proveedor"), ("drying/handling", "secado y manipulación"), ("colour variation", "variación de color"), ("shrinkage", "contracción"), ("seal test", "prueba de sellado"), ("trace samples", "muestras trazables"),
    ("water bottle cap moulds", "moldes para tapas de botellas de agua"), ("water bottle cap mould", "molde para tapas de botellas de agua"),
)

_UI_REPLACEMENTS = (
    ("Precision Moulding", "Moldeado de precisión"), ("Precision moulding", "Moldeado de precisión"),
    ("Precision Engineering", "Ingeniería de precisión"), ("Precision manufacturing", "Fabricación de precisión"),
    ("MOULDING", "MOLDEADO"), ("Mould Product Families", "Familias de productos de moldes"),
    ("Product Families", "familias de productos"), ("Across", "En"),
    ("Professional plastic mould manufacturer", "Fabricante profesional de moldes de plástico"),
    ("high-precision, long-life mould solutions", "soluciones de moldes de alta precisión y larga vida útil"),
    ("YEARS EXPERIENCE", "AÑOS DE EXPERIENCIA"), ("COUNTRIES SERVED", "PAÍSES ATENDIDOS"),
    ("MOULDS DELIVERED", "MOLDES ENTREGADOS"), ("OUR PRODUCTS", "NUESTROS PRODUCTOS"),
    ("Explore our comprehensive range of", "Explore nuestra gama completa de"),
    ("Each mould is engineered for high-volume production, dimensional accuracy and extended service life.", "Cada molde está diseñado para producción de gran volumen, precisión dimensional y una vida útil prolongada."),
    ("ADDITIONAL CAP MODEL REFERENCES", "REFERENCIAS ADICIONALES DE MODELOS DE TAPAS"),
    ("Additional Cap Model References", "Referencias adicionales de modelos de tapas"),
    ("Cap Mould", "Molde de tapas"), ("Mould Types", "Tipos de moldes"), ("Mould Life", "Vida útil del molde"),
    ("Water & Beverage Cap Mould Types", "Tipos de moldes para tapas de agua y bebidas"),
    ("High Quality PCO 1881 Mineral Water Cap Injection Mould", "Molde de inyección de alta calidad para tapas de agua mineral PCO 1881"),
    ("Cavity Available", "cavidades disponibles"), ("Factory Direct", "Directo de fábrica"),
    ("A balanced high-output configuration for production efficiency and predictable mould cost.", "Configuración equilibrada de alta producción para una fabricación eficiente y un coste de molde predecible."),
    ("High-precision water bottle cap moulds with cavity options matched to the buyer's line.", "Moldes de alta precisión para tapas de agua con opciones de cavidades adaptadas a la línea del comprador."),
    ("High productivity, precision machining and hot-runner balance for beverage closures.", "Alta productividad, mecanizado de precisión y equilibrio del canal caliente para cierres de bebidas."),
    ("Custom Compression & Injection Moulds", "Moldes personalizados de compresión e inyección"),
    ("Hot-runner tooling for still, sparkling and carbonated beverage production.", "Utillaje de canal caliente para bebidas sin gas, con gas y carbonatadas."),
    ("Key Advantages of Our", "Ventajas clave de nuestros"), ("Engineered for repeatable production, stable quality and a clear technical handover.", "Diseñado para una producción repetible, calidad estable y una entrega técnica clara."),
    ("Inside Our Water Cap Mould Engineering", "Dentro de nuestra ingeniería de moldes para tapas de agua"),
    ("Gallery", "Galería"), ("Click any image to enlarge. Samples and reference parts are shown for technical discussion.", "Haga clic en cualquier imagen para ampliarla. Las muestras y piezas de referencia se muestran para la conversación técnica."),
    ("Trial Videos", "Vídeos de pruebas"), ("Watch the mould trial and production references in full screen.", "Vea la prueba del molde y las referencias de producción a pantalla completa."),
    ("Quality Control & Inspection", "Control de calidad e inspección"), ("Every mould passes a documented inspection path before shipment.", "Cada molde sigue un recorrido de inspección documentado antes del envío."),
    ("Quality management evidence stays with the project file.", "La evidencia de gestión de calidad permanece en el expediente del proyecto."),
    ("Can one mould run", "¿Puede un molde producir"), ("What is the mould life?", "¿Cuál es la vida útil del molde?"),
    ("Learn More", "Ver más"), ("Auxiliary Machines", "Máquinas auxiliares"),
    ("cost-effective", "rentable"), ("automated", "automática"), ("assembly", "montaje"),
    ("solution", "solución"), ("high output", "alta producción"), ("replace the manual work of several operators", "sustituye el trabajo manual de varios operarios"),
    ("keeping the process consistent", "manteniendo constante el proceso"), ("Automatically inserts gaskets into bottle caps", "Inserta automáticamente juntas en las tapas de botella"),
    ("improving work efficiency, seating accuracy, product safety and production consistency", "mejorando la eficiencia, la precisión de asentamiento, la seguridad del producto y la estabilidad de la producción"),
    ("precision-built automatic wad inserting and cap lining machine", "máquina automática de inserción de juntas y revestimiento de tapas fabricada con precisión"),
    ("sturdy enclosed stainless-steel frame for reliable servicing and operation", "bastidor cerrado de acero inoxidable para un mantenimiento y funcionamiento fiables"),
    ("Three-part plastic sport-cap assembly equipment", "Equipo de montaje de tapas deportivas de plástico de tres piezas"),
    ("daily chemical and oil production lines", "líneas de producción de productos químicos de uso diario y aceite"),
    ("A non-spill five-gallon water-cap labeling and sealing solution for stable, clean and efficient cap production.", "Solución sin derrames para etiquetar y sellar tapas de garrafón de cinco galones, con una producción estable, limpia y eficiente."),
    ("S136 mirror steel supports long life in high-moisture production environments.", "El acero espejo S136 favorece una larga vida útil en entornos de producción con mucha humedad."),
    ("On-machine trials confirm the output target.", "Las pruebas en máquina confirman el objetivo de producción."),
    ("Mould structure, steel selection, inspection evidence and trial feedback stay connected through the project.", "La estructura del molde, la selección del acero, la evidencia de inspección y los comentarios de las pruebas permanecen conectados durante el proyecto."),
    ("Complete your cap production line with our specialized auxiliary machines. Designed to work seamlessly with our plastic cap molds, these machines handle critical post-molding operations such as lining, folding, slitting, printing, and wadding.", "Complete su línea de producción de tapas con nuestras máquinas auxiliares especializadas. Diseñadas para trabajar con nuestros moldes de tapas de plástico, realizan operaciones posteriores críticas como revestimiento, plegado, corte, impresión y colocación de juntas."),
    ("Why Cap Auxiliary Machines Are Essential", "Por qué son esenciales las máquinas auxiliares para tapas"),
    ("Learn More", "Ver más"), ("Automated Assembly Machine", "Máquina automática de montaje"), ("Cap Assembling Machine", "Máquina de montaje de tapas"), ("Cap Lining Machine", "Máquina de revestimiento de tapas"), ("5 Gallon Cap Labeling Machine", "Máquina de etiquetado de tapas de 5 galones"),
    ("NEWS & INSIGHTS", "NOTICIAS Y ANÁLISIS"), ("BOTTLE CAP MOULDS", "MOLDES DE TAPAS DE BOTELLA"), ("BOTTLE CAP MACHINE", "MÁQUINAS PARA TAPAS"),
    ("EXPLORE OUR WORK", "EXPLORE NUESTRO TRABAJO"), ("PRECISION TOOLING", "UTILLAJE DE PRECISIÓN"),
    ("Years of Experience", "Años de experiencia"), ("Countries Served", "Países atendidos"),
    ("Moulds Delivered", "Moldes entregados"), ("Skilled Team Members", "Miembros cualificados del equipo"),
    ("Design foundation", "Base de diseño"), ("Project matching", "Asignación del proyecto"),
    ("Technology review", "Revisión tecnológica"), ("Precision manufacturing", "Fabricación de precisión"),
    ("Global project support", "Soporte de proyectos internacionales"),
    ("5-Axis CNC Machining Centers", "Centros de mecanizado CNC de 5 ejes"),
    ("High-Speed EDM Machines", "Máquinas EDM de alta velocidad"), ("Wire-Cut EDM Machines", "Máquinas EDM de corte por hilo"),
    ("Precision Grinding Machines", "Máquinas rectificadoras de precisión"), ("CNC Lathes & Milling Machines", "Tornos y fresadoras CNC"),
    ("Injection Molding Trial Machines", "Máquinas de prueba de moldeo por inyección"),
    ("3D Coordinate Measuring Machines (CMM)", "Máquinas de medición por coordenadas 3D (CMM)"),
    ("Hardness Testers & Spectrometers", "Durómetros y espectrómetros"),
    ("Project quality records", "Registros de calidad del proyecto"), ("Material traceability", "Trazabilidad del material"),
    ("Trial and inspection evidence", "Evidencia de pruebas e inspección"), ("Buyer-specific documentation", "Documentación específica del comprador"),
    ("What Buyers Say", "Opiniones de compradores"), ("Common Questions", "Preguntas frecuentes"),
    ("Mould Trials", "Pruebas de moldes"), ("Samples", "Muestras"), ("Video Gallery", "Galería de vídeos"),
    ("Mould trial video", "Vídeo de prueba del molde"), ("Close", "Cerrar"), ("Play video", "Reproducir vídeo"),
    ("Play", "Reproducir"), ("Factory Address", "Dirección de fábrica"), ("Contact Methods", "Métodos de contacto"),
    ("PHONE / WHATSAPP", "TELÉFONO / WHATSAPP"), ("WEBSITE", "SITIO WEB"),
    ("Still Have Questions?", "¿Aún tiene preguntas?"), ("Quick Answers", "Respuestas rápidas"),
    ("Start Your Cap Mould Project", "Inicie su proyecto de moldes"),
    ("Want to See More Samples or Request a Quote?", "¿Quiere ver más muestras o solicitar una cotización?"),
    ("Need Auxiliary Equipment for Your Cap Line?", "¿Necesita equipos auxiliares para su línea de tapas?"),
    ("Let's Work Together", "Trabajemos juntos"),
    ("What is the typical cycle time?", "¿Cuál es el tiempo de ciclo habitual?"),
    ("Can one mould run PCO 1881 and 30/25?", "¿Puede un molde producir PCO 1881 y 30/25?"),
    ("What is the mould life?", "¿Cuál es la vida útil del molde?"),
    ("Do you provide installation support?", "¿Ofrecen soporte de instalación?"),
    ("A 48-cavity PCO 1881 mould commonly runs around 4.8–5.5 seconds, depending on the machine and resin.", "Un molde PCO 1881 de 48 cavidades suele trabajar en torno a 4,8–5,5 segundos, según la máquina y la resina."),
    ("Interchangeable cavity sets can be reviewed for compatible neck finishes.", "Podemos revisar juegos de cavidades intercambiables para acabados de cuello compatibles."),
    ("With maintenance, premium steel cavity components are designed for more than 5 million cycles.", "Con mantenimiento, los componentes de cavidad de acero premium están diseñados para superar 5 millones de ciclos."),
    ("Remote setup guidance and trial support are included in the technical handover.", "La orientación remota de puesta en marcha y el soporte de pruebas forman parte de la entrega técnica."),
    ("Water & Beverage Cap Mould Solutions", "Soluciones de moldes para tapas de agua y bebidas"),
    ("Water & Beverage Cap Mould Types", "Tipos de moldes para tapas de agua y bebidas"),
    ("Mineral Water Closure Cap Moulds | High-Precision Manufacturer", "Moldes para tapas de agua mineral | Fabricante de alta precisión"),
    ("Ideal for screw caps for mineral water, purified water, spring water and other beverage PET bottles.", "Ideales para tapas roscadas de agua mineral, agua purificada, agua de manantial y otras botellas PET de bebidas."),
    ("Custom neck finishes and high-speed closure tooling for international packaging projects.", "Acabados de cuello personalizados y utillaje de cierres de alta velocidad para proyectos internacionales de envases."),
    ("for international packaging projects", "para proyectos internacionales de envases"),
    ("CMM Inspection", "Inspección CMM"), ("Full dimensional reports for all cavities.", "Informes dimensionales completos para todas las cavidades."),
    ("Cycle Time Verification", "Verificación del tiempo de ciclo"), ("Cap Weight Audit", "Auditoría del peso de la tapa"),
    ("material distribution is checked cavity by cavity.", "la distribución del material se comprueba cavidad por cavidad."),
    ("ISO 9001 Certified", "Registros de calidad del proyecto"), ("Ultra-Fast Cycles", "Ciclos ultrarrápidos"),
    ("Optimized cooling and hot runners can achieve cycle times from 4.5 seconds.", "La refrigeración optimizada y los canales calientes pueden lograr tiempos de ciclo desde 4,5 segundos."),
    ("Micron-Level Tolerances", "Tolerancias a nivel de micras"),
    ("cavity-to-cavity variation is controlled for consistent cap dimensions.", "la variación entre cavidades se controla para mantener dimensiones uniformes de la tapa."),
    ("PCO & ISBT Standards", "Normas PCO e ISBT"),
    ("Neck-finish options support international beverage packaging requirements.", "Las opciones de acabado de cuello cumplen los requisitos internacionales de envases para bebidas."),
    ("Hot Runner Integration", "Integración de canal caliente"),
    ("Balanced nozzle control reduces waste and protects fill consistency.", "El control equilibrado de las boquillas reduce el desperdicio y protege la uniformidad del llenado."),
    ("Corrosion-Resistant Steel", "Acero resistente a la corrosión"), ("Quick Cavity Expansion", "Ampliación rápida de cavidades"),
    ("Modular inserts make future cavity upgrades easier to plan.", "Los insertos modulares facilitan planificar futuras ampliaciones de cavidades."),
    ("Stripper Plate & Ejection", "Placa extractora y expulsión"),
    ("A guided stripper plate releases tamper-evident caps smoothly without deforming bridges.", "Una placa extractora guiada libera suavemente las tapas con precinto sin deformar los puentes."),
    ("Hardened H13 stripper plate", "Placa extractora H13 endurecida"), ("Guided ejection with linear bearings", "Expulsión guiada con rodamientos lineales"),
    ("Two-stage ejection for fragile bridges", "Expulsión en dos etapas para puentes delicados"),
    ("Hot Runner & Cooling Design", "Diseño de canal caliente y refrigeración"),
    ("Balanced hot-runner layouts and conformal cooling keep temperature uniform in cavities.", "Los canales calientes equilibrados y la refrigeración conforme mantienen uniforme la temperatura en las cavidades."),
    ("Valve-gate or open-gate options", "Opciones de compuerta de válvula o abierta"),
    ("3D-printed conformal cooling inserts", "Insertos de refrigeración conforme impresos en 3D"),
    ("Thermal imaging verification before shipment", "Verificación por imagen térmica antes del envío"),
    ("PCO 1881 water cap mould trial", "Prueba de molde de tapas de agua PCO 1881"),
    ("Sports cap mould trial", "Prueba de molde de tapas deportivas"),
    ("PCO 1881 water cap mold", "Molde de tapas de agua PCO 1881"),
    ("Mineral Water Cap Injection Mould", "Molde de inyección de tapas para agua mineral"),
    ("38mm Neck Mineral Water Closure Mould", "Molde de cierre de agua mineral con cuello de 38 mm"),
    ("Balanced hot-runner layouts", "Diseño equilibrado de canales calientes"),
    ("keep temperature uniform", "mantienen uniforme la temperatura"), ("in cavities", "en las cavidades"),
    ("hot-runner", "canal caliente"), ("Custom neck finishes", "Acabados de cuello personalizados"),
    ("high-speed closure tooling", "utillaje de cierres de alta velocidad"),
    ("Ideal for screw caps", "Ideales para tapas roscadas"),
    ("The 72-cavity PCO 1881 mould doubled our output while keeping cap quality consistent.", "El molde PCO 1881 de 72 cavidades duplicó nuestra producción manteniendo constante la calidad de las tapas."),
    ("The lightweight cap design reduced material cost without changing the seal.", "El diseño ligero de la tapa redujo el coste de material sin cambiar el sellado."),
    ("The trial report made approval straightforward for our production team.", "El informe de pruebas facilitó la aprobación para nuestro equipo de producción."),
    ("Bottling plant manager", "Responsable de planta embotelladora"), ("Packaging engineer", "Ingeniero de envases"),
    ("Operations director", "Director de operaciones"), ("Water & Beverage", "Agua y bebidas"),
    ("Types", "Tipos"), ("Ideal", "Ideal"), ("Solutions", "Soluciones"), ("for PCO", "para PCO"),
    ("Bottle cap mold injection process", "Proceso de inyección de moldes para tapas"), ("5 gallon handle trial video", "Vídeo de prueba de asa para garrafón de 5 galones"),
    ("Flip Top Caps Mould Combination Video", "Vídeo de combinación de moldes de tapas abatibles"), ("Bottle cap assembly machine", "Máquina de montaje de tapas"),
)


def _replace(text: str, replacements: tuple[tuple[str, str], ...]) -> str:
    value = str(text or "")
    protected: dict[str, str] = {}
    for index, token in enumerate(("LEYA MOULD", "HMould", "WhatsApp", "PET", "OEM", "ODM", "DFM")):
        marker = f"\uE000{index}\uE001"
        value = re.sub(re.escape(token), marker, value, flags=re.I)
        protected[marker] = token
    for source, target in sorted(replacements, key=lambda row: len(row[0]), reverse=True):
        value = re.sub(r"(?<![A-Za-z])" + re.escape(source) + r"(?![A-Za-z])", target, value, flags=re.I)
    for marker, token in protected.items():
        value = value.replace(marker, token)
    return re.sub(r"\s{2,}", " ", value).strip()


def spanish_model_text(value: Any) -> str:
    """Translate only the descriptive shell of a model name/ALT."""
    text = re.sub(r"[-_]+", " ", str(value or "")).strip()
    text = _replace(text, _MODEL_REPLACEMENTS)
    return re.sub(r"\s+", " ", text).strip()


def spanish_model_description(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return "Referencia de catálogo HMould. La configuración final de cavidades, el acero, la interfaz de máquina y la evidencia de producción se confirman durante la revisión del proyecto de LEYA MOULD."
    return _replace(text, (("HMould catalogue model reference", "Referencia de catálogo de HMould"), ("Final cavity plan", "La configuración final de cavidades"), ("steel", "el acero"), ("machine interface", "la interfaz de máquina"), ("production evidence", "la evidencia de producción"), ("are confirmed during LEYA MOULD project review", "se confirman durante la revisión del proyecto de LEYA MOULD")) + _EDITORIAL_REPLACEMENTS)


def spanish_editorial_copy(value: Any) -> Any:
    """Return a copy with only Spanish-facing strings cleaned up."""
    def clean(node: Any, active: bool = False) -> Any:
        if isinstance(node, str):
            return _replace(node, _EDITORIAL_REPLACEMENTS) if active else node
        if isinstance(node, list):
            return [clean(item, active) for item in node]
        if isinstance(node, dict):
            result = {}
            for key, item in node.items():
                # Editorial objects use {en: ..., es: ...} at every level.
                # Keep English and owner metadata byte-for-byte unchanged; only
                # clean the Spanish branch and the language-neutral evidence
                # source labels.
                result[key] = clean(item, active or key == "es" or key == "evidenceSources")
            return result
        return copy.deepcopy(node)
    return clean(value)


def spanish_ui_text(value: Any) -> str:
    """Translate reviewed UI/category phrases without altering model facts."""
    return _replace(str(value or ""), _UI_REPLACEMENTS + _EDITORIAL_REPLACEMENTS)


def spanish_ui_copy(value: Any) -> Any:
    """Copy a page-specific English fallback into its Spanish UI form."""
    if isinstance(value, str):
        return spanish_ui_text(value)
    if isinstance(value, tuple):
        return tuple(spanish_ui_copy(item) for item in value)
    if isinstance(value, list):
        return [spanish_ui_copy(item) for item in value]
    if isinstance(value, dict):
        return {key: spanish_ui_copy(item) for key, item in value.items()}
    return copy.deepcopy(value)


def repair_es_common_copy(current: Any) -> dict:
    """Fill missing/stale Spanish fields while leaving owner-specific text intact."""
    result = copy.deepcopy(current) if isinstance(current, dict) else {}
    result.setdefault("es", {})
    if not isinstance(result["es"], dict):
        result["es"] = {}
    return result
