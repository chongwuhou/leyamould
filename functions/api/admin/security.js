import { authorizeAdminRequest } from "../../_shared/admin-security.js";
import {
  hashAdminPassword,
  loadAdminSecurityConfig,
  normalizeAdminPath,
  saveAdminSecurityConfig
} from "../../_shared/admin-security.js";

const clean = (value) => String(value ?? "").trim();
const response = (data, status = 200) => Response.json(data, { status, headers: { "cache-control": "no-store", "x-robots-tag": "noindex, nofollow, noarchive" } });

async function bumpPublishRevision(db) {
  const now = new Date().toISOString();
  await db.batch([
    db.prepare(`INSERT INTO site_state(key,value,updated_at) VALUES('publish_revision','1',CURRENT_TIMESTAMP)
      ON CONFLICT(key) DO UPDATE SET value=CAST(site_state.value AS INTEGER)+1,updated_at=CURRENT_TIMESTAMP`),
    db.prepare(`INSERT INTO site_state(key,value,updated_at) VALUES('publish_requested_at',?,CURRENT_TIMESTAMP)
      ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP`).bind(now),
    db.prepare(`INSERT INTO site_state(key,value,updated_at) VALUES('publish_request_reason','admin-path-changed',CURRENT_TIMESTAMP)
      ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP`)
  ]);
  const row = await db.prepare("SELECT value FROM site_state WHERE key='publish_revision'").first();
  return { revision: Number(row?.value || 0), requestedAt: now };
}

async function guard(context) {
  if (!clean(context.env.ADMIN_TOKEN)) return response({ error: "ADMIN_TOKEN is not configured" }, 503);
  if (!(await authorizeAdminRequest(context.request, context.env))) return response({ error: "Unauthorized" }, 401);
  if (!context.env.XUYI_DB) return response({ error: "XUYI_DB binding missing" }, 503);
  return null;
}

export async function onRequestGet(context) {
  const denied = await guard(context); if (denied) return denied;
  const security = await loadAdminSecurityConfig(context.env.XUYI_DB);
  return response({
    adminPath: security.adminPath,
    passwordConfigured: Boolean(security.password?.hash),
    passwordUpdatedAt: security.passwordUpdatedAt || "",
    adminUrl: new URL("/" + security.adminPath + "/", context.request.url).toString(),
    recoveryTokenConfigured: Boolean(clean(context.env.ADMIN_TOKEN))
  });
}

export async function onRequestPost(context) {
  const denied = await guard(context); if (denied) return denied;
  let payload;
  try { payload = await context.request.json(); }
  catch { return response({ error: "Invalid JSON" }, 400); }
  const db = context.env.XUYI_DB;
  const security = await loadAdminSecurityConfig(db);
  try {
    if (payload.action === "set_password") {
      const password = String(payload.password || "");
      if (password !== String(payload.confirmPassword || "")) throw new Error("两次输入的密码不一致");
      const updated = await saveAdminSecurityConfig(db, {
        ...security,
        password: await hashAdminPassword(password),
        passwordUpdatedAt: new Date().toISOString()
      });
      return response({ saved: true, passwordConfigured: Boolean(updated.password?.hash), passwordUpdatedAt: updated.passwordUpdatedAt, sessionsInvalidated: true });
    }
    if (payload.action === "save_path") {
      const adminPath = clean(payload.adminPath) === "admin" ? "admin" : normalizeAdminPath(payload.adminPath);
      const languageRow = await db.prepare("SELECT value FROM site_state WHERE key='language_config'").first();
      if (languageRow?.value) {
        try {
          const languageConfig = JSON.parse(languageRow.value);
          const conflict = (Array.isArray(languageConfig?.languages) ? languageConfig.languages : [])
            .some((item) => item?.enabled !== false && clean(item?.pathPrefix).toLowerCase() === adminPath);
          if (conflict) throw new Error("后台路径与已启用语种 URL 前缀冲突，请换一个");
        } catch (error) {
          if (clean(error?.message).includes("冲突")) throw error;
        }
      }
      if (adminPath === security.adminPath) return response({ saved: true, unchanged: true, adminPath, adminUrl: new URL("/" + adminPath + "/", context.request.url).toString() });
      await saveAdminSecurityConfig(db, { ...security, adminPath });
      const publish = await bumpPublishRevision(db);
      return response({ saved: true, adminPath, adminUrl: new URL("/" + adminPath + "/", context.request.url).toString(), publishQueued: true, ...publish });
    }
    return response({ error: "Unknown action" }, 400);
  } catch (error) {
    return response({ error: clean(error?.message || error) }, 400);
  }
}
