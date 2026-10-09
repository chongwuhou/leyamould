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
  if (clean(env.CF_ACCOUNT_ID) && clean(env.CF_ACCOUNT_ID) !== accountId) return false;
  if (clean(env.CF_PAGES_PROJECT) && clean(env.CF_PAGES_PROJECT) !== projectName) return false;
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

export async function authorizedBuildRequest(request, env) {
  if (await authorizeAdminRequest(request, env)) return true;
  return verifyCloudflareProjectToken(bearerToken(request), env);
}