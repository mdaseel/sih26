-- ============================================================
--  SolarGrid AI — 0005 let an approved vendor edit its own profile
--
--  BUG. Migration 0002 wrote:
--
--      create policy vendors_update_own on public.vendors
--        for update using (owner_id = auth.uid())
--        with check (owner_id = auth.uid() and status = 'PENDING');
--
--  The intent was "a vendor must not change its own status". What it actually
--  says is "after any self-update the row must be PENDING" — so the moment a
--  vendor is APPROVED, every edit it makes fails the check. Approved vendors
--  were locked out of correcting their own phone number or service areas.
--
--  RLS cannot compare the old and new row inside WITH CHECK, so "status must
--  not change" is not expressible here. It does not need to be: migration 0004
--  revoked table-level UPDATE and granted only the profile columns, and
--  `status` is not among them. A vendor cannot write that column at all,
--  whatever this policy says.
--
--  So the ownership test is the whole policy, and the column grants carry the
--  part RLS cannot express.
-- ============================================================

drop policy if exists vendors_update_own on public.vendors;

create policy vendors_update_own on public.vendors
  for update
  using (owner_id = auth.uid())
  with check (owner_id = auth.uid());

-- Same shape, same reason: a vendor may attach and describe its documents, but
-- `is_verified` and `verified_by` are not granted to it (migration 0004), so
-- the policy only needs to establish ownership.
drop policy if exists vd_insert_own on public.vendor_documents;

create policy vd_insert_own on public.vendor_documents
  for insert to authenticated
  with check (public.owns_vendor(vendor_id));
