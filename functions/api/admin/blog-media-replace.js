// Explicit owner-approved replacement for already-referenced Blog R2 media.
import { authorizedExplicitPublishRequest } from "../../_shared/build-auth.js";

const reply = (body, status = 200) => Response.json(body, {
  status,
  headers: { "cache-control": "no-store", "x-robots-tag": "noindex,nofollow,noarchive" }
});

function decodeMedia(item) {
  const path = String(item?.path || "");
  const prefix = "/media/blog/";
  const filename = path.startsWith(prefix) ? path.slice(prefix.length) : "";
  const encoded = String(item?.contentBase64 || "");
  if (!/^[a-z0-9_-]{20,70}\.(?:jpg|png|webp)$/.test(filename) ||
      String(item?.contentType || "") !== "image/webp" ||
      !encoded || encoded.length > 500000 ||
      !/^[A-Za-z0-9+/]+={0,2}$/.test(encoded)) {
    throw Error("Blog media replacement failed validation: " + path);
  }
  let binary;
  try { binary = atob(encoded); } catch { throw Error("Blog media replacement is not valid base64: " + path); }
  if (binary.length < 30000 || binary.length > 350 * 1024) throw Error("Blog media replacement size is outside the approved range: " + path);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) bytes[index] = binary.charCodeAt(index);
  return { path, key: "site-blog/" + filename, bytes };
}

export async function onRequestPost(context) {
  if (!(await authorizedExplicitPublishRequest(context.request, context.env))) return reply({ error: "Unauthorized Blog media replacement" }, 401);
  if (!context.env.LEYA_ASSETS) return reply({ error: "LEYA_ASSETS binding missing" }, 503);
  let payload;
  try { payload = await context.request.json(); } catch { return reply({ error: "Invalid JSON" }, 400); }
  if (!Array.isArray(payload?.media) || payload.media.length < 1 || payload.media.length > 12) return reply({ error: "A Blog media replacement batch is required" }, 400);
  const seen = new Set();
  try {
    const replaced = [];
    for (const raw of payload.media) {
      const item = decodeMedia(raw);
      if (seen.has(item.path)) throw Error("Duplicate Blog media replacement path: " + item.path);
      seen.add(item.path);
      await context.env.LEYA_ASSETS.put(item.key, item.bytes, {
        httpMetadata: { contentType: "image/webp" },
        customMetadata: { source: "xuyi-owner-reviewed-blog-media-replacement" }
      });
      replaced.push(item.path);
    }
    return reply({ success: true, replaced, count: replaced.length });
  } catch (error) {
    return reply({ error: "Blog media replacement failed: " + String(error?.message || "unknown error").slice(0, 240) }, 500);
  }
}
