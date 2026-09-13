"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/AppShell";
import { SolarGridAssistant } from "@/components/assistant/SolarGridAssistant";
import { CITIZEN_LINKS } from "@/components/Nav";
import { discomApi } from "@/lib/api";
import { supabase } from "@/lib/supabase";
import type { Me } from "@/lib/types";

export default function CitizenLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [state, setState] = useState<"checking" | "in" | "denied">("checking");
  const [email, setEmail] = useState<string | null>(null);
  const [me, setMe] = useState<Me | null>(null);

  async function signOut() {
    try { await supabase.auth.signOut(); } catch { /* 403 when no valid session — still navigate to /login */ }
    router.replace("/login");
  }

  useEffect(() => {
    let active = true;
    supabase.auth.getSession().then(async ({ data }) => {
      if (!active) return;
      if (!data.session) { router.replace("/login"); return; }
      setEmail(data.session.user?.email ?? null);
      try {
        const profile = await discomApi.me();
        if (!active) return;
        setMe(profile);
        // Strict portal isolation: only CITIZEN may use citizen portal
        if (profile.role !== "CITIZEN") {
          setState("denied");
        } else {
          setState("in");
        }
      } catch {
        setState("in"); // fallback if /me fails, don't block
      }
    });
    const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!session) router.replace("/login");
    });
    return () => { active = false; sub.subscription.unsubscribe(); };
  }, [router]);

  if (state === "checking") {
    return <div className="flex min-h-screen items-center justify-center text-sm" style={{ color: "rgb(var(--ink-faint))" }}>Checking your session…</div>;
  }
  if (state === "denied") {
    const target = me?.role === "VENDOR" ? "/vendor/dashboard" : me?.role === "DISCOM" || me?.role === "ADMIN" ? "/discom/dashboard" : "/login";
    return (
      <div className="flex min-h-screen items-center justify-center px-6">
        <div className="card max-w-md text-center">
          <h1 className="text-lg font-bold" style={{ color: "rgb(var(--ink))" }}>Citizen access only</h1>
          <p className="mt-2 text-sm" style={{ color: "rgb(var(--ink-faint))" }}>Your account role is <b>{me?.role}</b>. This portal is for citizens. Use your {me?.role === "VENDOR" ? "vendor" : "DISCOM"} portal instead.</p>
          <p className="mt-2 text-xs" style={{ color: "rgb(var(--ink-ghost))" }}>Email {email} is registered as {me?.role}. One account = one portal.</p>
          <Link href={target} className="btn-primary mt-4">Go to {me?.role === "VENDOR" ? "Vendor" : me?.role === "DISCOM" ? "DISCOM" : "Login"}</Link>
        </div>
      </div>
    );
  }

  return (
    <>
      <AppShell links={CITIZEN_LINKS} badge="Citizen" homeHref="/citizen/dashboard" email={email} onSignOut={signOut}>
        {children}
      </AppShell>
      <SolarGridAssistant />
    </>
  );
}
