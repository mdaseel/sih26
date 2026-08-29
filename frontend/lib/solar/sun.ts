/**
 * Where the sun is, for a given instant and place on Earth.
 *
 * This is the NOAA Solar Calculator algorithm (Astronomical Almanac / Meeus),
 * computed locally. It is genuine astronomy — not a lookup, not an
 * approximation of a season, and not a placeholder. For dates within a few
 * centuries of now it is accurate to well under a tenth of a degree, which is
 * far finer than anything a rooftop layout decision turns on.
 *
 * What it is NOT: a measurement of sunlight. Solar position tells you where
 * the sun is in the sky. It says nothing about cloud, haze or aerosol, so it
 * cannot yield irradiance. Anything derived from it here is labelled an
 * estimate, and `clearSkyIrradianceEstimate` says "clear-sky" in its name for
 * exactly that reason. If a measured-irradiance source is ever configured, it
 * belongs behind its own service, not in this file.
 *
 * CesiumJS computes its own sun position from the same instant for scene
 * lighting and shadows. Both derive from the same JulianDate, so the numbers
 * shown here and the light in the scene agree to within arcminutes.
 */

const DEG = Math.PI / 180;
const RAD = 180 / Math.PI;

export interface SunPosition {
  /** Degrees above the horizon. Negative means below it — night. */
  elevation: number;
  /** Degrees clockwise from true north. 180 = due south. */
  azimuth: number;
  /** Degrees from vertical: 90 - elevation, before refraction. */
  zenith: number;
  /** True when the sun is above the horizon at this instant. */
  isDaylight: boolean;
}

/** Days since the J2000.0 epoch, as a Julian century. */
function julianCentury(date: Date): number {
  const julianDay = date.getTime() / 86_400_000 + 2_440_587.5;
  return (julianDay - 2_451_545) / 36_525;
}

/**
 * Apparent atmospheric refraction, in degrees.
 *
 * The atmosphere bends light, so the sun appears higher than it geometrically
 * is — by about half a degree at the horizon, which is roughly its own
 * diameter. It matters for sunrise and sunset times and for grazing-incidence
 * light on a roof; it is negligible overhead.
 */
function refraction(elevationDeg: number): number {
  if (elevationDeg > 85) return 0;
  const te = Math.tan(elevationDeg * DEG);
  let correction: number;
  if (elevationDeg > 5) {
    correction = 58.1 / te - 0.07 / te ** 3 + 0.000_086 / te ** 5;
  } else if (elevationDeg > -0.575) {
    correction =
      1735 +
      elevationDeg *
        (-518.2 + elevationDeg * (103.4 + elevationDeg * (-12.79 + elevationDeg * 0.711)));
  } else {
    correction = -20.774 / te;
  }
  return correction / 3600;
}

/**
 * Sun elevation and azimuth for an instant and a location.
 *
 * @param date  the instant, in absolute time (a JS Date is UTC internally, so
 *              the caller's timezone does not enter into it)
 * @param latitude  degrees north, -90..90
 * @param longitude degrees east, -180..180
 */
export function sunPosition(date: Date, latitude: number, longitude: number): SunPosition {
  // Refuse bad input rather than answering it.
  //
  // Every quantity below flows from the timestamp, and NaN propagates through
  // the trigonometry until the azimuth branch falls through to its
  // pole/zenith fallback — returning a clean-looking 180° for a date that does
  // not exist. A sun position nobody can check is worse than an error.
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) {
    throw new RangeError("sunPosition needs a valid Date");
  }
  if (!Number.isFinite(latitude) || latitude < -90 || latitude > 90) {
    throw new RangeError(`latitude out of range: ${latitude}`);
  }
  if (!Number.isFinite(longitude) || longitude < -180 || longitude > 180) {
    throw new RangeError(`longitude out of range: ${longitude}`);
  }

  const t = julianCentury(date);

  // Geometric mean longitude and anomaly of the sun.
  const meanLongitude = (280.46646 + t * (36_000.76983 + t * 0.000_3032)) % 360;
  const meanAnomaly = 357.52911 + t * (35_999.05029 - 0.000_1537 * t);

  // Equation of centre: the correction from a circular orbit to the real one.
  const centre =
    Math.sin(meanAnomaly * DEG) * (1.914602 - t * (0.004817 + 0.000_014 * t)) +
    Math.sin(2 * meanAnomaly * DEG) * (0.019993 - 0.000_101 * t) +
    Math.sin(3 * meanAnomaly * DEG) * 0.000_289;

  const trueLongitude = meanLongitude + centre;

  // Apparent longitude accounts for nutation and aberration.
  const omega = 125.04 - 1934.136 * t;
  const apparentLongitude = trueLongitude - 0.00569 - 0.00478 * Math.sin(omega * DEG);

  // Obliquity of the ecliptic — the tilt that gives us seasons.
  const meanObliquity =
    23 + (26 + (21.448 - t * (46.815 + t * (0.00059 - t * 0.001_813))) / 60) / 60;
  const obliquity = meanObliquity + 0.00256 * Math.cos(omega * DEG);

  const declination =
    Math.asin(Math.sin(obliquity * DEG) * Math.sin(apparentLongitude * DEG)) * RAD;

  // Equation of time, in minutes: the difference between apparent solar time
  // and mean clock time, caused by orbital eccentricity and axial tilt.
  const y = Math.tan((obliquity / 2) * DEG) ** 2;
  const eccentricity = 0.016708634 - t * (0.000_042_037 + 0.000_000_1267 * t);
  const equationOfTime =
    4 *
    RAD *
    (y * Math.sin(2 * meanLongitude * DEG) -
      2 * eccentricity * Math.sin(meanAnomaly * DEG) +
      4 * eccentricity * y * Math.sin(meanAnomaly * DEG) * Math.cos(2 * meanLongitude * DEG) -
      0.5 * y * y * Math.sin(4 * meanLongitude * DEG) -
      1.25 * eccentricity * eccentricity * Math.sin(2 * meanAnomaly * DEG));

  // True solar time at this longitude, in minutes past local solar midnight.
  const minutesUtc =
    date.getUTCHours() * 60 + date.getUTCMinutes() + date.getUTCSeconds() / 60;
  const trueSolarTime = (minutesUtc + equationOfTime + 4 * longitude + 1440) % 1440;

  // Hour angle: degrees the Earth has turned from local solar noon.
  let hourAngle = trueSolarTime / 4 - 180;
  if (hourAngle < -180) hourAngle += 360;

  const latRad = latitude * DEG;
  const decRad = declination * DEG;

  const cosZenith =
    Math.sin(latRad) * Math.sin(decRad) +
    Math.cos(latRad) * Math.cos(decRad) * Math.cos(hourAngle * DEG);
  const zenith = Math.acos(Math.min(1, Math.max(-1, cosZenith))) * RAD;

  const geometricElevation = 90 - zenith;
  const elevation = geometricElevation + refraction(geometricElevation);

  // Azimuth, measured clockwise from true north.
  let azimuth: number;
  const denominator = Math.cos(latRad) * Math.sin(zenith * DEG);
  if (Math.abs(denominator) > 1e-9) {
    const cosAzimuth =
      (Math.sin(latRad) * Math.cos(zenith * DEG) - Math.sin(decRad)) / denominator;
    azimuth = Math.acos(Math.min(1, Math.max(-1, cosAzimuth))) * RAD;
    azimuth = hourAngle > 0 ? (azimuth + 180) % 360 : (540 - azimuth) % 360;
  } else {
    // Sun directly overhead or at a pole: azimuth is undefined, not zero.
    azimuth = latitude > 0 ? 180 : 0;
  }

  return {
    elevation: round(elevation, 3),
    azimuth: round(azimuth, 3),
    zenith: round(zenith, 3),
    isDaylight: elevation > 0,
  };
}

/**
 * The compass direction a fixed panel should face to catch the most sun over a
 * year: towards the equator.
 */
export function optimalAzimuth(latitude: number): number {
  return latitude >= 0 ? 180 : 0;
}

/**
 * The instant on `date`'s local day when the sun is highest at this location.
 *
 * Found by sweeping the day rather than solving the equation of time, because
 * the sweep reuses the same sunPosition() the rest of the app displays — one
 * definition of where the sun is, so the planner's default cannot disagree
 * with its own readout. Two passes: coarse to find the hour, fine to land on
 * the minute.
 *
 * This exists because the planner has to open on *something*, and opening on
 * the wall clock means a citizen planning their roof after dinner is shown an
 * unlit globe. Solar noon is the honest choice of default: it is a real
 * instant, it is labelled as the selected time, and "use current time" is one
 * click away.
 *
 * Above the arctic circles in winter there is no daylight to find. The sweep
 * still returns the day's maximum — the least-dark moment — and the caller can
 * see from the elevation that the sun never rose.
 */
export function solarNoon(date: Date, latitude: number, longitude: number): Date {
  const startOfDay = new Date(date);
  startOfDay.setHours(0, 0, 0, 0);

  const at = (minutes: number) => {
    const d = new Date(startOfDay);
    d.setMinutes(minutes);
    return d;
  };

  let best = 0;
  let bestElevation = -Infinity;

  for (let m = 0; m < 24 * 60; m += 20) {
    const elevation = sunPosition(at(m), latitude, longitude).elevation;
    if (elevation > bestElevation) {
      bestElevation = elevation;
      best = m;
    }
  }

  for (let m = Math.max(0, best - 20); m <= Math.min(24 * 60 - 1, best + 20); m += 1) {
    const elevation = sunPosition(at(m), latitude, longitude).elevation;
    if (elevation > bestElevation) {
      bestElevation = elevation;
      best = m;
    }
  }

  return at(best);
}

/**
 * A first-order annual-optimum tilt for a fixed array.
 *
 * The rule of thumb is latitude-proportional, flattened at low latitudes where
 * a steeper panel gains little and collects more dust. It is an estimate, not
 * an optimisation: a real answer depends on the local irradiance record, the
 * seasonal load shape, and whether winter or summer output matters more. The
 * UI must present it as a starting point.
 */
export function estimatedOptimalTilt(latitude: number): number {
  const absolute = Math.abs(latitude);
  const tilt = absolute < 25 ? absolute * 0.87 : absolute * 0.76 + 3.1;
  return Math.round(Math.min(40, Math.max(5, tilt)));
}

/**
 * Cosine of the angle between the sun and the panel's normal.
 *
 * 1.0 is the sun square-on to the glass; 0 is edge-on; negative means the sun
 * is behind the panel. This is the geometric driver of how much of the
 * available beam a panel intercepts, and it is exact — no weather in it.
 */
export function incidenceCosine(
  sun: Pick<SunPosition, "elevation" | "azimuth">,
  tiltDeg: number,
  azimuthDeg: number
): number {
  if (sun.elevation <= 0) return 0;
  const sunEl = sun.elevation * DEG;
  const sunAz = sun.azimuth * DEG;
  const tilt = tiltDeg * DEG;
  const panelAz = azimuthDeg * DEG;

  const cosine =
    Math.sin(sunEl) * Math.cos(tilt) +
    Math.cos(sunEl) * Math.sin(tilt) * Math.cos(sunAz - panelAz);
  return Math.max(0, cosine);
}

/**
 * Clear-sky irradiance on the panel, W/m². An ESTIMATE, and named so.
 *
 * Uses the Haurwitz/Meinel-style air-mass attenuation of the solar constant.
 * It assumes a cloudless, clean atmosphere, so it is an upper bound on a good
 * day and says nothing about today. Never present this as measured.
 */
export function clearSkyIrradianceEstimate(
  sun: Pick<SunPosition, "elevation" | "azimuth">,
  tiltDeg: number,
  azimuthDeg: number
): number {
  if (sun.elevation <= 0) return 0;
  const airMass = 1 / Math.sin(Math.max(sun.elevation, 3) * DEG);
  const directNormal = 1353 * 0.7 ** airMass ** 0.678;
  const beam = directNormal * incidenceCosine(sun, tiltDeg, azimuthDeg);
  // A crude isotropic diffuse term; real diffuse depends on the sky state.
  const diffuse = 0.1 * directNormal * ((1 + Math.cos(tiltDeg * DEG)) / 2);
  return Math.round(beam + diffuse);
}

function round(value: number, places: number): number {
  const factor = 10 ** places;
  return Math.round(value * factor) / factor;
}

/** Compass label for an azimuth, for readouts. */
export function compassLabel(azimuth: number): string {
  const points = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
  return points[Math.round((((azimuth % 360) + 360) % 360) / 22.5) % 16];
}
