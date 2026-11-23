"""Source renderer for the LEYA MOULD product site.

The water-cup project supplied the backend contracts, admin routes and Pages
Functions.  This module deliberately owns only the new mould site's public
source pages.  It never reads or writes the water-cup repository or its data.
"""
from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path

from locale_registry import approved_locales

ROOT = Path(__file__).resolve().parent
# The supplied logo is kept as a source asset so the published header can scale it without stretching.
CONFIG = json.loads((ROOT / "deployment/site.config.json").read_text(encoding="utf-8"))
ORIGIN = CONFIG["site"]["origin"]
INDEXING_APPROVED = CONFIG["site"].get("indexingApproved") is True
OUTPUT = ROOT / (os.environ.get("LEYA_OUTPUT_DIR") or ".")
CATALOG = json.loads((ROOT / "data/mould-catalog.json").read_text(encoding="utf-8"))
ADDRESS = "4-55,Xicheng New Village,Huangyan Taizhou,Zhejiang Province, China"
EMAIL = "amyhu@leyamould.com"
WHATSAPP = "+8613606727715"
WA_URL = "https://wa.me/8613606727715"
CATEGORY_LABELS = {
    "es": {"pet-preform-moulds": "Moldes de preformas PET", "bottle-cap-moulds": "Moldes de tapones", "bottle-moulds": "Moldes de botellas", "knife-fork-moulds": "Moldes de cuchillos y tenedores"},
    "pt": {"pet-preform-moulds": "Moldes de pré-formas PET", "bottle-cap-moulds": "Moldes de tampas", "bottle-moulds": "Moldes de garrafas", "knife-fork-moulds": "Moldes de facas e garfos"},
    "ru": {"pet-preform-moulds": "Пресс-формы для ПЭТ-преформ", "bottle-cap-moulds": "Пресс-формы для крышек", "bottle-moulds": "Пресс-формы для бутылок", "knife-fork-moulds": "Пресс-формы для ножей и вилок"},
    "tr": {"pet-preform-moulds": "PET Preform Kalıpları", "bottle-cap-moulds": "Şişe Kapak Kalıpları", "bottle-moulds": "Şişe Kalıpları", "knife-fork-moulds": "Bıçak ve Çatal Kalıpları"},
}

SNAPSHOT = ROOT / "_local_ops/build-snapshot.json"
STATE = {}
if SNAPSHOT.is_file():
    candidate = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    if candidate.get("site") == "leyamould":
        STATE = candidate

LOCALES = approved_locales(STATE, require_resources=False)
if not LOCALES:
    LOCALES = [{"code": "en", "pathPrefix": "", "nativeName": "English", "sortOrder": 10}]

TEXT = {
    "en": {
        "home": "Home", "about": "About us", "products": "Products", "capabilities": "Capabilities",
        "process": "How We Work", "news": "News", "samples": "Samples", "video": "Video", "cap_mould": "Cap Mould", "machine": "Machine", "contact_us": "Contact Us", "contact": "Contact", "quote": "Request a Quote",
        "hero_eyebrow": "PRECISION MOULDING · ENGINEERING · SUPPORT",
        "hero_title": "Your Trusted Plastic Cap Mould Manufacturer",
        "hero_text": "15+ years of precision moulding experience for global packaging projects, with clear engineering review from design through trial and handover.",
        "hero_primary": "Explore Mould Categories →", "hero_secondary": "Tell Us About Your Project",
        "hero_note": "LEYA MOULD · Huangyan, Taizhou, Zhejiang, China",
        "categories_eyebrow": "MOULD CATEGORIES", "categories_title": "Tooling directions for packaging and product makers.",
        "categories_text": "Start with a product family. We will confirm the drawing, material, cavity plan, machine interface and evidence required for a responsible quotation.",
        "why_eyebrow": "WHY LEYA MOULD", "why_title": "A practical engineering conversation before steel is cut.",
        "why_text": "A mould project is easier to control when the product drawing, resin, machine, quality points and sample plan are discussed together. LEYA MOULD keeps the workflow clear and project-specific.",
        "advantages": [("Design review", "Part geometry, parting line, cooling and ejection are checked against the intended process."), ("Project matching", "The tooling brief records the mould family, material, machine interface and target output information supplied by the buyer."), ("Sample-led decisions", "Trial parts and agreed inspection points guide optimisation before production handover."), ("Clear communication", "Drawings, PDFs, photos and revision notes stay attached to the enquiry." )],
        "process_eyebrow": "HOW WE WORK", "process_title": "From drawing to a controlled tooling handover.",
        "process_steps": [("01", "Share Design", "Send your drawing or sample for an initial technical review."), ("02", "DFM Analysis", "Review mould flow, parting, cooling and optimisation opportunities."), ("03", "Manufacturing", "Coordinate precision machining, EDM, fitting and heat treatment."), ("04", "Trial & Inspection", "Complete trial runs, dimensional checks and agreed inspection evidence."), ("05", "Delivery & Support", "Keep approved files, delivery notes and technical support connected.")],
        "technical_eyebrow": "TECHNICAL CONTENT", "technical_title": "Built around evidence, not generic promises.",
        "technical_text": "Product drawings, high-resolution images and PDFs will be added to the relevant category as they are approved. Until then, category pages clearly show which information is still to be confirmed.",
        "technical_cta": "Send a Drawing or PDF →", "resources_title": "Mould project resources", "resources_text": "Share the part drawing, target resin, expected cavities, machine model, sample or PDF. We will return with the questions needed for a useful quotation.",
        "footer_tagline": "Bottle, cap, preform and custom product mould support for international buyers.", "footer_products": "Products", "footer_capabilities": "Capabilities", "footer_contact": "Contact Us", "footer_design": "Mould Design & Engineering", "footer_manufacturing": "Precision Manufacturing", "footer_quality": "Quality & Inspection", "footer_support": "Trial & Technical Support", "footer_quote": "Request a Quote →", "footer_faq": "FAQs", "footer_privacy": "Privacy Policy", "footer_sticky": "Mould Project Enquiries", "footer_cta_title": "Ready to discuss your mould project?", "footer_cta_text": "Send your drawing, sample or PDF and tell us the production target.", "footer_eyebrow": "LEYA MOULD · ENGINEERING · MANUFACTURING", "form_required": "Company name, work email and project requirements are required. Technical drawings, samples and documents can be attached later by email or WhatsApp.", "form_company": "Company Name", "form_email": "Work Email", "form_category": "Mould Category", "form_quantity": "Estimated Quantity", "form_country": "Destination Country", "form_type": "Inquiry Type", "form_quote": "Request a Quote", "form_new": "New Mould Design", "form_review": "Existing Mould Review", "form_tech": "Technical Consultation", "form_material": "Target Material", "form_advise": "Please advise", "form_other": "Other / to be confirmed", "form_requirements": "Your Requirements", "form_consent": "I agree to the", "form_privacy": "privacy policy", "form_submit": "Send Project Enquiry →", "form_aria": "Mould project enquiry form", "back": "Back to Home →", "learn": "Learn More →", "view": "View Category →", "category_note": "Technical specifications, images and PDF references are added after project review.", "contact_title": "Tell us about your mould project.", "contact_intro": "Send the part drawing, sample, target material, cavity plan, machine information and delivery market. We will reply with the next technical questions.", "faq_title": "Mould project questions", "faq_intro": "A short starting point for buyers preparing a tooling enquiry.", "about_title": "About LEYA MOULD", "about_text": "LEYA MOULD Co.,Ltd is a mould-project brand based in Huangyan, Taizhou, Zhejiang Province, China. The site is being prepared around an evidence-led catalogue for packaging and product tooling.", "privacy_title": "Privacy & enquiry data", "privacy_text": "We use the information you submit to respond to mould project enquiries, technical questions and quotation requests. Contact amyhu@leyamould.com for data questions.", "blog_title": "Mould project resources", "blog_text": "Technical articles and approved project resources will be added as the mould catalogue is reviewed.",
    },
    "es": {}, "pt": {}, "ru": {}, "tr": {}
}
TEXT["es"] = {**TEXT["en"], "home":"Inicio", "about":"Sobre nosotros", "products":"Productos", "capabilities":"Capacidades", "process":"Cómo trabajamos", "news":"Recursos", "contact":"Contacto", "quote":"Solicitar cotización", "hero_eyebrow":"MOLDES DE PRECISIÓN · INGENIERÍA · SOPORTE", "hero_title":"Moldes preparados para su próxima producción.", "hero_text":"LEYA MOULD acompaña proyectos de moldes para preformas, tapones, botellas y cubiertos desde la revisión del diseño hasta las pruebas.", "hero_primary":"Explorar categorías →", "hero_secondary":"Cuéntenos su proyecto", "categories_eyebrow":"CATEGORÍAS DE MOLDES", "categories_title":"Direcciones de utillaje para fabricantes de envases y productos.", "categories_text":"Comience con una familia de productos. Confirmaremos el plano, material, cavidades, máquina y evidencias necesarias.", "why_eyebrow":"POR QUÉ LEYA MOULD", "why_title":"Una conversación técnica antes de fabricar el acero.", "why_text":"Un proyecto de moldes se controla mejor cuando se revisan juntos el plano, la resina, la máquina, los puntos de calidad y el plan de muestras.", "technical_eyebrow":"CONTENIDO TÉCNICO", "technical_title":"Basado en evidencias, no en promesas genéricas.", "technical_text":"Las imágenes de alta resolución y los PDF aprobados se añadirán a cada categoría cuando estén disponibles.", "technical_cta":"Enviar plano o PDF →", "resources_title":"Recursos del proyecto", "resources_text":"Comparta el plano, resina, cavidades, máquina, muestra o PDF. Responderemos con las preguntas necesarias.", "footer_tagline":"Soporte para moldes de botellas, tapones, preformas y productos a medida.", "footer_products":"Productos", "footer_capabilities":"Capacidades", "footer_contact":"Contacto", "footer_design":"Diseño e ingeniería", "footer_manufacturing":"Fabricación de precisión", "footer_quality":"Calidad e inspección", "footer_support":"Pruebas y soporte técnico", "footer_quote":"Solicitar cotización →", "footer_faq":"Preguntas frecuentes", "footer_privacy":"Privacidad", "footer_sticky":"Consultas de moldes", "footer_cta_title":"¿Hablamos de su proyecto?", "footer_cta_text":"Envíe su plano, muestra o PDF y el objetivo de producción.", "footer_eyebrow":"LEYA MOULD · INGENIERÍA · FABRICACIÓN", "contact_title":"Cuéntenos su proyecto de moldes.", "contact_intro":"Envíe el plano, muestra, material, cavidades, máquina y mercado de destino.", "faq_title":"Preguntas sobre moldes", "faq_intro":"Puntos iniciales para preparar una consulta técnica.", "about_title":"Sobre LEYA MOULD", "about_text":"LEYA MOULD Co.,Ltd es una marca de proyectos de moldes con sede en Huangyan, Taizhou, Zhejiang, China.", "privacy_title":"Privacidad y consultas", "privacy_text":"Usamos los datos enviados para responder consultas técnicas y solicitudes de cotización. Contacte con amyhu@leyamould.com.", "blog_title":"Recursos de moldes", "blog_text":"Los artículos técnicos y recursos aprobados se añadirán al revisar el catálogo."}
TEXT["pt"] = {**TEXT["en"], "home":"Início", "about":"Sobre nós", "products":"Produtos", "capabilities":"Capacidades", "process":"Como trabalhamos", "news":"Recursos", "contact":"Contato", "quote":"Solicitar cotação", "hero_eyebrow":"MOLDES DE PRECISÃO · ENGENHARIA · SUPORTE", "hero_title":"Moldes preparados para a sua próxima produção.", "hero_text":"A LEYA MOULD apoia projetos de moldes para pré-formas, tampas, garrafas e talheres desde a revisão do desenho até os testes.", "hero_primary":"Explorar categorias →", "hero_secondary":"Fale sobre o seu projeto", "categories_eyebrow":"CATEGORIAS DE MOLDES", "categories_title":"Soluções de ferramentaria para fabricantes de embalagens e produtos.", "categories_text":"Comece por uma família de produtos. Confirmaremos desenho, material, cavidades, máquina e evidências necessárias.", "why_eyebrow":"POR QUE LEYA MOULD", "why_title":"Uma conversa de engenharia antes de cortar o aço.", "why_text":"Um projeto de moldes é mais controlável quando desenho, resina, máquina, qualidade e amostras são analisados juntos.", "technical_eyebrow":"CONTEÚDO TÉCNICO", "technical_title":"Construído com evidências, não promessas genéricas.", "technical_text":"Imagens em alta resolução e PDFs aprovados serão adicionados a cada categoria quando disponíveis.", "technical_cta":"Enviar desenho ou PDF →", "resources_title":"Recursos do projeto", "resources_text":"Envie desenho, resina, cavidades, máquina, amostra ou PDF. Retornaremos com as perguntas técnicas necessárias.", "footer_tagline":"Suporte para moldes de garrafas, tampas, pré-formas e produtos personalizados.", "footer_products":"Produtos", "footer_capabilities":"Capacidades", "footer_contact":"Contato", "footer_design":"Projeto e engenharia", "footer_manufacturing":"Fabricação de precisão", "footer_quality":"Qualidade e inspeção", "footer_support":"Testes e suporte técnico", "footer_quote":"Solicitar cotação →", "footer_faq":"Perguntas frequentes", "footer_privacy":"Privacidade", "footer_sticky":"Consultas de moldes", "footer_cta_title":"Vamos conversar sobre o seu projeto?", "footer_cta_text":"Envie desenho, amostra ou PDF e a meta de produção.", "footer_eyebrow":"LEYA MOULD · ENGENHARIA · FABRICAÇÃO", "contact_title":"Fale sobre o seu projeto de moldes.", "contact_intro":"Envie desenho, amostra, material, cavidades, máquina e mercado de destino.", "faq_title":"Perguntas sobre moldes", "faq_intro":"Pontos iniciais para preparar uma consulta técnica.", "about_title":"Sobre a LEYA MOULD", "about_text":"A LEYA MOULD Co.,Ltd é uma marca de projetos de moldes sediada em Huangyan, Taizhou, Zhejiang, China.", "privacy_title":"Privacidade e consultas", "privacy_text":"Usamos os dados enviados para responder consultas técnicas e pedidos de cotação. Contacte amyhu@leyamould.com.", "blog_title":"Recursos de moldes", "blog_text":"Artigos técnicos e recursos aprovados serão adicionados após a revisão do catálogo."}
TEXT["ru"] = {**TEXT["en"], "home":"Главная", "about":"О компании", "products":"Продукция", "capabilities":"Возможности", "process":"Как мы работаем", "news":"Ресурсы", "contact":"Контакты", "quote":"Запросить расчёт", "hero_eyebrow":"ПРЕЦИЗИОННЫЕ ПРЕСС-ФОРМЫ · ИНЖИНИРИНГ · ПОДДЕРЖКА", "hero_title":"Пресс-формы для вашего следующего производства.", "hero_text":"LEYA MOULD сопровождает проекты пресс-форм для преформ, крышек, бутылок и столовых приборов от проверки чертежа до испытаний.", "hero_primary":"Категории пресс-форм →", "hero_secondary":"Обсудить проект", "categories_eyebrow":"КАТЕГОРИИ ПРЕСС-ФОРМ", "categories_title":"Оснастка для производителей упаковки и изделий.", "categories_text":"Выберите семейство изделий. Мы уточним чертёж, материал, число гнёзд, машину и необходимые подтверждения.", "why_eyebrow":"ПОЧЕМУ LEYA MOULD", "why_title":"Практический инженерный диалог до изготовления стали.", "why_text":"Проект проще контролировать, когда чертёж, полимер, машина, контроль качества и образцы рассматриваются вместе.", "technical_eyebrow":"ТЕХНИЧЕСКИЕ МАТЕРИАЛЫ", "technical_title":"Опора на подтверждённые данные, а не общие обещания.", "technical_text":"Одобренные изображения высокого разрешения и PDF будут добавлены к категориям после проверки.", "technical_cta":"Отправить чертёж или PDF →", "resources_title":"Материалы проекта", "resources_text":"Отправьте чертёж, полимер, число гнёзд, данные машины, образец или PDF. Мы вернёмся с необходимыми вопросами.", "footer_tagline":"Пресс-формы для бутылок, крышек, преформ и изделий по индивидуальному проекту.", "footer_products":"Продукция", "footer_capabilities":"Возможности", "footer_contact":"Контакты", "footer_design":"Проектирование и инжиниринг", "footer_manufacturing":"Прецизионное производство", "footer_quality":"Качество и контроль", "footer_support":"Испытания и техническая поддержка", "footer_quote":"Запросить расчёт →", "footer_faq":"Вопросы", "footer_privacy":"Конфиденциальность", "footer_sticky":"Запрос по пресс-форме", "footer_cta_title":"Обсудим ваш проект пресс-формы?", "footer_cta_text":"Отправьте чертёж, образец или PDF и цель производства.", "footer_eyebrow":"LEYA MOULD · ИНЖИНИРИНГ · ПРОИЗВОДСТВО", "contact_title":"Расскажите о проекте пресс-формы.", "contact_intro":"Отправьте чертёж, образец, материал, число гнёзд, данные машины и рынок.", "faq_title":"Вопросы о пресс-формах", "faq_intro":"Краткая основа для подготовки технического запроса.", "about_title":"О компании LEYA MOULD", "about_text":"LEYA MOULD Co.,Ltd — бренд проектов пресс-форм из Хуанъяня, Тайчжоу, провинция Чжэцзян, Китай.", "privacy_title":"Конфиденциальность и запросы", "privacy_text":"Мы используем отправленные данные для ответа на технические запросы и расчёты. Свяжитесь с amyhu@leyamould.com.", "blog_title":"Ресурсы по пресс-формам", "blog_text":"Технические статьи и одобренные материалы будут добавлены после проверки каталога."}
TEXT["tr"] = {**TEXT["en"], "home":"Ana Sayfa", "about":"Hakkımızda", "products":"Ürünler", "capabilities":"Yetenekler", "process":"Nasıl Çalışıyoruz", "news":"Kaynaklar", "contact":"İletişim", "quote":"Teklif İste", "hero_eyebrow":"HASSAS KALIPLAMA · MÜHENDİSLİK · DESTEK", "hero_title":"Bir sonraki üretiminiz için kalıplar.", "hero_text":"LEYA MOULD; preform, kapak, şişe ve çatal-bıçak kalıp projelerine tasarım incelemesinden denemeye kadar destek verir.", "hero_primary":"Kalıp Kategorilerini Gör →", "hero_secondary":"Projenizi Anlatın", "categories_eyebrow":"KALIP KATEGORİLERİ", "categories_title":"Ambalaj ve ürün üreticileri için kalıp yönleri.", "categories_text":"Bir ürün ailesi seçin. Çizim, malzeme, göz sayısı, makine ve gerekli kanıtları birlikte netleştirelim.", "why_eyebrow":"NEDEN LEYA MOULD", "why_title":"Çelik işlenmeden önce pratik mühendislik görüşmesi.", "why_text":"Çizim, reçine, makine, kalite noktaları ve numune planı birlikte incelendiğinde proje daha iyi kontrol edilir.", "technical_eyebrow":"TEKNİK İÇERİK", "technical_title":"Genel vaatler yerine kanıta dayalı çalışma.", "technical_text":"Onaylanan yüksek çözünürlüklü görseller ve PDF'ler inceleme sonrasında ilgili kategoriye eklenir.", "technical_cta":"Çizim veya PDF Gönder →", "resources_title":"Proje kaynakları", "resources_text":"Çizim, reçine, göz sayısı, makine, numune veya PDF gönderin. Gerekli teknik sorularla geri dönelim.", "footer_tagline":"Şişe, kapak, preform ve özel ürün kalıpları için uluslararası proje desteği.", "footer_products":"Ürünler", "footer_capabilities":"Yetenekler", "footer_contact":"İletişim", "footer_design":"Kalıp tasarımı ve mühendislik", "footer_manufacturing":"Hassas üretim", "footer_quality":"Kalite ve kontrol", "footer_support":"Deneme ve teknik destek", "footer_quote":"Teklif İste →", "footer_faq":"SSS", "footer_privacy":"Gizlilik", "footer_sticky":"Kalıp proje talepleri", "footer_cta_title":"Kalıp projenizi görüşelim mi?", "footer_cta_text":"Çiziminizi, numunenizi veya PDF'inizi ve üretim hedefinizi gönderin.", "footer_eyebrow":"LEYA MOULD · MÜHENDİSLİK · ÜRETİM", "contact_title":"Kalıp projenizi anlatın.", "contact_intro":"Parça çizimini, numuneyi, malzemeyi, göz sayısını, makineyi ve hedef pazarı gönderin.", "faq_title":"Kalıp projesi soruları", "faq_intro":"Teknik bir talep hazırlayan alıcılar için kısa başlangıç bilgileri.", "about_title":"LEYA MOULD Hakkında", "about_text":"LEYA MOULD Co.,Ltd, Huangyan, Taizhou, Zhejiang, Çin merkezli bir kalıp proje markasıdır.", "privacy_title":"Gizlilik ve talepler", "privacy_text":"Gönderdiğiniz bilgileri teknik sorulara ve teklif taleplerine yanıt vermek için kullanırız. amyhu@leyamould.com adresinden ulaşabilirsiniz.", "blog_title":"Kalıp proje kaynakları", "blog_text":"Teknik makaleler ve onaylı proje kaynakları katalog incelendikçe eklenecektir."}

TEXT["es"].update({"samples": "Muestras", "video": "Vídeo"})
TEXT["pt"].update({"samples": "Amostras", "video": "Vídeo"})
TEXT["ru"].update({"samples": "Образцы", "video": "Видео"})
TEXT["tr"].update({"samples": "Numuneler", "video": "Video"})
TEXT["es"].update({"cap_mould": "Moldes de tapones", "machine": "Máquina", "contact_us": "Contacto"})

def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)

def text(locale: str, key: str) -> str:
    return str(TEXT.get(locale, TEXT["en"]).get(key, TEXT["en"].get(key, key)))

def data(locale: str, key: str):
    return TEXT.get(locale, TEXT["en"]).get(key, TEXT["en"].get(key, []))

def category_title(locale: str, category: dict) -> str:
    return CATEGORY_LABELS.get(locale, {}).get(category["slug"], category["title"])

def route_for(locale: str, route: str) -> str:
    prefix = next((row["pathPrefix"] for row in LOCALES if row["code"] == locale), "")
    return route if not prefix else "/" + prefix + route

def local_link(locale: str, route: str) -> str:
    return route_for(locale, route)

def localized_href(locale: str, route: str) -> str:
    return local_link(locale, route)

def image(path: str, alt: str, loading: str = "lazy") -> str:
    return '<img src="' + esc(path) + '" alt="' + esc(alt) + '" loading="' + loading + '" decoding="async">'

def render_template(name: str, **values: str) -> str:
    content = (ROOT / "templates/site" / (name + ".html")).read_text(encoding="utf-8").rstrip("\n")
    for key, value in values.items():
        content = content.replace("{{" + key + "}}", str(value))
    if "{{" in content:
        raise ValueError("Unfilled mould template placeholder: " + name)
    return content

def header(locale: str, route: str) -> str:
    cats = CATALOG["categories"]
    nav = ['<a class="nav__link" href="' + local_link(locale, "/") + '">' + esc(text(locale, "home")) + '</a>']
    product_links = ''.join('<a href="' + localized_href(locale, "/collections/" + c["slug"] + "/") + '">' + esc(category_title(locale, c)) + '</a>' for c in cats)
    product_menu = '<div class="nav__drop"><button class="nav__toggle" data-mega-toggle type="button" aria-controls="menu-products" aria-expanded="false">' + esc(text(locale, "cap_mould")) + '<svg class="chevron" viewBox="0 0 24 24" aria-hidden="true"><path d="m5 9 7 7 7-7"/></svg></button><div class="mini-menu" id="menu-products"><a href="' + localized_href(locale, "/products/") + '"><strong>' + esc(text(locale, "products")) + '</strong></a>' + product_links + '</div></div>'
    about_menu = '<div class="nav__drop"><button class="nav__toggle" data-mega-toggle type="button" aria-controls="menu-about" aria-expanded="false">' + esc(text(locale, "about")) + '<svg class="chevron" viewBox="0 0 24 24" aria-hidden="true"><path d="m5 9 7 7 7-7"/></svg></button><div class="mini-menu" id="menu-about"><a href="' + localized_href(locale, "/about/") + '">' + esc(text(locale, "about")) + '</a><a href="' + localized_href(locale, "/capabilities/") + '">' + esc(text(locale, "capabilities")) + '</a><a href="' + localized_href(locale, "/manufacturing/") + '">' + esc(text(locale, "process")) + '</a><a href="' + localized_href(locale, "/quality-control/") + '">' + esc(text(locale, "footer_quality")) + '</a></div></div>'
    nav.append(about_menu)
    nav.append(product_menu)
    nav.append('<a class="nav__link" href="' + localized_href(locale, "/capabilities/") + '">' + esc(text(locale, "machine")) + '</a>')
    nav.append('<a class="nav__link" href="' + localized_href(locale, "/samples/") + '">' + esc(text(locale, "samples")) + '</a>')
    resources_menu = '<div class="nav__drop"><button class="nav__toggle" data-mega-toggle type="button" aria-controls="menu-resources" aria-expanded="false">' + esc(text(locale, "news")) + '<svg class="chevron" viewBox="0 0 24 24" aria-hidden="true"><path d="m5 9 7 7 7-7"/></svg></button><div class="mini-menu" id="menu-resources"><a href="' + localized_href(locale, "/news/") + '">' + esc(text(locale, "news")) + '</a><a href="' + localized_href(locale, "/faq/") + '">' + esc(text(locale, "faq_title")) + '</a></div></div>'
    nav.append(resources_menu)
    nav.append('<a class="nav__link" href="' + localized_href(locale, "/video/") + '">' + esc(text(locale, "video")) + '</a>')
    nav.append('<a class="nav__link" href="' + localized_href(locale, "/contact/") + '">' + esc(text(locale, "contact_us")) + '</a>')
    mobile = '<a href="' + local_link(locale, "/") + '">' + esc(text(locale, "home")) + '</a><a href="' + localized_href(locale, "/about/") + '">' + esc(text(locale, "about")) + '</a><a href="' + localized_href(locale, "/capabilities/") + '">' + esc(text(locale, "machine")) + '</a><a href="' + localized_href(locale, "/samples/") + '">' + esc(text(locale, "samples")) + '</a><a href="' + localized_href(locale, "/video/") + '">' + esc(text(locale, "video")) + '</a><a href="' + localized_href(locale, "/contact/") + '">' + esc(text(locale, "contact_us")) + '</a>'
    mobile += '<details><summary>' + esc(text(locale, "cap_mould")) + '</summary><a href="' + localized_href(locale, "/products/") + '">' + esc(text(locale, "products")) + '</a>' + product_links + '</details><details><summary>' + esc(text(locale, "news")) + '</summary><a href="' + localized_href(locale, "/news/") + '">' + esc(text(locale, "news")) + '</a><a href="' + localized_href(locale, "/faq/") + '">' + esc(text(locale, "faq_title")) + '</a></details>'
    options = ''.join('<option value="' + esc(lang["code"]) + '">' + esc(lang["nativeName"]) + '</option>' for lang in LOCALES)
    logo = '<a href="' + local_link(locale, "/") + '" class="logo" aria-label="LEYA MOULD home"><img class="logo__image" src="/assets/leyamould-logo.svg?v=logo1" alt="LEYA MOULD" width="260" height="51" decoding="async"></a>'
    actions = '<div class="header__actions"><a class="nav-phone-desktop" href="tel:+8613606727715">+86 136 0672 7715</a><select class="language-switch" data-language-switch aria-label="Choose language">' + options + '</select><button class="icon-button" id="search-toggle" aria-label="Search products" aria-expanded="false" type="button"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m16 16 5 5"/></svg></button><a class="button header__quote" href="' + localized_href(locale, "/contact/#inquiry") + '">' + esc(text(locale, "quote")) + '</a><button class="icon-button menu-button" id="mobile-menu" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-navigation"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg><span class="menu-label">Menu</span></button></div>'
    search = '<div id="search-panel" class="search-panel"><form class="shell search-panel__form" action="' + localized_href(locale, "/products/") + '" method="get"><input type="search" name="q" placeholder="Search mould category or application…" aria-label="Search mould category or application"><button class="button" type="submit">Search →</button></form></div>'
    top = '<div class="topbar top-bar"><div class="shell topbar__inner top-bar-inner"><div class="top-bar-left"><a href="mailto:' + EMAIL + '">✉ ' + EMAIL + '</a><a href="tel:+8613606727715">☎ +86 136 0672 7715</a><span>⌖ ' + esc(ADDRESS) + '</span></div><div class="top-bar-right"><a href="' + WA_URL + '" target="_blank" rel="noopener noreferrer">WhatsApp +8613606727715</a><a href="/video/">Video</a><a href="/contact/">Contact</a></div></div></div>'
    return render_template("header", TOPBAR=top, LOGO=logo, NAV_DESKTOP=''.join(nav), ACTIONS=actions, SEARCH=search, NAV_MOBILE=mobile)

def footer(locale: str) -> str:
    cap_links = [("Water / Beverage Cap Mould", "pet-preform-moulds"), ("Edible Oil Cap Mould", "bottle-cap-moulds"), ("Engine Oil Cap Mould", "bottle-cap-moulds"), ("Food Packaging Cap Mould", "bottle-cap-moulds"), ("Medical Cap Mould", "bottle-cap-moulds"), ("Cosmetic Flip-Top Cap Mould", "bottle-cap-moulds"), ("Personal Care Cap Mould", "bottle-cap-moulds"), ("Functional Cap Mould", "bottle-cap-moulds"), ("Handle Mould", "bottle-moulds")]
    links = ''.join('<p><a href="' + localized_href(locale, "/collections/" + slug + "/") + '">' + esc(title) + '</a></p>' for title, slug in cap_links)
    quick = ''.join('<p><a href="' + localized_href(locale, route) + '">' + esc(label) + '</a></p>' for label, route in ((text(locale, "about"), "/about/"), (text(locale, "samples"), "/samples/"), (text(locale, "video"), "/video/"), (text(locale, "news"), "/news/"), (text(locale, "faq_title"), "/faq/"), (text(locale, "contact_us"), "/contact/")))
    vals = {"PRODUCT_LINKS": links, "QUICK_LINKS": quick, "WHATSAPP_NUMBER": esc(WHATSAPP), "FOOTER_EYEBROW": esc(text(locale, "footer_eyebrow")), "FOOTER_CTA_TITLE": esc(text(locale, "footer_cta_title")), "FOOTER_CTA_TEXT": esc(text(locale, "footer_cta_text")), "FOOTER_CTA_BUTTON": esc(text(locale, "quote")), "FOOTER_TAGLINE": esc(text(locale, "footer_tagline")), "FOOTER_ADDRESS": esc(ADDRESS), "FOOTER_PRODUCTS_TITLE": esc(text(locale, "footer_products")), "FOOTER_CONTACT_TITLE": esc(text(locale, "footer_contact")), "FOOTER_QUOTE": esc(text(locale, "footer_quote")), "FOOTER_PRIVACY": esc(text(locale, "footer_privacy")), "FOOTER_STICKY": esc(text(locale, "footer_sticky"))}
    return render_template("footer", **vals)

def head(locale: str, title: str, description: str, route: str) -> str:
    robots = "index,follow" if INDEXING_APPROVED else "noindex,nofollow"
    canonical = ORIGIN + route_for(locale, route)
    alternates = ''.join('<link rel="alternate" hreflang="' + esc(lang["code"]) + '" href="' + esc(ORIGIN + route_for(lang["code"], route)) + '">' for lang in LOCALES)
    base = render_template("head", TITLE=esc(title), DESCRIPTION=esc(description)[:240], ASSET_VERSION="mould-v12")
    base = base.replace('<html lang="en">', '<html lang="' + esc(locale) + '">', 1).replace('noindex,nofollow', robots, 1)
    return base.replace('</head>', '<link rel="canonical" href="' + esc(canonical) + '">' + alternates + '<meta property="og:title" content="' + esc(title) + '"><meta property="og:description" content="' + esc(description) + '"></head>', 1)

def rail(locale: str) -> str:
    return '<aside class="rail" role="complementary" aria-label="Quick contact"><a href="' + WA_URL + '" target="_blank" rel="noopener noreferrer" class="rail-float rail-float--whatsapp" title="Chat on WhatsApp" aria-label="Chat on WhatsApp"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.5 11.2a8.4 8.4 0 0 1-12.4 7.4L4 20l1.4-4A8.4 8.4 0 1 1 20.5 11.2Z"/><path d="M9.2 8.8c.2-.4.4-.4.7-.4h.5c.2 0 .4.1.5.4l.6 1.4c.1.2.1.4-.1.6l-.5.6c.6 1.1 1.5 2 2.6 2.6l.6-.5c.2-.2.4-.2.6-.1l1.4.6c.3.1.4.3.4.5v.5c0 .3 0 .5-.4.7-.5.3-1.1.4-1.7.2-2.1-.6-4.7-3.2-5.3-5.3-.2-.6-.1-1.2.1-1.8Z"/></svg><span class="floating-tooltip">WhatsApp</span></a><a href="' + localized_href(locale, "/contact/") + '" class="rail-float rail-float--wechat" title="WeChat contact" aria-label="WeChat contact"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10.5 6.3C6.9 6.3 4 8.5 4 11.2c0 1.6 1 3 2.5 3.9L6 17l2.2-1.1c.7.2 1.5.3 2.3.3 3.6 0 6.5-2.2 6.5-4.9S14.1 6.3 10.5 6.3Z"/><path d="M14.2 10.1c3.2 0 5.8 1.9 5.8 4.4 0 1.3-.7 2.5-1.9 3.3l.4 1.5-1.8-.9c-.6.2-1.3.3-2 .3-3.2 0-5.8-1.8-5.8-4.2"/></svg><span class="floating-tooltip">WeChat</span></a><a href="tel:+8613606727715" class="rail-float rail-float--phone" title="Call us" aria-label="Call us"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7.1 4.5 9.7 4c.5-.1 1 .2 1.2.7l1.2 2.8c.2.4.1.9-.2 1.2l-1.4 1.4a13.4 13.4 0 0 0 3.4 3.4l1.4-1.4c.3-.3.8-.4 1.2-.2l2.8 1.2c.5.2.8.7.7 1.2l-.5 2.6c-.1.5-.5.8-1 .8C11.8 17.7 6.3 12.2 6.3 5.5c0-.5.3-.9.8-1Z"/></svg><span class="floating-tooltip">Call</span></a></aside>'

def shell(locale: str, title: str, description: str, route: str, body: str) -> str:
    return render_template("shell", HEAD=head(locale, title, description, route), HEADER=header(locale, route), SIDEBAR=rail(locale), BODY=body, FOOTER=footer(locale))

def intro(locale: str, title: str, subtitle: str, route: str) -> str:
    banner_map = {
        "/about/": "/upload/Banner/pheader-About.jpg",
        "/products/": "/upload/Banner/Plastic-flip-top-mold.jpg",
        "/capabilities/": "/upload/Banner/machine.jpg",
        "/samples/": "/upload/Banner/Cap-Samples.jpg",
        "/news/": "/upload/Banner/pheader-news.jpg",
        "/video/": "/upload/Banner/pheader-news.jpg",
        "/contact/": "/upload/Banner/pheader-contact.jpg",
        "/faq/": "/upload/Banner/pheader-faq.jpg",
    }
    banner = banner_map.get(route, "/upload/Banner/Plastic-flip-top-mold.jpg")
    cap = "https://www.cap-molds.com"
    return '<section class="reference-banner"><img src="' + cap + banner + '" alt="LEYA MOULD reference banner" loading="eager" decoding="async"></section><nav class="reference-breadcrumb" aria-label="Breadcrumb"><div class="shell"><a href="' + local_link(locale, "/") + '">' + esc(text(locale, "home")) + '</a><span>›</span><span>' + esc(title) + '</span></div></nav><header class="reference-page-header"><span class="eyebrow">LEYA MOULD · PRECISION TOOLING</span><h1>' + esc(title) + '</h1><p>' + esc(subtitle) + '</p></header>'

def section_heading(locale: str, eyebrow: str, title: str, description: str = "") -> str:
    return '<div class="section__head"><div><span class="eyebrow">' + esc(eyebrow) + '</span><h2 class="section__title">' + esc(title) + '</h2>' + (('<p class="copy-muted">' + esc(description) + '</p>') if description else '') + '</div></div>'

def category_card(locale: str, category: dict) -> str:
    href = localized_href(locale, "/collections/" + category["slug"] + "/")
    title = category_title(locale, category)
    return '<a class="category" href="' + href + '"><div class="category__photo">' + image(category["image"], title + " temporary reference image") + '</div><div class="category__body"><h3>' + esc(title) + '</h3><p class="copy-muted">' + esc(category["short"]) + '</p><span>' + esc(text(locale, "view")) + '</span></div></a>'

def cap_series_card(locale: str, item: dict) -> str:
    href = localized_href(locale, "/collections/bottle-cap-moulds/")
    return '<a class="cap-series-card" href="' + href + '"><div class="cap-series-card__image">' + image(item["image"], item["title"] + " reference image") + '</div><div class="cap-series-card__body"><h3>' + esc(item["title"]) + '</h3><p>' + esc(item["description"]) + '</p><div class="cap-series-card__meta"><span>' + esc(item["meta"]) + '</span><strong>' + esc(text(locale, "view")) + '</strong></div></div></a>'

def home(locale: str) -> str:
    cats = CATALOG["categories"]
    cap = "https://www.cap-molds.com"
    hero_img = cap + "/upload/Banner/Plastic-flip-top-mold.jpg"
    steel_img = cap + "/upload/Home/steel-quality.jpg"
    cap_series = [
        {"title": "Water / Beverage Cap Mould", "description": "High-precision tooling for mineral water, carbonated drinks and juice closures.", "meta": "PCO 1881 · Hot Runner", "image": cap + "/Upload/20260617/202606171039475377.jpg"},
        {"title": "Edible Oil Cap Mould", "description": "Pull-ring and tamper-evident solutions for olive, sunflower and cooking oils.", "meta": "Pull Ring · Tamper-Evident", "image": cap + "/Upload/20260617/202606171650511166.jpg"},
        {"title": "Engine Oil Cap Mould", "description": "Heavy-duty closures for automotive lubricant containers and industrial packaging.", "meta": "High Temp · Heavy Duty", "image": cap + "/upload/Engine-Oil-Cap/PCO38-engine-oil-cap-mould.jpg"},
        {"title": "Food Packaging Cap Mould", "description": "Food-grade screw and snap-on tooling for sauces, dairy and dry food containers.", "meta": "Food Grade · Airtight", "image": cap + "/upload/Food-Packaging-Cap/jar-cap-mould.jpg"},
        {"title": "Medical Cap Mould", "description": "Precision closures for pharmaceutical bottles, syrups and diagnostic packaging.", "meta": "Controlled · Burr-Free", "image": cap + "/upload/Medical-Cap/child-resistant-cap-mould.png"},
        {"title": "Cosmetic Cap Mould (Flip-Top)", "description": "Living-hinge tooling for shampoo, conditioner and skincare packaging.", "meta": "Living Hinge · Flip-Top", "image": cap + "/upload/Personal-Care-Cap/flip-top-cap-mould.jpg"},
        {"title": "Personal Care Cap Mould", "description": "Disc-top, tube-cap and lotion closure tooling with custom orifice options.", "meta": "Disc Top · Custom Orifice", "image": cap + "/upload/Personal-Care-Cap/flip-top-cap-mould.jpg"},
        {"title": "Functional Cap Mould (Combination)", "description": "Child-resistant, easy-open and tamper-evident mechanisms in one closure family.", "meta": "Child-Resistant · Easy-Open", "image": cap + "/upload/Functional-Cap/Functional-Cap-Mould.jpg"},
        {"title": "Handle Mould", "description": "Ergonomic handles for 5L–20L PET bottles, oil containers and chemical jerry cans.", "meta": "High Load · Ergonomic", "image": cap + "/upload/product/month_2105/202105262010194667.jpg"},
    ]
    samples = ["water-cap", "csd-cap", "hotfill-cap", "oil-cap", "soysauce-cap", "pharma-cap", "disc-top-cap", "flip-top-cap", "tamper-evident-cap", "push-pull-cap", "pull-ring-cap", "two-shot-cap", "custom-cap", "wide-mouth-cap", "squeeze-sports-cap", "motor-oil-cap", "5-gallon-cap", "bottle-handle"]
    hero = '<section class="hero hero-slider" data-hero tabindex="0" aria-label="LEYA MOULD"><div class="hero__backdrop"></div><div class="hero__inner shell"><div class="hero__copy"><span class="eyebrow">' + esc(text(locale, "hero_eyebrow")) + '</span><h1 id="hero-title">Your Trusted <span>Plastic Cap Mould</span> Manufacturer</h1><p id="hero-description">' + esc(text(locale, "hero_text")) + '</p><div class="actions"><a id="hero-cta" class="button button--round" href="' + localized_href(locale, "/products/") + '">' + esc(text(locale, "hero_primary")) + '</a><a class="button button--outline button--round" href="' + localized_href(locale, "/contact/#inquiry") + '">' + esc(text(locale, "hero_secondary")) + '</a></div><p class="hero__note">' + esc(text(locale, "hero_note")) + '</p></div><div class="hero__art"><a class="hero__art-link" href="' + localized_href(locale, "/products/") + '" aria-label="Explore mould categories"><img id="hero-image" src="' + hero_img + '" alt="LEYA MOULD precision machining reference" loading="eager" decoding="async"></a></div></div><button class="hero__arrow hero__arrow--prev" type="button" data-hero-nav="-1" aria-label="Previous slide">‹</button><button class="hero__arrow hero__arrow--next" type="button" data-hero-nav="1" aria-label="Next slide">›</button><div class="hero__controls"><button class="hero__dot active" data-hero-go="0" aria-pressed="true" type="button">01</button><button class="hero__dot" data-hero-go="1" aria-pressed="false" type="button">02</button><button class="hero__dot" data-hero-go="2" aria-pressed="false" type="button">03</button><span id="hero-status" class="sr-only" aria-live="polite">Slide 1 of 3</span></div></section>'
    advantages = ''.join('<article class="advantage-card"><span class="advantage-card__number">0' + str(i + 1) + '</span><h3>' + esc(title) + '</h3><p>' + esc(desc) + '</p></article>' for i, (title, desc) in enumerate(data(locale, "advantages")))
    advantages_section = '<section class="section section--advantages"><div class="shell">' + section_heading(locale, "WHY CHOOSE US", "Core Advantages of LEYA MOULD", "From mould design to trial delivery, we deliver value through engineering excellence and strict quality control.") + '<div class="advantage-grid">' + advantages + '</div></div></section>'
    categories = '<section class="section section--soft products-showcase"><div class="shell">' + section_heading(locale, text(locale, "categories_eyebrow"), text(locale, "categories_title"), text(locale, "categories_text")) + '<div class="grid grid--4 mould-category-grid">' + ''.join(category_card(locale, c) for c in cats) + '</div><div class="section__more"><a class="text-link" href="' + localized_href(locale, "/products/") + '">' + esc(text(locale, "products")) + ' →</a></div></div></section>'
    cap_products = '<section class="section cap-series-section"><div class="shell">' + section_heading(locale, "OUR PRODUCTS", "Cap Mould Series", "Explore nine specialized plastic cap mould categories engineered for high-volume production, dimensional accuracy and long service life.") + '<div class="cap-series-grid">' + ''.join(cap_series_card(locale, item) for item in cap_series) + '</div></div></section>'
    sample_cards = ''.join('<a class="sample-card" href="' + localized_href(locale, "/samples/") + '"><img src="' + cap + '/images/samples/' + s + '.jpg" alt="' + esc(s.replace("-", " ").title() + " reference sample") + '" loading="lazy" decoding="async"><span>' + esc(s.replace("-", " ").title()) + '</span></a>' for s in samples)
    samples_section = '<section class="section samples-section"><div class="shell">' + section_heading(locale, "SAMPLES GALLERY", "Plastic Cap Samples", "A wide variety of cap samples for beverage, food, pharma, personal-care and industrial closures. Use the arrows to browse the collection.") + '<div class="samples-track-wrap"><button class="samples-scroll samples-scroll--prev" type="button" data-samples-scroll="-1" aria-label="Previous samples">‹</button><div class="samples-track" data-samples-track>' + sample_cards + '</div><button class="samples-scroll samples-scroll--next" type="button" data-samples-scroll="1" aria-label="Next samples">›</button></div><div class="section__more"><a class="text-link" href="' + localized_href(locale, "/samples/") + '">' + esc(text(locale, "samples")) + ' →</a></div></div></section>'
    technology = '<section class="section technology-section"><div class="shell"><div class="section__head tech-section-head"><div><span class="eyebrow">OUR TECHNOLOGY</span><h2 class="section__title">Engineering Excellence Behind Every Mould</h2><div class="section-line"></div></div></div><div class="tech-grid"><div class="tech-img">' + image(cap + "/upload/Home/precision-machining.jpg", "5-axis CNC machining", "lazy") + '</div><div class="tech-text"><h3>Precision Manufacturing &amp; Strict QC</h3><p>5-axis CNC and EDM achieve ±0.005mm tolerances. Every mould undergoes CMM inspection, trial runs, and leak tests with documented reports.</p><ul class="tech-list"><li>Moldflow simulation before manufacturing</li><li>100% CMM inspection per cavity</li></ul></div></div><div class="tech-grid tech-grid--second"><div class="tech-text"><h3>Premium Steel &amp; Modular Design</h3><p>ASSAB S136, NAK80, H13 steels with vacuum heat treatment (HRC 48–52). Modular inserts enable fast cavity expansion and quick product changeovers.</p><ul class="tech-list"><li>Full material traceability with mill certificates</li><li>Standard delivery in 30–45 days</li></ul></div><div class="tech-img">' + image(cap + "/upload/Home/steel-quality.jpg", "Premium mould steel", "lazy") + '</div></div></div></section>'
    steps = ''.join('<article class="step"><strong>' + esc(num) + '</strong><h3>' + esc(title) + '</h3><p>' + esc(desc) + '</p></article>' for num, title, desc in data(locale, "process_steps"))
    process = '<section class="section workflow-section"><div class="shell">' + section_heading(locale, "HOW WE WORK", "Your Cap Mould Journey", "From your first drawing to delivery and technical support.") + '<div class="steps">' + steps + '</div></div></section>'
    testimonials = '<section class="section testimonial-section"><div class="shell">' + section_heading(locale, "TESTIMONIALS", "Trusted by Packaging Leaders Worldwide", "Hear what our global customers say about the quality, precision, and reliability of LEYA MOULD cap moulds.") + '<div class="testimonial-grid"><article class="testimonial-card"><p>“LEYA MOULD\'s water cap mould has been running over 3 million shots with zero defects.”</p><div><img src="https://flagcdn.com/w40/in.png" alt="India reference"><span>Production Head · India</span></div></article><article class="testimonial-card"><p>“From DFM to delivery, consistent quality and on-time support.”</p><div><img src="https://flagcdn.com/w40/br.png" alt="Brazil reference"><span>Technical Manager · Brazil</span></div></article><article class="testimonial-card"><p>“The tooling is robust, maintainable and ready for repeatable production.”</p><div><img src="https://flagcdn.com/w40/de.png" alt="Germany reference"><span>Plant Director · Germany</span></div></article></div></div></section>'
    references = '<section class="section reference-section"><div class="shell">' + section_heading(locale, "ENGINEERING REFERENCE", "Built for repeatable production decisions.", "Mould structure, steel selection, inspection evidence and trial feedback stay connected through the project.") + '<div class="reference-grid"><article><span>01</span><h3>Precision manufacturing</h3><p>Machining, EDM, fitting and assembly follow the approved tooling brief.</p></article><article><span>02</span><h3>Premium steel & modular design</h3><p>Material traceability and modular inserts keep future changes practical.</p></article><article><span>03</span><h3>Trial & inspection</h3><p>Sample results, dimensional checks and agreed revisions guide handover.</p></article></div></div></section>'
    resources = '<section class="section section--soft resource-section"><div class="shell">' + section_heading(locale, "NEWS & INSIGHTS", "Latest from LEYA MOULD", "Project notes, tooling updates and practical engineering guidance.") + '<div class="resource-grid"><a class="resource-card" href="' + localized_href(locale, "/news/") + '"><span class="eyebrow">NEWS</span><h3>Cap mould project notes</h3><p>Follow new category material, sample references and production lessons.</p><span class="text-link">Read updates →</span></a><a class="resource-card" href="' + localized_href(locale, "/news/") + '"><span class="eyebrow">ENGINEERING</span><h3>Lightweight closure design</h3><p>Review the design questions that influence sealing, cooling and cycle goals.</p><span class="text-link">Read updates →</span></a><a class="resource-card" href="' + localized_href(locale, "/news/") + '"><span class="eyebrow">QUALITY</span><h3>Inspection evidence</h3><p>Keep dimensions, trial results and approved revisions connected.</p><span class="text-link">Read updates →</span></a><a class="resource-card" href="' + localized_href(locale, "/faq/") + '"><span class="eyebrow">FAQ</span><h3>Prepare a useful tooling enquiry</h3><p>See the drawing, resin, machine and sample information that helps a quotation move faster.</p><span class="text-link">View FAQs →</span></a><a class="resource-card" href="' + localized_href(locale, "/video/") + '"><span class="eyebrow">VIDEO</span><h3>Mould trial and review</h3><p>Use the video area for future machine, trial and inspection media.</p><span class="text-link">View video →</span></a><a class="resource-card" href="' + localized_href(locale, "/contact/#inquiry") + '"><span class="eyebrow">CONTACT</span><h3>Send your project brief</h3><p>Tell LEYA MOULD what you are making and where the tooling must run.</p><span class="text-link">Start a conversation →</span></a></div></div></section>'
    return hero + advantages_section + cap_products + samples_section + technology + testimonials + process + resources

def products_page(locale: str) -> str:
    cap = "https://www.cap-molds.com"
    cap_series = [
        {"title": "Water / Beverage Cap Mould", "description": "High-precision tooling for mineral water, carbonated drinks and juice closures.", "meta": "PCO 1881 · Hot Runner", "image": cap + "/Upload/20260617/202606171039475377.jpg"},
        {"title": "Edible Oil Cap Mould", "description": "Pull-ring and tamper-evident solutions for olive, sunflower and cooking oils.", "meta": "Pull Ring · Tamper-Evident", "image": cap + "/Upload/20260617/202606171650511166.jpg"},
        {"title": "Engine Oil Cap Mould", "description": "Heavy-duty closures for automotive lubricant containers and industrial packaging.", "meta": "High Temp · Heavy Duty", "image": cap + "/upload/Engine-Oil-Cap/PCO38-engine-oil-cap-mould.jpg"},
        {"title": "Food Packaging Cap Mould", "description": "Food-grade screw and snap-on tooling for sauces, dairy and dry food containers.", "meta": "Food Grade · Airtight", "image": cap + "/upload/Food-Packaging-Cap/jar-cap-mould.jpg"},
        {"title": "Medical Cap Mould", "description": "Precision closures for pharmaceutical bottles, syrups and diagnostic packaging.", "meta": "Controlled · Burr-Free", "image": cap + "/upload/Medical-Cap/child-resistant-cap-mould.png"},
        {"title": "Cosmetic Cap Mould (Flip-Top)", "description": "Living-hinge tooling for shampoo, conditioner and skincare packaging.", "meta": "Living Hinge · Flip-Top", "image": cap + "/upload/Personal-Care-Cap/flip-top-cap-mould.jpg"},
        {"title": "Personal Care Cap Mould", "description": "Disc-top, tube-cap and lotion closure tooling with custom orifice options.", "meta": "Disc Top · Custom Orifice", "image": cap + "/upload/Personal-Care-Cap/flip-top-cap-mould.jpg"},
        {"title": "Functional Cap Mould (Combination)", "description": "Child-resistant, easy-open and tamper-evident mechanisms in one closure family.", "meta": "Child-Resistant · Easy-Open", "image": cap + "/upload/Functional-Cap/Functional-Cap-Mould.jpg"},
        {"title": "Handle Mould", "description": "Ergonomic handles for 5L–20L PET bottles, oil containers and chemical jerry cans.", "meta": "High Load · Ergonomic", "image": cap + "/upload/product/month_2105/202105262010194667.jpg"},
    ]
    hero = '<section class="catalog-hero"><div class="shell"><h1>Precision <span>CAP MOULD</span><br>Across 9 Key Categories</h1><p>Professional plastic cap mould manufacturer with 15+ years of experience. From beverage caps to medical closures, we deliver high-precision, long-life mould solutions.</p><a class="button button--round" href="' + localized_href(locale, "/contact/#inquiry") + '">' + esc(text(locale, "quote")) + ' →</a><div class="catalog-stats"><div><strong>15+</strong><span>YEARS EXPERIENCE</span></div><div><strong>9</strong><span>CAP CATEGORIES</span></div><div><strong>40+</strong><span>COUNTRIES SERVED</span></div><div><strong>2000+</strong><span>MOULDS DELIVERED</span></div></div></div></section>'
    crumb = '<nav class="reference-breadcrumb" aria-label="Breadcrumb"><div class="shell"><a href="' + local_link(locale, "/") + '">' + esc(text(locale, "home")) + '</a><span>›</span><span>' + esc(text(locale, "products")) + '</span></div></nav>'
    cards = ''.join(cap_series_card(locale, c) for c in cap_series)
    products = '<section class="section cap-series-section"><div class="shell">' + section_heading(locale, "OUR PRODUCTS", "Cap Mould Series", "Explore our comprehensive range of 9 specialized plastic cap mould categories. Each mould is engineered for high-volume production, dimensional accuracy and extended service life.") + '<div class="cap-series-grid">' + cards + '</div></div></section>'
    return hero + crumb + products

def category_page(locale: str, category: dict) -> str:
    checks = ''.join('<li>' + esc(x) + '</li>' for x in category["checks"])
    title = category_title(locale, category)
    body = intro(locale, title, category["short"], "/collections/" + category["slug"] + "/")
    body += '<section class="section"><div class="shell"><div class="split"><div>' + image(category["image"], title + " temporary reference image", "eager") + '</div><div><span class="eyebrow">' + esc(text(locale, "categories_eyebrow")) + '</span><h2 class="section__title">' + esc(title) + '</h2><p class="copy-muted">' + esc(category["detail"]) + '</p><ul class="mould-checklist">' + checks + '</ul><p class="notice">' + esc(text(locale, "category_note")) + '</p><a class="button" href="' + localized_href(locale, "/contact/#inquiry") + '">' + esc(text(locale, "quote")) + ' →</a></div></div></div></section>'
    body += '<section class="section section--soft"><div class="shell">' + section_heading(locale, text(locale, "technical_eyebrow"), text(locale, "resources_title"), text(locale, "resources_text")) + '<div class="split__placeholder"><strong>HIGH-RESOLUTION IMAGES / PDF</strong><p>' + esc(text(locale, "category_note")) + '</p></div></div></section>'
    return body

def about_page(locale: str) -> str:
    body = intro(locale, text(locale, "about_title"), text(locale, "about_text"), "/about/")
    body += '<section class="section"><div class="shell"><div class="article"><p>' + esc(text(locale, "about_text")) + '</p><h2>LEYA MOULD Co.,Ltd</h2><p>' + esc(ADDRESS) + '<br><a href="mailto:' + EMAIL + '">' + EMAIL + '</a><br><a href="' + WA_URL + '">WhatsApp: ' + esc(WHATSAPP) + '</a></p><h2>' + esc(text(locale, "why_title")) + '</h2><p>' + esc(text(locale, "why_text")) + '</p></div></div></section>'
    return body

def capabilities_page(locale: str) -> str:
    cards = ''.join('<a class="category" href="' + localized_href(locale, "/capabilities/" + s["slug"] + "/") + '"><div class="category__body"><h3>' + esc(s["title"]) + '</h3><p class="copy-muted">' + esc(s["text"]) + '</p><span>' + esc(text(locale, "learn")) + '</span></div></a>' for s in CATALOG["services"])
    return intro(locale, text(locale, "capabilities"), text(locale, "technical_text"), "/capabilities/") + '<section class="section"><div class="shell"><div class="grid grid--3">' + cards + '</div></div></section>'

def service_page(locale: str, service: dict) -> str:
    body = intro(locale, service["title"], service["text"], "/capabilities/" + service["slug"] + "/")
    body += '<section class="section"><div class="shell"><div class="split"><div><h2 class="section__title">' + esc(service["title"]) + '</h2><p class="copy-muted">' + esc(service["text"]) + '</p><p class="copy-muted">' + esc(text(locale, "technical_text")) + '</p></div><div class="split__placeholder"><strong>PROJECT FILES TO BE REVIEWED</strong><p>Drawing · sample · PDF · revision notes</p></div></div><p style="margin-top:28px"><a class="button" href="' + localized_href(locale, "/contact/#inquiry") + '">' + esc(text(locale, "quote")) + ' →</a></p></div></section>'
    return body

def contact_page(locale: str) -> str:
    labels = {"FORM_ARIA": text(locale, "form_aria"), "FORM_REQUIRED_NOTE": text(locale, "form_required"), "FORM_COMPANY": text(locale, "form_company"), "FORM_COMPANY_PLACEHOLDER": "Your company" if locale == "en" else text(locale, "form_company"), "FORM_EMAIL": text(locale, "form_email"), "FORM_CATEGORY": text(locale, "form_category"), "FORM_CATEGORY_PLACEHOLDER": "e.g. PET preform, bottle cap", "FORM_QUANTITY": text(locale, "form_quantity"), "FORM_QUANTITY_PLACEHOLDER": "e.g. annual volume or cavities", "FORM_COUNTRY": text(locale, "form_country"), "FORM_COUNTRY_PLACEHOLDER": "Country", "FORM_TYPE": text(locale, "form_type"), "FORM_TYPE_QUOTE": text(locale, "form_quote"), "FORM_TYPE_NEW": text(locale, "form_new"), "FORM_TYPE_REVIEW": text(locale, "form_review"), "FORM_TYPE_TECH": text(locale, "form_tech"), "FORM_MATERIAL": text(locale, "form_material"), "FORM_ADVISE": text(locale, "form_advise"), "FORM_OTHER": text(locale, "form_other"), "FORM_REQUIREMENTS": text(locale, "form_requirements"), "FORM_REQUIREMENTS_PLACEHOLDER": "Part drawing, target resin, cavities, cycle goals, sample or PDF reference", "FORM_CONSENT": text(locale, "form_consent"), "FORM_PRIVACY": text(locale, "form_privacy"), "FORM_SUBMIT": text(locale, "form_submit")}
    form = render_template("contact-form", **{key: esc(value) for key, value in labels.items()})
    body = intro(locale, text(locale, "contact_title"), text(locale, "contact_intro"), "/contact/")
    body += '<section class="section"><div class="shell"><div class="contact-layout"><div><span class="eyebrow">LEYA MOULD Co.,Ltd</span><h2 class="section__title">' + esc(text(locale, "contact_title")) + '</h2><p class="copy-muted">' + esc(text(locale, "contact_intro")) + '</p><div class="benefit"><h3>' + esc(ADDRESS) + '</h3><p><a href="mailto:' + EMAIL + '">' + EMAIL + '</a><br><a href="' + WA_URL + '">WhatsApp: ' + esc(WHATSAPP) + '</a></p></div></div>' + form + '</div></div></section>'
    return body

def faq_page(locale: str) -> str:
    pairs = [("What should I send first?", "A drawing, physical sample, PDF or clear reference photo plus the target resin and market."), ("Can you review an existing mould?", "Yes. Share the current mould information, sample results, problem description and any available inspection records."), ("Will the product pages contain PDFs and high-resolution photos?", "Yes. Approved preform, bottle, cap and knife-and-fork media will be added to the relevant category when supplied."), ("How do I request a quotation?", "Use the enquiry form or email amyhu@leyamould.com with the project brief." )]
    if locale != "en":
        pairs = [(text(locale, "faq_title"), text(locale, "faq_intro"))] + pairs[1:]
    rows = ''.join('<details><summary>' + esc(q) + '</summary><p>' + esc(a) + '</p></details>' for q, a in pairs)
    return intro(locale, text(locale, "faq_title"), text(locale, "faq_intro"), "/faq/") + '<section class="section"><div class="shell"><div class="faq-list">' + rows + '</div></div></section>'

def simple_page(locale: str, route: str, title: str, description: str, body: str) -> str:
    return intro(locale, title, description, route) + '<section class="section"><div class="shell"><div class="article">' + body + '</div></div></section>'

def write(path: str, content: str) -> None:
    target = OUTPUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

def generate() -> dict:
    routes: dict[str, str] = {}
    def add(locale: str, route: str, title: str, description: str, body: str) -> None:
        localized = route_for(locale, route)
        file_path = localized.strip("/") + "/index.html" if localized != "/" else "index.html"
        write(file_path, shell(locale, title + " | LEYA MOULD" if route != "/" else title + " | LEYA MOULD", description, route, body))
        routes[localized] = title
    for locale in LOCALES:
        code = locale["code"]
        add(code, "/", text(code, "hero_title"), text(code, "hero_text"), home(code))
        add(code, "/products/", text(code, "products"), text(code, "categories_text"), products_page(code))
        for category in CATALOG["categories"]:
            add(code, "/collections/" + category["slug"] + "/", category_title(code, category), category["short"], category_page(code, category))
            # A stable category detail route keeps future PDF/image imports compatible.
            add(code, "/products/" + category["slug"] + "/", category_title(code, category) + " Project", category["detail"], category_page(code, category))
        add(code, "/about/", text(code, "about_title"), text(code, "about_text"), about_page(code))
        add(code, "/capabilities/", text(code, "capabilities"), text(code, "technical_text"), capabilities_page(code))
        for service in CATALOG["services"]:
            add(code, "/capabilities/" + service["slug"] + "/", service["title"], service["text"], service_page(code, service))
        add(code, "/manufacturing/", text(code, "process"), text(code, "process_title"), simple_page(code, "/manufacturing/", text(code, "process"), text(code, "process_title"), '<p>' + esc(text(code, "process_title")) + '</p><p>' + esc(text(code, "technical_text")) + '</p>'))
        add(code, "/quality-control/", text(code, "footer_quality"), text(code, "technical_text"), simple_page(code, "/quality-control/", text(code, "footer_quality"), text(code, "technical_text"), '<p>' + esc(text(code, "technical_text")) + '</p>'))
        add(code, "/request-sample/", text(code, "quote"), text(code, "resources_text"), contact_page(code))
        add(code, "/contact/", text(code, "contact"), text(code, "contact_intro"), contact_page(code))
        samples_body = '<p>' + esc(text(code, "categories_text")) + '</p><div class="samples-page-grid">' + ''.join('<a class="sample-card" href="' + localized_href(code, "/contact/#inquiry") + '"><img src="https://www.cap-molds.com/images/samples/' + s + '.jpg" alt="' + esc(s.replace("-", " ").title() + " reference sample") + '" loading="lazy" decoding="async"><span>' + esc(s.replace("-", " ").title()) + '</span></a>' for s in ["water-cap", "csd-cap", "hotfill-cap", "oil-cap", "soysauce-cap", "pharma-cap", "disc-top-cap", "flip-top-cap", "tamper-evident-cap", "push-pull-cap", "two-shot-cap", "motor-oil-cap"]) + '</div>'
        add(code, "/samples/", text(code, "samples"), text(code, "categories_text"), simple_page(code, "/samples/", text(code, "samples"), text(code, "categories_text"), samples_body))
        add(code, "/news/", text(code, "news"), text(code, "blog_text"), simple_page(code, "/news/", text(code, "news"), text(code, "blog_text"), '<div class="resource-grid"><a class="resource-card" href="' + localized_href(code, "/faq/") + '"><span class="eyebrow">FAQ</span><h3>' + esc(text(code, "faq_title")) + '</h3><p>' + esc(text(code, "faq_intro")) + '</p></a><a class="resource-card" href="' + localized_href(code, "/capabilities/") + '"><span class="eyebrow">ENGINEERING</span><h3>' + esc(text(code, "capabilities")) + '</h3><p>' + esc(text(code, "technical_text")) + '</p></a><a class="resource-card" href="' + localized_href(code, "/contact/#inquiry") + '"><span class="eyebrow">PROJECT</span><h3>' + esc(text(code, "quote")) + '</h3><p>' + esc(text(code, "resources_text")) + '</p></a></div>'))
        add(code, "/video/", text(code, "video"), text(code, "technical_text"), simple_page(code, "/video/", text(code, "video"), text(code, "technical_text"), '<div class="video-placeholder"><span class="eyebrow">LEYA MOULD</span><h2>Production and mould review videos</h2><p>' + esc(text(code, "technical_text")) + '</p><a class="button" href="' + localized_href(code, "/contact/#inquiry") + '">' + esc(text(code, "quote")) + ' →</a></div>'))
        add(code, "/faq/", text(code, "faq_title"), text(code, "faq_intro"), faq_page(code))
        add(code, "/blog/", text(code, "blog_title"), text(code, "blog_text"), simple_page(code, "/blog/", text(code, "blog_title"), text(code, "blog_text"), '<p>' + esc(text(code, "blog_text")) + '</p><p><a class="button" href="' + localized_href(code, "/contact/#inquiry") + '">' + esc(text(code, "quote")) + ' →</a></p>'))
        add(code, "/privacy-policy/", text(code, "privacy_title"), text(code, "privacy_text"), simple_page(code, "/privacy-policy/", text(code, "privacy_title"), text(code, "privacy_text"), '<p>' + esc(text(code, "privacy_text")) + '</p>'))
    not_found = shell("en", "Page Not Found | LEYA MOULD", "The requested page could not be found.", "/404.html", intro("en", "Page Not Found", "The requested page could not be found.", "/404.html") + '<section class="section"><div class="shell"><a class="button" href="/">Back to Home →</a></div></section>')
    write("404.html", not_found)
    write("robots.txt", "User-agent: *\n" + ("Allow: /\nSitemap: " + ORIGIN + "/sitemap.xml\n" if INDEXING_APPROVED else "Disallow: /\n"))
    sitemap = ['<?xml version="1.0" encoding="utf-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for route in sorted(routes):
        sitemap.append("  <url><loc>" + esc(ORIGIN + route) + "</loc></url>")
    sitemap.append("</urlset>")
    write("sitemap.xml", "\n".join(sitemap) + "\n")
    manifest = {"schemaVersion": 1, "locales": [{**row, "enabled": True, "publishReady": True} for row in LOCALES], "routes": sorted(routes)}
    write("locale-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return {"routes": routes, "locales": LOCALES}

if __name__ == "__main__":
    result = generate()
    print("LEYA_MOULD_SOURCE_BUILD_OK", "HTML_FILES", len(result["routes"]), "LOCALES", ",".join(x["code"] for x in result["locales"]))

