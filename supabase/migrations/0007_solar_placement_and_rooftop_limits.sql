-- ============================================================
--  0007  Rooftop solar placement, and limits that match a rooftop
-- ============================================================
--
-- Two changes, both about the application being a *household* one.
--
-- 1. solar_placement
--    The 3D planner produces a real proposal: where the array sits, how many
--    modules, what they are rated at, the tilt and bearing, the roof height it
--    was measured against, and the suitability verdict that came out of it.
--    That travels with the application to the DISCOM and to the installer, so
--    it has to be stored rather than recomputed from nothing.
--
--    It lands in one jsonb column rather than a dozen typed ones because the
--    shape belongs to the planner and will move as the planner does. Nothing
--    in the engineering pipeline reads it: the power flow consumes pv_bus,
--    existing_pv_kw and new_pv_kw exactly as before, and this column is
--    descriptive metadata beside them. A migration adding a column nothing
--    joins on is cheap; one restructuring six is not.
--
-- 2. Residential capacity bounds
--    The original constraints allow up to 5000 kW, which is right for the
--    table in the abstract and wrong for what this form now collects. A house
--    does not host a 200 kW array, and an assessment of one describes a system
--    nobody will build. The bounds are widened to the DB only as far as the
--    citizen path needs: 3-11 kW proposed, up to 10 kW already installed.
--
--    Existing rows are left alone. Historic applications outside the new range
--    are real records of what was submitted, and rewriting them to fit a later
--    rule would be falsifying the archive -- so the constraint is added NOT
--    VALID and only enforced on new and updated rows.

-- ------------------------------------------------------------
--  1. Placement
-- ------------------------------------------------------------
alter table public.solar_applications
  add column if not exists solar_placement jsonb;

comment on column public.solar_applications.solar_placement is
  'Rooftop array proposal from the 3D planner: panel count and rating, tilt, '
  'azimuth, array footprint, sampled roof/terrain height, and the suitability '
  'verdict. Descriptive only - the power flow reads pv_bus and the kW columns.';

-- Clients may write it on their own application, like the other applicant
-- fields. Migration 0004 revoked column privileges by default, so the grant
-- has to be explicit.
grant update (solar_placement) on public.solar_applications to authenticated;
grant insert (solar_placement) on public.solar_applications to authenticated;

-- ------------------------------------------------------------
--  2. Residential capacity bounds
-- ------------------------------------------------------------
alter table public.solar_applications
  drop constraint if exists sa_new_pv_residential;
alter table public.solar_applications
  drop constraint if exists sa_existing_pv_residential;

alter table public.solar_applications
  add constraint sa_new_pv_residential
  check (new_pv_kw >= 3 and new_pv_kw <= 11) not valid;

alter table public.solar_applications
  add constraint sa_existing_pv_residential
  check (existing_pv_kw >= 0 and existing_pv_kw <= 10) not valid;

comment on constraint sa_new_pv_residential on public.solar_applications is
  'Household rooftop range. NOT VALID so existing records are preserved as '
  'submitted; enforced on every insert and update from here on.';
