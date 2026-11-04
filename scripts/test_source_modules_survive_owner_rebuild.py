#!/usr/bin/env python3
"""Regression: CMS owner choices survive reruns; new source catalog models do not break builds."""
from pathlib import Path
from tempfile import TemporaryDirectory
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from product_share_source import add_social_head
from site_renderer import SERIES
import model_catalog_buyer_comparison as comparisons
import curated_application_feature_answers as decisions

LOCALES = ("", "es/", "pt/", "ru/", "tr/")

def change_section(page, css, replacement):
    body = page.read_text(encoding="utf8")
    regex = re.compile(r'<section class="section ' + re.escape(css) + r'" id="' +
                       ("catalog-comparison" if css == "catalog-compare" else "buyer-evidence-checks") +
                       r'">.*?</section>', re.S)
    updated, count = regex.subn(lambda _: replacement, body, count=1)
    assert count == 1, (page, css)
    page.write_text(updated, encoding="utf8")
    return updated

with TemporaryDirectory(prefix="xuyi-owner-source-rebuild-") as temporary:
    stage = Path(temporary)
    for prefix in LOCALES:
        for src in (ROOT / "dist" / prefix / "products").glob("*/index.html"):
            dst = stage / prefix / src.relative_to(ROOT / "dist" / prefix)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        for route in decisions.TOPICS:
            src = ROOT / "dist" / prefix / route / "index.html"
            dst = stage / prefix / route / "index.html"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    # A custom CMS social preview is already present. Retain it, even if
    # it differs from the JSON-LD product photo.
    own_product = stage / "es/products/501/index.html"
    owner_image = "https://xuyibottles.com/assets/sku-hd/owner-approved-501.webp"
    contents = own_product.read_text(encoding="utf8")
    changed, count = re.subn(
        r'(<meta property="og:image" content=")[^"]+(")',
        lambda m: m.group(1) + owner_image + m.group(2), contents, count=1)
    assert count == 1
    own_product.write_text(changed, encoding="utf8")

    # The source renderer, not a dist postprocessor, builds missing preview
    # tags while respecting the independent D1 owner image above.
    preserved=add_social_head(own_product.read_text(encoding="utf8"),SERIES["501"])
    assert owner_image in preserved
    assert add_social_head(preserved,SERIES["501"])==preserved
    # A freshly approved model receives social tags from the shared renderer.
    fresh_product = stage / "pt/products/502/index.html"
    fresh_body = fresh_product.read_text(encoding="utf8")
    for key in (r'<meta property="og:image" content="[^"]+">',
                r'<meta name="twitter:image" content="[^"]+">',
                r'<meta name="twitter:card" content="[^"]+">'):
        fresh_body, count = re.subn(key, "", fresh_body, count=1)
        assert count == 1, key
    generated=add_social_head(fresh_body,SERIES["502"])
    fresh_product.write_text(generated, encoding="utf8")
    assert owner_image in own_product.read_text(encoding="utf8")
    assert 'property="og:image"' in fresh_product.read_text(encoding="utf8")
    assert add_social_head(generated,SERIES["502"])==generated

    # Catalog comparisons are now source-rendered, not a dist postprocessor.
    # An existing CMS-owned comparison block suppresses any generated replacement.
    from scripts.source_catalog_capacity_oz import source_body_enrichment

    def main_body(markup):
        return markup.split('<main id="main-content">',1)[1].split("</main>",1)[0]

    edited_model = stage / "es/products/501/index.html"
    owner_table = ('<section class="section catalog-compare" id="catalog-comparison">'
                   '<p>CMS editor approved a revised model matrix.</p></section>')
    change_section(edited_model, "catalog-compare", owner_table)
    owner_markup=edited_model.read_text(encoding="utf8")
    owner_main=main_body(owner_markup)
    assert source_body_enrichment(owner_main,"es",SERIES["501"])==owner_main
    assert source_body_enrichment(owner_main,"es",SERIES["501"])==owner_main
    assert owner_table in edited_model.read_text(encoding="utf8")

    # A newly approved source-catalog model receives the same five-locale
    # comparison through the source renderer, with no stale fixed-count gate.
    basis = next(r for r in comparisons.SOURCE_MODELS if not r.get("manualNew"))
    additional = {**basis, "model": "9998", "slug": "9998"}
    locale_codes=("en","es","pt","ru","tr")
    for prefix,locale in zip(LOCALES,locale_codes):
        target = stage / prefix / "products/9998/index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        source = (stage / prefix / "products" / str(basis["slug"]) / "index.html").read_text(encoding="utf8")
        source, count = re.subn(
            r'<section class="section catalog-compare" id="catalog-comparison">.*?</section>',
            "", source, count=1, flags=re.S)
        assert count == 1
        body=main_body(source)
        generated=source_body_enrichment(body,locale,additional)
        assert generated.count('id="catalog-comparison"')==1,(locale,"missing source-rendered comparison")
        assert source_body_enrichment(generated,locale,additional)==generated,(locale,"comparison not idempotent")
        start_main=source.index('<main id="main-content">')+len('<main id="main-content">')
        end_main=source.index("</main>",start_main)
        target.write_text(source[:start_main]+generated+source[end_main:],encoding="utf8")
    assert owner_table in edited_model.read_text(encoding="utf8")

    # Buyer decision guidance also belongs to the editor once published.
    owned = stage / "ru/applications/everyday-hydration/index.html"
    owner_guidance = ('<section class="section buyer-evidence-checks" id="buyer-evidence-checks">'
                      '<p>CMS-approved scenario advice remains in place.</p></section>')
    change_section(owned, "buyer-evidence-checks", owner_guidance)
    pending = stage / "tr/features/straw-lid/index.html"
    change_section(pending, "buyer-evidence-checks", "")
    assert decisions.apply(stage) == 1
    assert decisions.apply(stage) == 0
    assert owner_guidance in owned.read_text(encoding="utf8")
    assert 'id="buyer-evidence-checks"' in pending.read_text(encoding="utf8")

print("XUYI_OWNER_EDITS_OG_MODEL_COMPARISON_BUYER_GUIDANCE_GROWTH_REBUILD_PASSED")
