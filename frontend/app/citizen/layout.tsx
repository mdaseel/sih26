"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Nav } from "@/components/Nav";
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

  useEffect(() => {
    let active = true;

    supabase.auth.getSession().then(({ data }) => {
      if (!active) return;
      if (data.session) {
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
    <div className="min-h-screen">
      <Nav />
      <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
    </div>
  );
}
