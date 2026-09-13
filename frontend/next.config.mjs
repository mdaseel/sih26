/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Cesium is ~12 MB and contains GLSL/worker strings with \0 octals that
  // Terser breaks when minified inside template literals in strict mode.
  // We keep it as a separate chunk and disable mutation of its source.
  transpilePackages: [],
  webpack: (config) => {
    // Let Cesium's own workers/shaders pass through untouched; they are
    // served as static assets from public/cesium, not bundled.
    config.module.unknownContextCritical = false;
    return config;
  },
  // Ensure the huge Cesium chunk doesn't get pruned by Render's CDN between
  // deploys — Next already hashes it, but we must not inline it.
  productionBrowserSourceMaps: false,
};
export default nextConfig;
