import { describe, expect, it } from "vitest";

import {
  DEFAULT_PANEL_SPEC,
  fitsRoofArea,
  formatArea,
  formatLength,
  layoutFor,
  metresToFeet,
  modulePositions,
  panelsForCapacity,
  type PanelSpec,
} from "./array";
import { assessSuitability, bearingDifference, checkPlacement } from "./suitability";
import { sunPosition } from "./sun";

const SPEC: PanelSpec = { watts: 550, widthM: 1.134, lengthM: 2.278, gapM: 0.02 };

describe("panelsForCapacity", () => {
  it("rounds up so the array is not short of what was asked for", () => {
    // 5 kW / 550 W = 9.09 modules. Nine would be 4.95 kW — under the request.
    expect(panelsForCapacity(5, SPEC)).toBe(10);
  });

  it("gives an exact count when the capacity divides evenly", () => {
    expect(panelsForCapacity(5.5, SPEC)).toBe(10);
    expect(panelsForCapacity(11, SPEC)).toBe(20);
  });

  it("scales with the module rating rather than assuming one", () => {
    const bigger: PanelSpec = { ...SPEC, watts: 700 };
    expect(panelsForCapacity(5, bigger)).toBe(8);
    expect(panelsForCapacity(5, bigger)).toBeLessThan(panelsForCapacity(5, SPEC));
  });

  it("returns nothing for a capacity that is not a capacity", () => {
    expect(panelsForCapacity(0, SPEC)).toBe(0);
    expect(panelsForCapacity(-3, SPEC)).toBe(0);
    expect(panelsForCapacity(Number.NaN, SPEC)).toBe(0);
  });
});

describe("layoutFor", () => {
  it("reports what was asked for and what the hardware delivers, separately", () => {
    const layout = layoutFor(5, SPEC);

    expect(layout.requestedCapacityKw).toBe(5);
    expect(layout.panelCount).toBe(10);
    // Ten 550 W modules is 5.5 kW, not 5. Saying "5 kW" here would be a lie.
    expect(layout.actualCapacityKw).toBe(5.5);
  });

  it("lays the array out roughly square", () => {
    const layout = layoutFor(5, SPEC);
    expect(layout.columns).toBe(4);
    expect(layout.rows).toBe(3);
    expect(layout.columns * layout.rows).toBeGreaterThanOrEqual(layout.panelCount);
  });

  it("shortens the footprint as the array is tilted, without losing glass", () => {
    const flat = layoutFor(5, SPEC, 0);
    const steep = layoutFor(5, SPEC, 40);

    expect(steep.footprintLengthM).toBeLessThan(flat.footprintLengthM);
    expect(steep.moduleAreaSqm).toBe(flat.moduleAreaSqm);
  });

  it("gives an empty layout for no capacity rather than a degenerate one", () => {
    const layout = layoutFor(0, SPEC);
    expect(layout.panelCount).toBe(0);
    expect(layout.footprintWidthM).toBe(0);
    expect(layout.occupiedAreaSqm).toBe(0);
  });

  it("uses the configured default spec when none is passed", () => {
    expect(layoutFor(5).spec).toEqual(DEFAULT_PANEL_SPEC);
  });
});

describe("modulePositions", () => {
  it("produces exactly one position per module", () => {
    const layout = layoutFor(5, SPEC);
    expect(modulePositions(layout).length).toBe(layout.panelCount);
  });

  it("centres the array on the placement point", () => {
    const positions = modulePositions(layoutFor(5, SPEC));
    const meanAcross =
      positions.reduce((s, p) => s + p.acrossM, 0) / positions.length;

    // The last row may be partial, so across is centred but along need not be.
    expect(Math.abs(meanAcross)).toBeLessThan(0.6);
  });

  it("spaces modules by their width plus the gap", () => {
    const positions = modulePositions(layoutFor(5, SPEC));
    const row = positions.filter((p) => p.alongM === positions[0].alongM);
    const spacing = Math.abs(row[1].acrossM - row[0].acrossM);

    expect(spacing).toBeCloseTo(SPEC.widthM + SPEC.gapM, 5);
  });

  it("returns nothing for an empty array", () => {
    expect(modulePositions(layoutFor(0, SPEC))).toEqual([]);
  });
});

describe("fitsRoofArea", () => {
  it("says nothing when no roof area was declared", () => {
    const { fits, utilisationPct } = fitsRoofArea(layoutFor(5, SPEC), null);
    expect(fits).toBe(true);
    expect(utilisationPct).toBeNull();
  });

  it("detects an array too big for the declared roof", () => {
    expect(fitsRoofArea(layoutFor(11, SPEC), 10).fits).toBe(false);
  });

  it("reports utilisation against a roof that does fit", () => {
    const result = fitsRoofArea(layoutFor(5, SPEC), 100);
    expect(result.fits).toBe(true);
    expect(result.utilisationPct).toBeGreaterThan(0);
    expect(result.utilisationPct).toBeLessThan(100);
  });
});

describe("units", () => {
  it("converts metres to feet", () => {
    expect(metresToFeet(1)).toBeCloseTo(3.2808, 3);
  });

  it("formats lengths in the requested unit", () => {
    expect(formatLength(2, "m")).toBe("2.00 m");
    expect(formatLength(2, "ft")).toBe("6.56 ft");
  });

  it("converts area by the square of the length factor", () => {
    expect(formatArea(10, "m")).toBe("10.0 m²");
    expect(formatArea(10, "ft")).toBe("107.6 ft²");
  });
});

// ---------------------------------------------------------------
//  Suitability
// ---------------------------------------------------------------

/** Sun positions across a real day, so the assessment runs on real geometry. */
function dayFor(dateIso: string, lat: number, lon: number) {
  return Array.from({ length: 24 }, (_, h) =>
    sunPosition(new Date(`${dateIso}T${String(h).padStart(2, "0")}:00:00Z`), lat, lon)
  );
}

const BENGALURU = { lat: 12.9716, lon: 77.5946 };
const day = dayFor("2026-03-20", BENGALURU.lat, BENGALURU.lon);

const base = {
  latitude: BENGALURU.lat,
  tiltDeg: 12,
  azimuthDeg: 180,
  daySamples: day,
  buildingDataAvailable: true,
  shadedFraction: 0,
  roofAreaSqm: 100,
  arrayAreaSqm: 25,
};

describe("bearingDifference", () => {
  it("takes the short way round the compass", () => {
    expect(bearingDifference(350, 10)).toBe(20);
    expect(bearingDifference(10, 350)).toBe(20);
    expect(bearingDifference(0, 180)).toBe(180);
  });
});

describe("assessSuitability", () => {
  it("rates a well-aimed unshaded array as good", () => {
    const result = assessSuitability(base);

    expect(result.verdict).toBe("GOOD");
    expect(result.orientation).toBe("Suitable");
    expect(result.score).toBeGreaterThan(70);
  });

  it("marks a north-facing array in the northern hemisphere as poorly oriented", () => {
    const result = assessSuitability({ ...base, azimuthDeg: 0 });

    expect(result.orientation).toBe("Poor");
    expect(result.verdict).not.toBe("GOOD");
    expect(result.warnings.join(" ")).toMatch(/optimum bearing/);
  });

  it("never claims shading was checked when no building data exists", () => {
    // This is the important one: absence of data is not absence of shade.
    const result = assessSuitability({
      ...base,
      buildingDataAvailable: false,
      shadedFraction: null,
    });

    expect(result.shading).toBe("UNASSESSED");
    expect(result.shadedFractionPct).toBeNull();
    expect(result.warnings.join(" ")).toMatch(/No 3D building data/);
  });

  it("only ever calls a shading result partial, never definitive", () => {
    const result = assessSuitability({ ...base, shadedFraction: 0.1 });
    expect(result.shading).toBe("PARTIAL");
  });

  it("downgrades a heavily shaded array and says why", () => {
    const clear = assessSuitability(base);
    const shaded = assessSuitability({ ...base, shadedFraction: 0.5 });

    expect(shaded.score).toBeLessThan(clear.score);
    expect(shaded.warnings.join(" ")).toMatch(/shadow/);
  });

  it("warns when the array will not fit the declared roof", () => {
    const result = assessSuitability({ ...base, arrayAreaSqm: 140, roofAreaSqm: 100 });
    expect(result.warnings.join(" ")).toMatch(/roof is 100/);
  });

  it("offers the optimum tilt as a suggestion, not a rule", () => {
    const result = assessSuitability(base);

    expect(result.suggestedTilt).toBeGreaterThan(0);
    expect(result.suggestedAzimuth).toBe(180);
  });

  it("returns UNKNOWN rather than guessing when the sun never rises", () => {
    const polarNight = dayFor("2026-12-21", 78, 15);
    const result = assessSuitability({ ...base, latitude: 78, daySamples: polarNight });

    expect(result.verdict).toBe("UNKNOWN");
  });
});

describe("checkPlacement", () => {
  const ok = {
    heightAboveSurfaceM: 0.3,
    onBuilding: true,
    buildingDataAvailable: true,
    edgeClearanceM: 2,
    roofAreaSqm: 100,
    arrayAreaSqm: 25,
  };

  it("passes a sensible placement", () => {
    const checks = checkPlacement(ok);
    expect(checks).toHaveLength(1);
    expect(checks[0].level).toBe("ok");
  });

  it("errors when the array is underground", () => {
    const checks = checkPlacement({ ...ok, heightAboveSurfaceM: -3 });
    expect(checks.some((c) => c.level === "error")).toBe(true);
  });

  it("warns, but does not block, when building data is missing", () => {
    const checks = checkPlacement({ ...ok, buildingDataAvailable: false, onBuilding: false });

    expect(checks.some((c) => c.level === "warn")).toBe(true);
    expect(checks.some((c) => c.level === "error")).toBe(false);
  });

  it("warns near a roof edge", () => {
    const checks = checkPlacement({ ...ok, edgeClearanceM: 0.2 });
    expect(checks.some((c) => /roof edge/.test(c.message))).toBe(true);
  });

  it("warns when the array exceeds the declared roof", () => {
    const checks = checkPlacement({ ...ok, arrayAreaSqm: 150 });
    expect(checks.some((c) => /only 100/.test(c.message))).toBe(true);
  });
});
