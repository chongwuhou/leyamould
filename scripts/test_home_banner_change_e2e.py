#!/usr/bin/env python3
"""XUYI manual banner preview e2e; synthetic snapshot ALWAYS restored in finally."""
from pathlib import Path
import json,subprocess,sys,re
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
SNAP=ROOT/"_local_ops/build-snapshot.json"
assert SNAP.is_file(),"Local XUYI snapshot required, never use live D1"
original=SNAP.read_bytes()
data=json.loads(original.decode("utf8"))
assert data.get("site")=="leyamould"
defaults=json.loads((ROOT/"assets/home-banner-defaults.json").read_text(encoding="utf8"))
changed=json.loads(json.dumps(defaults,ensure_ascii=False))
changed["slides"][0]["img"]="/assets/curated-hd/feature-flip-top.webp"
changed["slides"][0]["link"]="/contact/"
changed["slides"][0]["title"]="XUYI QA Banner"
changed["slides"][0]["highlight"]="English Test Only"
changed["slides"][0]["cta"]="Visit Contact QA"
for loc in ("es","pt","ru","tr"):
 changed["slides"][0]["translations"][loc]["title"]="QA Banner "+loc
 changed["slides"][0]["translations"][loc]["highlight"]="Localized Test"
 changed["slides"][0]["translations"][loc]["cta"]="Contact "+loc
data["banners"]=changed
def build():
 proc=subprocess.run([sys.executable,"scripts/build_release.py"],cwd=ROOT,
   capture_output=True,text=True)
 if proc.returncode:raise RuntimeError(proc.stderr[-2500:]+proc.stdout[-1200:])
try:
 SNAP.write_text(json.dumps(data,ensure_ascii=False),encoding="utf8")
 build()
 for locale in ("en","es","pt","ru","tr"):
  page=ROOT/"dist"/(locale if locale!="en" else "")/"index.html"
  contents=page.read_text(encoding="utf8")
  marker="XUYI QA Banner" if locale=="en" else "QA Banner "+locale
  assert marker in contents,(locale,"title")
  assert '/assets/curated-hd/feature-flip-top.webp' in contents,(locale,"image")
  expected="/contact/" if locale=="en" else "/"+locale+"/contact/"
  assert expected in contents,(locale,"localized contact link",expected)
  tag=re.search(r'<script type="application/json" id="xuyi-home-banners">([^<]+)</script>',contents)
  assert tag,(locale,"JSON not found")
  slide=json.loads(tag.group(1))[0]
  assert slide["link"]==expected,(locale,"click-through link")
  assert slide["img"]==changed["slides"][0]["img"]
 print("XUYI_HOME_BANNER_CHANGE_E2E_PASSED",5,"languages, one image and URL, no remote D1 writes")
finally:
 SNAP.write_bytes(original)
 build()
 assert "XUYI QA Banner" not in (ROOT/"dist/index.html").read_text(encoding="utf8")
 print("XUYI_HOME_BANNER_TEST_SNAPSHOT_AND_BUILD_RESTORED")
