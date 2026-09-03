"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { ApiError, discomApi, vendorApi } from "@/lib/api";
import { AppShell } from "@/components/AppShell";
import { supabase } from "@/lib/supabase";
import type { Me, VendorSummary } from "@/lib/types";

const LINKS = [
  { href: "/vendor/dashboard", label: "Dashboard" },
  { href: "/vendor/map", label: "Map" },
  { href: "/vendor/applications", label: "My Applications" },
  { href: "/vendor/leads", label: "Leads" },
  { href: "/vendor/installations", label: "Installations" },
  { href: "/vendor/projects", label: "Projects" },
  { href: "/vendor/profile", label: "Profile" },
];

export default function VendorLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [summary, setSummary] = useState<VendorSummary | null>(null);
  const [me, setMe] = useState<Me | null>(null);
  const [state, setState] = useState<"checking" | "ok" | "no-profile" | "denied">("checking");
  const isAuthPage = pathname === "/vendor/login" || pathname === "/vendor/register";
  useEffect(() => {
    if (isAuthPage) { setState("ok"); return; }
    let active = true;
    let timeout: ReturnType<typeof setTimeout> | null = null;

    const checkSession = async () => {
      const { data } = await supabase.auth.getSession();
      if (!active) return;
      if (!data.session) {
        // Session may still be hydrating from storage — wait briefly before redirecting
        timeout = setTimeout(async () => {
          if (!active) return;
          const { data: retry } = await supabase.auth.getSession();
          if (!retry.session && active) router.replace("/vendor/login");
        }, 800);
        return;
      }
      try {
        const profile = await discomApi.me();
        if (!active) return;
        setMe(profile);
        if (profile.role !== "VENDOR") {
          setState("denied");
          return;
        }
        const s = await vendorApi.summary();
        if (!active) return;
        setSummary(s);
        setState("ok");
      } catch (e) {
        if (!active) return;
        const status = (e as ApiError).status;
        if (status === 403) setState("no-profile");
        else if (status === 401) router.replace("/vendor/login");
        else setState("denied");
      }
    };

    checkSession();

    const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!session && state === "ok") router.replace("/vendor/login");
    });

    return () => {
      active = false;
      if (timeout) clearTimeout(timeout);
      sub.subscription.unsubscribe();
    };
  }, [router, isAuthPage, pathname, state]);

  if (isAuthPage) return <>{children}</>;
  if (state === "checking") return <div className="flex min-h-screen items-center justify-center text-sm" style={{ color: "rgb(var(--ink-faint))" }}>Loading your vendor account…</div>;
  if (state === "denied") {
    const target = me?.role === "CITIZEN" ? "/citizen/dashboard" : me?.role === "DISCOM" ? "/discom/dashboard" : "/login";
    return (
      <div className="flex min-h-screen items-center justify-center px-6">
        <div className="card max-w-md text-center">
          <h1 className="text-lg font-bold" style={{ color: "rgb(var(--ink))" }}>Vendor access only</h1>
          <p className="mt-2 text-sm" style={{ color: "rgb(var(--ink-faint))" }}>Your account role is <b>{me?.role ?? "unknown"}</b>. This portal is for vendors (role VENDOR).</p>
          <p className="mt-2 text-xs" style={{ color: "rgb(var(--ink-ghost))" }}>Email hijacking prevented — one account = one portal. Create a separate vendor account or ask DISCOM to convert your role.</p>
          <Link href={target} className="btn-primary mt-4">Go to {me?.role === "CITIZEN" ? "Citizen" : me?.role === "DISCOM" ? "DISCOM" : "Login"}</Link>
        </div>
      </div>
    );
  }
  if (state === "no-profile") {
    return (
      <div className="flex min-h-screen items-center justify-center px-6">
        <div className="card max-w-md text-center">
          <h1 className="text-lg font-bold" style={{ color: "rgb(var(--ink))" }}>No vendor profile</h1>
          <p className="mt-2 text-sm" style={{ color: "rgb(var(--ink-faint))" }}>Your account is VENDOR but has no business profile yet.</p>
          <Link href="/vendor/register" className="btn-primary mt-4">Register your business</Link>
        </div>
      </div>
    );
  }
  return <AppShell links={LINKS} badge="Installer" homeHref="/vendor/dashboard" email={summary?.vendor.business_name ?? me?.email ?? null} onSignOut={async () => { await supabase.auth.signOut(); router.replace("/login"); }}>{children}</AppShell>;
}
