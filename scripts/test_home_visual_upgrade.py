#!/usr/bin/env python3
"""Keep the five-language generic homepage image high quality and truthful."""
from pathlib import Path
import json
import re
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from media_quality_guard import NEW,OLD,ALT,upgrade_home_visual
DIST=ROOT/"dist"
manifest=json.loads((ROOT/"data/curated-hd-manifest.json").read_text(encoding="utf-8"))
target=next(item for item in manifest["assets"] if item["target"]==NEW)
assert min(target["sourceDimensions"])>=1500
assert target["pageUse"]=="generic-menu-and-hero"
assert (DIST/NEW.lstrip("/")).is_file()
for locale in ALT:
    path=DIST/("" if locale=="en" else locale)/"index.html"
    source=path.read_text(encoding="utf-8")
    main=source.split('<main id="main-content">',1)[1].split("</main>",1)[0]
    assert 'src="'+NEW+'" alt="'+ALT[locale]+'"' in main,locale
    # Homepage blog/editorial photos stay as their original source reference.
    assert OLD in main,("Unexpected change of blog catalog image",locale)
    assert main.count('alt="'+ALT[locale]+'"')==1
    assert 'src="/assets/lo/lo-002-01.webp"' in (
        DIST/("" if locale=="en" else locale)/"collections/sports-water-bottles/index.html"
    ).read_text(encoding="utf-8"),("Sports LO-002 SKU main photo was changed",locale)
    changed=upgrade_home_visual('<img src="'+OLD+'" alt="Original" loading="lazy">',locale)
    assert 'src="'+NEW+'"' in changed and 'alt="'+ALT[locale]+'"' in changed
print("XUYI_HOME_5_LOCALES_HIGH_RES_MARKETING_AND_SKU_IMAGE_GUARD_PASSED")