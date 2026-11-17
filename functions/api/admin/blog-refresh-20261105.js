import { authorizedBuildRequest } from "../../_shared/build-auth.js";
import { ensureBlogSchema } from "../../_shared/blog-cms.js";
import { ensureTranslationSchema } from "../../_shared/translation.js";
import { bumpPublishRevision } from "../../_shared/site-settings.js";

const LOCALES = ["es", "pt", "ru", "tr"];
const TARGET_ORDER = [
  "golf-club-pro-shop-reusable-water-bottles-wholesale",
  "outdoor-gear-retailer-hiking-water-bottles-wholesale",
  "sustainable-lifestyle-store-reusable-bottles-wholesale"
];

const PATCHES = {
  "golf-club-pro-shop-reusable-water-bottles-wholesale": {
    en: {
      title: "How Should Golf Clubs Source 550ml / 18.6 oz Custom Plastic Water Bottles Wholesale for Pro Shops?",
      description: "A B2B wholesale sourcing guide for golf clubs comparing 550ml / 18.6 oz member bottles, custom plastic branding, mixed-color pro-shop assortments, tournament quantities, samples and repeat orders.",
      introSuffix: "For a practical first comparison, separate 550 ml (18.6 fl oz) member bottles from larger event formats, then verify the complete plastic assembly, lid and decoration before approving a wholesale order from a bottle manufacturer.",
      firstSuffix: "Build the range around the actual use case: a 550 ml (18.6 fl oz) bottle may suit a pro-shop shelf or member welcome pack, while a tournament allocation may need a different capacity or carry format. Ask the plastic bottle manufacturer to confirm the assembled dimensions, lid components, mixed-color options and decoration scope rather than quoting from a body-only photograph.",
      primary: "golf club custom plastic water bottles wholesale",
      secondary: ["550ml golf club water bottles", "18.6 oz golf member bottles", "custom golf pro shop drinkware", "golf tournament bottle manufacturer"]
    },
    es: {
      title: "¿Cómo pueden los clubes de golf comprar al por mayor botellas personalizadas de plástico de 550 ml / 18,6 oz para pro shops?",
      description: "Guía B2B de compra mayorista para clubes de golf: botellas de 550 ml / 18,6 oz, plástico personalizable, colores combinados para pro shops, cantidades de torneos, muestras y reposición.",
      introSuffix: "Como primera comparación, separe las botellas de 550 ml (18,6 oz líquidas) para miembros de los formatos grandes para eventos y confirme el conjunto plástico completo con un fabricante antes de aprobar el pedido mayorista.",
      firstSuffix: "Para el surtido, compare una botella de 550 ml (18,6 oz líquidas) con formatos mayores y pida al fabricante de botellas de plástico que confirme las dimensiones ensambladas, los componentes de la tapa, los colores combinados y el alcance de la personalización."
    },
    pt: {
      title: "Como os clubes de golfe devem comprar no atacado garrafas personalizadas de plástico de 550 ml / 18,6 oz para pro shops?",
      description: "Guia B2B de compras no atacado para clubes de golfe: garrafas de 550 ml / 18,6 oz, plástico personalizável, cores combinadas para pro shops, quantidades de torneio, amostras e reposição.",
      introSuffix: "Como primeira comparação, separe garrafas de 550 ml (18,6 fl oz) para associados dos formatos maiores para eventos e confirme o conjunto plástico completo com o fabricante antes de aprovar o pedido no atacado.",
      firstSuffix: "Para o sortimento, compare uma garrafa de 550 ml (18,6 fl oz) com formatos maiores e peça ao fabricante de garrafas plásticas as dimensões montadas, os componentes da tampa, as opções de cores combinadas e o escopo da personalização."
    },
    ru: {
      title: "Как гольф-клубам закупать оптом кастомные пластиковые бутылки 550 мл / 18,6 oz для pro shop?",
      description: "B2B-гид по оптовой закупке для гольф-клубов: бутылки 550 мл / 18,6 oz, кастомный пластик, смешанные цвета для pro shop, турнирные партии, образцы и повторные заказы.",
      introSuffix: "Для первой проверки отделите бутылки 550 мл (18,6 жидких унции) для участников от больших форматов для мероприятий и подтвердите полную пластиковую сборку у производителя до оптового заказа.",
      firstSuffix: "Для ассортимента сравните бутылку 550 мл (18,6 жидких унции) с крупными форматами и попросите производителя пластиковых бутылок подтвердить размеры в сборе, компоненты крышки, смешанные цвета и объём кастомизации."
    },
    tr: {
      title: "Golf kulüpleri pro shop için 550 ml / 18,6 oz özel plastik mataraları toptan nasıl almalı?",
      description: "Golf kulüpleri için B2B toptan satın alma rehberi: 550 ml / 18,6 oz mataralar, özel plastik, pro shop için karışık renkler, turnuva miktarları, numune ve tekrar siparişi.",
      introSuffix: "İlk karşılaştırmada üyeler için 550 ml (18,6 fl oz) ürünü etkinlikler için daha büyük formatlardan ayırın ve toptan siparişi onaylamadan önce komple plastik ürünü üreticiyle doğrulayın.",
      firstSuffix: "Ürün grubunda 550 ml (18,6 fl oz) modeli daha büyük formatlarla karşılaştırın; plastik matara üreticisinden komple ölçüleri, kapak bileşenlerini, karışık renk seçeneklerini ve kişiselleştirme kapsamını isteyin."
    }
  },
  "outdoor-gear-retailer-hiking-water-bottles-wholesale": {
    en: {
      title: "How Should Outdoor Retailers Source 800ml / 27 oz Custom Plastic Hiking Water Bottles Wholesale?",
      description: "A B2B wholesale buying guide for outdoor retailers comparing 800ml / 27 oz hiking bottles, backpack fit, custom plastic options, mixed-color assortments, samples, packaging and repeat replenishment.",
      introSuffix: "Compare 800 ml (27 fl oz) as a practical day-trip reference, then check the bottle, lid, carry point and backpack fit as one assembled product. For a wholesale or private-label program, request a factory quote that separates capacity, color, logo and packaging decisions.",
      firstSuffix: "Use 800 ml (27 fl oz) as a reference only after checking the actual customer routine. Ask the plastic bottle factory for a complete assembled sample, dimensions, backpack-fit notes and customization options before fixing the retail range.",
      primary: "800ml custom plastic hiking water bottles wholesale",
      secondary: ["27 oz hiking bottles wholesale", "outdoor retailer bottle supplier", "private label plastic hiking bottles", "mixed-color outdoor bottle assortment"]
    },
    es: {
      title: "¿Cómo pueden los minoristas outdoor comprar al por mayor botellas de senderismo personalizadas de plástico de 800 ml / 27 oz?",
      description: "Guía B2B para minoristas outdoor: botellas de senderismo de 800 ml / 27 oz, plástico personalizable, surtidos de colores combinados, muestras, embalaje y reposición.",
      introSuffix: "Compare 800 ml (27 oz líquidas) como referencia para excursiones de un día y revise botella, tapa, punto de transporte y ajuste como un conjunto ensamblado. Para un programa mayorista o de marca privada, solicite al fabricante una cotización separada por capacidad, color, logotipo y embalaje.",
      firstSuffix: "Use 800 ml (27 oz líquidas) como referencia después de comprobar la rutina real y pida al fabricante de botellas de plástico una muestra completa, medidas, notas de ajuste en mochila y opciones de personalización."
    },
    pt: {
      title: "Como os varejistas outdoor devem comprar no atacado garrafas de trilha personalizadas de plástico de 800 ml / 27 oz?",
      description: "Guia B2B para varejistas outdoor: garrafas de trilha de 800 ml / 27 oz, plástico personalizável, sortimentos de cores combinadas, amostras, embalagem e reposição.",
      introSuffix: "Compare 800 ml (27 fl oz) como referência para passeios de um dia e avalie garrafa, tampa, ponto de transporte e encaixe como um conjunto montado. Para um programa de atacado ou marca própria, peça ao fabricante uma cotação que separe capacidade, cor, logotipo e embalagem.",
      firstSuffix: "Use 800 ml (27 fl oz) como referência após verificar a rotina real e peça ao fabricante de garrafas plásticas uma amostra completa, medidas, notas de encaixe na mochila e opções de personalização."
    },
    ru: {
      title: "Как outdoor-магазинам закупать оптом кастомные пластиковые бутылки для походов 800 мл / 27 oz?",
      description: "B2B-гид для outdoor-ритейла: бутылки 800 мл / 27 oz для походов, кастомный пластик, смешанные цвета, образцы, упаковка и повторное пополнение.",
      introSuffix: "Сравнивайте 800 мл (27 жидких унции) как ориентир для однодневной прогулки, затем проверяйте бутылку, крышку, точку переноски и посадку в рюкзаке как одну сборку. Для оптовой или private-label программы попросите производителя разделить в предложении объём, цвет, логотип и упаковку.",
      firstSuffix: "Используйте 800 мл (27 жидких унции) как ориентир после проверки реального сценария и запросите у производителя пластиковых бутылок образец в сборе, размеры, заметки по посадке в рюкзаке и варианты кастомизации."
    },
    tr: {
      title: "Outdoor perakendecileri 800 ml / 27 oz özel plastik yürüyüş mataralarını toptan nasıl almalı?",
      description: "Outdoor perakendecileri için B2B rehber: 800 ml / 27 oz yürüyüş mataraları, özel plastik, karışık renkli ürün grupları, numune, ambalaj ve tekrar tedariki.",
      introSuffix: "800 ml (27 fl oz) hacmi günlük gezi için referans alın; ardından matarayı, kapağı, taşıma noktasını ve çantaya uyumu komple ürün olarak kontrol edin. Toptan veya private-label programında üreticiden hacim, renk, logo ve ambalaj kararlarını ayrı gösteren teklif isteyin.",
      firstSuffix: "800 ml (27 fl oz) hacmi gerçek kullanım kontrolünden sonra referans alın ve plastik matara üreticisinden komple numune, ölçüler, çantaya uyum notları ve kişiselleştirme seçenekleri isteyin."
    }
  },
  "sustainable-lifestyle-store-reusable-bottles-wholesale": {
    en: {
      title: "How Should Lifestyle Stores Source 380–800ml / 12.8–27 oz Custom Plastic Bottles Wholesale?",
      description: "A B2B wholesale and OEM guide for lifestyle retailers comparing 380–800ml / 12.8–27 oz reusable plastic bottles, material evidence, custom colors, packaging and replenishment.",
      introSuffix: "A 380 ml (12.8 fl oz) commuter bottle and an 800 ml (27 fl oz) day-use bottle serve different shelf and refill routines. Compare the complete plastic components, documented material information and custom packaging before making any environmental or safety statement.",
      firstSuffix: "Separate compact 380 ml (12.8 fl oz) formats from larger 800 ml (27 fl oz) options in the assortment plan. A plastic bottle manufacturer should identify the body, lid and seal materials and show which custom colors, logos and packaging formats can actually be produced for the requested wholesale quantity.",
      primary: "custom plastic reusable bottles wholesale for lifestyle stores",
      secondary: ["380ml reusable bottles wholesale", "12.8 oz lifestyle store bottles", "800ml refill shop bottles", "OEM plastic bottle manufacturer"]
    },
    es: {
      title: "¿Cómo pueden las tiendas de estilo de vida comprar al por mayor botellas personalizadas de plástico de 380–800 ml / 12,8–27 oz?",
      description: "Guía B2B de venta mayorista y OEM para tiendas de estilo de vida: botellas reutilizables de plástico de 380–800 ml / 12,8–27 oz, materiales, colores, embalaje y reposición.",
      introSuffix: "Una botella de 380 ml (12,8 oz líquidas) para desplazamientos y una de 800 ml (27 oz líquidas) para el día completo responden a rutinas distintas. Compare los componentes plásticos completos, la información documentada y el embalaje personalizado antes de afirmar algo sobre el producto.",
      firstSuffix: "Separe en el surtido los formatos compactos de 380 ml (12,8 oz líquidas) de las opciones grandes de 800 ml (27 oz líquidas). El fabricante de botellas de plástico debe identificar los materiales del cuerpo, la tapa y el sello, y confirmar qué colores, logotipos y embalajes personalizados puede producir para la cantidad solicitada."
    },
    pt: {
      title: "Como as lojas de lifestyle devem comprar no atacado garrafas personalizadas de plástico de 380–800 ml / 12,8–27 oz?",
      description: "Guia B2B de atacado e OEM para lojas de lifestyle: garrafas reutilizáveis de plástico de 380–800 ml / 12,8–27 oz, materiais, cores, embalagem e reposição.",
      introSuffix: "Uma garrafa de 380 ml (12,8 fl oz) para deslocamentos e uma de 800 ml (27 fl oz) para o dia inteiro atendem rotinas diferentes. Compare os componentes plásticos completos, a informação documentada e a embalagem personalizada antes de fazer qualquer afirmação.",
      firstSuffix: "No sortimento, separe formatos compactos de 380 ml (12,8 fl oz) das opções de 800 ml (27 fl oz). O fabricante de garrafas plásticas deve identificar os materiais do corpo, da tampa e do vedante e confirmar quais cores, logotipos e formatos de embalagem personalizados pode produzir para a quantidade no atacado."
    },
    ru: {
      title: "Как lifestyle-магазинам закупать оптом кастомные пластиковые бутылки 380–800 мл / 12,8–27 oz?",
      description: "B2B-гид по оптовой и OEM-закупке для lifestyle-ритейла: многоразовые пластиковые бутылки 380–800 мл / 12,8–27 oz, материалы, цвета, упаковка и пополнение.",
      introSuffix: "Бутылка 380 мл (12,8 жидких унции) для поездок и бутылка 800 мл (27 жидких унции) для длинного дня обслуживают разные сценарии. Сравните полную пластиковую сборку, документированные материалы и кастомную упаковку до экологических или потребительских заявлений.",
      firstSuffix: "В ассортименте разделите компактные форматы 380 мл (12,8 жидких унции) и варианты 800 мл (27 жидких унции). Производитель пластиковой бутылки должен указать материалы корпуса, крышки и уплотнителя, а также подтвердить доступные цвета, логотипы и упаковку для нужного оптового количества."
    },
    tr: {
      title: "Lifestyle mağazaları 380–800 ml / 12,8–27 oz özel plastik mataraları toptan nasıl almalı?",
      description: "Lifestyle mağazaları için B2B toptan ve OEM rehberi: 380–800 ml / 12,8–27 oz yeniden kullanılabilir plastik mataralar, malzeme, renk, ambalaj ve tekrar tedariki.",
      introSuffix: "380 ml (12,8 fl oz) işe gidiş ürünü ile 800 ml (27 fl oz) günlük kullanım ürünü farklı raf ve dolum rutinlerine hizmet eder. Çevresel veya güvenlik açıklaması yapmadan önce komple plastik bileşenleri, belgelenen malzemeleri ve özel ambalajı karşılaştırın.",
      firstSuffix: "Ürün grubunda kompakt 380 ml (12,8 fl oz) formatları 800 ml (27 fl oz) seçeneklerden ayırın. Plastik matara üreticisi gövde, kapak ve contanın malzemelerini belirtmeli; istenen toptan miktar için hangi özel renk, logo ve ambalaj formatlarını üretebildiğini doğrulamalıdır."
    }
  }
};

const clean = (value, max = 260000) => String(value ?? "").replace(/\0/g, "").slice(0, max);
const reply = (body, status = 200) => Response.json(body, { status, headers: { "cache-control": "no-store", "x-robots-tag": "noindex,nofollow,noarchive" } });
const esc = value => String(value ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
const unique = values => [...new Set(values)];
const count = (value, needle) => String(value).split(needle).length - 1;
const blocked = /<\s*(?:script|iframe|object|embed|form|style|link|base|meta|svg|math|template)\b|\bon[a-z-]+\s*=|srcdoc\s*=|(?:javascript|vbscript|data)\s*:/i;

async function authorized(context) {
  if (!clean(context.env.ADMIN_TOKEN)) return reply({ error: "ADMIN_TOKEN not configured" }, 503);
  if (!(await authorizedBuildRequest(context.request, context.env))) return reply({ error: "Unauthorized" }, 401);
  if (!context.env.XUYI_DB) return reply({ error: "XUYI_DB binding missing" }, 503);
  return null;
}

function validatePost(slug, post) {
  if (!post || post.slug !== slug) throw Error("Invalid Blog slug: " + slug);
  if (String(post.title || "").length < 40 || String(post.description || "").length < 80 || String(post.intro || "").length < 220) throw Error("SEO fields are too short: " + slug);
  if (!Array.isArray(post.sections) || post.sections.length !== 7 || post.sections.some(x => String(x?.heading || "").length < 10 || String(x?.paragraph || "").length < 600)) throw Error("Seven substantive sections required: " + slug);
  if (!Array.isArray(post.checklist) || post.checklist.length !== 10) throw Error("Ten-item checklist required: " + slug);
  if (!Array.isArray(post.faqs) || post.faqs.length !== 4) throw Error("Four FAQs required: " + slug);
  if (!Array.isArray(post.related) || post.related.length !== 3 || unique(post.related).length !== 3 || post.related.includes(slug)) throw Error("Three related articles required: " + slug);
  if (!Array.isArray(post.inline_links) || post.inline_links.length !== 2 || !post.buyerDecisionTable || !Array.isArray(post.buyerDecisionTable.rows) || post.buyerDecisionTable.rows.length !== 6) throw Error("Buyer matrix required: " + slug);
  if (!Array.isArray(post.product_notes) || post.product_notes.length !== 3) throw Error("Three product notes required: " + slug);
  const models = unique(post.product_notes.map(x => String(x?.sku || "")));
  if (models.length !== 3 || models.some(x => !/^[A-Za-z0-9][A-Za-z0-9-]{1,23}$/.test(x))) throw Error("Exactly three product notes required: " + slug);
  if (JSON.stringify(post).length > 100000) throw Error("Blog content is too large: " + slug);
}

function setText(html, regex, value, label) {
  if (regex.test(html)) return html.replace(regex, (...args) => args[1] + esc(value) + args[2]);
  if (html.includes(esc(value))) return html;
  throw Error("Expected localized HTML anchor missing: " + label);
}
function appendText(html, regex, suffix, label) {
  if (html.includes(esc(suffix))) return html;
  if (!regex.test(html)) throw Error("Expected localized HTML anchor missing: " + label);
  return html.replace(regex, (...args) => args[1] + args[2] + " " + esc(suffix) + args[3]);
}
function patchDetailHtml(html, patch, slug, locale) {
  let out = String(html || "");
  out = setText(out, /(<h1>)[\s\S]*?(<\/h1>)/, patch.title, slug + " " + locale + " h1");
  out = setText(out, /(<h1>[\s\S]*?<\/h1><p>)[\s\S]*?(<\/p>)/, patch.description, slug + " " + locale + " description");
  out = appendText(out, /(<p class="blog-lede">)([\s\S]*?)(<\/p>)/, patch.introSuffix, slug + " " + locale + " intro");
  out = appendText(out, /(<section class="blog-section" id="article-section-0">[\s\S]*?<p>)([\s\S]*?)( <span class="blog-editorial__product-note")/, patch.firstSuffix, slug + " " + locale + " first section");
  if (blocked.test(out) || count(out, 'class="blog-section"') !== 7 || count(out, 'class="blog-editorial__product-link"') !== 3 || count(out, "<details>") !== 4 || count(out, 'class="blog-related__item"') !== 3 || count(out, 'class="blog-buyer-matrix"') !== 1) throw Error("Localized article structure changed: " + slug + " " + locale);
  return out;
}
function patchCardHtml(html, patch, slug, locale) {
  let out = String(html || "");
  if (!out.includes('href="/blog/' + slug + '/"')) throw Error("Localized index card missing: " + slug + " " + locale);
  out = setText(out, /(<h3><a\b[^>]*>)[\s\S]*?(<\/a><\/h3>)/, patch.title, slug + " " + locale + " card title");
  out = setText(out, /(<h3>[\s\S]*?<\/h3><p>)[\s\S]*?(<\/p>)/, patch.description, slug + " " + locale + " card description");
  if (blocked.test(out) || count(out, 'href="/blog/' + slug + '/"') !== 3) throw Error("Localized index card structure changed: " + slug + " " + locale);
  return out;
}
function orderIndex(html, cards, sourceOrder, locale) {
  const blocks = String(html || "").match(/<article class="news-card">[\s\S]*?<\/article>/g) || [];
  if (!blocks.length) throw Error("Localized Blog index has no card blocks: " + locale);
  const bySlug = new Map(), originalOrder = [];
  for (const block of blocks) {
    const slug = /href="\/blog\/([^/]+)\//.exec(block)?.[1];
    if (slug && !bySlug.has(slug)) { bySlug.set(slug, block); originalOrder.push(slug); }
  }
  for (const [slug, card] of cards) bySlug.set(slug, card);
  const ordered = [];
  for (const slug of sourceOrder) if (bySlug.has(slug)) ordered.push(slug);
  for (const slug of originalOrder) if (!ordered.includes(slug)) ordered.push(slug);
  if (ordered.length !== bySlug.size || ordered.length !== blocks.length) throw Error("Localized Blog index card identity is ambiguous: " + locale);
  const first = html.indexOf(blocks[0]), last = html.lastIndexOf(blocks[blocks.length - 1]);
  if (first < 0 || last < first) throw Error("Localized Blog index card range invalid: " + locale);
  const end = last + blocks[blocks.length - 1].length;
  return html.slice(0, first) + ordered.map(slug => bySlug.get(slug)).join("\n") + html.slice(end);
}

export async function onRequestPost(context) {
  const denied = await authorized(context);
  if (denied) return denied;
  let input; try { input = await context.request.json(); } catch { return reply({ error: "Invalid JSON" }, 400); }
  if (input?.confirm !== "20261105-b2b-refresh") return reply({ error: "Fixed confirmation string required" }, 400);
  const db = context.env.XUYI_DB;
  await ensureBlogSchema(db); await ensureTranslationSchema(db);
  const existing = {}, statements = [];
  for (let i = 0; i < TARGET_ORDER.length; i++) {
    const slug = TARGET_ORDER[i], row = await db.prepare("SELECT status,content_json,updated_at FROM xuyi_blog_posts WHERE slug=?").bind(slug).first();
    if (row?.status !== "published") return reply({ error: "Published D1 article required: " + slug }, 409);
    let post; try { post = JSON.parse(row.content_json || "{}"); } catch { return reply({ error: "Invalid D1 JSON: " + slug }, 409); }
    const patch = PATCHES[slug].en;
    post.title = patch.title; post.description = patch.description; post.primary_keyword = patch.primary; post.secondary_keywords = patch.secondary; post.updated = "2026-11-05";
    if (!String(post.intro || "").includes(patch.introSuffix)) post.intro = String(post.intro || "").trim() + " " + patch.introSuffix;
    if (!String(post.sections?.[0]?.paragraph || "").includes(patch.firstSuffix)) post.sections[0].paragraph = String(post.sections[0].paragraph || "").trim() + " " + patch.firstSuffix;
    try { validatePost(slug, post); } catch (error) { return reply({ error: String(error.message || error) }, 400); }
    existing[slug] = { row, old: JSON.parse(row.content_json || "{}"), next: post };
  }
  const liveOrder = ((await db.prepare("SELECT slug FROM xuyi_blog_posts WHERE status='published' ORDER BY COALESCE(published_at,updated_at) DESC,slug ASC").all()).results || []).map(x => x.slug);
  const sourceOrder = [...TARGET_ORDER, ...liveOrder.filter(slug => !TARGET_ORDER.includes(slug))];
  let postsWritten = 0;
  for (let i = 0; i < TARGET_ORDER.length; i++) {
    const slug = TARGET_ORDER[i], item = existing[slug];
    if (JSON.stringify(item.old) !== JSON.stringify(item.next) || !String(item.row.updated_at || "").startsWith("2026-11-05")) {
      statements.push(db.prepare("UPDATE xuyi_blog_posts SET content_json=?,updated_at=datetime(CURRENT_TIMESTAMP,?) WHERE slug=? AND status='published'")
        .bind(JSON.stringify(item.next), "+" + String(TARGET_ORDER.length - i) + " seconds", slug));
      postsWritten++;
    }
  }
  let translationsWritten = 0, indexRowsWritten = 0;
  for (const locale of LOCALES) {
    const indexRow = await db.prepare("SELECT translated_json FROM xuyi_translation_overrides WHERE resource_id='page:/blog/' AND locale=?").bind(locale).first();
    if (!indexRow) return reply({ error: "Localized Blog index override missing: " + locale }, 409);
    let index; try { index = JSON.parse(indexRow.translated_json || "{}"); } catch { return reply({ error: "Invalid localized Blog index JSON: " + locale }, 409); }
    const cards = new Map();
    for (const slug of TARGET_ORDER) {
      const detailRow = await db.prepare("SELECT translated_json FROM xuyi_translation_overrides WHERE resource_id=? AND locale=?").bind("page:/blog/" + slug + "/", locale).first();
      if (!detailRow) return reply({ error: "Localized detail override missing: " + slug + " " + locale }, 409);
      let detail; try { detail = JSON.parse(detailRow.translated_json || "{}"); } catch { return reply({ error: "Invalid localized detail JSON: " + slug + " " + locale }, 409); }
      const patch = PATCHES[slug][locale];
      const nextHtml = patchDetailHtml(detail.mainHtml, patch, slug, locale);
      const nextDetail = { ...detail, title: patch.title, description: patch.description, mainHtml: nextHtml };
      if (JSON.stringify(detail) !== JSON.stringify(nextDetail)) {
        statements.push(db.prepare("UPDATE xuyi_translation_overrides SET translated_json=?,reviewed_at=CURRENT_TIMESTAMP WHERE resource_id=? AND locale=?")
          .bind(JSON.stringify(nextDetail), "page:/blog/" + slug + "/", locale));
        translationsWritten++;
      }
      const blocks = String(index.mainHtml || "").match(/<article class="news-card">[\s\S]*?<\/article>/g) || [];
      const currentCard = blocks.find(block => block.includes('href="/blog/' + slug + '/"'));
      if (!currentCard) return reply({ error: "Localized index card missing: " + slug + " " + locale }, 409);
      cards.set(slug, patchCardHtml(currentCard, patch, slug, locale));
    }
    const nextIndex = { ...index, mainHtml: orderIndex(index.mainHtml, cards, sourceOrder, locale) };
    if (JSON.stringify(index) !== JSON.stringify(nextIndex)) {
      statements.push(db.prepare("UPDATE xuyi_translation_overrides SET translated_json=?,reviewed_at=CURRENT_TIMESTAMP WHERE resource_id='page:/blog/' AND locale=?")
        .bind(JSON.stringify(nextIndex), locale));
      indexRowsWritten++;
    }
  }
  if (!statements.length) return reply({ success: true, alreadyCurrent: true, targets: TARGET_ORDER });
  await db.batch(statements);
  const revision = await bumpPublishRevision(db);
  return reply({ success: true, postsWritten, translationsWritten, indexRowsWritten, targets: TARGET_ORDER, ...revision });
}
