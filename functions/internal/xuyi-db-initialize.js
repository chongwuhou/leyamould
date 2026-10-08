// Temporary, bearer-authenticated, one-time XUYI D1 schema initializer.
// Delete from GitHub immediately after verification. No Demalong bindings are referenced.
const EXPECTED_SHA256 = "729b67a4f5e15dff451c129d121d3f947153aa40f60d1f4e8bc95447877c9c1f";
const statements = [
  "do not import internal supplier prices.\nCREATE TABLE IF NOT EXISTS products (\n  id TEXT PRIMARY KEY, source_model TEXT NOT NULL, name_en TEXT NOT NULL,\n  category_slug TEXT NOT NULL, description_en TEXT,\n  production_mode TEXT NOT NULL DEFAULT 'pending' CHECK(production_mode IN ('pending','in_house','partner')),\n  approval_state TEXT NOT NULL DEFAULT 'draft' CHECK(approval_state IN ('draft','review','published')),\n  source_ref TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP\n)",
  "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_slug,approval_state)",
  "CREATE TABLE IF NOT EXISTS variants (\n  id TEXT PRIMARY KEY, product_id TEXT NOT NULL REFERENCES products(id),\n  capacity_ml INTEGER, color TEXT, material_parts_json TEXT,\n  packing_json TEXT, image_key TEXT, status TEXT DEFAULT 'draft'\n)",
  "CREATE INDEX IF NOT EXISTS idx_variants_product ON variants(product_id)",
  "CREATE TABLE IF NOT EXISTS inquiries (\n  id TEXT PRIMARY KEY, source_url TEXT, product_id TEXT, source_model TEXT,\n  company_name TEXT NOT NULL, contact_email TEXT NOT NULL,\n  country TEXT, quantity INTEGER, requirements TEXT, language TEXT DEFAULT 'en',\n  status TEXT NOT NULL DEFAULT 'new', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP\n)",
  "CREATE INDEX IF NOT EXISTS idx_inquiries_created ON inquiries(created_at)",
  "CREATE TABLE IF NOT EXISTS import_jobs (\n  id TEXT PRIMARY KEY, source_type TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'staged',\n  record_count INTEGER NOT NULL DEFAULT 0, source_ref TEXT,\n  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP\n)"
];
async function sha256Hex(text) {
  const raw = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(raw)].map(v => v.toString(16).padStart(2,"0")).join("");
}
export async function onRequestPost({request,env}) {
  const auth = request.headers.get("Authorization") || "";
  if (!auth.startsWith("Bearer ") || await sha256Hex(auth.slice(7)) !== EXPECTED_SHA256) {
    return new Response("Forbidden", {status:403,headers:{"Cache-Control":"no-store"}});
  }
  if (!env.XUYI_DB) {
    return new Response("Missing XUYI_DB binding", {status:503,headers:{"Cache-Control":"no-store"}});
  }
  try {
    await env.XUYI_DB.batch(statements.map(sql => env.XUYI_DB.prepare(sql)));
    const res = await env.XUYI_DB.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('products','variants','inquiries','import_jobs') ORDER BY name").all();
    return new Response(JSON.stringify({success:true,db_binding:"XUYI_DB",tables:(res.results || []).map(v=>v.name)}), {status:200,headers:{"Content-Type":"application/json; charset=utf-8","Cache-Control":"no-store"}});
  } catch (err) {
    return new Response(JSON.stringify({success:false,error:String(err).slice(0,300)}), {status:500,headers:{"Content-Type":"application/json; charset=utf-8","Cache-Control":"no-store"}});
  }
}
export async function onRequestGet() {
  return new Response("Method Not Allowed", {status:405,headers:{"Cache-Control":"no-store"}});
}