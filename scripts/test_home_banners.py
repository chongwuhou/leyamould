#!/usr/bin/env python3
"""Five-language XUYI footer and first-frame banner release gate."""
import json,re,sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root))
from home_banner_config import DEFAULT,verified,for_locale,tag
dist=root/"dist"
snapshot=root/"_local_ops/build-snapshot.json"
state=json.loads(snapshot.read_text(encoding="utf8")) if snapshot.is_file() else {}
manifest=json.loads((dist/"locale-manifest.json").read_text(encoding="utf-8"))
langs=manifest["locales"]
assert state.get("site","xuyi-drinkware-site")=="xuyi-drinkware-site"
assert len(DEFAULT["slides"])==3
assert len(verified(DEFAULT)["slides"])==3
for language in langs:
 lang=language["code"]
 prefix=language["pathPrefix"]
 file=dist/(prefix or ".")/"index.html"
 text=file.read_text(encoding="utf8")
 assert text.count('id="xuyi-home-banners"')==1,(lang,"duplicate or missing banner JSON")
 match=re.search(r'<script type="application/json" id="xuyi-home-banners">([^<]+)</script>',text)
 assert match,(lang,"banner config missing")
 saved=json.loads(match.group(1))
 translated_routes=set()
 if lang!="en":
  translated_routes={"/"+file.parent.relative_to(dist/prefix).as_posix().strip("/")+"/" for file in (dist/prefix).rglob("index.html")}
  translated_routes.add("/")
 expected=for_locale(state,lang,translated_routes if lang!="en" else None)
 assert saved==expected,(lang,"localized banner settings lost")
 for item in saved:
  assert item["img"].startswith(("/media/","/assets/"))
  if item["img"].startswith("/assets/"):assert (dist/item["img"].lstrip("/")).exists()
 assert 'id="hero-image"' in text and 'id="hero-cta"' in text
 assert re.search(r'<h1 id="hero-title">[^<]+<span>',text)
 assert re.search(r'<a\b(?=[^>]*\bid="hero-cta")(?=[^>]*\bhref="'+re.escape(saved[0]["link"])+r'")[^>]*>',text),(lang,"hero link differs from reviewed D1")
 assert saved[0]["title"] in text
 assert text.count('class="footer__bottom"')==1
 assert 'Quick Links' not in text and '<h3>Contact Us</h3>' in (dist/"index.html").read_text(encoding="utf8")
 # The exact legal items are now in the footer bottom, not duplicated in columns.
 footer=text.split('<footer class="footer">',1)[1].split('</footer>',1)[0]
 bottom=footer.split('<div class="footer__bottom">',1)[1]
 assert 'href="/sitemap.xml"' in bottom
 privacy=("/"+prefix+"/privacy-policy/") if prefix and (dist/prefix/"privacy-policy/index.html").is_file() else "/privacy-policy/"
 assert 'href="'+privacy+'"' in bottom
 assert 'data-site-email' in footer and 'data-site-whatsapp' in footer
 assert 'data-site-whatsapp-number' in footer and re.search(r'WhatsApp:\s*\+\d',footer)
 contact_file=dist/(prefix or ".")/"contact/index.html"
 if contact_file.is_file():
  contact=contact_file.read_text(encoding="utf8")
  assert re.search(r'data-site-whatsapp-number[^>]*>[^<]*\+\d',contact),(lang,"contact phone invisible")
 assert "<h3>Quick Links</h3>" not in footer
for bad in [
 {"slides":[]},
 {"slides":[{**DEFAULT["slides"][0],"img":"//evil.example/cat.jpg"},*DEFAULT["slides"][1:]]},
 {"slides":[{**DEFAULT["slides"][0],"link":"javascript:alert(1)"},*DEFAULT["slides"][1:]]},
 {"slides":[{**DEFAULT["slides"][0],"title":"<script>alert(1)</script>"},*DEFAULT["slides"][1:]]}
]:
 try:verified(bad)
 except ValueError:pass
 else:raise AssertionError("Unsafe banner configuration passed")
assert 'const managed=JSON.parse' in (dist/"assets/site.js").read_text(encoding="utf8")
print("XUYI_HOME_BANNER_FOOTER_TESTS_PASSED",len(langs),"languages, 3 slides, privacy/sitemap and controls")
