// Fixed, owner-approved LEYA MOULD content seed.
//
// This endpoint is deliberately source-bound: it imports the reviewed News
// registry and the canonical shell baselines from this repository. It inserts
// only missing D1 rows, so an owner edit already present in D1 is never
// overwritten by a rebuild or by a rerun of this migration.
import EDITORIAL_DATA from "../../../data/mould-news-editorial.json";
import MOULD_CATALOG from "../../../data/mould-catalog.json";
import PRODUCT_STRUCTURED from "../../../data/mould-product-structured.json";
import PAGE_STRUCTURED_DATA from "../../../data/mould-page-structured.json";
import PAGE_BODY_DATA from "../../../data/mould-page-bodies.json";
import LEGACY_MEDIA_MANIFEST from "../../../data/mould-legacy-media-manifest.json";
import { authorizedMouldContentSeedRequest } from "../../_shared/build-auth.js";
import { ensureBlogSchema } from "../../_shared/blog-cms.js";
import { bumpPublishRevision, loadLanguageConfig, publicLanguages } from "../../_shared/site-settings.js";
import { ensureProductSeo } from "../../_shared/product-seo.js";
import { MOULD_PUBLIC_ROUTES, MOULD_ROUTES } from "../../_shared/mould-routes.js";

const respond = (body, status = 200) => Response.json(body, {
  status,
  headers: { "cache-control": "no-store", "x-robots-tag": "noindex,nofollow,noarchive" }
});

const BRAND = {
  schemaVersion: 1,
  source: {
    mode: "cloudflare-d1-site_state.brand_config",
    verifiedFromOrigin: "LEYA MOULD owner profile",
    capturedAt: "2026-11-24",
    note: "Initial LEYA MOULD shell seed; later owner edits remain authoritative."
  },
  identity: {
    legalName: "LEYA MOULD Co.,Ltd",
    displayName: "LEYA MOULD",
    textName: "LEYA MOULD",
    upperName: "LEYA MOULD",
    filterBrandName: "LEYA MOULD",
    acronym: "LM"
  },
  contact: {
    email: "amyhu@leyamould.com",
    phoneDisplay: "+86 136 0672 7715",
    phoneE164: "+8613606727715",
    whatsappUrl: "https://wa.me/8613606727715",
    whatsappShortUrl: "https://wa.me/8613606727715",
    address: "4-55,Xicheng New Village,Huangyan Taizhou,Zhejiang Province, China"
  },
  logos: {
    header: { src: "/assets/leyamould-logo.svg?v=logo1", alt: "LEYA MOULD" },
    footer: { src: "/assets/leyamould-logo.svg?v=logo1", alt: "LEYA MOULD" }
  },
  social: {},
  footer: {
    about: "Bottle, cap, preform and custom product mould support for international buyers.",
    contactHeading: "Contact LEYA MOULD",
    copyright: "© 2026 LEYA MOULD"
  },
  seo: {
    home: {
      en: { title: "Plastic Mould Manufacturer in China | LEYA MOULD", description: "Plastic injection moulds and tooling solutions for bottle, cap, preform and custom packaging projects." },
      es: { title: "Fabricante de moldes de plástico en China | LEYA MOULD", description: "Moldes de inyección y soluciones de utillaje para botellas, tapones, preformas y envases personalizados." }
    }
  },
  email: { defaultFromName: "LEYA MOULD Website", defaultFromPlaceholder: "amyhu@leyamould.com", ehloDomain: "leyamould.com" }
};

const COMMON_COPY = {
  en: {
    home: "Home", about: "About us", cap_mould: "Cap Mould", machine: "Machine", samples: "Sample", news: "News", video: "Video", contact_us: "Contact Us", contact: "Contact", quote: "Request a Quote", faq_title: "FAQs",
    footer_eyebrow: "LEYA MOULD · ENGINEERING · MANUFACTURING", footer_cta_title: "Ready to discuss your mould project?", footer_cta_text: "Send your drawing, sample or PDF and tell us the production target.", footer_products: "Products", footer_capabilities: "Capabilities", footer_contact: "Contact Us", footer_quick_links: "Quick Links", footer_quote: "Request a Quote →", footer_privacy: "Privacy Policy", footer_sitemap: "Sitemap", footer_sticky: "Mould Project Enquiries", footer_tagline: "Bottle, cap, preform and custom product mould support for international buyers.",
    shared_cta: {
      catalog: { title: "Start Your Cap Mould Project", description: "Send your drawing, sample or production requirements. We will reply with the next technical questions and a clear path forward.", note: "Contact us for a quote and technical consultation — we will reply within 24 hours.", eyebrow: "LEYA MOULD · ENGINEERING · SUPPORT", quoteLabel: "Request a Quote", phoneLabel: "Phone / WhatsApp", emailLabel: "Email", whatsappLabel: "WhatsApp" },
      samples: { title: "Want to See More Samples or Request a Quote?", description: "Contact LEYA MOULD today. We will send you the right samples and a practical proposal for your project.", note: "Tell us about your mould", eyebrow: "LEYA MOULD · ENGINEERING · SUPPORT", quoteLabel: "Request a Quote", phoneLabel: "Phone / WhatsApp", emailLabel: "Email", whatsappLabel: "WhatsApp" },
      auxiliary: { title: "Need Auxiliary Equipment for Your Cap Line?", description: "Contact LEYA MOULD to discuss your cap size, production volume and the auxiliary operations you require. We will recommend a practical machine setup for your factory.", note: "Tell us about your line", eyebrow: "LEYA MOULD · ENGINEERING · SUPPORT", quoteLabel: "Request a Quote", phoneLabel: "Phone / WhatsApp", emailLabel: "Email", whatsappLabel: "WhatsApp" },
      about: { title: "Let's Work Together", description: "Share your drawing, sample or production brief and we will help shape the next technical step.", note: "Chat with LEYA MOULD", eyebrow: "LEYA MOULD · ENGINEERING · SUPPORT", quoteLabel: "Request a Quote", phoneLabel: "Phone / WhatsApp", emailLabel: "Email", whatsappLabel: "WhatsApp" },
      faq: { title: "Still Have Questions?", description: "Our team is ready to help. Reach out and we'll respond within 24 hours.", note: "Ask about your project", eyebrow: "LEYA MOULD · ENGINEERING · SUPPORT", quoteLabel: "Request a Quote", phoneLabel: "Phone / WhatsApp", emailLabel: "Email", whatsappLabel: "WhatsApp" },
      category: { title: "Start Your Cap Mould Project", description: "Send us your drawing, sample, target material, cavity plan and delivery market. We will reply with the next technical questions.", note: "Tell us about your mould", eyebrow: "LEYA MOULD · ENGINEERING · SUPPORT", quoteLabel: "Request a Quote", phoneLabel: "Phone / WhatsApp", emailLabel: "Email", whatsappLabel: "WhatsApp" }
    }
  },
  es: {
    home: "Inicio", about: "Sobre nosotros", cap_mould: "Moldes de tapones", machine: "Máquina", samples: "Muestras", news: "Noticias", video: "Vídeo", contact_us: "Contacto", contact: "Contacto", quote: "Solicitar cotización", faq_title: "Preguntas frecuentes",
    footer_eyebrow: "LEYA MOULD · INGENIERÍA · FABRICACIÓN", footer_cta_title: "¿Hablamos de su proyecto?", footer_cta_text: "Envíe su plano, muestra o PDF y el objetivo de producción.", footer_products: "Productos", footer_capabilities: "Capacidades", footer_contact: "Contacto", footer_quick_links: "Enlaces rápidos", footer_quote: "Solicitar cotización →", footer_privacy: "Privacidad", footer_sitemap: "Mapa del sitio", footer_sticky: "Consultas de moldes", footer_tagline: "Soporte para moldes de botellas, tapones, preformas y productos a medida.",
    shared_cta: {
      catalog: { title: "Empiece su proyecto de moldes", description: "Envíenos su dibujo, muestra o requisitos de producción. Responderemos con las siguientes preguntas técnicas y un camino claro.", note: "Contáctenos para una cotización y consulta técnica; responderemos en 24 horas.", eyebrow: "LEYA MOULD · INGENIERÍA · SOPORTE", quoteLabel: "Solicitar cotización", phoneLabel: "Teléfono / WhatsApp", emailLabel: "Correo electrónico", whatsappLabel: "WhatsApp" },
      samples: { title: "¿Quiere ver más muestras o solicitar una cotización?", description: "Contacte hoy con LEYA MOULD. Le enviaremos las muestras adecuadas y una propuesta práctica para su proyecto.", note: "Cuéntenos sobre su molde", eyebrow: "LEYA MOULD · INGENIERÍA · SOPORTE", quoteLabel: "Solicitar cotización", phoneLabel: "Teléfono / WhatsApp", emailLabel: "Correo electrónico", whatsappLabel: "WhatsApp" },
      auxiliary: { title: "¿Necesita equipos auxiliares para su línea de tapas?", description: "Contacte con LEYA MOULD para hablar del tamaño de la tapa, el volumen de producción y las operaciones auxiliares que necesita. Le recomendaremos una configuración práctica.", note: "Cuéntenos sobre su línea", eyebrow: "LEYA MOULD · INGENIERÍA · SOPORTE", quoteLabel: "Solicitar cotización", phoneLabel: "Teléfono / WhatsApp", emailLabel: "Correo electrónico", whatsappLabel: "WhatsApp" },
      about: { title: "Trabajemos juntos", description: "Comparta su plano, muestra o requisitos de producción y le ayudaremos a definir el siguiente paso técnico.", note: "Hable con LEYA MOULD", eyebrow: "LEYA MOULD · INGENIERÍA · SOPORTE", quoteLabel: "Solicitar cotización", phoneLabel: "Teléfono / WhatsApp", emailLabel: "Correo electrónico", whatsappLabel: "WhatsApp" },
      faq: { title: "¿Todavía tiene preguntas?", description: "Nuestro equipo está listo para ayudarle. Escríbanos y responderemos en un plazo de 24 horas.", note: "Consulte su proyecto", eyebrow: "LEYA MOULD · INGENIERÍA · SOPORTE", quoteLabel: "Solicitar cotización", phoneLabel: "Teléfono / WhatsApp", emailLabel: "Correo electrónico", whatsappLabel: "WhatsApp" },
      category: { title: "Inicie su proyecto de moldes", description: "Envíenos el plano, la muestra, el material, las cavidades y el mercado de destino. Responderemos con las siguientes preguntas técnicas.", note: "Cuéntenos sobre su molde", eyebrow: "LEYA MOULD · INGENIERÍA · SOPORTE", quoteLabel: "Solicitar cotización", phoneLabel: "Teléfono / WhatsApp", emailLabel: "Correo electrónico", whatsappLabel: "WhatsApp" }
    }
  }
};

const NAVIGATION = [
  ["home", "", "Home", "/", 10],
  ["about", "", "About Us", "/about/", 20],
  ["products", "", "Cap Mould", "/Plastic-cap-mold.html", 30],
  ["product-water", "products", "Mineral Water Cap Mould", "/product/Mineral-Water-Closure-cap-Molds.html", 10],
  ["product-five-gallon", "products", "5 Gallon Water Cap Mould", "/product/5-Gallon-Water-Cap-Mould.html", 20],
  ["product-oil", "products", "Edible Oil Cap Mould", "/product/Oil-bottle-cap-mould.html", 30],
  ["product-flip", "products", "Flip top caps mould", "/product/Flip-top-caps-mould.html", 40],
  ["product-engine", "products", "Engine Oil Cap Mould", "/product/Engine-Oil-Cap-Mould.html", 50],
  ["product-food", "products", "Food Packaging Cap Mould", "/product/Food-Packaging-Cap-Mould.html", 60],
  ["product-medical", "products", "Medical Cap Mould", "/product/Medical-Cap-Mould.html", 70],
  ["product-personal", "products", "Personal Care Cap Mould", "/product/Personal-Care-Cap-Mould.html", 80],
  ["product-functional", "products", "Functional Cap Mould(Combination)", "/product/Functional-Cap-Mould.html", 90],
  ["product-handle", "products", "Plastic Handle mould", "/product/Plastic-Handle-Cap-mould.html", 100],
  ["product-wine", "products", "Wine Cap Mould", "/product/Wine-Cap-Mould.html", 110],
  ["product-pet-preform", "products", "PET Preform Mould", "/product/PET-Preform-Mould.html", 120],
  ["product-blow-bottle", "products", "Blow Bottle Mould", "/product/Blow-Bottle-Mould.html", 130],
  ["machine", "", "Machine", "/Bottle-Cap-Machine/Bottle-Cap-Machine.html", 40],
  ["samples", "", "Samples", "/samples/", 50],
  ["news", "", "News", "/news/", 60],
  ["video", "", "Video", "/video/", 70],
  ["contact", "", "Contact Us", "/contact/", 80]
];

const PAGE_COPY = {
  "/": ["Homepage", "Plastic Mould Manufacturer in China | LEYA MOULD", "Plastic injection moulds and tooling solutions for bottle, cap, preform and custom packaging projects."],
  "/about/": ["About", "About LEYA MOULD | Precision Plastic Mould Manufacturer", "Learn about LEYA MOULD's engineering-led approach to plastic bottle, cap, preform and custom product mould projects."],
  "/products/": ["Mould Categories", "Plastic Cap Mould Categories | LEYA MOULD", "Explore cap mould, bottle mould, preform mould and custom packaging tooling directions."],
  "/Plastic-cap-mold.html": ["Mould Categories", "Plastic Cap Mould Manufacturer | LEYA MOULD", "Review LEYA MOULD plastic cap mould families, applications and project information."],
  "/capabilities/": ["Capabilities", "Cap Auxiliary Machines and Mould Capabilities | LEYA MOULD", "Explore auxiliary equipment, mould engineering, manufacturing and trial support for cap production."],
  "/capabilities/mould-design/": ["Mould Design & Engineering", "Mould Design and Engineering | LEYA MOULD", "DFM review, parting, cooling, ejection and tooling decisions connected to the approved part requirement."],
  "/capabilities/precision-manufacturing/": ["Precision Manufacturing", "Precision Mould Manufacturing | LEYA MOULD", "Documented machining, EDM, fitting and inspection support for repeatable plastic mould production."],
  "/capabilities/trial-sampling/": ["Trial, Sampling & Optimisation", "Mould Trial and Sampling Support | LEYA MOULD", "Trial parts, dimensional checks and agreed evidence before production handover."],
  "/manufacturing/": ["How We Work", "Plastic Mould Manufacturing Process | LEYA MOULD", "A clear path from drawing review and DFM to machining, trial, inspection and technical handover."],
  "/quality-control/": ["Quality Control", "Mould Quality Control and Inspection | LEYA MOULD", "Quality checks, inspection evidence and change control for plastic cap and packaging mould projects."],
  "/request-sample/": ["Request a Sample", "Request a Plastic Mould Sample | LEYA MOULD", "Share your drawing, sample and production target for a project-specific mould review."],
  "/contact/": ["Contact Us", "Contact LEYA MOULD | Plastic Mould Projects", "Send LEYA MOULD your part drawing, material, cavity plan, machine information and target market."],
  "/samples/": ["Plastic Cap Samples", "Plastic Cap Mould Samples | LEYA MOULD", "Explore plastic cap samples and the mould directions used for packaging applications."],
  "/news/": ["News", "Plastic Cap Mould News and Engineering Insights | LEYA MOULD", "Technical news, buyer notes and engineering insights for plastic cap mould projects."],
  "/news/Bottle-cap-molds.html": ["Bottle Cap Mould News", "Bottle Cap Mould News | LEYA MOULD", "Engineering articles and buyer guidance for bottle cap mould design and production."],
  "/Bottle-Cap-Machine/Bottle-Cap-Machine.html": ["Bottle Cap Machine", "Bottle Cap Machines and Auxiliary Equipment | LEYA MOULD", "Auxiliary equipment and production support for bottle cap assembly, lining and handling."],
  "/video/": ["Video", "Cap Mould Trial Videos | LEYA MOULD", "Watch LEYA MOULD mould trial, tooling and auxiliary equipment videos."],
  "/faq/": ["FAQ", "Plastic Mould Project FAQs | LEYA MOULD", "Answers to common questions about drawings, materials, cavities, trials and mould project delivery."],
  "/blog/": ["Blog", "Mould Project Resources | LEYA MOULD", "Reviewed technical resources for buyers planning plastic mould and tooling projects."],
  "/privacy-policy/": ["Privacy Policy", "Privacy Policy | LEYA MOULD", "How LEYA MOULD handles project enquiry and contact information."]
};

// Structured public copy is separate from the SEO registry above.  It contains
// editable page-intro fields and a small set of body section labels; the
// renderer still owns the DOM and layout.  Missing fields are intentionally
// filled from the checked-in source renderer, never from owner-edited HTML.
const STRUCTURED_PAGE_COPY = {
  en: {
    "/about/": { eyebrow: "OUR STORY", title: "About LEYA MOULD", subtitle: "LEYA MOULD is a mould-project brand based in Huangyan, Taizhou, Zhejiang Province, China. We support international buyers with precision, clear engineering communication and practical project support.", sections: { overview: { title: "Who We Are" }, journey: { title: "Our Journey" }, advantages: { title: "Why Choose LEYA MOULD" }, facility: { title: "Our Facility & Equipment" }, quality: { title: "Certifications & Quality" }, production: { title: "Our Production Facilities" } } },
    "/products/": { eyebrow: "LEYA MOULD · PRECISION TOOLING", title: "Mould Categories", subtitle: "Explore cap mould, bottle mould, preform mould and custom packaging tooling directions." },
    "/Plastic-cap-mold.html": { eyebrow: "LEYA MOULD · PRECISION TOOLING", title: "Mould Categories", subtitle: "Review LEYA MOULD plastic cap mould families, applications and project information." },
    "/capabilities/": { eyebrow: "AUXILIARY EQUIPMENT", title: "Cap Auxiliary Machines", subtitle: "Complete your cap production line with specialized auxiliary machines for lining, folding, slitting, printing and wadding." },
    "/manufacturing/": { eyebrow: "HOW WE WORK", title: "Manufacturing Process", subtitle: "A clear path from drawing review and DFM to machining, trial, inspection and technical handover." },
    "/quality-control/": { eyebrow: "QUALITY CONTROL", title: "Quality Control", subtitle: "Quality checks, inspection evidence and change control for plastic cap and packaging mould projects." },
    "/request-sample/": { eyebrow: "REQUEST A SAMPLE", title: "Request a Sample", subtitle: "Share your drawing, sample and production target for a project-specific mould review." },
    "/contact/": { eyebrow: "LEYA MOULD · PRECISION TOOLING", title: "Contact Us", subtitle: "Send LEYA MOULD your part drawing, material, cavity plan, machine information and target market." },
    "/samples/": { eyebrow: "LEYA MOULD · PRECISION TOOLING", title: "Plastic Cap Samples", subtitle: "Explore a wide variety of plastic bottle caps manufactured with high-precision injection moulds." },
    "/news/": { eyebrow: "LEYA MOULD · PRECISION TOOLING", title: "News & Updates", subtitle: "Stay informed with LEYA MOULD mould technology, project notes and engineering insights." },
    "/video/": { eyebrow: "EXPLORE OUR WORK", title: "Video Gallery", subtitle: "Watch our latest mould demonstrations, factory tours and technical insights." },
    "/faq/": { eyebrow: "HELP CENTER", title: "Frequently Asked Questions", subtitle: "Find quick answers to common questions about our plastic cap moulds, auxiliary machines, ordering process and support." }
  },
  es: {
    "/about/": { eyebrow: "NUESTRA HISTORIA", title: "Sobre LEYA MOULD", subtitle: "LEYA MOULD es una marca de proyectos de moldes con sede en Huangyan, Taizhou, Zhejiang, China. Acompañamos a compradores internacionales con precisión, comunicación técnica clara y soporte práctico.", sections: { overview: { title: "Quiénes somos" }, journey: { title: "Nuestro recorrido" }, advantages: { title: "Por qué elegir LEYA MOULD" }, facility: { title: "Instalaciones y equipos" }, quality: { title: "Certificaciones y calidad" }, production: { title: "Nuestras instalaciones de producción" } } },
    "/products/": { eyebrow: "LEYA MOULD · UTILLAJE DE PRECISIÓN", title: "Categorías de moldes", subtitle: "Explore moldes de tapas, botellas, preformas y soluciones de utillaje para envases personalizados." },
    "/Plastic-cap-mold.html": { eyebrow: "LEYA MOULD · UTILLAJE DE PRECISIÓN", title: "Categorías de moldes", subtitle: "Revise las familias de moldes de tapas de plástico, sus aplicaciones y la información del proyecto." },
    "/capabilities/": { eyebrow: "EQUIPOS AUXILIARES", title: "Máquinas auxiliares para tapas", subtitle: "Complete su línea de producción con máquinas auxiliares para lining, plegado, corte, impresión y wadding." },
    "/manufacturing/": { eyebrow: "CÓMO TRABAJAMOS", title: "Proceso de fabricación", subtitle: "Un camino claro desde la revisión del plano y DFM hasta el mecanizado, la prueba, la inspección y la entrega técnica." },
    "/quality-control/": { eyebrow: "CONTROL DE CALIDAD", title: "Control de calidad", subtitle: "Comprobaciones de calidad, evidencias de inspección y control de cambios para proyectos de moldes de tapas y envases." },
    "/request-sample/": { eyebrow: "SOLICITAR UNA MUESTRA", title: "Solicitar una muestra", subtitle: "Comparta su plano, muestra y objetivo de producción para una revisión de molde específica." },
    "/contact/": { eyebrow: "LEYA MOULD · UTILLAJE DE PRECISIÓN", title: "Contacto", subtitle: "Envíe a LEYA MOULD el plano de la pieza, material, cavidades, información de máquina y mercado de destino." },
    "/samples/": { eyebrow: "LEYA MOULD · UTILLAJE DE PRECISIÓN", title: "Muestras de tapas de plástico", subtitle: "Explore una amplia variedad de tapas de botellas fabricadas con moldes de inyección de alta precisión." },
    "/news/": { eyebrow: "LEYA MOULD · UTILLAJE DE PRECISIÓN", title: "Noticias y novedades", subtitle: "Conozca las novedades técnicas, notas de proyectos y conocimientos de ingeniería de LEYA MOULD." },
    "/video/": { eyebrow: "EXPLORE NUESTRO TRABAJO", title: "Galería de vídeos", subtitle: "Vea nuestras demostraciones de moldes, recorridos de fábrica y conocimientos técnicos." },
    "/faq/": { eyebrow: "CENTRO DE AYUDA", title: "Preguntas frecuentes", subtitle: "Encuentre respuestas rápidas sobre nuestros moldes de tapas, máquinas auxiliares, proceso de pedido y soporte técnico." }
  }
};
for (const [locale, routes] of Object.entries(PAGE_STRUCTURED_DATA || {})) {
  if (!STRUCTURED_PAGE_COPY[locale]) STRUCTURED_PAGE_COPY[locale] = {};
  for (const [route, value] of Object.entries(routes || {})) {
    STRUCTURED_PAGE_COPY[locale][route] = { ...(STRUCTURED_PAGE_COPY[locale][route] || {}), ...(value || {}) };
  }
}

const PRODUCT_COPY = {
  "mineral-water-closure-cap-molds": ["Mineral Water Cap Mould", "Mineral Water Cap Mould Manufacturer | LEYA MOULD", "Plastic cap moulds for mineral water, beverage and PET closure applications."],
  "oil-bottle-cap-mould": ["Edible Oil Cap Mould", "Edible Oil Cap Mould Manufacturer | LEYA MOULD", "Tooling solutions for edible oil closures, pull-ring caps and pouring applications."],
  "flip-top-caps-mould": ["Flip Top Cap Mould", "Flip Top Cap Mould Manufacturer | LEYA MOULD", "Living-hinge flip-top cap moulds for personal care, household and dispensing packaging."],
  "engine-oil-cap-mould": ["Engine Oil Cap Mould", "Engine Oil Cap Mould Manufacturer | LEYA MOULD", "Durable mould solutions for engine oil, lubricant and industrial closure applications."],
  "food-packaging-cap-mould": ["Food Packaging Cap Mould", "Food Packaging Cap Mould Manufacturer | LEYA MOULD", "Plastic cap moulds for sauces, food, dairy and dry-food packaging closures."],
  "medical-cap-mould": ["Medical Cap Mould", "Medical Cap Mould Manufacturer | LEYA MOULD", "Precision moulding support for pharmaceutical, medical and diagnostic closures."],
  "personal-care-cap-mould": ["Personal Care Cap Mould", "Personal Care Cap Mould Manufacturer | LEYA MOULD", "Cap moulds for shampoo, lotion, disc-top and personal care packaging."],
  "functional-cap-mould": ["Functional Cap Mould", "Functional Cap Mould Manufacturer | LEYA MOULD", "Combination, dispensing and safety closure mould solutions for functional packaging."],
  "plastic-handle-cap-mould": ["Plastic Handle Mould", "Plastic Handle Mould Manufacturer | LEYA MOULD", "Injection moulds for bottle handles, carry handles and large-container packaging."],
  "five-gallon-water-cap-mould": ["5 Gallon Water Cap Mould", "5 Gallon Water Cap Mould Manufacturer | LEYA MOULD", "Mould solutions for large-format water closures, refill containers and 5 gallon packaging."],
  "wine-cap-mould": ["Wine Cap Mould", "Wine Cap Mould Manufacturer | LEYA MOULD", "Plastic closure mould solutions for wine, spirits and specialty beverage packaging."],
  "pet-preform-mould": ["PET Preform Mould", "PET Preform Mould Manufacturer | LEYA MOULD", "PET preform mould support for beverage, water, oil and custom bottle production."],
  "blow-bottle-mould": ["Blow Bottle Mould", "Blow Bottle Mould Manufacturer | LEYA MOULD", "Bottle mould solutions for blow-moulded packaging, containers and custom bottle projects."]
};

function isoDate(value) { return String(value || "").replaceAll("/", "-").slice(0, 10); }
function json(value) { return JSON.stringify(value); }
function mergeMissing(target, baseline) {
  let changed = false;
  if (!target || typeof target !== "object" || Array.isArray(target)) target = {};
  for (const [key, value] of Object.entries(baseline || {})) {
    if (!(key in target)) {
      target[key] = value;
      changed = true;
    } else if (value && typeof value === "object" && !Array.isArray(value) && target[key] && typeof target[key] === "object" && !Array.isArray(target[key])) {
      if (mergeMissing(target[key], value)) changed = true;
    }
  }
  return changed ? target : null;
}
// Replace only values that are absent or still equal to the original English
// baseline. This lets the reviewed Spanish baseline repair the first seed
// without overwriting a later owner edit in D1.
function mergeReviewed(target, baseline, englishBaseline) {
  let changed = false;
  if (!target || typeof target !== "object" || Array.isArray(target)) target = {};
  for (const [key, value] of Object.entries(baseline || {})) {
    const current = target[key];
    const english = englishBaseline && typeof englishBaseline === "object" ? englishBaseline[key] : undefined;
    if (!(key in target) || current === null || current === "" || (english !== undefined && JSON.stringify(current) === JSON.stringify(english))) {
      target[key] = value;
      changed = true;
    } else if (value && typeof value === "object" && !Array.isArray(value) && current && typeof current === "object" && !Array.isArray(current)) {
      if (mergeReviewed(current, value, english)) changed = true;
    }
  }
  return changed ? target : null;
}

const NAV_ES = {
  "/": "Inicio", "/about/": "Sobre nosotros", "/Plastic-cap-mold.html": "Moldes de tapones",
  "/Bottle-Cap-Machine/Bottle-Cap-Machine.html": "Máquina", "/samples/": "Muestras", "/news/": "Noticias", "/video/": "Vídeo", "/contact/": "Contacto",
  "/news/Bottle-cap-molds.html": "Noticias sobre moldes de tapas",
};
function navSpanishLabel(url, fallback) {
  if (NAV_ES[url]) return NAV_ES[url];
  const category = (MOULD_CATALOG?.categories || []).find(item => item && String(item.route || "") === String(url || ""));
  return String(category?.navTitleEs || category?.titleEs || fallback || "");
}
function seedPost(item) {
  const title = item.title || {};
  const description = item.description || {};
  const intro = item.intro || {};
  const alt = item.alt || {};
  return {
    schemaVersion: 1, source: "leya-mould-editorial", slug: item.slug, category: item.category,
    date: item.date, updated: isoDate(item.date), title: title.en || "", titleEs: title.es || "",
    description: description.en || "", descriptionEs: description.es || "", summary: description.en || "", summaryEs: description.es || "",
    intro: intro.en || "", introEs: intro.es || "", cover: item.cover || "", image: item.cover || "",
    alt: alt.en || title.en || "LEYA MOULD technical reference", altEs: alt.es || title.es || "Referencia técnica de LEYA MOULD",
    editorial: item
  };
}

const LEGACY_MEDIA_MAP = Object.fromEntries((Array.isArray(LEGACY_MEDIA_MANIFEST?.items) ? LEGACY_MEDIA_MANIFEST.items : [])
  .filter(row => row && row.source && row.target)
  .map(row => [String(row.source), String(row.target)]));
function migrateLegacyMedia(value) {
  let result = String(value || "");
  for (const [source, target] of Object.entries(LEGACY_MEDIA_MAP)) result = result.split(source).join(target);
  return result;
}

const PRODUCT_FIELDS = [
  "slug", "title", "titleEs", "navTitle", "navTitleEs", "description", "descriptionEs",
  "short", "shortEs", "detail", "detailEs", "meta", "metaEs", "route", "checks"
];
function seedProduct(item) {
  const content = { source: "leya-mould-catalog", schemaVersion: 1 };
  for (const field of PRODUCT_FIELDS) {
    if (Object.hasOwn(item || {}, field)) content[field] = item[field];
  }
  const structured = PRODUCT_STRUCTURED?.[String(item?.slug || "")];
  if (structured && typeof structured === "object") {
    content.body = structured.body || item.detail || item.description || "";
    content.sections = Array.isArray(structured.sections) ? structured.sections : [];
    content.faqs = Array.isArray(structured.faqs) ? structured.faqs : [];
    // Category business copy is D1-owned as one structured payload. The
    // renderer keeps only layout/escaping logic; products, advantages,
    // technology, samples, quality, testimonials and videos are editable
    // data rather than a second hidden source in Python.
    if (structured.category && typeof structured.category === "object") {
      content.category = structured.category;
    }
  }
  return content;
}

function seoBaseline(item, locale) {
  // Only seed a locale from its own reviewed fields.  Falling back to English
  // here would create a false multilingual SEO row and violate the D1
  // publishing standard.
  const suffix = locale === "en" ? "" : locale === "es" ? "Es" : null;
  if (suffix === null) return null;
  const title = String(item?.["title" + suffix] || "").trim();
  const description = String(item?.["description" + suffix] || "").trim();
  if (title.length < 2 || description.length < 30) return null;
  const seoTitle = (title + (locale === "es" ? " | LEYA MOULD" : " Manufacturer | LEYA MOULD")).slice(0, 90).trim();
  const metaDescription = description.slice(0, 240).trim();
  if (seoTitle.length < 12 || metaDescription.length < 30) return null;
  return { seoTitle, metaDescription };
}

async function ensureSchema(db) {
  await db.prepare("CREATE TABLE IF NOT EXISTS site_state (key TEXT PRIMARY KEY,value TEXT NOT NULL DEFAULT '',updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)").run();
  await db.prepare("CREATE TABLE IF NOT EXISTS site_navigation (id TEXT PRIMARY KEY,parent_id TEXT,label TEXT NOT NULL,url TEXT NOT NULL,sort_order INTEGER NOT NULL DEFAULT 0,enabled INTEGER NOT NULL DEFAULT 1,new_window INTEGER NOT NULL DEFAULT 0,updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)").run();
  try { await db.prepare("ALTER TABLE site_navigation ADD COLUMN translations_json TEXT NOT NULL DEFAULT '{}'").run(); } catch { /* existing column */ }
  await db.prepare("CREATE TABLE IF NOT EXISTS site_pages (route TEXT PRIMARY KEY,label TEXT NOT NULL,seo_title TEXT NOT NULL DEFAULT '',meta_description TEXT NOT NULL DEFAULT '',robots TEXT NOT NULL DEFAULT 'noindex,nofollow',sitemap_enabled INTEGER NOT NULL DEFAULT 0,updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)").run();
  await db.prepare("CREATE TABLE IF NOT EXISTS xuyi_page_content(route TEXT PRIMARY KEY,main_html TEXT NOT NULL DEFAULT '',publication_status TEXT NOT NULL DEFAULT 'draft' CHECK(publication_status IN ('draft','published')),updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)").run();
  await db.prepare("CREATE TABLE IF NOT EXISTS xuyi_product_content (model TEXT PRIMARY KEY,content_json TEXT NOT NULL DEFAULT '{}',publication_status TEXT NOT NULL DEFAULT 'draft' CHECK(publication_status IN ('draft','published')),updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)").run();
}

export async function onRequestPost(context) {
  if (!(await authorizedMouldContentSeedRequest(context.request, context.env))) return respond({ error: "Unauthorized mould content seed" }, 401);
  const db = context.env.LEYA_DB;
  if (!db) return respond({ error: "LEYA_DB binding missing" }, 503);
  try {
    await ensureSchema(db);
    await ensureBlogSchema(db);
    await ensureProductSeo(db);
    const inserted = { state: 0, navigation: 0, pages: 0, pageBodies: 0, products: 0, productSeo: 0, posts: 0 };
    const updated = { state: 0, navigation: 0, pages: 0, pageBodies: 0, products: 0, productSeo: 0, posts: 0 };
    const skipped = { state: 0, navigation: 0, pages: 0, pageBodies: 0, products: 0, productSeo: 0, posts: 0 };
    const statements = [];
    const stateRows = [
      ["brand_config", BRAND],
      ["contact_config", { schemaVersion: 1, contacts: [{ id: "default-sales", name: "Sales Team", title: "International Sales", email: BRAND.contact.email, phoneDisplay: BRAND.contact.phoneDisplay, phoneE164: BRAND.contact.phoneE164, whatsappUrl: BRAND.contact.whatsappUrl, avatarUrl: "", locales: [], regions: [], sortOrder: 10, enabled: true, isDefault: true }] }],
      ["common_copy", COMMON_COPY],
      ["page_copy", STRUCTURED_PAGE_COPY]
    ];
    const existingStateRows = ((await db.prepare("SELECT key,value FROM site_state WHERE key IN ('brand_config','contact_config','common_copy','page_copy')").all()).results || []);
    const existingState = new Map(existingStateRows.map(row => [String(row.key), row.value]));
    for (const [key, value] of stateRows) {
      if (!existingState.has(key)) {
        statements.push(db.prepare("INSERT INTO site_state(key,value,updated_at) VALUES(?,?,CURRENT_TIMESTAMP)").bind(key, json(value)));
        inserted.state += 1;
        continue;
      }
      // Shared copy and structured page copy gain new baseline fields over
      // time. Merge only missing keys; any owner-edited value remains intact.
      if (key === "common_copy" || key === "page_copy") {
        let current = {};
        try { current = JSON.parse(String(existingState.get(key) || "{}")); } catch { current = {}; }
        const merged = key === "common_copy"
          ? mergeReviewed(current, value, { en: COMMON_COPY.en })
          : mergeMissing(current, value);
        if (merged) {
          statements.push(db.prepare("UPDATE site_state SET value=?,updated_at=CURRENT_TIMESTAMP WHERE key=?").bind(json(merged), key));
          updated.state += 1;
        } else {
          skipped.state += 1;
        }
      } else {
        skipped.state += 1;
      }
    }

    const existingNavRows = ((await db.prepare("SELECT id,label,url,sort_order,translations_json FROM site_navigation").all()).results || []);
    const existingNav = new Map(existingNavRows.map(row => [String(row.id), row]));
    const seedBaselineLabels = new Set([
      "Functional Cap Mould (Combination)", "Plastic Handle Mould",
    ]);
    for (const [id, parentId, label, url, sortOrder] of NAVIGATION) {
      if (!MOULD_ROUTES.has(url)) { skipped.navigation += 1; continue; }
      const current = existingNav.get(id);
      const esLabel = navSpanishLabel(url, label);
      if (!current) {
        statements.push(db.prepare("INSERT INTO site_navigation(id,parent_id,label,url,sort_order,enabled,new_window,translations_json,updated_at) VALUES(?,?,?,?,?,1,0,?,CURRENT_TIMESTAMP)").bind(id, parentId || null, label, url, sortOrder, json(esLabel ? { es: esLabel } : {})));
        inserted.navigation += 1;
      } else if (seedBaselineLabels.has(String(current.label || "")) && String(current.label || "") !== label) {
        // Repair only labels written by the first seed revision; a later owner edit stays authoritative.
        statements.push(db.prepare("UPDATE site_navigation SET label=?,sort_order=?,updated_at=CURRENT_TIMESTAMP WHERE id=?").bind(label, sortOrder, id));
        inserted.navigation += 1;
      } else {
        let translations = {};
        try { translations = JSON.parse(String(current.translations_json || "{}")); } catch { translations = {}; }
        const existingEs = String(translations.es || "").trim();
        if (esLabel && (!existingEs || existingEs === String(current.label || "").trim())) {
          translations.es = esLabel;
          statements.push(db.prepare("UPDATE site_navigation SET translations_json=?,updated_at=CURRENT_TIMESTAMP WHERE id=?").bind(json(translations), id));
          updated.navigation += 1;
        } else {
          skipped.navigation += 1;
        }
      }
    }

    const pageRows = Object.entries(PAGE_COPY).map(([route, [label, title, description]]) => ({ route, label, title, description }));
    for (const [slug, [label, title, description]] of Object.entries(PRODUCT_COPY)) {
      const route = MOULD_PUBLIC_ROUTES.get(slug);
      if (route) pageRows.push({ route, label, title, description });
    }
    const existingPages = new Set(((await db.prepare("SELECT route FROM site_pages").all()).results || []).map(row => String(row.route)));
    for (const page of pageRows) {
      if (!MOULD_ROUTES.has(page.route) || existingPages.has(page.route)) { skipped.pages += 1; continue; }
      statements.push(db.prepare("INSERT INTO site_pages(route,label,seo_title,meta_description,robots,sitemap_enabled,updated_at) VALUES(?,?,?,?, 'index,follow',1,CURRENT_TIMESTAMP)").bind(page.route, page.label, page.title, page.description));
      inserted.pages += 1;
    }

    // Migrate only missing English page bodies. The source renderer remains
    // the fallback for Spanish until a reviewed page translation is present;
    // existing D1 owner edits are never overwritten.
    const bodyRows = Array.isArray(PAGE_BODY_DATA?.items) ? PAGE_BODY_DATA.items : [];
    const existingBodies = new Map(((await db.prepare("SELECT route,main_html FROM xuyi_page_content").all()).results || []).map(row => [String(row.route), String(row.main_html || "")]));
    for (const row of bodyRows) {
      const route = String(row?.route || "");
      const mainHtml = String(row?.mainHtml || "");
      if (!MOULD_ROUTES.has(route) || !mainHtml) { skipped.pageBodies += 1; continue; }
      if (!existingBodies.has(route)) {
        statements.push(db.prepare("INSERT INTO xuyi_page_content(route,main_html,publication_status,updated_at) VALUES(?,?, 'published', CURRENT_TIMESTAMP)").bind(route, migrateLegacyMedia(mainHtml)));
        inserted.pageBodies += 1;
        continue;
      }
      const current = existingBodies.get(route) || "";
      const migrated = migrateLegacyMedia(current);
      if (migrated !== current) {
        statements.push(db.prepare("UPDATE xuyi_page_content SET main_html=?,updated_at=CURRENT_TIMESTAMP WHERE route=?").bind(migrated, route));
        updated.pageBodies += 1;
      } else skipped.pageBodies += 1;
    }

    const existingProductRows = ((await db.prepare("SELECT model,content_json FROM xuyi_product_content").all()).results || []);
    const existingProducts = new Map(existingProductRows.map(row => [String(row.model), row.content_json]));
    const publicLocaleCodes = publicLanguages(await loadLanguageConfig(db)).map(language => String(language.code).toLowerCase());
    const existingSeoRows = ((await db.prepare("SELECT slug,locale FROM xuyi_product_seo").all()).results || []);
    const existingSeo = new Set(existingSeoRows.map(row => String(row.slug).toLowerCase() + "\u0000" + String(row.locale).toLowerCase()));
    const products = Array.isArray(MOULD_CATALOG?.categories) ? MOULD_CATALOG.categories : [];
    for (const item of products) {
      const model = String(item?.slug || "");
      if (!MOULD_PUBLIC_ROUTES.has(model)) { skipped.products += 1; continue; }
      const baseline = seedProduct(item);
      if (!existingProducts.has(model)) {
        statements.push(db.prepare("INSERT INTO xuyi_product_content(model,content_json,publication_status,updated_at) VALUES(?,?, 'published', CURRENT_TIMESTAMP)").bind(model, json(baseline)));
        inserted.products += 1;
        continue;
      }
      let current = {};
      try { current = JSON.parse(String(existingProducts.get(model) || "{}")); } catch { current = {}; }
      // Backfill only fields that were absent when the first migration ran.
      // This includes localized product copy/SEO; any owner-edited value stays
      // authoritative and is never replaced by the reviewed baseline.
      const merged = mergeMissing(current, baseline);
      if (merged) {
        statements.push(db.prepare("UPDATE xuyi_product_content SET content_json=?,updated_at=CURRENT_TIMESTAMP WHERE model=?").bind(json(merged), model));
        updated.products += 1;
      } else {
        skipped.products += 1;
      }
      for (const locale of publicLocaleCodes) {
        const seo = seoBaseline(item, locale);
        const key = model.toLowerCase() + "\u0000" + locale;
        if (!seo || existingSeo.has(key)) {
          skipped.productSeo += 1;
          continue;
        }
        statements.push(db.prepare("INSERT OR IGNORE INTO xuyi_product_seo(slug,locale,seo_title,meta_description,updated_at) VALUES(?,?,?,?,CURRENT_TIMESTAMP)")
          .bind(model.toLowerCase(), locale, seo.seoTitle, seo.metaDescription));
        existingSeo.add(key);
        inserted.productSeo += 1;
      }
    }

    const existingPosts = new Set(((await db.prepare("SELECT slug FROM xuyi_blog_posts").all()).results || []).map(row => String(row.slug)));
    const posts = Array.isArray(EDITORIAL_DATA?.items) ? EDITORIAL_DATA.items : [];
    for (const item of posts) {
      const slug = String(item?.slug || "");
      if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug) || existingPosts.has(slug)) { skipped.posts += 1; continue; }
      const post = seedPost(item);
      statements.push(db.prepare("INSERT INTO xuyi_blog_posts(slug,status,content_json,published_at) VALUES(?,'published',?,?)").bind(slug, json(post), isoDate(item.date) + "T12:00:00.000Z"));
      inserted.posts += 1;
    }
    if (statements.length) await db.batch(statements);
    const changed = Object.values(inserted).reduce((sum, value) => sum + value, 0) + Object.values(updated).reduce((sum, value) => sum + value, 0);
    const revision = changed ? await bumpPublishRevision(db) : { revision: 0, requestedAt: "" };
    return respond({ success: true, inserted, updated, skipped, totalNews: posts.length, totalProducts: products.length, pageBodyRoutes: bodyRows.length, structuredPageCopy: Object.keys(STRUCTURED_PAGE_COPY.en).length, sharedCtaVariants: Object.keys(COMMON_COPY.en.shared_cta).length, publishRevision: revision.revision, requestedAt: revision.requestedAt, ownerEditsPreserved: true, productImagesRemainTemplateBound: true });
  } catch (error) {
    return respond({ error: "D1 mould content seed failed: " + String(error?.message || error).slice(0, 240) }, 500);
  }
}


