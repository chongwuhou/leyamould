# LEYA MOULD — B2B Static Mould Website

LEYA MOULD Co.,Ltd is the mould-project site at https://leyamould.com.

This repository reuses the verified static-site framework and Pages Functions from the water-bottle project. The water-bottle repository is a read-only reference and is never modified by this project.

## Current source of truth

- Business content, products, page SEO, translations and publish state: this project's Cloudflare D1/CMS.
- Media objects: this project's Cloudflare R2.
- Shared page structure, rendering, tests and release rules: this repository.
- Production target: Cloudflare Pages project `leyamould`, branch `main`.

## Isolation

- D1: `leyamould-d1`, binding `LEYA_DB`.
- R2: `leyamould-r2`, binding `LEYA_ASSETS`.
- Overflow R2: `leyamould-model-pages`, binding `LEYA_MODEL_PAGES`.
- KV: `LEYA_KV`.
- No water-bottle D1 rows, R2 objects, customer inquiries, credentials or historical business content are migrated.

## Company

- Brand: LEYA MOULD
- Legal name: LEYA MOULD Co.,Ltd
- Address: 4-55,Xicheng New Village,Huangyan Taizhou,Zhejiang Province, China
- Mobile / WhatsApp: +86 136 0672 7715
- Email: amyhu@leyamould.com
- Public languages: English and Spanish

## Reference direction

The mould website front-end will follow the information architecture and visual direction of cap-molds.com, with mould categories and technical content cross-checked against hmould.com. Reference-site images are treated as replaceable source material and are not the project's business-data source.

## Checks

**READ BEFORE EVERY TASK:** `AGENTS.md`, `PROJECT_CHANGE_POLICY.md` and [`项目圣经/LEYA统一执行手册.md`](项目圣经/LEYA统一执行手册.md). The repository-level compatibility constraints in `docs/XUYI_OPERATIONAL_RUNBOOK_ZH.md` remain read-only mandatory rules for this mould project; LEYA-specific content, media and release decisions follow the project Bible.

```powershell
python scripts/preflight.py
python scripts/build_release.py
python scripts/test_mould_release.py
```

Do not deploy until DNS, independent bindings, CI credentials and a successful clean build are verified.

