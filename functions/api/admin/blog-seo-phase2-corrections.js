import { authorizedReviewedBlogSeoPhase2Request } from "../../_shared/build-auth.js";
import { bumpPublishRevision } from "../../_shared/site-settings.js";

const BATCH_ID = "2026-11-17-blog-seo-phase2-translation-semantics-v2";
const REPAIRS = [
  {
    resourceId: "page:/blog/bpa-free-plastic-water-bottle-sourcing/",
    locale: "es",
    replacements: [["gorras deportivas", "botellas deportivas"]]
  },
  {
    resourceId: "page:/blog/plastic-bottle-material-selection/",
    locale: "es",
    replacements: [["gorras deportivas", "botellas deportivas"]]
  },
  {
    resourceId: "page:/blog/tritan-vs-pp-petg-pc/",
    locale: "es",
    replacements: [["gorras deportivas", "botellas deportivas"]]
  },
  {
    resourceId: "page:/blog/tritan-vs-pp-petg-pc/",
    locale: "pt",
    replacements: [["especificar it", "especificar"], ["depende depende", "depende"]]
  },
  {
    resourceId: "page:/blog/tritan-vs-pp-petg-pc/",
    locale: "ru",
    replacements: [
      ["спортивных кепок", "спортивных бутылок"],
      ["оба понятны, но не являются синонимами", "оба могут быть прозрачными, но не являются синонимами"]
    ]
  },
  {
    resourceId: "page:/blog/tritan-vs-pp-petg-pc/",
    locale: "tr",
    replacements: [["anlaşılır olabilir", "şeffaf olabilir"]]
  }
];
const RESOURCE_IDS = [...new Set(REPAIRS.map((repair) => repair.resourceId))];
const LOCALES = [...new Set(REPAIRS.map((repair) => repair.locale))];
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
const reply = (body, status = 200) => Response.json(body, {
  status,
  headers: { "cache-control": "no-store", "x-robots-tag": "noindex,nofollow,noarchive" }
});
const count = (value, part) => String(value).split(part).length - 1;
const keyFor = (resourceId, locale) => resourceId + "|" + locale;
async function sha256(value) {
  const bytes = new TextEncoder().encode(value);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map((item) => item.toString(16).padStart(2, "0")).join("");
}
function parsePayload(row) {
  try {
    const payload = JSON.parse(row?.translated_json || "{}");
    return payload && typeof payload === "object" ? payload : null;
  } catch {
    return null;
  }
}
function applyReplacements(payload, replacements) {
  const next = structuredClone(payload);
  let changedOccurrences = 0;
  for (const field of ["title", "description", "mainHtml"]) {
    if (typeof next[field] !== "string") continue;
    let value = next[field];
    for (const [oldText, newText] of replacements) {
      changedOccurrences += count(value, oldText);
      value = value.split(oldText).join(newText);
    }
    next[field] = value;
  }
  return { next, changedOccurrences };
}
export async function onRequestPost(context) {
  if (!(await authorizedReviewedBlogSeoPhase2Request(context.request, context.env))) {
    return reply({ error: "Unauthorized reviewed Blog SEO phase-two repair request" }, 401);
  }
  const db = context.env.XUYI_DB;
  if (!db) return reply({ error: "XUYI_DB binding missing" }, 503);
  try {
    await db.prepare(AUDIT_SCHEMA).run();
    const resourcePlaceholders = RESOURCE_IDS.map(() => "?").join(",");
    const localePlaceholders = LOCALES.map(() => "?").join(",");
    const query = "SELECT resource_id,locale,translated_json FROM xuyi_translation_overrides WHERE resource_id IN (" +
      resourcePlaceholders + ") AND locale IN (" + localePlaceholders + ")";
    const rows = (await db.prepare(query).bind(...RESOURCE_IDS, ...LOCALES).all()).results || [];
    const lookup = new Map(rows.map((row) => [keyFor(row.resource_id, row.locale), row]));
    const plans = [];
    for (const repair of REPAIRS) {
      const row = lookup.get(keyFor(repair.resourceId, repair.locale));
      if (!row) return reply({ error: "Missing D1 translation record: " + keyFor(repair.resourceId, repair.locale) }, 409);
      const beforePayload = parsePayload(row);
      if (!beforePayload) return reply({ error: "Invalid translated_json: " + keyFor(repair.resourceId, repair.locale) }, 409);
      const { next, changedOccurrences } = applyReplacements(beforePayload, repair.replacements);
      plans.push({
        ...repair,
        beforeJson: row.translated_json,
        afterJson: JSON.stringify(next),
        changedOccurrences
      });
    }
    const now = new Date().toISOString();
    const statements = [];
    for (const plan of plans) {
      if (plan.changedOccurrences > 0) {
        statements.push(db.prepare(
          "UPDATE xuyi_translation_overrides SET translated_json=?,reviewed_at=? WHERE resource_id=? AND locale=? AND translated_json=?"
        ).bind(plan.afterJson, now, plan.resourceId, plan.locale, plan.beforeJson));
      }
      statements.push(db.prepare(
        "INSERT OR IGNORE INTO xuyi_translation_repair_audit(batch_id,resource_id,locale,field,old_sha256,new_sha256,changed_occurrences) VALUES(?,?,?,?,?,?,?)"
      ).bind(
        BATCH_ID,
        plan.resourceId,
        plan.locale,
        "translated_json.title|description|mainHtml",
        await sha256(plan.beforeJson),
        await sha256(plan.afterJson),
        plan.changedOccurrences
      ));
    }
    const results = await db.batch(statements);
    const changedRecords = plans.filter((plan) => plan.changedOccurrences > 0).length;
    const changedOccurrences = plans.reduce((sum, plan) => sum + plan.changedOccurrences, 0);
    const afterRows = (await db.prepare(query).bind(...RESOURCE_IDS, ...LOCALES).all()).results || [];
    const afterLookup = new Map(afterRows.map((row) => [keyFor(row.resource_id, row.locale), row]));
    const remaining = [];
    for (const plan of plans) {
      const payload = parsePayload(afterLookup.get(keyFor(plan.resourceId, plan.locale)));
      if (!payload) return reply({ error: "Final D1 check failed: invalid translated_json for " + keyFor(plan.resourceId, plan.locale) }, 409);
      for (const [oldText] of plan.replacements) {
        for (const field of ["title", "description", "mainHtml"]) {
          if (typeof payload[field] === "string" && count(payload[field], oldText) > 0) {
            remaining.push({ resourceId: plan.resourceId, locale: plan.locale, field, oldText });
          }
        }
      }
    }
    if (remaining.length) return reply({ error: "Final D1 check failed: approved source fragments remain", remaining }, 409);
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
      updatedRecords: changedRecords,
      changedOccurrences,
      remainingEnglishFragments: 0,
      publishRevision,
      compareAndSwapResults: results.length
    });
  } catch (error) {
    return reply({ error: "D1 Blog SEO phase-two repair failed: " + String(error?.message || "unknown error").slice(0, 240) }, 500);
  }
}
