"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { ApiError, vendorApi } from "@/lib/api";
import { supabase } from "@/lib/supabase";
import type { VendorSummary } from "@/lib/types";

const LINKS = [
  { href: "/vendor/dashboard", label: "Dashboard" },
  { href: "/vendor/leads", label: "Leads" },
  { href: "/vendor/appointments", label: "Appointments" },
  { href: "/vendor/installations", label: "Installations" },
  { href: "/vendor/projects", label: "Projects" },
  { href: "/vendor/profile", label: "Profile" },
];

/** Shell for the vendor portal. The role and vendor profile are resolved
 *  server-side on every request; this only decides what to draw. */
export default function VendorLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [summary, setSummary] = useState<VendorSummary | null>(null);
  const [state, setState] = useState<"checking" | "ok" | "no-profile">("checking");

  const isAuthPage = pathname === "/vendor/login" || pathname === "/vendor/register";

  useEffect(() => {
    if (isAuthPage) {
      setState("ok");
      return;
    }
    supabase.auth.getSession().then(async ({ data }) => {
      if (!data.session) {
        router.replace("/vendor/login");
        return;
      }
      try {
        setSummary(await vendorApi.summary());
        setState("ok");
      } catch (e) {
        setState((e as ApiError).status === 403 ? "no-profile" : "ok");
      }
    });
  }, [router, isAuthPage, pathname]);

  if (isAuthPage) return <>{children}</>;

  if (state === "checking") {
    return (
      <div className="flex min-h-screen items-center justify-center text-sm text-slate-500">
        Loading your vendor account…
      </div>
    );
  }

  if (state === "no-profile") {
    return (
      <div className="flex min-h-screen items-center justify-center px-6">
        <div className="card max-w-md text-center">
          <h1 className="text-lg font-semibold text-slate-100">No vendor profile</h1>
          <p className="mt-2 text-sm text-slate-400">
            This account is not registered as an installer yet.
          </p>
          <Link href="/vendor/register" className="btn-primary mt-4">
            Register your business
          </Link>
        </div>
      </div>
    );
  }

  const v = summary?.vendor;

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-800 bg-slate-950/80">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-4 px-6 py-3">
          <Link href="/vendor/dashboard" className="flex items-center gap-2">
            <span className="text-lg font-semibold text-slate-100">
              SolarGrid<span className="text-emerald-400"> Vendor</span>
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
                {l.href === "/vendor/leads" && summary && summary.new_leads > 0 && (
                  <span className="ml-1.5 rounded-full bg-emerald-900 px-1.5 text-[10px] text-emerald-200">
                    {summary.new_leads}
                  </span>
                )}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-3 text-xs text-slate-500">
            {v && (
              <span
                className={`rounded border px-2 py-0.5 ${
                  v.visible_to_customers
                    ? "border-green-900 bg-green-950/40 text-green-300"
                    : "border-amber-900 bg-amber-950/40 text-amber-300"
                }`}
                title={
                  v.visible_to_customers
                    ? "Customers can find your business"
                    : "Customers cannot see your business until a DISCOM approves it"
                }
              >
                {v.status}
              </span>
            )}
            <button
              onClick={async () => {
                await supabase.auth.signOut();
                router.replace("/vendor/login");
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
