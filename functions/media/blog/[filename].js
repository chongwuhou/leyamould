// Explicit public Blog R2 media route. D1 stores the public /media/blog/ path; R2 stores site-blog/.
const BLOG_FILENAME=/^[a-z0-9_-]{20,70}\.(?:jpg|png|webp)$/;

export async function onRequestGet({ params, env }) {
  if (!env.XUYI_ASSETS) return new Response("Media unavailable", { status: 503 });
  const filename = String(params?.filename || "");
  if (!BLOG_FILENAME.test(filename)) return new Response("Not found", { status: 404 });
  try {
    const object = await env.XUYI_ASSETS.get("site-blog/" + filename);
    if (!object) return new Response("Not found", { status: 404 });
    const type = filename.endsWith(".png") ? "image/png" : filename.endsWith(".jpg") ? "image/jpeg" : "image/webp";
    return new Response(object.body, {
      headers: {
        "Content-Type": type,
        "Cache-Control": "public,max-age=300",
        "X-Content-Type-Options": "nosniff"
      }
    });
  } catch {
    return new Response("Media unavailable", { status: 503 });
  }
}
