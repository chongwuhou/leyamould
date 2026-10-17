# XUYI 全站全面审核：海外常用盎司规格、五语 SEO、源码持久化

日期：2026-10-14（本地 WebCodex 项目 `D:\bendigpt-WebCodex\xuyi-drinkware-site`）。
状态：**本地完成、未推送 GitHub、未生产部署。**

## 审核发现、修正与边界

1. **上一版不合适**：把全部容量机械换算成整数 US fl oz（例如 800ml→27、1000ml→34、1200ml→41、2000ml→68），虽数学上较接近，却不能满足海外采购的常见规格词策略；旧渐变色脚本还写死了 27/34，存在重复覆盖风险。现已把所有营销规格统一路由到 `data/retail-oz-size-classes.json`，旧渐变色处理器只处理经过源资料证明的颜色，不再插入旧盎司词。
2. **真实 ml 与营销 oz class 分开**：元数据、标题、商品卡片、详情都有海外 **oz size class** 或 **approx**；保留工厂实际容量的 ml，页面明示规格档位**并非精确的美国液体盎司换算**。这符合现代美国水杯常见搜索习惯，也不会把「1000ml=32 fl oz」作为错误物理等式。
3. **统一规格映射：23 种有源数据的容量**：

| 工厂实际容量 | 英文市场词（不是精确净容量） | 工厂实际容量 | 英文市场词 |
| --- | --- | --- | --- |
| 380ml | 12 oz class | 400ml | approx. 14 oz |
| 450ml | 16 oz class | 500ml | 16.9 oz class |
| 550ml | 18 oz class | 600ml | 20 oz class |
| 650ml | 22 oz class | 700ml | 24 oz class |
| 750ml | 24 oz class | 800ml | 28 oz class |
| 900ml | 30 oz class | 1000ml | 32 oz class |
| 1100ml | 36 oz class | 1200ml | 40 oz class |
| 1300ml | approx. 44 oz | 1500ml | 50 oz class |
| 1600ml | 56 oz class | 1800ml | 60 oz class |
| 2000ml | 64 oz class | 2200ml | 72 oz class |
| 2300ml | 80 oz class | 2400ml | 80 oz class |
| 3800ml | 128 oz class | | |

对比权威公开零售网页，Owala 的常用 24 / 32 / 40 oz 为明确的真实零售规格档位；小众容量的标签标记为近似的营销类别，不冒充标准认证。美国包装净含量规则强调准确性；上述营销档位不替代真实容量或法规合规标签。

4. **产品结构审核**：101 个在册工厂型号 × 5 个语种 = 505 个本地详情页。92 个真实容量已可判定的型号共 460 页，全部展示源 ml + 国际买家使用的 oz class；3005 个相关产品卡片位置随之更新。**5247/5248 的 450ml 与 700ml 双容量全部保留**，没有只取首个型号。色彩描述源证据明确的 13 个型号保留真实渐变色说明。
5. **容量未确认**：2506 的 `60ml` 历史字段疑似错误，必须查工厂表；本轮在该型号五语详情页添加「原资料 60ml 待核实」警示，同时**修复原代码对货号永久排除的缺陷**：日后 CMS 将该型号容量核实修改为如 600ml，会自动重新纳入海外规格处理。8 个 G 系列是**工厂型号**，但没有可信容量，禁止给这 9 个型号添加虚构的毫升或 oz class。本次对这 9 个型号的 45 个五语详情页的 SEO 描述补齐了明确的定制材料询盘和“容量待确认”表达，旧描述优先保护机制采用单独的 45 条原始 SHA256 基线。
6. **材料与商业声明**：全部 505 页都允许客户就 Custom Tritan / BPA-free Materials 询盘；PC、PP、ABS 及真实目录材质未改成 Tritan；未将材料可定制冒充现成材料，也未增加任何成品认证。后台用户主动编辑的 SEO/title/description 以 D1 快照和校验基线保护，不被早期自动改写覆盖。
7. **SEO / 技术质量**：完整构建产物 971 文件（其中 757 HTML；站点地图 755 URL），自动测试检查五语标题唯一、Meta 长度、每页 canonical、G 系列身份、无图片和链接错误、OG 等。审计扫描不存在已退役的 800ml/27oz、1000ml/34oz、2000ml/68oz、1200ml/41oz、3800ml/129oz 直接展示。静态首页绿色主题由源 CSS 统一管理而非只修改首页 dist。
8. **待解决的 P0 图片事项**：现有 `_local_ops/seo-media-matching-2026-10-13/P0_54_verified_real_SKU_main_photo_queue.csv` 中 54 张待处理照片包含 35 个 P0 精确 SKU 主图与 19 个 P1 其它图位；目前 54/54 的 AI image-to-image 均为 NOT GENERATED，54/54 的审核替换均为 PENDING—original kept。**本轮容量与 SEO 修改没有完成这些图片的生成、真实 SKU 审核或替换**，不能把单项 SEO 回归成功误报成 P0 图片处理完成。
9. **部署/测试边界**：连续两次全站源码构建成功；第二次构建的 10 个核心样本文件 SHA256 完全一致。GitHub Actions 列出的 **54 项 Python 发布测试全部通过**，新增的 `scripts/test_retail_size_class_audit.py` 覆盖 23 种商业映射、101×5 型号页和 45 个未知容量的安全性；`scripts/test_source_catalog_capacity_oz.py` 验证后台编辑优先、无重复注入、未来新增型号等。本地 Windows Runner 没有 Node 命令，工作流中的 JS/Node 检测仍需正式 GitHub CI。线上 xuyibottles.com 的 HTTP 页面不能通过当前网页获取工具读取核验，因此**不得报告生产发布已完成**。

## 项目永久来源

- `AGENTS.md`、`PROJECT_CHANGE_POLICY.md`：改动在可重复的正式模板/CMS 感知构建器实现；不直接以 dist/ 修改为永久修复。
- `data/retail-oz-size-classes.json`：显式来源与近似规格档位（对当前 23 种 ml 容量统一审核）。
- `scripts/source_catalog_capacity_oz.py`：五语产品标题、描述、营销卡片、容量展示以及材料可定制询盘；2506 异常容量提示与其未来 CMS 纠错后的自动恢复。
- `scripts/verified_capacity_gradient_en.py`：仅维护已证明的渐变色文案，兼容旧处理器 API，但不再写入固定 27/34 oz。
- `data/volume-oz-cms-baseline-*.json`：原始 CMS 五语字段指纹；`data/no-volume-source-seo-baseline.json`：45 条未知容量的原始 SEO 指纹。
- `.github/workflows/publish-xuyi.yml`：自动发布测试门禁。
