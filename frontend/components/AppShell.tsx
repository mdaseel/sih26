"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { ThemeToggle } from "@/components/ThemeToggle";

export interface NavLink {
  href: string;
  label: string;
  icon?: string;
}

const ICONS: Record<string, string> = {
  Dashboard: "◈",
  "My Applications": "⬡",
  Applications: "⬡",
  Map: "◎",
  Installers: "⬢",
  Vendors: "⬢",
  "About Scheme": "✦",
  "New application": "＋",
  "Grid twin": "⬔",
  "Network map": "◎",
  Feeders: "⧉",
  Transformers: "⬣",
  "What-if": "◐",
  "Hosting capacity": "▦",
  Leads: "⬡",
  Appointments: "◷",
  Installations: "⬢",
  Projects: "▭",
  Profile: "◯",
};

export function AppShell({
  links,
  badge,
  homeHref,
  email,
  onSignOut,
  children,
}: {
  links: NavLink[];
  badge: string;
  homeHref: string;
  email?: string | null;
  onSignOut: () => void;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => { setDrawerOpen(false); }, [pathname]);
  useEffect(() => {
    if (!drawerOpen) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setDrawerOpen(false); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [drawerOpen]);

  const width = collapsed ? "lg:w-[4.5rem]" : "lg:w-[17rem]";

  const activeHref = links
    .filter((link) => pathname === link.href || pathname.startsWith(`${link.href}/`))
    .sort((a, b) => b.href.length - a.href.length)[0]?.href;

  const badgeTone = badge === "DISCOM" ? "bg-sky-500 text-white" : badge === "Installer" ? "bg-emerald-500 text-white" : "bg-[rgb(var(--brand))] text-[rgb(var(--brand-ink))]";

  return (
    <div className="min-h-screen">
      {/* Header — Apple glass material */}
      <header
        className="sticky top-0 z-40 border-b"
        style={{
          background: "rgb(var(--panel) / 0.72)",
          backdropFilter: "blur(20px) saturate(180%)",
          WebkitBackdropFilter: "blur(20px) saturate(180%)",
          borderColor: "rgb(var(--line) / 0.6)",
        }}
      >
        <div className="flex items-center gap-3 px-4 py-2.5">
          <button
            type="button"
            onClick={() => (window.matchMedia("(min-width: 1024px)").matches ? setCollapsed((c) => !c) : setDrawerOpen((o) => !o))}
            aria-label="Toggle navigation"
            aria-expanded={drawerOpen}
            className="group relative flex h-9 w-9 items-center justify-center rounded-xl border transition-all active:scale-95"
            style={{ borderColor: "rgb(var(--line))", background: "rgb(var(--panel))" }}
          >
            <span className="flex flex-col gap-1">
              <span className="block h-0.5 w-4 rounded-full bg-[rgb(var(--ink))] transition-all group-active:w-3" />
              <span className="block h-0.5 w-4 rounded-full bg-[rgb(var(--ink))] transition-all" />
              <span className="block h-0.5 w-3 rounded-full bg-[rgb(var(--ink))] transition-all group-active:w-4" />
            </span>
          </button>

          <Link href={homeHref} className="flex items-baseline gap-2.5 transition-opacity hover:opacity-80">
            <span className="flex items-center gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-xl text-sm font-black" style={{ background: "rgb(var(--brand))", color: "rgb(var(--brand-ink))" }}>◈</span>
              <span className="text-[17px] font-bold tracking-tight" style={{ color: "rgb(var(--ink))" }}>
                SolarGrid<span className="font-extrabold" style={{ color: "rgb(var(--accent))" }}> AI</span>
              </span>
            </span>
            <span className={`hidden rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest sm:inline-flex ${badgeTone}`}>{badge}</span>
          </Link>

          <div className="ml-auto flex items-center gap-2">
            {email && <span className="hidden max-w-[14rem] truncate text-xs sm:inline" style={{ color: "rgb(var(--ink-faint))" }}>{email}</span>}
            <ThemeToggle compact />
            <button
              onClick={onSignOut}
              className="rounded-full border px-4 py-1.5 text-xs font-semibold transition-all active:scale-95 hover:opacity-90"
              style={{ borderColor: "rgb(var(--line))", background: "rgb(var(--panel))", color: "rgb(var(--ink))" }}
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      <div className="flex">
        <aside
          className={`fixed inset-y-0 left-0 z-50 w-[17rem] border-r transition-all duration-300 ease-[cubic-bezier(0.32,0.72,0,1)] lg:sticky lg:top-[57px] lg:z-30 lg:h-[calc(100vh-57px)] lg:translate-x-0 ${width} ${drawerOpen ? "translate-x-0 shadow-2xl" : "-translate-x-full"}`}
          style={{ borderColor: "rgb(var(--line) / 0.6)", background: "rgb(var(--panel))" }}
        >
          <div className="flex h-full flex-col">
            <div className="flex items-center justify-between border-b px-4 py-3 lg:hidden" style={{ borderColor: "rgb(var(--line) / 0.6)" }}>
              <span className="text-sm font-semibold" style={{ color: "rgb(var(--ink))" }}>Menu</span>
              <button onClick={() => setDrawerOpen(false)} aria-label="Close navigation" className="flex h-8 w-8 items-center justify-center rounded-full border text-sm" style={{ borderColor: "rgb(var(--line))" }}>✕</button>
            </div>

            <nav className="scroll-pane flex-1 space-y-1 p-3">
              {links.map((link) => {
                const active = link.href === activeHref;
                const icon = ICONS[link.label] ?? "·";
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    title={collapsed ? link.label : undefined}
                    className="group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all active:scale-[0.98]"
                    style={{
                      background: active ? "rgb(var(--accent) / 0.1)" : "transparent",
                      color: active ? "rgb(var(--accent-strong))" : "rgb(var(--ink-muted))",
                      borderLeft: active ? "3px solid rgb(var(--accent))" : "3px solid transparent",
                    }}
                  >
                    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-xs transition-all" style={{ background: active ? "rgb(var(--accent))" : "rgb(var(--panel-raised))", color: active ? "white" : "rgb(var(--ink-faint))" }}>{icon}</span>
                    <span className={`${collapsed ? "lg:hidden" : ""} ${active ? "font-semibold" : ""}`}>{link.label}</span>
                    {active && !collapsed && <span className="ml-auto h-1.5 w-1.5 rounded-full bg-[rgb(var(--accent))]" />}
                  </Link>
                );
              })}
            </nav>

            <div className="border-t p-3" style={{ borderColor: "rgb(var(--line) / 0.6)" }}>
              <div className={`rounded-2xl p-3 ${collapsed ? "lg:hidden" : ""}`} style={{ background: "linear-gradient(135deg, rgb(var(--accent) / 0.12), rgb(var(--brand) / 0.12))", border: "1px solid rgb(var(--line) / 0.5)" }}>
                <p className="text-xs font-semibold" style={{ color: "rgb(var(--ink))" }}>Need help?</p>
                <p className="mt-1 text-xs leading-relaxed" style={{ color: "rgb(var(--ink-faint))" }}>Check scheme eligibility or chat with DISCOM support.</p>
              </div>
            </div>
          </div>
        </aside>

        {drawerOpen && <button aria-hidden tabIndex={-1} onClick={() => setDrawerOpen(false)} className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm lg:hidden animate-fade" />}

        <main className="min-w-0 flex-1 px-4 py-6 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-7xl page-enter">{children}</div>
        </main>
      </div>
    </div>
  );
}
