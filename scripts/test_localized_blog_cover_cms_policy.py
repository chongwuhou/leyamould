#!/usr/bin/env python3
"""A later D1-reviewed Blog image selection is not reset by old media fixes."""
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from repair_localized_blog_thumbnails import apply,OVERRIDES,ORIGINALS

slug="custom-logo-water-bottle-checklist"
previous=OVERRIDES[slug]
old=ORIGINALS[slug]
owner="/assets/blog/editor-approved-custom-cover.webp"

with TemporaryDirectory(prefix="xuyi-blog-media-owner-") as td:
    dist=Path(td)
    for locale in ("es","pt","ru","tr"):
        path=ROOT/"dist"/locale/"blog"
        for file in path.rglob("index.html"):
            dest=dist/file.relative_to(ROOT/"dist")
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(file,dest)

    # Simulate a subsequent CMS publication: it updates the selected post's
    # listing, body, related cards, social data and JSON-LD to its new cover.
    lang=dist/"es"/"blog"
    for file in lang.rglob("index.html"):
        doc=file.read_text(encoding="utf8")
        if previous in doc:
            file.write_text(doc.replace(previous,owner),encoding="utf8")

    # Simulate an older untranslated cover in a different locale that still
    # needs the reviewed legacy correction.
    pt=dist/"pt"/"blog"/slug/"index.html"
    doc=pt.read_text(encoding="utf8")
    hero='<div class="blog-detail__cover"><img src="'+previous+'"'
    assert hero in doc
    pt.write_text(doc.replace(hero,'<div class="blog-detail__cover"><img src="'+old+'"'),encoding="utf8")

    first=apply(dist)
    assert owner in (lang/"index.html").read_text(encoding="utf8")
    assert owner in (lang/slug/"index.html").read_text(encoding="utf8")
    assert previous not in (lang/slug/"index.html").read_text(encoding="utf8")
    assert previous in pt.read_text(encoding="utf8")
    assert '<div class="blog-detail__cover"><img src="'+previous+'"' in pt.read_text(encoding="utf8")

    before={f:f.read_bytes() for f in dist.rglob("index.html")}
    assert apply(dist)==0
    assert all(f.read_bytes()==data for f,data in before.items())
print("XUYI_LOCALIZED_BLOG_CMS_IMAGE_OVERRIDE_FIVE_LOCALE_SOURCE_POLICY_PASSED")