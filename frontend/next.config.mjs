/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Cesium 1.144 ships GLSL/worker strings containing \0 octals inside
  // ` ` template literals. SWC's strict parser (used by `next build`)
  // rejects them as "Octal escape sequences are not allowed in template
  // strings" — dev (`next dev`, no minify) never hits this. Transpiling
  // Cesium through SWC rewrites those escapes to \x00 before minify, which
  // is the documented fix for Next + Cesium.
  transpilePackages: ["cesium", "@cesium/engine", "@spz-loader/core"],
  webpack: (config) => {
    config.module.unknownContextCritical = false;
    // Workers are served from public/cesium (copied by postinstall/build),
    // not resolved through the bundler.
    return config;
  },
  productionBrowserSourceMaps: false,
};
export default nextConfig;
