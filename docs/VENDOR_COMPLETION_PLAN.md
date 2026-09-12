# Vendor Installation Completion Report — Detailed Plan (DRAFT, NOT IMPLEMENTED)

> Status: **IMPLEMENTED** (owner approved all four §11 decisions). Migration
> 0009 applied; backend + vendor workspace + DISCOM review + citizen banner
> built; `tsc`, backend pytest (60) and frontend vitest (113) green.
>
> Goal: after a vendor picks an installation, they file a **completion report**
> (equipment, capacity, dates, photos, checklist, remarks). Submitting it moves
> tracking `INSTALLING → INSTALLED → (submit) → awaiting verification`; DISCOM
> verifies (or returns for correction) to close the application as `VERIFIED`.
> The citizen tracker follows automatically through the existing status-history
> trigger — no tracker change required.

---

## 1. Current state (verified against the repo)

| Piece | Location | Behaviour |
|---|---|---|
| Vendor installations list | `frontend/app/vendor/installations/page.tsx` | Status buttons `PENDING → … → VERIFICATION_PENDING` + one `installed kW` box. No detail fields. Stage-skipping possible. |
| Status update API | `POST /vendor/installations/{id}/status` (`routes_vendor_portal.py:195`) + `vendor_portal.update_installation_status` (`vendor_portal.py:239`) | Accepts `status + installed_capacity_kw`; stamps `started/completed_at`; **mirrors to application** (`IN_PROGRESS→INSTALLING`, `COMPLETED/VERIFICATION_PENDING→INSTALLED`); refuses `VERIFIED` (403). Audited. |
| DISCOM verify | `POST /discom/installations/{id}/verify` + `frontend/app/discom/installations/page.tsx` | Sole path to `VERIFIED`; sets `discom_verified*`, flips application to `VERIFIED`. Reviewer sees only kW + applicant/bus today. |
| Tracker | `lib/tracking.ts` + `ApplicationTracker.tsx` | Stages `Installer chosen → Installation → Verified` driven by `application_status_history` trigger. `VERIFIED` is terminal. |
| Uploads | `POST /vendor/documents/upload` + `get_storage_service()` | Validated (size, allow-list, magic bytes), server-side keys. Document types from `scheme_config` (`VENDOR/document_types`). |
| Guards | migration `0004` grants; `discom_verified*` columns revoked for clients | Vendors cannot self-verify even with a valid token. |

## 2. User flow (happy path)

```
vendor picks installation (exists: claim/accept lead)
  → SITE_VISIT → SCHEDULED → IN_PROGRESS            (vendor, sequential)
  → fills COMPLETION REPORT (new form, §4)
  → COMPLETED (report stored, app = INSTALLED)
  → SUBMIT FOR VERIFICATION → VERIFICATION_PENDING  (app stays INSTALLED)
  → DISCOM reviews report + photos (§5)
      → VERIFIED  (app = VERIFIED, tracker greens, CLOSED)
      → RETURNED with reason (installation = IN_PROGRESS, app = INSTALLING,
        vendor sees reason, fixes, resubmits)
citizen tracker: Installer chosen ✓ → Installation ✓ → Verified ✓ (automatic)
```

## 3. Pages

### P1 — Vendor: Installation workspace (NEW, `frontend/app/vendor/installations/[id]/page.tsx`)
Currently the vendor has only a list with jump-buttons. New per-installation
page with three blocks:
1. **Header**: application number, applicant (vendor-visible fields only, per
   `VendorVisibleApplication`), bus, approved kW, category ceiling
   (`capacity_limits.py`: Residential 1–10, others 1–500), current statuses.
2. **Progress stepper** (sequential, server-enforced): `PENDING → SITE_VISIT →
   SCHEDULED → IN_PROGRESS → COMPLETED → VERIFICATION_PENDING → VERIFIED 🔒`.
   Next-allowed transition only; completed steps show timestamps
   (`started_at/completed_at`).
3. **Completion report form** (§4) + **Submit for verification** button
   (enabled only when report validates complete and status is `COMPLETED`).
   Read-only mirror once submitted; DISCOM return-reason banner if returned.

Existing list page keeps its rail; each card links into the workspace.

### P2 — DISCOM: verification review (UPGRADE, `frontend/app/discom/installations/page.tsx`)
Awaiting-verification cards gain:
* Full completion report (§4 fields) + photo thumbnails (signed URLs, existing
  `document_url` endpoint).
* **Variance flag**: `installed vs approved kW` (amber ≥10% off, red outside
  category ceiling), `installed vs category ceiling` check.
* Two actions: **Mark verified** (existing, + notes) and **Return for
  correction** (new: reason required → installation `IN_PROGRESS`,
  application `INSTALLING`, reason visible to vendor + citizen tracker stays
  on Installation with the return note in history).

### P3 — Citizen: returned-banner (small, explicit)
Tracker needs no change (re-entering `INSTALLING` renders automatically), but
a return must be **visible, not tracker-only**: the citizen application page
shows `⚠️ Installation returned by DISCOM for correction` + the short reason
(sourced from the latest history note / installation `return_notes`) until the
vendor resubmits. One banner component, no new route.

## 4. Completion report fields (vendor-submitted, DISCOM-read)

| # | Field | Type | Required | Validation / source |
|---|---|---|---|---|
| 1 | `installed_capacity_kw` | number, kW, 0.1 step | yes, at COMPLETED | ≤ category ceiling (`capacity_limits.py`); variance vs approved `new_pv_kw` flagged ≥10% |
| 2 | `panel_make` | text(100) | yes | free text, e.g. "Tier-1 550W vendor" |
| 3 | `panel_model` | text(100) | yes | free text |
| 4 | `panel_count` | integer ≥1 | yes | cross-check: `panel_count × rated W ≈ installed kW` (±15% **warning only, never blocks** — DC/AC sizing differences are legitimate) |
| 5 | `panel_watts_each` | integer ≥1 | yes | drives the cross-check in (4) |
| 6 | `inverter_make` | text(100) | yes | free text |
| 7 | `inverter_model` | text(100) | yes | free text |
| 8 | `inverter_capacity_kw` | number >0 | yes | must be ≥ `installed_capacity_kw` (undersized inverter blocks submit) |
| 9 | `install_date` | date | yes | not future, not before `started_at` |
| 10 | `completion_notes` | text(2000) | no | free remarks (shadow, roof issues, deviations) |
| 11 | `checklist` | 6 booleans | all true to submit | modules torqued · wiring/MCB · earthing · net-meter paperwork · generation test · customer demo |
| 12 | `photo_document_ids` | uuid[] (≥2) | yes | uploaded via existing `/vendor/documents/upload`; new types `completion_photo`, `commissioning_test` in `scheme_config` |
| 13 | `submitter_confirm` | boolean | true to submit | "Work matches the approved capacity and the photos are of this site" |

Read-only after submit; editable again only if DISCOM returns it.

## 5. API contracts (new/changed)

| Method / path | Actor | Behaviour |
|---|---|---|
| `PATCH /vendor/installations/{id}/report` (new) | vendor (owner only) | Upsert §4 fields; allowed in `IN_PROGRESS/COMPLETED`; `VERIFIED`/verified rows refused |
| `POST /vendor/installations/{id}/submit` (new) | vendor | Validates §4 completeness + checklist + photos + inverter rule → `COMPLETED → VERIFICATION_PENDING`; audit `vendor.installation.submit` |
| `POST /vendor/installations/{id}/status` (exists, tightened) | vendor | Sequential transitions only (new service guard); `VERIFIED` still 403 |
| `POST /discom/installations/{id}/return` (new) | DISCOM | `→ IN_PROGRESS` + reason; application `→ INSTALLING`; audit; reason stored as `return_notes` + history note |
| `POST /discom/installations/{id}/verify` (exists) | DISCOM | Unchanged, still the sole `VERIFIED` path |
| `GET /vendor/installations` / detail (exists) | vendor | Extended payload: report fields + return history + variance flags |

## 6. Database (migration `0009_installation_completion_report`)

```sql
alter table public.installations
  add column if not exists panel_make text,
  add column if not exists panel_model text,
  add column if not exists panel_count integer check (panel_count is null or panel_count >= 1),
  add column if not exists panel_watts_each integer check (panel_watts_each is null or panel_watts_each >= 1),
  add column if not exists inverter_make text,
  add column if not exists inverter_model text,
  add column if not exists inverter_capacity_kw numeric(10,3),
  add column if not exists install_date date,
  add column if not exists completion_notes text,
  add column if not exists checklist jsonb not null default '{}',
  add column if not exists photo_document_ids uuid[] not null default '{}',
  add column if not exists return_notes text,
  add column if not exists returned_at timestamptz;
-- grants (0004 pattern): vendors UPDATE new columns only; discom_verified* untouched
grant update (panel_make, panel_model, panel_count, panel_watts_each,
  inverter_make, inverter_model, inverter_capacity_kw, install_date,
  completion_notes, checklist, photo_document_ids) on public.installations to authenticated;
```

  `photo_document_ids` references existing `vendor_documents` rows (signed-URL
  reads already exist). No new bucket, no new table. Constraint is additive;
  existing rows read as "report not filed".
  Upload allow-list: `scheme_config (VENDOR/document_types)` already held 6
  business types, so `COMPLETION_PHOTO` + `COMMISSIONING_TEST` were added to
  that live row (both `required: false`; profile page may also offer them).

## 7. Tracking / status map (no tracker code change)

| Installation | Application | Tracker stage |
|---|---|---|
| SITE_VISIT / SCHEDULED | VENDOR_SELECTED | Installer chosen (current) |
| IN_PROGRESS | INSTALLING | Installation (current) |
| COMPLETED | INSTALLED | Installation (done→awaiting) |
| VERIFICATION_PENDING | INSTALLED | Installation (current, "awaiting DISCOM") |
| RETURNED → IN_PROGRESS | INSTALLING | Installation (current again + note) |
| VERIFIED | VERIFIED | Verified ✓ terminal |

All transitions via service-role writes the status-history trigger already
records (same mechanism as today).

## 8. Security / honesty rules carried over

* Vendors write only their own installations (`_own` check); `VERIFIED` +
  `discom_verified*` unreachable (service 403 + RLS + revoked grants).
* Capacity validated against `capacity_limits.py` + approved kW; variance is a
  visible flag, never an auto-rejection of honest deviations.
* Photos must be ≥2, uploaded files (magic-byte checked), never URLs.
* Every transition audited (`vendor.installation.submit`,
  `installation.returned`, existing verify rows).

## 9. Acceptance criteria

1. Vendor files a full report on a picked installation → COMPLETED → submit →
   VERIFICATION_PENDING; tracker shows Installation current with timestamps.
2. DISCOM sees report + photos + variance flag; verify closes to VERIFIED
   (tracker green) or return reopens with reason vendor-side.
3. Negative: skip-step submit refused (422); vendor VERIFIED attempt 403;
   vendor B on vendor A's installation 403; undersized inverter blocks submit;
   <2 photos blocks submit.
4. `tsc`, `pytest`, `verify_phase1.py` green; migration applies cleanly on a
  fresh + existing DB (NOT VALID-safe).

## 10. Build order (after approval)

1. Migration 0009 + grants → 2. service + 3 new endpoints + guards →
3. P1 vendor workspace → 4. P2 DISCOM upgrade → 5. negative tests + docs.

## 11. Owner decisions (locked)

1. Panel cross-check ±15% → **warn only, never block** (DC/AC sizing is legitimate).
2. Photo minimum **2** (rooftop/panels + meter/electrical). Inverter photo/serial optional later.
3. Citizen return notice → **explicit banner** (`⚠️ Installation returned by DISCOM for correction` + reason), not tracker-only.
4. Commercial 500 kW → **same report/checklist**, existing category ceilings apply. Heavier DPR-style commissioning noted as future extension only.


