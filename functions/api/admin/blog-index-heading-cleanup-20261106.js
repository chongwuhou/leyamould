import { authorizedBuildRequest } from "../../_shared/build-auth.js";
import { ensureTranslationSchema } from "../../_shared/translation.js";
import { bumpPublishRevision, publishableLanguageCodes } from "../../_shared/site-settings.js";

const reply = (body, status = 200) => Response.json(body, {
  status,
  headers: { "cache-control": "no-store", "x-robots-tag": "noindex,nofollow,noarchive" }
});
const clean = value => String(value ?? "").replace(/\0/g, "");
const count = (value, needle) => String(value).split(needle).length - 1;

async function authorized(context) {
  if (!clean(context.env.ADMIN_TOKEN)) return reply({ error: "ADMIN_TOKEN not configured" }, 503);
  if (!(await authorizedBuildRequest(context.request, context.env))) return reply({ error: "Unauthorized" }, 401);
  if (!context.env.XUYI_DB) return reply({ error: "XUYI_DB binding missing" }, 503);
  return null;
}

function removeDuplicateHeading(mainHtml, locale) {
  const html = String(mainHtml || "");
  const marker = '<div class="section__head">';
  const grid = '<div class="blog-listing__grid">';
  const start = html.indexOf(marker);
  const end = html.indexOf(grid, start + marker.length);
  if (start < 0) {
    if (count(html, 'class="section__head"') === 0) return html;
    throw Error("Unrecognized localized Blog heading structure: " + locale);
  }
  if (end < 0 || end <= start) throw Error("Localized Blog grid is missing: " + locale);
  const next = html.slice(0, start) + html.slice(end);
  if (count(next, 'class="section__head"') !== 0 ||
      count(next, 'class="blog-listing__grid"') !== 1 ||
       count(next, '<article class="news-card">') < 1 ||
      count(next, "<h1>") !== 1 ||
      !next.includes('class="page-intro"')) {
    throw Error("Localized Blog heading cleanup validation failed: " + locale);
  }
  return next;
}

export async function onRequestPost(context) {
  const denied = await authorized(context);
  if (denied) return denied;
  let input;
  try { input = await context.request.json(); } catch { return reply({ error: "Invalid JSON" }, 400); }
  if (input?.confirm !== "20261106-blog-index-heading") {
    return reply({ error: "Fixed confirmation string required" }, 400);
  }

  const db = context.env.XUYI_DB;
  await ensureTranslationSchema(db);
  const locales = await publishableLanguageCodes(db, { excludeSource: true });
  const statements = [];
  let rowsWritten = 0;

  for (const locale of locales) {
    const row = await db.prepare(
      "SELECT translated_json FROM xuyi_translation_overrides WHERE resource_id='page:/blog/' AND locale=?"
    ).bind(locale).first();
    if (!row) return reply({ error: "Localized Blog index override missing: " + locale }, 409);

    let content;
    try { content = JSON.parse(row.translated_json || "{}"); }
    catch { return reply({ error: "Invalid localized Blog index JSON: " + locale }, 409); }

    const nextHtml = removeDuplicateHeading(content.mainHtml, locale);
    const next = { ...content, mainHtml: nextHtml };
    if (JSON.stringify(content) !== JSON.stringify(next)) {
      statements.push(db.prepare(
        "UPDATE xuyi_translation_overrides SET translated_json=?,reviewed_at=CURRENT_TIMESTAMP WHERE resource_id='page:/blog/' AND locale=?"
      ).bind(JSON.stringify(next), locale));
      rowsWritten++;
    }
  }

  if (!statements.length) return reply({ success: true, alreadyCurrent: true, locales });
  await db.batch(statements);
  const revision = await bumpPublishRevision(db);
  return reply({ success: true, rowsWritten, locales, ...revision });
}

