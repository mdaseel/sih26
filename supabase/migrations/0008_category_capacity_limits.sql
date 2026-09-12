-- ============================================================
--  0008  Category-wise rooftop capacity limits
-- ============================================================
--
-- 0007 capped every application at 3-11 kW, which is right for a house and
-- wrong for a shop, a school or a factory. The form has collected
-- connection_type all along; this migration makes the database respect it:
--
--   Residential    1-10 kW   (PM Surya Ghar individual rooftop)
--   Commercial     1-500 kW  (to sanctioned load, 500 kW net-metering cap)
--   Institutional  1-500 kW  (as commercial rooftop)
--   Industrial     1-500 kW  (larger needs DISCOM/state approval)
--   NULL / other   treated as Residential (the strictest, safe default)
--
-- Like 0007, the constraint is NOT VALID: historic rows stay exactly as
-- submitted and only new/updated rows are checked. The API validates first
-- (services/capacity_limits.py) so applicants get a readable message; this
-- is the backstop against direct writes.

alter table public.solar_applications
  drop constraint if exists sa_new_pv_residential;
alter table public.solar_applications
  drop constraint if exists sa_existing_pv_residential;
alter table public.solar_applications
  drop constraint if exists sa_pv_by_category;

alter table public.solar_applications
  add constraint sa_pv_by_category
  check (
    case coalesce(connection_type, 'Residential')
      when 'Residential' then
        new_pv_kw >= 1 and new_pv_kw <= 10
        and existing_pv_kw >= 0 and existing_pv_kw <= 10
      when 'Commercial' then
        new_pv_kw >= 1 and new_pv_kw <= 500
        and existing_pv_kw >= 0 and existing_pv_kw <= 500
      when 'Institutional' then
        new_pv_kw >= 1 and new_pv_kw <= 500
        and existing_pv_kw >= 0 and existing_pv_kw <= 500
      when 'Industrial' then
        new_pv_kw >= 1 and new_pv_kw <= 500
        and existing_pv_kw >= 0 and existing_pv_kw <= 500
      else
        new_pv_kw >= 1 and new_pv_kw <= 10
        and existing_pv_kw >= 0 and existing_pv_kw <= 10
    end
  ) not valid;

comment on constraint sa_pv_by_category on public.solar_applications is
  'Rooftop range by consumer category (Residential 1-10 kW, others 1-500 kW). NOT VALID so existing records are preserved; enforced on new/updated rows.';
