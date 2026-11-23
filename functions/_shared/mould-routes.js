// LEYA MOULD route and category ownership.  This is the backend allow-list;
// the checked-in Python catalogue remains the visual/content fallback.
export const MOULD_MODELS = new Set([
  "mineral-water-closure-cap-molds", "oil-bottle-cap-mould", "flip-top-caps-mould",
  "engine-oil-cap-mould", "food-packaging-cap-mould", "medical-cap-mould",
  "personal-care-cap-mould", "functional-cap-mould", "plastic-handle-cap-mould"
]);
export const MOULD_ROUTES = new Set([
  "/", "/about/", "/products/", "/Plastic-cap-mold.html", "/capabilities/",
  "/capabilities/mould-design/", "/capabilities/precision-manufacturing/",
  "/capabilities/trial-sampling/", "/manufacturing/", "/quality-control/",
  "/request-sample/", "/contact/", "/samples/", "/news/",
  "/news/Bottle-cap-molds.html", "/Bottle-Cap-Machine/Bottle-Cap-Machine.html",
  "/video/", "/faq/", "/blog/", "/privacy-policy/",
  ...[...MOULD_MODELS].map(slug => "/product/" + slug + ".html")
]);
export const MANAGED_MODELS = MOULD_MODELS;
export const MANAGED_ROUTES = MOULD_ROUTES;

