-- ============================================================
--  SolarGrid AI — 0001 initial schema
--  Phase 1: Supabase foundation
-- ============================================================

create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";

-- ------------------------------------------------------------
--  Enumerated types
-- ------------------------------------------------------------
create type user_role as enum ('CITIZEN', 'DISCOM', 'VENDOR', 'ADMIN');

create type application_status as enum (
  'DRAFT',
  'SUBMITTED',
  'ASSESSING',
  'ASSESSED',
  'UNDER_DISCOM_REVIEW',
  'APPROVED',
  'ENGINEERING_REVIEW',
  'REJECTED',
  'VENDOR_SELECTED',
  'INSTALLING',
  'INSTALLED',
  'VERIFIED',
  'CANCELLED'
);

-- Risk classes are exactly the three the existing model emits.
create type risk_level as enum ('SAFE', 'CAUTION', 'CONSTRAINED');

-- Constraint types mirror constraint_type in dataset_generation_phase2.py
create type constraint_kind as enum (
  'none',
  'voltage',
  'voltage_rise',
  'line_loading',
  'transformer_loading',
  'caution'
);

create type grid_asset_type as enum (
  'SUBSTATION',
  'FEEDER',
  'TRANSFORMER',
  'BUS',
  'LINE',
  'CUSTOMER_POINT'
);

create type vendor_status as enum ('PENDING', 'UNDER_REVIEW', 'APPROVED', 'REJECTED', 'SUSPENDED');

create type installation_status as enum (
  'PENDING',
  'SITE_VISIT',
  'SCHEDULED',
  'IN_PROGRESS',
  'COMPLETED',
  'VERIFICATION_PENDING',
  'VERIFIED'
);

create type appointment_status as enum ('REQUESTED', 'CONFIRMED', 'RESCHEDULED', 'COMPLETED', 'CANCELLED');

-- ------------------------------------------------------------
--  updated_at helper
-- ------------------------------------------------------------
create or replace function public.touch_updated_at()
returns trigger
language plpgsql
as $fn$
begin
  new.updated_at = now();
  return new;
end;
$fn$;

-- ============================================================
--  profiles — extends auth.users
-- ============================================================
create table public.profiles (
  id            uuid primary key references auth.users(id) on delete cascade,
  role          user_role   not null default 'CITIZEN',
  full_name     text,
  email         text,
  phone         text,
  address       text,
  district      text,
  state         text,
  pincode       text,
  discom_name   text,
  is_active     boolean     not null default true,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

create index profiles_role_idx on public.profiles(role);

create trigger profiles_touch before update on public.profiles
  for each row execute function public.touch_updated_at();

-- Auto-create a profile whenever an auth user is created.
-- Role always defaults to CITIZEN; privilege is never driven by
-- client-supplied signup metadata.
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $fn$
begin
  insert into public.profiles (id, email, full_name)
  values (new.id, new.email, new.raw_user_meta_data ->> 'full_name')
  on conflict (id) do nothing;
  return new;
end;
$fn$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ============================================================
--  grid_assets — seeded from the existing feeder model
--  Source: feeder_network.json, valid_pv_buses.csv, electrical_features.csv
-- ============================================================
create table public.grid_assets (
  id                       uuid primary key default gen_random_uuid(),
  asset_type               grid_asset_type not null,
  asset_code               text not null,
  name                     text,
  feeder_id                text not null default 'IEEE_CompTestFeeder',
  parent_asset_code        text,

  -- Electrical attributes (from the existing static feature DB)
  vn_kv                    numeric(10,4),
  sn_kva                   numeric(12,3),
  transformer_association  text,
  feeder_section           text,
  existing_load_kw         numeric(12,3),
  existing_q_kvar          numeric(12,3),
  base_voltage_pu          numeric(10,5),
  feeder_distance_km       numeric(12,4),
  upstream_r_ohm           numeric(12,4),
  upstream_x_ohm           numeric(12,4),
  upstream_z_ohm           numeric(12,4),
  phase_configuration      text,

  -- PV eligibility (from valid_pv_buses.csv / excluded_buses.csv)
  pv_eligible              boolean not null default false,
  eligibility_reason       text,

  -- Geography. NULL by default: the IEEE feeder ships no coordinates.
  -- Any value here is an illustrative placement, never surveyed data.
  latitude                 numeric(10,7),
  longitude                numeric(10,7),
  geometry_source          text not null default 'SYNTHETIC_LAYOUT',

  attributes               jsonb not null default '{}'::jsonb,
  created_at               timestamptz not null default now(),
  updated_at               timestamptz not null default now(),

  constraint grid_assets_code_unique unique (feeder_id, asset_type, asset_code)
);

create index grid_assets_type_idx     on public.grid_assets(asset_type);
create index grid_assets_code_idx     on public.grid_assets(asset_code);
create index grid_assets_eligible_idx on public.grid_assets(pv_eligible) where pv_eligible;
create index grid_assets_parent_idx   on public.grid_assets(parent_asset_code);

create trigger grid_assets_touch before update on public.grid_assets
  for each row execute function public.touch_updated_at();

-- ============================================================
--  solar_applications
-- ============================================================
create table public.solar_applications (
  id                      uuid primary key default gen_random_uuid(),
  application_number      text unique not null
                            default 'SG-' || upper(substr(replace(gen_random_uuid()::text, '-', ''), 1, 10)),
  applicant_id            uuid not null references public.profiles(id) on delete cascade,

  -- Applicant-facing details
  applicant_name          text not null,
  contact_phone           text,
  address_line            text,
  district                text,
  state                   text,
  pincode                 text,
  latitude                numeric(10,7),
  longitude               numeric(10,7),

  -- Electricity connection
  consumer_number         text,
  connection_type         text,
  sanctioned_load_kw      numeric(10,3),
  monthly_consumption_kwh numeric(12,3),

  -- Roof
  roof_area_sqm           numeric(10,2),
  roof_type               text,
  shading_level           text,

  -- Technical inputs consumed by the ML + power-flow layers
  pv_bus                  text not null,
  existing_pv_kw          numeric(10,3) not null default 0,
  new_pv_kw               numeric(10,3) not null,
  total_pv_kw             numeric(10,3) generated always as (existing_pv_kw + new_pv_kw) stored,

  status                  application_status not null default 'DRAFT',
  submitted_at            timestamptz,
  reviewed_by             uuid references public.profiles(id),
  reviewed_at             timestamptz,
  review_notes            text,

  created_at              timestamptz not null default now(),
  updated_at              timestamptz not null default now(),

  constraint sa_new_pv_positive   check (new_pv_kw > 0 and new_pv_kw <= 5000),
  constraint sa_existing_pv_valid check (existing_pv_kw >= 0 and existing_pv_kw <= 5000)
);

create index sa_applicant_idx on public.solar_applications(applicant_id);
create index sa_status_idx    on public.solar_applications(status);
create index sa_bus_idx       on public.solar_applications(pv_bus);
create index sa_created_idx   on public.solar_applications(created_at desc);

create trigger sa_touch before update on public.solar_applications
  for each row execute function public.touch_updated_at();

-- ============================================================
--  application_status_history
-- ============================================================
create table public.application_status_history (
  id              uuid primary key default gen_random_uuid(),
  application_id  uuid not null references public.solar_applications(id) on delete cascade,
  from_status     application_status,
  to_status       application_status not null,
  changed_by      uuid references public.profiles(id),
  actor_role      user_role,
  note            text,
  created_at      timestamptz not null default now()
);

create index ash_app_idx on public.application_status_history(application_id, created_at desc);

-- Record every status transition automatically.
create or replace function public.log_application_status_change()
returns trigger
language plpgsql
security definer
set search_path = public
as $fn$
begin
  if (tg_op = 'INSERT') then
    insert into public.application_status_history (application_id, from_status, to_status, changed_by, note)
    values (new.id, null, new.status, new.applicant_id, 'Application created');
  elsif (new.status is distinct from old.status) then
    insert into public.application_status_history (application_id, from_status, to_status, changed_by, note)
    values (new.id, old.status, new.status, auth.uid(), null);
  end if;
  return new;
end;
$fn$;

create trigger sa_status_history
  after insert or update of status on public.solar_applications
  for each row execute function public.log_application_status_change();

-- ============================================================
--  simulation_results — deterministic power-flow output
--  WRITE PATH: backend service role only. This is engineering truth.
-- ============================================================
create table public.simulation_results (
  id                               uuid primary key default gen_random_uuid(),
  application_id                   uuid not null references public.solar_applications(id) on delete cascade,

  pv_bus                           text not null,
  existing_pv_kw                   numeric(10,3) not null,
  new_pv_kw                        numeric(10,3) not null,
  total_pv_kw                      numeric(10,3) not null,

  -- Voltage (per-unit), named after the existing pipeline's columns
  base_voltage_pu                  numeric(10,5),
  pv_voltage_pu                    numeric(10,5),
  voltage_rise_pu                  numeric(10,5),
  feeder_min_voltage_pu            numeric(10,5),
  feeder_max_voltage_pu            numeric(10,5),
  min_voltage_bus                  text,
  max_voltage_bus                  text,

  -- Loading
  base_max_line_loading_pct        numeric(10,3),
  max_line_loading_pct             numeric(10,3),
  worst_line                       text,
  base_max_transformer_loading_pct numeric(10,3),
  max_transformer_loading_pct      numeric(10,3),
  worst_transformer                text,

  -- Power
  base_total_p_kw                  numeric(14,3),
  pv_total_p_kw                    numeric(14,3),
  power_loss_kw                    numeric(14,3),
  delta_losses_kw                  numeric(14,3),
  reverse_power_flow               boolean not null default false,
  reverse_reason                   text,
  solar_penetration_pct            numeric(12,3),

  converged                        boolean not null default true,
  engine                           text not null default 'pandapower',
  engine_version                   text,
  network_file                     text not null default 'feeder_network.json',
  runtime_ms                       integer,

  created_at                       timestamptz not null default now()
);

create index sim_app_idx on public.simulation_results(application_id, created_at desc);

-- ============================================================
--  risk_assessments — ML pre-screen + final engineering verdict
--  WRITE PATH: backend service role only.
-- ============================================================
create table public.risk_assessments (
  id                      uuid primary key default gen_random_uuid(),
  application_id          uuid not null references public.solar_applications(id) on delete cascade,
  simulation_id           uuid references public.simulation_results(id) on delete set null,

  -- Layer 1: ML pre-screening
  ml_prediction           risk_level not null,
  safe_probability        numeric(6,5) not null,
  caution_probability     numeric(6,5) not null,
  constrained_probability numeric(6,5) not null,
  model_file              text not null default 'suryagrid_model_v2.pkl',
  model_version           text not null default 'v2.0',
  feature_count           integer not null default 18,

  -- Layer 2: deterministic engineering verification (the authority)
  engineering_risk        risk_level not null,
  constraint_type         constraint_kind not null default 'none',
  constraint_reason       text,

  -- Do the two layers agree? Surfaced to DISCOM, never used to overrule physics.
  ml_agrees_with_engineering boolean
    generated always as (ml_prediction = engineering_risk) stored,

  -- Snapshot of the thresholds applied, copied from scenario_config.json
  thresholds_snapshot     jsonb not null default '{}'::jsonb,
  config_file             text not null default 'scenario_config.json',

  created_at              timestamptz not null default now(),

  constraint ra_probs_valid check (
    safe_probability between 0 and 1 and
    caution_probability between 0 and 1 and
    constrained_probability between 0 and 1
  )
);

create index ra_app_idx  on public.risk_assessments(application_id, created_at desc);
create index ra_risk_idx on public.risk_assessments(engineering_risk);

-- ============================================================
--  vendors
-- ============================================================
create table public.vendors (
  id                       uuid primary key default gen_random_uuid(),
  owner_id                 uuid unique references public.profiles(id) on delete cascade,
  business_name            text not null,
  representative_name      text,
  email                    text,
  phone                    text,
  address_line             text,
  district                 text,
  state                    text,
  pincode                  text,
  latitude                 numeric(10,7),
  longitude                numeric(10,7),
  registration_number      text,
  gst_number               text,
  service_areas            text[] not null default '{}',
  installation_capacity_kw numeric(12,3),
  years_experience         integer,
  rating                   numeric(3,2) check (rating is null or rating between 0 and 5),
  completed_installations  integer not null default 0,

  status                   vendor_status not null default 'PENDING',
  is_active                boolean not null default true,
  verified_by              uuid references public.profiles(id),
  verified_at              timestamptz,
  rejection_reason         text,

  created_at               timestamptz not null default now(),
  updated_at               timestamptz not null default now()
);

create index vendors_status_idx on public.vendors(status) where status = 'APPROVED';
create index vendors_geo_idx    on public.vendors(latitude, longitude);

create trigger vendors_touch before update on public.vendors
  for each row execute function public.touch_updated_at();

create table public.vendor_documents (
  id              uuid primary key default gen_random_uuid(),
  vendor_id       uuid not null references public.vendors(id) on delete cascade,
  document_type   text not null,
  file_path       text not null,
  file_name       text,
  mime_type       text,
  file_size_bytes bigint,
  is_verified     boolean not null default false,
  verified_by     uuid references public.profiles(id),
  verified_at     timestamptz,
  notes           text,
  created_at      timestamptz not null default now()
);

create index vd_vendor_idx on public.vendor_documents(vendor_id);

-- ============================================================
--  appointments
-- ============================================================
create table public.appointments (
  id               uuid primary key default gen_random_uuid(),
  application_id   uuid not null references public.solar_applications(id) on delete cascade,
  vendor_id        uuid not null references public.vendors(id) on delete cascade,
  citizen_id       uuid not null references public.profiles(id) on delete cascade,
  scheduled_at     timestamptz not null,
  duration_minutes integer not null default 60,
  purpose          text not null default 'SITE_VISIT',
  status           appointment_status not null default 'REQUESTED',
  notes            text,
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);

create index appt_app_idx    on public.appointments(application_id);
create index appt_vendor_idx on public.appointments(vendor_id, scheduled_at);

create trigger appt_touch before update on public.appointments
  for each row execute function public.touch_updated_at();

-- ============================================================
--  installations
-- ============================================================
create table public.installations (
  id                    uuid primary key default gen_random_uuid(),
  application_id        uuid not null unique references public.solar_applications(id) on delete cascade,
  vendor_id             uuid references public.vendors(id) on delete set null,
  status                installation_status not null default 'PENDING',
  installed_capacity_kw numeric(10,3),
  started_at            timestamptz,
  completed_at          timestamptz,

  -- DISCOM verification. Vendors must never be able to set these.
  discom_verified       boolean not null default false,
  discom_verified_by    uuid references public.profiles(id),
  discom_verified_at    timestamptz,
  verification_notes    text,

  created_at            timestamptz not null default now(),
  updated_at            timestamptz not null default now()
);

create index inst_vendor_idx on public.installations(vendor_id);
create index inst_status_idx on public.installations(status);

create trigger inst_touch before update on public.installations
  for each row execute function public.touch_updated_at();

-- ============================================================
--  scheme_config — PM Surya Ghar / CFA parameters, configurable
-- ============================================================
create table public.scheme_config (
  id             uuid primary key default gen_random_uuid(),
  scheme_code    text not null,
  config_key     text not null,
  config_value   jsonb not null,
  description    text,
  effective_from date not null default current_date,
  effective_to   date,
  source_url     text,
  is_active      boolean not null default true,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now(),

  constraint scheme_config_unique unique (scheme_code, config_key, effective_from)
);

create trigger scheme_touch before update on public.scheme_config
  for each row execute function public.touch_updated_at();

-- ============================================================
--  audit_logs — append-only
-- ============================================================
create table public.audit_logs (
  id           uuid primary key default gen_random_uuid(),
  actor_id     uuid references public.profiles(id) on delete set null,
  actor_role   user_role,
  action       text not null,
  entity_type  text not null,
  entity_id    uuid,
  before_state jsonb,
  after_state  jsonb,
  ip_address   inet,
  user_agent   text,
  created_at   timestamptz not null default now()
);

create index audit_entity_idx  on public.audit_logs(entity_type, entity_id);
create index audit_actor_idx   on public.audit_logs(actor_id, created_at desc);
create index audit_created_idx on public.audit_logs(created_at desc);
