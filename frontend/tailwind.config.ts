import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        safe: { bg: "#052e16", fg: "#4ade80", ring: "#166534" },
        caution: { bg: "#3b2f05", fg: "#facc15", ring: "#854d0e" },
        constrained: { bg: "#450a0a", fg: "#f87171", ring: "#991b1b" },
      },
      fontFamily: {
        display: ["var(--font-poppins)", "system-ui", "sans-serif"],
      },
      keyframes: {
        "fade-in": { from: { opacity: "0" }, to: { opacity: "1" } },
        "slide-up": { from: { opacity: "0", transform: "translateY(10px)" }, to: { opacity: "1", transform: "none" } },
        "scale-in": { from: { opacity: "0", transform: "scale(0.97)" }, to: { opacity: "1", transform: "scale(1)" } },
        shimmer: { "0%": { backgroundPosition: "200% 0" }, "100%": { backgroundPosition: "-200% 0" } },
      },
      animation: {
        "fade-in": "fade-in 0.5s cubic-bezier(0.23,1,0.32,1) both",
        "slide-up": "slide-up 0.6s cubic-bezier(0.23,1,0.32,1) both",
        "scale-in": "scale-in 0.4s cubic-bezier(0.175,0.885,0.32,1.275) both",
      },
      backdropBlur: { xs: "2px" },
    },
  },
  plugins: [],
};
export default config;
