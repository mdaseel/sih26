"""Apply supabase/migrations/*.sql to the Supabase Postgres database.

Uses the direct database connection (SUPABASE_DB_URL, or SUPABASE_URL when it
holds a postgresql:// string) so no Supabase CLI or Docker is required.

Each file runs inside a single transaction: a migration either lands whole or
not at all. Already-applied migrations are detected via the applied_migrations
table and skipped, so re-running is safe.

Usage:
    python backend/scripts/apply_migrations.py            # apply pending
    python backend/scripts/apply_migrations.py --status   # report only
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import psycopg  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.paths import REPO_ROOT  # noqa: E402

MIGRATIONS_DIR = REPO_ROOT / "supabase" / "migrations"

LEDGER = """
create table if not exists public.applied_migrations (
    filename    text primary key,
    checksum    text not null,
    applied_at  timestamptz not null default now()
);
"""


def sql_files() -> list[Path]:
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true", help="report state without applying")
    args = ap.parse_args()

    settings = get_settings()
    if not settings.database_configured:
        print("FAIL: no database URL. Set SUPABASE_DB_URL (postgresql://...) in .env")
        return 1

    files = sql_files()
    if not files:
        print(f"FAIL: no .sql files in {MIGRATIONS_DIR}")
        return 1

    # The pooler host is safe to show; credentials are not.
    host = settings.database_url.split("@")[-1]
    print(f"target: {host}")
    print(f"migrations: {[f.name for f in files]}\n")

    with psycopg.connect(settings.database_url, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute(LEDGER)
        conn.commit()

        with conn.cursor() as cur:
            cur.execute("select filename, checksum from public.applied_migrations")
            applied = dict(cur.fetchall())

        for path in files:
            body = path.read_text(encoding="utf-8")
            checksum = hashlib.sha256(body.encode()).hexdigest()[:16]

            if path.name in applied:
                same = applied[path.name] == checksum
                print(
                    f"  [SKIP] {path.name} — already applied"
                    + ("" if same else "  ** WARNING: file changed since it was applied **")
                )
                continue

            if args.status:
                print(f"  [PENDING] {path.name}")
                continue

            print(f"  [APPLY] {path.name} ({len(body):,} chars) ... ", end="", flush=True)
            try:
                with conn.cursor() as cur:
                    cur.execute(body)
                    cur.execute(
                        "insert into public.applied_migrations (filename, checksum) values (%s, %s)",
                        (path.name, checksum),
                    )
                conn.commit()
                print("OK")
            except Exception as exc:  # noqa: BLE001
                conn.rollback()
                print("FAILED (rolled back)")
                print(f"\n  {type(exc).__name__}: {exc}")
                return 1

        # Report what now exists.
        with conn.cursor() as cur:
            cur.execute(
                """
                select table_name from information_schema.tables
                where table_schema = 'public' and table_type = 'BASE TABLE'
                order by table_name
                """
            )
            tables = [r[0] for r in cur.fetchall()]
            cur.execute("select count(*) from pg_policies where schemaname = 'public'")
            policies = cur.fetchone()[0]
            cur.execute(
                """
                select c.relname from pg_class c
                join pg_namespace n on n.oid = c.relnamespace
                where n.nspname = 'public' and c.relkind = 'r' and c.relrowsecurity
                order by c.relname
                """
            )
            rls_tables = [r[0] for r in cur.fetchall()]

    print(f"\npublic tables ({len(tables)}): {', '.join(tables)}")
    print(f"RLS enabled on {len(rls_tables)} tables")
    print(f"RLS policies: {policies}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
