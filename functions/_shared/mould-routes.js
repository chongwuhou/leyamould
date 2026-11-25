// LEYA MOULD route and category ownership.  This is the backend allow-list;
// the checked-in Python catalogue remains the visual/content fallback.
export const MOULD_MODELS = new Set([
  "mineral-water-closure-cap-molds", "oil-bottle-cap-mould", "flip-top-caps-mould",
  "engine-oil-cap-mould", "food-packaging-cap-mould", "medical-cap-mould",
  "personal-care-cap-mould", "functional-cap-mould", "plastic-handle-cap-mould",
  "five-gallon-water-cap-mould", "wine-cap-mould", "pet-preform-mould", "blow-bottle-mould"
]);
// The checked-in catalogue keeps the reference site's public filename casing.
// Admin/D1 records use the stable lowercase model slug; keep this mapping in
// one module so SEO, translations, snapshot filtering and admin links agree.
export const MOULD_PUBLIC_ROUTES = new Map([
  ["mineral-water-closure-cap-molds", "/product/Mineral-Water-Closure-cap-Molds.html"],
  ["oil-bottle-cap-mould", "/product/Oil-bottle-cap-mould.html"],
  ["flip-top-caps-mould", "/product/Flip-top-caps-mould.html"],
  ["engine-oil-cap-mould", "/product/Engine-Oil-Cap-Mould.html"],
  ["food-packaging-cap-mould", "/product/Food-Packaging-Cap-Mould.html"],
  ["medical-cap-mould", "/product/Medical-Cap-Mould.html"],
  ["personal-care-cap-mould", "/product/Personal-Care-Cap-Mould.html"],
  ["functional-cap-mould", "/product/Functional-Cap-Mould.html"],
  ["plastic-handle-cap-mould", "/product/Plastic-Handle-Cap-mould.html"],
  ["five-gallon-water-cap-mould", "/product/5-Gallon-Water-Cap-Mould.html"],
  ["wine-cap-mould", "/product/Wine-Cap-Mould.html"],
  ["pet-preform-mould", "/product/PET-Preform-Mould.html"],
  ["blow-bottle-mould", "/product/Blow-Bottle-Mould.html"]
]);
export function mouldRoute(model) { return MOULD_PUBLIC_ROUTES.get(String(model || "")) || "/product/" + String(model || "") + ".html"; }
export function mouldModelFromRoute(route) {
  const value=String(route || "");
  for (const [model,publicRoute] of MOULD_PUBLIC_ROUTES) {
    if (value===publicRoute || value==="/product/"+model+".html") return model;
  }
  return "";
}
export const MOULD_ROUTES = new Set([
  "/", "/about/", "/products/", "/Plastic-cap-mold.html", "/capabilities/",
  "/capabilities/mould-design/", "/capabilities/precision-manufacturing/",
  "/capabilities/trial-sampling/", "/manufacturing/", "/quality-control/",
  "/request-sample/", "/contact/", "/samples/", "/news/",
  "/news/Bottle-cap-molds.html", "/Bottle-Cap-Machine/Bottle-Cap-Machine.html",
  "/video/", "/faq/", "/blog/", "/privacy-policy/",
  ...[...MOULD_PUBLIC_ROUTES.values()],
  ...[...MOULD_MODELS].map(slug => "/product/" + slug + ".html")
]);
export const MANAGED_MODELS = MOULD_MODELS;
export const MANAGED_ROUTES = MOULD_ROUTES;

// Published category rows may be added from the LEYA CMS. Keep the static
// allow-list for the original catalogue, but validate new D1-backed categories
// by the same safe slug/route contract instead of requiring a code change.
export const DYNAMIC_MODEL_RE = /^[a-z0-9][a-z0-9-]{1,63}$/;
export const DYNAMIC_PRODUCT_ROUTE_RE = /^\/product\/[a-z0-9][a-z0-9-]{1,63}\.html$/;
export function isMouldModel(value) {
  return DYNAMIC_MODEL_RE.test(String(value || ""));
}
export function isMouldProductRoute(value) {
  return DYNAMIC_PRODUCT_ROUTE_RE.test(String(value || ""));
}
export function isMouldRoute(value) {
  const route = String(value || "");
  return MOULD_ROUTES.has(route) || isMouldProductRoute(route);
}

