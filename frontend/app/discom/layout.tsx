"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { discomApi } from "@/lib/api";
import { supabase } from "@/lib/supabase";
import type { Me } from "@/lib/types";

const LINKS = [
  { href: "/discom/dashboard", label: "Dashboard" },
  { href: "/discom/applications", label: "Applications" },
  { href: "/discom/map", label: "Map" },
  { href: "/discom/grid-twin", label: "Grid twin" },
  { href: "/discom/feeders", label: "Feeders" },
  { href: "/discom/transformers", label: "Transformers" },
  { href: "/discom/hosting-capacity", label: "Hosting capacity" },
  { href: "/discom/what-if", label: "What-if" },
  { href: "/discom/vendors", label: "Vendors" },
  { href: "/discom/installations", label: "Installations" },
];

/**
 * DISCOM area shell.
 *
 * The role check here decides what to *render*. It grants nothing: every
 * /api/discom route re-resolves the caller's role from the database, so a user
 * who forced their way past this screen would still be refused by the server.
 */
export default function DiscomLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [me, setMe] = useState<Me | null>(null);
  const [state, setState] = useState<"checking" | "ok" | "denied">("checking");

  useEffect(() => {
    supabase.auth.getSession().then(async ({ data }) => {
      if (!data.session) {
        router.replace("/login");
        return;
      }
      try {
        const profile = await discomApi.me();
        setMe(profile);
        setState(profile.is_discom ? "ok" : "denied");
      } catch {
        setState("denied");
      }
    });
  }, [router]);

  if (state === "checking") {
    return (
      <div className="flex min-h-screen items-center justify-center text-sm text-slate-500">
        Checking your access…
      </div>
    );
  }

  if (state === "denied") {
    return (
      <div className="flex min-h-screen items-center justify-center px-6">
        <div className="card max-w-md text-center">
          <h1 className="text-lg font-semibold text-slate-100">DISCOM access required</h1>
          <p className="mt-2 text-sm text-slate-400">
            Your account has the role <b>{me?.role ?? "unknown"}</b>. The review
            console is limited to DISCOM and ADMIN accounts.
          </p>
          <p className="mt-3 text-xs text-slate-600">
            This screen is a convenience. The server refuses these routes for your
            role regardless of what the browser displays.
          </p>
          <Link href="/citizen/dashboard" className="btn-ghost mt-4">
            Back to my applications
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-800 bg-slate-950/80">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-4 px-6 py-3">
          <Link href="/discom/dashboard" className="flex items-center gap-2">
            <span className="text-lg font-semibold text-slate-100">
              SolarGrid<span className="text-amber-400"> DISCOM</span>
            </span>
            <span className="rounded border border-slate-700 px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-slate-500">
              Prototype
            </span>
          </Link>

          <nav className="flex flex-1 flex-wrap gap-1">
            {LINKS.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                className={`rounded-lg px-2.5 py-1.5 text-sm transition ${
                  pathname === l.href
                    ? "bg-slate-800 text-slate-100"
                    : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
                }`}
              >
                {l.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-3 text-xs text-slate-500">
            <span className="hidden sm:inline">{me?.email}</span>
            <span className="rounded border border-amber-900 bg-amber-950/40 px-2 py-0.5 text-amber-300">
              {me?.role}
            </span>
            <button
              onClick={async () => {
                await supabase.auth.signOut();
                router.replace("/login");
              }}
              className="btn-ghost !px-3 !py-1.5 !text-xs"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
    </div>
  );
}
