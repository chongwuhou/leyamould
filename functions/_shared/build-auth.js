import { authorizeAdminRequest } from "./admin-security.js";

const clean = (value) => String(value ?? "").trim();

function constantTimeEqual(a, b) {
  const aa = new TextEncoder().encode(a);
  const bb = new TextEncoder().encode(b);
  let diff = aa.length ^ bb.length;
  const length = Math.max(aa.length, bb.length);
  for (let i = 0; i < length; i++) {
    diff |= (aa[i % Math.max(aa.length, 1)] || 0) ^ (bb[i % Math.max(bb.length, 1)] || 0);
  }
  return diff === 0;
}

function bearerToken(request) {
  return clean(request.headers.get("authorization")).replace(/^Bearer\s+/i, "");
}

async function verifyCloudflareProjectToken(token, env) {
  if (!token) return false;
  // These two identifiers are public (not credentials), and pin the
  // authorization check to XUYI even when Pages variables are absent.
  const accountId = "a4032d0251103d6ef680b2aaddce1afc";
  const projectName = "xuyi-drinkware-site";
  // The Cloudflare GET below validates this exact project; Pages environment
  // variables are not a second, potentially stale source of truth.
  try {
    const response = await fetch(
      "https://api.cloudflare.com/client/v4/accounts/" + accountId +
      "/pages/projects/" + projectName,
      {
        headers: {
          authorization: "Bearer " + token,
          accept: "application/json"
        }
      }
    );
    if (!response.ok) return false;
    const payload = await response.json();
    return Boolean(payload?.success && payload?.result?.name === projectName);
  } catch {
    return false;
  }
}

// A Cloudflare project token proves access to deployment metadata, not
// permission to edit content or read customer records. Preserve the existing
// Demalong-style admin session for all writes and private admin modules.
const BUILD_READ_PATHS = new Set([
  "/api/build-snapshot", "/api/publish-state",
  "/api/admin/brand-config", "/api/admin/site-config",
  "/api/admin/pages", "/api/admin/product-content",
  "/api/admin/page-content", "/api/admin/page-translations"
]);

export async function authorizedBuildRequest(request, env) {
  if (await authorizeAdminRequest(request, env)) return true;
  if (request.method !== "GET" && request.method !== "HEAD") return false;
  const pathname = new URL(request.url).pathname;
  if (!BUILD_READ_PATHS.has(pathname)) return false;
  return verifyCloudflareProjectToken(bearerToken(request), env);
}