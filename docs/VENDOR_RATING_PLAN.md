# Vendor Rating & Feedback — Detailed Plan (DRAFT, NOT IMPLEMENTED)

> Status: **IMPLEMENTED** (owner approved "build it"). Migration 0010 applied;
> service + 5 endpoints built; citizen card, marketplace counts, vendor strip,
> DISCOM flags live. `tsc`, backend pytest (60), frontend vitest (113) green.
>
> Goal: citizens rate completed vendor work (1–5 + tags + comment); the live
> average follows the vendor everywhere (marketplace, profile, DISCOM queue);
> sustained bad ratings flag the vendor so DISCOM can warn, suspend, or reject
> — and reinstate. Closes the accountability loop the marketplace today lacks:
> `vendors.rating` exists as a column but **nothing ever writes it**.

## 1. Current state (verified)

| Piece | Location | Behaviour |
|---|---|---|
| `vendors.rating numeric(3,2)` + `completed_installations` | migration 0001 | Display-only columns; no write path exists |
| Rating display | `VendorList.tsx:108`, `VendorMap.tsx:298`, vendor `profile/page.tsx:146` | Shows `x.x / 5` or "not rated"; profile notes rating is DISCOM-set (today: never) |
| DISCOM vendor powers | `routes_vendors.py:325 review_vendor` (APPROVED/REJECTED/UNDER_REVIEW/SUSPENDED) + `discom/vendors/page.tsx` | Suspend/reject/reinstate already work; queue shows no quality signal |
| Engagement proof | `appointments` (citizen→vendor) + `installations.application_id` unique | Exactly who hired whom, per application — the anti-fake-review anchor |
| Completed-work proof | `installations` + new 0009 report columns | Rating eligibility can require real completed work |

## 2. User flow

```
installation VERIFIED (existing close)
  → citizen sees "Rate this installer" on their application (once per vendor engagement)
  → 1–5 stars + quick tags + optional comment → submit
  → vendor average updates everywhere instantly
  → avg < 2.5 or ≥2 one-star reviews in 90d → ⚠️ flag on DISCOM queue
  → DISCOM: warn (notes) / SUSPEND (hidden from marketplace) / REJECT / reinstate
  → suspended vendor's in-flight installations stay visible; no new leads
```

## 3. Pages

### P1 — Citizen: rate card (NEW block on `citizen/applications/[id]`)
Shown only when: application has a VERIFIED installation with a vendor AND no
review by this citizen for that vendor+application yet. Elements: 5-star input,
tag chips (`On time`, `Clean work`, `Good communication`, `Transparent pricing`,
`Poor finishing`, `Delays`, `Unprofessional`), comment box (500 chars), submit.
After submit: read-only "You rated X/5" + edit-once window (7 days, then locked).

### P2 — Vendor marketplace + profile (UPGRADE, existing components)
`VendorList`/`VendorMap`/profile show `★ avg (n reviews)`; new `GET
/api/vendors/{id}/reviews` public summary (latest 10, tags histogram). Vendor's
own dashboard gets a "My ratings" strip (avg trend, recent comments).

### P3 — DISCOM vendor queue (UPGRADE, `discom/vendors`)
New columns: `★ avg (n)` + `⚠️ quality flag` (rule §6); review drill-down
(stars, tags, comments, per-application link); existing
approve/reject/suspend/reinstate buttons unchanged, now quality-informed;
suspend requires reason → stored in `rejection_reason`, audited, vendor sees it
on their dashboard.

## 4. Review fields (citizen-submitted, DISCOM/vendor-read)

| # | Field | Type | Required | Rules |
|---|---|---|---|---|
| 1 | `rating` | int 1–5 | yes | stars; 1–2 must pick ≥1 negative tag or write a comment |
| 2 | `tags` | text[] from fixed list | ≥1 if rating ≤2 | allow-list enforced server-side (no freeform abuse vector) |
| 3 | `comment` | text(500) | no | profanity/length server-trimmed; hidden if vendor disputes? No — see §8 |
| 4 | `application_id` + `vendor_id` | uuid | system | must match an engaged pair (appointment or installation) owned by caller |
| 5 | edit window | — | — | one edit within 7 days; original kept in audit |

One review per (citizen, vendor, application). Re-installations for the same
citizen by the same vendor on a *new* application may review again.

## 5. API contracts (new)

| Method / path | Actor | Behaviour |
|---|---|---|
| `POST /applications/{id}/vendors/{vid}/reviews` | citizen (owner) | Eligibility: engaged pair + installation exists with status ≥ INSTALLED; upserts within window; recomputes average |
| `GET /applications/{id}/vendors/{vid}/reviews/eligibility` | citizen | `{eligible, reason}` drives the rate-card visibility |
| `GET /vendors/{id}/reviews` | public | avg, count, tag histogram, latest 10 (no citizen PII beyond first name + initial) |
| `GET /vendor/ratings` | vendor | own avg, trend, all comments on their work |
| `GET /discom/vendors/ratings/flags` (or extend review list) | DISCOM | vendors breaching §6 rule with supporting review excerpts |

## 6. Database (migration `0010_vendor_reviews`)

```sql
create table public.vendor_reviews (
  id uuid primary key default gen_random_uuid(),
  application_id uuid not null references public.solar_applications(id) on delete cascade,
  vendor_id uuid not null references public.vendors(id) on delete cascade,
  citizen_id uuid not null references public.profiles(id) on delete cascade,
  rating smallint not null check (rating between 1 and 5),
  tags text[] not null default '{}',
  comment text check (comment is null or char_length(comment) <= 500),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint one_review_per_engagement unique (citizen_id, vendor_id, application_id)
);
-- average maintained by trigger on insert/update/delete:
-- vendors.rating = rounded avg, vendors updated_at touched; NULL when no reviews
-- RLS: citizens INSERT own rows only where an engagement exists; SELECT own +
--   vendors read theirs; DISCOM/service full read (existing patterns)
```

Quality-flag rule (computed, not stored): `avg < 2.5 with n ≥ 3`, OR `≥2
ratings of 1★ within 90 days`. Vendors below `n < 3` show "too few reviews",
never a flag — protects newcomers from one angry outlier.

## 7. Extra features analyzed (recommendations)

| Feature | Verdict | Reason |
|---|---|---|
| Eligibility = real engagement + installation ≥ INSTALLED | **include** | Kills fake/bot reviews at the root; uses existing tables |
| Edit-once (7d) + audit of originals | **include** | Corrects fat-finger 1★ without enabling harassment edits |
| Fixed tag allow-list, server-enforced | **include** | Structured signal for DISCOM (`Delays ×6`) without free-text abuse |
| Newcomer guard (`n < 3` → no flag) | **include** | One bad review must not suspend a business |
| Suspend hides from marketplace, keeps in-flight work visible | **include** | Matches existing `is_active`/`visible_to_customers` semantics |
| Review disputes / vendor replies | **defer** | Real need, but doubles scope; public comments + DISCOM judgement suffice for SIH |
| Photo in review | **defer** | Completion photos already give DISCOM evidence |
| Rating-weighted vendor ranking / auto-suspend | **reject** | Ranking may inform sort later; suspension must stay a human DISCOM decision with reason + audit |

## 8. Security / honesty rules

* Citizens review only vendors they engaged (appointment/installation join),
  once per application; RLS + service checks both.
* No citizen PII in public summaries (first name + initial only).
* Averages are trigger-maintained from stored rows — recomputable, never
  hand-edited (profile page keeps its "set by the system" note, now true).
* Suspend/reject/reinstate keep today's flow + reason + audit; vendor sees the
  reason on their dashboard.

## 9. Acceptance criteria

1. Post-VERIFIED citizen sees rate card once; submits 5★ + tags → avg updates on marketplace/profile/queue instantly.
2. Ineligible citizen (no engagement) → 403; double-submit → 409; edit after 7d → 422.
3. Flag appears exactly under the §6 rule; newcomer with one 1★ shows no flag.
4. DISCOM suspends flagged vendor → hidden from citizen marketplace, in-flight work intact, reason visible to vendor; reinstate restores.
5. `tsc`, `pytest`, migration clean on fresh + existing DB.

## 10. Build order (after approval)

1. Migration 0010 + trigger + RLS → 2. review endpoints + eligibility + public summary →
3. P1 citizen rate card → 4. P2 marketplace/profile surfaces → 5. P3 DISCOM flags + drill-down → 6. tests.
