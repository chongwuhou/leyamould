#!/usr/bin/env python3
"""D1 nav parity with Demalong: real top-level ordering and child menus."""
import sys,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
import site_renderer as renderer

nav=[
 dict(id="home",parent_id="",label="Home",url="/",sort_order=10),
 dict(id="products",parent_id="",label="Products",url="/products/",sort_order=20),
 dict(id="capabilities",parent_id="",label="Capabilities",url="/capabilities/",sort_order=30),
 dict(id="about",parent_id="",label="About",url="/about/",sort_order=40),
 dict(id="why-us",parent_id="",label="Why Us",url="/why-us/",sort_order=50),
 dict(id="blog",parent_id="",label="Blog",url="/blog/",sort_order=60),
 dict(id="contact",parent_id="",label="Contact Us",url="/contact/",sort_order=70),
 dict(id="custom-top",parent_id="",label="Shipping Check",url="/shipping-logistics/#shipping",sort_order=15),
 dict(id="custom-child",parent_id="products",label="More Bottles",url="/products/2095/",sort_order=19),
 dict(id="custom-cap",parent_id="capabilities",label="OEM Methods",url="/privacy-policy/",sort_order=25)
]
saved=renderer.BUILD_STATE
try:
 renderer.BUILD_STATE={**saved,"navigation":nav}
 html=renderer.header()
 assert '<a class="nav__link" href="/shipping-logistics/#shipping">Shipping Check</a>' in html
 assert html.index('>Home</a>')<html.index('>Shipping Check</a>')<html.index('>Products')
 assert 'More Bottles' in html and html.count('More Bottles')==2,("D1 child must appear in desktop+mobile",html.count('More Bottles'))
 assert html.count('OEM Methods')==2
 assert html.count('Shipping Check')==2
 assert html.count('href="/faq/"')==2,"FAQ must stay accessible via desktop and mobile even with D1 custom nav"
 assert 'id="menu-products"' in html
 assert 'id="menu-capabilities"' in html
 assert html.count('<div class="mega__column">')==4
 # A saved external D1 link must always carry safe target attributes.
 nav.append(dict(id="external",parent_id="",label="Trade Portal",url="https://example.com/trade",sort_order=35,new_window=1))
 assert 'rel="noopener noreferrer"' in renderer.header()
 # Invalid content and non-approved protocols cannot become HTML.
 nav.append(dict(id="injection",parent_id="",label="<script>alert(1)</script>",url="javascript:alert(1)",sort_order=99))
 assert '<script>alert' not in renderer.header()
finally:
 renderer.BUILD_STATE=saved
print("XUYI_D1_NAVIGATION_TEMPLATE_TESTS_PASSED",10,"checks")