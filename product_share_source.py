"""Source-level product social previews: a spreadsheet is not a SKU photo.

Use genuine model-linked images in Product.image. When a catalog model only
has an Excel screenshot, OG uses explicitly labeled category artwork instead.
"""
from __future__ import annotations
from html import escape
import re

ORIGIN = "https://xuyibottles.com"
UNVERIFIED_MAIN_IMAGES = {
    "Plastic Sports Water Bottles": "/media/ppt/slide-059.webp",
    "Kids Plastic Water Bottles": "/media/ppt/slide-030.webp",
    "Large Capacity Water Jugs": "/media/ppt/slide-055.webp",
    "Plastic Shaker Bottles": "/media/ppt/slide-094.webp",
}
CATEGORY_PREVIEWS = {
    "Plastic Sports Water Bottles": "/assets/social/product-unverified-sports.webp",
    "Kids Plastic Water Bottles": "/assets/social/product-unverified-kids.webp",
    "Large Capacity Water Jugs": "/assets/social/product-unverified-jugs.webp",
    "Plastic Shaker Bottles": "/assets/social/product-unverified-shaker.webp",
}


def real_product_images(product):
    """Skip Excel spreadsheet rows, generic category art and mismatched reuse."""
    # The six human-reviewed shaker HD photos already have a permanent
    # original->approved URL map. Apply it at the model-source layer so
    # schema, social preview and sitemap agree BEFORE publishing.
    from product_image_sitemap import approved_shaker_image_aliases
    aliases=approved_shaker_image_aliases()
    verified = []
    for image in product.get("images", []):
        if not isinstance(image, str) or not image.startswith(("/media/", "/assets/")):
            continue
        if ".." in image or "/excel/" in image.lower() or image.startswith("/assets/products/"):
            continue
        if image in UNVERIFIED_MAIN_IMAGES.values():
            continue
        if str(product.get("model")) == "2100" and "/gallery/2099-" in image:
            continue
        image=aliases.get(image,image)
        if image not in verified:
            verified.append(image)
    return verified


def social_path(product):
    verified = real_product_images(product)
    if verified:
        return verified[0]
    category = product.get("category")
    if category not in CATEGORY_PREVIEWS:
        raise ValueError("Unknown category: " + str(category))
    return CATEGORY_PREVIEWS[category]


def add_social_head(document, product):
    """Source renderer: add safe OG/Twitter previews, preserve later owner art."""
    if "</head>" not in document:
        raise ValueError("Product document missing head")
    head, tail = document.split("</head>", 1)
    existing = re.search(r'<meta property="og:image" content="([^"]*)">', head)
    owner = existing.group(1) if existing else ""
    if owner.startswith(ORIGIN + "/") and "/excel/" not in owner.lower():
        url = owner
    else:
        url = ORIGIN + social_path(product)
    safe = escape(url, quote=True)
    head = re.sub(r'<meta property="og:image" content="[^"]*">', "", head)
    head = re.sub(r'<meta name="twitter:image" content="[^"]*">', "", head)
    head = re.sub(r'<meta name="twitter:card" content="[^"]*">', "", head)
    head += (
        '<meta property="og:image" content="' + safe + '">'
        '<meta name="twitter:card" content="summary_large_image">'
        '<meta name="twitter:image" content="' + safe + '">'
    )
    return head + "</head>" + tail