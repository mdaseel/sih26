/**
 * Rooftop solar constants shared by the form, the 3D planner and the tests.
 *
 * These mirror backend/app/models/schemas.py. The backend is the enforcing
 * side — a request outside these bounds is rejected there regardless of what
 * the browser does — but the form needs the same numbers to guide input rather
 * than let someone fill a whole page and be refused at the end.
 */

/**
 * What a house can actually carry.
 *
 * The engineering layers will simulate 200 kW at a bus quite happily, and for
 * a DISCOM studying a feeder that is a reasonable thing to ask. A household's
 * rooftop application is not that: a residential roof and a single-phase
 * service do not host it, so an assessment of one describes a system nobody
 * will build.
 */
export const MIN_NEW_PV_KW = 3;
export const MAX_NEW_PV_KW = 11;
export const MAX_EXISTING_PV_KW = 10;

/**
 * Default module rating used to turn a capacity into a panel count.
 *
 * Configurable because module ratings move with the market — a 2020 roof is
 * 330 W panels and a 2026 one is 550–650 W. Override with
 * NEXT_PUBLIC_PANEL_WATTS rather than editing this.
 */
export const DEFAULT_PANEL_WATTS = Number(
  process.env.NEXT_PUBLIC_PANEL_WATTS ?? 550
);

/** Physical size of one module, metres. A typical 550 W tier-1 module. */
export const DEFAULT_PANEL_WIDTH_M = Number(
  process.env.NEXT_PUBLIC_PANEL_WIDTH_M ?? 1.134
);
export const DEFAULT_PANEL_HEIGHT_M = Number(
  process.env.NEXT_PUBLIC_PANEL_LENGTH_M ?? 2.278
);

/** Gap between modules in a row, metres — mounting rail allowance. */
export const DEFAULT_PANEL_GAP_M = 0.02;

/** Default tilt presets offered in the planner. */
export const TILT_PRESETS = [10, 15, 20, 25, 30, 35, 40] as const;

export function capacityWithinResidentialRange(kw: number): boolean {
  return kw >= MIN_NEW_PV_KW && kw <= MAX_NEW_PV_KW;
}
