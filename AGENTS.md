# XUYI website mandatory change policy

Before editing this project, read [PROJECT_CHANGE_POLICY.md](PROJECT_CHANGE_POLICY.md).
This applies to localGPT, Codex, other coding agents and human maintainers.

1. Make every correction in the **shared source template, CMS-aware data,
   reusable rendering function, or version-controlled build pipeline**.
   Never count editing dist output or already deployed HTML as a fix.
2. Cloudflare **D1/CMS owner edits are authoritative**. Later edits to SEO
   titles, translations, Blog text, links and product images must not be
   overwritten or rejected by earlier cleanup scripts.
3. Make source transformations **idempotent and tolerant of existing
   owner-selected content**. Do not require old image URLs or previous
   page totals to remain unchanged forever.
4. Rebuild the entire site from source and test a second rebuild; validate
   all five locales, canonical/hreflang, links, inquiry functionality and
   representative live URLs before declaring a production release complete.
5. Keep G-series factory model status intact. Never invent product data,
   certifications, physical factory evidence or exact-SKU photographs.
6. Make the smallest change that fixes the proven issue. Do not modify
   unrelated front-end design, D1 inquiries or R2 original media.

If a legacy script violates these rules, fix that script and add a regression
test reproducing a realistic owner/CMS update before publishing.

7. **永久规则 / Permanent rule:** 用户后续随时可能在后台改图片、SEO、语言、内链和文章，或增加新型号与语言。所有修复必须改正式源模板/数据/CMS 感知构建器，并随每次全站重建自动复现；严禁把改动 `dist/`、手工线上编辑或临时修补当成完成。发布前验证「后台修改优先、重复运行幂等、新增内容不被旧计数卡住」。必须把回归测试接入自动发布门禁。

8. **海外零售容量规格永久规则（2026-10-14 修订）：**工厂准确毫升容量始终保留在参数表。海外营销 SEO、产品卡片采用 `data/retail-oz-size-classes.json` 的海外常用 oz 规格档位（例如 800ml→28 oz class、1000ml→32 oz class、1200ml→40 oz class、2000ml→64 oz class），**不得当作精确 US fl oz 等式**。必须明确标注 size class/approximate，实际容量按源数据 ml 为准。多容量逐一标注，异常 2506、未知 G 型号不猜测。Tritan / BPA Free 用于定制材料询盘，不冒充现有材质或认证；后台 SEO 修改优先保留。唯一构建入口 `scripts/source_catalog_capacity_oz.py` + 审核规格表 + 测试。