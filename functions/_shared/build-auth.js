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
  "/api/admin/brand-config", "/api/admin/home-banners", "/api/admin/site-config",
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

// The reviewed batch endpoint is the only write route that may accept the
// existing CI token after it proves access to this exact Pages project.
export async function authorizedReviewedBlogBatchRequest(request, env) {
  if (request.method !== "POST" || !new Set([
    "/api/admin/blog-batch",
    "/api/admin/blog-batch-20261020",
    "/api/admin/blog-batch-20261021",
    "/api/admin/blog-batch-20261022",
    "/api/admin/blog-batch-20261023",
    "/api/admin/blog-batch-20261024",
    "/api/admin/blog-batch-20261025",
    "/api/admin/blog-batch-20261026",
    "/api/admin/blog-batch-20261027",
    "/api/admin/blog-batch-20261028",
    "/api/admin/blog-batch-20261029",
    "/api/admin/blog-batch-20261030",
    "/api/admin/blog-batch-20261031",
    "/api/admin/blog-batch-20261101"
  ]).has(new URL(request.url).pathname)) return false;
  return verifyCloudflareProjectToken(bearerToken(request), env);
}

// Owner-reviewed, sha256-bound R2 images. This narrow CI exception cannot edit other content.
export async function authorizedReviewedBlogImageUploadRequest(request, env) {
 if (request.method!=="POST" || !["/api/admin/blog-images-20261030","/api/admin/blog-images-20261031","/api/admin/blog-images-20261101"].includes(new URL(request.url).pathname)) return false;
 return verifyCloudflareProjectToken(bearerToken(request),env);
}
// Narrow exception for the reviewed 101-model daily XLSX publisher. The
// existing GitHub CI Cloudflare token proves access to THIS XUYI project,
// but may only call the source-validated, append-only, three-per-day endpoint.
// Ordinary admin CRUD remains password/session protected as before.
// Exact one-time, owner-reviewed three-image R2/CMS upload. General admin writes remain restricted.
export async function authorizedReviewedBlogCoverRequest(request, env) {
 const url=new URL(request.url);
 if (request.method!=="POST" || url.pathname!=="/api/admin/blog-covers-20261029" ||
     !new Set(["upload","commit"]).has(url.searchParams.get("mode"))) return false;
 return verifyCloudflareProjectToken(bearerToken(request),env);
}
export async function authorizedDailyProductReviewRequest(request, env) {
  if (new URL(request.url).pathname !== "/api/admin/daily-product-reviews" ||
      !new Set(["GET", "POST"]).has(request.method)) return false;
  if (await authorizeAdminRequest(request, env)) return true;
  return verifyCloudflareProjectToken(bearerToken(request), env);
}

// Fixed, source-reviewed one-time migration: the caller may select a batch,
// but never supply arbitrary SEO copy or model names to a write endpoint.
export async function authorizedProductSeoPromotionRequest(request, env){
  if(new URL(request.url).pathname!=="/api/admin/product-seo-promotion-20261020"||
     !new Set(["GET","POST"]).has(request.method))return false;
  return verifyCloudflareProjectToken(bearerToken(request),env);
}