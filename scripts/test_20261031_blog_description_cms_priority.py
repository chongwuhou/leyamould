#!/usr/bin/env python3
"""Guard D1 CMS-owner precedence and repeat-build idempotency in 4 locales."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from blog_locale_description_baseline import reviewed_descriptions,resolve_description

def main():
    records=reviewed_descriptions()
    descriptions={}
    for key,row in records.items():
        route,loc=key
        approved=resolve_description(route,loc,row["baseline"])
        assert approved==row["approved"],key
        assert approved!=row["baseline"],key
        assert resolve_description(route,loc,approved)==approved,key
        owner="Editor-customized description for "+loc+" "+route
        assert resolve_description(route,loc,owner)==owner,key
        descriptions.setdefault(loc,set()).add(approved)
    assert {k:len(v) for k,v in descriptions.items()}=={"es":3,"pt":3,"ru":3,"tr":3}
    assert resolve_description("/blog/other/","es","Other D1 description")=="Other D1 description"
    for i in (1,2,3):
        loc=json.loads((ROOT/f"data/blog-localized-copy-20261031-{i}.json").read_text("utf8"))
        for lang in ("es","pt","ru","tr"):
            route="/blog/"+["construction-site-crew-water-bottles-bulk-procurement","workplace-refill-station-reusable-bottle-bulk-sourcing","bicycle-shop-water-bottle-cage-fit-wholesale-buying"][i-1]+"/"
            assert loc[lang]["description"]==records[(route,lang)]["approved"]
    print("XUYI_20261031_BLOG_DESCRIPTION_UNIQUE_CMS_OWNER_EDIT_PRIORITY_12_CASES_PASS")
if __name__=="__main__":main()
