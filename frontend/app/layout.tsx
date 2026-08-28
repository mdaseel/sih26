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
      <body>
        {children}
        <footer className="border-t border-slate-900 px-6 py-4 text-center text-xs text-slate-600">
          SolarGrid AI · Prototype · Synthetic grid data (IEEE Comprehensive Test
          Feeder) · Not an official DISCOM or PM Surya Ghar portal
        </footer>
      </body>
    </html>
  );
}
