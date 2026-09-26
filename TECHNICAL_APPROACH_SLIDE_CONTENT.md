# Technical Approach Slide Content — SolarGrid AI

> **SIH 2026 Presentation Slide Specification**  
> *1-Sentence Evaluator Summary*: SolarGrid AI evaluates rooftop solar connection requests in milliseconds using a 18-feature Random Forest ML pre-screener, then verifies physical grid compliance with a deterministic pandapower Newton-Raphson power flow engine, serving a 2D/3D digital twin and multi-stakeholder DISCOM workflow.

---

## SLIDE HEADER
- **Title**: TECHNICAL APPROACH & SYSTEM ARCHITECTURE
- **Subtitle**: SolarGrid AI — Physics-First Rooftop Solar Hosting Capacity Screening & Grid Integration Platform
- **Badge**: Smart India Hackathon 2026 | Problem Statement: Distribution Utility Grid Stability

---

## SECTION 1 — INPUT DATA & GRID INGESTION
- **Header**: 1. INPUT DATA & GRID ASSETS
- **Sub-box 1**: Consumer Request Inputs
  - Solar Capacity (`new_pv_kw`, `existing_pv_kw`)
  - Target Bus ID (`pv_bus`) & Geographical Location
- **Sub-box 2**: Distribution Grid Network Model
  - IEEE Comprehensive Test Feeder (`feeder_network.json`)
  - 114 Buses · 40 Lines · 30 Transformers · 4.16/12.47 kV
- **Sub-box 3**: Pre-computed Asset Features
  - `electrical_features.csv` & `valid_pv_buses.csv`
  - Upstream Impedance ($R, X, Z$), Distances, Base Load

---

## SECTION 2 — PRE-SCREENING & DUAL EVALUATION (HERO SECTION - CORE INNOVATION)
- **Header**: 2. AI PRE-SCREEN & DETERMINISTIC PHYSICS VERIFICATION ENGINE
- **Sub-box A**: Fast ML Pre-screening Layer (Milliseconds)
  - Model: `suryagrid_model_v2.pkl` (Random Forest, 18 Features)
  - Inputs: Bus ID, Solar kW, Transformer kVA, Impedances, Penetration Ratios
  - Outputs: `SAFE` / `CAUTION` / `CONSTRAINED` + Confidence Probabilities
- **Sub-box B**: Deterministic Power Flow Physics Engine (Authority)
  - Solver: `pandapower` (Newton-Raphson, 50 ms execution)
  - Method: `BASE` (existing PV) vs. `PV` (existing + new) Differential Analysis
  - Measurements: $V_{\min}, V_{\max}$, Bus Voltage Rise ($\Delta V$), Line & Trafo Loading, Reverse Flow
- **Sub-box C**: Domain Risk Assessment & Discrepancy Gate
  - Threshold Rules: Hard limits ($V_{\max} > 1.05\text{ pu}, V_{\min} < 0.90\text{ pu}, \Delta V > 0.05\text{ pu}, \text{Loading} > 100\%$)
  - Rule: **Physics Decides** — ML pre-screen never overrides power flow. Disagreements explicitly flagged (`ml_agrees_with_engineering = false`).

---

## SECTION 3 — SIDE FLOW: BISECTION HOSTING CAPACITY & DIGITAL TWIN
- **Header**: 3. CAPACITY ENGINE & DIGITAL TWIN VISUALISATION
- **Sub-box 1**: Hosting Capacity Solver
  - Binary Bisection Search (~11 power flow solves per bus)
  - Evaluates both Per-Bus Capacity & Simultaneous Feeder Section Limit
- **Sub-box 2**: Interactive 2D/3D Grid Digital Twin
  - 2D Single Line Diagram (`TwinDiagram.tsx` via Network Graph)
  - 3D Geospatial Digital Twin (`GridTwin3D.tsx` via CesiumJS)
- **Sub-box 3**: Multi-Agent AI Grid Assistant
  - NVIDIA NIM LLM Assistant grounded in power-flow tool context

---

## SECTION 4 — APPLICATION & SERVICE LAYER
- **Header**: 4. REST API & SECURE STORAGE
- **Sub-box 1**: FastAPI Service Layer
  - 51 REST Endpoints (`/api/assess`, `/api/applications`, `/api/twin`)
  - Role-Based Access Control (`require_discom`, `require_vendor`)
- **Sub-box 2**: Security & Database (Supabase)
  - 13 Postgres Tables + 29 Row Level Security (RLS) Policies
  - Zero-Client-Write Security on Engineering Verdicts

---

## SECTION 5 — MULTI-STAKEHOLDER PORTALS & OUTPUTS
- **Header**: 5. USER PORTALS & FINAL OUTPUTS
- **Sub-box 1**: Citizen Portal
  - Solar Feasibility Pre-screen · Application Tracker · PM Surya Ghar Subsidy Estimator
- **Sub-box 2**: DISCOM Control Room
  - Engineering Review Queue · 2D/3D Grid Twin · What-If Simulator · Hosting Capacity Map
- **Sub-box 3**: Vendor & Verification Portal
  - Lead Management · Site Visit Scheduler · Photographic Proof Completion Filing

---

## SECTION 6 — FUTURE / PLANNED EXTENSIONS (VISUALLY DEMARCATED)
- **Header**: 6. PLANNED SCADA & SMART METER EXTENSIONS [FUTURE MODULES]
- **Items**:
  - Live DISCOM SCADA & AMI Smart Meter Feed Ingestion
  - Dynamic Time-Series Seasonal Load Profiles
  - Satellite Irradiance Telemetry Integration (GEE / CAMS)

---

## BOTTOM PANEL — TECHNOLOGY STACK
- **AI / ML**: Scikit-Learn 1.3.2 · Random Forest · NumPy · Pandas · NVIDIA NIM LLM
- **Physics & Grid Engine**: pandapower 3.4.0 · Newton-Raphson · NetworkX · IEEE Test Feeder
- **Backend & Storage**: FastAPI · Python 3.12 · Supabase Postgres · Row Level Security (RLS)
- **Frontend & Visualisation**: Next.js 14 · React 18 · TypeScript · CesiumJS (3D) · Leaflet (2D) · Recharts
- **DevOps & Deployment**: Docker · Docker Compose · Render
