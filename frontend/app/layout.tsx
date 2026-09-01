import type { Metadata } from "next";
import { Poppins } from "next/font/google";
import "./globals.css";

/**
 * Typeface.
 *
 * Poppins, the geometric sans from the design: rounded bowls, single-storey
 * 'g', wide apertures. It carries the whole interface — navigation, forms,
 * tables, readouts — so the weights loaded here are the ones actually used.
 * 800 exists for the landing headline and nowhere else.
 *
 * Loaded through next/font, which self-hosts the files at build time. That
 * matters for more than speed: no request leaves the user's browser for
 * Google's servers, and the font cannot shift under us when the CDN changes.
 *
 * Exposed as a CSS variable rather than a class so globals.css can decide
 * where it applies.
 */
const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-poppins",
  display: "swap",
});

export const metadata: Metadata = {
  title: "SolarGrid AI",
  description:
    "Rooftop solar hosting-capacity screening: ML pre-screening verified by deterministic power flow.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={poppins.variable}>
      <head>
        {/*
          Applies the stored theme before the first paint.
          Anything that waits for React runs after the browser has already
          painted, so a reader who chose dark would see a light flash on every
          navigation. Inline and blocking is the one place that is warranted.
        */}
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=localStorage.getItem('solargrid-theme');if(t==='dark'){document.documentElement.classList.add('dark')}}catch(e){}})();`,
          }}
        />
      </head>
      <body>
        {children}
        <footer
          className="mt-8 border-t px-6 py-6 text-center text-xs"
          style={{
            borderColor: "rgb(var(--line))",
            background: "rgb(var(--panel) / 0.6)",
            backdropFilter: "blur(12px)",
            color: "rgb(var(--ink-faint))",
          }}
        >
          <span className="inline-flex items-center gap-2">
            <span className="flex h-6 w-6 items-center justify-center rounded-lg text-[10px] font-black" style={{ background: "rgb(var(--brand))", color: "rgb(var(--brand-ink))" }}>◈</span>
            SolarGrid AI · Prototype · Synthetic grid data (IEEE Test Feeder) · Not an official DISCOM or PM Surya Ghar portal
          </span>
        </footer>
      </body>
    </html>
  );
}
