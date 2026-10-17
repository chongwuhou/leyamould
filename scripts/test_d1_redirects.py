#!/usr/bin/env python3
"""D1 redirect compiler E2E contract (no actual production D1 mutations)."""
from site_redirects import redirect_lines
rows=[
 {"source_path":"/old-plastic-bottle/","target_path":"/products/2501/","status_code":301},
 {"source_path":"/old-contact/","target_path":"/contact/","status_code":302},
 {"source_path":"/trade/","target_path":"https://example.com/partner","status_code":301}
]
result=redirect_lines(rows)
assert result==[
 "/old-plastic-bottle/ /products/2501/ 301",
 "/old-contact/ /contact/ 302",
 "/trade/ https://example.com/partner 301"]
assert redirect_lines([])==[]
invalid=[
 [{"source_path":"/api/admin/auth","target_path":"/contact/","status_code":301}],
 [{"source_path":"/admin/","target_path":"/","status_code":301}],
 [{"source_path":"/media/product/x.webp","target_path":"/","status_code":301}],
 [{"source_path":"/x/","target_path":"javascript:alert(1)","status_code":302}],
 [{"source_path":"/x/","target_path":"//attacker.example","status_code":301}],
 [{"source_path":"/x/","target_path":"https://user:pw@bad.example","status_code":301}],
 [{"source_path":"/x/","target_path":"/x/","status_code":301}],
 [{"source_path":"/x/\n/any","target_path":"/","status_code":301}],
 [{"source_path":"/x/","target_path":"/","status_code":308}],
 [rows[0],rows[0]],
]
for data in invalid:
 try:redirect_lines(data)
 except ValueError:pass
 else:raise AssertionError("Invalid redirect was allowed: "+repr(data))
print("XUYI_D1_REDIRECT_COMPILER_TESTS_PASSED",len(invalid)+4,"checks")
