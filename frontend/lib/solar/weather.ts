/**
 * Live sky conditions over the roof being planned.
 *
 * Two different things get called "where the sun is" and they come from
 * different places. The *direction* — azimuth and elevation — is astronomy:
 * lib/solar/sun.ts computes it from the NOAA algorithm and it is exact, so no
 * service is asked for it. What a forecast adds is the *state of the sky*
 * between that sun and the roof: cloud cover, and the beam actually arriving
 * once the cloud has taken its share.
 *
 * Open-Meteo is used because it needs no key. That matters here: an API key
 * would have to be shipped to the browser, and the repository's rule is that
 * keys are not committed. If the call fails the planner says so and draws the
 * geometry alone — a cloud figure invented locally would be exactly the kind
 * of plausible number this codebase refuses to print.
 */

const ENDPOINT = "https://api.open-meteo.com/v1/forecast";

export interface SkyConditions {
  /** Percent of sky covered, 0–100. */
  cloudCoverPct: number;
  /** Beam irradiance on a surface facing the sun, W/m². */
  directNormalWm2: number;
  /** Global horizontal irradiance, W/m². */
  globalHorizontalWm2: number;
  temperatureC: number;
  /** Instant the observation applies to. */
  observedAt: Date;
  /** Where it came from, so the UI never implies more than it has. */
  source: "open-meteo";
}

interface CurrentBlock {
  time?: string;
  cloud_cover?: number;
  temperature_2m?: number;
  shortwave_radiation?: number;
  direct_normal_irradiance?: number;
}

function finite(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

/**
 * Current conditions at a site, or null if the service did not answer with
 * usable numbers. Null is a real answer here and the caller must handle it;
 * there is no fallback figure, on purpose.
 */
export async function fetchSkyConditions(
  latitude: number,
  longitude: number,
  signal?: AbortSignal
): Promise<SkyConditions | null> {
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return null;

  const url =
    `${ENDPOINT}?latitude=${latitude.toFixed(4)}&longitude=${longitude.toFixed(4)}` +
    "&current=cloud_cover,temperature_2m,shortwave_radiation,direct_normal_irradiance" +
    "&timezone=auto";

  const response = await fetch(url, { signal });
  if (!response.ok) return null;

  const body = (await response.json()) as { current?: CurrentBlock };
  const current = body.current;
  if (!current) return null;

  const cloud = finite(current.cloud_cover);
  const dni = finite(current.direct_normal_irradiance);
  const ghi = finite(current.shortwave_radiation);
  const temp = finite(current.temperature_2m);
  // Cloud cover is the one field the planner draws conclusions from; without
  // it there is nothing worth reporting.
  if (cloud === null) return null;

  const observed = current.time ? new Date(current.time) : new Date();

  return {
    cloudCoverPct: Math.max(0, Math.min(100, cloud)),
    directNormalWm2: dni ?? 0,
    globalHorizontalWm2: ghi ?? 0,
    temperatureC: temp ?? Number.NaN,
    observedAt: Number.isNaN(observed.getTime()) ? new Date() : observed,
    source: "open-meteo",
  };
}

/** Plain-language sky, for a caption next to the sun rays. */
export function skyLabel(cloudCoverPct: number): string {
  if (cloudCoverPct <= 12) return "Clear";
  if (cloudCoverPct <= 40) return "Mostly clear";
  if (cloudCoverPct <= 70) return "Partly cloudy";
  if (cloudCoverPct <= 90) return "Mostly cloudy";
  return "Overcast";
}

/**
 * How solid the sun rays should look, 0.25–1.

 * Drawn from measured cloud cover rather than chosen: an overcast roof gets
 * faint rays because the beam really is mostly gone, and the picture should
 * not promise sunlight the sky is not delivering.
 */
export function rayOpacityFor(cloudCoverPct: number | null): number {
  if (cloudCoverPct === null) return 0.85;
  return 0.25 + 0.75 * (1 - Math.max(0, Math.min(100, cloudCoverPct)) / 100);
}
