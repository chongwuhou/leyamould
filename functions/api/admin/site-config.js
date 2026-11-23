import { authorizedBuildRequest } from "../../_shared/build-auth.js";

const clean = (value) => String(value ?? "").trim();

const DEFAULT_REDIRECTS = [["/about", "/about/"], ["/blog", "/blog/"], ["/contact", "/contact/"], ["/products", "/products/"]].map(([sourcePath,targetPath])=>({sourcePath,targetPath,statusCode:301}));

const LEGACY_DEFAULT_NAVIGATION = [
  {
    "id": "home",
    "parentId": "",
    "label": "Home",
    "url": "/",
    "sortOrder": 10,
    "newWindow": false
  },
  {
    "id": "products",
    "parentId": "",
    "label": "Products",
    "url": "/products/",
    "sortOrder": 20,
    "newWindow": false
  },
  {
    "id": "category-sports-water-bottles",
    "parentId": "products",
    "label": "Plastic Sports Water Bottles",
    "url": "/collections/sports-water-bottles/",
    "sortOrder": 10,
    "newWindow": false
  },
  {
    "id": "category-large-capacity-water-jugs",
    "parentId": "products",
    "label": "Large Capacity Water Jugs",
    "url": "/collections/large-capacity-water-jugs/",
    "sortOrder": 20,
    "newWindow": false
  },
  {
    "id": "category-kids-water-bottles",
    "parentId": "products",
    "label": "Kids Plastic Water Bottles",
    "url": "/collections/kids-water-bottles/",
    "sortOrder": 30,
    "newWindow": false
  },
  {
    "id": "category-plastic-shaker-bottles",
    "parentId": "products",
    "label": "Plastic Shaker Bottles",
    "url": "/collections/plastic-shaker-bottles/",
    "sortOrder": 40,
    "newWindow": false
  },
  {
    "id": "capabilities",
    "parentId": "",
    "label": "Capabilities",
    "url": "/capabilities/",
    "sortOrder": 30,
    "newWindow": false
  },
  {
    "id": "cap-custom-water-bottle",
    "parentId": "capabilities",
    "label": "Custom Water Bottle",
    "url": "/capabilities/custom-water-bottle/",
    "sortOrder": 10,
    "newWindow": false
  },
  {
    "id": "cap-custom-molding",
    "parentId": "capabilities",
    "label": "Custom Molding",
    "url": "/capabilities/custom-molding/",
    "sortOrder": 20,
    "newWindow": false
  },
  {
    "id": "cap-custom-logo",
    "parentId": "capabilities",
    "label": "Custom Logo",
    "url": "/capabilities/custom-logo/",
    "sortOrder": 30,
    "newWindow": false
  },
  {
    "id": "cap-custom-graphics",
    "parentId": "capabilities",
    "label": "Custom Graphics",
    "url": "/capabilities/custom-graphics/",
    "sortOrder": 40,
    "newWindow": false
  },
  {
    "id": "cap-custom-manufacturing",
    "parentId": "capabilities",
    "label": "Custom Manufacturing",
    "url": "/capabilities/custom-manufacturing/",
    "sortOrder": 50,
    "newWindow": false
  },
  {
    "id": "cap-custom-packaging",
    "parentId": "capabilities",
    "label": "Custom Packaging",
    "url": "/capabilities/custom-packaging/",
    "sortOrder": 60,
    "newWindow": false
  },
  {
    "id": "about",
    "parentId": "",
    "label": "About",
    "url": "/about/",
    "sortOrder": 40,
    "newWindow": false
  },
  {
    "id": "why-us",
    "parentId": "",
    "label": "Why Us",
    "url": "/why-us/",
    "sortOrder": 50,
    "newWindow": false
  },
  {
    "id": "blog",
    "parentId": "",
    "label": "Blog",
    "url": "/blog/",
    "sortOrder": 60,
    "newWindow": false
  },
  {
    "id": "contact",
    "parentId": "",
    "label": "Contact Us",
    "url": "/contact/",
    "sortOrder": 70,
    "newWindow": false
  }
];

const DEFAULT_NAVIGATION = [
  {id:"home",parentId:"",label:"Home",url:"/",sortOrder:10,newWindow:false},
  {id:"about",parentId:"",label:"About Us",url:"/about/",sortOrder:20,newWindow:false},
  {id:"products",parentId:"",label:"Cap Mould",url:"/Plastic-cap-mold.html",sortOrder:30,newWindow:false},
  {id:"product-water",parentId:"products",label:"Mineral Water Cap Mould",url:"/product/Mineral-Water-Closure-cap-Molds.html",sortOrder:10,newWindow:false},
  {id:"product-oil",parentId:"products",label:"Edible Oil Cap Mould",url:"/product/Oil-bottle-cap-mould.html",sortOrder:20,newWindow:false},
  {id:"product-flip",parentId:"products",label:"Flip top caps mould",url:"/product/Flip-top-caps-mould.html",sortOrder:30,newWindow:false},
  {id:"product-engine",parentId:"products",label:"Engine Oil Cap Mould",url:"/product/Engine-Oil-Cap-Mould.html",sortOrder:40,newWindow:false},
  {id:"product-food",parentId:"products",label:"Food Packaging Cap Mould",url:"/product/Food-Packaging-Cap-Mould.html",sortOrder:50,newWindow:false},
  {id:"product-medical",parentId:"products",label:"Medical Cap Mould",url:"/product/Medical-Cap-Mould.html",sortOrder:60,newWindow:false},
  {id:"product-personal",parentId:"products",label:"Personal Care Cap Mould",url:"/product/Personal-Care-Cap-Mould.html",sortOrder:70,newWindow:false},
  {id:"product-functional",parentId:"products",label:"Functional Cap Mould (Combination)",url:"/product/Functional-Cap-Mould.html",sortOrder:80,newWindow:false},
  {id:"product-handle",parentId:"products",label:"Plastic Handle mould",url:"/product/Plastic-Handle-Cap-mould.html",sortOrder:90,newWindow:false},
  {id:"machine",parentId:"",label:"Machine",url:"/Bottle-Cap-Machine/Bottle-Cap-Machine.html",sortOrder:40,newWindow:false},
  {id:"samples",parentId:"",label:"Samples",url:"/samples/",sortOrder:50,newWindow:false},
  {id:"news",parentId:"",label:"News",url:"/news/",sortOrder:60,newWindow:false},
  {id:"video",parentId:"",label:"Video",url:"/video/",sortOrder:70,newWindow:false},
  {id:"contact",parentId:"",label:"Contact Us",url:"/contact/",sortOrder:80,newWindow:false}
];

const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS site_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`,
  `CREATE TABLE IF NOT EXISTS site_redirects (
    source_path TEXT PRIMARY KEY,
    target_path TEXT NOT NULL,
    status_code INTEGER NOT NULL DEFAULT 301 CHECK (status_code IN (301,302)),
    enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0,1)),
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`,
  `CREATE TABLE IF NOT EXISTS site_navigation (
    id TEXT PRIMARY KEY,
    parent_id TEXT,
    label TEXT NOT NULL,
    url TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0,1)),
    new_window INTEGER NOT NULL DEFAULT 0 CHECK (new_window IN (0,1)),
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

function validPath(value) {
  const path = clean(value);
  return path.startsWith("/") && !/[\r\n\s]/.test(path) && path.length <= 500;
}

function validTarget(value) {
  const target = clean(value);
  return (validPath(target) || /^https:\/\/[^\s]+$/i.test(target)) && target.length <= 1000;
}

function validNavUrl(value) {
  const url = clean(value);
  return validPath(url) || /^https:\/\/[^\s]+$/i.test(url) || /^(mailto|tel):[^\s]+$/i.test(url);
}

const RESERVED_REDIRECT_SOURCES = ["/api/","/admin/","/assets/","/media/","/_","/robots.txt","/sitemap.xml","/build-meta.json"];
function validRedirectSource(value) {
  const route=clean(value).toLowerCase();
  return validPath(value) && !route.startsWith("//") && !RESERVED_REDIRECT_SOURCES.some(x=>route.startsWith(x));
}
function validateRedirects(input) {
  if (!Array.isArray(input) || input.length > 500) throw new Error("Redirect list must contain 0-500 rows");
  const seen = new Set();
  return input.map((row) => {
    const sourcePath = clean(row?.sourcePath);
    const targetPath = clean(row?.targetPath);
    const statusCode = Number(row?.statusCode || 301);
    if (!validRedirectSource(sourcePath)) throw new Error("Invalid/reserved redirect source: " + sourcePath);
    if (!validTarget(targetPath)) throw new Error("Invalid redirect target for " + sourcePath);
    if (![301,302].includes(statusCode)) throw new Error("Redirect status must be 301 or 302");
    if (sourcePath === targetPath) throw new Error("Redirect cannot point to itself: " + sourcePath);
    if (seen.has(sourcePath)) throw new Error("Duplicate redirect source: " + sourcePath);
    seen.add(sourcePath);
    return { sourcePath, targetPath, statusCode };
  });
}

function validateNavigation(input) {
  if (!Array.isArray(input) || input.length < 1 || input.length > 150) throw new Error("Navigation must contain 1-150 items");
  const ids = new Set();
  const rows = input.map((row, index) => {
    const id = clean(row?.id);
    const parentId = clean(row?.parentId);
    const label = clean(row?.label);
    const url = clean(row?.url);
    const sortOrder = Number.isFinite(Number(row?.sortOrder)) ? Math.trunc(Number(row.sortOrder)) : (index + 1) * 10;
    if (!/^[a-z0-9][a-z0-9-]{0,79}$/i.test(id)) throw new Error("Invalid navigation id: " + id);
    if (ids.has(id)) throw new Error("Duplicate navigation id: " + id);
    if (!label || label.length > 80) throw new Error("Invalid navigation label for " + id);
    if (!validNavUrl(url)) throw new Error("Invalid navigation URL for " + id);
    ids.add(id);
    return { id, parentId, label, url, sortOrder, newWindow: Boolean(row?.newWindow) };
  });
  const byId = new Map(rows.map((row) => [row.id, row]));
  for (const row of rows) {
    if (row.parentId && !byId.has(row.parentId)) throw new Error("Unknown parent " + row.parentId + " for " + row.id);
    if (row.parentId === row.id) throw new Error("Navigation item cannot parent itself: " + row.id);
    const visited = new Set([row.id]);
    let cursor = row.parentId;
    while (cursor) {
      if (visited.has(cursor)) throw new Error("Navigation parent cycle detected at " + row.id);
      visited.add(cursor);
      cursor = byId.get(cursor)?.parentId || "";
    }
  }
  return rows;
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

async function load(db) {
  const [redirectsResult, navigationResult] = await db.batch([
    db.prepare(`SELECT source_path,target_path,status_code FROM site_redirects
      WHERE enabled=1 ORDER BY source_path`),
    db.prepare(`SELECT id,parent_id,label,url,sort_order,new_window FROM site_navigation
      WHERE enabled=1 ORDER BY COALESCE(parent_id,''),sort_order,id`)
  ]);
  const storedRedirects = (redirectsResult.results || []).map((row) => ({
    sourcePath: row.source_path, targetPath: row.target_path, statusCode: Number(row.status_code || 301)
  }));
  const storedNavigation = (navigationResult.results || []).map((row) => ({
    id: row.id, parentId: row.parent_id || "", label: row.label, url: row.url,
    sortOrder: Number(row.sort_order || 0), newWindow: Boolean(row.new_window)
  }));
  return {
    redirects: storedRedirects.length ? storedRedirects : DEFAULT_REDIRECTS,
    navigation: storedNavigation.length ? storedNavigation : DEFAULT_NAVIGATION,
    redirectsUsingDefaults: !storedRedirects.length,
    navigationUsingDefaults: !storedNavigation.length
  };
}

export async function onRequestGet(context) {
  const denied = await requireAdmin(context);
  if (denied) return denied;
  await ensureSchema(context.env.LEYA_DB);
  return response(await load(context.env.LEYA_DB));
}

export async function onRequestPost(context) {
  const denied = await requireAdmin(context);
  if (denied) return denied;
  const db = context.env.LEYA_DB;
  await ensureSchema(db);
  let payload;
  try { payload = await context.request.json(); }
  catch { return response({ error: "Invalid JSON" }, 400); }

  try {
    if (payload.action === "save_redirects") {
      const rows = validateRedirects(payload.redirects);
      const statements = [db.prepare("DELETE FROM site_redirects")];
      for (const row of rows) {
        statements.push(db.prepare(`INSERT INTO site_redirects
          (source_path,target_path,status_code,enabled,updated_at) VALUES(?,?,?,1,CURRENT_TIMESTAMP)`)
          .bind(row.sourcePath, row.targetPath, row.statusCode));
      }
      await db.batch(statements);
      return response({ saved: true, kind: "redirects", count: rows.length, ...(await queuePublish(db)) });
    }
    if (payload.action === "save_navigation") {
      const rows = validateNavigation(payload.navigation);
      const statements = [db.prepare("DELETE FROM site_navigation")];
      for (const row of rows) {
        statements.push(db.prepare(`INSERT INTO site_navigation
          (id,parent_id,label,url,sort_order,enabled,new_window,updated_at)
          VALUES(?,?,?,?,?,1,?,CURRENT_TIMESTAMP)`)
          .bind(row.id, row.parentId || null, row.label, row.url, row.sortOrder, row.newWindow ? 1 : 0));
      }
      await db.batch(statements);
      return response({ saved: true, kind: "navigation", count: rows.length, ...(await queuePublish(db)) });
    }
    return response({ error: "Unknown action" }, 400);
  } catch (error) {
    return response({ error: clean(error?.message || error) }, 400);
  }
}

