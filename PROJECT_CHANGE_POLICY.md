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
   historical page/product/locale totals. Detect missing baseline routes and actual broken links.
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
- 现在与未来核实的产品容量，须在全部已配置发布语种详情、型号卡片及允许改写的 SEO 中展示 **工厂真实 ml + 海外常用 oz 规格档位**，不再机械整数换算。海外销售档位明确标注 **size class/approximate**，不得将 1000ml 与 32 US fl oz 写成等式，真实容量以源表 ml 为准。全部现有规格用 `data/retail-oz-size-classes.json` 中经审核映射；多容量如 5247/5248 分别对应；未来容量优先匹配有界偏差的常见档位，不合适时明确标注 approx。
- 未经核实的容量不可臆测。G 系列仍是**工厂型号**，但其容量资料未齐，2506 标有异常 60ml，确认前不应追加对应 oz 参数。
- 用户提供 Tritan 与 BPA Free 作为可询价的定制业务方向：所有产品允许展示**定制材料询盘关键词**，但不得把旧目录 PC/PP/ABS 材质直接改为 Tritan、不得称已有成品已获得 BPA Free 认证。询盘时须核对树脂、盖体密封件、样品与测试。
- 唯一入口：`scripts/source_catalog_capacity_oz.py`、`data/volume-oz-cms-baseline-*.json` 和自动化测试。D1/CMS 后台主动改写的 SEO 原文优先；新型号在无后台独立 SEO 文案时自动补充 ml/oz，已有文案则保留。


## P0 博客场景图片不可再乱配 / Permanent B2B photo relevance gate（2026-10-29）

每篇新 B 端文章选图须以**标题+买家行业+采购/使用场景**为主，实际看图片并写出具体场景契合理由；不能仅因为含水杯、图片漂亮或自动化检测通过就发稿。同批不复用图片；禁止虚构工厂/客户/真实型号证据。详见 `docs/BLOG_COVER_VISUAL_STANDARD.md`。从 2026-10-29 参考图起，今后审核证据与图片 SHA-256 必须留在 `data/blog-cover-editorial-approvals.json`，通过 `scripts/test_blog_cover_editorial_standard.py` 和 CI；新稿缺完整视觉审核或不匹配时禁止自动发布。真实视觉适配和版权仍需要编辑负责，CI 只验证可机检证据。不得覆盖站长 D1/CMS 图片编辑，不得通过改生成 HTML 兜底。

## 永久执行标准（2026-11-05 定稿：简单、统一、可重复）

核心原则：先读本文件、PROJECT_CHANGE_POLICY.md 和项目圣经；Cloudflare D1/CMS 是运行时唯一事实源。能在正式数据源完成就不另造接口，能复用现有构建入口就不增加新层。所有批量处理必须幂等、条件更新、保留人工修改、可验证、可回滚。

### AI/工具发布与 D1/R2 唯一写入门禁（2026-11-05）

产品、博客、评价、翻译和图片等业务数据必须写入 Cloudflare D1/CMS；图片必须先进入 R2，再由 D1 保存路径、ALT、语言和引用关系。工具默认只读或 dry-run，正式写入必须使用已鉴权的正式入口，采用条件写入并记录 publish revision。严禁直接改 dist、线上 HTML、Pages 成品或 R2 缓存。完整门禁见 [项目圣经/2026-11-05_统一内容发布与翻译审计标准.md](项目圣经/2026-11-05_统一内容发布与翻译审计标准.md)。

#### 两种正式操作模式

- **人工模式：** 操作者在后台读取当前 D1/CMS 值，修改正式字段，人工核验事实和语言，审核后写入 D1/CMS，再走标准构建、CI 和线上核验。
- **AI API 模式：** AI API 只生成草稿、翻译初稿、SEO 建议、去重和审计结果；结果先进入 D1/CMS 任务或待审核状态，保存资源 ID、语言、source hash、provider、操作者、时间和错误信息。未经明确授权和人工审核，不得自动发布。
- **API 安全：** 任何付费、限量免费、试用赠金、额度或计费不明确的 API 均禁止；允许的 API 也必须使用受控 Secret，不得写入 D1、GitHub、日志或前台。API 失败、版本冲突、字段缺失或事实无法核验时停止，不强制覆盖。
- **网页翻译边界：** Google Translate 网页不是后台 API，不提供稳定的 D1 自动回写能力；不得使用网页抓取、非官方接口或浏览器自动搬运替代正式翻译任务。需要翻译的内容仍必须通过 D1/CMS 正式审核入口。
- **D1/R2 优先：** 任何操作都先确认字段所有者；后台人工值优先，产品/Blog/评价/翻译写 D1，图片先写 R2 再写 D1 引用。不得用旧静态文件、临时 JSON 或生成 HTML 覆盖正式数据。

### 产品 SEO

- 每个型号 × 语言独立维护 title、H1、description、OG 和正文；标题与 H1 必须差异化，按真实产品特征组合 B2B、wholesale、OEM、manufacturer/factory、颜色、真实材质、场景和长尾词，禁止整站复用同一句。
- 容量保留工厂真实 ml；海外表达同时给出经审核的 approximate/size class oz，不写成精确等式。没有来源的材质、认证、尺寸、颜色、MOQ、工厂证据不补造。
- 塑料可作为定制方向；Tritan、BPA-free 等只能写成可询价定制，不得冒充现有 SKU 材质或认证。
- D1/CMS 已有人工值优先；只写缺失、旧模板值或明确允许改写的字段。重复执行不得回退、重复插入或覆盖用户修改。

### 博客与评价

- 博客正文在 D1/CMS 编辑并审核；自然放入 2–5 个真实相关产品链接，结尾人工选择 2–3 篇相关阅读，全部已配置发布语种路径同步检查。图片必须先看正文与画面，记录来源、SHA 和审核结论，不用通用图、旧 SKU 图或虚构工厂/客户证据。
- 评价只接受来源可核验、能精确映射 SKU、未重复的真实内容，并保存 fingerprint、source 和审核状态。AI 只能做草稿、翻译、去重、格式整理与风险筛查；禁止生成虚假体验、补造型号参数或把未经人工/来源审核的内容写入 D1。
- AI 的作用是提效，不是替代事实核验；涉及发布的最终内容须按来源和后台人工修改复核。所有追加或修改采用条件写入，绝不删除、覆盖用户已有数据。

### 固定发布流程

D1/CMS snapshot → 读取当前值和字段所有者 → 条件写入正式数据源 → bump publish revision → 两次干净构建/回归 → 检查全部已配置发布语种、canonical/hreflang、sitemap、重复卡片与链接 → 核验代表线上路由。失败停在 CI，不发布临时产物；不要用 dist、线上 HTML 或一次性后处理替代正式修复。

#### 直接发布 Blog 的永久默认口径（2026-11-08）

凡用户直接提出“发布、上线、更新 Blog”而未另行限定，默认是英文源文加 D1 `site_state.language_config` 中全部 `enabled=true` 且 `publishReady=true` 语种的完整发布；只发布英文或只写翻译队列不算完成。

针对 AI、localGPT、脚本和自动化工具，整篇文章更新采用 API-only 流程：读取 D1/CMS → 审核图片并上传 R2 → D1 保存媒体引用 → 通过 `/api/admin/blog`、`/api/admin/blog-media`、`/api/admin/page-translations` 等受控入口写入 → bump publish revision → GitHub Actions 标准构建/CI → Cloudflare Pages 部署 → API 与线上 URL 回读。人工操作者可以在正式后台浏览器中编辑和审核，但 AI/脚本/自动化不得打开浏览器后台代替 API，不得直接改 dist、线上 HTML、Pages 成品或 R2 缓存。AI 生成内容只能先形成审核稿；通过事实、语言、SEO/GEO、内链、图片场景和安全门禁后，才可写入正式 D1/CMS。

每篇 B2B Blog 必须有独立标题/H1/搜索意图，正文有 2–5 个真实产品链接、2–3 篇相关阅读、FAQ 或采购清单、清楚的事实边界；各语言必须独立写入正文、列表卡片、ALT、CTA 和元数据，不得英文回退。封面图必须唯一、契合采购场景、清晰压缩为 WebP，记录 R2 路径、尺寸、SHA-256 和编辑插图边界。完成验收要核对 D1/R2、publish revision、构建/部署、全部语言 URL 状态 200、html lang、title/H1、canonical/hreflang、sitemap、列表数量及 D1 顺序；任何一项失败都不能报告为完成。

- **构建失败必须修复源数据或共享模板**：若标准构建因 D1/CMS 字段形状、语言内容或模板门禁失败，必须修正对应正式数据/共享模板并重新走 CI；禁止 AI/脚本/自动化以临时静态文件、浏览器改页面或跳过验证来“补发布”。人工应使用正式后台编辑器修正 D1/CMS。
- **多语 Blog 详情源 HTML必须保留标准品牌眉标**：多语文章正文要保留与共享渲染器兼容的 `blog-meta` 时间线和 `XUYI · ...` 品牌眉标，D1/CMS 更新必须先通过这些源字段门禁再进入静态构建。
- **多语译文任务标记 approved 后仍必须重新构建**：`approve_job` 只是 D1 审核状态变更，不替代发布；完成批量审核后必须 bump revision、重新构建/部署并回读最终线上 URL，避免静态产物落后于 D1。


## 2026-11-08 发布复盘：源头清理与固定执行卡（P0）

本次三篇 B2B Blog 发布暴露出的主要问题已经在源代码层处理，不能靠记忆或聊天上下文补救。以后 localGPT、人工、AI API、脚本和 GitHub Actions 都按本节执行。

### 已清理的硬编码和不合理点

1. **语种不再由代码猜测。** 语言列表、启用状态、可发布状态、URL 前缀和排序全部读取 D1 的 `site_state.language_config`。旧调度器、批量入口和语言队列中的固定 `es/pt/ru/tr` 数组与 SQLite 语言 CHECK 约束已移除；旧表会在保留数据的前提下迁移到无固定语种约束的表。D1 没有语言注册表时只保留英文源语种作为 fail-safe，不得假装完成多语发布。

2. **多语 Blog 列表不再按“本次新增文章”硬推顺序。** 英文运行时列表的 `listBlogPosts(db,"published")` 完整结果是唯一顺序源；其他语种只对自己的 D1 翻译卡片做同序重排，必须保留卡片 HTML、图片、标题和链接。任何数量不一致、重复 slug、缺卡片或条件更新冲突都停止发布。

3. **翻译卡片匹配不再假定目录只有两位字母。** 统一通过 D1 语言注册表中的 `pathPrefix` 解析 `/blog/` 与多语路径，允许将来新增 BCP47 语种，不再使用 `[a-z]{2}` 这样的隐含规则。

4. **已完成的定时任务不再污染活动队列。** `published/cancelled` 历史记录保留在 D1 供审计，但后台活动队列只显示 `scheduled/needs_review`，不会因为历史状态长期显示“待处理”。

5. **静态构建与 D1 不再混用旧快照。** 所有文章、翻译、媒体引用和列表顺序先在 D1/R2 条件写入，再 bump revision，最后由干净构建生成静态页面。审批状态变化本身不等于已发布，必须重新构建并核验线上结果。

### 固定执行卡（每次 Blog 发布/更新照抄）

1. 读取项目圣经、`AGENTS.md`、本文件、D1 当前 revision、`language_config` 和目标资源；先确定字段所有者。
2. API 读取 D1/CMS 当前文章；生成或修改英文源文；事实不明确时停在草稿，不补造容量、材质、认证、MOQ、工厂、客户或评价事实。
3. 读取 D1 中所有 `enabled=true && publishReady=true` 的目标语种，不能自己维护语种数组。英文源文发布成功后，为每个目标语种建立唯一的翻译任务和 source hash。
4. 图片先目视核对主题和采购场景，再压缩为清晰 WebP 上传 R2；成功后把路径、ALT、语言、SHA-256 和引用关系写入 D1。
5. 翻译由人工或当前 AI 会话生成草稿；逐语种审核 title、H1、description、正文、FAQ、CTA、ALT、列表卡片、链接和品牌/产品事实。任何整句英文回退、HTML 不完整、产品链接错误或 source hash 变化都停止。
6. 通过正式 API 条件写入 D1：文章用 Blog CMS 入口，媒体用 Blog Media 入口，页面翻译用 Page Translations 入口；不直接改 dist、线上 HTML、Pages 成品或 R2 缓存。
7. 运行两次干净构建和全部相关 CI；重点检查 Blog 元信息、品牌眉标、FAQ/结构化数据、内部链接、列表数量、D1 顺序、canonical、hreflang、sitemap、图片引用和新增语种兼容性。
8. CI 通过后才部署。API 回读 D1 revision、构建 SHA、R2 HEAD、英文及全部目标语种 URL 状态 200；英文与各语种 Blog 列表必须逐项同序。失败只能报告草稿/待审核，不得报告完成。

### 明确禁止的捷径

- 人工可以使用正式后台浏览器完成编辑、审核和发布；AI、localGPT、脚本和自动化发布不得使用浏览器自动化或网页抓取代替受控 API。Google Translate 网页不是后端发布接口，不能作为自动回写链路；仍不得使用非官方或费用/额度不明翻译 API。
- 不在构建后用一次性正则或脚本修改 `dist/**/*.html` 来掩盖 D1/模板问题。
- 不以固定文章总数、固定语种数、固定产品数或固定分页数作为成功条件；只验证 D1 当前资源的完整性、增长和一致性。
- 不为了通过 CI 临时删除图片、翻译、卡片、评价或 D1 数据；必须修复真正的 D1 记录、共享模板、渲染器或迁移逻辑。

## 2026-11-08 全站源码硬编码审计补充

本轮审计覆盖运行时 Blog CMS、翻译审批、定时发布、语言构建器、产品渲染器、路由校验和发布工作流。新增 `scripts/test_runtime_source_of_truth.py` 并接入 CI。

已移除或改为数据/配置来源：

- 固定语种数组、语种 CHECK 约束、只支持两位字母的 Blog 路径正则；
- Blog 日期标签、已知语言修正词、图库短标题中的语言字典；
- 构建器中固定站点域名、产品图片行截断、固定产品总数断言；
- 产品多语资格不再依赖生成路由清单或“newProduct”标记，而是直接核验已发布 D1 产品记录；
- Blog 排序器和翻译审批器都按路径结构识别 Blog 卡片，不再列举当前语种。

以下属于允许保留的“有意常量”，但不得拿来当业务事实源：安全限制、HTML 安全标签黑名单、状态枚举、URL/slug 格式、人工审核的产品分类映射、历史回放批次和测试 fixture。历史批处理只用于审计/回放，不是日常发布入口。

以后新增语种只需完成 D1 `language_config`、对应审核资源和 D1 翻译记录；若必须改线上业务代码才能加入语种，视为硬编码回归，CI 必须阻止发布。


## 2026-11-08 最终源码复核补充

本次最终复核以 GitHub main 当前提交为准，排除了 dist/、生成的静态页面、图片和项目历史文档，扫描了 460 个受控源码/发布/测试入口，并对关键运行文件逐一做了语法与回归检查。

新增修复已落到源码：产品 SEO 语言校验、产品图片 ALT 导入校验、旧 Blog 批处理、Blog 图片审核、媒体 canonical、Blog 编辑增强和后台路由冲突检查均不再维护固定语种数组；全部改为 D1 language_config、受控站点配置或已审核资源驱动。Blog 动态 Function 的 canonical 也按请求 origin 校验，避免把域名写死在运行逻辑中。

全量扫描仍能看到历史日期批次、一次性迁移/修复接口和测试 fixture 中的固定语种、固定日期或固定域名。这些只保留用于可审计回放，不能作为日常发布入口，也不参与当前 D1 语种、产品数量、Blog 排序或翻译资格判断；新增业务代码不得复制这种模式。线上运行路径的回归规则已继续加入 `scripts/test_runtime_source_of_truth.py`。
