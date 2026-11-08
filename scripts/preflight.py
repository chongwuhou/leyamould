#!/usr/bin/env python3
"""Hard checks before touching XUYI's production deployment."""
from pathlib import Path
import json
import sys
import os
from datetime import datetime

ROOT=Path(__file__).resolve().parent.parent
cfg=json.loads((ROOT/"deployment/site.config.json").read_text(encoding="utf-8"))
checks={
 "site origin":cfg["site"]["origin"]=="https://xuyibottles.com",
 "Cloudflare Pages identity":cfg["cloudflare"]["pagesProjectName"]=="xuyi-drinkware-site",
 "D1 isolated":cfg["cloudflare"]["d1Database"]=="xuyi-drinkware-d1" and cfg["cloudflare"]["d1Binding"]=="XUYI_DB",
 "R2 isolated":cfg["cloudflare"]["r2Bucket"]=="xuyi-drinkware-r2" and cfg["cloudflare"]["r2Binding"]=="XUYI_ASSETS",
 "Explicit indexing flag is boolean":type(cfg["site"]["indexingApproved"]) is bool,
 "Independent template files":all((ROOT/"templates/site"/(name+".html")).is_file() for name in ("shell","header","footer","sidebar")),
 "Independent Pages Functions":all((ROOT/p).is_file() for p in ("functions/blog/[[path]].js","functions/api/admin/blog.js","functions/api/admin/publish.js","functions/api/publish-state.js")),
 "GitHub Actions configured":(ROOT/".github/workflows/publish-xuyi.yml").is_file(),
 "Build artifact isolated":(ROOT/"scripts/build_release.py").is_file(),
 "Scheduler locale count is D1-driven":"prepared.length!==locales.length" in (ROOT/"functions/_shared/publish-scheduler.js").read_text(encoding="utf-8"),
}
for name,ok in checks.items():print(("PASS" if ok else "FAIL"),name)
if not all(checks.values()):sys.exit("XUYI_PREFLIGHT_FAILED")
print("XUYI_PREFLIGHT_PASSED",len(checks),"checks")
