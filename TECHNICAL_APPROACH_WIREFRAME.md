# Technical Approach Wireframe — SolarGrid AI

> **16:9 Presentation Architecture Wireframe for SIH 2026**

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  TECHNICAL APPROACH & SYSTEM ARCHITECTURE — SolarGrid AI                                   [SIH 2026 TOP SLIDE]      │
│  Physics-First Rooftop Solar Hosting Capacity Screening & Grid Integration Platform                                   │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                        │
│ ┌──────────────────────┐   ┌──────────────────────────────────────────────────┐   ┌──────────────────────────────────┐ │
│ │ 1. INPUT DATA & GRID │   │ 2. AI PRE-SCREEN & PHYSICS ENGINE (HERO)         │   │ 3. HOSTING CAPACITY & 3D TWIN    │ │
│ ├──────────────────────┤   ├──────────────────────────────────────────────────┤   ├──────────────────────────────────┤ │
│ │                      │   │  ┌────────────────────────────────────────────┐  │   │  ┌────────────────────────────┐  │ │
│ │ • Consumer Request   │───┼─►│ Fast ML Pre-screening Layer (Random Forest)  │  │───┼─►│ Bisection Hosting Capacity │  │ │
│ │   - Bus ID & Location│   │  │ 18 Features → SAFE / CAUTION / CONSTRAINED │  │   │  │ Solves ~11 PF runs per bus │  │ │
│ │   - New Solar kW     │   │  └─────────────────────┬──────────────────────┘  │   │  └──────────────┬─────────────┘  │ │
│ │                      │   │                        │ (Pre-screen verdict)    │   │                 │                │ │
│ │ • IEEE Feeder Model  │   │                        ▼                         │   │                 ▼                │ │
│ │   - IEEE 114-Bus     │   │  ┌────────────────────────────────────────────┐  │   │  ┌────────────────────────────┐  │ │
│ │   - 40 Lines, 30 Tr  │───┼─►│ pandapower Deterministic Physics Engine   │  │───┼─►│ 2D/3D Digital Grid Twin    │  │ │
│ │                      │   │  │ BASE vs. PV Case Newton-Raphson Solver   │  │   │  │ Cesium 3D + 2D Topology    │  │ │
│ │ • Asset Features     │   │  └─────────────────────┬──────────────────────┘  │   │  └──────────────┬─────────────┘  │ │
│ │   - Upstream R/X/Z   │   │                        │ (Exact V, Rise, Loading)│   │                 │                │ │
│ │   - Base Load & kVA  │   │                        ▼                         │   │                 ▼                │ │
│ │                      │   │  ┌────────────────────────────────────────────┐  │   │  ┌────────────────────────────┐  │ │
│ │                      │   │  │ Domain Risk Assessment & Discrepancy Gate  │  │   │  │ Multi-Agent AI Assistant   │  │ │
│ │                      │   │  │ scenario_config.json Rules (Physics Decides)│  │   │  │ NVIDIA NIM + Grid Telemetry│  │ │
│ └──────────────────────┘   │  └────────────────────────────────────────────┘  │   │  └────────────────────────────┘  │ │
│                            └────────────────────────┬─────────────────────────┘   └──────────────────────────────────┘ │
│                                                     │                                                                  │
│                                                     ▼                                                                  │
│                            ┌──────────────────────────────────────────────────┐                                        │
│                            │ 4. REST API & SECURE STORAGE LAYER               │                                        │
│                            ├──────────────────────────────────────────────────┤                                        │
│                            │ • FastAPI Backend (51 Endpoints, Python 3.12)    │                                        │
│                            │ • Supabase Postgres (13 Tables, 29 RLS Policies) │                                        │
│                            │ • Zero-Client-Write Security on Risk Verdicts    │                                        │
│                            └────────────────────────┬─────────────────────────┘                                        │
│                                                     │                                                                  │
│                                                     ▼                                                                  │
│ ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ 5. MULTI-STAKEHOLDER PORTALS & FINAL OUTPUTS                                                                       │ │
│ ├──────────────────────────────────────┬──────────────────────────────────────┬──────────────────────────────────────┤ │
│ │ CITIZEN PORTAL                       │ DISCOM CONTROL ROOM                  │ VENDOR PORTAL                        │ │
│ │ • Instant Solar Feasibility Check    │ • Application Review Queue           │ • Verified Lead Management           │ │
│ │ • Application Status Tracker         │ • 2D / 3D Grid Twin & What-If        │ • Site Visit Scheduler               │ │
│ │ • PM Surya Ghar Subsidy Estimator    │ • Hosting Capacity Heatmaps          │ • Photographic Proof Completion      │ │
│ └──────────────────────────────────────┴──────────────────────────────────────┴──────────────────────────────────────┘ │
│                                                                                                                        │
│ ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ 6. PLANNED SCADA & SMART METER EXTENSIONS [FUTURE MODULES]                                                         │ │
│ │ • Live SCADA / AMI Ingestion   • Time-Series Seasonal Load Profiles   • Satellite Irradiance Telemetry (GEE/CAMS)     │ │
│ └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                                                        │
│ ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ TECH STACK                                                                                                         │ │
│ │ AI/ML: Scikit-Learn (Random Forest) · NVIDIA NIM | Physics: pandapower (Newton-Raphson) · IEEE Test Feeder          │ │
│ │ Backend: FastAPI · Python 3.12 · Supabase Postgres (RLS) | Frontend: Next.js 14 · React 18 · CesiumJS 3D · Leaflet  │ │
│ └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
