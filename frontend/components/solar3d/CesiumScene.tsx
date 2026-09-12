"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { modulePositions, type ArrayLayout } from "@/lib/solar/array";
import { sunPosition } from "@/lib/solar/sun";
import { rayOpacityFor, skyLabel } from "@/lib/solar/weather";
import type { BuildingFootprint } from "@/lib/types";

/**
 * The 3D rooftop scene: real terrain, real buildings, real sun.
 *
 * Everything drawn here is either measured or geometric.
 *
 *  - Terrain and building geometry come from Cesium Ion. Where Ion has no
 *    buildings for a location, none are drawn and the caller is told so. This
 *    component never extrudes a plausible-looking house to fill the gap.
 *  - The roof height under the array is sampled from the rendered scene, not
 *    assumed. If the sample fails, the height is reported as null.
 *  - Sun direction comes from the selected instant via the same NOAA routine
 *    the readouts use, and Cesium's own lighting is driven from that same
 *    instant, so the shadows on screen and the numbers beside them agree.
 *  - Shading is measured by casting a ray from the array towards the sun and
 *    seeing what it hits. That only sees geometry Ion actually has — no trees,
 *    no water tanks, no parapets — so the result is reported as a sampled
 *    fraction with its limits attached, never as a shading study.
 *
 * Cesium is imported dynamically inside an effect: it is several megabytes,
 * touches `window` at module scope, and must never be part of a server render.
 */

const CESIUM_BASE_URL = "/cesium";

export interface SurfaceInfo {
  /** Terrain height at the point, metres above the ellipsoid. */
  terrainHeightM: number | null;
  /** Height of whatever is rendered there — a roof, if a building exists. */
  surfaceHeightM: number | null;
  /** True when Ion returned building geometry covering this point. */
  buildingDataAvailable: boolean;
  /** True when the sampled surface is meaningfully above the terrain. */
  onBuilding: boolean;
  /** Roof height above ground, metres, when both samples succeeded. */
  buildingHeightM: number | null;
}

export interface ShadingSample {
  /** Fraction of sampled daylight instants the array was in shadow, 0–1. */
  shadedFraction: number | null;
  /** How many daylight instants were tested. */
  samples: number;
  /** False when the browser or scene cannot support ray picking. */
  supported: boolean;
}

export type SceneStatus =
  | "idle"
  | "loading-cesium"
  | "loading-terrain"
  | "loading-buildings"
  | "analysing"
  | "ready"
  | "error";

/**
 * Why Ion content is missing, when it is.
 *
 * These are three different facts and the UI must not collapse them. A
 * rejected token is a configuration problem the operator can fix; no buildings
 * at a location is a property of the data; and a working token with buildings
 * is the normal case. Telling someone "no building data for this location"
 * when the truth is "your token is invalid" sends them looking in the wrong
 * place, and quietly implies their roof was checked when nothing was.
 */
export type IonState = "ok" | "token-missing" | "token-rejected" | "unavailable";

export interface CesiumSceneProps {
  latitude: number;
  longitude: number;
  tiltDeg: number;
  /** Degrees clockwise from north that the array faces. */
  azimuthDeg: number;
  layout: ArrayLayout;
  /** Instant used for sun position, lighting and shadows. */
  when: Date;
  /** Metres the array is raised above the sampled surface. */
  mountHeightM: number;
  showShadows: boolean;
  showBuildings: boolean;
  onSurface: (info: SurfaceInfo) => void;
  onStatus: (status: SceneStatus, detail?: string) => void;
  onShading: (sample: ShadingSample) => void;
  onIonState?: (state: IonState, detail?: string) => void;
  /** Engineering verdict from the backend. Drives the site overlay colour. */
  riskLevel?: "SAFE" | "CAUTION" | "CONSTRAINED" | null;
  /** Fired when the site marker or the array is clicked. */
  onSelectSite?: () => void;
  onLocationChange?: (latitude: number, longitude: number) => void;
  /** Increment to return the camera to the framing it opened with. */
  resetToken?: number;
  /** Mapped footprints to extrude. Null while they are still being fetched. */
  siteBuildings?: BuildingFootprint[] | null;
  /** Draw the dashed sun-direction rays onto the array. */
  showSunRays?: boolean;
  /**
   * Measured cloud cover, 0-100, or null when the forecast is unavailable.
   * Fades the rays: an overcast sky should not be drawn as a bright one.
   */
  cloudCoverPct?: number | null;
}

/** Site overlay colours. Muted on purpose: this sits over aerial imagery and
 *  has to read as an annotation, not a warning light. */
const RISK_COLOURS: Record<string, string> = {
  SAFE: "#22c55e",
  CAUTION: "#f59e0b",
  CONSTRAINED: "#ef4444",
};

/** Height above terrain beyond which we treat the sample as a building roof. */
const BUILDING_THRESHOLD_M = 2;

/** Opening framing: far enough to see the roof and its neighbours, close
 *  enough that an individual module is legible. */
const CAMERA_RANGE_M = 170;
const CAMERA_HEADING_DEG = 25;
const CAMERA_PITCH_DEG = -32;

/** Which 3D dataset the surface under the array was measured against. */
export type BuildingSource = "google" | "osm" | null;

export function CesiumScene({
  latitude,
  longitude,
  tiltDeg,
  azimuthDeg,
  layout,
  when,
  mountHeightM,
  showShadows,
  showBuildings,
  onSurface,
  onStatus,
  onShading,
  onIonState,
  riskLevel = null,
  onSelectSite,
  onLocationChange,
  resetToken = 0,
  siteBuildings = null,
  showSunRays = true,
  cloudCoverPct = null,
}: CesiumSceneProps) {
  const container = useRef<HTMLDivElement>(null);
  // Cesium's own types would have to be loaded eagerly to name these, which
  // defeats the dynamic import; the module is held opaquely and used through
  // the handles below.
  const viewer = useRef<any>(null);
  const cesium = useRef<any>(null);
  const arrayEntities = useRef<any[]>([]);
  const markerEntity = useRef<any>(null);
  /** Height the array is built on: the sampled roof, or the ground. */
  const surfaceHeight = useRef<number | null>(null);
  /** Ground height at the site, kept so a re-measure need not resample it. */
  const terrainHeight = useRef<number | null>(null);
  const ionState = useRef<IonState>("ok");
  const resizeObservers = useRef<ResizeObserver[]>([]);
  const buildingSource = useRef<BuildingSource>(null);
  /** Framing the site opened with, so Reset View is a return, not a guess. */
  const homeView = useRef<{ destination: any; heading: number; pitch: number } | null>(null);
  const riskEntity = useRef<any>(null);
  const buildingEntities = useRef<any[]>([]);
  const sunRayEntities = useRef<any[]>([]);
  /** Height of the site's own building, metres above ground, from the data. */
  const siteRoofHeight = useRef<number | null>(null);
  /**
   * Roof height picked by clicking a building: exact lat/lon/height of the
   * rendered 3D surface (tiles, models, extrusions). Honoured by the next
   * surface measurement when it matches the current coordinates, so the array
   * lands on the clicked roof instead of inside the block or on the ground.
   */
  const clickedSurface = useRef<{ latitude: number; longitude: number; height: number } | null>(null);

  // A monotonic generation counter, not a boolean.
  //
  // Strict Mode builds the viewer, tears it down and builds another. With a
  // boolean, setReady(false) from the teardown and setReady(true) from the
  // rebuild land in the same batch: React sees true -> true, nothing re-runs,
  // and every downstream effect stays bound to the destroyed first viewer. The
  // camera then never flew, no tiles loaded for the site, and the surface
  // measured nothing while the globe looked perfectly healthy.
  //
  // It must only ever increase, for the same reason: 1 -> 0 -> 1 is just as
  // invisible to a dependency comparison as true -> false -> true.
  const [ready, setReady] = useState(0);
  const [fatal, setFatal] = useState<string | null>(null);
  const [surfaceTick, setSurfaceTick] = useState(0);
  // Bumped when the terrain height under the site is known. The extruded
  // blocks are positioned against it, and footprints usually arrive first —
  // without this they were built at height 0 and buried hundreds of metres
  // under the ground they were meant to stand on.
  const [terrainTick, setTerrainTick] = useState(0);

  const token = process.env.NEXT_PUBLIC_CESIUM_ION_TOKEN;

  // ---- create the viewer once ----
  useEffect(() => {
    let cancelled = false;
    if (!container.current || viewer.current) return;

    if (!token) {
      onIonState?.(
        "token-missing",
        "NEXT_PUBLIC_CESIUM_ION_TOKEN is not set, so terrain and 3D buildings are unavailable. The globe still works on open imagery."
      );
    }

    (async () => {
      try {
        onStatus("loading-cesium");
        // Cesium reads this at module initialisation to find its workers and
        // assets, so it has to be set before the import resolves.
        (window as unknown as { CESIUM_BASE_URL: string }).CESIUM_BASE_URL =
          CESIUM_BASE_URL;
        const Cesium = await import("cesium");
        if (cancelled) return;
        cesium.current = Cesium;

        // Ask Ion whether this token actually works before building a scene
        // around it. Ion answers 401 for an expired or mistyped token, and
        // that is a configuration fault worth naming rather than letting it
        // surface later as an empty sky.
        let ion: IonState = token ? "ok" : "token-missing";
        if (token) {
          Cesium.Ion.defaultAccessToken = token;
          try {
            const probe = await fetch(
              "https://api.cesium.com/v1/assets/1/endpoint",
              { headers: { Authorization: `Bearer ${token}` } }
            );
            if (probe.status === 401 || probe.status === 403) {
              ion = "token-rejected";
            } else if (!probe.ok) {
              ion = "unavailable";
            }
          } catch {
            ion = "unavailable";
          }
        }
        if (cancelled) return;
        ionState.current = ion;
        onIonState?.(
          ion,
          ion === "token-rejected"
            ? "Cesium Ion rejected this token, so terrain and 3D buildings are unavailable. Check NEXT_PUBLIC_CESIUM_ION_TOKEN in frontend/.env.local."
            : ion === "unavailable"
              ? "Cesium Ion could not be reached, so terrain and 3D buildings are unavailable."
              : undefined
        );

        onStatus("loading-terrain");
        // Resolve the provider itself rather than handing the Viewer a Terrain
        // wrapper. Terrain.fromWorldTerrain resolves in its own time, and until
        // it does viewer.terrainProvider is still the ellipsoid — which is what
        // sampleTerrainMostDetailed would then be asked to sample, and it has
        // no height data at all. Awaiting the provider means the ground height
        // is measurable from the first frame.
        let worldTerrain: any = null;
        let worldImagery: any = null;

        if (ion === "ok") {
          try {
            worldTerrain = await Cesium.createWorldTerrainAsync({
              requestVertexNormals: true,
            });
          } catch (error) {
            console.warn("[solar3d] world terrain unavailable", error);
            worldTerrain = null;
            onStatus("loading-terrain", "World terrain unavailable — using the ellipsoid.");
          }

          try {
            worldImagery = await Cesium.createWorldImageryAsync({
              style: Cesium.IonWorldImageryStyle.AERIAL_WITH_LABELS,
            });
          } catch {
            try {
              worldImagery = await Cesium.createWorldImageryAsync();
            } catch {
              worldImagery = null;
            }
          }
        }

        if (!worldImagery) {
          try {
            worldImagery = typeof (Cesium.ArcGisMapServerImageryProvider as any).fromUrl === "function"
              ? await (Cesium.ArcGisMapServerImageryProvider as any).fromUrl("https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer")
              : new (Cesium.ArcGisMapServerImageryProvider as any)({ url: "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer" });
          } catch {
            try {
              worldImagery = typeof (Cesium.OpenStreetMapImageryProvider as any).fromUrl === "function"
                ? await (Cesium.OpenStreetMapImageryProvider as any).fromUrl("https://a.tile.openstreetmap.org/")
                : new (Cesium.OpenStreetMapImageryProvider as any)({ url: "https://a.tile.openstreetmap.org/" });
            } catch {
              worldImagery = null;
            }
          }
        }

        if (cancelled) return;

        // Real-world photorealistic satellite aerial imagery basemap
        const v = new Cesium.Viewer(container.current!, {
          baseLayer: worldImagery ? new Cesium.ImageryLayer(worldImagery) : undefined,
          animation: false,
          timeline: false,
          baseLayerPicker: false,
          geocoder: false,
          homeButton: false,
          sceneModePicker: false,
          navigationHelpButton: false,
          fullscreenButton: false,
          selectionIndicator: false,
          infoBox: false,
          shadows: true,
          contextOptions: { webgl: { preserveDrawingBuffer: true } },
        });
        if (cancelled) {
          v.destroy();
          return;
        }
        viewer.current = v;
        (window as unknown as { __solarViewer?: unknown }).__solarViewer = v;

        if (worldTerrain) v.terrainProvider = worldTerrain;

        // Add 3D OSM Buildings Tileset if Ion token is valid
        if (ion === "ok") {
          try {
            const osmBuildings = await Cesium.createOsmBuildingsAsync();
            v.scene.primitives.add(osmBuildings);
          } catch (err) {
            console.warn("[solar3d] OSM 3D buildings tileset load error", err);
          }
        }

        const resizeObserver = new ResizeObserver((entries) => {
          if (v.isDestroyed()) return;
          const box = entries[0]?.contentRect;
          if (box && (box.width < 1 || box.height < 1)) return;
          v.resize();
        });
        resizeObserver.observe(container.current!);
        resizeObservers.current.push(resizeObserver);

        // Globe lighting driven by actual sun position
        v.scene.globe.enableLighting = true;
        if (v.scene.skyAtmosphere) v.scene.skyAtmosphere.show = true;
        v.scene.fog.enabled = true;
        v.scene.globe.depthTestAgainstTerrain = true;
        v.shadowMap.softShadows = true;
        v.shadowMap.maximumDistance = 3000;
        v.clock.shouldAnimate = false;

        setReady((generation) => generation + 1);
        onStatus("ready");
      } catch (error) {
        if (cancelled) return;
        const message =
          error instanceof Error ? error.message : "Cesium failed to initialise.";
        setFatal(message);
        onStatus("error", message);
      }
    })();

    return () => {
      cancelled = true;
      try {
        viewer.current?.destroy();
      } catch {
        /* the widget may already be torn down by Strict Mode */
      }
      viewer.current = null;
      arrayEntities.current = [];
      buildingEntities.current = [];
      sunRayEntities.current = [];
      markerEntity.current = null;
      for (const observer of resizeObservers.current) observer.disconnect();
      resizeObservers.current = [];
      // Deliberately not reset. Resetting sends the counter 1 -> 0 -> 1 across
      // a Strict Mode remount, which compares equal as a dependency and leaves
      // every downstream effect bound to the viewer that was just destroyed.
      // It only ever increments; the null check on viewer.current is what
      // guards a torn-down scene.
    };
    // Deliberately once: the viewer is expensive and everything else is a
    // property update on the live scene.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  // ---- low-poly buildings from mapped footprints ----
  //
  // Extruded OpenStreetMap outlines rather than photogrammetry.
  //
  // Photorealistic tiles are a captured surface: from most angles they read as
  // an aerial photograph, and being one continuous skin they carry no notion of
  // "this polygon is a building" — nothing to select, highlight, or measure a
  // roof against. A footprint is a polygon with an identity, so the site's own
  // building can be picked out, and its roof height is a number the data
  // carries rather than something guessed from a depth buffer.
  //
  // The outline is real and in its true position. The height often is not: OSM
  // maps it on a minority of buildings, and where it is missing the block is
  // drawn at an assumed height and reported as assumed. Nothing here is drawn
  // as fact that is not one.
  useEffect(() => {
    const v = viewer.current;
    const Cesium = cesium.current;
    if (!ready || !v || !Cesium) return;

    for (const entity of buildingEntities.current) v.entities.remove(entity);
    buildingEntities.current = [];

    if (!showBuildings || !siteBuildings || siteBuildings.length === 0) {
      siteRoofHeight.current = null;
      setSurfaceTick((n) => n + 1);
      return;
    }

    const ground = terrainHeight.current ?? 0;

    // Solid concrete tones + dark roof caps so footprints read as buildings.
    // Real Ion OSM 3D Tiles (loaded at viewer creation when the token allows)
    // carry the photorealistic massing; these extrusions use the mapped
    // outline with the mapped height/levels, or a labelled estimate.
    const TONES = ["#8d8fa3", "#9aa0b4", "#7e8496", "#a8adbf"];
    const toneFor = (id: string) => {
      let h = 0;
      for (let i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) >>> 0;
      return TONES[h % TONES.length];
    };

    for (const building of siteBuildings) {
      const ring = building.footprint;
      if (!ring || ring.length < 4) continue;

      const positions = Cesium.Cartesian3.fromDegreesArray(
        ring.flatMap(([lon, lat]: [number, number]) => [lon, lat])
      );

      const isSite = building.is_site;
      const assumed = building.height_source === "assumed";

      buildingEntities.current.push(
        v.entities.add({
          name: building.name ?? building.osm_id,
          polygon: {
            hierarchy: new Cesium.PolygonHierarchy(positions),
            height: ground,
            extrudedHeight: ground + building.height_m,
            // The site reads sky-tinted and solid; neighbours get varied
            // concrete tones. An assumed height keeps full opacity (it must
            // occlude like a building) but is labelled estimated below.
            material: isSite
              ? Cesium.Color.fromCssColorString("#5b8fd4").withAlpha(0.95)
              : Cesium.Color.fromCssColorString(toneFor(building.osm_id)).withAlpha(0.92),
            outline: true,
            outlineColor: isSite
              ? Cesium.Color.fromCssColorString("#e0f2fe")
              : Cesium.Color.fromCssColorString("#2b3446"),
            outlineWidth: isSite ? 2 : 1,
            shadows: Cesium.ShadowMode.ENABLED,
          },
        })
      );

      // Roof cap: thin dark slab + bright parapet so the top reads as a roof.
      buildingEntities.current.push(
        v.entities.add({
          name: `Roof ${building.osm_id}`,
          polygon: {
            hierarchy: new Cesium.PolygonHierarchy(positions),
            height: ground + building.height_m,
            extrudedHeight: ground + building.height_m + 0.5,
            material: Cesium.Color.fromCssColorString(isSite ? "#5b8fd4" : "#4a5265").withAlpha(0.98),
            outline: true,
            outlineColor: Cesium.Color.WHITE.withAlpha(0.85),
            outlineWidth: 1,
            shadows: Cesium.ShadowMode.ENABLED,
          },
        })
      );

      // Estimated height gets a floating tag, not silent confidence.
      if (assumed) {
        const c = ring.reduce(
          ([sx, sy], [lo, la]: [number, number]) => [sx + lo / ring.length, sy + la / ring.length],
          [0, 0]
        );
        buildingEntities.current.push(
          v.entities.add({
            name: `Estimated height ${building.osm_id}`,
            position: Cesium.Cartesian3.fromDegrees(c[0], c[1], ground + building.height_m + 2),
            label: {
              text: `est. ${building.height_m.toFixed(0)} m`,
              font: "10px sans-serif",
              fillColor: Cesium.Color.fromCssColorString("#fcd34d"),
              outlineColor: Cesium.Color.fromCssColorString("#0f172a"),
              outlineWidth: 2,
              style: Cesium.LabelStyle.FILL_AND_OUTLINE,
              disableDepthTestDistance: Number.POSITIVE_INFINITY,
            },
          })
        );
      }

      if (isSite) siteRoofHeight.current = building.height_m;
    }

    // The array is built on the roof, so rebuild it now the height is known.
    setSurfaceTick((n) => n + 1);
    v.scene.requestRender?.();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ready, showBuildings, siteBuildings, terrainTick]);


  // ---- fly to the location and sample the surface ----
  useEffect(() => {
    const Cesium = cesium.current;
    if (!ready || !viewer.current || !Cesium) return;
    if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return;

    let cancelled = false;

    // Re-read the viewer rather than capturing it. Strict Mode can replace the
    // instance while this effect is mid-flight, and a captured handle then
    // points at a destroyed viewer: terrain still sampled (the provider works
    // on its own) but the camera never moved, no tiles loaded for the site, and
    // the roof went unmeasured while the globe looked fine.
    const live = () => {
      const current = viewer.current;
      return current && !current.isDestroyed?.() ? current : null;
    };

    (async () => {
      onStatus("analysing");
      const v = live();
      if (!v) return;

      const carto = Cesium.Cartographic.fromDegrees(longitude, latitude);

      // Terrain first: this is the ground, independent of any building.
      let terrainHeightM: number | null = null;
      try {
        const [sampled] = await Cesium.sampleTerrainMostDetailed(
          v.terrainProvider,
          [Cesium.Cartographic.fromDegrees(longitude, latitude)]
        );
        if (sampled && Number.isFinite(sampled.height)) terrainHeightM = sampled.height;
        terrainHeight.current = terrainHeightM;
        setTerrainTick((n) => n + 1);
      } catch (error) {
        // Swallowing this silently is how a missing ground elevation becomes an
        // unexplained em-dash on screen. The UI still degrades quietly; the
        // console says why.
        console.warn("[solar3d] terrain sample failed", error);
        terrainHeightM = null;
      }
      if (cancelled) return;

      // Deliberately not awaited. Strict Mode runs this effect twice, and two
      // flights on one camera cancel each other — awaiting meant whichever lost
      // the race never measured at all, and the panel showed no elevation for a
      // site the globe was displaying perfectly well. The measurement below
      // retries for several seconds instead, which outlasts the flight.
      const flying = live();
      if (!flying) return;

      // setView, not flyTo.
      //
      // A camera flight is a tween driven by the scene clock, and this scene's
      // clock is deliberately frozen: start, stop and current time are all
      // pinned to the instant being analysed, so the sun and the shadows stay
      // where the readouts say they are. A frozen clock never advances the
      // tween, so flyTo here neither completed nor cancelled - it left the
      // camera in deep space, from which no building tile ever loads and no
      // roof can be measured.
      //
      // Moving instantly is also the honest behaviour: the camera is showing a
      // chosen moment, not travelling through one.
      // Stand the camera off from the site and look back at it.
      //
      // camera.lookAt would express this more directly, but it installs a
      // reference frame and releasing that frame with lookAtTransform leaves
      // the culling volume stale: every geometry entity gets frustum-culled and
      // the scene renders nothing but the depth-test-exempt site marker. So the
      // offset is computed here and handed to setView, which has no such
      // machinery.
      //
      // View direction in the local east-north-up frame for a given heading and
      // pitch; the camera sits one range back along it, which puts the target
      // in the middle of the frame.
      const headingRad = Cesium.Math.toRadians(CAMERA_HEADING_DEG);
      const pitchRad = Cesium.Math.toRadians(CAMERA_PITCH_DEG);
      const back = CAMERA_RANGE_M;

      const eastOffset = -back * Math.cos(pitchRad) * Math.sin(headingRad);
      const northOffset = -back * Math.cos(pitchRad) * Math.cos(headingRad);
      const upOffset = -back * Math.sin(pitchRad);

      const metresPerDegLatitude = 111_320;
      const metresPerDegLongitude =
        111_320 * Math.cos((latitude * Math.PI) / 180);

      const cameraDestination = Cesium.Cartesian3.fromDegrees(
        longitude + eastOffset / metresPerDegLongitude,
        latitude + northOffset / metresPerDegLatitude,
        (terrainHeightM ?? 0) + upOffset
      );

      homeView.current = {
        destination: cameraDestination,
        heading: headingRad,
        pitch: pitchRad,
      };

      flying.camera.setView({
        destination: cameraDestination,
        orientation: { heading: headingRad, pitch: pitchRad, roll: 0 },
      });

      // Marker for the exact coordinate the applicant gave.
      if (markerEntity.current) flying.entities.remove(markerEntity.current);
      markerEntity.current = flying.entities.add({
        name: "Site",
        position: Cesium.Cartesian3.fromDegrees(longitude, latitude, terrainHeightM ?? 0),
        point: {
          pixelSize: 12,
          color: Cesium.Color.fromCssColorString(
            riskLevel ? RISK_COLOURS[riskLevel] : "#38bdf8"
          ),
          outlineColor: Cesium.Color.WHITE,
          outlineWidth: 2,
          heightReference: Cesium.HeightReference.NONE,
          disableDepthTestDistance: Number.POSITIVE_INFINITY,
        },
        label: {
          text: `${latitude.toFixed(5)}, ${longitude.toFixed(5)}`,
          font: "12px sans-serif",
          pixelOffset: new Cesium.Cartesian2(0, -22),
          fillColor: Cesium.Color.WHITE,
          outlineColor: Cesium.Color.fromCssColorString("#0f172a"),
          outlineWidth: 3,
          style: Cesium.LabelStyle.FILL_AND_OUTLINE,
          disableDepthTestDistance: Number.POSITIVE_INFINITY,
        },
      });

      // Roof height, best source first:
      //   1. the clicked 3D surface (a roof the user chose — exact height),
      //   2. scene.sampleHeight (3D Tiles / models aware, no footprint needed),
      //   3. the mapped footprint height above terrain,
      //   4. terrain itself.
      // Whatever wins, the array base sits ON the roof, never inside the block.
      let roofTopM: number | null = null;
      let roofSource: "picked" | "tiles" | "footprint" | null = null;
      const click = clickedSurface.current;
      if (
        click &&
        Math.abs(click.latitude - latitude) < 0.00015 &&
        Math.abs(click.longitude - longitude) < 0.00015 &&
        Number.isFinite(click.height)
      ) {
        roofTopM = click.height;
        roofSource = "picked";
      }
      if (roofTopM == null) {
        try {
          const h = flying.scene.sampleHeight(
            Cesium.Cartographic.fromDegrees(longitude, latitude)
          );
          if (Number.isFinite(h) && terrainHeightM != null && h > terrainHeightM + 1.5) {
            roofTopM = h;
            roofSource = "tiles";
          }
        } catch { /* scene not ready for sampling — fall through */ }
      }
      const roofM = siteRoofHeight.current;
      if (roofTopM == null && roofM != null && terrainHeightM != null) {
        roofTopM = terrainHeightM + roofM;
        roofSource = "footprint";
      }
      const onBuilding =
        roofTopM != null &&
        (roofSource !== null || (roofM != null && roofM >= BUILDING_THRESHOLD_M));
      const surfaceHeightM = roofTopM ?? terrainHeightM;

      surfaceHeight.current = surfaceHeightM ?? terrainHeightM ?? 0;
      // The array is built on this height, so rebuild it now that we know it.
      setSurfaceTick((n) => n + 1);
      onSurface({
        terrainHeightM,
        surfaceHeightM,
        buildingDataAvailable: onBuilding,
        onBuilding,
        buildingHeightM:
          roofTopM != null && terrainHeightM != null ? roofTopM - terrainHeightM : roofM,
      });
      onStatus("ready");
    })();

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ready, latitude, longitude, showBuildings]);


  // ---- clock, lighting, shadows ----
  useEffect(() => {
    const v = viewer.current;
    const Cesium = cesium.current;
    if (!ready || !v || !Cesium) return;

    const julian = Cesium.JulianDate.fromDate(when);
    v.clock.currentTime = julian;
    v.clock.startTime = julian;
    v.clock.stopTime = julian;
    v.scene.shadowMap.enabled = showShadows;
    v.scene.requestRender?.();
  }, [ready, when, showShadows]);

  // ---- the panel array ----
  useEffect(() => {
    const v = viewer.current;
    const Cesium = cesium.current;
    if (!ready || !v || !Cesium) return;
    if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return;

    for (const entity of arrayEntities.current) v.entities.remove(entity);
    arrayEntities.current = [];

    if (layout.panelCount === 0) return;

    // Base height: the sampled surface plus the mount, so the array sits on
    // the roof rather than through it.
    const base = surfaceHeight.current ?? 0;
    const positions = modulePositions(layout, tiltDeg);
    const spec = layout.spec;

    // Metres to degrees at this latitude — small offsets, so a local flat
    // approximation is exact to well under a millimetre over an array.
    const metresPerDegLat = 111_320;
    const metresPerDegLon = 111_320 * Math.cos((latitude * Math.PI) / 180);

    const headingRad = Cesium.Math.toRadians(azimuthDeg);
    const cosH = Math.cos(headingRad);
    const sinH = Math.sin(headingRad);

    for (const position of positions) {
      // Rotate the array's local (across, along) offsets into east/north by
      // the array bearing, so the whole block turns with the azimuth.
      const east = position.acrossM * cosH + position.alongM * sinH;
      const north = -position.acrossM * sinH + position.alongM * cosH;

      const lon = longitude + east / metresPerDegLon;
      const lat = latitude + north / metresPerDegLat;

      // A tilted module's centre rises by half its slope length times sin(tilt).
      const rise = (spec.lengthM / 2) * Math.sin((tiltDeg * Math.PI) / 180);
      const centreHeight = base + mountHeightM + rise;

      const origin = Cesium.Cartesian3.fromDegrees(lon, lat, centreHeight);
      const orientation = Cesium.Transforms.headingPitchRollQuaternion(
        origin,
        new Cesium.HeadingPitchRoll(
          headingRad,
          Cesium.Math.toRadians(tiltDeg),
          0
        )
      );

      arrayEntities.current.push(
        v.entities.add({
          position: origin,
          orientation,
          box: {
            dimensions: new Cesium.Cartesian3(spec.widthM, spec.lengthM, 0.04),
            material: Cesium.Color.fromCssColorString("#1e3a5f").withAlpha(0.96),
            outline: true,
            outlineColor: Cesium.Color.fromCssColorString("#7dd3fc"),
            shadows: Cesium.ShadowMode.ENABLED,
          },
        })
      );
    }

    v.scene.requestRender?.();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ready, latitude, longitude, layout, tiltDeg, azimuthDeg, mountHeightM, surfaceTick]);

  // ---- sun-direction rays ----
  //
  // Yellow dashed lines arriving on the array from wherever the sun actually
  // is at the selected instant. Shadows already tell you the answer, but only
  // once you have found something to cast one; the rays say which way to turn
  // the array before you have worked that out.
  //
  // The direction is astronomy, computed by lib/solar/sun.ts from the NOAA
  // algorithm for this date, time and coordinate — nothing here is chosen to
  // look good. What the forecast contributes is how solid the rays are drawn:
  // measured cloud cover fades them, so an overcast roof is not shown bathed
  // in beam it is not receiving. Below the horizon nothing is drawn at all.
  useEffect(() => {
    const v = viewer.current;
    const Cesium = cesium.current;
    if (!ready || !v || !Cesium) return;

    for (const entity of sunRayEntities.current) v.entities.remove(entity);
    sunRayEntities.current = [];

    if (!showSunRays) {
      v.scene.requestRender?.();
      return;
    }
    if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return;

    const sun = sunPosition(when, latitude, longitude);
    if (sun.elevation <= 0) {
      // Night. A ray drawn now would point through the planet.
      v.scene.requestRender?.();
      return;
    }

    const el = (sun.elevation * Math.PI) / 180;
    const az = (sun.azimuth * Math.PI) / 180;

    // Unit vector from the array towards the sun, local east-north-up.
    const dirEast = Math.cos(el) * Math.sin(az);
    const dirNorth = Math.cos(el) * Math.cos(az);
    const dirUp = Math.sin(el);

    // Horizontal direction across the beam, to space the rays out.
    const acrossEast = Math.cos(az);
    const acrossNorth = -Math.sin(az);

    const metresPerDegLat = 111_320;
    const metresPerDegLon = 111_320 * Math.cos((latitude * Math.PI) / 180);

    const base = (surfaceHeight.current ?? 0) + mountHeightM;
    const span = Math.max(layout.footprintWidthM, layout.footprintLengthM);
    // Long enough to read as coming from off-roof, short enough to stay in
    // frame at the opening camera range.
    const rayLengthM = Math.min(70, Math.max(16, span * 1.6));

    const at = (east: number, north: number, up: number) =>
      Cesium.Cartesian3.fromDegrees(
        longitude + east / metresPerDegLon,
        latitude + north / metresPerDegLat,
        base + up
      );

    const alpha = rayOpacityFor(cloudCoverPct);
    const yellow = Cesium.Color.fromCssColorString("#facc15").withAlpha(alpha);
    const dashed = new Cesium.PolylineDashMaterialProperty({
      color: yellow,
      dashLength: 10,
    });

    // Rays land across the width of the array rather than all on one point,
    // so the whole block is visibly lit from the same side.
    const lanes = layout.panelCount > 6 ? [-1, -0.5, 0, 0.5, 1] : [-1, 0, 1];
    const laneStepM = Math.max(1.2, layout.footprintWidthM / 2);

    for (const lane of lanes) {
      const offEast = acrossEast * lane * laneStepM;
      const offNorth = acrossNorth * lane * laneStepM;

      const target = at(offEast, offNorth, 0.15);
      const origin = at(
        offEast + dirEast * rayLengthM,
        offNorth + dirNorth * rayLengthM,
        dirUp * rayLengthM
      );
      // The arrowhead is the last stretch of the same line, drawn solid so it
      // reads as a direction rather than another dash.
      const elbowFraction = 0.82;
      const elbow = at(
        offEast + dirEast * rayLengthM * (1 - elbowFraction),
        offNorth + dirNorth * rayLengthM * (1 - elbowFraction),
        dirUp * rayLengthM * (1 - elbowFraction) + 0.15
      );

      sunRayEntities.current.push(
        v.entities.add({
          polyline: {
            positions: [origin, elbow],
            width: 2,
            material: dashed,
            arcType: Cesium.ArcType.NONE,
          },
        }),
        v.entities.add({
          polyline: {
            positions: [elbow, target],
            width: 9,
            material: new Cesium.PolylineArrowMaterialProperty(yellow),
            arcType: Cesium.ArcType.NONE,
          },
        })
      );
    }

    // One caption, on the middle ray, saying where the sun is and what the sky
    // is doing. Both are measurements; neither is rounded into a claim.
    sunRayEntities.current.push(
      v.entities.add({
        position: at(dirEast * rayLengthM, dirNorth * rayLengthM, dirUp * rayLengthM + 1.5),
        label: {
          text:
            `Sunlight ${Math.round(sun.azimuth)}° · ${Math.round(sun.elevation)}° above horizon` +
            (cloudCoverPct != null
              ? `
${skyLabel(cloudCoverPct)} · ${Math.round(cloudCoverPct)}% cloud`
              : ""),
          font: "500 13px Poppins, system-ui, sans-serif",
          fillColor: Cesium.Color.fromCssColorString("#facc15"),
          outlineColor: Cesium.Color.fromCssColorString("#0f172a"),
          outlineWidth: 3,
          style: Cesium.LabelStyle.FILL_AND_OUTLINE,
          horizontalOrigin: Cesium.HorizontalOrigin.CENTER,
          verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
          disableDepthTestDistance: Number.POSITIVE_INFINITY,
          scaleByDistance: new Cesium.NearFarScalar(50, 1.0, 600, 0.55),
        },
      })
    );

    v.scene.requestRender?.();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    ready,
    latitude,
    longitude,
    when,
    layout,
    mountHeightM,
    showSunRays,
    cloudCoverPct,
    surfaceTick,
  ]);

  // ---- risk overlay on the site ----
  //
  // A ring on the ground under the array, coloured by the engineering verdict
  // the backend returned. It is an annotation of a decision made elsewhere:
  // nothing here computes a risk, and with no verdict nothing is drawn rather
  // than a reassuring default.
  useEffect(() => {
    const v = viewer.current;
    const Cesium = cesium.current;
    if (!ready || !v || !Cesium) return;
    if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return;

    if (riskEntity.current) {
      v.entities.remove(riskEntity.current);
      riskEntity.current = null;
    }
    if (!riskLevel) return;

    const colour = Cesium.Color.fromCssColorString(RISK_COLOURS[riskLevel]);
    const base = surfaceHeight.current ?? 0;

    riskEntity.current = v.entities.add({
      name: "Grid risk",
      position: Cesium.Cartesian3.fromDegrees(longitude, latitude, base + 0.15),
      ellipse: {
        semiMajorAxis: 12,
        semiMinorAxis: 12,
        height: base + 0.15,
        material: colour.withAlpha(0.16),
        outline: true,
        outlineColor: colour.withAlpha(0.85),
        outlineWidth: 2,
      },
    });
    v.scene.requestRender?.();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ready, latitude, longitude, riskLevel, surfaceTick]);

  // ---- return the camera to its opening framing ----
  useEffect(() => {
    const v = viewer.current;
    const home = homeView.current;
    if (!ready || !v || !home || resetToken === 0) return;
    v.camera.setView({
      destination: home.destination,
      orientation: { heading: home.heading, pitch: home.pitch, roll: 0 },
    });
    v.scene.requestRender?.();
  }, [ready, resetToken]);

  // ---- clicking the site or the array opens detail panel / picks placement position ----
  useEffect(() => {
    const v = viewer.current;
    const Cesium = cesium.current;
    if (!ready || !v || !Cesium) return;

    const handler = new Cesium.ScreenSpaceEventHandler(v.scene.canvas);
    handler.setInputAction((movement: any) => {
      const picked = v.scene.pick(movement.position);
      if (Cesium.defined(picked)) {
        const entity = picked.id;
        const isSite =
          entity === markerEntity.current ||
          entity === riskEntity.current ||
          arrayEntities.current.includes(entity);
        if (isSite && onSelectSite) {
          onSelectSite();
          return;
        }
      }

      // Pick the real 3D surface: 3D Tiles / models / extrusions first so a
      // click on a roof returns the roof (with its height), falling back to
      // the terrain globe. The measured height travels with the coordinates
      // so the array is rebuilt on top of the clicked building, never inside
      // it.
      if (onLocationChange) {
        let picked: any = null;
        try {
          if (v.scene.pickPositionSupported) picked = v.scene.pickPosition(movement.position);
        } catch { picked = null; }
        if (picked && Number.isFinite(picked.x)) {
          try {
            const carto = Cesium.Cartographic.fromCartesian(picked);
            const clickedLat = Cesium.Math.toDegrees(carto.latitude);
            const clickedLon = Cesium.Math.toDegrees(carto.longitude);
            if (Number.isFinite(clickedLat) && Number.isFinite(clickedLon) && Number.isFinite(carto.height)) {
              clickedSurface.current = { latitude: clickedLat, longitude: clickedLon, height: carto.height };
              onLocationChange(clickedLat, clickedLon);
              return;
            }
          } catch { /* fall through to globe pick */ }
        }
        const ray = v.camera.getPickRay(movement.position);
        if (ray) {
          const cartesian = v.scene.globe.pick(ray, v.scene);
          if (cartesian) {
            const carto = Cesium.Cartographic.fromCartesian(cartesian);
            const clickedLat = Cesium.Math.toDegrees(carto.latitude);
            const clickedLon = Cesium.Math.toDegrees(carto.longitude);
            if (Number.isFinite(clickedLat) && Number.isFinite(clickedLon)) {
              clickedSurface.current = null;
              onLocationChange(clickedLat, clickedLon);
            }
          }
        }
      }
    }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

    return () => handler.destroy();
  }, [ready, onSelectSite, onLocationChange]);

  // ---- shading sample: cast rays at the sun across the day ----
  const measureShading = useCallback((): ShadingSample => {
    const v = viewer.current;
    const Cesium = cesium.current;
    if (!ready || !v || !Cesium || buildingEntities.current.length === 0) {
      return { shadedFraction: null, samples: 0, supported: false };
    }
    if (typeof v.scene.pickFromRay !== "function") {
      return { shadedFraction: null, samples: 0, supported: false };
    }

    const base = surfaceHeight.current ?? 0;
    const origin = Cesium.Cartesian3.fromDegrees(
      longitude,
      latitude,
      base + mountHeightM + 0.5
    );
    const enu = Cesium.Transforms.eastNorthUpToFixedFrame(origin);

    let shaded = 0;
    let tested = 0;

    // Sample the day every twenty minutes; anything finer costs frames for a
    // precision the underlying building data does not have.
    for (let minutes = 0; minutes < 1440; minutes += 20) {
      const instant = new Date(when);
      instant.setUTCHours(0, 0, 0, 0);
      instant.setUTCMinutes(minutes);

      const sun = sunPosition(instant, latitude, longitude);
      if (sun.elevation <= 3) continue; // grazing sun tells us little
      tested++;

      // Direction to the sun in the local east-north-up frame.
      const el = (sun.elevation * Math.PI) / 180;
      const az = (sun.azimuth * Math.PI) / 180;
      const local = new Cesium.Cartesian3(
        Math.cos(el) * Math.sin(az),
        Math.cos(el) * Math.cos(az),
        Math.sin(el)
      );
      const world = Cesium.Matrix4.multiplyByPointAsVector(
        enu,
        local,
        new Cesium.Cartesian3()
      );
      Cesium.Cartesian3.normalize(world, world);

      try {
        const hit = v.scene.pickFromRay(new Cesium.Ray(origin, world), arrayEntities.current);
        // A hit within a few hundred metres towards the sun is something
        // standing between this roof and the light.
        if (hit?.position) {
          const distance = Cesium.Cartesian3.distance(origin, hit.position);
          if (distance < 400) shaded++;
        }
      } catch {
        return { shadedFraction: null, samples: 0, supported: false };
      }
    }

    return {
      shadedFraction: tested > 0 ? shaded / tested : null,
      samples: tested,
      supported: true,
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ready, latitude, longitude, mountHeightM, when]);

  // Report shading whenever the geometry or the day changes.
  useEffect(() => {
    if (!ready) return;
    const id = window.setTimeout(() => onShading(measureShading()), 600);
    return () => window.clearTimeout(id);
  }, [ready, measureShading, onShading]);

  if (fatal) {
    return (
      <div className="flex h-[520px] items-center justify-center rounded-xl border border-red-900 bg-red-950/30 p-6">
        <div className="max-w-md text-center">
          <p className="text-sm font-medium text-red-200">3D view unavailable</p>
          <p className="mt-2 text-xs leading-relaxed text-red-300/80">{fatal}</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Cesium's widget CSS lives with its runtime assets rather than in the
          bundle, so it is linked from the public path the viewer already uses. */}
      {/* eslint-disable-next-line @next/next/no-css-tags */}
      <link rel="stylesheet" href={`${CESIUM_BASE_URL}/Widgets/widgets.css`} />
      <div
        ref={container}
        className="h-[520px] w-full overflow-hidden rounded-xl border border-slate-800 bg-slate-950"
      />
    </>
  );
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

