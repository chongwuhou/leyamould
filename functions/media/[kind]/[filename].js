// Read-only XUYI catalog media proxy. Allowlisted paths from XUYI-owned source catalogs.
// No Demalong resource is referenced.
export async function onRequestGet({ params, env }) {
  if (!env.XUYI_ASSETS) return new Response("Media unavailable", {status:503});
  const kind = String(params.kind || "");
  const filename = String(params.filename || "");
  let key;
  if (kind === "excel" && /^row-\d{3}\.webp$/.test(filename)) {
    const row = Number(filename.slice(4,7));
    if (row < 3 || row > 78) return new Response("Not found", {status:404});
    key = "site-preview/excel/" + filename;
  } else if (kind === "ppt" && /^slide-\d{3}\.webp$/.test(filename)) {
    const slide = Number(filename.slice(6,9));
    if (!((slide >= 5 && slide <= 77) || (slide >= 91 && slide <= 96))) {
      return new Response("Not found", {status:404});
    }
    key = "catalog-staging/ppt/" + filename;
  } else {
    return new Response("Not found", {status:404});
  }
  try {
    const obj = await env.XUYI_ASSETS.get(key);
    if (!obj) return new Response("Not found", {status:404});
    return new Response(obj.body, {
      headers: {
        "Content-Type":"image/webp",
        "Cache-Control":"public,max-age=3600",
        "X-Content-Type-Options":"nosniff"
      }
    });
  } catch {
    return new Response("Media unavailable", {status:503});
  }
}
