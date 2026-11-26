"""Regression checks for product-family Product/FAQ/Breadcrumb schema."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import mould_build  # noqa: E402


def nodes(payload: str):
    obj = json.loads(payload)
    return obj.get("@graph", [])


original = mould_build.CATALOG.get("categories")
original_strict_d1 = mould_build.STRICT_D1
# This is a pure renderer-contract test.  It supplies its own demo product
# row and must not require a production D1 snapshot just to resolve the
# shared breadcrumb label.
mould_build.STRICT_D1 = False
mould_build.CATALOG["categories"] = [{
    "slug": "demo-family", "route": "/product/demo-family.html", "title": "Demo Family",
    "image": "/media/product/demo-family.webp",
    "faqs": [{"question": "Which drawing is needed?", "answer": "The approved family drawing and interface details."}],
    "faqsEs": [{"question": "¿Qué plano se necesita?", "answer": "El plano aprobado de la familia y los detalles de interfaz."}],
}]

for locale, expected_faq in (("en", "Which drawing is needed?"), ("es", "¿Qué plano se necesita?")):
    canonical = "https://leyamould.com/" + ("es/" if locale == "es" else "") + "product/demo-family.html"
    graph = nodes(mould_build._json_ld(locale, "Demo Family", "Reviewed family description", "/product/demo-family.html", canonical, "https://leyamould.com/assets/about/about-hero-generated.webp"))
    product = [node for node in graph if node.get("@type") == "Product"]
    faq = [node for node in graph if node.get("@type") == "FAQPage"]
    breadcrumb = [node for node in graph if node.get("@type") == "BreadcrumbList"]
    assert len(product) == 1 and product[0]["image"] == ["https://leyamould.com/media/product/demo-family.webp"]
    assert len(faq) == 1 and faq[0]["mainEntity"][0]["name"] == expected_faq
    assert len(breadcrumb) == 1 and len(breadcrumb[0]["itemListElement"]) == 3
    assert breadcrumb[0]["itemListElement"][1]["item"].endswith("/products/")

print("PASS: product image, localized FAQPage and three-level BreadcrumbList are aligned")
mould_build.STRICT_D1 = original_strict_d1
