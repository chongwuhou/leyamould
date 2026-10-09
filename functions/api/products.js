// B2B public product directory. Draft records must NEVER be returned.
const headers = { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" };
export async function onRequestGet({ request, env }) {
  if (!env.XUYI_DB) return new Response(JSON.stringify({ error: "Catalog temporarily unavailable" }), { status: 503, headers });
  const url = new URL(request.url);
  const category = url.searchParams.get("category") || "";
  const limit = Math.min(48, Math.max(1, Number.parseInt(url.searchParams.get("limit") || "24", 10) || 24));
  if (category && !/^[a-z0-9-]{1,72}$/.test(category)) return new Response(JSON.stringify({ error: "Invalid category" }), { status: 400, headers });
  try {
    const query = category
      ? env.XUYI_DB.prepare("SELECT id, source_model AS model, name_en AS name, category_slug AS category, description_en AS description FROM products WHERE approval_state = 'published' AND category_slug = ? ORDER BY source_model LIMIT ?").bind(category, limit)
      : env.XUYI_DB.prepare("SELECT id, source_model AS model, name_en AS name, category_slug AS category, description_en AS description FROM products WHERE approval_state = 'published' ORDER BY category_slug, source_model LIMIT ?").bind(limit);
    const rows = await query.all();
    return new Response(JSON.stringify({ products: rows.results || [], count: (rows.results || []).length }), { headers });
  } catch (e) {
    return new Response(JSON.stringify({ error: "Catalog temporarily unavailable" }), { status: 503, headers });
  }
}