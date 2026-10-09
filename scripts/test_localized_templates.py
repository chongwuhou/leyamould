#!/usr/bin/env python3
"""Regression: shared templates, reviewed locale routes and sitemap stay in sync."""
from pathlib import Path
import importlib.util
import json
import re
import shutil
import tempfile

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("xuyi_locale_renderer", ROOT / "scripts/render_locales.py")
locale = importlib.util.module_from_spec(spec)
spec.loader.exec_module(locale)

with tempfile.TemporaryDirectory(prefix="xuyi-locale-qa-") as workspace:
    root = Path(workspace)
    dist = root / "dist"
    for relative in ["index.html", "about/index.html", "contact/index.html", "sitemap.xml"]:
        path = dist / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "dist" / relative, path)
    # Fixture must start from an English-only sitemap, even when the real
    # production dist already contains all four translated languages.
    (dist / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>',encoding="utf-8")
    sample_html = (
        '<section class="section"><div class="shell">'
        '<h1>Botellas plasticas para marcas y distribuidores</h1>'
        '<p>Contenido aprobado para prueba local solamente, sin publicacion real.</p>'
        '<a href="/about/?source=qa#team">Conozca mas</a>'
        '<a href="/contact/#inquiry">Pida una muestra</a>'
        '</div></section>'
    )
    snapshot = {"site":"xuyi-drinkware-site",
        "languages":{"languages":[{"code":"en","enabled":True,"publishReady":True},
          {"code":"es","enabled":True,"publishReady":True,"pathPrefix":"es"}]},
        "translations":[
          {"resourceId":"page:/","locale":"es",
           "content":{"title":"Inicio de prueba","description":"Resumen revisado de prueba","mainHtml":sample_html}},
          {"resourceId":"page:/about/","locale":"es",
           "content":{"title":"Nosotros de prueba","description":"Informacion de prueba","mainHtml":sample_html}},
          {"resourceId":"page:/contact/","locale":"pt",
           "content":{"title":"Unreviewed","description":"Never publish","mainHtml":sample_html}}
        ]}
    fixture=root/"snapshot.json"
    fixture.write_text(json.dumps(snapshot),encoding="utf-8")
    locale.DIST=dist
    locale.SNAPSHOT=fixture
    locale.main()
    home=(dist/"es/index.html").read_text(encoding="utf-8")
    about=(dist/"es/about/index.html").read_text(encoding="utf-8")
    english=(dist/"index.html").read_text(encoding="utf-8")
    sitemap=(dist/"sitemap.xml").read_text(encoding="utf-8")
    assert '<html lang="es">' in home
    assert '<link rel="canonical" href="https://xuyibottles.com/es/">' in home
    assert 'href="/es/about/' in home and 'href="/es/about/' in about
    assert 'href="/contact/#inquiry"' in home, "Missing localized pages must safely stay English"
    assert "/es/contact/" not in home
    assert '<meta name="robots" content="noindex,nofollow">' in home
    assert '<link rel="alternate" hreflang="es" href="https://xuyibottles.com/es/">' in english
    assert '<link rel="alternate" hreflang="en" href="https://xuyibottles.com/about/">' in about
    assert "<loc>https://xuyibottles.com/es/</loc>" in sitemap
    assert "<loc>https://xuyibottles.com/es/about/</loc>" in sitemap
    assert "<loc>https://xuyibottles.com/es/contact/</loc>" not in sitemap
    assert not (dist/"es/contact/index.html").exists()
    locale.main()
    again=(dist/"sitemap.xml").read_text(encoding="utf-8")
    assert again.count("<loc>https://xuyibottles.com/es/about/</loc>")==1
    print("XUYI_LOCALIZED_TEMPLATE_REGRESSION_PASSED 13 checks, temporary fixture only")