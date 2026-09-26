# Technical Architecture Audit — SolarGrid AI

> **Smart India Hackathon (SIH) 2026 — Evidence-Based System Verification**  
> *Primary Source of Truth: Repository Source Code & Validated Artifacts*

---

## 1. Project Objective
SolarGrid AI is a full-stack, enterprise-grade distribution utility solution for pre-screening, evaluating, and managing rooftop solar grid integration under initiatives like **PM Surya Ghar Muft Bijli Yojana**. It resolves the conflict between rapid consumer solar adoption and power distribution grid stability.

When a citizen submits a rooftop solar connection request:
1. A Machine Learning model pre-screens the request in **milliseconds** across 18 grid and asset features.
2. A deterministic **pandapower** power flow simulates exact physical grid impact (voltage rise, line loading, transformer loading, reverse power flow) in **~50 ms**.
3. **Physics Decides**: The power-flow result governs the verdict (`SAFE`, `CAUTION`, `CONSTRAINED`). If the ML pre-screen disagrees, the discrepancy is flagged explicitly for DISCOM engineers.

---

## 2. Actual End-to-End Pipeline

```
[Citizen / DISCOM Request]
          │
          ▼
[Input Assembly & Data Harmonisation]
 (Feeder DB + CSV + Request Params)
          │
  ┌───────┴─────────────────────────────────┐
  │                                         │
  ▼                                         ▼
[ML Pre-Screening Layer]           [Deterministic Physics Engine]
 (Random Forest, 18 Features)       (pandapower Newton-Raphson)
 (suryagrid_model_v2.pkl)           (BASE vs. PV Power Flow)
  │                                         │
  │ ML Risk & Probabilities                 │ Physical Metrics (Vmin/max, Rise, Loading)
  └───────────────┬─────────────────────────┘
                  │
                  ▼
   [Domain Risk Verdict Engine]
    (scenario_config.json Thresholds)
    - CONSTRAINED: Hard limits exceeded
    - CAUTION: Caution bands / Reverse flow
    - SAFE: All metrics normal
                  │
  ┌───────────────┼─────────────────────────┐
  │               │                         │
  ▼               ▼                         ▼
[Bisection      [2D / 3D Grid            [DISCOM & Vendor
 Hosting Cap]   Digital Twin]            Workflow Engine]
(Max PV kW)     (Cesium3D & Leaflet)     (Approvals & Verification)
```

---

## 3. Data Sources & Physical Feeder Base
- **IEEE Comprehensive Test Feeder**:
  - File: `feeder_network.json` (114 buses, 40 lines, 30 transformers, 1 substation, voltage 4.16 kV / 12.47 kV).
  - Verification script: `build_feeder.py` (validated against IEEE PES Distribution Systems Analysis Subcommittee published reference).
- **Eligible PV Buses Dataset**: `valid_pv_buses.csv` (71 PV-eligible buses with feeder distances, sections, and transformer associations).
- **Electrical Asset Features**: `electrical_features.csv` (Upstream $R, X, Z$ impedances, nominal voltages, transformer rated kVA, base load kW).
- **Synthetic Geographic Layout**: Distances between grid assets are physically exact in km; absolute map placement is synthetic/illustrative for demonstration (`docs/ARCHITECTURE.md`).

---

## 4. Preprocessing & Feature Engineering
- **18-Feature Vector Assembly**: Implemented in `MLPredictionService.build_features()` ([`backend/app/services/ml_prediction.py`](file:///c:/Users/ASUS/Documents/sih26/backend/app/services/ml_prediction.py#L107-L141)):
  1. `pv_bus`: Integer-casted bus ID (matches fitted `OneHotEncoder`).
  2. `existing_pv_kw`: Existing solar generation on bus.
  3. `new_pv_kw`: Requested new solar capacity.
  4. `total_pv_kw`: Combined solar capacity (`existing + new`).
  5. `pv_bus_vn_kv`: Nominal voltage rating (kV).
  6. `existing_load_at_bus_kw`: Baseline load at bus.
  7. `transformer_association`: Associated distribution transformer ID.
  8. `feeder_section`: Feeder section grouping.
  9. `transformer_sn_kva`: Rated transformer apparent power (kVA).
  10. `base_voltage_pu`: Baseline voltage without solar injection (pu).
  11. `feeder_distance_km`: Distance along feeder from substation (km).
  12. `upstream_r_ohm`: Cumulative upstream resistance ($\Omega$).
  13. `upstream_x_ohm`: Cumulative upstream reactance ($\Omega$).
  14. `upstream_z_ohm`: Cumulative upstream impedance ($\Omega$).
  15. `pv_penetration_ratio`: `total_pv_kw / existing_load_at_bus_kw` (or `total_pv_kw / 1.0` for 0-load bus).
  16. `pv_to_transformer_ratio`: `total_pv_kw / transformer_sn_kva`.
  17. `new_pv_to_transformer_ratio`: `new_pv_kw / transformer_sn_kva`.
  18. `load_to_transformer_ratio`: `existing_load_at_bus_kw / transformer_sn_kva`.
- **Zero Leakage**: No power-flow output (voltage, loading) is used in ML features.

---

## 5. Model Architecture & Training Workflow
- **Model Classifier**: Scikit-learn Pipeline containing `OneHotEncoder(handle_unknown="ignore")` + `StandardScaler` + `RandomForestClassifier`.
- **Model Checkpoint**: `suryagrid_model_v2.pkl` (scikit-learn 1.3.2 pin, 18 input features).
- **Training Script**: `train_ml_v2.py` trained on 1,692 simulated scenarios (`pv_dataset_enriched_augmented.csv`).
- **Pre-screen Performance**: 97.6% test accuracy on 254-row test set (`ml_dataset_test_enriched.csv`).

---

## 6. Deterministic Physics Engine & Power Flow
- **Engine**: `pandapower 3.4.0` with Newton-Raphson solver ([`backend/app/services/power_flow.py`](file:///c:/Users/ASUS/Documents/sih26/backend/app/services/power_flow.py)).
- **Dual-State Evaluation**:
  - `BASE` case: Feeder + existing solar generation.
  - `PV` case: Feeder + existing solar + proposed new solar injection.
  - `Delta`: Differential analysis between PV and BASE states.
- **Physical Metrics Extracted**:
  - Feeder Min/Max Voltages ($V_{\min}, V_{\max}$ in per-unit `pu`).
  - Target Bus Voltage Rise ($\Delta V_{\text{rise}}$ in `pu`).
  - Max Line Loading (%) & Worst Line ID.
  - Max Transformer Loading (%) & Worst Transformer ID.
  - Active Power Losses ($P_{\text{loss}}$ in kW) & $\Delta P_{\text{loss}}$.
  - Reverse Power Flow ($P < 0$ returning to substation).

---

## 7. Domain Risk Verdict & Threshold Rules
- **Rule Engine**: `RiskAssessmentService` ([`backend/app/services/risk_assessment.py`](file:///c:/Users/ASUS/Documents/sih26/backend/app/services/risk_assessment.py)).
- **Configuration Source**: `scenario_config.json`.
- **Decision Hierarchy**:
  - **CONSTRAINED (Hard Violation, First Match Wins)**:
    - $V_{\max} > 1.05\text{ pu}$
    - $V_{\min} < 0.90\text{ pu}$
    - $|\Delta V_{\text{rise}}| > 0.05\text{ pu}$
    - Line loading $> 100\%$
    - Transformer loading $> 100\%$
  - **CAUTION (Caution Band Violation)**:
    - $V_{\max} > 1.03\text{ pu}$
    - $V_{\min} < 0.90\text{ pu}$
    - $|\Delta V_{\text{rise}}| \ge 0.03\text{ pu}$
    - Line loading $\ge 80\%$
    - Transformer loading $\ge 95\%$
    - Reverse Power Flow detected
  - **SAFE**: All metrics within safe engineering envelopes.

---

## 8. Side Flows & Advanced Algorithms
1. **Hosting Capacity Bisection Engine**:
   - Implemented in `HostingCapacityService` ([`backend/app/services/hosting_capacity.py`](file:///c:/Users/ASUS/Documents/sih26/backend/app/services/hosting_capacity.py)).
   - Binary bisection search over 10-12 power flow solves per bus to find exact maximum allowable PV kW before tripping constraints.
   - Evaluates both **Per-Bus Capacity** and **Simultaneous Feeder-Section Capacity** (prevents overestimating grid limits by up to 23×).
2. **2D & 3D Grid Digital Twin**:
   - 2D Single-Line Topology Graph: `TopologyService` ([`backend/app/services/topology.py`](file:///c:/Users/ASUS/Documents/sih26/backend/app/services/topology.py)) + `TwinDiagram.tsx`. Uses exact electrical connectivity (`respect_switches=True`).
   - 3D Geospatial Digital Twin: `GridTwin3D.tsx` (CesiumJS 3D viewer with camera animations, bus voltage heatmaps, and asset telemetry).
3. **Multi-Agent AI Assistant**:
   - Implemented in `ai_assistant.py` ([`backend/app/services/ai_assistant.py`](file:///c:/Users/ASUS/Documents/sih26/backend/app/services/ai_assistant.py)) via NVIDIA NIM LLM.
   - Natural language assistant answering citizen and DISCOM questions using tool-call context from physics engine (never hallucinates electrical measurements).

---

## 9. Backend Architecture & Security
- **Framework**: FastAPI (Python 3.12) with 51 endpoints across 6 routers (`routes.py`, `routes_discom.py`, `routes_vendors.py`, `routes_vendor_portal.py`, `routes_assistant.py`, `routes_scheme.py`).
- **Security & Authorization**:
  - JWT Authentication via Supabase Auth.
  - Role-Based Access Control (RBAC): `require_discom`, `require_vendor`, `require_citizen`.
  - Postgres Row Level Security (RLS): 13 tables, 29 RLS policies.
  - Client Write Protection: `simulation_results` and `risk_assessments` have **zero client write policies**; written exclusively via server service-role key.

---

## 10. Frontend & Visualisation
- **Framework**: Next.js 14 (App Router), React 18, TypeScript, TailwindCSS.
- **Portals**:
  - **Citizen Portal**: Pre-screen application form, progress tracker, PM Surya Ghar subsidy estimator, local vendor discovery.
  - **DISCOM Control Room**: Application approval queue, power-flow detailed inspector, 2D/3D digital twin, hosting capacity heatmaps, what-if scenario simulator.
  - **Vendor Portal**: Lead management, site visit scheduler, completion report filing with photographic proof verification.

---

## 11. Implemented vs. Planned Feature Classification

### IMPLEMENTED
- IEEE Comprehensive Test Feeder network model & topology (`feeder_network.json`).
- 18-feature Random Forest ML pre-screening service (`suryagrid_model_v2.pkl`).
- Deterministic pandapower Newton-Raphson power flow engine (`PowerFlowService`).
- Configurable threshold domain risk assessment engine (`RiskAssessmentService`).
- Bisection hosting capacity solver for individual buses & feeder sections (`HostingCapacityService`).
- 2D single-line diagram graph digital twin (`TopologyService` + `TwinDiagram.tsx`).
- 3D CesiumJS geospatial grid digital twin (`GridTwin3D.tsx`).
- 2D GIS Leaflet interactive map (`GridMap.tsx`).
- 51 REST API routes with FastAPI + Pydantic validation.
- Supabase Postgres schema with 13 tables and 29 RLS security policies.
- Role-based portals for Citizen, DISCOM Engineer, and Installation Vendor.
- NVIDIA NIM powered natural language Grid Assistant (`ai_assistant.py`).
- PM Surya Ghar subsidy rate & CFA calculation service (`scheme.py`).

### PARTIALLY IMPLEMENTED
- Geographic bus coordinates (distances are real km; map coordinates are synthetic/illustrative).
- Vendor distance calculation (currently straight-line spatial distance).

### PLANNED / FUTURE WORK (Visually demarcated on slide)
- Real-time DISCOM SCADA / AMI Smart Meter telemetry ingestion.
- Multi-feeder dynamic switching & distribution automation.
- Time-series dynamic seasonal load profiles.
- Satellite automated solar irradiance feed (GEE / CAMS integration).

---

## 12. Supporting Evidence File Index
- Backend Entry & Router: [`backend/app/main.py`](file:///c:/Users/ASUS/Documents/sih26/backend/app/main.py), [`backend/app/api/routes.py`](file:///c:/Users/ASUS/Documents/sih26/backend/app/api/routes.py)
- ML Pre-screen Service: [`backend/app/services/ml_prediction.py`](file:///c:/Users/ASUS/Documents/sih26/backend/app/services/ml_prediction.py)
- Power Flow Service: [`backend/app/services/power_flow.py`](file:///c:/Users/ASUS/Documents/sih26/backend/app/services/power_flow.py)
- Risk Verdict Engine: [`backend/app/services/risk_assessment.py`](file:///c:/Users/ASUS/Documents/sih26/backend/app/services/risk_assessment.py)
- Hosting Capacity Service: [`backend/app/services/hosting_capacity.py`](file:///c:/Users/ASUS/Documents/sih26/backend/app/services/hosting_capacity.py)
- AI Grid Assistant: [`backend/app/services/ai_assistant.py`](file:///c:/Users/ASUS/Documents/sih26/backend/app/services/ai_assistant.py)
- Model Checkpoint: `suryagrid_model_v2.pkl`
- Threshold Configuration: `scenario_config.json`
- Database Schema & RLS: [`supabase/migrations/0001_initial_schema.sql`](file:///c:/Users/ASUS/Documents/sih26/supabase/migrations/0001_initial_schema.sql), `0002_rls_policies.sql`
- 3D Digital Twin Component: [`frontend/components/GridTwin3D.tsx`](file:///c:/Users/ASUS/Documents/sih26/frontend/components/GridTwin3D.tsx)
- 2D Single Line Diagram: [`frontend/components/TwinDiagram.tsx`](file:///c:/Users/ASUS/Documents/sih26/frontend/components/TwinDiagram.tsx)
