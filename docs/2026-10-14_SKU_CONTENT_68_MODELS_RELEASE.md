# XUYI 产品正文差异化第四批发布审计 — 2026-10-14

## 本轮准确范围
- 101 个工厂源型号 × 五语=505 产品详情页（不把 Products 列表计作第 102 款）。
- 前三批 54 型号；新增 14 型号 × 五语=70 个详情页；**累计 68 型号、340 页**，剩余 33 型号。
- 运动杯 6 型号：2458、2459、2309、2403、2401、2406；儿童杯 4 型号：2315、2316、2411、2412；大容量水壶 4 型号：2282、2306、2308、2418。
- 资料核验来自已有目录源及 CMS 快照：容量、尺寸、材质组合、外观颜色、独立包装、装箱数与外箱规格。未推断杯盖结构、手柄、密封强度、年龄认证、BPA-Free 成品认证、库存、MOQ 或真实照片。
- 2316/2318、2306/2305、2308/2307 等多项核心参数相同的型号不编造结构差异，只记录真实颜色、数据与供应商确认问题。

## 正式源码修改和字段归属
- `data/phase4-next14-openings-{en,es,pt,ru,tr}.json`：70 篇真实型号对应的独立采购段落；英语及四语各 100–150 词。
- `data/phase4-next14-locale-addenda.json`：对少量俄语/土耳其语型号段落补足核验内容。
- `data/phase4-next14-d1-baselines.json`：冻结每个型号翻译 `mainHtml` 字段的四语 SHA256 源指纹，只在 CMS 正文未由站长改写时自动注入已核实的开头。
- `sku_unique_openings_phase2.py`：在原本的正式源渲染阶段合并第四批数据，沿用 `sku_unique_openings.py` 的 D1 优先逻辑；不在构建后修改 `dist` HTML。
- `scripts/test_phase4_fourteen_unique_sku_openings.py`：严格检查 14 款、70 路由、五语、单次注入、已改写文本幂等、模拟 CMS 用户修改不可覆盖、未来新增型号不受旧型号数限制；加入 `.github/workflows/publish-xuyi.yml` 门禁。
- `scripts/prepare_product_copy_queue.py` 重新生成 33 个剩余型号的目录资料与相似度排序，生成文件为 `_local_ops/phase2-remaining-sku-priority.csv`，**下批不虚构未核实差异**。

## 审计结果
- `scripts/audit_product_body_similarity.py` 以五语对应、同类别最近邻、屏蔽数字的可见正文三元词组 Jaccard 作诊断，**不是搜索引擎的处罚阈值**。
- 本批固定 14×5=70 页：开头最近邻相似度中位数 **1.000 → 0.0309**，完整产品主体 **0.9926 → 0.8040**。
- 全站已优化英语 68 页：主体中位数约 **0.800**，未优化 33 页主体中位数 **0.986**；其余五语已优化主体中位数 ES 0.809 / PT 0.800 / RU 0.784 / TR 0.783。
- 基线及新审计明细在 `_local_ops/product-body-similarity-before-phase4-2026-10-14.json`、`_local_ops/product-body-similarity-2026-10-14.json`。

## 本地质量门禁
- 两次 `python -B scripts/build_release.py` 全站干净构建通过，生成 973 文件、757 HTML、505 产品详情、755 sitemap URL。
- 首页、站点地图及本批 14×5 页共 72 个文件 SHA256 相同，无二次构建漂移。
- 13/13 Python 回归通过：网站链接、首批内容、第二至四批独立内容、五语 SEO、CMS 编辑优先、SEO 元数据、G 系列厂内身份、产品 Sitemap 图片。
- 用户原本有 54 张低清图片待处理，本轮未变动任何产品图片、R2 原始对象和 D1 询盘。

## 发布前后要求
- 把正式源码、数据、回归门禁和本报告一并提交 GitHub `main` 后，经 GitHub Actions 全部测试、Cloudflare Pages 生产发布与线上版本核查成功才可宣称上线。