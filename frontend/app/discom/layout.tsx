"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { discomApi } from "@/lib/api";
import { AppShell } from "@/components/AppShell";
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
    <AppShell
      links={LINKS}
      badge="DISCOM"
      homeHref="/discom/dashboard"
      email={me?.email ?? null}
      onSignOut={async () => {
        await supabase.auth.signOut();
        router.replace("/login");
      }}
    >
      {children}
    </AppShell>
  );
}
