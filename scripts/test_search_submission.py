#!/usr/bin/env python3
"""Fail-closed checks for all planned search-engine submissions."""
from pathlib import Path
import importlib.util
import json
import os
import sys
from unittest.mock import patch
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
import search_submission as module
import preindex_security_gate as gate

site=json.loads((ROOT/"deployment/site.config.json").read_text(encoding="utf-8"))
assert site["cloudflare"]["pagesProjectName"]=="xuyi-drinkware-site"
assert module.approved() is site["site"]["indexingApproved"]
dist=ROOT/"dist"
manifest=module.create_manifest()
urls=module.sitemap_urls((dist/"sitemap.xml").read_bytes())
assert len(urls)==len(manifest["urls"])>=675
assert len(set(manifest["urls"]))==len(urls)
assert all(k.startswith(module.ORIGIN+"/") for k in manifest["urls"])
assert not (dist/"_headers").read_text(encoding="utf-8").startswith("/*")
headers=(dist/"_headers").read_text(encoding="utf-8")
header_lines=headers.splitlines()
published=json.loads((dist/"locale-manifest.json").read_text(encoding="utf-8"))["locales"]
for lang in published:
    prefix=lang["pathPrefix"]
    expected="/"+prefix+"/" if prefix else "/"
    assert header_lines.count(expected)==1,(lang,"language-specific hero preload missing")
assert headers.count('rel="preload"')==len(published),"Do not preload four banners across all pages"
assert module.new_or_changed(manifest,manifest)==[]
assert module.new_or_changed(None,manifest,first_launch=True)==sorted(manifest["urls"])
modified=dict(manifest["urls"])
one=next(iter(modified))
modified[one]="newhash"
assert module.new_or_changed(manifest,{**manifest,"urls":modified})==[one]

try:
    module.sitemap_urls(b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                        b'<url><loc>https://someone-else.com/</loc></url></urlset>')
except ValueError:pass
else:raise AssertionError("Cross-domain search submission allowed")
with patch.object(module,"approved",return_value=False),patch.object(gate,"approved",return_value=False):
    with patch.dict(os.environ,{"XUYI_INDEXNOW_KEY":"a"*32},clear=False):
        assert module.key_file() is None
        assert not (dist/("a"*32+".txt")).exists()
        with patch("urllib.request.urlopen",side_effect=AssertionError("Attempted external search submission")):
            gate.check()
            argv=sys.argv
            try:
                sys.argv=["search_submission.py","--submit"]
                module.main()
            finally:sys.argv=argv
assert not any(f.name.endswith(".txt") and f.stem=="a"*32 for f in dist.iterdir())
# Indexing authorization must check BOTH apex and www without a stale-source
# exception. Pages returns 410 for source tombstones, which is safe like 404.
checked=[]
class SafeSourceResponse:
    status=410
    def __enter__(self):return self
    def __exit__(self,*args):return False
def safe_source_probe(request,timeout=15):
    checked.append(request.full_url)
    return SafeSourceResponse()
with patch.object(gate,"approved",return_value=True), patch("urllib.request.urlopen",side_effect=safe_source_probe):
    gate.check()
assert len(checked)==6,checked
assert set(checked)=={origin+path for origin in (module.ORIGIN,module.ORIGIN.replace("https://","https://www.",1))
                     for path in gate.SENSITIVE}
def unsafe_source_probe(request,timeout=15):
    if request.full_url.endswith("/build.py"):return type("UnsafeResponse",(),{"status":200,"__enter__":lambda self:self,"__exit__":lambda self,*args:False})()
    return SafeSourceResponse()
with patch.object(gate,"approved",return_value=True), patch("urllib.request.urlopen",side_effect=unsafe_source_probe):
    try:gate.check()
    except RuntimeError as exc:assert "old-source cache" in str(exc)
    else:raise AssertionError("Public source file returned HTTP 200 without stopping indexing")
with TemporaryDirectory() as temp:
    with patch.object(module,"approved",return_value=True),patch.object(module,"DIST",Path(temp)):
        with patch.dict(os.environ,{"XUYI_INDEXNOW_KEY":"c"*32},clear=False):
            assert module.key_file()=="c"*32
            assert (Path(temp)/("c"*32+".txt")).read_text(encoding="utf-8")=="c"*32
    with patch.object(module,"fetch",return_value=b"User-agent: *\nDisallow: /\n"):
        try:module.verify_live()
        except ValueError as exc:assert "robots.txt" in str(exc)
        else:raise AssertionError("Blocked robots did not stop IndexNow submission")
print("XUYI_SEARCH_SUBMISSION_SAFE",len(urls),"verified URLs, blocked-state and approval protections tested without external submissions")