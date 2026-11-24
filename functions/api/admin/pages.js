// LEYA MOULD page/SEO registry. The public renderer owns the visual shell;
// this module owns reviewed route metadata and publish revisions.
import { authorizedBuildRequest } from "../../_shared/build-auth.js";
import { ensureProductSeo, canonicalProductSlug } from "../../_shared/product-seo.js";
import { MOULD_ROUTES, MOULD_PUBLIC_ROUTES } from "../../_shared/mould-routes.js";

const clean = value => String(value ?? "").trim();
const ROBOTS = new Set(["index,follow", "noindex,follow", "noindex,nofollow"]);
const PAGE_LABELS = new Map([
  ["/", "Homepage"], ["/about/", "About"], ["/products/", "Mould Categories"], ["/Plastic-cap-mold.html", "Mould Categories"], ["/capabilities/", "Capabilities"],
  ["/capabilities/mould-design/", "Mould Design & Engineering"], ["/capabilities/precision-manufacturing/", "Precision Manufacturing"], ["/capabilities/trial-sampling/", "Trial, Sampling & Optimisation"],
  ["/manufacturing/", "How We Work"], ["/quality-control/", "Quality Control"], ["/request-sample/", "Request a Sample"], ["/contact/", "Contact Us"], ["/samples/", "Plastic Cap Samples"], ["/news/", "News"],
  ["/news/Bottle-cap-molds.html", "Bottle Cap Mould News"], ["/Bottle-Cap-Machine/Bottle-Cap-Machine.html", "Bottle Cap Machine"], ["/video/", "Video"], ["/faq/", "FAQ"], ["/blog/", "Blog"], ["/privacy-policy/", "Privacy Policy"]
]);
for (const [model,route] of MOULD_PUBLIC_ROUTES) PAGE_LABELS.set(route, route.split("/").pop().replace(/\.html$/, ""));
const DEFAULT_PAGES = [...PAGE_LABELS].map(([route, label]) => ({ route, label, seoTitle: "", metaDescription: "", robots: "noindex,nofollow", sitemapEnabled: false }));
const KNOWN_ROUTES = new Set(DEFAULT_PAGES.map(page => page.route));
const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS site_state (key TEXT PRIMARY KEY, value TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)`,
  `CREATE TABLE IF NOT EXISTS site_pages (route TEXT PRIMARY KEY, label TEXT NOT NULL, seo_title TEXT NOT NULL DEFAULT '', meta_description TEXT NOT NULL DEFAULT '', robots TEXT NOT NULL DEFAULT 'noindex,nofollow' CHECK (robots IN ('index,follow','noindex,follow','noindex,nofollow')), sitemap_enabled INTEGER NOT NULL DEFAULT 0 CHECK (sitemap_enabled IN (0,1)), updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)`
];
const response = (data, status = 200) => Response.json(data, { status, headers: { "cache-control": "no-store", "x-robots-tag": "noindex, nofollow, noarchive" } });
async function requireAdmin(context) { if (!clean(context.env.ADMIN_TOKEN)) return response({ error: "ADMIN_TOKEN is not configured" }, 503); if (!(await authorizedBuildRequest(context.request, context.env))) return response({ error: "Unauthorized" }, 401); if (!context.env.LEYA_DB) return response({ error: "LEYA_DB binding missing" }, 503); return null; }
async function ensureSchema(db) { for (const sql of SCHEMA) await db.prepare(sql).run(); }
async function queuePublish(db) {
  const now = new Date().toISOString();
  await db.batch([db.prepare(`INSERT INTO site_state(key,value,updated_at) VALUES('publish_revision','1',CURRENT_TIMESTAMP) ON CONFLICT(key) DO UPDATE SET value=CAST(site_state.value AS INTEGER)+1,updated_at=CURRENT_TIMESTAMP`), db.prepare(`INSERT INTO site_state(key,value,updated_at) VALUES('publish_requested_at',?,CURRENT_TIMESTAMP) ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP`).bind(now)]);
  const row = await db.prepare("SELECT value FROM site_state WHERE key='publish_revision'").first(); return { revision: Number(row?.value || 0), requestedAt: now };
}
function validatePages(input, knownRoutes = KNOWN_ROUTES) {
  if (!Array.isArray(input) || !input.length) throw new Error("Page list must contain at least one configured page");
  const seen = new Set();
  return input.map(row => {
    const route = clean(row?.route), label = clean(row?.label), seoTitle = clean(row?.seoTitle), metaDescription = clean(row?.metaDescription), robots = clean(row?.robots) || "noindex,nofollow";
    if (!knownRoutes.has(route)) throw new Error("Unknown LEYA route: " + route);
    if (seen.has(route)) throw new Error("Duplicate managed page: " + route);
    if (!label || label.length > 120) throw new Error("Invalid page label: " + route);
    if (seoTitle.length > 90 || metaDescription.length > 240 || !ROBOTS.has(robots)) throw new Error("Invalid SEO metadata: " + route);
    seen.add(route); return { route, label, seoTitle, metaDescription, robots, sitemapEnabled: row?.sitemapEnabled !== false };
  });
}
async function loadPages(db) {
  const result = await db.prepare("SELECT route,label,seo_title,meta_description,robots,sitemap_enabled FROM site_pages ORDER BY route").all();
  const stored = (result.results || []).map(row => ({ route: row.route, label: row.label, seoTitle: row.seo_title || "", metaDescription: row.meta_description || "", robots: row.robots || "noindex,nofollow", sitemapEnabled: Boolean(row.sitemap_enabled) }));
  if (!stored.length) return { pages: DEFAULT_PAGES, usingDefaults: true };
  const byRoute = new Map(stored.map(row => [row.route, row])); const extras = stored.filter(row => !KNOWN_ROUTES.has(row.route));
  return { pages: [...DEFAULT_PAGES.map(fallback => ({ ...fallback, ...(byRoute.get(fallback.route) || {}) })), ...extras].sort((a, b) => a.route.localeCompare(b.route)), usingDefaults: false };
}
export async function onRequestGet(context) { const denied = await requireAdmin(context); if (denied) return denied; await ensureSchema(context.env.LEYA_DB); return response(await loadPages(context.env.LEYA_DB)); }
export async function onRequestPost(context) {
  const denied = await requireAdmin(context); if (denied) return denied; const db = context.env.LEYA_DB; await ensureSchema(db);
  let payload; try { payload = await context.request.json(); } catch { return response({ error: "Invalid JSON" }, 400); }
  if (payload.action !== "save_pages") return response({ error: "Unknown action" }, 400);
  try {
    const configured = (await db.prepare("SELECT route FROM site_pages").all()).results || [];
    const knownRoutes = new Set([...KNOWN_ROUTES, ...configured.map(row => String(row.route || ""))].filter(Boolean)); const pages = validatePages(payload.pages, knownRoutes);
    const prior = (await db.prepare("SELECT route,seo_title,meta_description FROM site_pages").all()).results || []; const priorByRoute = new Map(prior.map(row => [row.route, row])); const statements = []; await ensureProductSeo(db);
    for (const page of pages) {
      statements.push(db.prepare(`INSERT INTO site_pages(route,label,seo_title,meta_description,robots,sitemap_enabled,updated_at) VALUES(?,?,?,?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(route) DO UPDATE SET label=excluded.label,seo_title=excluded.seo_title,meta_description=excluded.meta_description,robots=excluded.robots,sitemap_enabled=excluded.sitemap_enabled,updated_at=CURRENT_TIMESTAMP`).bind(page.route, page.label, page.seoTitle, page.metaDescription, page.robots, page.sitemapEnabled ? 1 : 0));
      const old = priorByRoute.get(page.route);
      if (old && page.route.startsWith("/product/") && page.seoTitle && page.metaDescription && (old.seo_title !== page.seoTitle || old.meta_description !== page.metaDescription)) {
        const slug = canonicalProductSlug(page.route.split("/")[2].replace(/\.html$/, ""));
        statements.push(db.prepare(`INSERT INTO xuyi_product_seo(slug,locale,seo_title,meta_description,updated_at) VALUES(?,'en',?,?,CURRENT_TIMESTAMP) ON CONFLICT(slug,locale) DO UPDATE SET seo_title=excluded.seo_title,meta_description=excluded.meta_description,updated_at=CURRENT_TIMESTAMP`).bind(slug, page.seoTitle, page.metaDescription));
      }
    }
    await db.batch(statements); return response({ saved: true, count: pages.length, ...(await queuePublish(db)) });
  } catch (error) { return response({ error: clean(error?.message || error) }, 400); }
}
