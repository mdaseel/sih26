-- ============================================================
--  SolarGrid AI — 0003 lock down the migration ledger
--
--  applied_migrations is created by backend/scripts/apply_migrations.py and is
--  internal bookkeeping. Without RLS, PostgREST would serve it to anyone
--  holding the anon key. Enable RLS and define no policy: the service role
--  still reaches it (it bypasses RLS), every client is denied.
-- ============================================================

alter table public.applied_migrations enable row level security;

revoke all on public.applied_migrations from anon, authenticated;
