import { authorizedReviewedBlogTranslationRepairRequest } from "../../_shared/build-auth.js";
import { bumpPublishRevision } from "../../_shared/site-settings.js";

const BATCH_ID = "2026-11-05-blog-translation-repair";
const AUDIT_SCHEMA = `CREATE TABLE IF NOT EXISTS xuyi_translation_repair_audit (
  batch_id TEXT NOT NULL,
  resource_id TEXT NOT NULL,
  locale TEXT NOT NULL,
  field TEXT NOT NULL,
  old_sha256 TEXT NOT NULL,
  new_sha256 TEXT NOT NULL,
  changed_occurrences INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(batch_id, resource_id, locale)
)`;
const REPAIRS = [
  {
    route: "/blog/bottle-factory-rfq-template/", locale: "es", replacements: [
      ["wholesale buying guide →", "guía de compra mayorista →"],
      ["how MOQ affects pricing →", "cómo afecta el MOQ al precio →"],
      ["request a sample →", "solicitar una muestra →"],
      ["OEM/ODM services →", "servicios OEM/ODM →"]
    ]
  },
  {
    route: "/blog/can-you-put-hot-water-in-plastic-water-bottle/", locale: "es", replacements: [
      ["Plastic Water Bottle Compliance: Food-Contact Documents Buyers Should Request", "Cumplimiento de las botellas de agua de plástico: documentos de contacto alimentario que deben solicitar los compradores"],
      ["PC, Tritan, PP and PETG: Selecting Plastic Bottle Materials", "PC, Tritan, PP y PETG: cómo seleccionar los materiales para botellas de plástico"],
      ["BPA-Free Plastic Water Bottles: What Wholesale Buyers Must Verify", "Botellas de agua de plástico sin BPA: qué deben verificar los compradores mayoristas"]
    ]
  },
  {
    route: "/blog/can-you-put-hot-water-in-plastic-water-bottle/", locale: "pt", replacements: [
      ["Plastic Water Bottle Compliance: Food-Contact Documents Buyers Should Request", "Conformidade de garrafas de água de plástico: documentos de contato com alimentos que os compradores devem solicitar"],
      ["PC, Tritan, PP and PETG: Selecting Plastic Bottle Materials", "PC, Tritan, PP e PETG: como selecionar materiais para garrafas de plástico"],
      ["BPA-Free Plastic Water Bottles: What Wholesale Buyers Must Verify", "Garrafas de água de plástico sem BPA: o que os compradores por atacado devem verificar"]
    ]
  },
  {
    route: "/blog/can-you-put-hot-water-in-plastic-water-bottle/", locale: "ru", replacements: [
      ["Plastic Water Bottle Compliance: Food-Contact Documents Buyers Should Request", "Соответствие пластиковых бутылок для воды требованиям: документы для контакта с пищевыми продуктами, которые следует запросить покупателям"],
      ["PC, Tritan, PP and PETG: Selecting Plastic Bottle Materials", "PC, Tritan, PP и PETG: выбор материалов для пластиковых бутылок"],
      ["BPA-Free Plastic Water Bottles: What Wholesale Buyers Must Verify", "Пластиковые бутылки для воды без BPA: что должны проверить оптовые покупатели"]
    ]
  },
  {
    route: "/blog/can-you-put-hot-water-in-plastic-water-bottle/", locale: "tr", replacements: [
      ["Plastic Water Bottle Compliance: Food-Contact Documents Buyers Should Request", "Plastik su şişelerinde uygunluk: alıcıların talep etmesi gereken gıda temas belgeleri"],
      ["PC, Tritan, PP and PETG: Selecting Plastic Bottle Materials", "PC, Tritan, PP ve PETG: plastik şişe malzemelerini seçme rehberi"],
      ["BPA-Free Plastic Water Bottles: What Wholesale Buyers Must Verify", "BPA içermeyen plastik su şişeleri: toptan alıcıların doğrulaması gerekenler"]
    ]
  },
  {
    route: "/blog/why-does-reusable-water-bottle-smell-bad/", locale: "es", replacements: [
      ["Leakproof Water Bottle Lids: A Buyer Testing Checklist", "Tapas herméticas para botellas de agua: lista de pruebas para compradores"],
      ["Replacement Water Bottle Lids: Bulk Spare-Parts Guide", "Tapas de repuesto para botellas de agua: guía de piezas de recambio al por mayor"],
      ["Plastic Water Bottle Quality Control Checklist for Bulk Orders", "Lista de control de calidad de botellas de agua de plástico para pedidos al por mayor"]
    ]
  },
  {
    route: "/blog/why-does-reusable-water-bottle-smell-bad/", locale: "pt", replacements: [
      ["Leakproof Water Bottle Lids: A Buyer Testing Checklist", "Tampas à prova de vazamentos para garrafas de água: checklist de testes para compradores"],
      ["Replacement Water Bottle Lids: Bulk Spare-Parts Guide", "Tampas de reposição para garrafas de água: guia de peças de reposição no atacado"],
      ["Plastic Water Bottle Quality Control Checklist for Bulk Orders", "Checklist de controle de qualidade de garrafas de água de plástico para pedidos em atacado"]
    ]
  },
  {
    route: "/blog/why-does-reusable-water-bottle-smell-bad/", locale: "ru", replacements: [
      ["Leakproof Water Bottle Lids: A Buyer Testing Checklist", "Герметичные крышки для бутылок воды: список проверок для покупателей"],
      ["Replacement Water Bottle Lids: Bulk Spare-Parts Guide", "Сменные крышки для бутылок воды: руководство по оптовым запасным деталям"],
      ["Plastic Water Bottle Quality Control Checklist for Bulk Orders", "Чек-лист контроля качества пластиковых бутылок для оптовых заказов"]
    ]
  },
  {
    route: "/blog/why-does-reusable-water-bottle-smell-bad/", locale: "tr", replacements: [
      ["Leakproof Water Bottle Lids: A Buyer Testing Checklist", "Sızdırmaz su şişesi kapakları: alıcılar için test kontrol listesi"],
      ["Replacement Water Bottle Lids: Bulk Spare-Parts Guide", "Yedek su şişesi kapakları: toplu yedek parça rehberi"],
      ["Plastic Water Bottle Quality Control Checklist for Bulk Orders", "Toplu siparişler için plastik su şişesi kalite kontrol listesi"]
    ]
  }
];
const reply = (body, status = 200) => Response.json(body, {
  status,
  headers: { "cache-control": "no-store", "x-robots-tag": "noindex,nofollow,noarchive" }
});
const count = (value, part) => String(value).split(part).length - 1;

async function sha256(value) {
  const bytes = new TextEncoder().encode(value);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map((item) => item.toString(16).padStart(2, "0")).join("");
}

function parseMainHtml(row) {
  let payload;
  try { payload = JSON.parse(row.translated_json || "{}"); } catch { return null; }
  return payload && typeof payload.mainHtml === "string" ? payload.mainHtml : null;
}

export async function onRequestPost(context) {
  if (!(await authorizedReviewedBlogTranslationRepairRequest(context.request, context.env))) {
    return reply({ error: "Unauthorized reviewed translation repair request" }, 401);
  }
  const db = context.env.XUYI_DB;
  if (!db) return reply({ error: "XUYI_DB binding missing" }, 503);
  try {
    await db.prepare(AUDIT_SCHEMA).run();
    const resourceIds = [
      "page:/blog/bottle-factory-rfq-template/",
      "page:/blog/can-you-put-hot-water-in-plastic-water-bottle/",
      "page:/blog/why-does-reusable-water-bottle-smell-bad/"
    ];
    const locales = ["es", "pt", "ru", "tr"];
    const rows = (await db.prepare(
      "SELECT resource_id,locale,translated_json FROM xuyi_translation_overrides WHERE resource_id IN (?,?,?) AND locale IN (?,?,?,?)"
    ).bind(...resourceIds, ...locales).all()).results || [];
    const lookup = new Map(rows.map((row) => [row.resource_id + "|" + row.locale, row]));
    const plans = [];
    for (const repair of REPAIRS) {
      const resourceId = "page:" + repair.route;
      const row = lookup.get(resourceId + "|" + repair.locale);
      if (!row) return reply({ error: "Missing D1 translation record: " + resourceId + "|" + repair.locale }, 409);
      const before = parseMainHtml(row);
      if (before === null) return reply({ error: "Invalid translated_json.mainHtml: " + resourceId + "|" + repair.locale }, 409);
      const after = repair.replacements.reduce((text, pair) => text.split(pair[0]).join(pair[1]), before);
      plans.push({ ...repair, resourceId, before, after, changedOccurrences: repair.replacements.reduce((sum, pair) => sum + count(before, pair[0]), 0) });
    }
    const now = new Date().toISOString();
    const statements = [];
    let updateStatements = 0;
    for (const plan of plans) {
      for (const [oldText, newText] of plan.replacements) {
        statements.push(db.prepare(
          "UPDATE xuyi_translation_overrides SET translated_json=json_set(translated_json,'$.mainHtml',replace(json_extract(translated_json,'$.mainHtml'),?,?)),reviewed_at=? WHERE resource_id=? AND locale=? AND instr(json_extract(translated_json,'$.mainHtml'),?)>0"
        ).bind(oldText, newText, now, plan.resourceId, plan.locale, oldText));
        updateStatements++;
      }
    }
    for (const plan of plans) {
      statements.push(db.prepare(
        "INSERT OR IGNORE INTO xuyi_translation_repair_audit(batch_id,resource_id,locale,field,old_sha256,new_sha256,changed_occurrences) VALUES(?,?,?,?,?,?,?)"
      ).bind(BATCH_ID, plan.resourceId, plan.locale, "translated_json.mainHtml", await sha256(plan.before), await sha256(plan.after), plan.changedOccurrences));
    }
    const results = await db.batch(statements);
    const changedOccurrences = results.slice(0, updateStatements).reduce((sum, row) => sum + Number(row?.meta?.changes || 0), 0);
    const afterRows = (await db.prepare(
      "SELECT resource_id,locale,translated_json FROM xuyi_translation_overrides WHERE resource_id IN (?,?,?) AND locale IN (?,?,?,?)"
    ).bind(...resourceIds, ...locales).all()).results || [];
    const afterLookup = new Map(afterRows.map((row) => [row.resource_id + "|" + row.locale, row]));
    let remainingEnglishFragments = 0;
    for (const plan of plans) {
      const body = parseMainHtml(afterLookup.get(plan.resourceId + "|" + plan.locale) || {});
      if (body === null) return reply({ error: "Final D1 check failed: invalid translation body." }, 409);
      for (const [oldText, newText] of plan.replacements) {
        remainingEnglishFragments += count(body, oldText);
        if (count(plan.before, oldText) > 0 && count(body, newText) < count(plan.before, oldText)) {
          return reply({ error: "Final D1 check failed: replacement incomplete for " + plan.resourceId + "|" + plan.locale }, 409);
        }
      }
    }
    if (remainingEnglishFragments !== 0) return reply({ error: "Final D1 check failed: English fragments remain." }, 409);
    let publishRevision = 0;
    if (changedOccurrences > 0) {
      publishRevision = (await bumpPublishRevision(db)).revision;
    } else {
      const setting = await db.prepare("SELECT value FROM site_state WHERE key='publish_revision'").first();
      publishRevision = Number(setting?.value || 0);
    }
    return reply({
      success: true,
      batchId: BATCH_ID,
      checkedRecords: plans.length,
      updatedRecords: plans.filter((plan) => plan.changedOccurrences > 0).length,
      changedOccurrences,
      remainingEnglishFragments,
      auditRows: plans.length,
      publishRevision
    });
  } catch (error) {
    return reply({ error: "D1 translation repair failed: " + String(error?.message || "unknown error").slice(0, 240) }, 500);
  }
}
