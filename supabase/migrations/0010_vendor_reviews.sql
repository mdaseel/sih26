-- ============================================================
--  0010  Vendor reviews (citizen ratings + feedback)
-- ============================================================
--
-- vendors.rating exists since 0001 but nothing ever wrote it. Citizens rate
-- completed vendor work (1-5 + tags + comment); a trigger maintains the live
-- average on vendors.rating; DISCOM reads flags and acts (warn/suspend/
-- reject/reinstate via the existing review flow). Suspension itself stays a
-- human DISCOM decision — this table only supplies the evidence.
--
-- Anti-fake anchors: one review per (citizen, vendor, application), and only
-- where the citizen actually engaged the vendor (appointment or installation).

create table public.vendor_reviews (
  id              uuid primary key default gen_random_uuid(),
  application_id  uuid not null references public.solar_applications(id) on delete cascade,
  vendor_id       uuid not null references public.vendors(id) on delete cascade,
  citizen_id      uuid not null references public.profiles(id) on delete cascade,
  rating          smallint not null check (rating between 1 and 5),
  tags            text[] not null default '{}',
  comment         text check (comment is null or char_length(comment) <= 500),
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  constraint one_review_per_engagement unique (citizen_id, vendor_id, application_id)
);

create index vr_vendor_idx on public.vendor_reviews(vendor_id);
create index vr_app_idx on public.vendor_reviews(application_id);

create trigger vr_touch before update on public.vendor_reviews
  for each row execute function public.touch_updated_at();

-- Live average on vendors.rating, recomputed from stored rows only.
create or replace function public.refresh_vendor_rating()
returns trigger language plpgsql as $$
begin
  update public.vendors v
     set rating = sub.avg_rating,
         updated_at = now()
    from (
      select vendor_id, round(avg(rating)::numeric, 2) as avg_rating
        from public.vendor_reviews
       where vendor_id = coalesce(new.vendor_id, old.vendor_id)
       group by vendor_id
    ) sub
   where v.id = sub.vendor_id;
  -- No reviews left (delete): back to unrated rather than a stale number.
  if not found then
    update public.vendors
       set rating = null, updated_at = now()
     where id = coalesce(new.vendor_id, old.vendor_id)
       and not exists (
         select 1 from public.vendor_reviews r where r.vendor_id = coalesce(new.vendor_id, old.vendor_id)
       );
  end if;
  return coalesce(new, old);
end $$;

drop trigger if exists vr_refresh_rating on public.vendor_reviews;
create trigger vr_refresh_rating
  after insert or update of rating or delete on public.vendor_reviews
  for each row execute function public.refresh_vendor_rating();

-- ============================================================
--  RLS
-- ============================================================
alter table public.vendor_reviews enable row level security;

-- Citizens insert only their own review for a vendor they engaged
-- (appointment) or whose installation sits on their application.
create policy vr_insert_engaged on public.vendor_reviews
  for insert to authenticated
  with check (
    citizen_id = auth.uid()
    and (
      exists (
        select 1 from public.appointments ap
         where ap.application_id = vendor_reviews.application_id
           and ap.vendor_id = vendor_reviews.vendor_id
           and ap.citizen_id = auth.uid()
      )
      or exists (
        select 1 from public.installations i
          join public.solar_applications a on a.id = i.application_id
         where i.application_id = vendor_reviews.application_id
           and i.vendor_id = vendor_reviews.vendor_id
           and a.applicant_id = auth.uid()
      )
    )
  );

-- Read: own rows, the reviewed vendor, DISCOM; public summaries are served
-- by the API from an allow-listed projection (first name + initial only).
create policy vr_select on public.vendor_reviews
  for select using (
    citizen_id = auth.uid()
    or public.owns_vendor(vendor_id)
    or public.is_discom()
  );

-- Citizens may correct within the edit window; the service audits originals.
create policy vr_update_own on public.vendor_reviews
  for update using (citizen_id = auth.uid())
  with check (citizen_id = auth.uid());

-- No client deletes: a review is evidence, not a draft.
-- (No delete policy: RLS denies what it does not permit.)
