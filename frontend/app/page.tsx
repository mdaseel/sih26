"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { supabase } from "@/lib/supabase";

const HERO_IMAGE = "/hero-rooftop.jpg";
const NAV = [
  { href: "/citizen/dashboard", label: "Dashboard" },
  { href: "/citizen/applications", label: "My Applications" },
  { href: "/citizen/map", label: "Map" },
  { href: "/citizen/vendors", label: "Installers" },
  { href: "/citizen/scheme", label: "About Scheme" },
];

export default function Home() {
  const pathname = usePathname();
  const [signedIn, setSignedIn] = useState<boolean | null>(null);
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    let active = true;
    supabase.auth.getSession().then(({ data }) => { if (active) setSignedIn(Boolean(data.session)); });
    return () => { active = false; };
  }, [pathname]);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  const applyHref = signedIn ? "/citizen/applications/new" : "/login";

  return (
    <div className="min-h-screen bg-[rgb(var(--surface))]">
      {/* Nav — Apple translucent */}
      <header
        className={`sticky top-0 z-40 border-b transition-all ${scrolled ? "shadow-sm" : ""}`}
        style={{
          background: scrolled ? "rgb(var(--panel) / 0.78)" : "rgb(var(--panel) / 0.55)",
          backdropFilter: "blur(20px) saturate(180%)",
          WebkitBackdropFilter: "blur(20px) saturate(180%)",
          borderColor: "rgb(var(--line) / 0.5)",
        }}
      >
        <div className="mx-auto flex max-w-[1400px] flex-wrap items-center gap-4 px-4 py-3 sm:px-6">
          <Link href="/" className="flex items-center gap-2.5 transition-transform active:scale-95">
            <SolarMark />
            <span className="text-[18px] font-bold tracking-tight" style={{ color: "rgb(var(--ink))" }}>SolarGrid<span style={{ color: "rgb(var(--accent))" }}> AI</span></span>
            <span className="hidden rounded-full bg-[rgb(var(--brand))] px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest text-[rgb(var(--brand-ink))] sm:inline-flex">Live</span>
          </Link>
          <nav className="hidden flex-1 items-center justify-center gap-7 md:flex">
            {NAV.map((item) => (
              <Link key={item.href} href={item.href} className="text-sm font-medium transition-colors hover:opacity-60" style={{ color: "rgb(var(--ink))" }}>{item.label}</Link>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-3">
            <ThemeToggle compact />
            <Link href="/login" className="hidden text-sm font-medium sm:inline" style={{ color: "rgb(var(--ink-muted))" }}>Sign in</Link>
            <Link href={applyHref} className="rounded-full px-6 py-2.5 text-sm font-bold transition-all active:scale-95 hover:scale-[1.02] hover:shadow-lg" style={{ background: "rgb(var(--brand))", color: "rgb(var(--brand-ink))", boxShadow: "0 4px 16px rgb(var(--brand) / 0.3)" }}>{signedIn ? "Dashboard →" : "Apply now →"}</Link>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-[1400px] px-4 sm:px-6">
        {/* Hero — interactive, layered */}
        <section className="relative mt-6 overflow-hidden rounded-[32px] animate-scale-in" style={{ boxShadow: "0 24px 64px rgb(var(--shadow) / 0.12)" }}>
          <div className="relative min-h-[480px] bg-cover bg-center sm:min-h-[560px] lg:min-h-[640px]" style={{ backgroundImage: `linear-gradient(100deg, rgba(8,12,28,0.82) 0%, rgba(8,12,28,0.55) 42%, rgba(8,12,28,0.12) 68%), url('${HERO_IMAGE}'), linear-gradient(135deg, #0f172a 0%, #1e3a5f 45%, #38bdf8 100%)` }}>
            {/* Grid pattern overlay */}
            <div className="pointer-events-none absolute inset-0 opacity-[0.07]" style={{ backgroundImage: "linear-gradient(rgba(255,255,255,0.4) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.4) 1px, transparent 1px)", backgroundSize: "32px 32px" }} />
            {/* Floating stats — Apple hint of depth */}
            <div className="absolute right-4 top-4 hidden gap-3 lg:flex">
              <div className="glass-strong rounded-2xl px-4 py-3 animate-float" style={{ animationDelay: "0ms" }}>
                <div className="text-[11px] font-semibold uppercase tracking-widest" style={{ color: "rgb(var(--ink-faint))" }}>Screened</div>
                <div className="font-mono text-lg font-bold" style={{ color: "rgb(var(--ink))" }}>1,692<span className="text-xs font-normal" style={{ color: "rgb(var(--ink-faint))" }}> scenarios</span></div>
              </div>
              <div className="glass-strong rounded-2xl px-4 py-3 animate-float" style={{ animationDelay: "300ms" }}>
                <div className="text-[11px] font-semibold uppercase tracking-widest" style={{ color: "rgb(var(--ink-faint))" }}>Verification</div>
                <div className="text-sm font-bold" style={{ color: "rgb(var(--ink))" }}>Power flow <span className="text-xs font-normal text-emerald-600">✓ decides</span></div>
              </div>
            </div>

            <div className="relative flex min-h-[480px] flex-col justify-center px-6 py-14 sm:min-h-[560px] sm:px-10 lg:min-h-[640px] lg:px-14">
              <div className="inline-flex w-fit items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-semibold backdrop-blur-md animate-slide-up" style={{ background: "rgb(255 255 255 / 0.12)", borderColor: "rgb(255 255 255 / 0.2)", color: "white" }}>
                <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" /> IEEE Comprehensive Test Feeder · Validated model
              </div>
              <h1 className="mt-5 max-w-2xl text-[2.6rem] font-extrabold leading-[0.95] tracking-tight text-white sm:text-[3.5rem] lg:text-[4.4rem] animate-slide-up" style={{ animationDelay: "80ms", letterSpacing: "-0.03em" }}>
                Bringing The<br />
                <span className="bg-gradient-to-r from-[#d4f34a] to-[#facc15] bg-clip-text text-transparent">Sun&apos;s Power</span><br />
                To Every Home.
              </h1>
              <p className="mt-5 max-w-xl text-[15px] leading-relaxed text-white/80 animate-slide-up" style={{ animationDelay: "160ms" }}>
                Machine-learning pre-screen in milliseconds, then a deterministic power-flow verification. The power flow decides — the model is a fast opinion, not the answer.
              </p>
              <div className="mt-8 flex flex-wrap gap-3 animate-slide-up" style={{ animationDelay: "240ms" }}>
                <Link href={applyHref} className="inline-flex items-center gap-2 rounded-full px-8 py-4 text-base font-bold transition-all active:scale-95 hover:scale-[1.02] hover:shadow-xl" style={{ background: "rgb(var(--brand))", color: "rgb(var(--brand-ink))", boxShadow: "0 8px 24px rgb(var(--brand) / 0.35)" }}>Apply now <span>→</span></Link>
                <Link href="/citizen/scheme" className="inline-flex items-center gap-2 rounded-full border px-8 py-4 text-base font-semibold backdrop-blur-md transition-all active:scale-95 hover:bg-white/10" style={{ borderColor: "rgb(255 255 255 / 0.25)", color: "white" }}>How it works</Link>
              </div>
              <div className="mt-8 flex flex-wrap gap-6 text-xs text-white/60 animate-slide-up" style={{ animationDelay: "320ms" }}>
                <span className="flex items-center gap-1.5"><span className="h-1.5 w-1.5 rounded-full bg-emerald-400" /> Millisecond pre-screen</span>
                <span className="flex items-center gap-1.5"><span className="h-1.5 w-1.5 rounded-full bg-sky-400" /> Full power-flow simulation</span>
                <span className="flex items-center gap-1.5"><span className="h-1.5 w-1.5 rounded-full bg-amber-400" /> DISCOM decides</span>
              </div>
            </div>
          </div>
        </section>

        {/* Features — staggered, interactive */}
        <section className="grid gap-4 py-10 sm:grid-cols-3 stagger">
          <Feature icon="◈" title="Check before you commit" body="Your requested capacity is screened against the local distribution network — ML pre-screen then full power-flow simulation. You know in seconds, not weeks." accent="brand" href="/citizen/scheme" />
          <Feature icon="⬢" title="Plan the roof in 3D" body="Place the array on your rooftop, set tilt and bearing, see where the sun falls across the day with real terrain and buildings." accent="accent" href={applyHref} />
          <Feature icon="◎" title="Find a verified installer" body="Only installers the DISCOM has approved, sorted by true road distance from your site. No guesswork, no cold calls." accent="emerald" href="/citizen/vendors" />
        </section>

        {/* Trust bar */}
        <section className="grid gap-4 pb-10 sm:grid-cols-4">
          <TrustMetric value="~50ms" label="Power-flow solve" sub="BASE + PV cases" />
          <TrustMetric value="11" label="Bisection solves" sub="Hosting capacity" />
          <TrustMetric value="97.6%" label="Model test accuracy" sub="With known limits disclosed" />
          <TrustMetric value="1 feeder" label="One topology, honestly" sub="Research network, not SCADA" />
        </section>

        {/* Bottom CTA */}
        <section className="mb-10 overflow-hidden rounded-[24px] p-[1.5px]" style={{ background: "linear-gradient(135deg, rgb(var(--accent)), rgb(var(--brand)))" }}>
          <div className="flex flex-wrap items-center justify-between gap-6 rounded-[22px] px-6 py-6 sm:px-8" style={{ background: "rgb(var(--panel))" }}>
            <div>
              <h3 className="text-lg font-bold" style={{ color: "rgb(var(--ink))" }}>Ready to see if your roof can host solar?</h3>
              <p className="mt-1 text-sm" style={{ color: "rgb(var(--ink-faint))" }}>Start an application — it takes two minutes and you&apos;ll be screened instantly.</p>
            </div>
            <Link href={applyHref} className="shrink-0 rounded-full px-8 py-3.5 text-sm font-bold transition-all active:scale-95 hover:scale-[1.02] hover:shadow-lg" style={{ background: "rgb(var(--brand))", color: "rgb(var(--brand-ink))", boxShadow: "0 4px 16px rgb(var(--brand) / 0.3)" }}>Start application →</Link>
          </div>
        </section>

        <p className="pb-8 text-center text-xs" style={{ color: "rgb(var(--ink-ghost))" }}>A technical pre-screening service. It is not an approval: your distribution company decides whether a connection goes ahead. • IEEE data • Synthetic coordinates • Fictional vendors</p>
      </div>
    </div>
  );
}

function Feature({ icon, title, body, accent, href }: { icon: string; title: string; body: string; accent: "brand" | "accent" | "emerald"; href: string }) {
  const bg = accent === "brand" ? "rgb(var(--brand))" : accent === "accent" ? "rgb(var(--accent))" : "#10b981";
  return (
    <Link href={href} className="card-interactive group block">
      <div className="flex h-10 w-10 items-center justify-center rounded-xl text-sm font-bold text-white transition-transform group-hover:scale-110 group-hover:rotate-3" style={{ background: bg }}>{icon}</div>
      <h2 className="mt-4 text-[15px] font-bold" style={{ color: "rgb(var(--ink))" }}>{title}</h2>
      <p className="mt-2 text-sm leading-relaxed" style={{ color: "rgb(var(--ink-muted))" }}>{body}</p>
      <span className="mt-4 inline-flex items-center gap-1 text-xs font-semibold opacity-60 transition-all group-hover:opacity-100 group-hover:translate-x-1 group-hover:text-[rgb(var(--accent-strong))]" style={{ color: "rgb(var(--ink-faint))" }}>Learn more →</span>
    </Link>
  );
}
function TrustMetric({ value, label, sub }: { value: string; label: string; sub: string }) {
  return (
    <div className="card text-center">
      <div className="font-mono text-2xl font-bold" style={{ color: "rgb(var(--ink))" }}>{value}</div>
      <div className="text-xs font-semibold" style={{ color: "rgb(var(--ink))" }}>{label}</div>
      <div className="text-xs" style={{ color: "rgb(var(--ink-faint))" }}>{sub}</div>
    </div>
  );
}
function SolarMark() {
  return (
    <svg width="36" height="36" viewBox="0 0 40 40" aria-hidden="true" className="shrink-0">
      <circle cx="20" cy="14" r="6" fill="#f59e0b" />
      {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => <rect key={deg} x="19.2" y="1.5" width="1.6" height="4" rx="0.8" fill="#f59e0b" transform={`rotate(${deg} 20 14)`} />)}
      <g fill="#0ea5e9">{[0, 1, 2].map((row) => [0, 1, 2, 3].map((col) => <rect key={`${row}-${col}`} x={7 + col * 6.6} y={23 + row * 4.4} width="5.6" height="3.4" rx="0.6" />))}</g>
    </svg>
  );
}
