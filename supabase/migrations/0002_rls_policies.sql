-- ============================================================
--  SolarGrid AI — 0002 Row Level Security
--
--  Threat model this file defends against:
--    * A citizen editing their own risk result to get approved.
--    * A citizen approving their own application.
--    * A vendor self-approving, or marking DISCOM verification done.
--    * An unapproved vendor being discoverable by customers.
--    * Any client writing electrical values.
--
--  Governing principle: simulation_results and risk_assessments have
--  NO insert/update/delete policy for any client role. Postgres RLS
--  denies what it does not explicitly allow, so those tables are
--  append-only from the backend service role, which bypasses RLS.
--  The frontend physically cannot fabricate electrical values.
-- ============================================================

-- ------------------------------------------------------------
--  Role helpers (security definer to avoid recursive RLS on profiles)
-- ------------------------------------------------------------
create or replace function public.current_user_role()
returns user_role
language sql
stable
security definer
set search_path = public
as $fn$
  select role from public.profiles where id = auth.uid();
$fn$;

create or replace function public.is_discom()
returns boolean
language sql
stable
security definer
set search_path = public
as $fn$
  select coalesce(
    (select role in ('DISCOM', 'ADMIN') and is_active
     from public.profiles where id = auth.uid()),
    false);
$fn$;

create or replace function public.is_admin()
returns boolean
language sql
stable
security definer
set search_path = public
as $fn$
  select coalesce(
    (select role = 'ADMIN' and is_active from public.profiles where id = auth.uid()),
    false);
$fn$;

create or replace function public.owns_vendor(v_id uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $fn$
  select exists (
    select 1 from public.vendors
    where id = v_id and owner_id = auth.uid()
  );
$fn$;

-- ------------------------------------------------------------
--  Enable RLS everywhere
-- ------------------------------------------------------------
alter table public.profiles                   enable row level security;
alter table public.grid_assets                enable row level security;
alter table public.solar_applications         enable row level security;
alter table public.application_status_history enable row level security;
alter table public.simulation_results         enable row level security;
alter table public.risk_assessments           enable row level security;
alter table public.vendors                    enable row level security;
alter table public.vendor_documents           enable row level security;
alter table public.appointments               enable row level security;
alter table public.installations              enable row level security;
alter table public.scheme_config              enable row level security;
alter table public.audit_logs                 enable row level security;

-- ============================================================
--  profiles
-- ============================================================
create policy profiles_select_own on public.profiles
  for select using (id = auth.uid() or public.is_discom());

create policy profiles_update_own on public.profiles
  for update using (id = auth.uid()) with check (id = auth.uid());

-- NOTE: role is deliberately NOT protected by a column grant here, because
-- Postgres RLS cannot express "any column except role". The backend revokes
-- column-level UPDATE on profiles.role below, which does express it.
revoke update (role) on public.profiles from authenticated;

create policy profiles_admin_all on public.profiles
  for all using (public.is_admin()) with check (public.is_admin());

-- ============================================================
--  grid_assets — reference data. Readable by any signed-in user,
--  writable only by the service role (no write policy exists).
-- ============================================================
create policy grid_assets_read on public.grid_assets
  for select to authenticated using (true);

-- ============================================================
--  solar_applications
-- ============================================================
create policy sa_select_own on public.solar_applications
  for select using (applicant_id = auth.uid() or public.is_discom());

create policy sa_insert_own on public.solar_applications
  for insert to authenticated
  with check (
    applicant_id = auth.uid()
    -- A new application may only be created in a pre-assessment state.
    and status in ('DRAFT', 'SUBMITTED')
  );

-- A citizen may edit their own application only while it is still theirs to
-- edit, and may only move it between DRAFT / SUBMITTED / CANCELLED. Every
-- approval state is unreachable from the client.
create policy sa_update_own_predecision on public.solar_applications
  for update
  using (applicant_id = auth.uid() and status in ('DRAFT', 'SUBMITTED'))
  with check (applicant_id = auth.uid() and status in ('DRAFT', 'SUBMITTED', 'CANCELLED'));

create policy sa_update_discom on public.solar_applications
  for update using (public.is_discom()) with check (public.is_discom());

create policy sa_delete_own_draft on public.solar_applications
  for delete using (applicant_id = auth.uid() and status = 'DRAFT');

-- ============================================================
--  application_status_history — read-only to clients.
--  Rows are written by the trigger (security definer) or service role.
-- ============================================================
create policy ash_select on public.application_status_history
  for select using (
    public.is_discom()
    or exists (
      select 1 from public.solar_applications a
      where a.id = application_status_history.application_id
        and a.applicant_id = auth.uid()
    )
  );

-- ============================================================
--  simulation_results — READ ONLY. No write policy by design (Rule 4/7).
-- ============================================================
create policy sim_select on public.simulation_results
  for select using (
    public.is_discom()
    or exists (
      select 1 from public.solar_applications a
      where a.id = simulation_results.application_id
        and a.applicant_id = auth.uid()
    )
  );

-- ============================================================
--  risk_assessments — READ ONLY. No write policy by design (Rule 4/7).
-- ============================================================
create policy ra_select on public.risk_assessments
  for select using (
    public.is_discom()
    or exists (
      select 1 from public.solar_applications a
      where a.id = risk_assessments.application_id
        and a.applicant_id = auth.uid()
    )
  );

-- ============================================================
--  vendors
--  Rule 12: customers see APPROVED and active vendors only.
-- ============================================================
create policy vendors_public_approved on public.vendors
  for select to authenticated
  using (status = 'APPROVED' and is_active);

create policy vendors_select_own on public.vendors
  for select using (owner_id = auth.uid() or public.is_discom());

create policy vendors_insert_own on public.vendors
  for insert to authenticated
  with check (
    owner_id = auth.uid()
    -- A vendor always self-registers as PENDING. Self-approval is impossible.
    and status = 'PENDING'
    and verified_by is null
    and verified_at is null
  );

-- A vendor may edit its own profile but can never move its own status.
create policy vendors_update_own on public.vendors
  for update
  using (owner_id = auth.uid())
  with check (owner_id = auth.uid() and status = 'PENDING');

-- Only DISCOM/ADMIN can change vendor status (approve / reject / suspend).
create policy vendors_update_discom on public.vendors
  for update using (public.is_discom()) with check (public.is_discom());

-- ============================================================
--  vendor_documents
-- ============================================================
create policy vd_select on public.vendor_documents
  for select using (public.owns_vendor(vendor_id) or public.is_discom());

create policy vd_insert_own on public.vendor_documents
  for insert to authenticated
  with check (
    public.owns_vendor(vendor_id)
    and is_verified = false
    and verified_by is null
  );

create policy vd_update_discom on public.vendor_documents
  for update using (public.is_discom()) with check (public.is_discom());

create policy vd_delete_own_unverified on public.vendor_documents
  for delete using (public.owns_vendor(vendor_id) and is_verified = false);

-- ============================================================
--  appointments
-- ============================================================
create policy appt_select on public.appointments
  for select using (
    citizen_id = auth.uid() or public.owns_vendor(vendor_id) or public.is_discom()
  );

create policy appt_insert_citizen on public.appointments
  for insert to authenticated
  with check (
    citizen_id = auth.uid()
    and exists (
      select 1 from public.solar_applications a
      where a.id = application_id and a.applicant_id = auth.uid()
    )
    -- Rule 12: an appointment can only be booked with an approved vendor.
    and exists (
      select 1 from public.vendors v
      where v.id = vendor_id and v.status = 'APPROVED' and v.is_active
    )
  );

create policy appt_update_participant on public.appointments
  for update
  using (citizen_id = auth.uid() or public.owns_vendor(vendor_id))
  with check (citizen_id = auth.uid() or public.owns_vendor(vendor_id));

-- ============================================================
--  installations
--  A vendor may drive installation progress but must never be able to
--  assert DISCOM verification. Enforced by column grant, since RLS
--  cannot express "these columns must not change".
-- ============================================================
create policy inst_select on public.installations
  for select using (
    public.owns_vendor(vendor_id)
    or public.is_discom()
    or exists (
      select 1 from public.solar_applications a
      where a.id = installations.application_id and a.applicant_id = auth.uid()
    )
  );

create policy inst_update_vendor on public.installations
  for update
  using (public.owns_vendor(vendor_id))
  with check (
    public.owns_vendor(vendor_id)
    -- A vendor can advance at most to VERIFICATION_PENDING, never to VERIFIED.
    and status <> 'VERIFIED'
  );

create policy inst_update_discom on public.installations
  for update using (public.is_discom()) with check (public.is_discom());

revoke update (discom_verified, discom_verified_by, discom_verified_at)
  on public.installations from authenticated;

-- ============================================================
--  scheme_config — public reference data, service-role writable only.
-- ============================================================
create policy scheme_read on public.scheme_config
  for select to authenticated using (is_active);

-- ============================================================
--  audit_logs — append-only, admin-readable. No client write policy.
-- ============================================================
create policy audit_select_admin on public.audit_logs
  for select using (public.is_admin());
