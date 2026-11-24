// Read-only owner audit for D1 edits and release requests.
// The endpoint never exposes submissions, credentials or translation secrets.
import { authorizedBuildRequest } from "../../_shared/build-auth.js";
import { ensureLeyaSystemSchema } from "../../_shared/leya-system.js";

const reply = (body, status = 200) => Response.json(body, {
  status,
  headers: {
    "cache-control": "no-store",
    "x-robots-tag": "noindex,nofollow,noarchive"
  }
});

export async function onRequestGet(context) {
  if (!(await authorizedBuildRequest(context.request, context.env))) return reply({ error: "Unauthorized" }, 401);
  const db = context.env.LEYA_DB;
  if (!db) return reply({ error: "LEYA_DB binding missing" }, 503);
  const url = new URL(context.request.url);
  const limit = Math.min(200, Math.max(10, Number(url.searchParams.get("limit")) || 50));
  const resourceType = String(url.searchParams.get("resourceType") || "").trim().slice(0, 120);
  const resourceId = String(url.searchParams.get("resourceId") || "").trim().slice(0, 300);
  try {
    await ensureLeyaSystemSchema(db);
    const where = [];
    const bindings = [];
    if (resourceType) { where.push("resource_type=?"); bindings.push(resourceType); }
    if (resourceId) { where.push("resource_id=?"); bindings.push(resourceId); }
    const query = `SELECT id,actor,action,resource_type,resource_id,before_hash,after_hash,
      publish_revision,metadata_json,created_at FROM leya_content_audit
      ${where.length ? "WHERE " + where.join(" AND ") : ""}
      ORDER BY created_at DESC,id DESC LIMIT ?`;
    bindings.push(limit);
    const rows = (await db.prepare(query).bind(...bindings).all()).results || [];
    return reply({
      schemaVersion: 1,
      limit,
      items: rows.map((row) => {
        let metadata = {};
        try { metadata = JSON.parse(row.metadata_json || "{}"); } catch {}
        return { ...row, metadata };
      })
    });
  } catch (error) {
    return reply({ error: "LEYA audit unavailable", detail: String(error?.message || error).slice(0, 240) }, 503);
  }
}

