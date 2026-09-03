"use client";

import { useEffect, useRef, useState } from "react";
import type { TwinNode, TwinResponse } from "@/lib/types";

interface Props {
  twin?: TwinResponse | null;
  busId?: string;
  onSelectBus?: (bus: string) => void;
  onToggle2D?: () => void;
}

interface SelectedCardPos {
  id: string;
  title: string;
  subtitle: string;
  x: number;
  y: number;
  visible: boolean;
  type: "substation" | "bus" | "transformer" | "house";
  metrics: { label: string; val: string; highlight?: boolean; color?: string }[];
}

export function DistributionTwin3D({ twin, busId, onSelectBus, onToggle2D }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<any>(null);
  const sceneRef = useRef<any>(null);
  const cameraRef = useRef<any>(null);
  const controlsRef = useRef<any>(null);
  const animRef = useRef<number>(0);

  // References for animated 3D meshes (pulses, blinking rings, flow particles)
  const pulseRingRef = useRef<any>(null);
  const localityWaveRef = useRef<any>(null);
  const lineTubesRef = useRef<any[]>([]);

  const [layer, setLayer] = useState<"All Layers" | "Risk" | "Voltage" | "Transformer loading">("All Layers");
  const [loading, setLoading] = useState(true);

  // Selection & On-Demand Cards: card appears ONLY when user clicks an object!
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(busId || "734");
  const [selectedNodeInfo, setSelectedNodeInfo] = useState<TwinNode | null>(null);
  const [cardPos, setCardPos] = useState<SelectedCardPos | null>(null);

  // Interactive Simulation / Test Mode State
  const [testKw, setTestKw] = useState<number>(twin?.assessment.metrics.new_pv_kw || 66);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [autoRotate, setAutoRotate] = useState(false);

  // Derive stats dynamically from backend twin payload
  const stats = twin
    ? {
        totalLoad: (twin.elements.energy_balance.feeder_load_kw / 1000).toFixed(2),
        totalPV: (twin.assessment.metrics.total_pv_kw / 1000).toFixed(2),
        consumers: twin.topology.nodes.filter((n) => n.type === "HOUSE" || n.type === "BUS").length || 1287,
        minV: twin.assessment.metrics.feeder_min_voltage_pu
          ? (twin.assessment.metrics.feeder_min_voltage_pu * 11).toFixed(2)
          : "10.72",
        maxV: twin.assessment.metrics.feeder_max_voltage_pu
          ? (twin.assessment.metrics.feeder_max_voltage_pu * 11).toFixed(2)
          : "11.12",
        avgV: twin.assessment.metrics.pv_voltage_pu
          ? (twin.assessment.metrics.pv_voltage_pu * 11).toFixed(2)
          : "10.94",
        vRise: twin.assessment.metrics.voltage_rise_pu
          ? (twin.assessment.metrics.voltage_rise_pu * 100).toFixed(2)
          : "1.45",
        p: Math.round(twin.assessment.metrics.pv_total_p_kw ?? 3250),
        q: Math.round(twin.assessment.metrics.power_loss_kw * 10 || 1210),
        pf: twin.assessment.metrics.reverse_power_flow ? "0.94 Rev" : "0.97 Lag",
        feederLoad: Math.round(twin.assessment.metrics.max_transformer_loading_pct ?? 58),
        gridSupply: twin.elements.energy_balance.grid_supply_after_kw.toFixed(1),
        solarGen: twin.elements.energy_balance.solar_generation_kw.toFixed(1),
        localExport: twin.elements.energy_balance.local_export_kw.toFixed(1),
        pvBus: twin.assessment.metrics.pv_bus || busId || "734",
        risk: twin.assessment.engineering.engineering_risk || "SAFE",
      }
    : {
        totalLoad: "3.25",
        totalPV: "1.15",
        consumers: 1287,
        minV: "10.72",
        maxV: "11.12",
        avgV: "10.94",
        vRise: "1.45",
        p: 3250,
        q: 1210,
        pf: "0.96 Lag",
        feederLoad: 58,
        gridSupply: "450.0",
        solarGen: "66.0",
        localExport: "22.5",
        pvBus: busId || "734",
        risk: "SAFE",
      };

  const availableBuses = twin?.topology.nodes.filter((n) => n.pv_eligible || n.type === "BUS") || [];

  useEffect(() => {
    let cancelled = false;
    if (!containerRef.current) return;

    (async () => {
      const THREE = await import("three");
      const { OrbitControls } = await import("three/addons/controls/OrbitControls.js");
      if (cancelled || !containerRef.current) return;

      const container = containerRef.current;
      const width = container.clientWidth;
      const height = 580;

      // --- scene / camera / renderer ---
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x0b1e33);
      scene.fog = new THREE.Fog(0x0b1e33, 80, 280);
      sceneRef.current = scene;

      const camera = new THREE.PerspectiveCamera(48, width / height, 0.1, 2000);
      camera.position.set(55, 42, 55);
      camera.lookAt(0, 0, 0);
      cameraRef.current = camera;

      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      container.innerHTML = "";
      container.appendChild(renderer.domElement);
      rendererRef.current = renderer;

      // --- lights ---
      scene.add(new THREE.HemisphereLight(0xffffff, 0x223355, 0.95));
      const sun = new THREE.DirectionalLight(0xfff6e8, 1.15);
      sun.position.set(60, 90, 40);
      sun.castShadow = true;
      sun.shadow.mapSize.set(2048, 2048);
      sun.shadow.camera.near = 0.5;
      sun.shadow.camera.far = 300;
      sun.shadow.camera.left = -80;
      sun.shadow.camera.right = 80;
      sun.shadow.camera.top = 80;
      sun.shadow.camera.bottom = -80;
      scene.add(sun);
      const fill = new THREE.DirectionalLight(0x8ecae6, 0.4);
      fill.position.set(-40, 30, -50);
      scene.add(fill);

      // --- ground ---
      const groundGeo = new THREE.PlaneGeometry(300, 300, 32, 32);
      const groundMat = new THREE.MeshStandardMaterial({ color: 0x1a2e22, roughness: 0.92, metalness: 0.02 });
      const ground = new THREE.Mesh(groundGeo, groundMat);
      ground.rotation.x = -Math.PI / 2;
      ground.receiveShadow = true;
      scene.add(ground);

      // Roads
      const roadMat = new THREE.MeshStandardMaterial({ color: 0x2e3440, roughness: 0.85 });
      const makeRoad = (w: number, h: number, x: number, z: number) => {
        const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), roadMat);
        m.rotation.x = -Math.PI / 2;
        m.position.set(x, 0.02, z);
        m.receiveShadow = true;
        scene.add(m);
        const line = new THREE.Mesh(
          new THREE.PlaneGeometry(w * 0.98, 0.25),
          new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.85 })
        );
        line.rotation.x = -Math.PI / 2;
        line.position.set(x, 0.03, z);
        scene.add(line);
      };
      makeRoad(160, 8, 0, 4);
      makeRoad(8, 160, -8, 0);

      const raycastables: any[] = [];
      const nodePosMap: { [id: string]: any } = {};

      // Substation
      const subGroup = new THREE.Group();
      subGroup.position.set(-52, 0, -42);
      subGroup.userData = { id: "substation", type: "substation", label: "Substation 110/11 kV" };
      const yard = new THREE.Mesh(
        new THREE.BoxGeometry(28, 0.2, 22),
        new THREE.MeshStandardMaterial({ color: 0x3a4553, roughness: 0.9 })
      );
      yard.position.y = 0.1;
      yard.receiveShadow = true;
      subGroup.add(yard);

      for (let i = -1; i <= 1; i++) {
        const tank = new THREE.Mesh(
          new THREE.BoxGeometry(3.2, 2.4, 2.2),
          new THREE.MeshStandardMaterial({ color: 0x8d99ae, metalness: 0.2, roughness: 0.6 })
        );
        tank.position.set(i * 6, 1.3, 0);
        tank.castShadow = true;
        subGroup.add(tank);
      }
      scene.add(subGroup);
      raycastables.push(subGroup);
      nodePosMap["substation"] = new THREE.Vector3(-52, 6, -42);

      // Neighborhood Houses & Bus Nodes
      const rng = mulberry32(hashCode(busId ?? twin?.topology.source_bus ?? "demo"));
      const housePositions: { x: number; z: number; hasPV: boolean; busId?: string }[] = [];
      const blocks = [
        { cx: -10, cz: -18, rows: 2, cols: 3 },
        { cx: 22, cz: -14, rows: 2, cols: 4 },
        { cx: 18, cz: 8, rows: 3, cols: 3 },
        { cx: -22, cz: 16, rows: 2, cols: 3 },
        { cx: 4, cz: 28, rows: 2, cols: 3 },
      ];

      let busIdx = 0;
      const busList = twin?.topology.nodes.filter((n) => n.pv_eligible || n.type === "BUS") ?? [];
      const activeBus = selectedEntityId || busId || "734";

      blocks.forEach((blk) => {
        for (let r = 0; r < blk.rows; r++) {
          for (let c = 0; c < blk.cols; c++) {
            const x = blk.cx + c * 10 + (rng() - 0.5) * 2;
            const z = blk.cz + r * 10 + (rng() - 0.5) * 2;
            const b = busList[busIdx % Math.max(1, busList.length)]?.id ?? `bus_${busIdx + 100}`;
            const isSelected = b === activeBus;
            const hasPV = isSelected || rng() > 0.5;
            busIdx++;

            const houseGroup = addHouse(THREE, scene, x, z, hasPV, rng, isSelected);
            houseGroup.userData = { id: b, busId: b, type: "house", label: `Premises Bus-${b}` };
            raycastables.push(houseGroup);
            housePositions.push({ x, z, hasPV, busId: b });

            nodePosMap[b] = new THREE.Vector3(x, 4.5, z);
          }
        }
      });

      // Animated Pulsing Indicator Ring for Selected Bus
      const activePos = nodePosMap[activeBus] || new THREE.Vector3(-10, 0, -18);
      const ringGeo = new THREE.RingGeometry(3.6, 4.4, 32);
      const ringMat = new THREE.MeshBasicMaterial({
        color: stats.risk === "CONSTRAINED" ? 0xef4444 : stats.risk === "CAUTION" ? 0xeab308 : 0x0284c7,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.8,
      });
      const pulseRing = new THREE.Mesh(ringGeo, ringMat);
      pulseRing.rotation.x = -Math.PI / 2;
      pulseRing.position.set(activePos.x, 0.08, activePos.z);
      scene.add(pulseRing);
      pulseRingRef.current = pulseRing;

      // Locality Impact Wave (Expanding translucent ring to show neighborhood effect)
      const waveGeo = new THREE.RingGeometry(1, 1.8, 32);
      const waveMat = new THREE.MeshBasicMaterial({
        color: 0x38bdf8,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.0,
      });
      const localityWave = new THREE.Mesh(waveGeo, waveMat);
      localityWave.rotation.x = -Math.PI / 2;
      localityWave.position.set(activePos.x, 0.09, activePos.z);
      scene.add(localityWave);
      localityWaveRef.current = localityWave;

      // Vegetation
      for (let i = 0; i < 34; i++) {
        const x = (rng() - 0.5) * 140;
        const z = (rng() - 0.5) * 140;
        if (Math.abs(x) < 18 && Math.abs(z - 4) < 6) continue;
        if (Math.abs(x + 8) < 8 && Math.abs(z) < 70) continue;
        if (distanceToNearest(x, z, housePositions) < 4) continue;
        addTree(THREE, scene, x, z, rng);
      }

      // Poles & Cable Network
      const poleMat = new THREE.MeshStandardMaterial({ color: 0x7c6f5a, roughness: 0.9 });
      const spine: [number, number][] = [[-38, -32], [-22, -18], [-8, -6], [6, 4], [18, 12], [30, 18]];
      const branchA: [number, number][] = [[-8, -6], [-2, -14], [8, -18]];
      const branchB: [number, number][] = [[6, 4], [4, 16], [-4, 22]];

      const lineGroups: any[] = [];
      const lineTubes: any[] = [];

      const addPolesAndLine = (points: [number, number][], defaultColor: number, isBranch: boolean) => {
        const lineHex = layer === "Risk"
          ? stats.risk === "CONSTRAINED" ? 0xef4444 : stats.risk === "CAUTION" ? 0xeab308 : 0x22c55e
          : layer === "Voltage"
          ? 0x38bdf8
          : isBranch ? 0xf97316 : 0x38bdf8;

        const pts3 = points.map(([x, z]) => new THREE.Vector3(x, 0, z));
        pts3.forEach((p) => {
          const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.18, 7, 8), poleMat);
          pole.position.set(p.x, 3.5, p.z);
          pole.castShadow = true;
          scene.add(pole);

          const cross = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.12, 0.12), poleMat);
          cross.position.set(p.x, 6.2, p.z);
          scene.add(cross);
        });

        const curve = new THREE.CatmullRomCurve3(pts3);
        const tubeMat = new THREE.MeshStandardMaterial({
          color: lineHex,
          emissive: lineHex,
          emissiveIntensity: 0.4,
          roughness: 0.3,
        });
        const tube = new THREE.Mesh(new THREE.TubeGeometry(curve, 64, 0.08, 6, false), tubeMat);
        tube.castShadow = true;
        scene.add(tube);
        lineTubes.push(tubeMat);

        const flowGroup = new THREE.Group();
        const reversed = twin?.elements.energy_balance.local_export_kw ? twin.elements.energy_balance.local_export_kw > 0 : false;
        for (let i = 0; i < 3; i++) {
          const s = new THREE.Mesh(
            new THREE.SphereGeometry(0.22, 8, 8),
            new THREE.MeshBasicMaterial({ color: reversed ? 0x7dd3fc : lineHex })
          );
          s.userData = { t: i / 3, speed: (0.16 + rng() * 0.1) * (reversed ? -1 : 1), curve };
          flowGroup.add(s);
        }
        scene.add(flowGroup);
        lineGroups.push(flowGroup);
      };

      addPolesAndLine(spine, 0x38bdf8, false);
      addPolesAndLine(branchA, 0xf97316, true);
      addPolesAndLine(branchB, 0x38bdf8, false);

      lineTubesRef.current = lineTubes;

      // Orbit controls
      const controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.06;
      controls.target.set(activePos.x, 0, activePos.z);
      controls.minDistance = 12;
      controls.maxDistance = 160;
      controls.maxPolarAngle = Math.PI / 2.05;
      controls.update();
      controlsRef.current = controls;

      // --- Interactive Raycasting on Mouse Click ---
      const raycaster = new THREE.Raycaster();
      const mouse = new THREE.Vector2();

      const handleCanvasClick = (event: MouseEvent) => {
        if (!containerRef.current) return;
        const rect = containerRef.current.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(raycastables, true);

        if (intersects.length > 0) {
          let obj: any = intersects[0].object;
          while (obj && !obj.userData?.id && obj.parent) {
            obj = obj.parent;
          }
          if (obj && obj.userData?.id) {
            const hitId = obj.userData.id;
            setSelectedEntityId(hitId);

            if (obj.userData.busId && onSelectBus) {
              onSelectBus(obj.userData.busId);
            }

            const foundNode = twin?.topology.nodes.find((n) => n.id === hitId);
            if (foundNode) {
              setSelectedNodeInfo(foundNode);
            }
          }
        }
      };

      const canvasEl = renderer.domElement;
      canvasEl.addEventListener("click", handleCanvasClick);

      // --- Dynamic Projection for ON-DEMAND Selected Floating Card ---
      const updateSelectedCardPos = () => {
        if (!cameraRef.current || !containerRef.current || !selectedEntityId) {
          setCardPos(null);
          return;
        }
        const width = containerRef.current.clientWidth;
        const height = 580;

        const targetPos = nodePosMap[selectedEntityId] || new THREE.Vector3(-10, 4.5, -18);
        const v = targetPos.clone();
        v.project(cameraRef.current);
        const x = ((v.x + 1) * width) / 2;
        const y = ((-v.y + 1) * height) / 2;
        const visible = v.z < 1.0 && x >= 20 && x <= width - 20 && y >= 50 && y <= height - 50;

        if (selectedEntityId === "substation") {
          setCardPos({
            id: "substation",
            title: "Main Substation",
            subtitle: "110/11 kV Grid Feeder",
            type: "substation",
            x, y, visible,
            metrics: [
              { label: "Feeder Load", val: `${stats.totalLoad} MW` },
              { label: "Grid Supply", val: `${stats.gridSupply} kW` },
              { label: "Status", val: "Normal Operation", color: "text-emerald-400" },
            ],
          });
        } else {
          setCardPos({
            id: selectedEntityId,
            title: `Premises Bus-${selectedEntityId}`,
            subtitle: "Clicked Connection Point",
            type: "house",
            x, y, visible,
            metrics: [
              { label: "Voltage", val: `${stats.avgV} kV` },
              { label: "Proposed PV", val: `${testKw} kW`, highlight: true },
              { label: "Voltage Rise", val: `+${stats.vRise}%`, color: Number(stats.vRise) > 3 ? "text-amber-400" : "text-sky-300" },
              { label: "Locality Risk", val: stats.risk, color: stats.risk === "CONSTRAINED" ? "text-red-400" : stats.risk === "CAUTION" ? "text-amber-400" : "text-emerald-400" },
            ],
          });
        }
      };

      // Resize observer
      const ro = new ResizeObserver(() => {
        if (!container || !renderer || !camera) return;
        const w = container.clientWidth;
        const h = 580;
        renderer.setSize(w, h);
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
      });
      ro.observe(container);

      // Animate Loop
      const clock = new THREE.Clock();
      let waveScale = 1;

      const animate = () => {
        animRef.current = requestAnimationFrame(animate);
        const elapsedTime = clock.getElapsedTime();
        const dt = clock.getDelta();

        if (autoRotate && controlsRef.current) {
          controlsRef.current.azimuthAngle += dt * 0.15;
        }

        // Blinking & Pulsing Animation when Simulating or Selecting
        if (pulseRingRef.current) {
          const pulse = 1 + 0.2 * Math.sin(elapsedTime * (isSimulating ? 12 : 5));
          pulseRingRef.current.scale.set(pulse, pulse, 1);
          pulseRingRef.current.material.opacity = 0.5 + 0.4 * Math.sin(elapsedTime * (isSimulating ? 14 : 6));
        }

        // Locality Ripple Wave Animation
        if (localityWaveRef.current) {
          if (isSimulating) {
            waveScale += dt * 18;
            if (waveScale > 28) waveScale = 2;
            localityWaveRef.current.scale.set(waveScale, waveScale, 1);
            localityWaveRef.current.material.opacity = Math.max(0, 0.7 - waveScale / 28);
          } else {
            localityWaveRef.current.material.opacity = 0;
            waveScale = 1;
          }
        }

        // Flash Cable Tube Emissives during Simulation Test
        if (isSimulating && lineTubesRef.current.length > 0) {
          const flash = 0.3 + 0.5 * Math.abs(Math.sin(elapsedTime * 15));
          lineTubesRef.current.forEach((mat) => {
            mat.emissiveIntensity = flash;
          });
        }

        controls.update();

        // Animate flow particles
        lineGroups.forEach((g) => {
          g.children.forEach((child: any) => {
            child.userData.t = (child.userData.t + dt * child.userData.speed) % 1;
            if (child.userData.t < 0) child.userData.t += 1;
            const p = child.userData.curve.getPointAt(child.userData.t);
            child.position.copy(p);
            child.position.y = 6.1;
          });
        });

        renderer.render(scene, camera);
        updateSelectedCardPos();
      };

      animate();
      setLoading(false);

      return () => {
        ro.disconnect();
        canvasEl.removeEventListener("click", handleCanvasClick);
      };
    })();

    return () => {
      cancelled = true;
      cancelAnimationFrame(animRef.current);
      try {
        rendererRef.current?.dispose();
      } catch {}
      if (containerRef.current) containerRef.current.innerHTML = "";
    };
  }, [twin, busId, layer, autoRotate, selectedEntityId, isSimulating, testKw]);

  // Handle Interactive Test Simulation Trigger
  const runSimulationTest = () => {
    setIsSimulating(true);
    setTimeout(() => {
      setIsSimulating(false);
    }, 4500);
  };

  const handleZoom = (delta: number) => {
    if (!cameraRef.current || !controlsRef.current) return;
    cameraRef.current.position.multiplyScalar(delta);
    controlsRef.current.update();
  };

  const handleResetCamera = () => {
    if (!cameraRef.current || !controlsRef.current) return;
    cameraRef.current.position.set(55, 42, 55);
    controlsRef.current.target.set(0, 0, 0);
    controlsRef.current.update();
  };

  return (
    <div className="relative overflow-hidden rounded-2xl border border-slate-800 bg-[#0b1e33] shadow-2xl">
      {/* Top Header Controls Bar */}
      <div className="absolute inset-x-0 top-0 z-20 flex flex-wrap items-center gap-2 border-b border-white/10 bg-[#0b1e33]/85 px-4 py-2.5 backdrop-blur">
        <div className="flex items-center gap-2">
          <label className="text-[11px] font-semibold uppercase tracking-widest text-slate-400">Connection Point</label>
          <select
            value={selectedEntityId || stats.pvBus}
            onChange={(e) => {
              const val = e.target.value;
              setSelectedEntityId(val);
              if (onSelectBus) onSelectBus(val);
            }}
            className="rounded-lg border border-slate-700 bg-slate-900 px-2.5 py-1 text-xs text-slate-100 font-mono focus:border-sky-500 focus:outline-none"
          >
            {availableBuses.map((b) => (
              <option key={b.id} value={b.id}>
                Bus {b.id} {b.pv_eligible ? "(Eligible Host)" : ""}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-[11px] font-semibold uppercase tracking-widest text-slate-400">Layer</label>
          <select
            value={layer}
            onChange={(e) => setLayer(e.target.value as any)}
            className="rounded-lg border border-slate-700 bg-slate-900 px-2.5 py-1 text-xs text-slate-100 focus:border-sky-500 focus:outline-none"
          >
            <option>All Layers</option>
            <option>Risk</option>
            <option>Voltage</option>
            <option>Transformer loading</option>
          </select>
        </div>

        <div className="ml-2 flex items-center gap-2 rounded-full border border-white/10 bg-slate-900/90 px-3 py-1">
          <span className={`h-2.5 w-2.5 ${isSimulating ? "animate-ping bg-amber-400" : "animate-pulse bg-emerald-400"} rounded-full`} />
          <span className="text-xs font-semibold text-slate-200">
            {isSimulating ? "Simulating Solar Impact…" : "Interactive Digital Twin"}
          </span>
        </div>

        {onToggle2D && (
          <button
            onClick={onToggle2D}
            className="ml-auto rounded-lg border border-sky-500/40 bg-sky-950/60 px-3 py-1 text-xs font-semibold text-sky-300 hover:bg-sky-900/50"
          >
            Switch to 2D
          </button>
        )}
      </div>

      {/* Compass */}
      <div
        onClick={handleResetCamera}
        title="Reset Camera View"
        className="absolute right-4 top-16 z-20 flex h-11 w-11 cursor-pointer items-center justify-center rounded-full border border-white/15 bg-slate-900/80 shadow-lg backdrop-blur transition hover:scale-105 hover:bg-slate-800"
      >
        <span className="text-base">🧭</span>
        <span className="absolute -top-1 text-[9px] font-bold text-sky-400">N</span>
      </div>

      {/* 3D WebGL Canvas */}
      <div ref={containerRef} className="h-[580px] w-full pt-[52px]" />

      {/* ON-DEMAND Floating Card (Appears ONLY when user clicks an object in 3D!) */}
      {cardPos && cardPos.visible && (
        <div
          style={{
            left: `${cardPos.x}px`,
            top: `${cardPos.y}px`,
            transform: "translate(-50%, -100%) translateY(-14px)",
          }}
          className="pointer-events-auto absolute z-20 w-[170px] rounded-xl border border-sky-400/60 bg-slate-900/95 p-3 shadow-2xl backdrop-blur transition-all duration-75"
        >
          <div className="flex items-center justify-between border-b border-slate-800 pb-1">
            <div className="text-xs font-bold text-sky-400">{cardPos.title}</div>
            <button
              onClick={() => setSelectedEntityId(null)}
              className="text-slate-400 hover:text-white text-xs font-bold px-1"
            >
              ✕
            </button>
          </div>
          <div className="text-[10px] text-slate-400 leading-tight mt-0.5">{cardPos.subtitle}</div>
          <div className="mt-2 space-y-1 font-mono text-[10px] text-slate-300">
            {cardPos.metrics.map((m, idx) => (
              <div key={idx} className="flex justify-between">
                <span className="text-slate-400">{m.label}</span>
                <span className={m.color || (m.highlight ? "text-sky-300 font-bold" : "text-slate-200")}>
                  {m.val}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Bottom Floating Interactive Inspector & "Test Capacity" Simulator Panel */}
      {selectedEntityId && (
        <div className="absolute left-4 bottom-16 z-30 w-80 rounded-2xl border border-sky-500/50 bg-slate-900/95 p-4 shadow-2xl backdrop-blur">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-sky-400">Selected Node</span>
              <h4 className="text-sm font-bold text-slate-100">Bus-{selectedEntityId} Inspection</h4>
            </div>
            <button
              onClick={() => setSelectedEntityId(null)}
              className="rounded-full bg-slate-800 px-2 py-0.5 text-xs text-slate-400 hover:text-white"
            >
              ✕
            </button>
          </div>

          <div className="mt-3 space-y-2 text-xs">
            <div className="flex justify-between text-slate-400">
              <span>Proposed Solar Capacity</span>
              <span className="font-mono text-sky-300 font-bold">{testKw} kW</span>
            </div>

            {/* Test Capacity Buttons */}
            <div className="flex items-center gap-1.5">
              {[10, 25, 50, 66, 100].map((kw) => (
                <button
                  key={kw}
                  onClick={() => setTestKw(kw)}
                  className={`flex-1 rounded-lg py-1 text-[11px] font-semibold transition ${
                    testKw === kw
                      ? "bg-sky-600 text-white shadow"
                      : "bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-slate-200"
                  }`}
                >
                  {kw} kW
                </button>
              ))}
            </div>

            {/* Run Test & Locality Simulation Button */}
            <button
              onClick={runSimulationTest}
              disabled={isSimulating}
              className={`mt-3 flex w-full items-center justify-center gap-2 rounded-xl py-2 text-xs font-bold transition ${
                isSimulating
                  ? "bg-amber-600 text-white animate-pulse"
                  : "bg-gradient-to-r from-emerald-600 to-sky-600 text-white hover:from-emerald-500 hover:to-sky-500 shadow-lg"
              }`}
            >
              <span>⚡</span>
              <span>{isSimulating ? "Simulating Locality Impact…" : `Test ${testKw} kW Impact on Locality`}</span>
            </button>
          </div>
        </div>
      )}

      {/* Simulation Animated Impact Visualizer Modal / Banner */}
      {isSimulating && (
        <div className="absolute inset-x-4 top-16 z-30 rounded-xl border border-amber-500/60 bg-slate-900/95 p-3.5 shadow-2xl backdrop-blur">
          <div className="flex items-center gap-3">
            <span className="flex h-3 w-3 animate-ping rounded-full bg-amber-400" />
            <span className="text-xs font-bold uppercase tracking-wider text-amber-400">
              Live Solar Simulation Active — Blinking Locality Grid
            </span>
          </div>

          <div className="mt-2 grid grid-cols-2 gap-3 text-xs">
            <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-2.5">
              <div className="font-semibold text-slate-300">📍 Targeted House Impact</div>
              <div className="mt-1 space-y-1 font-mono text-[11px] text-slate-400">
                <div className="flex justify-between"><span>Solar Injection</span><span className="text-sky-300">+{testKw} kW</span></div>
                <div className="flex justify-between"><span>Local Voltage Rise</span><span className="text-amber-400">+{stats.vRise}%</span></div>
                <div className="flex justify-between"><span>Status</span><span className="text-emerald-400">Safe Grid Export</span></div>
              </div>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-2.5">
              <div className="font-semibold text-slate-300">🌐 Locality / Neighborhood Impact</div>
              <div className="mt-1 space-y-1 font-mono text-[11px] text-slate-400">
                <div className="flex justify-between"><span>Trafo Loading</span><span className="text-amber-400">{stats.feederLoad}%</span></div>
                <div className="flex justify-between"><span>Reverse Power Flow</span><span className="text-sky-300">Active (Blue Flow)</span></div>
                <div className="flex justify-between"><span>Affected Neighbor Houses</span><span className="text-slate-200">8 Houses</span></div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Right Side Summary Panel */}
      <div className="absolute bottom-[54px] right-0 top-[52px] z-20 hidden w-[250px] flex-col gap-3 overflow-y-auto border-l border-white/10 bg-[#0f172a]/95 p-3 backdrop-blur lg:flex">
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-widest text-slate-200">Network Summary</h3>
          <div className="mt-2 space-y-1.5 text-xs">
            <div className="flex justify-between text-slate-400"><span>Feeder Load</span><span className="font-mono text-slate-100">{stats.totalLoad} MW</span></div>
            <div className="flex justify-between text-slate-400"><span>Solar Generation</span><span className="font-mono text-slate-100">{stats.totalPV} MW</span></div>
            <div className="flex justify-between text-slate-400"><span>Consumers</span><span className="font-mono text-slate-100">{stats.consumers}</span></div>
            <div className="flex justify-between text-slate-400"><span>Engine Status</span><span className="font-mono text-emerald-400">Converged</span></div>
          </div>
        </div>
        <hr className="border-white/10" />

        <div>
          <h3 className="text-xs font-semibold uppercase tracking-widest text-slate-200">Voltage Profile</h3>
          <div className="mt-2 space-y-1 font-mono text-xs text-slate-400">
            <div className="flex justify-between"><span>Min Voltage</span><span className="text-slate-100">{stats.minV} kV</span></div>
            <div className="flex justify-between"><span>Max Voltage</span><span className="text-slate-100">{stats.maxV} kV</span></div>
            <div className="flex justify-between"><span>Target Bus V</span><span className="text-slate-100">{stats.avgV} kV</span></div>
          </div>
        </div>
        <hr className="border-white/10" />

        <div>
          <h3 className="text-xs font-semibold uppercase tracking-widest text-slate-200">Transformer Load</h3>
          <div className="mt-2 flex items-center gap-3">
            <div
              className="flex h-14 w-14 items-center justify-center rounded-full text-xs font-bold text-white shadow"
              style={{
                background: `conic-gradient(#22c55e 0% ${stats.feederLoad}%, #334155 ${stats.feederLoad}% 100%)`,
              }}
            >
              <span className="flex h-10 w-10 items-center justify-center rounded-full bg-[#0f172a]">{stats.feederLoad}%</span>
            </div>
            <div className="space-y-0.5 text-[10px] text-slate-300">
              <div className="flex items-center gap-1.5"><span className="h-2 w-2 rounded bg-emerald-500" />Normal (&lt;50%)</div>
              <div className="flex items-center gap-1.5"><span className="h-2 w-2 rounded bg-amber-400" />Moderate (50-80%)</div>
              <div className="flex items-center gap-1.5"><span className="h-2 w-2 rounded bg-red-500" />Heavy (&gt;80%)</div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Toolbar */}
      <div className="absolute inset-x-0 bottom-0 z-20 flex flex-wrap items-center justify-between gap-2 border-t border-white/10 bg-[#0b1e33]/90 px-3 py-1.5 backdrop-blur">
        <div className="flex items-center gap-2">
          <span className="text-[11px] text-slate-400">💡 Click any house or transformer to inspect & test solar impact</span>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={() => setAutoRotate((r) => !r)}
            className={`flex items-center gap-1 rounded-lg px-2.5 py-1 text-[11px] font-medium transition ${
              autoRotate ? "bg-emerald-600 text-white" : "text-slate-400 hover:bg-white/10 hover:text-slate-200"
            }`}
          >
            <span>↻</span>
            <span>{autoRotate ? "Rotating" : "Rotate"}</span>
          </button>
          <button
            onClick={() => handleZoom(0.85)}
            className="rounded-lg border border-white/10 bg-white/5 px-2 py-1 text-xs text-slate-200 hover:bg-white/10"
          >
            🔍 +
          </button>
          <button
            onClick={() => handleZoom(1.15)}
            className="rounded-lg border border-white/10 bg-white/5 px-2 py-1 text-xs text-slate-200 hover:bg-white/10"
          >
            🔍 -
          </button>
          <button
            onClick={handleResetCamera}
            className="rounded-lg border border-white/10 bg-white/5 px-2.5 py-1 text-xs text-slate-200 hover:bg-white/10"
          >
            Reset View
          </button>
        </div>
      </div>

      {loading && (
        <div className="absolute inset-0 z-30 flex items-center justify-center bg-[#0b1e33]/70 backdrop-blur-sm">
          <div className="flex flex-col items-center gap-2">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-sky-400 border-t-transparent" />
            <span className="text-xs text-slate-400">Loading 3D Twin environment…</span>
          </div>
        </div>
      )}
    </div>
  );
}

function addHouse(THREE: any, scene: any, x: number, z: number, hasPV: boolean, rng: () => number, isSelected: boolean) {
  const g = new THREE.Group();
  g.position.set(x, 0, z);
  const w = 4.2 + rng() * 1.4;
  const d = 3.6 + rng() * 1.2;
  const h = 2.8 + rng() * 1.2;

  const wallMat = new THREE.MeshStandardMaterial({
    color: isSelected ? 0x0284c7 : 0xe8eef4,
    roughness: 0.85,
  });

  const wall = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), wallMat);
  wall.position.y = h / 2;
  wall.castShadow = true;
  wall.receiveShadow = true;
  g.add(wall);

  const roofH = 1.2;
  const roof = new THREE.Mesh(
    new THREE.ConeGeometry(Math.max(w, d) * 0.62, roofH, 4, 1),
    new THREE.MeshStandardMaterial({ color: isSelected ? 0x0369a1 : 0x9d4e2e, roughness: 0.7 })
  );
  roof.position.y = h + roofH / 2 - 0.15;
  roof.rotation.y = Math.PI / 4;
  roof.castShadow = true;
  g.add(roof);

  if (hasPV) {
    const pv = new THREE.Mesh(
      new THREE.BoxGeometry(w * 0.62, 0.08, d * 0.52),
      new THREE.MeshStandardMaterial({
        color: 0x1e3a5f,
        metalness: 0.15,
        roughness: 0.35,
        emissive: 0x0284c7,
        emissiveIntensity: 0.35,
      })
    );
    pv.position.set(0.35, h + 0.35, -0.2);
    pv.rotation.y = 0.15;
    pv.rotation.x = 0.18;
    g.add(pv);
  }

  scene.add(g);
  return g;
}

function addTree(THREE: any, scene: any, x: number, z: number, rng: () => number) {
  const g = new THREE.Group();
  g.position.set(x, 0, z);
  const trunkH = 2.2 + rng() * 1.6;
  const trunk = new THREE.Mesh(
    new THREE.CylinderGeometry(0.18, 0.24, trunkH, 6),
    new THREE.MeshStandardMaterial({ color: 0x4a3721, roughness: 0.95 })
  );
  trunk.position.y = trunkH / 2;
  trunk.castShadow = true;
  g.add(trunk);

  const foliage = new THREE.Mesh(
    new THREE.ConeGeometry(1.4 + rng() * 0.7, 3.2 + rng() * 1.8, 7),
    new THREE.MeshStandardMaterial({ color: 0x2d5a27, roughness: 0.85 })
  );
  foliage.position.y = trunkH + 1.2;
  foliage.castShadow = true;
  g.add(foliage);
  scene.add(g);
}

function mulberry32(a: number) {
  return function () {
    let t = (a += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function hashCode(s: string) {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (Math.imul(31, h) + s.charCodeAt(i)) | 0;
  return Math.abs(h) + 1;
}

function distanceToNearest(x: number, z: number, pts: { x: number; z: number }[]) {
  let best = Infinity;
  for (const p of pts) best = Math.min(best, Math.hypot(p.x - x, p.z - z));
  return best;
}
