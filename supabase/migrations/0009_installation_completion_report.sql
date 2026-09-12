-- ============================================================
--  0009  Installation completion report (vendor-filed)
-- ============================================================
--
-- The vendor installations page advanced work with status buttons and one kW
-- box. DISCOM verification therefore happened nearly blind. These columns let
-- the vendor file what was actually built: equipment, capacity, dates, a
-- commissioning checklist, photo references and remarks — and let DISCOM
-- return the job with a reason instead of only approving it.
--
-- Photos reuse vendor_documents (uploaded through the existing validated
-- upload); photo_document_ids references those rows. No new bucket/table.
-- discom_verified* columns are untouched: vendors still cannot self-verify.

alter table public.installations
  add column if not exists panel_make text,
  add column if not exists panel_model text,
  add column if not exists panel_count integer
    check (panel_count is null or panel_count >= 1),
  add column if not exists panel_watts_each integer
    check (panel_watts_each is null or panel_watts_each >= 1),
  add column if not exists inverter_make text,
  add column if not exists inverter_model text,
  add column if not exists inverter_capacity_kw numeric(10,3)
    check (inverter_capacity_kw is null or inverter_capacity_kw > 0),
  add column if not exists install_date date,
  add column if not exists completion_notes text
    check (completion_notes is null or char_length(completion_notes) <= 2000),
  add column if not exists checklist jsonb not null default '{}',
  add column if not exists photo_document_ids uuid[] not null default '{}',
  add column if not exists return_notes text,
  add column if not exists returned_at timestamptz;

comment on column public.installations.checklist is
  'Commissioning checklist as {key: true} for the six required items. All six must be true before submit.';
comment on column public.installations.photo_document_ids is
  'vendor_documents ids proving the work (min 2: rooftop/panels + meter). Read via existing signed-URL endpoint.';
comment on column public.installations.return_notes is
  'DISCOM reason when work is returned for correction. Shown to vendor and citizen until resubmitted.';

-- Vendors may write exactly the report columns (0004 pattern: explicit
-- grants; status/installed_capacity_kw/started/completed_at keep theirs).
grant update (
  panel_make, panel_model, panel_count, panel_watts_each,
  inverter_make, inverter_model, inverter_capacity_kw, install_date,
  completion_notes, checklist, photo_document_ids
) on public.installations to authenticated;
