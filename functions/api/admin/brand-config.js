import { brandPublicPayload, loadBrandConfigFromD1, normalizeBrandConfig } from "../../_shared/brand-config.js";
import { authorizedBuildRequest } from "../../_shared/build-auth.js";

const clean = (value) => String(value ?? "").trim();

function response(data, status = 200) {
  return Response.json(data, {
    status,
    headers: {
      "cache-control": "no-store",
      "x-robots-tag": "noindex, nofollow, noarchive"
    }
  });
}

async function ensureState(db) {
  await db.prepare(`CREATE TABLE IF NOT EXISTS site_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`).run();
}

async function nextRevision(db) {
  const row = await db.prepare("SELECT value FROM site_state WHERE key='publish_revision'").first();
  return Number(row?.value || 0) + 1;
}

export async function onRequestGet(context) {
  if (!clean(context.env.ADMIN_TOKEN)) return response({ error: "ADMIN_TOKEN is not configured" }, 503);
  if (!(await authorizedBuildRequest(context.request, context.env))) return response({ error: "Unauthorized" }, 401);
  const db = context.env.LEYA_DB;
  if (!db) return response({ error: "LEYA_DB binding missing" }, 503);
  const stored = await loadBrandConfigFromD1(db);
  if (!stored) return response({ source:"leya-default",updatedAt:"",config:{
    identity:{legalName:"LEYA MOULD Co.,Ltd",displayName:"LEYA MOULD",textName:"LEYA MOULD",upperName:"LEYA MOULD",filterBrandName:"LEYA MOULD",acronym:"LM"},
    contact:{email:"amyhu@leyamould.com",phoneDisplay:"+86 136 0672 7715",phoneE164:"+8613606727715",whatsappUrl:"https://wa.me/8613606727715",address:"4-55,Xicheng New Village,Huangyan Taizhou,Zhejiang Province, China"},
    logos:{header:{src:"/favicon.svg",alt:"LEYA MOULD"},footer:{src:"/favicon.svg",alt:"LEYA MOULD"}},
    social:{},footer:{about:"Plastic moulds and tooling solutions for bottle, cap, preform and custom packaging projects.",contactHeading:"Contact LEYA MOULD",copyright:"LEYA MOULD"},
    seo:{home:{en:{title:"Plastic Mould Manufacturer in China | LEYA MOULD",description:"Plastic injection moulds and tooling solutions for bottle, cap, preform and custom packaging projects."}}}
  }});
  return response(brandPublicPayload(stored.config, stored.updatedAt));
}

export async function onRequestPost(context) {
  if (!clean(context.env.ADMIN_TOKEN)) return response({ error: "ADMIN_TOKEN is not configured" }, 503);
  if (!(await authorizedBuildRequest(context.request, context.env))) return response({ error: "Unauthorized" }, 401);
  const db = context.env.LEYA_DB;
  if (!db) return response({ error: "LEYA_DB binding missing" }, 503);
  await ensureState(db);
  let payload;
  try { payload = await context.request.json(); }
  catch { return response({ error: "Invalid JSON" }, 400); }
  try {
    const previous = await loadBrandConfigFromD1(db);
    const config = normalizeBrandConfig(payload.config);
    const revision = await nextRevision(db);
    const now = new Date().toISOString();
    await db.batch([
      db.prepare(`INSERT INTO site_state(key,value,updated_at) VALUES('brand_config',?,CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP`).bind(JSON.stringify(config)),
      db.prepare(`INSERT INTO site_state(key,value,updated_at) VALUES('publish_revision',?,CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP`).bind(String(revision)),
      db.prepare(`INSERT INTO site_state(key,value,updated_at) VALUES('publish_requested_at',?,CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP`).bind(now)
    ]);
    try {
      const previousDefault = previous?.config?.email?.defaultFromName || "";
      await db.prepare(`UPDATE form_smtp_settings
        SET from_name=?,updated_at=CURRENT_TIMESTAMP
        WHERE id=1 AND (from_name='' OR from_name=?)`)
        .bind(config.email.defaultFromName, previousDefault)
        .run();
    } catch {
      // The form schema may not be initialized on a brand-new site yet.
    }
    return response({ saved: true, revision, requestedAt: now, config });
  } catch (error) {
    return response({ error: clean(error?.message || error) }, 400);
  }
}
