# XUYI unified scheduled publishing

Updated: 2026-11-02

## Purpose

The admin module "10 自动发布与定时任务" is the owner control plane for both authentic product reviews and reviewed Blog articles. It persists task configuration and execution history in XUYI D1. The browser never contains the Cloudflare project token or any source workbook.

## Default tasks

| Task | Enabled on first initialization | Time zone | Default time | Daily limit |
|---|---:|---|---:|---:|
| Product reviews | Yes | Asia/Shanghai | 09:17 | 3 |
| Blog articles | Yes | Asia/Shanghai | 00:00 earliest check | 3 |

Defaults are inserted with INSERT OR IGNORE; existing owner settings are never overwritten by subsequent schema checks. System default tasks can be paused or edited, but not deleted. Custom tasks can be created, edited, paused, resumed, and deleted.

Review tasks run once per configured local date. The review publication ledger and daily cap use Beijing calendar dates, so review tasks are restricted to Asia/Shanghai. Multiple active review tasks contribute to one global daily quota; each task also has its own per-run limit. A review task first created after its scheduled time on a given day is intentionally deferred until the next day, avoiding an unexpected immediate batch on initial activation.

Blog tasks poll every five minutes after their configured earliest-check time. Each Blog article has its own scheduled Beijing timestamp in the Blog editor. Multiple active Blog tasks contribute to one global daily quota, and each task also has its own per-task daily limit. All review and Blog daily quotas reset on the Beijing calendar date, regardless of a task's selected execution time zone. The sum of enabled task limits is the Blog-wide daily cap; both content-type totals are shown in the admin scheduler and calculated from D1. A queued article is not eligible until its exact scheduled timestamp has passed.
## Blog editorial gate

A Blog article is scheduled from the existing Blog editor, not generated automatically. Before scheduling:
- the article must remain a draft and contain substantive body content;
- the body must include 2–5 distinct product-model links;
- 2–3 related-article slugs must resolve to already published Blog articles;
- the owner must explicitly confirm that the body, links, related reading, and cover have been reviewed and approved;
- the exact serialized article content is SHA-256 bound to the queue entry.

If the draft changes after scheduling, the hash check moves it to needs_review and prevents publication. Manually publishing or retiring a scheduled article cancels its pending queue item. Published posts are never auto-published a second time.

## Review source safety

The only accepted source files remain 101-zhenshipingjia.xlsx and 101-additional-reviews-only.xlsx, through their approved private derived JSON payloads. The publisher preserves:
- source-row and SHA-256 fingerprint deduplication;
- the exclusion of the known duplicate customer/SKU attribution;
- multiple distinct customers reviewing the same model;
- the append-only v2 review ledger;
- a server-enforced daily quota derived from enabled review tasks.

No source workbook, derived review payload, or private customer data is copied to dist/ or public R2 storage.

## Execution architecture

- GitHub Actions runs a five-minute scheduler heartbeat from the private repository's main branch.
- The runner uses the existing CLOUDFLARE_API_TOKEN secret. The dedicated /api/admin/scheduler-runner endpoint accepts only POST and verifies that token against this exact Cloudflare Pages project.
- The regular /api/admin/scheduler CRUD API remains protected by the normal website admin session.
- D1 task claims are idempotent: review tasks claim once per task/date; Blog tasks claim once per five-minute local-time bucket. The GitHub workflow has a concurrency group to prevent overlapping scheduler runs.
- On a successful D1 publication, the runner dispatches the existing publish-xuyi.yml workflow so the static pages rebuild promptly. The existing 30-minute revision poll remains a fallback.
- The site build continues to fetch the authenticated D1 snapshot and deploy the static site. A scheduled article becomes visible on the static website after that build finishes.

## D1 tables

- xuyi_publish_tasks: recurring task configuration.
- xuyi_publish_runs: idempotent claims and execution history.
- xuyi_blog_schedule: article-level schedule, editorial approval, content hash, and publication state.
- Existing xuyi_product_reviews, review publication ledgers, and Blog CMS tables remain authoritative for content.

All new tables are additive and created idempotently. No existing reviews or articles are deleted or rewritten by scheduler initialization.

## Safety / deployment notes

- Creating the scheduler tables seeds the two default task rows but does not publish any content.
- No existing Blog article is automatically queued; the owner must schedule a draft in the Blog editor.
- Pausing a task prevents new claims. Resuming permits the next due task check.
- Daily quotas are enforced server-side; changing the UI alone cannot bypass them.
- Do not deploy the scheduler workflow until the Cloudflare project token and GITHUB_TOKEN workflow permission are available. Do not run the scheduler against production during a dry-run or validation pass.