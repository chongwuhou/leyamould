const GROUP_IMAGES = new Set(["oem-logo.webp","oem-color.webp","oem-artwork.webp","oem-packaging.webp","oem-tooling.webp","oem-sampling.webp","factory-raw.webp","factory-bottle-packing.webp","factory-final-pack.webp","factory-shipment.webp","plastic-injection-blow.webp","plastic-extrusion-blow.webp","plastic-lid-molding.webp","qa-color-box.webp","qa-print-life.webp","qa-temp-humidity.webp","qa-vibration.webp","qa-crush-edge.webp","qa-bursting.webp","freight-air-sea.webp","freight-door.webp","freight-express.webp","freight-warehouse.webp"]);
const CAPABILITY_IMAGES = new Set(["everich-plastic-bottles.webp","everich-engineering-drawing.webp","everich-production-lines.webp","everich-silk-printing.webp","kreat-print-transfer.webp","kreat-box-packaging.webp","gox-kids-custom-bottle.webp"]);
// Read-only XUYI catalog media proxy. Allowlisted paths from XUYI-owned source catalogs.
// Only XUYI media resources are allowed.
export async function onRequestGet({ params, env }) {
  if (!env.LEYA_ASSETS) return new Response("Media unavailable", {status:503});
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
  } else if (kind === "capability" && CAPABILITY_IMAGES.has(filename)) {
    key = "site-capabilities/" + filename;
  } else if (kind === "gallery" && /^(?:(?:2095|2099|5299|5340|8563)-0[1-3]|xuyi-g(?:01|02|03|04|05|09|10|12)-0[1-4])\.webp$/.test(filename)) {
    key = "site-gallery/" + filename;
  } else if (kind === "blog" && /^[a-z0-9_-]{20,70}\.(?:jpg|png|webp)$/.test(filename)) {
    key = "site-blog/" + filename;
  } else if (["product","page","shared"].includes(kind) && /^[a-f0-9]{32}\.(?:jpg|png|webp)$/.test(filename)) {
    key = "site-media/" + kind + "/" + filename;
  } else if (kind === "group" && /^[a-z0-9-]+\.webp$/.test(filename) && GROUP_IMAGES.has(filename)) {
    key = "site-preview/group/" + filename;
  } else {
    return new Response("Not found", {status:404});
  }
  try {
    const obj = await env.LEYA_ASSETS.get(key);
    if (!obj) return new Response("Not found", {status:404});
    return new Response(obj.body, {
      headers: {
        "Content-Type": ["blog","product","page","shared"].includes(kind) ? (filename.endsWith(".png") ? "image/png" : filename.endsWith(".jpg") ? "image/jpeg" : "image/webp") : "image/webp",
        "Cache-Control":"public,max-age=300",
        "X-Content-Type-Options":"nosniff"
      }
    });
  } catch {
    return new Response("Media unavailable", {status:503});
  }
}
