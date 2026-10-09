import {
  constantTimeEqual,
  createPasswordSession,
  createRecoverySession,
  loadAdminSecurityConfig,
  verifyAdminPassword
} from "../../_shared/admin-security.js";

const clean = (value) => String(value ?? "").trim();
const response = (data, status = 200) => Response.json(data, { status, headers: { "cache-control": "no-store", "x-robots-tag": "noindex, nofollow, noarchive" } });
const LOGIN_WINDOW_SECONDS = 15 * 60;
const LOGIN_MAX_FAILURES = 8;

async function ensureLoginSchema(db) {
  await db.prepare(`CREATE TABLE IF NOT EXISTS admin_login_attempts (
    ip_hash TEXT NOT NULL,
    attempted_at INTEGER NOT NULL
  )`).run();
  await db.prepare("CREATE INDEX IF NOT EXISTS idx_admin_login_attempts_ip_time ON admin_login_attempts(ip_hash,attempted_at)").run();
}

async function clientHash(request) {
  const ip = clean(request.headers.get("cf-connecting-ip")) || clean(request.headers.get("x-forwarded-for")).split(",")[0] || "unknown";
  const digest = new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(ip)));
  return [...digest].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

async function loginRateState(db, ipHash) {
  const now = Math.floor(Date.now() / 1000);
  await db.prepare("DELETE FROM admin_login_attempts WHERE attempted_at < ?").bind(now - 3600).run();
  const row = await db.prepare("SELECT COUNT(*) AS n, MIN(attempted_at) AS first_at FROM admin_login_attempts WHERE ip_hash=? AND attempted_at>=?")
    .bind(ipHash, now - LOGIN_WINDOW_SECONDS).first();
  const failures = Number(row?.n || 0);
  return { now, failures, limited: failures >= LOGIN_MAX_FAILURES, retryAfter: failures >= LOGIN_MAX_FAILURES ? Math.max(1, LOGIN_WINDOW_SECONDS - (now - Number(row?.first_at || now))) : 0 };
}

export async function onRequestGet(context) {
  if (!context.env.XUYI_DB) return response({ error: "XUYI_DB binding missing" }, 503);
  const security = await loadAdminSecurityConfig(context.env.XUYI_DB);
  return response({
    configured: Boolean(clean(context.env.ADMIN_TOKEN)),
    passwordConfigured: Boolean(security.password?.hash)
  });
}

export async function onRequestPost(context) {
  if (!clean(context.env.ADMIN_TOKEN)) return response({ error: "ADMIN_TOKEN is not configured" }, 503);
  if (!context.env.XUYI_DB) return response({ error: "XUYI_DB binding missing" }, 503);
  let payload;
  try { payload = await context.request.json(); }
  catch { return response({ error: "Invalid JSON" }, 400); }
  const password = String(payload?.password || "");
  if (!password || password.length > 256) return response({ error: "请输入后台密码" }, 400);
  await ensureLoginSchema(context.env.XUYI_DB);
  const ipHash = await clientHash(context.request);
  const rate = await loginRateState(context.env.XUYI_DB, ipHash);
  if (rate.limited) {
    return Response.json({ error: "登录失败次数过多，请稍后再试" }, {
      status: 429,
      headers: { "cache-control": "no-store", "x-robots-tag": "noindex, nofollow, noarchive", "retry-after": String(rate.retryAfter) }
    });
  }
  const security = await loadAdminSecurityConfig(context.env.XUYI_DB);
  if (constantTimeEqual(password, clean(context.env.ADMIN_TOKEN))) {
    await context.env.XUYI_DB.prepare("DELETE FROM admin_login_attempts WHERE ip_hash=?").bind(ipHash).run();
    return response({ ok: true, mode: "recovery", sessionToken: await createRecoverySession(context.env, security), expiresIn: 3600 });
  }
  if (await verifyAdminPassword(password, security.password)) {
    await context.env.XUYI_DB.prepare("DELETE FROM admin_login_attempts WHERE ip_hash=?").bind(ipHash).run();
    return response({ ok: true, mode: "password", sessionToken: await createPasswordSession(context.env, security), expiresIn: 43200 });
  }
  await context.env.XUYI_DB.prepare("INSERT INTO admin_login_attempts(ip_hash,attempted_at) VALUES(?,?)").bind(ipHash, rate.now).run();
  return response({ error: "密码不正确" }, 401);
}