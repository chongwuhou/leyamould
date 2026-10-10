#!/usr/bin/env python3
"""Prevent XUYI FAQ links disappearing from the shared five-language chrome."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/"dist"
tested=0
for locale in ("","es","pt","ru","tr"):
 prefix="/"+locale if locale else ""
 faq=prefix+"/faq/"
 assert (DIST/locale/"faq/index.html").is_file(),("FAQ page not generated",locale)
 pages=[DIST/locale/"index.html",DIST/locale/"products/index.html",DIST/locale/"contact/index.html"]
 for page in pages:
  html=page.read_text(encoding="utf8")
  nav=re.search(r'<nav class="nav"[^>]*>(.*?)</nav>',html,re.S)
  assert nav,(locale,page,"desktop nav missing")
  desktop=nav.group(1)
  mobile=html.split('<nav class="mobile-nav" id="mobile-navigation"',1)[1].split('</nav>',1)[0]
  footer=html.split('<footer class="footer">',1)[1].split('</footer>',1)[0]
  for location,part in (("desktop",desktop),("mobile",mobile),("footer",footer)):
   found=re.findall(r'href="'+re.escape(faq)+'"',part)
   assert len(found)==1,(locale,page,location,len(found))
  assert '<h3>Quick Links</h3>' not in footer,(locale,page)
  bottom=footer.split('<div class="footer__bottom">',1)[1]
  assert 'href="/sitemap.xml"' in bottom,(locale,page)
  assert "Privacy Policy" in bottom or locale!="",(locale,page)
  tested+=1
print("XUYI_FIVE_LANGUAGE_FAQ_ENTRY_TEST_PASSED",tested,"page chrome samples; desktop/mobile/footer")