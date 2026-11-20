import { authorizedBuildRequest } from "../../_shared/build-auth.js";
import {ensureProductSeo,canonicalProductSlug} from "../../_shared/product-seo.js";

const clean = (value) => String(value ?? "").trim();
const ROBOTS = new Set(["index,follow", "noindex,follow", "noindex,nofollow"]);

// Allowed routes originate from XUYI's checked-in route manifest, never unrelated product routes.
const DEFAULT_PAGES = [
  ["/about/", "About"],
  ["/applications/everyday-hydration/", "Everyday Water Bottles"],
  ["/applications/gym-sports/", "Gym & Sports Water Bottles"],
  ["/applications/kids-school/", "Kids & School Bottles"],
  ["/applications/outdoor-travel/", "Outdoor & Travel Drinkware"],
  ["/applications/promotional-gifts/", "Custom Promotional Bottles"],
  ["/blog/", "Blog"],
  ["/capabilities/custom-graphics/", "Custom Graphics & Colors"],
  ["/capabilities/custom-logo/", "Custom Logo & Branding"],
  ["/capabilities/custom-manufacturing/", "Custom Manufacturing"],
  ["/capabilities/custom-molding/", "Custom Molding"],
  ["/capabilities/custom-packaging/", "Custom Packaging"],
  ["/capabilities/custom-water-bottle/", "Custom Water Bottle"],
  ["/capabilities/", "Capabilities"],
  ["/capabilities/oem-odm/", "OEM / ODM Services"],
  ["/collections/kids-water-bottles/", "Kids Water Bottles"],
  ["/collections/large-capacity-water-jugs/", "Large Capacity Water Jugs"],
  ["/collections/plastic-shaker-bottles/", "Protein Shaker Bottles"],
  ["/collections/sports-water-bottles/", "Sports Water Bottles"],
  ["/contact/", "Contact Us"],
  ["/faq/", "FAQ"],
  ["/features/carry-handle/", "Carry-Handle Bottle Styles"],
  ["/features/flip-top/", "Flip-Top Bottle Styles"],
  ["/features/gradient-colors/", "Gradient Color Plastic Bottles"],
  ["/features/large-capacity/", "Large Capacity Plastic Bottles"],
  ["/features/straw-lid/", "Straw Lid Bottle Styles"],
  ["/", "Homepage"],
  ["/manufacturing/", "Manufacturing"],
  ["/privacy-policy/", "Privacy Policy"],
  ["/products/2095/", "Model 2095"],
  ["/products/2099/", "Model 2099"],
  ["/products/2100/", "Model 2100"],
  ["/products/2106/", "Model 2106"],
  ["/products/2108/", "Model 2108"],
  ["/products/2109/", "Model 2109"],
  ["/products/2209/", "Model 2209"],
  ["/products/2212/", "Model 2212"],
  ["/products/2215/", "Model 2215"],
  ["/products/2250/", "Model 2250"],
  ["/products/2270/", "Model 2270"],
  ["/products/2271/", "Model 2271"],
  ["/products/2280/", "Model 2280"],
  ["/products/2281/", "Model 2281"],
  ["/products/2282/", "Model 2282"],
  ["/products/2290/", "Model 2290"],
  ["/products/2291/", "Model 2291"],
  ["/products/2292/", "Model 2292"],
  ["/products/2302/", "Model 2302"],
  ["/products/2303/", "Model 2303"],
  ["/products/2305/", "Model 2305"],
  ["/products/2306-transparent/", "Model 2306-transparent"],
  ["/products/2306/", "Model 2306"],
  ["/products/2307-transparent/", "Model 2307-transparent"],
  ["/products/2307/", "Model 2307"],
  ["/products/2308-transparent/", "Model 2308-transparent"],
  ["/products/2308/", "Model 2308"],
  ["/products/2309/", "Model 2309"],
  ["/products/2310/", "Model 2310"],
  ["/products/2311/", "Model 2311"],
  ["/products/2312/", "Model 2312"],
  ["/products/2315/", "Model 2315"],
  ["/products/2316/", "Model 2316"],
  ["/products/2317/", "Model 2317"],
  ["/products/2318/", "Model 2318"],
  ["/products/2319/", "Model 2319"],
  ["/products/2350/", "Model 2350"],
  ["/products/2400-transparent/", "Model 2400-transparent"],
  ["/products/2400/", "Model 2400"],
  ["/products/2401-transparent/", "Model 2401-transparent"],
  ["/products/2401/", "Model 2401"],
  ["/products/2402/", "Model 2402"],
  ["/products/2403/", "Model 2403"],
  ["/products/2405/", "Model 2405"],
  ["/products/2406/", "Model 2406"],
  ["/products/2407/", "Model 2407"],
  ["/products/2408/", "Model 2408"],
  ["/products/2409/", "Model 2409"],
  ["/products/2410/", "Model 2410"],
  ["/products/2411/", "Model 2411"],
  ["/products/2412/", "Model 2412"],
  ["/products/2413/", "Model 2413"],
  ["/products/2416/", "Model 2416"],
  ["/products/2417/", "Model 2417"],
  ["/products/2418/", "Model 2418"],
  ["/products/2419/", "Model 2419"],
  ["/products/2458/", "Model 2458"],
  ["/products/2459/", "Model 2459"],
  ["/products/2470/", "Model 2470"],
  ["/products/2487/", "Model 2487"],
  ["/products/2501/", "Model 2501"],
  ["/products/2502/", "Model 2502"],
  ["/products/2505/", "Model 2505"],
  ["/products/2506/", "Model 2506"],
  ["/products/2507/", "Model 2507"],
  ["/products/2508/", "Model 2508"],
  ["/products/2509/", "Model 2509"],
  ["/products/2511/", "Model 2511"],
  ["/products/2512/", "Model 2512"],
  ["/products/2513/", "Model 2513"],
  ["/products/2514/", "Model 2514"],
  ["/products/2515/", "Model 2515"],
  ["/products/2516/", "Model 2516"],
  ["/products/2517/", "Model 2517"],
  ["/products/501/", "Model 501"],
  ["/products/502/", "Model 502"],
  ["/products/507/", "Model 507"],
  ["/products/509/", "Model 509"],
  ["/products/510/", "Model 510"],
  ["/products/5247/", "Model 5247"],
  ["/products/5248/", "Model 5248"],
  ["/products/5299/", "Model 5299"],
  ["/products/5340/", "Model 5340"],
  ["/products/6252/", "Model 6252"],
  ["/products/8563/", "Model 8563"],
  ["/products/", "All Products"],
  ["/quality-control/", "Quality Control"],
  ["/request-sample/", "Request a Sample"],
  ["/shipping-logistics/", "Shipping & Logistics"],
  ["/why-us/", "Why Us"]
].map(([route,label]) => ({
  route,label,seoTitle:"",metaDescription:"",
  robots:"noindex,nofollow",sitemapEnabled:false
}));
const KNOWN_ROUTES = new Set(DEFAULT_PAGES.map((page) => page.route));

const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS site_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`,
  `CREATE TABLE IF NOT EXISTS site_pages (
    route TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    seo_title TEXT NOT NULL DEFAULT '',
    meta_description TEXT NOT NULL DEFAULT '',
    robots TEXT NOT NULL DEFAULT 'index,follow'
      CHECK (robots IN ('index,follow','noindex,follow','noindex,nofollow')),
    sitemap_enabled INTEGER NOT NULL DEFAULT 1 CHECK (sitemap_enabled IN (0,1)),
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`
];

function response(data, status = 200) {
  return Response.json(data, {
    status,
    headers: {
      "cache-control": "no-store",
      "x-robots-tag": "noindex, nofollow, noarchive"
    }
  });
}

async function requireAdmin(context) {
  if (!clean(context.env.ADMIN_TOKEN)) return response({ error: "ADMIN_TOKEN is not configured" }, 503);
  if (!(await authorizedBuildRequest(context.request, context.env))) return response({ error: "Unauthorized" }, 401);
  if (!context.env.LEYA_DB) return response({ error: "LEYA_DB binding missing" }, 503);
  return null;
}

async function ensureSchema(db) {
  for (const sql of SCHEMA) await db.prepare(sql).run();
}

async function queuePublish(db) {
  const now = new Date().toISOString();
  await db.batch([
    db.prepare(`INSERT INTO site_state(key,value,updated_at) VALUES('publish_revision','1',CURRENT_TIMESTAMP)
      ON CONFLICT(key) DO UPDATE SET value=CAST(site_state.value AS INTEGER)+1,updated_at=CURRENT_TIMESTAMP`),
    db.prepare(`INSERT INTO site_state(key,value,updated_at) VALUES('publish_requested_at',?,CURRENT_TIMESTAMP)
      ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP`).bind(now)
  ]);
  const row = await db.prepare("SELECT value FROM site_state WHERE key='publish_revision'").first();
  return { revision: Number(row?.value || 0), requestedAt: now };
}

function validatePages(input, knownRoutes = KNOWN_ROUTES) {
  if (!Array.isArray(input) || !input.length) {
    throw new Error("Page list must contain at least one configured page");
  }
  const seen = new Set();
  return input.map((row) => {
    const route = clean(row?.route);
    const label = clean(row?.label);
    const seoTitle = clean(row?.seoTitle);
    const metaDescription = clean(row?.metaDescription);
    const robots = clean(row?.robots) || "noindex,nofollow";
    if (!knownRoutes.has(route)) throw new Error("Unknown configured page: " + route);
    if (seen.has(route)) throw new Error("Duplicate managed page: " + route);
    if (!label || label.length > 120) throw new Error("Invalid page label: " + route);
    if (seoTitle.length > 90) throw new Error("SEO title is too long: " + route);
    if (metaDescription.length > 240) throw new Error("Meta description is too long: " + route);
    if (!ROBOTS.has(robots)) throw new Error("Invalid robots value: " + route);
    seen.add(route);
    return {
      route, label, seoTitle, metaDescription, robots,
      sitemapEnabled: row?.sitemapEnabled !== false
    };
  });
}

async function loadPages(db) {
  const result = await db.prepare(`SELECT route,label,seo_title,meta_description,robots,sitemap_enabled
    FROM site_pages ORDER BY route`).all();
  const stored = (result.results || []).map((row) => ({
    route: row.route,
    label: row.label,
    seoTitle: row.seo_title || "",
    metaDescription: row.meta_description || "",
    robots: row.robots || "noindex,nofollow",
    sitemapEnabled: Boolean(row.sitemap_enabled)
  }));
  if (!stored.length) return { pages: DEFAULT_PAGES, usingDefaults: true };
  const byRoute = new Map(stored.map((row) => [row.route, row]));
  const extras=stored.filter(row=>!KNOWN_ROUTES.has(row.route));
  return {
    pages: [...DEFAULT_PAGES.map((fallback) => ({ ...fallback, ...(byRoute.get(fallback.route) || {}) })),...extras].sort((a,b)=>a.route.localeCompare(b.route)),
    usingDefaults: false
  };
}

export async function onRequestGet(context) {
  const denied = await requireAdmin(context);
  if (denied) return denied;
  await ensureSchema(context.env.LEYA_DB);
  return response(await loadPages(context.env.LEYA_DB));
}

export async function onRequestPost(context) {
  const denied = await requireAdmin(context);
  if (denied) return denied;
  const db = context.env.LEYA_DB;
  await ensureSchema(db);
  let payload;
  try { payload = await context.request.json(); }
  catch { return response({ error: "Invalid JSON" }, 400); }
  if (payload.action !== "save_pages") return response({ error: "Unknown action" }, 400);
  try {
    const configuredRows=(await db.prepare("SELECT route FROM site_pages").all()).results||[];
    const knownRoutes=new Set([...KNOWN_ROUTES,...configuredRows.map(row=>String(row.route||""))].filter(Boolean));
    const pages = validatePages(payload.pages,knownRoutes);
    // NEVER DELETE all of site_pages during an ordinary editor save: source
    // approved LO/G/transparent/new-model records would disappear forever.
    // Update the known rows and retain every other D1-owned route.
    const prior=(await db.prepare("SELECT route,seo_title,meta_description FROM site_pages").all()).results||[];
    const priorByRoute=new Map(prior.map(row=>[row.route,row]));
    const statements = [];
    await ensureProductSeo(db);
    for (const page of pages) {
      statements.push(db.prepare(`INSERT INTO site_pages
        (route,label,seo_title,meta_description,robots,sitemap_enabled,updated_at)
        VALUES(?,?,?,?,?,?,CURRENT_TIMESTAMP)
        ON CONFLICT(route) DO UPDATE SET label=excluded.label,
        seo_title=excluded.seo_title,meta_description=excluded.meta_description,
        robots=excluded.robots,sitemap_enabled=excluded.sitemap_enabled,
        updated_at=CURRENT_TIMESTAMP`)
        .bind(page.route, page.label, page.seoTitle, page.metaDescription, page.robots, page.sitemapEnabled ? 1 : 0));
      const old=priorByRoute.get(page.route);
      if(old&&page.route.startsWith("/products/")&&page.route!=="/products/"&&
         (old.seo_title!==page.seoTitle||old.meta_description!==page.metaDescription)&&
         page.seoTitle&&page.metaDescription){
        const slug=canonicalProductSlug(page.route.split("/")[2].replace(/---$/,"透明款"));
        statements.push(db.prepare("INSERT INTO xuyi_product_seo (slug,locale,seo_title,meta_description,updated_at) VALUES(?,'en',?,?,CURRENT_TIMESTAMP) "+
          "ON CONFLICT(slug,locale) DO UPDATE SET seo_title=excluded.seo_title,meta_description=excluded.meta_description,updated_at=CURRENT_TIMESTAMP")
          .bind(slug,page.seoTitle,page.metaDescription));
      }
    }
    await db.batch(statements);
    return response({ saved: true, count: pages.length, ...(await queuePublish(db)) });
  } catch (error) {
    return response({ error: clean(error?.message || error) }, 400);
  }
}
