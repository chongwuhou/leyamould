> **历史记录，盎司旧版本已失效：**本文件包含直接取整换算得到的 27/34/41/68 oz 等过时示例，只用于追溯旧操作，不得重新部署或作为当前 SEO 规格来源。**现行规则与全部 23 种市场档位请以 `docs/2026-10-14_RETAIL_OZ_FULL_SITE_AUDIT.md`、`data/retail-oz-size-classes.json` 和 `AGENTS.md` 为准。**

# XUYI 全部容量 US fl oz 同步与 Tritan / BPA Free 定制搜索词

日期：2026-10-14；执行标准：项目 `AGENTS.md` 和 `PROJECT_CHANGE_POLICY.md`。

## 全站修改，非一次性 HTML 修补

- 正式构建入口 `scripts/build_release.py` 新增 `source_catalog_capacity_oz.apply(DIST)`，后续任意完整发布都会重新生成。
- 动态读取 `site_renderer.SERIES` 中本次 CMS 覆盖后的容量，不按 800/1000ml 或历史 85 条目录固定列表执行。
- **美制液体盎司**换算：每 1 US fl oz = 29.5735295625ml；SEO Title / 页面标题可简写 `oz`，说明与容量标注使用 `US fl oz` 以区分质量盎司及英制液体盎司。营销场景采用最接近的整数。
- 例如：380ml (13 oz)、500ml (17 oz)、550ml (19 oz)、600ml (20 oz)、650ml (22 oz)、700ml (24 oz)、750ml (25 oz)、800ml (27 oz)、1000ml (34 oz)、1200ml (41 oz)、1500ml (51 oz)、1800ml (61 oz)、2000ml (68 oz)、3800ml (128 oz)。
- 当前 101 个型号中：**92 个已核实容量型号 × 五语言 = 460 个详情页**增加准确容量标记；3005 个产品卡片补充容量标签和站内搜索语料；所有 101×5 = 505 个产品详情页展示材料**定制采购询盘**。
- 5247、5248 已有 450ml / 700ml 两种源数据，显示 **450ml (15 US fl oz) / 700ml (24 US fl oz)**；不能只取第一种。
- 原记录 `2506` 的异常 `60ml` 暂不换算（需验证源容量）；八个 G 系列仍是 XUYI **工厂型号**，没有核实容量前不附加虚构 ml/oz；一旦有真实 D1 容量可自动追加。
- 五语 Title / Description 依据审核过的 CMS/源 SEO 指纹，仅在数据原样时自动改写。保存的来源校验表：`data/volume-oz-cms-baseline-{en,es,pt,ru,tr}.json`；后台对任何一项 SEO 字段的主动修改将保护该型号两项 SEO 字段。后续新批准型号若无独立 CMS Title/Description 则自动生成准确的 ml/oz SEO；已有自定义文案不强行覆盖。

## Tritan 与 BPA Free 描述准确性

全站五语产品详情的「定制材料询盘」中均可搜索 `Tritan`、`BPA-free` 等词。源目录中的 PC、PP、ABS 等现有材质原封不动，不能把以下采购询盘写成已被确认的物料/整杯检测结果。

推荐英文询盘语义：

> Custom Tritan and BPA-Free Options — Ask for a Quote. Ask whether a Tritan copolyester body and BPA-free material specification can be customized for this exact model. Confirm resin, lids, seals, samples and finished-product testing.

所有可编辑 SEO Description 也增加材料采购搜索词和明确的定制语义。Tritan 是 Eastman 的品牌共聚酯，Eastman 官网说明这种材料本身 BPA-free；但用户的某个现有 SKU 是否实际采用 Tritan、可否更换整个材料及是否能达到某目标市场的完整成品检测标准仍须对应样品确认。

## 验证/未执行项

- 2 次全站源码重建，代表页面共 10 条的 SHA256 一致。
- 53 项正式 GitHub Actions Python 发布门禁回归全部通过（包括 `scripts/test_source_catalog_capacity_oz.py`），涵盖五语模型、全站容量、已改 CMS SEO 的数据优先权、非重复追加、多容量以及后续新增型号。
- 官方流程还有 16 项 Node.js / JS 验证：当前本地 Windows Runner 没有 Node 可执行程序，本次不能证明这些已通过；正式 GitHub CI 仍需核实。
- 本次未更改生产 D1、R2 和 Cloudflare Pages；**本地文件构建成功并不等于线上 xuyibottles.com 已发布**。