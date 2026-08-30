import type { Metadata } from "next";
import "./globals.css";

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
    <html lang="en">
      <head>
        {/*
          Applies the stored theme before the first paint.
          Anything that waits for React runs after the browser has already
          painted, so a reader who chose light would see a dark flash on every
          navigation. Inline and blocking is the one place that is warranted.
        */}
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=localStorage.getItem('solargrid-theme');if(t==='light'){document.documentElement.classList.add('light')}}catch(e){}})();`,
          }}
        />
      </head>
      <body>
        {children}
        <footer
          className="border-t px-6 py-4 text-center text-xs"
          style={{
            borderColor: "rgb(var(--line) / 0.6)",
            color: "rgb(var(--ink-faint))",
          }}
        >
          SolarGrid AI · Prototype · Synthetic grid data (IEEE Comprehensive Test
          Feeder) · Not an official DISCOM or PM Surya Ghar portal
        </footer>
      </body>
    </html>
  );
}
