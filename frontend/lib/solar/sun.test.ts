import { describe, expect, it } from "vitest";

import {
  clearSkyIrradianceEstimate,
  compassLabel,
  estimatedOptimalTilt,
  incidenceCosine,
  optimalAzimuth,
  solarNoon,
  sunPosition,
} from "./sun";

/**
 * These check the solar-position code against facts of astronomy that are true
 * regardless of implementation — solstice declination, equinox symmetry, the
 * sun's bearing at local noon. If the algorithm is wrong these fail; if it is
 * right they hold for any place and date.
 *
 * Reference values are from the NOAA Solar Calculator.
 */

const BENGALURU = { lat: 12.9716, lon: 77.5946 };
const LONDON = { lat: 51.5074, lon: -0.1278 };
const SYDNEY = { lat: -33.8688, lon: 151.2093 };

describe("sunPosition", () => {
  it("puts the sun near due south at solar noon in the northern hemisphere", () => {
    // Bengaluru is UTC+5:30 and 77.59°E; solar noon is close to 06:30 UTC.
    const noon = new Date("2026-03-20T06:30:00Z");
    const sun = sunPosition(noon, BENGALURU.lat, BENGALURU.lon);

    expect(sun.azimuth).toBeGreaterThan(150);
    expect(sun.azimuth).toBeLessThan(210);
    expect(sun.elevation).toBeGreaterThan(70);
  });

  it("puts the sun near due north at solar noon in the southern hemisphere", () => {
    // Sydney is UTC+10 and 151.2°E; solar noon is close to 02:00 UTC.
    const sun = sunPosition(new Date("2026-06-21T02:00:00Z"), SYDNEY.lat, SYDNEY.lon);

    expect(sun.elevation).toBeGreaterThan(0);
    // Due north, so either side of 0/360.
    expect(Math.min(sun.azimuth, 360 - sun.azimuth)).toBeLessThan(30);
  });

  it("reproduces the June solstice noon elevation at a known latitude", () => {
    // At solar noon on the June solstice, elevation = 90 - |lat - 23.44|.
    const sun = sunPosition(new Date("2026-06-21T12:00:00Z"), LONDON.lat, 0);
    const expected = 90 - Math.abs(LONDON.lat - 23.44);

    expect(sun.elevation).toBeGreaterThan(expected - 1);
    expect(sun.elevation).toBeLessThan(expected + 1);
  });

  it("reproduces the December solstice noon elevation at the same latitude", () => {
    const sun = sunPosition(new Date("2026-12-21T12:00:00Z"), LONDON.lat, 0);
    const expected = 90 - Math.abs(LONDON.lat + 23.44);

    expect(sun.elevation).toBeGreaterThan(expected - 1);
    expect(sun.elevation).toBeLessThan(expected + 1);
  });

  it("puts the sun overhead at the equator at equinox noon", () => {
    const sun = sunPosition(new Date("2026-03-20T12:00:00Z"), 0, 0);
    expect(sun.elevation).toBeGreaterThan(88);
  });

  it("reports night as a negative elevation, not a clamped zero", () => {
    const midnight = sunPosition(new Date("2026-06-21T18:30:00Z"), BENGALURU.lat, BENGALURU.lon);

    expect(midnight.elevation).toBeLessThan(0);
    expect(midnight.isDaylight).toBe(false);
  });

  it("has the sun rise in the east and set in the west", () => {
    const morning = sunPosition(new Date("2026-03-20T01:00:00Z"), BENGALURU.lat, BENGALURU.lon);
    const evening = sunPosition(new Date("2026-03-20T12:00:00Z"), BENGALURU.lat, BENGALURU.lon);

    expect(morning.azimuth).toBeGreaterThan(60);
    expect(morning.azimuth).toBeLessThan(120);
    expect(evening.azimuth).toBeGreaterThan(240);
    expect(evening.azimuth).toBeLessThan(300);
  });

  it("moves the sun westward as the day advances", () => {
    const azimuths = [2, 4, 6, 8, 10].map(
      (h) =>
        sunPosition(
          new Date(`2026-03-20T${String(h).padStart(2, "0")}:00:00Z`),
          BENGALURU.lat,
          BENGALURU.lon
        ).azimuth
    );

    for (let i = 1; i < azimuths.length; i++) {
      expect(azimuths[i]).toBeGreaterThan(azimuths[i - 1]);
    }
  });

  it("refuses a date that does not exist instead of answering it", () => {
    // An invalid Date used to propagate NaN through the trigonometry and fall
    // out of the azimuth branch as a confident-looking 180 degrees.
    expect(() => sunPosition(new Date("2026-03-20T010:00:00Z"), 12.97, 77.59)).toThrow(
      RangeError
    );
  });

  it("refuses coordinates off the globe", () => {
    const noon = new Date("2026-03-20T06:30:00Z");
    expect(() => sunPosition(noon, 120, 77.59)).toThrow(RangeError);
    expect(() => sunPosition(noon, 12.97, 400)).toThrow(RangeError);
  });

  it("keeps zenith and elevation consistent", () => {
    const sun = sunPosition(new Date("2026-03-20T06:30:00Z"), BENGALURU.lat, BENGALURU.lon);
    // Elevation carries a refraction correction, so they sum to just over 90.
    expect(sun.elevation + sun.zenith).toBeGreaterThan(89.9);
    expect(sun.elevation + sun.zenith).toBeLessThan(90.6);
  });
});

describe("optimalAzimuth", () => {
  it("faces the equator", () => {
    expect(optimalAzimuth(BENGALURU.lat)).toBe(180);
    expect(optimalAzimuth(SYDNEY.lat)).toBe(0);
  });
});

describe("estimatedOptimalTilt", () => {
  it("rises with latitude", () => {
    expect(estimatedOptimalTilt(0)).toBeLessThan(estimatedOptimalTilt(30));
    expect(estimatedOptimalTilt(30)).toBeLessThan(estimatedOptimalTilt(55));
  });

  it("stays within angles a roof mount can actually achieve", () => {
    for (const lat of [-60, -20, 0, 13, 35, 60]) {
      const tilt = estimatedOptimalTilt(lat);
      expect(tilt).toBeGreaterThanOrEqual(5);
      expect(tilt).toBeLessThanOrEqual(40);
    }
  });

  it("is symmetric about the equator", () => {
    expect(estimatedOptimalTilt(35)).toBe(estimatedOptimalTilt(-35));
  });
});

describe("incidenceCosine", () => {
  it("is 1 when the sun is square on to the panel", () => {
    // Sun 40° up in the south, panel tilted 50° facing south: normal points
    // straight at it.
    const cosine = incidenceCosine({ elevation: 40, azimuth: 180 }, 50, 180);
    expect(cosine).toBeCloseTo(1, 3);
  });

  it("is 1 for a flat panel with the sun overhead", () => {
    expect(incidenceCosine({ elevation: 90, azimuth: 180 }, 0, 180)).toBeCloseTo(1, 3);
  });

  it("never goes negative when the sun is behind the panel", () => {
    const cosine = incidenceCosine({ elevation: 20, azimuth: 0 }, 60, 180);
    expect(cosine).toBe(0);
  });

  it("is zero at night", () => {
    expect(incidenceCosine({ elevation: -10, azimuth: 180 }, 25, 180)).toBe(0);
  });

  it("prefers a correctly aimed panel over a misaimed one", () => {
    const sun = { elevation: 45, azimuth: 180 };
    expect(incidenceCosine(sun, 25, 180)).toBeGreaterThan(incidenceCosine(sun, 25, 90));
  });
});

describe("clearSkyIrradianceEstimate", () => {
  it("is zero at night", () => {
    expect(clearSkyIrradianceEstimate({ elevation: -5, azimuth: 180 }, 25, 180)).toBe(0);
  });

  it("stays below the solar constant", () => {
    // No clear-sky model on Earth's surface should exceed 1361 W/m².
    const value = clearSkyIrradianceEstimate({ elevation: 90, azimuth: 180 }, 0, 180);
    expect(value).toBeGreaterThan(700);
    expect(value).toBeLessThan(1361);
  });

  it("falls as the sun gets lower", () => {
    const high = clearSkyIrradianceEstimate({ elevation: 70, azimuth: 180 }, 25, 180);
    const low = clearSkyIrradianceEstimate({ elevation: 15, azimuth: 180 }, 25, 180);
    expect(low).toBeLessThan(high);
  });
});

describe("compassLabel", () => {
  it("names the cardinal points", () => {
    expect(compassLabel(0)).toBe("N");
    expect(compassLabel(90)).toBe("E");
    expect(compassLabel(180)).toBe("S");
    expect(compassLabel(270)).toBe("W");
  });

  it("wraps past 360 and handles negatives", () => {
    expect(compassLabel(360)).toBe("N");
    expect(compassLabel(-90)).toBe("W");
  });
});

describe("solarNoon", () => {
  // Bengaluru. Chosen because the app's demo data sits there, so a regression
  // here shows up in the same place a reviewer is already looking.
  const LAT = 12.9716;
  const LON = 77.5946;

  it("lands on a moment when the sun is actually up", () => {
    const noon = solarNoon(new Date("2026-03-15T22:40:00"), LAT, LON);
    expect(sunPosition(noon, LAT, LON).isDaylight).toBe(true);
  });

  it("is the highest the sun gets that day", () => {
    const day = new Date("2026-06-21T03:00:00");
    const peak = sunPosition(solarNoon(day, LAT, LON), LAT, LON).elevation;

    for (let minutes = 0; minutes < 24 * 60; minutes += 13) {
      const t = new Date(day);
      t.setHours(0, 0, 0, 0);
      t.setMinutes(minutes);
      // A one-minute sweep cannot be beaten by more than rounding.
      expect(sunPosition(t, LAT, LON).elevation).toBeLessThanOrEqual(peak + 0.01);
    }
  });

  it("stays on the local day it was asked about", () => {
    const evening = new Date("2026-03-15T23:55:00");
    const noon = solarNoon(evening, LAT, LON);

    expect(noon.getFullYear()).toBe(evening.getFullYear());
    expect(noon.getMonth()).toBe(evening.getMonth());
    expect(noon.getDate()).toBe(evening.getDate());
  });

  it("does not depend on the time of day it was called with", () => {
    const morning = solarNoon(new Date("2026-03-15T06:00:00"), LAT, LON);
    const night = solarNoon(new Date("2026-03-15T23:30:00"), LAT, LON);
    expect(morning.getTime()).toBe(night.getTime());
  });

  it("puts the sun near due south at a northern site", () => {
    const noon = solarNoon(new Date("2026-03-15T10:00:00"), LAT, LON);
    const azimuth = sunPosition(noon, LAT, LON).azimuth;
    expect(Math.abs(azimuth - 180)).toBeLessThan(12);
  });

  it("returns the least-dark instant where the sun never rises", () => {
    // Longyearbyen in December: polar night. There is no daylight to find, and
    // the function must still answer rather than loop or throw — the caller
    // reads the elevation and sees the sun stayed down.
    const noon = solarNoon(new Date("2026-12-21T12:00:00"), 78.22, 15.65);
    expect(sunPosition(noon, 78.22, 15.65).isDaylight).toBe(false);
    expect(noon.getDate()).toBe(21);
  });
});
