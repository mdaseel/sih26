/**
 * Copies CesiumJS's runtime assets into public/cesium.
 *
 * Cesium fetches its own web workers, glyph atlases, shaders and widget CSS at
 * runtime from CESIUM_BASE_URL — they are data files, not modules, so a
 * bundler cannot reach them by following imports. They have to sit on disk
 * under the public path before the viewer starts.
 *
 * public/cesium is generated, so it is gitignored and rebuilt by postinstall.
 * That keeps ~7 MB of vendor binaries out of the repository while still
 * guaranteeing a fresh clone works after `npm install`.
 */

import { cp, mkdir, rm, stat } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..");
const source = join(root, "node_modules", "cesium", "Build", "Cesium");
const target = join(root, "public", "cesium");

const DIRECTORIES = ["Assets", "ThirdParty", "Widgets", "Workers"];

async function exists(path) {
  try {
    await stat(path);
    return true;
  } catch {
    return false;
  }
}

async function main() {
  if (!(await exists(source))) {
    // Not an error worth failing an install over: someone may be installing
    // without Cesium, and the 3D view reports its own missing assets clearly.
    console.warn(
      "[cesium] node_modules/cesium/Build/Cesium not found — skipping asset copy."
    );
    return;
  }

  await rm(target, { recursive: true, force: true });
  await mkdir(target, { recursive: true });

  for (const directory of DIRECTORIES) {
    const from = join(source, directory);
    if (!(await exists(from))) {
      console.warn(`[cesium] ${directory} missing from the Cesium build — skipped.`);
      continue;
    }
    await cp(from, join(target, directory), { recursive: true });
  }

  console.log(`[cesium] assets copied to public/cesium`);
}

main().catch((error) => {
  console.error("[cesium] failed to copy assets:", error);
  process.exitCode = 1;
});
