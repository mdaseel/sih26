"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { ApiError, vendorApi } from "@/lib/api";
import { AppShell } from "@/components/AppShell";
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
    <AppShell
      links={LINKS}
      badge="Installer"
      homeHref="/vendor/dashboard"
      email={summary?.vendor.business_name ?? null}
      onSignOut={async () => {
        await supabase.auth.signOut();
        router.replace("/login");
      }}
    >
      {children}
    </AppShell>
  );
}
