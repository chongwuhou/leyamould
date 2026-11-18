# XUYI site — durable change rules

> **唯一执行入口：** 具体操作统一按 [XUYI 网站统一执行手册](docs/XUYI_OPERATIONAL_RUNBOOK_ZH.md)。本文件的原则优先级不变；带日期的历史说明仅供追溯。

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


## P0 博客场景图片不可再乱配 / Permanent B2B photo relevance gate（2026-10-29）

每篇新 B 端文章选图须以**标题+买家行业+采购/使用场景**为主，实际看图片并写出具体场景契合理由；不能仅因为含水杯、图片漂亮或自动化检测通过就发稿。同批不复用图片；禁止虚构工厂/客户/真实型号证据。详见 `docs/BLOG_COVER_VISUAL_STANDARD.md`。从 2026-10-29 参考图起，今后审核证据与图片 SHA-256 必须留在 `data/blog-cover-editorial-approvals.json`，通过 `scripts/test_blog_cover_editorial_standard.py` 和 CI；新稿缺完整视觉审核或不匹配时禁止自动发布。真实视觉适配和版权仍需要编辑负责，CI 只验证可机检证据。不得覆盖站长 D1/CMS 图片编辑，不得通过改生成 HTML 兜底。

## 永久执行标准（2026-11-05 定稿：简单、统一、可重复）

核心原则：先读本文件、PROJECT_CHANGE_POLICY.md 和项目圣经；Cloudflare D1/CMS 是运行时唯一事实源。能在正式数据源完成就不另造接口，能复用现有构建入口就不增加新层。所有批量处理必须幂等、条件更新、保留人工修改、可验证、可回滚。

### AI/工具发布与 D1/R2 唯一写入门禁（2026-11-05）

产品、博客、评价、翻译和图片等业务数据必须写入 Cloudflare D1/CMS；图片必须先进入 R2，再由 D1 保存路径、ALT、语言和引用关系。AI 只能生成待审核草稿、翻译初稿和审计结果，不能直接发布或编造事实；工具只能使用已鉴权的正式 D1/CMS、R2 入口，默认 dry-run，条件写入，保留人工值，记录 publish revision。严禁直接改 dist、线上 HTML、Pages 成品或 R2 缓存。完整门禁见 [项目圣经/2026-11-05_统一内容发布与翻译审计标准.md](项目圣经/2026-11-05_统一内容发布与翻译审计标准.md)。


### 产品 SEO

- 每个型号 × 语言独立维护 title、H1、description、OG 和正文；标题与 H1 必须差异化，按真实产品特征组合 B2B、wholesale、OEM、manufacturer/factory、颜色、真实材质、场景和长尾词，禁止整站复用同一句。
- 容量保留工厂真实 ml；海外表达同时给出经审核的 approximate/size class oz，不写成精确等式。没有来源的材质、认证、尺寸、颜色、MOQ、工厂证据不补造。
- 塑料可作为定制方向；Tritan、BPA-free 等只能写成可询价定制，不得冒充现有 SKU 材质或认证。
- D1/CMS 已有人工值优先；只写缺失、旧模板值或明确允许改写的字段。重复执行不得回退、重复插入或覆盖用户修改。

### 博客与评价

- 博客正文在 D1/CMS 编辑并审核；自然放入 2–5 个真实相关产品链接，结尾人工选择 2–3 篇相关阅读，所有 D1 当前已发布语种路径同步检查。图片必须先看正文与画面，记录来源、SHA 和审核结论，不用通用图、旧 SKU 图或虚构工厂/客户证据。
- 评价只接受来源可核验、能精确映射 SKU、未重复的真实内容，并保存 fingerprint、source 和审核状态。AI 只能做草稿、翻译、去重、格式整理与风险筛查；禁止生成虚假体验、补造型号参数或把未经人工/来源审核的内容写入 D1。
- AI 的作用是提效，不是替代事实核验；涉及发布的最终内容须按来源和后台人工修改复核。所有追加或修改采用条件写入，绝不删除、覆盖用户已有数据。

### 固定发布流程

D1/CMS snapshot → 读取当前值和字段所有者 → 条件写入正式数据源 → bump publish revision → 两次干净构建/回归 → 检查 D1 当前已发布语种、canonical/hreflang、sitemap、重复卡片与链接 → 核验代表线上路由。失败停在 CI，不发布临时产物；不要用 dist、线上 HTML 或一次性后处理替代正式修复。




## Blog 静态发布与列表一致性（2026-11-11 定稿）

- 生产 Blog 默认走 Cloudflare Pages 静态构建；D1/CMS snapshot 是唯一内容源。英文和所有后台标记为 enabled + publishReady 的语种，其 /blog/ 列表都从同一份 D1 published blogPosts 生成。
- 列表顺序统一为 D1 查询 `ORDER BY COALESCE(published_at, updated_at) DESC, slug ASC`。多语列表只调整完整卡片的位置，保留 D1 卡片 HTML；不按语言分别排序、不把新卡片追加到末尾、不写死批次 slug。
- `functions/blog/[[path]].js` 保留动态 D1 能力但默认不接管页面，只有显式设置 `XUYI_BLOG_RUNTIME_MODE=dynamic` 才启用；动态入口必须使用同一排序规则。
- 发布门禁必须检查英文和所有发布就绪语种的卡片数量、slug 集合、顺序、单 H1、图片/正文/OG 一致性；任一缺卡、重复卡、额外卡或顺序不一致都停止发布。

## 2026-11-18 根因加固：禁止重复支付同一类成本

近期复盘结论和永久门禁统一见 [docs/XUYI_OPERATIONAL_RUNBOOK_ZH.md](docs/XUYI_OPERATIONAL_RUNBOOK_ZH.md) 第 12 节及 [项目圣经/2026-11-18_近期Bug返工回滚与防复发复盘](项目圣经/2026-11-18_近期Bug返工回滚与防复发复盘.md)。正式 workflow 只允许通用发布入口；Pages Functions 必须先做语法检查；共享渲染器不得依赖历史 HTML 精确替换；旧新组件契约、静态资源版本和并发取消策略必须有自动门禁。任何修复若没有对应回归测试、两次干净构建和线上证据，不得标记完成。
