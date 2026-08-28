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
    },
  },
  plugins: [],
};
export default config;
