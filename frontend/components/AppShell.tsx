"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { ThemeToggle } from "@/components/ThemeToggle";

/**
 * The shell every portal sits in: a left sidebar, a hamburger, and the theme
 * switch.
 *
 * One component for all three portals because the three had drifted — the same
 * header rebuilt three times with slightly different spacing and sign-out
 * behaviour. They differ in their links and their badge, so those are props;
 * everything else is shared.
 *
 * Behaviour differs by width on purpose. On a wide screen the sidebar is
 * always there and the hamburger only collapses it to icons, because a
 * reviewer moving between applications and feeders wants the map of the
 * section visible. On a narrow one it is a drawer over the content, closed by
 * default, and it closes again on navigation — a menu that stays open over the
 * page you just asked for is a menu in the way.
 */

export interface NavLink {
  href: string;
  label: string;
}

export function AppShell({
  links,
  badge,
  homeHref,
  email,
  onSignOut,
  children,
}: {
  links: NavLink[];
  /** Short portal name shown under the wordmark: Citizen, DISCOM, Installer. */
  badge: string;
  homeHref: string;
  email?: string | null;
  onSignOut: () => void;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  // Close the drawer when the route changes. Without this the menu covers the
  // page it was used to reach.
  useEffect(() => {
    setDrawerOpen(false);
  }, [pathname]);

  // Escape closes it, because a full-screen overlay with no keyboard exit is a
  // trap for anyone not using a mouse.
  useEffect(() => {
    if (!drawerOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setDrawerOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [drawerOpen]);

  const width = collapsed ? "lg:w-[4.5rem]" : "lg:w-64";

  /**
   * Exactly one link is ever active.
   *
   * A plain prefix test lights up every ancestor: on /citizen/applications/new
   * both "My applications" and "New application" matched, so two entries were
   * highlighted at once and neither told you where you were. The longest
   * matching href wins instead, which is the most specific section containing
   * the page — and only that one is marked.
   */
  const activeHref = links
    .filter(
      (link) => pathname === link.href || pathname.startsWith(`${link.href}/`)
    )
    .sort((a, b) => b.href.length - a.href.length)[0]?.href;

  return (
    <div className="min-h-screen">
      {/* ---- top bar ---- */}
      <header
        className="sticky top-0 z-40 border-b backdrop-blur"
        style={{
          borderColor: "rgb(var(--line) / 0.6)",
          background: "rgb(var(--panel) / 0.82)",
        }}
      >
        <div className="flex items-center gap-3 px-4 py-2.5">
          <button
            type="button"
            onClick={() =>
              // The same control does the useful thing at each width: opens the
              // drawer where there is no room, collapses the rail where there is.
              window.matchMedia("(min-width: 1024px)").matches
                ? setCollapsed((c) => !c)
                : setDrawerOpen((o) => !o)
            }
            aria-label="Toggle navigation"
            aria-expanded={drawerOpen}
            className="btn-ghost !px-2.5 !py-2"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M4 7h16M4 12h16M4 17h16"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          </button>

          <Link href={homeHref} className="flex items-baseline gap-2">
            <span className="text-lg font-semibold" style={{ color: "rgb(var(--ink))" }}>
              SolarGrid<span className="text-sky-400"> AI</span>
            </span>
            <span
              className="rounded border px-1.5 py-0.5 text-[10px] uppercase tracking-wide"
              style={{
                borderColor: "rgb(var(--line))",
                color: "rgb(var(--ink-faint))",
              }}
            >
              {badge}
            </span>
          </Link>

          <div className="ml-auto flex items-center gap-2">
            {email && (
              <span
                className="hidden text-xs sm:inline"
                style={{ color: "rgb(var(--ink-faint))" }}
              >
                {email}
              </span>
            )}
            <ThemeToggle compact />
            <button onClick={onSignOut} className="btn-ghost !px-3 !py-1.5 !text-xs">
              Sign out
            </button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* ---- sidebar ---- */}
        <aside
          className={`fixed inset-y-0 left-0 z-50 w-64 transform border-r transition-transform duration-200 lg:sticky lg:top-[3.25rem] lg:z-30 lg:h-[calc(100vh-3.25rem)] lg:translate-x-0 lg:transition-[width] ${width} ${
            drawerOpen ? "translate-x-0" : "-translate-x-full"
          }`}
          style={{
            borderColor: "rgb(var(--line) / 0.6)",
            background: "rgb(var(--panel))",
          }}
        >
          <div className="flex h-full flex-col">
            {/* The drawer needs its own header: on a narrow screen it covers
                the top bar, so the way out has to travel with it. */}
            <div
              className="flex items-center justify-between border-b px-4 py-3 lg:hidden"
              style={{ borderColor: "rgb(var(--line) / 0.6)" }}
            >
              <span className="text-sm font-semibold" style={{ color: "rgb(var(--ink))" }}>
                Menu
              </span>
              <button
                onClick={() => setDrawerOpen(false)}
                aria-label="Close navigation"
                className="btn-ghost !px-2 !py-1"
              >
                ✕
              </button>
            </div>

            <nav className="scroll-pane flex-1 space-y-1 p-3">
              {links.map((link) => {
                const active = link.href === activeHref;
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    title={collapsed ? link.label : undefined}
                    className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors"
                    style={{
                      background: active ? "rgb(var(--panel-raised))" : "transparent",
                      color: active ? "rgb(var(--ink))" : "rgb(var(--ink-muted))",
                    }}
                  >
                    <span
                      className="h-1.5 w-1.5 shrink-0 rounded-full transition-colors"
                      style={{
                        background: active
                          ? "rgb(var(--accent))"
                          : "rgb(var(--ink-faint) / 0.45)",
                      }}
                    />
                    <span className={collapsed ? "lg:hidden" : ""}>{link.label}</span>
                  </Link>
                );
              })}
            </nav>
          </div>
        </aside>

        {/* Scrim. Only on small screens, where the drawer floats over content. */}
        {drawerOpen && (
          <button
            aria-hidden="true"
            tabIndex={-1}
            onClick={() => setDrawerOpen(false)}
            className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          />
        )}

        <main className="min-w-0 flex-1 px-4 py-6 sm:px-6">{children}</main>
      </div>
    </div>
  );
}
