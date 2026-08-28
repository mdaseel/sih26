-- ============================================================
--  SolarGrid AI — 0006 keep audit attribution after a user is deleted
--
--  BUG. audit_logs.actor_id references profiles(id) ON DELETE SET NULL. That
--  is right for a foreign key and wrong for an audit trail: deleting an
--  account silently rewrites history, so every past action by that person
--  becomes anonymous. Verified — after test users were removed, 25 of 25
--  recent audit rows had a null actor while still recording the action.
--
--  An audit log has to answer "who did this" after the fact, including for
--  someone who has since left. So the actor's identifier is also stored as
--  plain text, which no cascade can clear. actor_id keeps the live foreign
--  key for joins; actor_ref is the durable record.
-- ============================================================

alter table public.audit_logs
  add column if not exists actor_ref text,
  add column if not exists actor_email text;

comment on column public.audit_logs.actor_ref is
  'Actor id as text. Survives deletion of the profile, unlike actor_id.';
comment on column public.audit_logs.actor_email is
  'Actor email at the time of the action, for readable attribution.';

-- Backfill what is still recoverable. Rows whose actor was already nulled
-- cannot be recovered — that history is gone, which is the point of the fix.
update public.audit_logs
set actor_ref = actor_id::text
where actor_ref is null and actor_id is not null;

create index if not exists audit_actor_ref_idx on public.audit_logs(actor_ref);
