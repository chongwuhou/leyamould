import { authorizedCmsSourceMigrationRequest } from "../../_shared/build-auth.js";
import { ensureBlogSchema, normalizeBuyerDecisionTable } from "../../_shared/blog-cms.js";
import { bumpPublishRevision } from "../../_shared/site-settings.js";

const reply = (body, status = 200) => Response.json(body, {
  status,
  headers: { "cache-control": "no-store", "x-robots-tag": "noindex,nofollow,noarchive" }
});
const slugPattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

function sameJson(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
}

export async function onRequestPost(context) {
  if (!(await authorizedCmsSourceMigrationRequest(context.request, context.env))) {
    return reply({ error: "Unauthorized source migration request" }, 401);
  }
  const db = context.env.XUYI_DB;
  if (!db) return reply({ error: "XUYI_DB binding missing" }, 503);

  let payload;
  try { payload = await context.request.json(); }
  catch { return reply({ error: "Invalid JSON" }, 400); }

  const items = payload?.blogBuyerDecisionTables;
  if (!Array.isArray(items) || items.length < 1 || items.length > 200) {
    return reply({ error: "Expected 1–200 reviewed Blog buyer decision tables." }, 400);
  }

  try {
    await ensureBlogSchema(db);
    const seen = new Set();
    const updates = [];
    const skipped = [];
    const conflicts = [];
    for (const item of items) {
      const slug = String(item?.slug || "").trim().toLowerCase();
      if (!slugPattern.test(slug) || seen.has(slug)) {
        return reply({ error: "Invalid or duplicate Blog slug: " + slug }, 400);
      }
      seen.add(slug);
      const table = normalizeBuyerDecisionTable(item?.buyerDecisionTable);
      if (!table || table === false) {
        return reply({ error: "Missing buyerDecisionTable: " + slug }, 400);
      }
      const row = await db.prepare("SELECT status,content_json FROM xuyi_blog_posts WHERE slug=?").bind(slug).first();
      if (!row) {
        conflicts.push({ slug, reason: "D1 Blog row is missing" });
        continue;
      }
      if (row.status !== "published") {
        conflicts.push({ slug, reason: "D1 Blog row is not published" });
        continue;
      }
      let content;
      try { content = JSON.parse(row.content_json || "{}"); }
      catch { conflicts.push({ slug, reason: "D1 content_json is invalid" }); continue; }
      const current = content?.buyerDecisionTable;
      if (current === false) {
        skipped.push({ slug, reason: "owner suppression preserved" });
        continue;
      }
      if (current !== undefined && current !== null) {
        if (sameJson(normalizeBuyerDecisionTable(current), table)) skipped.push({ slug, reason: "already present" });
        else conflicts.push({ slug, reason: "existing owner value differs" });
        continue;
      }
      const next = { ...content, buyerDecisionTable: table };
      updates.push(db.prepare(
        "UPDATE xuyi_blog_posts SET content_json=?,updated_at=CURRENT_TIMESTAMP WHERE slug=? AND status='published' AND content_json=?"
      ).bind(JSON.stringify(next), slug, row.content_json));
    }

    if (conflicts.length) {
      return reply({ error: "D1 source migration stopped before writing; owner/conflict values were preserved.", conflicts }, 409);
    }
    const results = updates.length ? await db.batch(updates) : [];
    const failed = results.filter(row => Number(row?.meta?.changes || 0) !== 1).length;
    if (failed) return reply({ error: "D1 changed during conditional source migration; no retry was attempted.", failed }, 409);

    const changed = results.length;
    const revision = changed ? await bumpPublishRevision(db) : { revision: null };
    return reply({
      success: true,
      source: "reviewed-source-field-backfill",
      updated: changed,
      skipped: skipped.length,
      skippedDetails: skipped,
      publishRevision: revision.revision,
      d1Field: "xuyi_blog_posts.content_json.buyerDecisionTable"
    });
  } catch (error) {
    return reply({ error: "D1 source migration failed: " + String(error?.message || "unknown error").slice(0, 240) }, 500);
  }
}
