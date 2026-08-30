"use client";

import { useEffect, useState } from "react";

/**
 * Light / dark switch.
 *
 * The choice is stored per browser and applied by adding `light` to <html>,
 * which is what globals.css keys the whole palette off. Reading and writing
 * localStorage are both wrapped: a private window, cleared site data, or a
 * browser set to block storage all throw on access, and a theme button is not
 * worth taking the page down for.
 *
 * The first paint is handled by a blocking script in the root layout, not
 * here — by the time React hydrates it is already too late to avoid a flash.
 */

export type Theme = "dark" | "light";

const STORAGE_KEY = "solargrid-theme";

export function applyTheme(theme: Theme) {
  // Light is the default, so the class marks the exception.
  document.documentElement.classList.toggle("dark", theme === "dark");
  try {
    window.localStorage.setItem(STORAGE_KEY, theme);
  } catch {
    /* storage unavailable: the theme still applies for this page */
  }
}

function currentTheme(): Theme {
  if (typeof document === "undefined") return "light";
  return document.documentElement.classList.contains("dark") ? "dark" : "light";
}

export function ThemeToggle({ compact = false }: { compact?: boolean }) {
  // Starts on the default and corrects itself on mount. Rendering the real
  // value during SSR is impossible — the server cannot know what this browser
  // stored — and guessing produces a hydration mismatch.
  const [theme, setTheme] = useState<Theme>("light");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setTheme(currentTheme());
    setMounted(true);
  }, []);

  function toggle() {
    const next: Theme = theme === "dark" ? "light" : "dark";
    applyTheme(next);
    setTheme(next);
  }

  const label = theme === "dark" ? "Switch to light theme" : "Switch to dark theme";

  return (
    <button
      type="button"
      onClick={toggle}
      title={label}
      aria-label={label}
      // Until mounted the icon would be a guess; keep it invisible rather than
      // flip it under the reader a moment after they look at it.
      className={`btn-ghost !px-2.5 !py-1.5 ${compact ? "!text-xs" : "!text-sm"} ${
        mounted ? "" : "opacity-0"
      }`}
    >
      {theme === "dark" ? (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <circle cx="12" cy="12" r="4.2" stroke="currentColor" strokeWidth="1.8" />
          <path
            d="M12 2.5v2.2M12 19.3v2.2M4.2 12H2m20 0h-2.2M5.6 5.6 4 4m16 16-1.6-1.6M5.6 18.4 4 20M20 4l-1.6 1.6"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
          />
        </svg>
      ) : (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path
            d="M20 13.4A8.4 8.4 0 1 1 10.6 4a6.8 6.8 0 0 0 9.4 9.4Z"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinejoin="round"
          />
        </svg>
      )}
      {!compact && <span>{theme === "dark" ? "Light" : "Dark"}</span>}
    </button>
  );
}
