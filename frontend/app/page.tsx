"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { supabase } from "@/lib/supabase";

/**
 * Landing page.
 *
 * This used to be a redirect: signed out to /login, signed in to the
 * dashboard. It is now a real front door, and the redirect is gone — a public
 * page that bounces every visitor away cannot introduce the scheme to anyone
 * who has not already signed up.
 *
 * Signing in is still one click away, and the primary action changes for
 * someone already signed in: "Apply" becomes their dashboard rather than a
 * login wall they have already passed.
 */

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

  useEffect(() => {
    let active = true;
    supabase.auth.getSession().then(({ data }) => {
      if (active) setSignedIn(Boolean(data.session));
    });
    return () => {
      active = false;
    };
  }, [pathname]);

  // Until the session is known, send the call to action to the sign-in page.
  // It is the safe destination either way: a signed-in visitor is forwarded on
  // from there, and a signed-out one is where they need to be.
  const applyHref = signedIn ? "/citizen/applications/new" : "/login";

  return (
    <div className="mx-auto max-w-[1400px] px-4 sm:px-6">
      {/* ---- top navigation ---- */}
      <header className="flex flex-wrap items-center gap-x-8 gap-y-4 py-5">
        <Link href="/" className="flex items-center gap-2.5">
          <SolarMark />
          <span className="text-lg font-bold tracking-tight text-[rgb(var(--ink))]">
            SolarGrid
          </span>
        </Link>

        <nav className="flex flex-1 flex-wrap items-center justify-center gap-x-7 gap-y-2">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="text-[15px] font-semibold text-[rgb(var(--ink))] transition-opacity hover:opacity-70"
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <Link
          href={applyHref}
          className="rounded-full px-8 py-3 text-[15px] font-bold transition-transform hover:scale-[1.02]"
          style={{
            background: "rgb(var(--brand))",
            color: "rgb(var(--brand-ink))",
          }}
        >
          {signedIn ? "Dashboard" : "Apply"}
        </Link>
      </header>

      {/* ---- hero ---- */}
      <section className="relative overflow-hidden rounded-[28px]">
        {/*
          The photograph is a background rather than an <img> so the headline
          can sit over it at any width without a second layout to maintain.
          The gradient underneath is not decoration: if the file is missing the
          panel still reads as a warm sunlit roof and the type stays legible,
          rather than collapsing to a white box with white text on it.
        */}
        <div
          className="min-h-[420px] bg-cover bg-center sm:min-h-[520px] lg:min-h-[620px]"
          style={{
            backgroundImage: `linear-gradient(90deg, rgba(20,16,10,0.72) 0%, rgba(20,16,10,0.32) 45%, rgba(20,16,10,0.08) 70%), url('${HERO_IMAGE}'), linear-gradient(120deg, #b4711f 0%, #e0a04a 45%, #f6d08a 100%)`,
          }}
        >
          <div className="flex min-h-[420px] flex-col justify-center px-6 py-16 sm:min-h-[520px] sm:px-12 lg:min-h-[620px] lg:px-16">
            <h1 className="max-w-2xl text-[2.5rem] font-extrabold leading-[1.08] tracking-tight text-white sm:text-[3.25rem] lg:text-[4rem]">
              Bringing The
              <br />
              <span style={{ color: "rgb(var(--brand))" }}>Sun&rsquo;s Power</span>
              <br />
              To Every Home.
            </h1>

            <div className="mt-9">
              <Link
                href={applyHref}
                className="inline-flex items-center gap-2 rounded-full px-8 py-4 text-base font-bold transition-transform hover:scale-[1.02]"
                style={{
                  background: "rgb(var(--brand))",
                  color: "rgb(var(--brand-ink))",
                }}
              >
                Apply Now
                <span aria-hidden="true">-&gt;</span>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ---- what this actually is ----
          A landing page that only sells is a landing page that misleads. This
          says plainly what the service does and, just as plainly, what it is
          not: the screening is advisory and the DISCOM decides. */}
      <section className="grid gap-4 py-14 sm:grid-cols-3">
        <Feature
          title="Check before you commit"
          body="Your requested capacity is screened against the local distribution
                network — a machine-learning pre-screen, then a full power-flow
                simulation."
        />
        <Feature
          title="Plan the roof in 3D"
          body="Place the array on your own rooftop, set the tilt and bearing, and
                see where the sun falls across the day."
        />
        <Feature
          title="Find a verified installer"
          body="Only installers the DISCOM has approved appear here, with the
                distance from your site."
        />
      </section>

      <p className="pb-14 text-center text-xs text-[rgb(var(--ink-faint))]">
        A technical pre-screening service. It is not an approval: your
        distribution company decides whether a connection goes ahead.
      </p>
    </div>
  );
}

function Feature({ title, body }: { title: string; body: string }) {
  return (
    <div className="card">
      <h2 className="text-base font-bold">{title}</h2>
      <p className="mt-2 text-sm leading-relaxed">{body}</p>
    </div>
  );
}

/** The mark from the design: a sun over a panel grid. */
function SolarMark() {
  return (
    <svg width="34" height="34" viewBox="0 0 40 40" aria-hidden="true">
      <circle cx="20" cy="14" r="6" fill="#f5a623" />
      {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => (
        <rect
          key={deg}
          x="19.2"
          y="1.5"
          width="1.6"
          height="4"
          rx="0.8"
          fill="#f5a623"
          transform={`rotate(${deg} 20 14)`}
        />
      ))}
      <g fill="#1f7ae0">
        {[0, 1, 2].map((row) =>
          [0, 1, 2, 3].map((col) => (
            <rect
              key={`${row}-${col}`}
              x={7 + col * 6.6}
              y={23 + row * 4.4}
              width="5.6"
              height="3.4"
              rx="0.6"
            />
          ))
        )}
      </g>
    </svg>
  );
}
