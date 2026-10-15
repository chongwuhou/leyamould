"""Reviewed Spanish homepage/blog microcopy at D1-source render stage.

Exact HTML fragments identify untouched legacy machine translations. If a CMS
editor has rewritten an element, the old snippet no longer matches and the
new editorial content wins. Never edit generated dist HTML.
"""
_RULES={
 "/":{
  '<p class="hero__note">Taizhou, China · Vasos de plástico · Consultas OEM/ODM</p>':
  '<p class="hero__note">Taizhou, China · Botellas de plástico · Consultas OEM/ODM</p>',
  '<h2>Confiable <em>Botella de plástico</em> Socio fabricante.</h2>':
  '<h2>Socio fabricante confiable de <em>botellas de plástico</em>.</h2>'
 },
 "/blog/":{
  '<span class="eyebrow">XUYI · VASOS DE PLÁSTICO</span>':
  '<span class="eyebrow">XUYI · BOTELLAS DE PLÁSTICO</span>'
 }
}
def reviewed_spanish_copy(route,locale,fields):
    if locale!="es":return fields
    # Blog eyebrow is a shared editorial element on the index *and* each
    # article. Only rewrite the exact reviewed source element, never prose.
    scope="/" if route=="/" else "/blog/" if route.startswith("/blog/") else None
    if scope is None:return fields
    original=fields.get("mainHtml")
    if not isinstance(original,str):return fields
    current=original
    for before,after in _RULES[scope].items():
        # Guard the full approved element, not just words occurring elsewhere.
        if before in current:
            if current.count(before)!=1:
                raise ValueError("Unexpected duplicate Spanish source fragment: "+route)
            current=current.replace(before,after,1)
    return fields if current==original else {**fields,"mainHtml":current}