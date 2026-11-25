# XUYI unified publication queue

Status: current architecture

## Purpose

The admin module "11 发布队列（手动）" is the owner control plane for reviewed product reviews and Blog articles. It persists queue configuration and history in XUYI D1. Automatic publication is retired; the browser never contains the Cloudflare project token or any source workbook.

## Default tasks

| Queue | Automatic execution | Time zone | Default time | Daily limit |
|---|---:|---|---:|---:|
| Product reviews | No | Asia/Shanghai | 09:17 (planning only) | 3 |
| Blog articles | No | Asia/Shanghai | 00:00 (planning only) | 3 |

Defaults are inserted with INSERT OR IGNORE; all task rows are forced to `enabled=0`. Existing task history is preserved, but no task can resume automatic execution. Custom queue records can be created, edited, paused, or deleted.

Historical review task settings and ledger rows are retained for reference. They no longer claim work or consume a daily quota.

Blog and review schedule times are retained as planning metadata only. No five-minute heartbeat, task claim, quota consumption, content publication, or build dispatch occurs. The queue remains available for owner review and manual publication through the normal CMS modules.
## Blog editorial gate

A Blog article is scheduled from the existing Blog editor, not generated automatically. Before scheduling:
- the article must remain a draft and contain substantive body content;
- the body must include 2–5 distinct product-model links;
- 2–3 related-article slugs must resolve to already published Blog articles;
- the owner must explicitly confirm that the body, links, related reading, and cover have been reviewed and approved;
- the exact serialized article content is SHA-256 bound to the queue entry.

If the draft changes after scheduling, the hash check moves it to needs_review. Manually publishing or retiring a queued article cancels its pending queue item. Published posts are never auto-published.

## Review source safety

The only accepted source files remain 101-zhenshipingjia.xlsx and 101-additional-reviews-only.xlsx, through their approved private derived JSON payloads. The publisher preserves:
- source-row and SHA-256 fingerprint deduplication;
- the exclusion of the known duplicate customer/SKU attribution;
- multiple distinct customers reviewing the same model;
- the append-only v2 review ledger;
- the historical quota fields, which are no longer consumed by an automatic runner.

No source workbook, derived review payload, or private customer data is copied to dist/ or public R2 storage.

## Execution architecture

- The former five-minute scheduler heartbeat and `/api/admin/scheduler-runner` endpoint are deleted. Scheduled tasks remain visible as queue history, but no background process claims or publishes them.
- The regular `/api/admin/scheduler` CRUD API remains protected by the normal website admin session and rejects resume/enable requests.
- The shared claim and publish functions fail closed when called by stale code, returning a disabled result without changing publication data.
- Manual CMS publication remains available only through its explicit owner authorization and the read-only D1 snapshot build path.
- The site build continues to fetch the authenticated D1 snapshot and deploy the static site after an owner-triggered manual publication.

## D1 tables

- xuyi_publish_tasks: retained queue configuration (all rows disabled).
- xuyi_publish_runs: retained historical execution records; no new automatic claims are created.
- xuyi_blog_schedule: article-level schedule, editorial approval, content hash, and publication state.
- Existing xuyi_product_reviews, review publication ledgers, and Blog CMS tables remain authoritative for content.

All new tables are additive and created idempotently. No existing reviews or articles are deleted or rewritten by scheduler initialization.

## Safety / deployment notes

- Creating the queue tables inserts two disabled default rows and does not publish or queue content automatically.
- No existing Blog article is automatically queued; the owner must use the Blog editor and then publish manually.
- Queue records can be paused or deleted; resume is rejected while automatic publication is retired.
- There is no automatic daily quota consumer. Manual CMS publication still enforces its own content and authorization checks.

