-- ============================================================
--  SolarGrid AI — 0004 fix column-level privileges
--
--  SECURITY FIX. Migration 0002 tried to protect individual columns with
--
--      revoke update (role) on public.profiles from authenticated;
--
--  That is a no-op. In Postgres a table-level GRANT UPDATE covers every
--  column, and revoking a single column's privilege does not override it.
--  Supabase grants table-level UPDATE to both `anon` and `authenticated` by
--  default, so `role` remained writable.
--
--  Verified exploit before this migration: a CITIZEN updated their own
--  profiles.role to 'DISCOM' and gained review privileges. RLS did not stop it
--  because the policy authorises the ROW ("you may edit your own profile") and
--  says nothing about WHICH COLUMNS may change.
--
--  The correct pattern is to revoke UPDATE at table level, then grant it back
--  on the specific columns that are safe to expose.
-- ============================================================

-- ------------------------------------------------------------
--  profiles — a user may edit their contact details, nothing else.
--  role, is_active, discom_name, email and id are all off limits.
-- ------------------------------------------------------------
revoke update on public.profiles from anon, authenticated;

grant update (full_name, phone, address, district, state, pincode)
  on public.profiles to authenticated;

-- ------------------------------------------------------------
--  installations — a vendor may report progress but must never assert
--  that the DISCOM has verified the work.
--
--  Consequence: DISCOM verification is performed by the backend through the
--  service role, which is a different Postgres role and keeps its privileges.
--  That is the intended path — verification is an authorised server action,
--  not a client write.
-- ------------------------------------------------------------
revoke update on public.installations from anon, authenticated;

grant update (status, installed_capacity_kw, started_at, completed_at)
  on public.installations to authenticated;

-- ------------------------------------------------------------
--  vendors — a vendor may maintain its business profile. Verification state,
--  activation, rating and completion counts are set by the DISCOM/backend.
-- ------------------------------------------------------------
revoke update on public.vendors from anon, authenticated;

grant update (
    business_name, representative_name, email, phone,
    address_line, district, state, pincode, latitude, longitude,
    registration_number, gst_number, service_areas,
    installation_capacity_kw, years_experience
  ) on public.vendors to authenticated;

-- ------------------------------------------------------------
--  vendor_documents — a vendor may attach documents; only the DISCOM/backend
--  may mark one verified.
-- ------------------------------------------------------------
revoke update on public.vendor_documents from anon, authenticated;

grant update (document_type, file_path, file_name, mime_type, file_size_bytes, notes)
  on public.vendor_documents to authenticated;

-- ------------------------------------------------------------
--  Unauthenticated callers have no legitimate writes anywhere.
--  RLS already denies them, since every policy resolves auth.uid(); this is
--  the second layer.
-- ------------------------------------------------------------
revoke insert, update, delete on
    public.profiles,
    public.grid_assets,
    public.solar_applications,
    public.application_status_history,
    public.simulation_results,
    public.risk_assessments,
    public.vendors,
    public.vendor_documents,
    public.appointments,
    public.installations,
    public.scheme_config,
    public.audit_logs
  from anon;

-- ------------------------------------------------------------
--  Engineering truth: revoke writes from authenticated entirely.
--  These tables have no client write policy, so RLS already refuses. Removing
--  the grant means the request is rejected before RLS is even consulted.
-- ------------------------------------------------------------
revoke insert, update, delete on
    public.simulation_results,
    public.risk_assessments,
    public.grid_assets,
    public.scheme_config,
    public.audit_logs,
    public.application_status_history
  from authenticated;
