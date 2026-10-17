#!/usr/bin/env python3
"""The same six user-selected homepage brand marks appear in all five languages."""
import json
import re
from pathlib import Path

root=Path(__file__).resolve().parent.parent
dist=root/"dist"
manifest=json.loads((dist/"locale-manifest.json").read_text(encoding="utf-8"))
catalog=json.loads((root/"data/customer-logos.json").read_text(encoding="utf-8"))
expected=[x["logo_path"] for x in catalog["group_brand_marks"]]
assert len(expected)==6 and len(set(expected))==6
for logo in expected:
    assert (dist/logo.lstrip("/")).is_file(),("Missing published logo image",logo)

headers={
    "en":("BRANDS &amp; CUSTOMERS","Brands &amp; Customers"),
    "es":("MARCAS Y CLIENTES","Marcas y clientes"),
    "pt":("MARCAS E CLIENTES","Marcas e clientes"),
    "ru":("БРЕНДЫ И КЛИЕНТЫ","Бренды и клиенты"),
    "tr":("MARKALAR VE MÜŞTERİLER","Markalar ve Müşteriler"),
}
for loc in manifest["locales"]:
    lang=loc["code"]
    if lang not in headers:continue
    page=dist/(loc["pathPrefix"] or ".")/"index.html"
    html=page.read_text(encoding="utf-8")
    assert html.count('id="customer-brands"')==1,(lang,"Missing or duplicate brand carousel")
    section=re.search(r'<section class="client-logo section" id="customer-brands">.*?</section>',html,re.S)
    assert section,(lang,"Missing carousel markup")
    body=section.group(0)
    assert all(title in body for title in headers[lang]),(lang,"Brand heading not localized")
    assert body.count('class="client-logo__set"')==2,(lang,"Missing carousel sets")
    assert body.count('class="client-logo__set" aria-hidden="true"')==1,(lang,"Missing scrolling repeat set")
    images=re.findall(r'<img\b[^>]*\bsrc="(/assets/customer-logos/[^"]+)"',body)
    assert images==expected+expected,(lang,"Brand logos differ from approved six-mark sequence",images)
    assert body.count('class="client-logo__cell"')==12,(lang,"Incomplete carousel")
    assert len(re.findall(r'<img\b[^>]*\balt="[^"]+"',body))==12,(lang,"Missing accessible logo ALT")
print("XUYI_FIVE_LANGUAGE_BRAND_CAROUSEL_PASSED",len(headers),"languages, six ordered logos each")
