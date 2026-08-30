"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/AppShell";
import { CITIZEN_LINKS } from "@/components/Nav";
import { supabase } from "@/lib/supabase";

/**
 * Client-side gate for the citizen area.
 *
 * This is a convenience, not a security control: it stops signed-out users
 * seeing an empty shell. The real enforcement is server-side — the backend
 * rejects requests without a valid JWT, and Row Level Security scopes every
 * row to its owner. Bypassing this component would reveal nothing.
 */
export default function CitizenLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const [state, setState] = useState<"checking" | "in">("checking");
  const [email, setEmail] = useState<string | null>(null);

  async function signOut() {
    await supabase.auth.signOut();
    router.replace("/login");
  }

  useEffect(() => {
    let active = true;

    supabase.auth.getSession().then(({ data }) => {
      if (!active) return;
      if (data.session) {
        setEmail(data.session.user?.email ?? null);
        setState("in");
      } else {
        router.replace("/login");
      }
    });

    const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!session) router.replace("/login");
    });

    return () => {
      active = false;
      sub.subscription.unsubscribe();
    };
  }, [router]);

  if (state === "checking") {
    return (
      <div className="flex min-h-screen items-center justify-center text-sm text-slate-500">
        Checking your session…
      </div>
    );
  }

  return (
    <AppShell
      links={CITIZEN_LINKS}
      badge="Citizen"
      homeHref="/citizen/dashboard"
      email={email}
      onSignOut={signOut}
    >
      {children}
    </AppShell>
  );
}
