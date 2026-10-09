const clean = (value) => String(value ?? "").trim();
const encoder = new TextEncoder();
const PASSWORD_ITERATIONS = 210000;
const SESSION_TTL_SECONDS = 12 * 60 * 60;
const RECOVERY_TTL_SECONDS = 60 * 60;
const RESERVED_PATHS = new Set([
  "api","assets","blog","about-us","contact-us","brands","filter-types","replacement-filters",
  "es","de","pt","ru","tr","id","zh","favicon.ico","robots.txt","sitemap.xml",
  "admin","about","products","collections","capabilities","applications","features",
  "why-us","faq","contact","manufacturing","quality-control","shipping-logistics",
  "privacy-policy","request-sample","media"
]);

function constantTimeEqual(a, b) {
  const aa = encoder.encode(String(a || ""));
  const bb = encoder.encode(String(b || ""));
  let diff = aa.length ^ bb.length;
  const length = Math.max(aa.length, bb.length);
  for (let i = 0; i < length; i++) diff |= (aa[i % Math.max(aa.length, 1)] || 0) ^ (bb[i % Math.max(bb.length, 1)] || 0);
  return diff === 0;
}

function bytesToBase64Url(bytes) {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replaceAll("+", "-").replaceAll("/", "_").replace(/=+$/g, "");
}

function base64UrlToBytes(value) {
  const padded = String(value || "").replaceAll("-", "+").replaceAll("_", "/").padEnd(Math.ceil(String(value || "").length / 4) * 4, "=");
  const binary = atob(padded);
  return Uint8Array.from(binary, (ch) => ch.charCodeAt(0));
}

export function normalizeAdminPath(value) {
  const path = clean(value).replace(/^\/+|\/+$/g, "").toLowerCase();
  if (!/^[a-z0-9][a-z0-9-]{2,47}$/.test(path)) throw new Error("后台路径只能使用 3-48 位小写字母、数字和连字符");
  if (RESERVED_PATHS.has(path)) throw new Error("该后台路径属于系统保留路径，请换一个");
  return path;
}

export function defaultAdminSecurityConfig() {
  return { schemaVersion: 1, adminPath: "admin", password: null, passwordUpdatedAt: "" };
}

export function normalizeAdminSecurityConfig(input = {}) {
  const base = defaultAdminSecurityConfig();
  let adminPath = clean(input?.adminPath || base.adminPath);
  if (adminPath !== "admin") adminPath = normalizeAdminPath(adminPath);
  const password = input?.password && typeof input.password === "object" && clean(input.password.hash) && clean(input.password.salt)
    ? {
        algorithm: "PBKDF2-SHA256",
        iterations: Math.max(100000, Math.min(500000, Number(input.password.iterations || PASSWORD_ITERATIONS))),
        salt: clean(input.password.salt),
        hash: clean(input.password.hash)
      }
    : null;
  return {
    schemaVersion: 1,
    adminPath,
    password,
    passwordUpdatedAt: clean(input?.passwordUpdatedAt)
  };
}

async function ensureState(db) {
  await db.prepare(`CREATE TABLE IF NOT EXISTS site_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`).run();
}

export async function loadAdminSecurityConfig(db) {
  if (!db) return defaultAdminSecurityConfig();
  let row;
  try { row = await db.prepare("SELECT value FROM site_state WHERE key='admin_security_config'").first(); }
  catch { return defaultAdminSecurityConfig(); }
  if (!row?.value) return defaultAdminSecurityConfig();
  try { return normalizeAdminSecurityConfig(JSON.parse(row.value)); }
  catch { return defaultAdminSecurityConfig(); }
}

export async function saveAdminSecurityConfig(db, config) {
  const normalized = normalizeAdminSecurityConfig(config);
  await ensureState(db);
  await db.prepare(`INSERT INTO site_state(key,value,updated_at) VALUES('admin_security_config',?,CURRENT_TIMESTAMP)
    ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP`).bind(JSON.stringify(normalized)).run();
  return normalized;
}

async function pbkdf2(password, salt, iterations) {
  const key = await crypto.subtle.importKey("raw", encoder.encode(password), "PBKDF2", false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits({ name: "PBKDF2", hash: "SHA-256", salt, iterations }, key, 256);
  return new Uint8Array(bits);
}

export async function hashAdminPassword(password) {
  const value = String(password || "");
  if (value.length < 10) throw new Error("后台密码至少 10 位，建议 12 位以上");
  if (value.length > 128) throw new Error("后台密码不能超过 128 位");
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const hash = await pbkdf2(value, salt, PASSWORD_ITERATIONS);
  return {
    algorithm: "PBKDF2-SHA256",
    iterations: PASSWORD_ITERATIONS,
    salt: bytesToBase64Url(salt),
    hash: bytesToBase64Url(hash)
  };
}

export async function verifyAdminPassword(password, passwordConfig) {
  if (!passwordConfig?.hash || !passwordConfig?.salt) return false;
  const derived = await pbkdf2(String(password || ""), base64UrlToBytes(passwordConfig.salt), Number(passwordConfig.iterations || PASSWORD_ITERATIONS));
  return constantTimeEqual(bytesToBase64Url(derived), passwordConfig.hash);
}

async function hmac(keyText, message) {
  const key = await crypto.subtle.importKey("raw", encoder.encode(keyText), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return new Uint8Array(await crypto.subtle.sign("HMAC", key, encoder.encode(message)));
}

async function createSignedSession(kind, env, security, ttlSeconds) {
  const adminToken = clean(env.ADMIN_TOKEN);
  if (!adminToken) throw new Error("ADMIN_TOKEN is not configured");
  const now = Math.floor(Date.now() / 1000);
  const payload = bytesToBase64Url(encoder.encode(JSON.stringify({ v: 1, k: kind, iat: now, exp: now + ttlSeconds, n: crypto.randomUUID() })));
  const secret = kind === "password" ? adminToken + "|" + clean(security?.password?.hash) : adminToken + "|recovery";
  const signature = bytesToBase64Url(await hmac(secret, payload));
  return `adm1.${payload}.${signature}`;
}

export async function createPasswordSession(env, security) {
  if (!security?.password?.hash) throw new Error("后台密码尚未设置");
  return createSignedSession("password", env, security, SESSION_TTL_SECONDS);
}

export async function createRecoverySession(env, security) {
  return createSignedSession("recovery", env, security, RECOVERY_TTL_SECONDS);
}

async function verifySignedSession(token, env) {
  const [prefix, payload, signature] = String(token || "").split(".");
  if (prefix !== "adm1" || !payload || !signature) return false;
  let claims;
  try { claims = JSON.parse(new TextDecoder().decode(base64UrlToBytes(payload))); }
  catch { return false; }
  if (!claims?.exp || Number(claims.exp) < Math.floor(Date.now() / 1000)) return false;
  const adminToken = clean(env.ADMIN_TOKEN);
  if (!adminToken) return false;
  let secret;
  if (claims.k === "recovery") {
    secret = adminToken + "|recovery";
  } else if (claims.k === "password") {
    const security = await loadAdminSecurityConfig(env.XUYI_DB);
    if (!security.password?.hash) return false;
    secret = adminToken + "|" + security.password.hash;
  } else return false;
  const expected = bytesToBase64Url(await hmac(secret, payload));
  return constantTimeEqual(expected, signature);
}

export async function authorizeAdminRequest(request, env) {
  const supplied = clean(request.headers.get("authorization")).replace(/^Bearer\s+/i, "") || clean(request.headers.get("x-admin-token"));
  if (!supplied) return false;
  const adminToken = clean(env.ADMIN_TOKEN);
  if (adminToken && constantTimeEqual(supplied, adminToken)) return true;
  if (supplied.startsWith("adm1.")) return verifySignedSession(supplied, env);
  return false;
}

export function adminBuildConfig(config) {
  const normalized = normalizeAdminSecurityConfig(config);
  return { schemaVersion: 1, adminPath: normalized.adminPath };
}

export { constantTimeEqual };