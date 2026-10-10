#!/usr/bin/env python3
"""Verify D1-managed original text survives while source-verified notes appear.

No cloud requests, D1 mutations or generated-file writes.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import site_renderer as site
from editorial_support import for_route
from blog_editorial import render_primary_evidence

old_write=site.write
saved=dict(site.BODY_OVERRIDES)
captured={}
site.write=lambda path,body:captured.__setitem__(path,body)
routes={
  "/about/":("Four Traceable Model References","rs-model-proof-section"),
  "/manufacturing/":("Part and Material Record","production-buyer-evidence"),
  "/quality-control/":("ISO 2859-1:2026","quality-buyer-evidence"),
  "/blog/plastic-bottle-material-selection/":("US FDA: Determining","id=\"primary-sources\""),
  "/blog/kids-water-bottle-procurement/":("bottle purchasing needs an end-use","id=\"primary-sources\"")
}
try:
 for route,(needle,marker) in routes.items():
  edited='<section class="cms-content"><h1>Approved D1 article body</h1><p>Private-label procurement text approved by the business editor; its original content must remain unchanged by source-based public supplements.</p></section>'
  assert len(edited)>=100
  site.BODY_OVERRIDES[route]=edited
  path=route.lstrip('/')+"index.html"
  shell='<html><head><title>Approved D1 content</title></head><body><main id="main-content"><p>OLD ORIGINAL SOURCE BODY</p></main></body></html>'
  site.build_url(path,"QA",shell)
  result=captured[path]
  assert edited in result,(route,"CMS body discarded")
  assert needle in result,(route,"verified supplement missing")
  assert marker in result,(route,"reviewed source module missing")
  # An editor may later save the supplemental text together with the body.
  # It must never be appended a second time.
  supplement=(render_primary_evidence(route.strip("/").split("/")[-1])
              if route.startswith("/blog/") else for_route(route,""))
  site.BODY_OVERRIDES[route]=edited+supplement
  site.build_url(path,"QA",shell)
  unique_marker=('class="section '+marker+'"' if route in ('/manufacturing/','/quality-control/')
                 else marker)
  assert captured[path].count(unique_marker)==1,(route,"duplicate editorial supplement")
finally:
 site.write=old_write
 site.BODY_OVERRIDES.clear()
 site.BODY_OVERRIDES.update(saved)
print("XUYI_EDITORIAL_D1_OVERLAY_PASSED",len(routes),"routes; original text retained, no duplicate references")