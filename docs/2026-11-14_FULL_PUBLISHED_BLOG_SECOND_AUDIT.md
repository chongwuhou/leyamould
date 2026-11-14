# 2026-11-14 全量已发布文章二次审核记录

- 范围：97 篇已发布英文源文、后台配置的 4 个目标语种、485 个文章详情 URL。
- 目标：保持所有既有 slug、路径、canonical、hreflang 和文章链接不变；正文、FAQ、检查清单、真实产品内链和相关阅读以 D1/CMS 为源。
- 本次修复：统一已发布文章的内容深度和多语种页面；旧英文静态 slug 通过 D1 完整文章行渲染；英文产品内链通过 D1 product_notes 生成；发布前检查 D1 revision、source revision 和 build-meta 必须同时一致。
- 最终门禁：D1 写入完成、构建通过、线上 485 页状态和结构复核通过后，才可对外宣称完成；旧 Actions 任务不得覆盖最新 source revision。
