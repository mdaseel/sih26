"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { supabase } from "@/lib/supabase";

const LINKS = [
  { href: "/citizen/dashboard", label: "Dashboard" },
  { href: "/citizen/applications", label: "My applications" },
  { href: "/citizen/applications/new", label: "New application" },
  { href: "/citizen/twin", label: "Grid twin" },
  { href: "/citizen/map", label: "Map" },
  { href: "/citizen/vendors", label: "Installers" },
  { href: "/citizen/scheme", label: "PM Surya Ghar" },
];

export function Nav() {
  const pathname = usePathname();
  const router = useRouter();
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => setEmail(data.user?.email ?? null));
  }, []);

  async function signOut() {
    await supabase.auth.signOut();
    router.replace("/login");
  }

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-4 px-6 py-3">
        <Link href="/citizen/dashboard" className="flex items-center gap-2">
          <span className="text-lg font-semibold text-slate-100">
            SolarGrid<span className="text-sky-400"> AI</span>
          </span>
          <span className="rounded border border-slate-700 px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-slate-500">
            Prototype
          </span>
        </Link>

        <nav className="flex flex-1 flex-wrap gap-1">
          {LINKS.map((l) => {
            const active = pathname === l.href;
            return (
              <Link
                key={l.href}
                href={l.href}
                className={`rounded-lg px-3 py-1.5 text-sm transition ${
                  active
                    ? "bg-slate-800 text-slate-100"
                    : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
                }`}
              >
                {l.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-3 text-xs text-slate-500">
          {email && <span className="hidden sm:inline">{email}</span>}
          <button onClick={signOut} className="btn-ghost !px-3 !py-1.5 !text-xs">
            Sign out
          </button>
        </div>
      </div>
    </header>
  );
}
