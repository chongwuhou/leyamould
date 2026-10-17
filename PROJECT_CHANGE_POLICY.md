# XUYI site — durable change rules

**The site owner requires all fixes to survive subsequent complete rebuilds.**
## P0 / Mandatory owner directive — Template or CMS only (2026-10-14; applies to every future task)

**Read AGENTS.md and this file at the beginning of EVERY task, without waiting for reminders.** This section overrides historical descriptions that accepted post-generation HTML rewrites as permanent implementations.

- **Batch change scope:** Product details, titles, material/capacity copy, FAQ, Blog, locale translations, schema, OG, images, internal links, headers/footers, components, and any large multi-page change **MUST** originate in the relevant shared template/component, canonical source record, or the Cloudflare D1 CMS (the true owner of that field). A reusable postprocessor doing find/replace across generated `dist/**/*.html` is NOT a shared template and is not a compliant final implementation even if it is version-controlled and runs in build_release.
- **Resolve field ownership first:** Determine which value comes from D1, catalog data, the template renderer, and any administrator override. For D1-owned page copy or SEO, correct it in D1/CMS or the schema/renderer that uses D1, never in a hardcoded fallback that silently supersedes an operator change. For template-owned layout, correct the actual shared template/component. Source data and templates may be edited only after confirming which one owns the field.
- **Temporary testing is allowed:** Snapshot/backup and test on disposable generated HTML or fixtures, then discard test edits. The production change must still be implemented upstream and verified from a **clean build**. Never publish a patched `dist/`, hand-edited live HTML, or temporary test output.
- **No regression on future admin updates:** Regression tests must simulate an administrator changing at least one relevant product/Blog/SEO/image/translation/link field and confirm that two clean rebuilds retain the owner's change and do not reinsert old content; new SKUs and approved locales must be allowed.
- **Evidence in every final handoff:** Identify the shared template or D1 record updated (with file path or named table/field), tests performed, CMS override behavior, source rebuild evidence, and production status. If only generated HTML or an obsolete postprocessor was edited, the job is **incomplete** and must not be presented as a finished fix.
- **Legacy migration:** Existing post-render HTML mutation scripts are technical debt to refactor when their feature is next modified. A newly introduced mass rewrite after rendering is prohibited. This priority supersedes existing pipeline comments endorsing old dist postprocessing.
- **Required CI guard:** Check this policy, ignore tracked built HTML, and run the CMS/rebuild regressions before deployment. Never call a policy document alone a complete compliance guarantee; ensure each feature is actually sourced from the right template/database.



1. **Change the source of truth.** Prefer shared page templates, CMS/data inputs
   or versioned build functions. Do not hand-edit generated dist output, edit
   only production HTML, or treat temporary local outputs as a permanent fix.
2. **D1/CMS owner edits take precedence.** Only apply historic curation when
   the field still has the baseline value. New SEO titles, descriptions, photos,
   translated copy and content edited in admin must not be overwritten by
   older cleanup scripts. The cms_seo_curation_guard helper implements this
   policy for curated title/description transforms.
3. **Keep production sources immutable.** Never invent dimensions, materials,
   certifications, MOQ, inventory, manufacturing evidence or changed factory
   model identity. G-series codes are confirmed factory models. Do not replace
   a specific product image without exact source/model visual review.
4. **Guard growth, not a frozen count.** A new approved product, article or
   language page should not fail a release simply because previous totals were
   85, 101, 505 or 755. Detect missing baseline routes and actual broken links.
5. **Rebuild verification is mandatory.** Rebuild from source (the builder
   deletes and regenerates dist), run SEO/locale/Blog/media regressions and
   verify a second clean rebuild produces the same intended outputs. Test
   explicit CMS-edited data before deploying.
6. **No blind deployment.** Publish only when source changes and required tests
   pass; verify the deployed revision and representative production URLs.
7. **No unrequested new features.** Fix the proven defect only and preserve
   unrelated layouts, database, original R2 objects and customer inquiries.

This project policy stays in the repository for future maintainers and code
assistants independently of chat history.

**Entry point for future coding sessions:** [AGENTS.md](AGENTS.md). All
template, metadata, internal-link, Blog and image cleanups must use the same
CMS-priority and repeat-build rules. Source-image URL changes by the owner are
not regressions merely because a legacy rewrite no longer finds its old input.

## 永久执行标准（任何未来建站任务均沿用）
- 先找到**真正数据源/公共模板/正式构建步骤**，再修改；`dist/`、线上 HTML、一次性脚本生成的临时目录只可用于核验，不可作为唯一修复位置。
- 发布时 **D1/CMS 用户编辑优先于旧的 SEO/图片/Blog/内链修复**：后台已有的 OG 图、产品图、缩略图、编辑内容或内部链接不得被强制替换，也不得因为新 URL 与旧源不匹配而阻断构建。
- **支持增长与重复执行**：新增产品、获准的语言和文章不受旧固定总量上限限制；重复执行同一修复须无额外插入、无字段回退。仅保留必要的「已发布基线不丢失」和源真实性校验。
- 必须做**真实 CMS 改写场景测试**：先编辑一个已有 SEO/图片/文章模块，再重跑处理器确认新值不变；然后分别在旧内容、已修内容和新增内容上运行，验证各自行为。
- 每个相关修复把测试加入 `.github/workflows/publish-xuyi.yml`。全站构建和 CI 验证通过后才允许生产发布，并核对 Cloudflare 实际版本。**本政策不等于自动获准部署。**

## 产品容量和定制材料长期统一要求（2026-10-14）
- 现在与未来核实的产品容量，须在五语详情、型号卡片及允许改写的 SEO 中展示 **工厂真实 ml + 海外常用 oz 规格档位**，不再机械整数换算。海外销售档位明确标注 **size class/approximate**，不得将 1000ml 与 32 US fl oz 写成等式，真实容量以源表 ml 为准。全部现有规格用 `data/retail-oz-size-classes.json` 中经审核映射；多容量如 5247/5248 分别对应；未来容量优先匹配有界偏差的常见档位，不合适时明确标注 approx。
- 未经核实的容量不可臆测。G 系列仍是**工厂型号**，但其容量资料未齐，2506 标有异常 60ml，确认前不应追加对应 oz 参数。
- 用户提供 Tritan 与 BPA Free 作为可询价的定制业务方向：所有产品允许展示**定制材料询盘关键词**，但不得把旧目录 PC/PP/ABS 材质直接改为 Tritan、不得称已有成品已获得 BPA Free 认证。询盘时须核对树脂、盖体密封件、样品与测试。
- 唯一入口：`scripts/source_catalog_capacity_oz.py`、`data/volume-oz-cms-baseline-*.json` 和自动化测试。D1/CMS 后台主动改写的 SEO 原文优先；新型号在无后台独立 SEO 文案时自动补充 ml/oz，已有文案则保留。
