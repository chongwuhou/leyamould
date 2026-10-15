# XUYI website mandatory change policy

Before editing this project, read [PROJECT_CHANGE_POLICY.md](PROJECT_CHANGE_POLICY.md).
This applies to localGPT, Codex, other coding agents and human maintainers.
## P0：站长永久指令——所有批量变更只允许在模板 / 正式数据源实施（每次任务开工前必读）
**优先级高于任何历史脚本、旧审计说明、临时实现与建议。适用于今后所有 SEO、GEO、多语言、容量、产品、博客、图片、内链、OG/Schema、样式和后台批量任务。**

1. **每次执行任务，第一步必须阅读本文件和 `PROJECT_CHANGE_POLICY.md`**，明确涉及的共享模板、实际字段所有者（Cloudflare D1/CMS、项目权威数据文件）及正式渲染入口。即使用户只说「继续、批量、修复、上线」，也不能跳过。
2. **凡是批量内容/布局修改，先修改共享模板/组件/正式源数据或 D1/CMS 数据源，再由标准构建生成所有页面。** 不允许把页面已经渲染完后的字符串替换、手工逐页编辑、直接写 `dist/`、线上 HTML 或 R2 缓存当作实施方案。源文件里的「循环改生成 HTML」同样**不自动等于模板化**；应把逻辑前移到模板/正式渲染器或 CMS 字段。
3. **允许用生成页做一次性诊断和隔离测试**，但测试数据必须隔离、可还原、不可发布；测试一结束，必须回到模板或数据库完成正式修复，再从干净源重新全量构建；绝不把测试产物当最终成果。
4. **后台 D1/CMS 用户编辑拥有最终优先权。** 对标题、描述、翻译、文章、图片、内链、容量等必须检测字段是否在后台已更新；用户手动改写不能被静态回退表、旧数据指纹、构建后 HTML 替换覆盖。
5. **批量任务完成证据必须包含**：源模板或数据库/源字段的具体修改位置、真实 CMS 编辑优先测试、五语/相关路由回归、两次干净全站构建、无重复注入与新增型号不被旧总数卡住、生产 CI 和线上核验（若获准部署）。若只是改了产物或历史后处理脚本，必须明确标记「尚未真正完成」。
6. **已有直接在 `dist/` 后处理 HTML 的历史脚本属于待迁移旧债，不是今后新增或延续这种做法的许可。** 今后触及相关功能，应优先把其结果迁移进共享模板/正规数据层，并移除冲突的后处理入口；不可用「后处理脚本纳入 build 流程」冒充符合这一条指令。
7. **用户无须再次提醒。** 完成每个任务前必须自检本规则；冲突时以本 P0 规则为准，先拒绝不持久的捷径并选择模板/CMS 方案。



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


## 博客新文章编辑发布规则（2026-10-15，永久执行）

**此条是编辑质量规则，不可用自动注入、整页 HTML 计数或仅通过 CI 伪装已经完成。** 每篇今后新发布或实质改写的 XUYI 博客，**正文中自然分散链接 2–5 个真实、主题相关且资料可信的不同产品型号详情页**；**正文结束处由编辑挑选 2–3 篇直接相关的其他博客文章作为“相关阅读”**。不计入页头、导航、侧栏、页脚和未人工挑选的自动推荐；同型号重复链接只算一次。逐条打开核对 URL、型号、主题和对应语言路径，禁止编造规格和认证。**编辑在 CMS 正式正文中完成并审核后方可发布**；CMS 人工修改优先。此前 16 篇不能凭模板推荐模块或全页链接统计被宣称已完成编辑整改。具体操作规范：`docs/BLOG_EDITORIAL_PUBLISH_CHECKLIST.md`。