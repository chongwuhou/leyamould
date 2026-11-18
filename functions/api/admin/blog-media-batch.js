import { authorizedReviewedBlogBatchRequest } from "../../_shared/build-auth.js";

const reply = (body, status = 200) => Response.json(body, {
  status,
  headers: { "cache-control": "no-store", "x-robots-tag": "noindex,nofollow,noarchive" }
});

function decodeReviewedMedia(item) {
  const path = String(item?.path || "");
  const prefix = "/media/blog/";
  const filename = path.startsWith(prefix) ? path.slice(prefix.length) : "";
  const contentType = String(item?.contentType || "");
  const encoded = String(item?.contentBase64 || "");
  if (!/^[a-z0-9_-]+[.]webp$/.test(filename) || contentType !== "image/webp" || !encoded || encoded.length > 500000 || !/^[A-Za-z0-9+/]+={0,2}$/.test(encoded)) {
    throw Error("Reviewed Blog media failed validation: " + path);
  }
  let binary;
  try { binary = atob(encoded); } catch { throw Error("Reviewed Blog media is not valid base64: " + path); }
  if (binary.length < 30000 || binary.length > 350 * 1024) throw Error("Reviewed Blog media size is outside the approved range: " + path);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) bytes[index] = binary.charCodeAt(index);
  return { path, key: "site-blog/" + filename, bytes, contentType };
}

export async function onRequestPost(context) {
  if (!(await authorizedReviewedBlogBatchRequest(context.request, context.env))) return reply({ error: "Unauthorized reviewed batch request" }, 401);
  if (!context.env.XUYI_ASSETS) return reply({ error: "XUYI_ASSETS binding missing" }, 503);
  let payload;
  try { payload = await context.request.json(); } catch { return reply({ error: "Invalid JSON" }, 400); }
  if (!Array.isArray(payload?.media) || payload.media.length < 1 || payload.media.length > 12) return reply({ error: "A reviewed Blog media batch is required" }, 400);
  const seen = new Set();
  const items = [];
  try {
    for (const raw of payload.media) {
      const item = decodeReviewedMedia(raw);
      if (seen.has(item.path)) throw Error("Duplicate reviewed Blog media path: " + item.path);
      seen.add(item.path);
      items.push(item);
    }
    const uploaded = [];
    const kept = [];
    for (const item of items) {
      const existing = await context.env.XUYI_ASSETS.head(item.key);
      if (existing) {
        if (existing.httpMetadata?.contentType && existing.httpMetadata.contentType !== item.contentType) throw Error("Existing Blog cover has a different content type: " + item.path);
        kept.push(item.path);
        continue;
      }
      await context.env.XUYI_ASSETS.put(item.key, item.bytes, { httpMetadata: { contentType: item.contentType }, customMetadata: { source: "xuyi-reviewed-blog-batch" } });
      uploaded.push(item.key);
    }
    return reply({ success: true, uploaded, kept, count: items.length });
  } catch (error) {
    return reply({ error: "R2 Blog media batch failed: " + String(error?.message || "unknown error").slice(0, 240) }, 500);
  }
}
