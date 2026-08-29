/**
 * Turning a requested capacity into an actual array of modules.
 *
 * Everything the 3D scene draws comes from here, so the picture and the
 * numbers underneath it cannot drift apart: the panel count in the readout is
 * the number of rectangles on the roof, and the footprint quoted is the
 * footprint drawn.
 *
 * Nothing here is electrical in the grid sense. Capacity, count and area are
 * geometry and a module rating; voltage, loading and risk come from the
 * backend power flow and are never derived in this file.
 */

import {
  DEFAULT_PANEL_GAP_M,
  DEFAULT_PANEL_HEIGHT_M,
  DEFAULT_PANEL_WATTS,
  DEFAULT_PANEL_WIDTH_M,
} from "@/lib/solar/config";

export interface PanelSpec {
  /** Module rating, watts. */
  watts: number;
  /** Module width across the array row, metres. */
  widthM: number;
  /** Module length up the slope, metres. */
  lengthM: number;
  /** Gap between modules, metres. */
  gapM: number;
}

export const DEFAULT_PANEL_SPEC: PanelSpec = {
  watts: DEFAULT_PANEL_WATTS,
  widthM: DEFAULT_PANEL_WIDTH_M,
  lengthM: DEFAULT_PANEL_HEIGHT_M,
  gapM: DEFAULT_PANEL_GAP_M,
};

export interface ArrayLayout {
  /** Modules needed to reach at least the requested capacity. */
  panelCount: number;
  /** What those modules actually add up to — the honest number. */
  actualCapacityKw: number;
  /** What was asked for. */
  requestedCapacityKw: number;
  columns: number;
  rows: number;
  /** Footprint of the whole array laid flat, metres. */
  footprintWidthM: number;
  footprintLengthM: number;
  /** Glass area, m². Not the same as footprint once tilted. */
  moduleAreaSqm: number;
  /** Ground/roof area the tilted array occupies, m². */
  occupiedAreaSqm: number;
  spec: PanelSpec;
}

/**
 * Modules for a capacity, rounded UP.
 *
 * Rounding up matters: 5 kW at 550 W is 9.09 modules, and nine modules is
 * 4.95 kW — short of what the citizen asked for. Ten gives 5.5 kW, so the
 * layout reports both the request and what the hardware actually delivers
 * rather than quietly pretending they are the same.
 */
export function panelsForCapacity(capacityKw: number, spec: PanelSpec): number {
  if (!Number.isFinite(capacityKw) || capacityKw <= 0) return 0;
  return Math.ceil((capacityKw * 1000) / spec.watts);
}

/**
 * Lay `count` modules out in as square a block as fits, portrait, in rows up
 * the slope. A roughly square array is what installers actually build: it
 * keeps cable runs short and fits a typical roof plane better than one long
 * strip.
 */
export function layoutFor(
  requestedCapacityKw: number,
  spec: PanelSpec = DEFAULT_PANEL_SPEC,
  tiltDeg = 0
): ArrayLayout {
  const panelCount = panelsForCapacity(requestedCapacityKw, spec);
  const columns = panelCount > 0 ? Math.ceil(Math.sqrt(panelCount)) : 0;
  const rows = columns > 0 ? Math.ceil(panelCount / columns) : 0;

  const footprintWidthM =
    columns > 0 ? columns * spec.widthM + (columns - 1) * spec.gapM : 0;
  const slopeLengthM = rows > 0 ? rows * spec.lengthM + (rows - 1) * spec.gapM : 0;

  // Tilting a panel shortens the ground it covers by cos(tilt); the array is
  // no shorter, it just lies over less roof.
  const footprintLengthM = slopeLengthM * Math.cos((tiltDeg * Math.PI) / 180);

  const moduleAreaSqm = panelCount * spec.widthM * spec.lengthM;

  return {
    panelCount,
    actualCapacityKw: round((panelCount * spec.watts) / 1000, 3),
    requestedCapacityKw: round(requestedCapacityKw, 3),
    columns,
    rows,
    footprintWidthM: round(footprintWidthM, 3),
    footprintLengthM: round(footprintLengthM, 3),
    moduleAreaSqm: round(moduleAreaSqm, 2),
    occupiedAreaSqm: round(footprintWidthM * footprintLengthM, 2),
    spec,
  };
}

/** Local offsets of each module's centre within the array, metres (east, north). */
export function modulePositions(
  layout: ArrayLayout,
  tiltDeg = 0
): { alongM: number; acrossM: number; index: number }[] {
  const { columns, rows, panelCount, spec } = layout;
  if (panelCount === 0) return [];

  const pitchAcross = spec.widthM + spec.gapM;
  const pitchAlong = (spec.lengthM + spec.gapM) * Math.cos((tiltDeg * Math.PI) / 180);

  const out: { alongM: number; acrossM: number; index: number }[] = [];
  for (let index = 0; index < panelCount; index++) {
    const row = Math.floor(index / columns);
    const column = index % columns;
    out.push({
      acrossM: (column - (columns - 1) / 2) * pitchAcross,
      alongM: (row - (rows - 1) / 2) * pitchAlong,
      index,
    });
  }
  return out;
}

/** Does the array fit the roof area the applicant declared? */
export function fitsRoofArea(
  layout: ArrayLayout,
  roofAreaSqm: number | null | undefined
): { fits: boolean; utilisationPct: number | null } {
  if (roofAreaSqm == null || roofAreaSqm <= 0) {
    return { fits: true, utilisationPct: null };
  }
  const utilisation = (layout.occupiedAreaSqm / roofAreaSqm) * 100;
  return { fits: layout.occupiedAreaSqm <= roofAreaSqm, utilisationPct: round(utilisation, 1) };
}

const M_TO_FT = 3.280_839_895;

export function metresToFeet(metres: number): number {
  return metres * M_TO_FT;
}

export function formatLength(metres: number, units: "m" | "ft"): string {
  return units === "m"
    ? `${metres.toFixed(2)} m`
    : `${metresToFeet(metres).toFixed(2)} ft`;
}

export function formatArea(sqm: number, units: "m" | "ft"): string {
  return units === "m"
    ? `${sqm.toFixed(1)} m²`
    : `${(sqm * M_TO_FT * M_TO_FT).toFixed(1)} ft²`;
}

function round(value: number, places: number): number {
  const factor = 10 ** places;
  return Math.round(value * factor) / factor;
}
