/**
 * Is this a sensible place and orientation to put panels?
 *
 * What this can honestly answer, and what it cannot, is the whole design of
 * this module.
 *
 * It CAN answer geometry. Where the sun goes over a day at this latitude, how
 * squarely the panel faces it, whether the tilt is near the annual optimum,
 * whether the array fits the roof. That is trigonometry on real numbers and it
 * is reliable.
 *
 * It CANNOT answer shading. Knowing that a neighbouring building shades this
 * roof at 4pm in December requires the geometry of that building, and Cesium's
 * OSM building data is extruded footprints — no chimneys, no water tanks, no
 * trees, no parapet walls, and nothing at all in areas OSM has not mapped. So
 * where building data is absent the verdict says shading is UNASSESSED rather
 * than assuming none, and where it is present the result is described as a
 * visual shadow check, never as a shading study.
 *
 * The distinction is the difference between a tool and a liability: a citizen
 * who is told POOR because of a tree that was never in the data has been
 * misled, and so has one told GOOD for the same reason.
 */

import { estimatedOptimalTilt, incidenceCosine, optimalAzimuth, type SunPosition } from "@/lib/solar/sun";

export type SuitabilityVerdict = "GOOD" | "PARTIAL" | "POOR" | "UNKNOWN";
export type ShadingConfidence = "ASSESSED" | "PARTIAL" | "UNASSESSED";

export interface SuitabilityInput {
  latitude: number;
  tiltDeg: number;
  azimuthDeg: number;
  /** Sun positions sampled across the assessed day. */
  daySamples: SunPosition[];
  /** True when 3D building geometry actually loaded for this location. */
  buildingDataAvailable: boolean;
  /** Fraction of sampled daylight hours the array is in shadow, if measurable. */
  shadedFraction: number | null;
  /** Declared roof area, m², when known. */
  roofAreaSqm: number | null;
  /** Ground area the array occupies, m². */
  arrayAreaSqm: number;
}

export interface SuitabilityResult {
  verdict: SuitabilityVerdict;
  /** 0–100. Geometry only — it is not a yield prediction. */
  score: number;
  sunExposure: "High" | "Moderate" | "Low";
  orientation: "Suitable" | "Acceptable" | "Poor";
  tiltAssessment: "Near optimal" | "Acceptable" | "Far from optimal";
  shading: ShadingConfidence;
  shadedFractionPct: number | null;
  reasons: string[];
  warnings: string[];
  /** Estimated annual-optimum tilt, presented as a starting point. */
  suggestedTilt: number;
  suggestedAzimuth: number;
}

/**
 * Mean incidence cosine over the daylight samples, weighted by sun elevation.
 *
 * Weighting by elevation is a stand-in for the fact that low sun travels
 * through more atmosphere and delivers less energy. It keeps a panel that only
 * performs at dawn from scoring like one that performs at noon.
 */
function weightedExposure(input: SuitabilityInput): number {
  const daylight = input.daySamples.filter((s) => s.elevation > 0);
  if (daylight.length === 0) return 0;

  let weighted = 0;
  let weight = 0;
  for (const sample of daylight) {
    const w = Math.sin((sample.elevation * Math.PI) / 180);
    weighted += incidenceCosine(sample, input.tiltDeg, input.azimuthDeg) * w;
    weight += w;
  }
  return weight > 0 ? weighted / weight : 0;
}

/** Smallest angle between two compass bearings, degrees. */
export function bearingDifference(a: number, b: number): number {
  const diff = Math.abs(((a - b) % 360) + 360) % 360;
  return diff > 180 ? 360 - diff : diff;
}

export function assessSuitability(input: SuitabilityInput): SuitabilityResult {
  const reasons: string[] = [];
  const warnings: string[] = [];

  const suggestedTilt = estimatedOptimalTilt(input.latitude);
  const suggestedAzimuth = optimalAzimuth(input.latitude);

  const exposure = weightedExposure(input);
  const azimuthError = bearingDifference(input.azimuthDeg, suggestedAzimuth);
  const tiltError = Math.abs(input.tiltDeg - suggestedTilt);

  // ---- orientation ----
  const orientation: SuitabilityResult["orientation"] =
    azimuthError <= 30 ? "Suitable" : azimuthError <= 75 ? "Acceptable" : "Poor";
  if (orientation === "Suitable") {
    reasons.push(
      `Array faces within ${Math.round(azimuthError)}° of the optimum bearing for this latitude.`
    );
  } else {
    warnings.push(
      `Array faces ${Math.round(azimuthError)}° away from the optimum bearing (${suggestedAzimuth}°), which costs output.`
    );
  }

  // ---- tilt ----
  const tiltAssessment: SuitabilityResult["tiltAssessment"] =
    tiltError <= 7 ? "Near optimal" : tiltError <= 15 ? "Acceptable" : "Far from optimal";
  if (tiltAssessment === "Far from optimal") {
    warnings.push(
      `Tilt of ${input.tiltDeg}° is well away from the estimated annual optimum of ${suggestedTilt}° here.`
    );
  }

  // ---- sun exposure ----
  const sunExposure: SuitabilityResult["sunExposure"] =
    exposure >= 0.75 ? "High" : exposure >= 0.5 ? "Moderate" : "Low";
  if (sunExposure === "Low") {
    warnings.push(
      "The array intercepts little of the available sun on the assessed day at this tilt and bearing."
    );
  }

  // ---- shading: only claimed where the data can support it ----
  let shading: ShadingConfidence;
  let shadedFractionPct: number | null = null;
  if (!input.buildingDataAvailable) {
    shading = "UNASSESSED";
    warnings.push(
      "No 3D building data covers this location, so nothing nearby could be tested for shadow. Trees, tanks and parapets are never in this data."
    );
  } else if (input.shadedFraction == null) {
    shading = "UNASSESSED";
  } else {
    shading = "PARTIAL";
    shadedFractionPct = Math.round(input.shadedFraction * 100);
    if (input.shadedFraction > 0.3) {
      warnings.push(
        `Surrounding buildings put the array in shadow for about ${shadedFractionPct}% of the sampled daylight.`
      );
    } else {
      reasons.push(
        `Modelled buildings shade the array for about ${shadedFractionPct}% of the sampled daylight.`
      );
    }
  }

  // ---- roof area ----
  if (input.roofAreaSqm != null && input.roofAreaSqm > 0) {
    const utilisation = input.arrayAreaSqm / input.roofAreaSqm;
    if (utilisation > 1) {
      warnings.push(
        `The array needs about ${input.arrayAreaSqm.toFixed(1)} m² but the declared roof is ${input.roofAreaSqm} m².`
      );
    } else if (utilisation > 0.85) {
      warnings.push(
        "The array uses almost the whole declared roof, leaving little room for access or setback."
      );
    } else {
      reasons.push(
        `The array uses about ${Math.round(utilisation * 100)}% of the declared roof area.`
      );
    }
  }

  // ---- score: geometry only ----
  const exposureScore = Math.min(1, exposure / 0.85) * 60;
  const orientationScore = Math.max(0, 1 - azimuthError / 90) * 20;
  const tiltScore = Math.max(0, 1 - tiltError / 25) * 20;
  let score = exposureScore + orientationScore + tiltScore;
  if (input.shadedFraction != null) score *= 1 - Math.min(0.6, input.shadedFraction);

  const roundedScore = Math.round(Math.max(0, Math.min(100, score)));

  // ---- verdict ----
  let verdict: SuitabilityVerdict;
  if (input.daySamples.filter((s) => s.elevation > 0).length === 0) {
    verdict = "UNKNOWN";
    warnings.push("The sun does not rise above the horizon on the assessed day here.");
  } else if (roundedScore >= 70 && orientation !== "Poor") {
    verdict = "GOOD";
  } else if (roundedScore >= 45) {
    verdict = "PARTIAL";
  } else {
    verdict = "POOR";
  }

  return {
    verdict,
    score: roundedScore,
    sunExposure,
    orientation,
    tiltAssessment,
    shading,
    shadedFractionPct,
    reasons,
    warnings,
    suggestedTilt,
    suggestedAzimuth,
  };
}

/** Placement checks that are about geometry, not policy. */
export interface PlacementCheckInput {
  /** Panel base height above the surface beneath it, metres. Negative = below. */
  heightAboveSurfaceM: number | null;
  /** True when the placement sits on a building the data actually contains. */
  onBuilding: boolean;
  buildingDataAvailable: boolean;
  /** Distance from the array edge to the nearest roof edge, metres, if known. */
  edgeClearanceM: number | null;
  roofAreaSqm: number | null;
  arrayAreaSqm: number;
}

export interface PlacementCheck {
  level: "ok" | "warn" | "error";
  message: string;
}

export function checkPlacement(input: PlacementCheckInput): PlacementCheck[] {
  const checks: PlacementCheck[] = [];

  if (input.heightAboveSurfaceM != null && input.heightAboveSurfaceM < -0.5) {
    checks.push({
      level: "error",
      message: "The array is below the surface here — raise it onto the roof.",
    });
  }

  if (!input.buildingDataAvailable) {
    checks.push({
      level: "warn",
      message:
        "3D building data is unavailable for this location, so the array is placed on terrain. Roof height and edges cannot be checked.",
    });
  } else if (!input.onBuilding) {
    checks.push({
      level: "warn",
      message: "The array is not over a mapped building — check it is on your roof.",
    });
  }

  if (input.edgeClearanceM != null && input.edgeClearanceM < 0.5) {
    checks.push({
      level: "warn",
      message: `The array is about ${input.edgeClearanceM.toFixed(1)} m from the roof edge; most codes require a setback.`,
    });
  }

  if (input.roofAreaSqm != null && input.roofAreaSqm > 0 && input.arrayAreaSqm > input.roofAreaSqm) {
    checks.push({
      level: "warn",
      message: `The array needs ${input.arrayAreaSqm.toFixed(1)} m² but only ${input.roofAreaSqm} m² of roof was declared.`,
    });
  }

  if (checks.length === 0) {
    checks.push({ level: "ok", message: "Placement looks suitable." });
  }
  return checks;
}
