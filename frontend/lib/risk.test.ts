import { describe, expect, it } from "vitest";

import {
  lineRisk,
  strokeFor,
  transformerRisk,
  voltageRiseRisk,
  voltageRisk,
  worstRisk,
} from "./risk";

/** The thresholds the API sends, from scenario_config.json. */
const T = {
  voltage_hard_low_pu: 0.9,
  voltage_hard_high_pu: 1.05,
  voltage_caution_low_pu: 0.9,
  voltage_caution_high_pu: 1.03,
  voltage_rise_hard_pu: 0.05,
  voltage_rise_caution_pu: 0.03,
  line_loading_hard_pct: 100,
  line_loading_caution_pct: 80,
  transformer_loading_hard_pct: 100,
  transformer_loading_caution_pct: 95,
};

describe("voltageRisk", () => {
  it("treats a normal voltage as safe", () => {
    expect(voltageRisk(1.0, T)).toBe("SAFE");
    expect(voltageRisk(0.95, T)).toBe("SAFE");
  });

  it("flags the caution band above and below", () => {
    expect(voltageRisk(1.04, T)).toBe("CAUTION");
  });

  it("flags a hard breach in either direction", () => {
    expect(voltageRisk(1.06, T)).toBe("CONSTRAINED");
    expect(voltageRisk(0.89, T)).toBe("CONSTRAINED");
  });

  it("is exclusive at the hard limit, matching the backend rule", () => {
    // The backend uses `>` for hard limits, so exactly 1.05 is not a breach.
    expect(voltageRisk(1.05, T)).toBe("CAUTION");
    expect(voltageRisk(1.050001, T)).toBe("CONSTRAINED");
  });

  it("returns null rather than guessing when there is no value", () => {
    expect(voltageRisk(null, T)).toBeNull();
    expect(voltageRisk(undefined, T)).toBeNull();
    expect(voltageRisk(NaN, T)).toBeNull();
  });
});

describe("voltageRiseRisk", () => {
  it("reproduces the bus 734 case", () => {
    // 0.05751 pu against a 0.05 hard limit — the documented CONSTRAINED case.
    expect(voltageRiseRisk(0.05751, T)).toBe("CONSTRAINED");
  });

  it("reproduces the bus 6231 case", () => {
    expect(voltageRiseRisk(0.0519, T)).toBe("CONSTRAINED");
  });

  it("keeps the backend's asymmetric comparisons", () => {
    // hard is `>`, caution is `>=`
    expect(voltageRiseRisk(0.05, T)).toBe("CAUTION");
    expect(voltageRiseRisk(0.03, T)).toBe("CAUTION");
    expect(voltageRiseRisk(0.0299, T)).toBe("SAFE");
  });

  it("judges a fall in voltage by its magnitude", () => {
    expect(voltageRiseRisk(-0.06, T)).toBe("CONSTRAINED");
  });
});

describe("loading", () => {
  it("uses the feeder-specific transformer caution band of 95%", () => {
    // 92.8% is the validated base loading of T7 and must not read as caution.
    expect(transformerRisk(92.8, T)).toBe("SAFE");
    expect(transformerRisk(95, T)).toBe("CAUTION");
    expect(transformerRisk(100, T)).toBe("CAUTION");
    expect(transformerRisk(100.6, T)).toBe("CONSTRAINED");
  });

  it("uses the 80% line caution band", () => {
    expect(lineRisk(8.77, T)).toBe("SAFE");
    expect(lineRisk(80, T)).toBe("CAUTION");
    expect(lineRisk(101, T)).toBe("CONSTRAINED");
  });
});

describe("worstRisk", () => {
  it("returns the most severe judgement", () => {
    expect(worstRisk("SAFE", "CAUTION", "CONSTRAINED")).toBe("CONSTRAINED");
    expect(worstRisk("SAFE", "CAUTION")).toBe("CAUTION");
    expect(worstRisk("SAFE", "SAFE")).toBe("SAFE");
  });

  it("ignores missing values instead of treating them as safe", () => {
    expect(worstRisk(null, "CAUTION")).toBe("CAUTION");
    expect(worstRisk(null, null)).toBeNull();
  });
});

describe("fallbacks", () => {
  it("falls back to the documented limit when a threshold is missing", () => {
    // A missing key must not compare false and silently paint everything green.
    expect(voltageRiseRisk(0.06, {})).toBe("CONSTRAINED");
    expect(transformerRisk(101, {})).toBe("CONSTRAINED");
  });

  it("ignores a non-numeric threshold", () => {
    expect(voltageRiseRisk(0.06, { voltage_rise_hard_pu: NaN })).toBe("CONSTRAINED");
  });
});

describe("colours", () => {
  it("gives an unknown risk a neutral colour, not green", () => {
    expect(strokeFor(null)).not.toBe(strokeFor("SAFE"));
  });
});
