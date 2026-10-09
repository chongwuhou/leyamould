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
  const accountId = clean(env.CF_ACCOUNT_ID);
  const projectName = clean(env.CF_PAGES_PROJECT);
  if (!accountId || !projectName) return false;
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