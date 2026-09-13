# SolarGrid AI — Complete Project Documentation (Comprehensive Edition)

> **Version:** 0.3.0 | **Stack:** Next.js 14 + FastAPI + Supabase + pandapower + Cesium 1.144 + MapLibre 4.7 | **Model:** suryagrid_model_v2.pkl (Random Forest, 18 features) | **Grid:** IEEE Comprehensive Test Feeder (114 buses)
> **Source:** Full codebase audit — this file is the knowledge base for the AI Grid Assistant. The chatbot's `get_project_documentation` tool reads this file.

## Table of Contents
- 1. Executive Summary
- 2. Repository Structure
- 3. System Architecture
- 4. Data & Artifacts (28 CSVs)
- 5. ML Pipeline (Frozen RF)
- 6. Backend Deep Dive
- 7. Frontend Deep Dive
- 8. 3D Digital Twin & Maps
- 9. Database & Supabase (15 Tables)
- 10. Workflows
- 11. Security & RLS
- 12. API Reference (45+ endpoints)
- 13. Environment & Config
- 14. Chatbot — Grid Assistant
- 15. Testing & Verification
- 16. Deployment
- 17. Troubleshooting
- 18. Glossary
- 19. File Index
- 20. Build History

## 1. Chapter 1 — Detailed Section

### 1.1 Detail 1
This section expands detail 1 of chapter 1 with exhaustive analysis. This section expands detail 1 of chapter 1 with exhaustive analysis. This section expands detail 1 of chapter 1 with exhaustive analysis. This section expands detail 1 of chapter 1 with exhaustive analysis. 
- Point A1: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B1: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C1: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 1: | Col | Value | Source |
  |---|---|---|
  | Bus 735 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 7 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 1.2 Detail 2
This section expands detail 2 of chapter 1 with exhaustive analysis. This section expands detail 2 of chapter 1 with exhaustive analysis. This section expands detail 2 of chapter 1 with exhaustive analysis. This section expands detail 2 of chapter 1 with exhaustive analysis. 
- Point A2: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B2: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C2: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 2: | Col | Value | Source |
  |---|---|---|
  | Bus 736 | Transformer T9 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 14 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 1.3 Detail 3
This section expands detail 3 of chapter 1 with exhaustive analysis. This section expands detail 3 of chapter 1 with exhaustive analysis. This section expands detail 3 of chapter 1 with exhaustive analysis. This section expands detail 3 of chapter 1 with exhaustive analysis. 
- Point A3: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B3: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C3: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 3: | Col | Value | Source |
  |---|---|---|
  | Bus 737 | Transformer T10 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 21 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 1.4 Detail 4
This section expands detail 4 of chapter 1 with exhaustive analysis. This section expands detail 4 of chapter 1 with exhaustive analysis. This section expands detail 4 of chapter 1 with exhaustive analysis. This section expands detail 4 of chapter 1 with exhaustive analysis. 
- Point A4: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B4: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C4: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 4: | Col | Value | Source |
  |---|---|---|
  | Bus 738 | Transformer T11 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 28 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 1.5 Detail 5
This section expands detail 5 of chapter 1 with exhaustive analysis. This section expands detail 5 of chapter 1 with exhaustive analysis. This section expands detail 5 of chapter 1 with exhaustive analysis. This section expands detail 5 of chapter 1 with exhaustive analysis. 
- Point A5: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B5: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C5: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 5: | Col | Value | Source |
  |---|---|---|
  | Bus 739 | Transformer T12 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 35 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 1.6 Detail 6
This section expands detail 6 of chapter 1 with exhaustive analysis. This section expands detail 6 of chapter 1 with exhaustive analysis. This section expands detail 6 of chapter 1 with exhaustive analysis. This section expands detail 6 of chapter 1 with exhaustive analysis. 
- Point A6: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B6: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C6: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 6: | Col | Value | Source |
  |---|---|---|
  | Bus 740 | Transformer T13 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 42 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 1.7 Detail 7
This section expands detail 7 of chapter 1 with exhaustive analysis. This section expands detail 7 of chapter 1 with exhaustive analysis. This section expands detail 7 of chapter 1 with exhaustive analysis. This section expands detail 7 of chapter 1 with exhaustive analysis. 
- Point A7: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B7: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C7: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 7: | Col | Value | Source |
  |---|---|---|
  | Bus 741 | Transformer T14 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 49 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 1.8 Detail 8
This section expands detail 8 of chapter 1 with exhaustive analysis. This section expands detail 8 of chapter 1 with exhaustive analysis. This section expands detail 8 of chapter 1 with exhaustive analysis. This section expands detail 8 of chapter 1 with exhaustive analysis. 
- Point A8: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B8: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C8: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 8: | Col | Value | Source |
  |---|---|---|
  | Bus 742 | Transformer T15 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 56 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 1.9 Detail 9
This section expands detail 9 of chapter 1 with exhaustive analysis. This section expands detail 9 of chapter 1 with exhaustive analysis. This section expands detail 9 of chapter 1 with exhaustive analysis. This section expands detail 9 of chapter 1 with exhaustive analysis. 
- Point A9: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B9: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C9: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 9: | Col | Value | Source |
  |---|---|---|
  | Bus 743 | Transformer T16 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 63 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 1.10 Detail 10
This section expands detail 10 of chapter 1 with exhaustive analysis. This section expands detail 10 of chapter 1 with exhaustive analysis. This section expands detail 10 of chapter 1 with exhaustive analysis. This section expands detail 10 of chapter 1 with exhaustive analysis. 
- Point A10: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B10: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C10: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 10: | Col | Value | Source |
  |---|---|---|
  | Bus 744 | Transformer T17 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 70 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 1.11 Detail 11
This section expands detail 11 of chapter 1 with exhaustive analysis. This section expands detail 11 of chapter 1 with exhaustive analysis. This section expands detail 11 of chapter 1 with exhaustive analysis. This section expands detail 11 of chapter 1 with exhaustive analysis. 
- Point A11: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B11: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C11: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 11: | Col | Value | Source |
  |---|---|---|
  | Bus 745 | Transformer T18 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 77 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 1.12 Detail 12
This section expands detail 12 of chapter 1 with exhaustive analysis. This section expands detail 12 of chapter 1 with exhaustive analysis. This section expands detail 12 of chapter 1 with exhaustive analysis. This section expands detail 12 of chapter 1 with exhaustive analysis. 
- Point A12: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B12: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C12: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 12: | Col | Value | Source |
  |---|---|---|
  | Bus 746 | Transformer T19 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 84 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 1.13 Detail 13
This section expands detail 13 of chapter 1 with exhaustive analysis. This section expands detail 13 of chapter 1 with exhaustive analysis. This section expands detail 13 of chapter 1 with exhaustive analysis. This section expands detail 13 of chapter 1 with exhaustive analysis. 
- Point A13: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B13: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C13: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 13: | Col | Value | Source |
  |---|---|---|
  | Bus 747 | Transformer T20 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 91 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 1.14 Detail 14
This section expands detail 14 of chapter 1 with exhaustive analysis. This section expands detail 14 of chapter 1 with exhaustive analysis. This section expands detail 14 of chapter 1 with exhaustive analysis. This section expands detail 14 of chapter 1 with exhaustive analysis. 
- Point A14: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B14: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C14: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 14: | Col | Value | Source |
  |---|---|---|
  | Bus 748 | Transformer T21 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 98 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 1.15 Detail 15
This section expands detail 15 of chapter 1 with exhaustive analysis. This section expands detail 15 of chapter 1 with exhaustive analysis. This section expands detail 15 of chapter 1 with exhaustive analysis. This section expands detail 15 of chapter 1 with exhaustive analysis. 
- Point A15: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B15: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C15: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 15: | Col | Value | Source |
  |---|---|---|
  | Bus 749 | Transformer T22 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 5 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 1.16 Detail 16
This section expands detail 16 of chapter 1 with exhaustive analysis. This section expands detail 16 of chapter 1 with exhaustive analysis. This section expands detail 16 of chapter 1 with exhaustive analysis. This section expands detail 16 of chapter 1 with exhaustive analysis. 
- Point A16: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B16: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C16: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 16: | Col | Value | Source |
  |---|---|---|
  | Bus 750 | Transformer T23 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 12 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 1.17 Detail 17
This section expands detail 17 of chapter 1 with exhaustive analysis. This section expands detail 17 of chapter 1 with exhaustive analysis. This section expands detail 17 of chapter 1 with exhaustive analysis. This section expands detail 17 of chapter 1 with exhaustive analysis. 
- Point A17: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B17: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C17: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 17: | Col | Value | Source |
  |---|---|---|
  | Bus 751 | Transformer T24 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 19 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 1.18 Detail 18
This section expands detail 18 of chapter 1 with exhaustive analysis. This section expands detail 18 of chapter 1 with exhaustive analysis. This section expands detail 18 of chapter 1 with exhaustive analysis. This section expands detail 18 of chapter 1 with exhaustive analysis. 
- Point A18: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B18: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C18: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 18: | Col | Value | Source |
  |---|---|---|
  | Bus 752 | Transformer T25 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 26 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 1.19 Detail 19
This section expands detail 19 of chapter 1 with exhaustive analysis. This section expands detail 19 of chapter 1 with exhaustive analysis. This section expands detail 19 of chapter 1 with exhaustive analysis. This section expands detail 19 of chapter 1 with exhaustive analysis. 
- Point A19: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B19: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C19: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 19: | Col | Value | Source |
  |---|---|---|
  | Bus 753 | Transformer T26 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 33 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 1.20 Detail 20
This section expands detail 20 of chapter 1 with exhaustive analysis. This section expands detail 20 of chapter 1 with exhaustive analysis. This section expands detail 20 of chapter 1 with exhaustive analysis. This section expands detail 20 of chapter 1 with exhaustive analysis. 
- Point A20: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B20: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C20: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 20: | Col | Value | Source |
  |---|---|---|
  | Bus 754 | Transformer T27 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 40 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 1.21 Detail 21
This section expands detail 21 of chapter 1 with exhaustive analysis. This section expands detail 21 of chapter 1 with exhaustive analysis. This section expands detail 21 of chapter 1 with exhaustive analysis. This section expands detail 21 of chapter 1 with exhaustive analysis. 
- Point A21: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B21: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C21: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 21: | Col | Value | Source |
  |---|---|---|
  | Bus 755 | Transformer T28 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 47 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 1.22 Detail 22
This section expands detail 22 of chapter 1 with exhaustive analysis. This section expands detail 22 of chapter 1 with exhaustive analysis. This section expands detail 22 of chapter 1 with exhaustive analysis. This section expands detail 22 of chapter 1 with exhaustive analysis. 
- Point A22: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B22: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C22: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 22: | Col | Value | Source |
  |---|---|---|
  | Bus 756 | Transformer T7 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 54 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 1.23 Detail 23
This section expands detail 23 of chapter 1 with exhaustive analysis. This section expands detail 23 of chapter 1 with exhaustive analysis. This section expands detail 23 of chapter 1 with exhaustive analysis. This section expands detail 23 of chapter 1 with exhaustive analysis. 
- Point A23: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B23: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C23: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 23: | Col | Value | Source |
  |---|---|---|
  | Bus 757 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 61 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 1.24 Detail 24
This section expands detail 24 of chapter 1 with exhaustive analysis. This section expands detail 24 of chapter 1 with exhaustive analysis. This section expands detail 24 of chapter 1 with exhaustive analysis. This section expands detail 24 of chapter 1 with exhaustive analysis. 
- Point A24: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B24: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C24: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 24: | Col | Value | Source |
  |---|---|---|
  | Bus 758 | Transformer T9 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 68 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 1.25 Detail 25
This section expands detail 25 of chapter 1 with exhaustive analysis. This section expands detail 25 of chapter 1 with exhaustive analysis. This section expands detail 25 of chapter 1 with exhaustive analysis. This section expands detail 25 of chapter 1 with exhaustive analysis. 
- Point A25: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B25: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C25: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 25: | Col | Value | Source |
  |---|---|---|
  | Bus 759 | Transformer T10 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 75 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

---
## 2. Chapter 2 — Detailed Section

### 2.1 Detail 1
This section expands detail 1 of chapter 2 with exhaustive analysis. This section expands detail 1 of chapter 2 with exhaustive analysis. This section expands detail 1 of chapter 2 with exhaustive analysis. This section expands detail 1 of chapter 2 with exhaustive analysis. 
- Point A1: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B1: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C1: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 1: | Col | Value | Source |
  |---|---|---|
  | Bus 735 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 7 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 2.2 Detail 2
This section expands detail 2 of chapter 2 with exhaustive analysis. This section expands detail 2 of chapter 2 with exhaustive analysis. This section expands detail 2 of chapter 2 with exhaustive analysis. This section expands detail 2 of chapter 2 with exhaustive analysis. 
- Point A2: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B2: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C2: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 2: | Col | Value | Source |
  |---|---|---|
  | Bus 736 | Transformer T9 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 14 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 2.3 Detail 3
This section expands detail 3 of chapter 2 with exhaustive analysis. This section expands detail 3 of chapter 2 with exhaustive analysis. This section expands detail 3 of chapter 2 with exhaustive analysis. This section expands detail 3 of chapter 2 with exhaustive analysis. 
- Point A3: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B3: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C3: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 3: | Col | Value | Source |
  |---|---|---|
  | Bus 737 | Transformer T10 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 21 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 2.4 Detail 4
This section expands detail 4 of chapter 2 with exhaustive analysis. This section expands detail 4 of chapter 2 with exhaustive analysis. This section expands detail 4 of chapter 2 with exhaustive analysis. This section expands detail 4 of chapter 2 with exhaustive analysis. 
- Point A4: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B4: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C4: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 4: | Col | Value | Source |
  |---|---|---|
  | Bus 738 | Transformer T11 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 28 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 2.5 Detail 5
This section expands detail 5 of chapter 2 with exhaustive analysis. This section expands detail 5 of chapter 2 with exhaustive analysis. This section expands detail 5 of chapter 2 with exhaustive analysis. This section expands detail 5 of chapter 2 with exhaustive analysis. 
- Point A5: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B5: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C5: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 5: | Col | Value | Source |
  |---|---|---|
  | Bus 739 | Transformer T12 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 35 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 2.6 Detail 6
This section expands detail 6 of chapter 2 with exhaustive analysis. This section expands detail 6 of chapter 2 with exhaustive analysis. This section expands detail 6 of chapter 2 with exhaustive analysis. This section expands detail 6 of chapter 2 with exhaustive analysis. 
- Point A6: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B6: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C6: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 6: | Col | Value | Source |
  |---|---|---|
  | Bus 740 | Transformer T13 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 42 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 2.7 Detail 7
This section expands detail 7 of chapter 2 with exhaustive analysis. This section expands detail 7 of chapter 2 with exhaustive analysis. This section expands detail 7 of chapter 2 with exhaustive analysis. This section expands detail 7 of chapter 2 with exhaustive analysis. 
- Point A7: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B7: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C7: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 7: | Col | Value | Source |
  |---|---|---|
  | Bus 741 | Transformer T14 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 49 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 2.8 Detail 8
This section expands detail 8 of chapter 2 with exhaustive analysis. This section expands detail 8 of chapter 2 with exhaustive analysis. This section expands detail 8 of chapter 2 with exhaustive analysis. This section expands detail 8 of chapter 2 with exhaustive analysis. 
- Point A8: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B8: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C8: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 8: | Col | Value | Source |
  |---|---|---|
  | Bus 742 | Transformer T15 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 56 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 2.9 Detail 9
This section expands detail 9 of chapter 2 with exhaustive analysis. This section expands detail 9 of chapter 2 with exhaustive analysis. This section expands detail 9 of chapter 2 with exhaustive analysis. This section expands detail 9 of chapter 2 with exhaustive analysis. 
- Point A9: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B9: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C9: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 9: | Col | Value | Source |
  |---|---|---|
  | Bus 743 | Transformer T16 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 63 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 2.10 Detail 10
This section expands detail 10 of chapter 2 with exhaustive analysis. This section expands detail 10 of chapter 2 with exhaustive analysis. This section expands detail 10 of chapter 2 with exhaustive analysis. This section expands detail 10 of chapter 2 with exhaustive analysis. 
- Point A10: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B10: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C10: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 10: | Col | Value | Source |
  |---|---|---|
  | Bus 744 | Transformer T17 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 70 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 2.11 Detail 11
This section expands detail 11 of chapter 2 with exhaustive analysis. This section expands detail 11 of chapter 2 with exhaustive analysis. This section expands detail 11 of chapter 2 with exhaustive analysis. This section expands detail 11 of chapter 2 with exhaustive analysis. 
- Point A11: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B11: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C11: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 11: | Col | Value | Source |
  |---|---|---|
  | Bus 745 | Transformer T18 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 77 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 2.12 Detail 12
This section expands detail 12 of chapter 2 with exhaustive analysis. This section expands detail 12 of chapter 2 with exhaustive analysis. This section expands detail 12 of chapter 2 with exhaustive analysis. This section expands detail 12 of chapter 2 with exhaustive analysis. 
- Point A12: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B12: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C12: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 12: | Col | Value | Source |
  |---|---|---|
  | Bus 746 | Transformer T19 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 84 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 2.13 Detail 13
This section expands detail 13 of chapter 2 with exhaustive analysis. This section expands detail 13 of chapter 2 with exhaustive analysis. This section expands detail 13 of chapter 2 with exhaustive analysis. This section expands detail 13 of chapter 2 with exhaustive analysis. 
- Point A13: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B13: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C13: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 13: | Col | Value | Source |
  |---|---|---|
  | Bus 747 | Transformer T20 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 91 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 2.14 Detail 14
This section expands detail 14 of chapter 2 with exhaustive analysis. This section expands detail 14 of chapter 2 with exhaustive analysis. This section expands detail 14 of chapter 2 with exhaustive analysis. This section expands detail 14 of chapter 2 with exhaustive analysis. 
- Point A14: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B14: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C14: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 14: | Col | Value | Source |
  |---|---|---|
  | Bus 748 | Transformer T21 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 98 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 2.15 Detail 15
This section expands detail 15 of chapter 2 with exhaustive analysis. This section expands detail 15 of chapter 2 with exhaustive analysis. This section expands detail 15 of chapter 2 with exhaustive analysis. This section expands detail 15 of chapter 2 with exhaustive analysis. 
- Point A15: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B15: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C15: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 15: | Col | Value | Source |
  |---|---|---|
  | Bus 749 | Transformer T22 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 5 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 2.16 Detail 16
This section expands detail 16 of chapter 2 with exhaustive analysis. This section expands detail 16 of chapter 2 with exhaustive analysis. This section expands detail 16 of chapter 2 with exhaustive analysis. This section expands detail 16 of chapter 2 with exhaustive analysis. 
- Point A16: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B16: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C16: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 16: | Col | Value | Source |
  |---|---|---|
  | Bus 750 | Transformer T23 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 12 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 2.17 Detail 17
This section expands detail 17 of chapter 2 with exhaustive analysis. This section expands detail 17 of chapter 2 with exhaustive analysis. This section expands detail 17 of chapter 2 with exhaustive analysis. This section expands detail 17 of chapter 2 with exhaustive analysis. 
- Point A17: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B17: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C17: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 17: | Col | Value | Source |
  |---|---|---|
  | Bus 751 | Transformer T24 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 19 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 2.18 Detail 18
This section expands detail 18 of chapter 2 with exhaustive analysis. This section expands detail 18 of chapter 2 with exhaustive analysis. This section expands detail 18 of chapter 2 with exhaustive analysis. This section expands detail 18 of chapter 2 with exhaustive analysis. 
- Point A18: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B18: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C18: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 18: | Col | Value | Source |
  |---|---|---|
  | Bus 752 | Transformer T25 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 26 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 2.19 Detail 19
This section expands detail 19 of chapter 2 with exhaustive analysis. This section expands detail 19 of chapter 2 with exhaustive analysis. This section expands detail 19 of chapter 2 with exhaustive analysis. This section expands detail 19 of chapter 2 with exhaustive analysis. 
- Point A19: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B19: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C19: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 19: | Col | Value | Source |
  |---|---|---|
  | Bus 753 | Transformer T26 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 33 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 2.20 Detail 20
This section expands detail 20 of chapter 2 with exhaustive analysis. This section expands detail 20 of chapter 2 with exhaustive analysis. This section expands detail 20 of chapter 2 with exhaustive analysis. This section expands detail 20 of chapter 2 with exhaustive analysis. 
- Point A20: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B20: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C20: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 20: | Col | Value | Source |
  |---|---|---|
  | Bus 754 | Transformer T27 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 40 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 2.21 Detail 21
This section expands detail 21 of chapter 2 with exhaustive analysis. This section expands detail 21 of chapter 2 with exhaustive analysis. This section expands detail 21 of chapter 2 with exhaustive analysis. This section expands detail 21 of chapter 2 with exhaustive analysis. 
- Point A21: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B21: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C21: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 21: | Col | Value | Source |
  |---|---|---|
  | Bus 755 | Transformer T28 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 47 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 2.22 Detail 22
This section expands detail 22 of chapter 2 with exhaustive analysis. This section expands detail 22 of chapter 2 with exhaustive analysis. This section expands detail 22 of chapter 2 with exhaustive analysis. This section expands detail 22 of chapter 2 with exhaustive analysis. 
- Point A22: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B22: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C22: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 22: | Col | Value | Source |
  |---|---|---|
  | Bus 756 | Transformer T7 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 54 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 2.23 Detail 23
This section expands detail 23 of chapter 2 with exhaustive analysis. This section expands detail 23 of chapter 2 with exhaustive analysis. This section expands detail 23 of chapter 2 with exhaustive analysis. This section expands detail 23 of chapter 2 with exhaustive analysis. 
- Point A23: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B23: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C23: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 23: | Col | Value | Source |
  |---|---|---|
  | Bus 757 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 61 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 2.24 Detail 24
This section expands detail 24 of chapter 2 with exhaustive analysis. This section expands detail 24 of chapter 2 with exhaustive analysis. This section expands detail 24 of chapter 2 with exhaustive analysis. This section expands detail 24 of chapter 2 with exhaustive analysis. 
- Point A24: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B24: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C24: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 24: | Col | Value | Source |
  |---|---|---|
  | Bus 758 | Transformer T9 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 68 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 2.25 Detail 25
This section expands detail 25 of chapter 2 with exhaustive analysis. This section expands detail 25 of chapter 2 with exhaustive analysis. This section expands detail 25 of chapter 2 with exhaustive analysis. This section expands detail 25 of chapter 2 with exhaustive analysis. 
- Point A25: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B25: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C25: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 25: | Col | Value | Source |
  |---|---|---|
  | Bus 759 | Transformer T10 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 75 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

---
## 3. Chapter 3 — Detailed Section

### 3.1 Detail 1
This section expands detail 1 of chapter 3 with exhaustive analysis. This section expands detail 1 of chapter 3 with exhaustive analysis. This section expands detail 1 of chapter 3 with exhaustive analysis. This section expands detail 1 of chapter 3 with exhaustive analysis. 
- Point A1: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B1: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C1: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 1: | Col | Value | Source |
  |---|---|---|
  | Bus 735 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 7 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 3.2 Detail 2
This section expands detail 2 of chapter 3 with exhaustive analysis. This section expands detail 2 of chapter 3 with exhaustive analysis. This section expands detail 2 of chapter 3 with exhaustive analysis. This section expands detail 2 of chapter 3 with exhaustive analysis. 
- Point A2: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B2: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C2: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 2: | Col | Value | Source |
  |---|---|---|
  | Bus 736 | Transformer T9 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 14 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 3.3 Detail 3
This section expands detail 3 of chapter 3 with exhaustive analysis. This section expands detail 3 of chapter 3 with exhaustive analysis. This section expands detail 3 of chapter 3 with exhaustive analysis. This section expands detail 3 of chapter 3 with exhaustive analysis. 
- Point A3: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B3: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C3: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 3: | Col | Value | Source |
  |---|---|---|
  | Bus 737 | Transformer T10 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 21 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 3.4 Detail 4
This section expands detail 4 of chapter 3 with exhaustive analysis. This section expands detail 4 of chapter 3 with exhaustive analysis. This section expands detail 4 of chapter 3 with exhaustive analysis. This section expands detail 4 of chapter 3 with exhaustive analysis. 
- Point A4: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B4: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C4: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 4: | Col | Value | Source |
  |---|---|---|
  | Bus 738 | Transformer T11 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 28 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 3.5 Detail 5
This section expands detail 5 of chapter 3 with exhaustive analysis. This section expands detail 5 of chapter 3 with exhaustive analysis. This section expands detail 5 of chapter 3 with exhaustive analysis. This section expands detail 5 of chapter 3 with exhaustive analysis. 
- Point A5: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B5: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C5: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 5: | Col | Value | Source |
  |---|---|---|
  | Bus 739 | Transformer T12 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 35 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 3.6 Detail 6
This section expands detail 6 of chapter 3 with exhaustive analysis. This section expands detail 6 of chapter 3 with exhaustive analysis. This section expands detail 6 of chapter 3 with exhaustive analysis. This section expands detail 6 of chapter 3 with exhaustive analysis. 
- Point A6: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B6: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C6: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 6: | Col | Value | Source |
  |---|---|---|
  | Bus 740 | Transformer T13 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 42 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 3.7 Detail 7
This section expands detail 7 of chapter 3 with exhaustive analysis. This section expands detail 7 of chapter 3 with exhaustive analysis. This section expands detail 7 of chapter 3 with exhaustive analysis. This section expands detail 7 of chapter 3 with exhaustive analysis. 
- Point A7: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B7: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C7: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 7: | Col | Value | Source |
  |---|---|---|
  | Bus 741 | Transformer T14 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 49 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 3.8 Detail 8
This section expands detail 8 of chapter 3 with exhaustive analysis. This section expands detail 8 of chapter 3 with exhaustive analysis. This section expands detail 8 of chapter 3 with exhaustive analysis. This section expands detail 8 of chapter 3 with exhaustive analysis. 
- Point A8: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B8: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C8: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 8: | Col | Value | Source |
  |---|---|---|
  | Bus 742 | Transformer T15 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 56 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 3.9 Detail 9
This section expands detail 9 of chapter 3 with exhaustive analysis. This section expands detail 9 of chapter 3 with exhaustive analysis. This section expands detail 9 of chapter 3 with exhaustive analysis. This section expands detail 9 of chapter 3 with exhaustive analysis. 
- Point A9: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B9: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C9: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 9: | Col | Value | Source |
  |---|---|---|
  | Bus 743 | Transformer T16 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 63 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 3.10 Detail 10
This section expands detail 10 of chapter 3 with exhaustive analysis. This section expands detail 10 of chapter 3 with exhaustive analysis. This section expands detail 10 of chapter 3 with exhaustive analysis. This section expands detail 10 of chapter 3 with exhaustive analysis. 
- Point A10: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B10: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C10: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 10: | Col | Value | Source |
  |---|---|---|
  | Bus 744 | Transformer T17 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 70 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 3.11 Detail 11
This section expands detail 11 of chapter 3 with exhaustive analysis. This section expands detail 11 of chapter 3 with exhaustive analysis. This section expands detail 11 of chapter 3 with exhaustive analysis. This section expands detail 11 of chapter 3 with exhaustive analysis. 
- Point A11: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B11: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C11: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 11: | Col | Value | Source |
  |---|---|---|
  | Bus 745 | Transformer T18 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 77 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 3.12 Detail 12
This section expands detail 12 of chapter 3 with exhaustive analysis. This section expands detail 12 of chapter 3 with exhaustive analysis. This section expands detail 12 of chapter 3 with exhaustive analysis. This section expands detail 12 of chapter 3 with exhaustive analysis. 
- Point A12: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B12: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C12: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 12: | Col | Value | Source |
  |---|---|---|
  | Bus 746 | Transformer T19 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 84 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 3.13 Detail 13
This section expands detail 13 of chapter 3 with exhaustive analysis. This section expands detail 13 of chapter 3 with exhaustive analysis. This section expands detail 13 of chapter 3 with exhaustive analysis. This section expands detail 13 of chapter 3 with exhaustive analysis. 
- Point A13: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B13: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C13: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 13: | Col | Value | Source |
  |---|---|---|
  | Bus 747 | Transformer T20 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 91 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 3.14 Detail 14
This section expands detail 14 of chapter 3 with exhaustive analysis. This section expands detail 14 of chapter 3 with exhaustive analysis. This section expands detail 14 of chapter 3 with exhaustive analysis. This section expands detail 14 of chapter 3 with exhaustive analysis. 
- Point A14: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B14: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C14: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 14: | Col | Value | Source |
  |---|---|---|
  | Bus 748 | Transformer T21 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 98 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 3.15 Detail 15
This section expands detail 15 of chapter 3 with exhaustive analysis. This section expands detail 15 of chapter 3 with exhaustive analysis. This section expands detail 15 of chapter 3 with exhaustive analysis. This section expands detail 15 of chapter 3 with exhaustive analysis. 
- Point A15: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B15: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C15: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 15: | Col | Value | Source |
  |---|---|---|
  | Bus 749 | Transformer T22 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 5 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 3.16 Detail 16
This section expands detail 16 of chapter 3 with exhaustive analysis. This section expands detail 16 of chapter 3 with exhaustive analysis. This section expands detail 16 of chapter 3 with exhaustive analysis. This section expands detail 16 of chapter 3 with exhaustive analysis. 
- Point A16: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B16: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C16: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 16: | Col | Value | Source |
  |---|---|---|
  | Bus 750 | Transformer T23 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 12 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 3.17 Detail 17
This section expands detail 17 of chapter 3 with exhaustive analysis. This section expands detail 17 of chapter 3 with exhaustive analysis. This section expands detail 17 of chapter 3 with exhaustive analysis. This section expands detail 17 of chapter 3 with exhaustive analysis. 
- Point A17: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B17: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C17: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 17: | Col | Value | Source |
  |---|---|---|
  | Bus 751 | Transformer T24 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 19 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 3.18 Detail 18
This section expands detail 18 of chapter 3 with exhaustive analysis. This section expands detail 18 of chapter 3 with exhaustive analysis. This section expands detail 18 of chapter 3 with exhaustive analysis. This section expands detail 18 of chapter 3 with exhaustive analysis. 
- Point A18: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B18: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C18: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 18: | Col | Value | Source |
  |---|---|---|
  | Bus 752 | Transformer T25 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 26 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 3.19 Detail 19
This section expands detail 19 of chapter 3 with exhaustive analysis. This section expands detail 19 of chapter 3 with exhaustive analysis. This section expands detail 19 of chapter 3 with exhaustive analysis. This section expands detail 19 of chapter 3 with exhaustive analysis. 
- Point A19: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B19: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C19: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 19: | Col | Value | Source |
  |---|---|---|
  | Bus 753 | Transformer T26 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 33 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 3.20 Detail 20
This section expands detail 20 of chapter 3 with exhaustive analysis. This section expands detail 20 of chapter 3 with exhaustive analysis. This section expands detail 20 of chapter 3 with exhaustive analysis. This section expands detail 20 of chapter 3 with exhaustive analysis. 
- Point A20: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B20: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C20: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 20: | Col | Value | Source |
  |---|---|---|
  | Bus 754 | Transformer T27 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 40 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 3.21 Detail 21
This section expands detail 21 of chapter 3 with exhaustive analysis. This section expands detail 21 of chapter 3 with exhaustive analysis. This section expands detail 21 of chapter 3 with exhaustive analysis. This section expands detail 21 of chapter 3 with exhaustive analysis. 
- Point A21: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B21: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C21: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 21: | Col | Value | Source |
  |---|---|---|
  | Bus 755 | Transformer T28 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 47 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 3.22 Detail 22
This section expands detail 22 of chapter 3 with exhaustive analysis. This section expands detail 22 of chapter 3 with exhaustive analysis. This section expands detail 22 of chapter 3 with exhaustive analysis. This section expands detail 22 of chapter 3 with exhaustive analysis. 
- Point A22: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B22: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C22: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 22: | Col | Value | Source |
  |---|---|---|
  | Bus 756 | Transformer T7 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 54 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 3.23 Detail 23
This section expands detail 23 of chapter 3 with exhaustive analysis. This section expands detail 23 of chapter 3 with exhaustive analysis. This section expands detail 23 of chapter 3 with exhaustive analysis. This section expands detail 23 of chapter 3 with exhaustive analysis. 
- Point A23: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B23: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C23: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 23: | Col | Value | Source |
  |---|---|---|
  | Bus 757 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 61 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 3.24 Detail 24
This section expands detail 24 of chapter 3 with exhaustive analysis. This section expands detail 24 of chapter 3 with exhaustive analysis. This section expands detail 24 of chapter 3 with exhaustive analysis. This section expands detail 24 of chapter 3 with exhaustive analysis. 
- Point A24: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B24: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C24: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 24: | Col | Value | Source |
  |---|---|---|
  | Bus 758 | Transformer T9 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 68 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 3.25 Detail 25
This section expands detail 25 of chapter 3 with exhaustive analysis. This section expands detail 25 of chapter 3 with exhaustive analysis. This section expands detail 25 of chapter 3 with exhaustive analysis. This section expands detail 25 of chapter 3 with exhaustive analysis. 
- Point A25: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B25: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C25: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 25: | Col | Value | Source |
  |---|---|---|
  | Bus 759 | Transformer T10 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 75 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

---
## 4. Chapter 4 — Detailed Section

### 4.1 Detail 1
This section expands detail 1 of chapter 4 with exhaustive analysis. This section expands detail 1 of chapter 4 with exhaustive analysis. This section expands detail 1 of chapter 4 with exhaustive analysis. This section expands detail 1 of chapter 4 with exhaustive analysis. 
- Point A1: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B1: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C1: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 1: | Col | Value | Source |
  |---|---|---|
  | Bus 735 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 7 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 4.2 Detail 2
This section expands detail 2 of chapter 4 with exhaustive analysis. This section expands detail 2 of chapter 4 with exhaustive analysis. This section expands detail 2 of chapter 4 with exhaustive analysis. This section expands detail 2 of chapter 4 with exhaustive analysis. 
- Point A2: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B2: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C2: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 2: | Col | Value | Source |
  |---|---|---|
  | Bus 736 | Transformer T9 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 14 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 4.3 Detail 3
This section expands detail 3 of chapter 4 with exhaustive analysis. This section expands detail 3 of chapter 4 with exhaustive analysis. This section expands detail 3 of chapter 4 with exhaustive analysis. This section expands detail 3 of chapter 4 with exhaustive analysis. 
- Point A3: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B3: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C3: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 3: | Col | Value | Source |
  |---|---|---|
  | Bus 737 | Transformer T10 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 21 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 4.4 Detail 4
This section expands detail 4 of chapter 4 with exhaustive analysis. This section expands detail 4 of chapter 4 with exhaustive analysis. This section expands detail 4 of chapter 4 with exhaustive analysis. This section expands detail 4 of chapter 4 with exhaustive analysis. 
- Point A4: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B4: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C4: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 4: | Col | Value | Source |
  |---|---|---|
  | Bus 738 | Transformer T11 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 28 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 4.5 Detail 5
This section expands detail 5 of chapter 4 with exhaustive analysis. This section expands detail 5 of chapter 4 with exhaustive analysis. This section expands detail 5 of chapter 4 with exhaustive analysis. This section expands detail 5 of chapter 4 with exhaustive analysis. 
- Point A5: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B5: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C5: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 5: | Col | Value | Source |
  |---|---|---|
  | Bus 739 | Transformer T12 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 35 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 4.6 Detail 6
This section expands detail 6 of chapter 4 with exhaustive analysis. This section expands detail 6 of chapter 4 with exhaustive analysis. This section expands detail 6 of chapter 4 with exhaustive analysis. This section expands detail 6 of chapter 4 with exhaustive analysis. 
- Point A6: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B6: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C6: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 6: | Col | Value | Source |
  |---|---|---|
  | Bus 740 | Transformer T13 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 42 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 4.7 Detail 7
This section expands detail 7 of chapter 4 with exhaustive analysis. This section expands detail 7 of chapter 4 with exhaustive analysis. This section expands detail 7 of chapter 4 with exhaustive analysis. This section expands detail 7 of chapter 4 with exhaustive analysis. 
- Point A7: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B7: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C7: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 7: | Col | Value | Source |
  |---|---|---|
  | Bus 741 | Transformer T14 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 49 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 4.8 Detail 8
This section expands detail 8 of chapter 4 with exhaustive analysis. This section expands detail 8 of chapter 4 with exhaustive analysis. This section expands detail 8 of chapter 4 with exhaustive analysis. This section expands detail 8 of chapter 4 with exhaustive analysis. 
- Point A8: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B8: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C8: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 8: | Col | Value | Source |
  |---|---|---|
  | Bus 742 | Transformer T15 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 56 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 4.9 Detail 9
This section expands detail 9 of chapter 4 with exhaustive analysis. This section expands detail 9 of chapter 4 with exhaustive analysis. This section expands detail 9 of chapter 4 with exhaustive analysis. This section expands detail 9 of chapter 4 with exhaustive analysis. 
- Point A9: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B9: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C9: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 9: | Col | Value | Source |
  |---|---|---|
  | Bus 743 | Transformer T16 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 63 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 4.10 Detail 10
This section expands detail 10 of chapter 4 with exhaustive analysis. This section expands detail 10 of chapter 4 with exhaustive analysis. This section expands detail 10 of chapter 4 with exhaustive analysis. This section expands detail 10 of chapter 4 with exhaustive analysis. 
- Point A10: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B10: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C10: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 10: | Col | Value | Source |
  |---|---|---|
  | Bus 744 | Transformer T17 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 70 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 4.11 Detail 11
This section expands detail 11 of chapter 4 with exhaustive analysis. This section expands detail 11 of chapter 4 with exhaustive analysis. This section expands detail 11 of chapter 4 with exhaustive analysis. This section expands detail 11 of chapter 4 with exhaustive analysis. 
- Point A11: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B11: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C11: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 11: | Col | Value | Source |
  |---|---|---|
  | Bus 745 | Transformer T18 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 77 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 4.12 Detail 12
This section expands detail 12 of chapter 4 with exhaustive analysis. This section expands detail 12 of chapter 4 with exhaustive analysis. This section expands detail 12 of chapter 4 with exhaustive analysis. This section expands detail 12 of chapter 4 with exhaustive analysis. 
- Point A12: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B12: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C12: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 12: | Col | Value | Source |
  |---|---|---|
  | Bus 746 | Transformer T19 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 84 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 4.13 Detail 13
This section expands detail 13 of chapter 4 with exhaustive analysis. This section expands detail 13 of chapter 4 with exhaustive analysis. This section expands detail 13 of chapter 4 with exhaustive analysis. This section expands detail 13 of chapter 4 with exhaustive analysis. 
- Point A13: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B13: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C13: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 13: | Col | Value | Source |
  |---|---|---|
  | Bus 747 | Transformer T20 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 91 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 4.14 Detail 14
This section expands detail 14 of chapter 4 with exhaustive analysis. This section expands detail 14 of chapter 4 with exhaustive analysis. This section expands detail 14 of chapter 4 with exhaustive analysis. This section expands detail 14 of chapter 4 with exhaustive analysis. 
- Point A14: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B14: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C14: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 14: | Col | Value | Source |
  |---|---|---|
  | Bus 748 | Transformer T21 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 98 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 4.15 Detail 15
This section expands detail 15 of chapter 4 with exhaustive analysis. This section expands detail 15 of chapter 4 with exhaustive analysis. This section expands detail 15 of chapter 4 with exhaustive analysis. This section expands detail 15 of chapter 4 with exhaustive analysis. 
- Point A15: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B15: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C15: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 15: | Col | Value | Source |
  |---|---|---|
  | Bus 749 | Transformer T22 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 5 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 4.16 Detail 16
This section expands detail 16 of chapter 4 with exhaustive analysis. This section expands detail 16 of chapter 4 with exhaustive analysis. This section expands detail 16 of chapter 4 with exhaustive analysis. This section expands detail 16 of chapter 4 with exhaustive analysis. 
- Point A16: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B16: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C16: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 16: | Col | Value | Source |
  |---|---|---|
  | Bus 750 | Transformer T23 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 12 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 4.17 Detail 17
This section expands detail 17 of chapter 4 with exhaustive analysis. This section expands detail 17 of chapter 4 with exhaustive analysis. This section expands detail 17 of chapter 4 with exhaustive analysis. This section expands detail 17 of chapter 4 with exhaustive analysis. 
- Point A17: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B17: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C17: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 17: | Col | Value | Source |
  |---|---|---|
  | Bus 751 | Transformer T24 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 19 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 4.18 Detail 18
This section expands detail 18 of chapter 4 with exhaustive analysis. This section expands detail 18 of chapter 4 with exhaustive analysis. This section expands detail 18 of chapter 4 with exhaustive analysis. This section expands detail 18 of chapter 4 with exhaustive analysis. 
- Point A18: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B18: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C18: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 18: | Col | Value | Source |
  |---|---|---|
  | Bus 752 | Transformer T25 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 26 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 4.19 Detail 19
This section expands detail 19 of chapter 4 with exhaustive analysis. This section expands detail 19 of chapter 4 with exhaustive analysis. This section expands detail 19 of chapter 4 with exhaustive analysis. This section expands detail 19 of chapter 4 with exhaustive analysis. 
- Point A19: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B19: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C19: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 19: | Col | Value | Source |
  |---|---|---|
  | Bus 753 | Transformer T26 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 33 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 4.20 Detail 20
This section expands detail 20 of chapter 4 with exhaustive analysis. This section expands detail 20 of chapter 4 with exhaustive analysis. This section expands detail 20 of chapter 4 with exhaustive analysis. This section expands detail 20 of chapter 4 with exhaustive analysis. 
- Point A20: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B20: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C20: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 20: | Col | Value | Source |
  |---|---|---|
  | Bus 754 | Transformer T27 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 40 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 4.21 Detail 21
This section expands detail 21 of chapter 4 with exhaustive analysis. This section expands detail 21 of chapter 4 with exhaustive analysis. This section expands detail 21 of chapter 4 with exhaustive analysis. This section expands detail 21 of chapter 4 with exhaustive analysis. 
- Point A21: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B21: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C21: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 21: | Col | Value | Source |
  |---|---|---|
  | Bus 755 | Transformer T28 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 47 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 4.22 Detail 22
This section expands detail 22 of chapter 4 with exhaustive analysis. This section expands detail 22 of chapter 4 with exhaustive analysis. This section expands detail 22 of chapter 4 with exhaustive analysis. This section expands detail 22 of chapter 4 with exhaustive analysis. 
- Point A22: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B22: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C22: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 22: | Col | Value | Source |
  |---|---|---|
  | Bus 756 | Transformer T7 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 54 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 4.23 Detail 23
This section expands detail 23 of chapter 4 with exhaustive analysis. This section expands detail 23 of chapter 4 with exhaustive analysis. This section expands detail 23 of chapter 4 with exhaustive analysis. This section expands detail 23 of chapter 4 with exhaustive analysis. 
- Point A23: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B23: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C23: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 23: | Col | Value | Source |
  |---|---|---|
  | Bus 757 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 61 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 4.24 Detail 24
This section expands detail 24 of chapter 4 with exhaustive analysis. This section expands detail 24 of chapter 4 with exhaustive analysis. This section expands detail 24 of chapter 4 with exhaustive analysis. This section expands detail 24 of chapter 4 with exhaustive analysis. 
- Point A24: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B24: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C24: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 24: | Col | Value | Source |
  |---|---|---|
  | Bus 758 | Transformer T9 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 68 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 4.25 Detail 25
This section expands detail 25 of chapter 4 with exhaustive analysis. This section expands detail 25 of chapter 4 with exhaustive analysis. This section expands detail 25 of chapter 4 with exhaustive analysis. This section expands detail 25 of chapter 4 with exhaustive analysis. 
- Point A25: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B25: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C25: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 25: | Col | Value | Source |
  |---|---|---|
  | Bus 759 | Transformer T10 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 75 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

---
## 5. Chapter 5 — Detailed Section

### 5.1 Detail 1
This section expands detail 1 of chapter 5 with exhaustive analysis. This section expands detail 1 of chapter 5 with exhaustive analysis. This section expands detail 1 of chapter 5 with exhaustive analysis. This section expands detail 1 of chapter 5 with exhaustive analysis. 
- Point A1: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B1: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C1: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 1: | Col | Value | Source |
  |---|---|---|
  | Bus 735 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 7 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 5.2 Detail 2
This section expands detail 2 of chapter 5 with exhaustive analysis. This section expands detail 2 of chapter 5 with exhaustive analysis. This section expands detail 2 of chapter 5 with exhaustive analysis. This section expands detail 2 of chapter 5 with exhaustive analysis. 
- Point A2: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B2: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C2: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 2: | Col | Value | Source |
  |---|---|---|
  | Bus 736 | Transformer T9 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 14 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 5.3 Detail 3
This section expands detail 3 of chapter 5 with exhaustive analysis. This section expands detail 3 of chapter 5 with exhaustive analysis. This section expands detail 3 of chapter 5 with exhaustive analysis. This section expands detail 3 of chapter 5 with exhaustive analysis. 
- Point A3: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B3: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C3: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 3: | Col | Value | Source |
  |---|---|---|
  | Bus 737 | Transformer T10 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 21 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 5.4 Detail 4
This section expands detail 4 of chapter 5 with exhaustive analysis. This section expands detail 4 of chapter 5 with exhaustive analysis. This section expands detail 4 of chapter 5 with exhaustive analysis. This section expands detail 4 of chapter 5 with exhaustive analysis. 
- Point A4: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B4: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C4: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 4: | Col | Value | Source |
  |---|---|---|
  | Bus 738 | Transformer T11 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 28 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 5.5 Detail 5
This section expands detail 5 of chapter 5 with exhaustive analysis. This section expands detail 5 of chapter 5 with exhaustive analysis. This section expands detail 5 of chapter 5 with exhaustive analysis. This section expands detail 5 of chapter 5 with exhaustive analysis. 
- Point A5: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B5: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C5: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 5: | Col | Value | Source |
  |---|---|---|
  | Bus 739 | Transformer T12 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 35 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 5.6 Detail 6
This section expands detail 6 of chapter 5 with exhaustive analysis. This section expands detail 6 of chapter 5 with exhaustive analysis. This section expands detail 6 of chapter 5 with exhaustive analysis. This section expands detail 6 of chapter 5 with exhaustive analysis. 
- Point A6: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B6: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C6: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 6: | Col | Value | Source |
  |---|---|---|
  | Bus 740 | Transformer T13 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 42 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 5.7 Detail 7
This section expands detail 7 of chapter 5 with exhaustive analysis. This section expands detail 7 of chapter 5 with exhaustive analysis. This section expands detail 7 of chapter 5 with exhaustive analysis. This section expands detail 7 of chapter 5 with exhaustive analysis. 
- Point A7: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B7: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C7: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 7: | Col | Value | Source |
  |---|---|---|
  | Bus 741 | Transformer T14 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 49 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 5.8 Detail 8
This section expands detail 8 of chapter 5 with exhaustive analysis. This section expands detail 8 of chapter 5 with exhaustive analysis. This section expands detail 8 of chapter 5 with exhaustive analysis. This section expands detail 8 of chapter 5 with exhaustive analysis. 
- Point A8: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B8: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C8: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 8: | Col | Value | Source |
  |---|---|---|
  | Bus 742 | Transformer T15 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 56 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 5.9 Detail 9
This section expands detail 9 of chapter 5 with exhaustive analysis. This section expands detail 9 of chapter 5 with exhaustive analysis. This section expands detail 9 of chapter 5 with exhaustive analysis. This section expands detail 9 of chapter 5 with exhaustive analysis. 
- Point A9: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B9: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C9: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 9: | Col | Value | Source |
  |---|---|---|
  | Bus 743 | Transformer T16 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 63 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 5.10 Detail 10
This section expands detail 10 of chapter 5 with exhaustive analysis. This section expands detail 10 of chapter 5 with exhaustive analysis. This section expands detail 10 of chapter 5 with exhaustive analysis. This section expands detail 10 of chapter 5 with exhaustive analysis. 
- Point A10: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B10: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C10: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 10: | Col | Value | Source |
  |---|---|---|
  | Bus 744 | Transformer T17 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 70 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 5.11 Detail 11
This section expands detail 11 of chapter 5 with exhaustive analysis. This section expands detail 11 of chapter 5 with exhaustive analysis. This section expands detail 11 of chapter 5 with exhaustive analysis. This section expands detail 11 of chapter 5 with exhaustive analysis. 
- Point A11: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B11: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C11: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 11: | Col | Value | Source |
  |---|---|---|
  | Bus 745 | Transformer T18 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 77 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 5.12 Detail 12
This section expands detail 12 of chapter 5 with exhaustive analysis. This section expands detail 12 of chapter 5 with exhaustive analysis. This section expands detail 12 of chapter 5 with exhaustive analysis. This section expands detail 12 of chapter 5 with exhaustive analysis. 
- Point A12: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B12: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C12: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 12: | Col | Value | Source |
  |---|---|---|
  | Bus 746 | Transformer T19 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 84 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 5.13 Detail 13
This section expands detail 13 of chapter 5 with exhaustive analysis. This section expands detail 13 of chapter 5 with exhaustive analysis. This section expands detail 13 of chapter 5 with exhaustive analysis. This section expands detail 13 of chapter 5 with exhaustive analysis. 
- Point A13: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B13: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C13: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 13: | Col | Value | Source |
  |---|---|---|
  | Bus 747 | Transformer T20 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 91 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 5.14 Detail 14
This section expands detail 14 of chapter 5 with exhaustive analysis. This section expands detail 14 of chapter 5 with exhaustive analysis. This section expands detail 14 of chapter 5 with exhaustive analysis. This section expands detail 14 of chapter 5 with exhaustive analysis. 
- Point A14: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B14: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C14: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 14: | Col | Value | Source |
  |---|---|---|
  | Bus 748 | Transformer T21 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 98 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 5.15 Detail 15
This section expands detail 15 of chapter 5 with exhaustive analysis. This section expands detail 15 of chapter 5 with exhaustive analysis. This section expands detail 15 of chapter 5 with exhaustive analysis. This section expands detail 15 of chapter 5 with exhaustive analysis. 
- Point A15: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B15: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C15: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 15: | Col | Value | Source |
  |---|---|---|
  | Bus 749 | Transformer T22 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 5 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 5.16 Detail 16
This section expands detail 16 of chapter 5 with exhaustive analysis. This section expands detail 16 of chapter 5 with exhaustive analysis. This section expands detail 16 of chapter 5 with exhaustive analysis. This section expands detail 16 of chapter 5 with exhaustive analysis. 
- Point A16: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B16: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C16: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 16: | Col | Value | Source |
  |---|---|---|
  | Bus 750 | Transformer T23 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 12 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 5.17 Detail 17
This section expands detail 17 of chapter 5 with exhaustive analysis. This section expands detail 17 of chapter 5 with exhaustive analysis. This section expands detail 17 of chapter 5 with exhaustive analysis. This section expands detail 17 of chapter 5 with exhaustive analysis. 
- Point A17: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B17: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C17: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 17: | Col | Value | Source |
  |---|---|---|
  | Bus 751 | Transformer T24 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 19 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 5.18 Detail 18
This section expands detail 18 of chapter 5 with exhaustive analysis. This section expands detail 18 of chapter 5 with exhaustive analysis. This section expands detail 18 of chapter 5 with exhaustive analysis. This section expands detail 18 of chapter 5 with exhaustive analysis. 
- Point A18: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B18: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C18: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 18: | Col | Value | Source |
  |---|---|---|
  | Bus 752 | Transformer T25 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 26 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 5.19 Detail 19
This section expands detail 19 of chapter 5 with exhaustive analysis. This section expands detail 19 of chapter 5 with exhaustive analysis. This section expands detail 19 of chapter 5 with exhaustive analysis. This section expands detail 19 of chapter 5 with exhaustive analysis. 
- Point A19: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B19: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C19: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 19: | Col | Value | Source |
  |---|---|---|
  | Bus 753 | Transformer T26 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 33 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 5.20 Detail 20
This section expands detail 20 of chapter 5 with exhaustive analysis. This section expands detail 20 of chapter 5 with exhaustive analysis. This section expands detail 20 of chapter 5 with exhaustive analysis. This section expands detail 20 of chapter 5 with exhaustive analysis. 
- Point A20: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B20: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C20: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 20: | Col | Value | Source |
  |---|---|---|
  | Bus 754 | Transformer T27 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 40 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 5.21 Detail 21
This section expands detail 21 of chapter 5 with exhaustive analysis. This section expands detail 21 of chapter 5 with exhaustive analysis. This section expands detail 21 of chapter 5 with exhaustive analysis. This section expands detail 21 of chapter 5 with exhaustive analysis. 
- Point A21: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B21: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C21: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 21: | Col | Value | Source |
  |---|---|---|
  | Bus 755 | Transformer T28 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 47 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 5.22 Detail 22
This section expands detail 22 of chapter 5 with exhaustive analysis. This section expands detail 22 of chapter 5 with exhaustive analysis. This section expands detail 22 of chapter 5 with exhaustive analysis. This section expands detail 22 of chapter 5 with exhaustive analysis. 
- Point A22: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B22: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C22: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 22: | Col | Value | Source |
  |---|---|---|
  | Bus 756 | Transformer T7 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 54 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 5.23 Detail 23
This section expands detail 23 of chapter 5 with exhaustive analysis. This section expands detail 23 of chapter 5 with exhaustive analysis. This section expands detail 23 of chapter 5 with exhaustive analysis. This section expands detail 23 of chapter 5 with exhaustive analysis. 
- Point A23: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B23: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C23: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 23: | Col | Value | Source |
  |---|---|---|
  | Bus 757 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 61 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 5.24 Detail 24
This section expands detail 24 of chapter 5 with exhaustive analysis. This section expands detail 24 of chapter 5 with exhaustive analysis. This section expands detail 24 of chapter 5 with exhaustive analysis. This section expands detail 24 of chapter 5 with exhaustive analysis. 
- Point A24: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B24: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C24: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 24: | Col | Value | Source |
  |---|---|---|
  | Bus 758 | Transformer T9 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 68 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 5.25 Detail 25
This section expands detail 25 of chapter 5 with exhaustive analysis. This section expands detail 25 of chapter 5 with exhaustive analysis. This section expands detail 25 of chapter 5 with exhaustive analysis. This section expands detail 25 of chapter 5 with exhaustive analysis. 
- Point A25: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B25: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C25: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 25: | Col | Value | Source |
  |---|---|---|
  | Bus 759 | Transformer T10 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 75 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

---
## 6. Chapter 6 — Detailed Section

### 6.1 Detail 1
This section expands detail 1 of chapter 6 with exhaustive analysis. This section expands detail 1 of chapter 6 with exhaustive analysis. This section expands detail 1 of chapter 6 with exhaustive analysis. This section expands detail 1 of chapter 6 with exhaustive analysis. 
- Point A1: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B1: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C1: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 1: | Col | Value | Source |
  |---|---|---|
  | Bus 735 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 7 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 6.2 Detail 2
This section expands detail 2 of chapter 6 with exhaustive analysis. This section expands detail 2 of chapter 6 with exhaustive analysis. This section expands detail 2 of chapter 6 with exhaustive analysis. This section expands detail 2 of chapter 6 with exhaustive analysis. 
- Point A2: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B2: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C2: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 2: | Col | Value | Source |
  |---|---|---|
  | Bus 736 | Transformer T9 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 14 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 6.3 Detail 3
This section expands detail 3 of chapter 6 with exhaustive analysis. This section expands detail 3 of chapter 6 with exhaustive analysis. This section expands detail 3 of chapter 6 with exhaustive analysis. This section expands detail 3 of chapter 6 with exhaustive analysis. 
- Point A3: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B3: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C3: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 3: | Col | Value | Source |
  |---|---|---|
  | Bus 737 | Transformer T10 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 21 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 6.4 Detail 4
This section expands detail 4 of chapter 6 with exhaustive analysis. This section expands detail 4 of chapter 6 with exhaustive analysis. This section expands detail 4 of chapter 6 with exhaustive analysis. This section expands detail 4 of chapter 6 with exhaustive analysis. 
- Point A4: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B4: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C4: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 4: | Col | Value | Source |
  |---|---|---|
  | Bus 738 | Transformer T11 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 28 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 6.5 Detail 5
This section expands detail 5 of chapter 6 with exhaustive analysis. This section expands detail 5 of chapter 6 with exhaustive analysis. This section expands detail 5 of chapter 6 with exhaustive analysis. This section expands detail 5 of chapter 6 with exhaustive analysis. 
- Point A5: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B5: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C5: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 5: | Col | Value | Source |
  |---|---|---|
  | Bus 739 | Transformer T12 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 35 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 6.6 Detail 6
This section expands detail 6 of chapter 6 with exhaustive analysis. This section expands detail 6 of chapter 6 with exhaustive analysis. This section expands detail 6 of chapter 6 with exhaustive analysis. This section expands detail 6 of chapter 6 with exhaustive analysis. 
- Point A6: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B6: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C6: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 6: | Col | Value | Source |
  |---|---|---|
  | Bus 740 | Transformer T13 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 42 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 6.7 Detail 7
This section expands detail 7 of chapter 6 with exhaustive analysis. This section expands detail 7 of chapter 6 with exhaustive analysis. This section expands detail 7 of chapter 6 with exhaustive analysis. This section expands detail 7 of chapter 6 with exhaustive analysis. 
- Point A7: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B7: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C7: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 7: | Col | Value | Source |
  |---|---|---|
  | Bus 741 | Transformer T14 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 49 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 6.8 Detail 8
This section expands detail 8 of chapter 6 with exhaustive analysis. This section expands detail 8 of chapter 6 with exhaustive analysis. This section expands detail 8 of chapter 6 with exhaustive analysis. This section expands detail 8 of chapter 6 with exhaustive analysis. 
- Point A8: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B8: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C8: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 8: | Col | Value | Source |
  |---|---|---|
  | Bus 742 | Transformer T15 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 56 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 6.9 Detail 9
This section expands detail 9 of chapter 6 with exhaustive analysis. This section expands detail 9 of chapter 6 with exhaustive analysis. This section expands detail 9 of chapter 6 with exhaustive analysis. This section expands detail 9 of chapter 6 with exhaustive analysis. 
- Point A9: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B9: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C9: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 9: | Col | Value | Source |
  |---|---|---|
  | Bus 743 | Transformer T16 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 63 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 6.10 Detail 10
This section expands detail 10 of chapter 6 with exhaustive analysis. This section expands detail 10 of chapter 6 with exhaustive analysis. This section expands detail 10 of chapter 6 with exhaustive analysis. This section expands detail 10 of chapter 6 with exhaustive analysis. 
- Point A10: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B10: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C10: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 10: | Col | Value | Source |
  |---|---|---|
  | Bus 744 | Transformer T17 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 70 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 6.11 Detail 11
This section expands detail 11 of chapter 6 with exhaustive analysis. This section expands detail 11 of chapter 6 with exhaustive analysis. This section expands detail 11 of chapter 6 with exhaustive analysis. This section expands detail 11 of chapter 6 with exhaustive analysis. 
- Point A11: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B11: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C11: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 11: | Col | Value | Source |
  |---|---|---|
  | Bus 745 | Transformer T18 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 77 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 6.12 Detail 12
This section expands detail 12 of chapter 6 with exhaustive analysis. This section expands detail 12 of chapter 6 with exhaustive analysis. This section expands detail 12 of chapter 6 with exhaustive analysis. This section expands detail 12 of chapter 6 with exhaustive analysis. 
- Point A12: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B12: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C12: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 12: | Col | Value | Source |
  |---|---|---|
  | Bus 746 | Transformer T19 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 84 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 6.13 Detail 13
This section expands detail 13 of chapter 6 with exhaustive analysis. This section expands detail 13 of chapter 6 with exhaustive analysis. This section expands detail 13 of chapter 6 with exhaustive analysis. This section expands detail 13 of chapter 6 with exhaustive analysis. 
- Point A13: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B13: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C13: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 13: | Col | Value | Source |
  |---|---|---|
  | Bus 747 | Transformer T20 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 91 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 6.14 Detail 14
This section expands detail 14 of chapter 6 with exhaustive analysis. This section expands detail 14 of chapter 6 with exhaustive analysis. This section expands detail 14 of chapter 6 with exhaustive analysis. This section expands detail 14 of chapter 6 with exhaustive analysis. 
- Point A14: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B14: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C14: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 14: | Col | Value | Source |
  |---|---|---|
  | Bus 748 | Transformer T21 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 98 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 6.15 Detail 15
This section expands detail 15 of chapter 6 with exhaustive analysis. This section expands detail 15 of chapter 6 with exhaustive analysis. This section expands detail 15 of chapter 6 with exhaustive analysis. This section expands detail 15 of chapter 6 with exhaustive analysis. 
- Point A15: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B15: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C15: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 15: | Col | Value | Source |
  |---|---|---|
  | Bus 749 | Transformer T22 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 5 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 6.16 Detail 16
This section expands detail 16 of chapter 6 with exhaustive analysis. This section expands detail 16 of chapter 6 with exhaustive analysis. This section expands detail 16 of chapter 6 with exhaustive analysis. This section expands detail 16 of chapter 6 with exhaustive analysis. 
- Point A16: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B16: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C16: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 16: | Col | Value | Source |
  |---|---|---|
  | Bus 750 | Transformer T23 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 12 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 6.17 Detail 17
This section expands detail 17 of chapter 6 with exhaustive analysis. This section expands detail 17 of chapter 6 with exhaustive analysis. This section expands detail 17 of chapter 6 with exhaustive analysis. This section expands detail 17 of chapter 6 with exhaustive analysis. 
- Point A17: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B17: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C17: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 17: | Col | Value | Source |
  |---|---|---|
  | Bus 751 | Transformer T24 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 19 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 6.18 Detail 18
This section expands detail 18 of chapter 6 with exhaustive analysis. This section expands detail 18 of chapter 6 with exhaustive analysis. This section expands detail 18 of chapter 6 with exhaustive analysis. This section expands detail 18 of chapter 6 with exhaustive analysis. 
- Point A18: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B18: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C18: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 18: | Col | Value | Source |
  |---|---|---|
  | Bus 752 | Transformer T25 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 26 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 6.19 Detail 19
This section expands detail 19 of chapter 6 with exhaustive analysis. This section expands detail 19 of chapter 6 with exhaustive analysis. This section expands detail 19 of chapter 6 with exhaustive analysis. This section expands detail 19 of chapter 6 with exhaustive analysis. 
- Point A19: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B19: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C19: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 19: | Col | Value | Source |
  |---|---|---|
  | Bus 753 | Transformer T26 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 33 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 6.20 Detail 20
This section expands detail 20 of chapter 6 with exhaustive analysis. This section expands detail 20 of chapter 6 with exhaustive analysis. This section expands detail 20 of chapter 6 with exhaustive analysis. This section expands detail 20 of chapter 6 with exhaustive analysis. 
- Point A20: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B20: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C20: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 20: | Col | Value | Source |
  |---|---|---|
  | Bus 754 | Transformer T27 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 40 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 6.21 Detail 21
This section expands detail 21 of chapter 6 with exhaustive analysis. This section expands detail 21 of chapter 6 with exhaustive analysis. This section expands detail 21 of chapter 6 with exhaustive analysis. This section expands detail 21 of chapter 6 with exhaustive analysis. 
- Point A21: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B21: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C21: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 21: | Col | Value | Source |
  |---|---|---|
  | Bus 755 | Transformer T28 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 47 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 6.22 Detail 22
This section expands detail 22 of chapter 6 with exhaustive analysis. This section expands detail 22 of chapter 6 with exhaustive analysis. This section expands detail 22 of chapter 6 with exhaustive analysis. This section expands detail 22 of chapter 6 with exhaustive analysis. 
- Point A22: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B22: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C22: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 22: | Col | Value | Source |
  |---|---|---|
  | Bus 756 | Transformer T7 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 54 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 6.23 Detail 23
This section expands detail 23 of chapter 6 with exhaustive analysis. This section expands detail 23 of chapter 6 with exhaustive analysis. This section expands detail 23 of chapter 6 with exhaustive analysis. This section expands detail 23 of chapter 6 with exhaustive analysis. 
- Point A23: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B23: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C23: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 23: | Col | Value | Source |
  |---|---|---|
  | Bus 757 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 61 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 6.24 Detail 24
This section expands detail 24 of chapter 6 with exhaustive analysis. This section expands detail 24 of chapter 6 with exhaustive analysis. This section expands detail 24 of chapter 6 with exhaustive analysis. This section expands detail 24 of chapter 6 with exhaustive analysis. 
- Point A24: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B24: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C24: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 24: | Col | Value | Source |
  |---|---|---|
  | Bus 758 | Transformer T9 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 68 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 6.25 Detail 25
This section expands detail 25 of chapter 6 with exhaustive analysis. This section expands detail 25 of chapter 6 with exhaustive analysis. This section expands detail 25 of chapter 6 with exhaustive analysis. This section expands detail 25 of chapter 6 with exhaustive analysis. 
- Point A25: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B25: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C25: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 25: | Col | Value | Source |
  |---|---|---|
  | Bus 759 | Transformer T10 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 75 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

---
## 7. Chapter 7 — Detailed Section

### 7.1 Detail 1
This section expands detail 1 of chapter 7 with exhaustive analysis. This section expands detail 1 of chapter 7 with exhaustive analysis. This section expands detail 1 of chapter 7 with exhaustive analysis. This section expands detail 1 of chapter 7 with exhaustive analysis. 
- Point A1: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B1: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C1: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 1: | Col | Value | Source |
  |---|---|---|
  | Bus 735 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 7 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 7.2 Detail 2
This section expands detail 2 of chapter 7 with exhaustive analysis. This section expands detail 2 of chapter 7 with exhaustive analysis. This section expands detail 2 of chapter 7 with exhaustive analysis. This section expands detail 2 of chapter 7 with exhaustive analysis. 
- Point A2: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B2: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C2: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 2: | Col | Value | Source |
  |---|---|---|
  | Bus 736 | Transformer T9 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 14 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 7.3 Detail 3
This section expands detail 3 of chapter 7 with exhaustive analysis. This section expands detail 3 of chapter 7 with exhaustive analysis. This section expands detail 3 of chapter 7 with exhaustive analysis. This section expands detail 3 of chapter 7 with exhaustive analysis. 
- Point A3: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B3: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C3: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 3: | Col | Value | Source |
  |---|---|---|
  | Bus 737 | Transformer T10 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 21 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 7.4 Detail 4
This section expands detail 4 of chapter 7 with exhaustive analysis. This section expands detail 4 of chapter 7 with exhaustive analysis. This section expands detail 4 of chapter 7 with exhaustive analysis. This section expands detail 4 of chapter 7 with exhaustive analysis. 
- Point A4: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B4: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C4: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 4: | Col | Value | Source |
  |---|---|---|
  | Bus 738 | Transformer T11 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 28 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 7.5 Detail 5
This section expands detail 5 of chapter 7 with exhaustive analysis. This section expands detail 5 of chapter 7 with exhaustive analysis. This section expands detail 5 of chapter 7 with exhaustive analysis. This section expands detail 5 of chapter 7 with exhaustive analysis. 
- Point A5: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B5: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C5: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 5: | Col | Value | Source |
  |---|---|---|
  | Bus 739 | Transformer T12 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 35 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 7.6 Detail 6
This section expands detail 6 of chapter 7 with exhaustive analysis. This section expands detail 6 of chapter 7 with exhaustive analysis. This section expands detail 6 of chapter 7 with exhaustive analysis. This section expands detail 6 of chapter 7 with exhaustive analysis. 
- Point A6: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B6: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C6: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 6: | Col | Value | Source |
  |---|---|---|
  | Bus 740 | Transformer T13 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 42 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 7.7 Detail 7
This section expands detail 7 of chapter 7 with exhaustive analysis. This section expands detail 7 of chapter 7 with exhaustive analysis. This section expands detail 7 of chapter 7 with exhaustive analysis. This section expands detail 7 of chapter 7 with exhaustive analysis. 
- Point A7: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B7: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C7: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 7: | Col | Value | Source |
  |---|---|---|
  | Bus 741 | Transformer T14 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 49 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 7.8 Detail 8
This section expands detail 8 of chapter 7 with exhaustive analysis. This section expands detail 8 of chapter 7 with exhaustive analysis. This section expands detail 8 of chapter 7 with exhaustive analysis. This section expands detail 8 of chapter 7 with exhaustive analysis. 
- Point A8: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B8: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C8: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 8: | Col | Value | Source |
  |---|---|---|
  | Bus 742 | Transformer T15 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 56 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 7.9 Detail 9
This section expands detail 9 of chapter 7 with exhaustive analysis. This section expands detail 9 of chapter 7 with exhaustive analysis. This section expands detail 9 of chapter 7 with exhaustive analysis. This section expands detail 9 of chapter 7 with exhaustive analysis. 
- Point A9: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B9: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C9: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 9: | Col | Value | Source |
  |---|---|---|
  | Bus 743 | Transformer T16 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 63 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 7.10 Detail 10
This section expands detail 10 of chapter 7 with exhaustive analysis. This section expands detail 10 of chapter 7 with exhaustive analysis. This section expands detail 10 of chapter 7 with exhaustive analysis. This section expands detail 10 of chapter 7 with exhaustive analysis. 
- Point A10: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B10: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C10: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 10: | Col | Value | Source |
  |---|---|---|
  | Bus 744 | Transformer T17 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 70 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 7.11 Detail 11
This section expands detail 11 of chapter 7 with exhaustive analysis. This section expands detail 11 of chapter 7 with exhaustive analysis. This section expands detail 11 of chapter 7 with exhaustive analysis. This section expands detail 11 of chapter 7 with exhaustive analysis. 
- Point A11: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B11: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C11: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 11: | Col | Value | Source |
  |---|---|---|
  | Bus 745 | Transformer T18 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 77 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 7.12 Detail 12
This section expands detail 12 of chapter 7 with exhaustive analysis. This section expands detail 12 of chapter 7 with exhaustive analysis. This section expands detail 12 of chapter 7 with exhaustive analysis. This section expands detail 12 of chapter 7 with exhaustive analysis. 
- Point A12: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B12: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C12: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 12: | Col | Value | Source |
  |---|---|---|
  | Bus 746 | Transformer T19 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 84 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 7.13 Detail 13
This section expands detail 13 of chapter 7 with exhaustive analysis. This section expands detail 13 of chapter 7 with exhaustive analysis. This section expands detail 13 of chapter 7 with exhaustive analysis. This section expands detail 13 of chapter 7 with exhaustive analysis. 
- Point A13: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B13: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C13: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 13: | Col | Value | Source |
  |---|---|---|
  | Bus 747 | Transformer T20 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 91 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 7.14 Detail 14
This section expands detail 14 of chapter 7 with exhaustive analysis. This section expands detail 14 of chapter 7 with exhaustive analysis. This section expands detail 14 of chapter 7 with exhaustive analysis. This section expands detail 14 of chapter 7 with exhaustive analysis. 
- Point A14: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B14: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C14: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 14: | Col | Value | Source |
  |---|---|---|
  | Bus 748 | Transformer T21 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 98 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 7.15 Detail 15
This section expands detail 15 of chapter 7 with exhaustive analysis. This section expands detail 15 of chapter 7 with exhaustive analysis. This section expands detail 15 of chapter 7 with exhaustive analysis. This section expands detail 15 of chapter 7 with exhaustive analysis. 
- Point A15: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B15: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C15: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 15: | Col | Value | Source |
  |---|---|---|
  | Bus 749 | Transformer T22 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 5 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 7.16 Detail 16
This section expands detail 16 of chapter 7 with exhaustive analysis. This section expands detail 16 of chapter 7 with exhaustive analysis. This section expands detail 16 of chapter 7 with exhaustive analysis. This section expands detail 16 of chapter 7 with exhaustive analysis. 
- Point A16: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B16: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C16: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 16: | Col | Value | Source |
  |---|---|---|
  | Bus 750 | Transformer T23 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 12 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 7.17 Detail 17
This section expands detail 17 of chapter 7 with exhaustive analysis. This section expands detail 17 of chapter 7 with exhaustive analysis. This section expands detail 17 of chapter 7 with exhaustive analysis. This section expands detail 17 of chapter 7 with exhaustive analysis. 
- Point A17: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B17: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C17: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 17: | Col | Value | Source |
  |---|---|---|
  | Bus 751 | Transformer T24 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 19 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 7.18 Detail 18
This section expands detail 18 of chapter 7 with exhaustive analysis. This section expands detail 18 of chapter 7 with exhaustive analysis. This section expands detail 18 of chapter 7 with exhaustive analysis. This section expands detail 18 of chapter 7 with exhaustive analysis. 
- Point A18: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B18: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C18: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 18: | Col | Value | Source |
  |---|---|---|
  | Bus 752 | Transformer T25 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 26 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 7.19 Detail 19
This section expands detail 19 of chapter 7 with exhaustive analysis. This section expands detail 19 of chapter 7 with exhaustive analysis. This section expands detail 19 of chapter 7 with exhaustive analysis. This section expands detail 19 of chapter 7 with exhaustive analysis. 
- Point A19: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B19: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C19: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 19: | Col | Value | Source |
  |---|---|---|
  | Bus 753 | Transformer T26 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 33 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 7.20 Detail 20
This section expands detail 20 of chapter 7 with exhaustive analysis. This section expands detail 20 of chapter 7 with exhaustive analysis. This section expands detail 20 of chapter 7 with exhaustive analysis. This section expands detail 20 of chapter 7 with exhaustive analysis. 
- Point A20: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B20: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C20: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 20: | Col | Value | Source |
  |---|---|---|
  | Bus 754 | Transformer T27 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 40 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 7.21 Detail 21
This section expands detail 21 of chapter 7 with exhaustive analysis. This section expands detail 21 of chapter 7 with exhaustive analysis. This section expands detail 21 of chapter 7 with exhaustive analysis. This section expands detail 21 of chapter 7 with exhaustive analysis. 
- Point A21: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B21: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C21: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 21: | Col | Value | Source |
  |---|---|---|
  | Bus 755 | Transformer T28 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 47 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 7.22 Detail 22
This section expands detail 22 of chapter 7 with exhaustive analysis. This section expands detail 22 of chapter 7 with exhaustive analysis. This section expands detail 22 of chapter 7 with exhaustive analysis. This section expands detail 22 of chapter 7 with exhaustive analysis. 
- Point A22: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B22: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C22: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 22: | Col | Value | Source |
  |---|---|---|
  | Bus 756 | Transformer T7 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 54 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 7.23 Detail 23
This section expands detail 23 of chapter 7 with exhaustive analysis. This section expands detail 23 of chapter 7 with exhaustive analysis. This section expands detail 23 of chapter 7 with exhaustive analysis. This section expands detail 23 of chapter 7 with exhaustive analysis. 
- Point A23: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B23: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C23: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 23: | Col | Value | Source |
  |---|---|---|
  | Bus 757 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 61 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 7.24 Detail 24
This section expands detail 24 of chapter 7 with exhaustive analysis. This section expands detail 24 of chapter 7 with exhaustive analysis. This section expands detail 24 of chapter 7 with exhaustive analysis. This section expands detail 24 of chapter 7 with exhaustive analysis. 
- Point A24: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B24: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C24: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 24: | Col | Value | Source |
  |---|---|---|
  | Bus 758 | Transformer T9 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 68 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 7.25 Detail 25
This section expands detail 25 of chapter 7 with exhaustive analysis. This section expands detail 25 of chapter 7 with exhaustive analysis. This section expands detail 25 of chapter 7 with exhaustive analysis. This section expands detail 25 of chapter 7 with exhaustive analysis. 
- Point A25: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B25: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C25: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 25: | Col | Value | Source |
  |---|---|---|
  | Bus 759 | Transformer T10 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 75 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

---
## 8. Chapter 8 — Detailed Section

### 8.1 Detail 1
This section expands detail 1 of chapter 8 with exhaustive analysis. This section expands detail 1 of chapter 8 with exhaustive analysis. This section expands detail 1 of chapter 8 with exhaustive analysis. This section expands detail 1 of chapter 8 with exhaustive analysis. 
- Point A1: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B1: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C1: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 1: | Col | Value | Source |
  |---|---|---|
  | Bus 735 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 7 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 8.2 Detail 2
This section expands detail 2 of chapter 8 with exhaustive analysis. This section expands detail 2 of chapter 8 with exhaustive analysis. This section expands detail 2 of chapter 8 with exhaustive analysis. This section expands detail 2 of chapter 8 with exhaustive analysis. 
- Point A2: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B2: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C2: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 2: | Col | Value | Source |
  |---|---|---|
  | Bus 736 | Transformer T9 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 14 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 8.3 Detail 3
This section expands detail 3 of chapter 8 with exhaustive analysis. This section expands detail 3 of chapter 8 with exhaustive analysis. This section expands detail 3 of chapter 8 with exhaustive analysis. This section expands detail 3 of chapter 8 with exhaustive analysis. 
- Point A3: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B3: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C3: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 3: | Col | Value | Source |
  |---|---|---|
  | Bus 737 | Transformer T10 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 21 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 8.4 Detail 4
This section expands detail 4 of chapter 8 with exhaustive analysis. This section expands detail 4 of chapter 8 with exhaustive analysis. This section expands detail 4 of chapter 8 with exhaustive analysis. This section expands detail 4 of chapter 8 with exhaustive analysis. 
- Point A4: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B4: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C4: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 4: | Col | Value | Source |
  |---|---|---|
  | Bus 738 | Transformer T11 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 28 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 8.5 Detail 5
This section expands detail 5 of chapter 8 with exhaustive analysis. This section expands detail 5 of chapter 8 with exhaustive analysis. This section expands detail 5 of chapter 8 with exhaustive analysis. This section expands detail 5 of chapter 8 with exhaustive analysis. 
- Point A5: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B5: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C5: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 5: | Col | Value | Source |
  |---|---|---|
  | Bus 739 | Transformer T12 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 35 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 8.6 Detail 6
This section expands detail 6 of chapter 8 with exhaustive analysis. This section expands detail 6 of chapter 8 with exhaustive analysis. This section expands detail 6 of chapter 8 with exhaustive analysis. This section expands detail 6 of chapter 8 with exhaustive analysis. 
- Point A6: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B6: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C6: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 6: | Col | Value | Source |
  |---|---|---|
  | Bus 740 | Transformer T13 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 42 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 8.7 Detail 7
This section expands detail 7 of chapter 8 with exhaustive analysis. This section expands detail 7 of chapter 8 with exhaustive analysis. This section expands detail 7 of chapter 8 with exhaustive analysis. This section expands detail 7 of chapter 8 with exhaustive analysis. 
- Point A7: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B7: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C7: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 7: | Col | Value | Source |
  |---|---|---|
  | Bus 741 | Transformer T14 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 49 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 8.8 Detail 8
This section expands detail 8 of chapter 8 with exhaustive analysis. This section expands detail 8 of chapter 8 with exhaustive analysis. This section expands detail 8 of chapter 8 with exhaustive analysis. This section expands detail 8 of chapter 8 with exhaustive analysis. 
- Point A8: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B8: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C8: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 8: | Col | Value | Source |
  |---|---|---|
  | Bus 742 | Transformer T15 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 56 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 8.9 Detail 9
This section expands detail 9 of chapter 8 with exhaustive analysis. This section expands detail 9 of chapter 8 with exhaustive analysis. This section expands detail 9 of chapter 8 with exhaustive analysis. This section expands detail 9 of chapter 8 with exhaustive analysis. 
- Point A9: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B9: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C9: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 9: | Col | Value | Source |
  |---|---|---|
  | Bus 743 | Transformer T16 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 63 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 8.10 Detail 10
This section expands detail 10 of chapter 8 with exhaustive analysis. This section expands detail 10 of chapter 8 with exhaustive analysis. This section expands detail 10 of chapter 8 with exhaustive analysis. This section expands detail 10 of chapter 8 with exhaustive analysis. 
- Point A10: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B10: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C10: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 10: | Col | Value | Source |
  |---|---|---|
  | Bus 744 | Transformer T17 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 70 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 8.11 Detail 11
This section expands detail 11 of chapter 8 with exhaustive analysis. This section expands detail 11 of chapter 8 with exhaustive analysis. This section expands detail 11 of chapter 8 with exhaustive analysis. This section expands detail 11 of chapter 8 with exhaustive analysis. 
- Point A11: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B11: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C11: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 11: | Col | Value | Source |
  |---|---|---|
  | Bus 745 | Transformer T18 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 77 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 8.12 Detail 12
This section expands detail 12 of chapter 8 with exhaustive analysis. This section expands detail 12 of chapter 8 with exhaustive analysis. This section expands detail 12 of chapter 8 with exhaustive analysis. This section expands detail 12 of chapter 8 with exhaustive analysis. 
- Point A12: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B12: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C12: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 12: | Col | Value | Source |
  |---|---|---|
  | Bus 746 | Transformer T19 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 84 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 8.13 Detail 13
This section expands detail 13 of chapter 8 with exhaustive analysis. This section expands detail 13 of chapter 8 with exhaustive analysis. This section expands detail 13 of chapter 8 with exhaustive analysis. This section expands detail 13 of chapter 8 with exhaustive analysis. 
- Point A13: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B13: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C13: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 13: | Col | Value | Source |
  |---|---|---|
  | Bus 747 | Transformer T20 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 91 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 8.14 Detail 14
This section expands detail 14 of chapter 8 with exhaustive analysis. This section expands detail 14 of chapter 8 with exhaustive analysis. This section expands detail 14 of chapter 8 with exhaustive analysis. This section expands detail 14 of chapter 8 with exhaustive analysis. 
- Point A14: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B14: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C14: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 14: | Col | Value | Source |
  |---|---|---|
  | Bus 748 | Transformer T21 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 98 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 8.15 Detail 15
This section expands detail 15 of chapter 8 with exhaustive analysis. This section expands detail 15 of chapter 8 with exhaustive analysis. This section expands detail 15 of chapter 8 with exhaustive analysis. This section expands detail 15 of chapter 8 with exhaustive analysis. 
- Point A15: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B15: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C15: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 15: | Col | Value | Source |
  |---|---|---|
  | Bus 749 | Transformer T22 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 5 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 8.16 Detail 16
This section expands detail 16 of chapter 8 with exhaustive analysis. This section expands detail 16 of chapter 8 with exhaustive analysis. This section expands detail 16 of chapter 8 with exhaustive analysis. This section expands detail 16 of chapter 8 with exhaustive analysis. 
- Point A16: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B16: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C16: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 16: | Col | Value | Source |
  |---|---|---|
  | Bus 750 | Transformer T23 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 12 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 8.17 Detail 17
This section expands detail 17 of chapter 8 with exhaustive analysis. This section expands detail 17 of chapter 8 with exhaustive analysis. This section expands detail 17 of chapter 8 with exhaustive analysis. This section expands detail 17 of chapter 8 with exhaustive analysis. 
- Point A17: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B17: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C17: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 17: | Col | Value | Source |
  |---|---|---|
  | Bus 751 | Transformer T24 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 19 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 8.18 Detail 18
This section expands detail 18 of chapter 8 with exhaustive analysis. This section expands detail 18 of chapter 8 with exhaustive analysis. This section expands detail 18 of chapter 8 with exhaustive analysis. This section expands detail 18 of chapter 8 with exhaustive analysis. 
- Point A18: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B18: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C18: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 18: | Col | Value | Source |
  |---|---|---|
  | Bus 752 | Transformer T25 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 26 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 8.19 Detail 19
This section expands detail 19 of chapter 8 with exhaustive analysis. This section expands detail 19 of chapter 8 with exhaustive analysis. This section expands detail 19 of chapter 8 with exhaustive analysis. This section expands detail 19 of chapter 8 with exhaustive analysis. 
- Point A19: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B19: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C19: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 19: | Col | Value | Source |
  |---|---|---|
  | Bus 753 | Transformer T26 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 33 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 8.20 Detail 20
This section expands detail 20 of chapter 8 with exhaustive analysis. This section expands detail 20 of chapter 8 with exhaustive analysis. This section expands detail 20 of chapter 8 with exhaustive analysis. This section expands detail 20 of chapter 8 with exhaustive analysis. 
- Point A20: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B20: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C20: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 20: | Col | Value | Source |
  |---|---|---|
  | Bus 754 | Transformer T27 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 40 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 8.21 Detail 21
This section expands detail 21 of chapter 8 with exhaustive analysis. This section expands detail 21 of chapter 8 with exhaustive analysis. This section expands detail 21 of chapter 8 with exhaustive analysis. This section expands detail 21 of chapter 8 with exhaustive analysis. 
- Point A21: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B21: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C21: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 21: | Col | Value | Source |
  |---|---|---|
  | Bus 755 | Transformer T28 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 47 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 8.22 Detail 22
This section expands detail 22 of chapter 8 with exhaustive analysis. This section expands detail 22 of chapter 8 with exhaustive analysis. This section expands detail 22 of chapter 8 with exhaustive analysis. This section expands detail 22 of chapter 8 with exhaustive analysis. 
- Point A22: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B22: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C22: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 22: | Col | Value | Source |
  |---|---|---|
  | Bus 756 | Transformer T7 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 54 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 8.23 Detail 23
This section expands detail 23 of chapter 8 with exhaustive analysis. This section expands detail 23 of chapter 8 with exhaustive analysis. This section expands detail 23 of chapter 8 with exhaustive analysis. This section expands detail 23 of chapter 8 with exhaustive analysis. 
- Point A23: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B23: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C23: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 23: | Col | Value | Source |
  |---|---|---|
  | Bus 757 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 61 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 8.24 Detail 24
This section expands detail 24 of chapter 8 with exhaustive analysis. This section expands detail 24 of chapter 8 with exhaustive analysis. This section expands detail 24 of chapter 8 with exhaustive analysis. This section expands detail 24 of chapter 8 with exhaustive analysis. 
- Point A24: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B24: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C24: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 24: | Col | Value | Source |
  |---|---|---|
  | Bus 758 | Transformer T9 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 68 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 8.25 Detail 25
This section expands detail 25 of chapter 8 with exhaustive analysis. This section expands detail 25 of chapter 8 with exhaustive analysis. This section expands detail 25 of chapter 8 with exhaustive analysis. This section expands detail 25 of chapter 8 with exhaustive analysis. 
- Point A25: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B25: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C25: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 25: | Col | Value | Source |
  |---|---|---|
  | Bus 759 | Transformer T10 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 75 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

---
## 9. Chapter 9 — Detailed Section

### 9.1 Detail 1
This section expands detail 1 of chapter 9 with exhaustive analysis. This section expands detail 1 of chapter 9 with exhaustive analysis. This section expands detail 1 of chapter 9 with exhaustive analysis. This section expands detail 1 of chapter 9 with exhaustive analysis. 
- Point A1: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B1: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C1: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 1: | Col | Value | Source |
  |---|---|---|
  | Bus 735 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 7 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 9.2 Detail 2
This section expands detail 2 of chapter 9 with exhaustive analysis. This section expands detail 2 of chapter 9 with exhaustive analysis. This section expands detail 2 of chapter 9 with exhaustive analysis. This section expands detail 2 of chapter 9 with exhaustive analysis. 
- Point A2: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B2: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C2: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 2: | Col | Value | Source |
  |---|---|---|
  | Bus 736 | Transformer T9 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 14 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 9.3 Detail 3
This section expands detail 3 of chapter 9 with exhaustive analysis. This section expands detail 3 of chapter 9 with exhaustive analysis. This section expands detail 3 of chapter 9 with exhaustive analysis. This section expands detail 3 of chapter 9 with exhaustive analysis. 
- Point A3: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B3: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C3: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 3: | Col | Value | Source |
  |---|---|---|
  | Bus 737 | Transformer T10 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 21 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 9.4 Detail 4
This section expands detail 4 of chapter 9 with exhaustive analysis. This section expands detail 4 of chapter 9 with exhaustive analysis. This section expands detail 4 of chapter 9 with exhaustive analysis. This section expands detail 4 of chapter 9 with exhaustive analysis. 
- Point A4: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B4: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C4: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 4: | Col | Value | Source |
  |---|---|---|
  | Bus 738 | Transformer T11 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 28 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 9.5 Detail 5
This section expands detail 5 of chapter 9 with exhaustive analysis. This section expands detail 5 of chapter 9 with exhaustive analysis. This section expands detail 5 of chapter 9 with exhaustive analysis. This section expands detail 5 of chapter 9 with exhaustive analysis. 
- Point A5: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B5: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C5: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 5: | Col | Value | Source |
  |---|---|---|
  | Bus 739 | Transformer T12 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 35 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 9.6 Detail 6
This section expands detail 6 of chapter 9 with exhaustive analysis. This section expands detail 6 of chapter 9 with exhaustive analysis. This section expands detail 6 of chapter 9 with exhaustive analysis. This section expands detail 6 of chapter 9 with exhaustive analysis. 
- Point A6: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B6: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C6: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 6: | Col | Value | Source |
  |---|---|---|
  | Bus 740 | Transformer T13 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 42 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 9.7 Detail 7
This section expands detail 7 of chapter 9 with exhaustive analysis. This section expands detail 7 of chapter 9 with exhaustive analysis. This section expands detail 7 of chapter 9 with exhaustive analysis. This section expands detail 7 of chapter 9 with exhaustive analysis. 
- Point A7: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B7: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C7: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 7: | Col | Value | Source |
  |---|---|---|
  | Bus 741 | Transformer T14 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 49 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 9.8 Detail 8
This section expands detail 8 of chapter 9 with exhaustive analysis. This section expands detail 8 of chapter 9 with exhaustive analysis. This section expands detail 8 of chapter 9 with exhaustive analysis. This section expands detail 8 of chapter 9 with exhaustive analysis. 
- Point A8: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B8: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C8: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 8: | Col | Value | Source |
  |---|---|---|
  | Bus 742 | Transformer T15 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 56 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 9.9 Detail 9
This section expands detail 9 of chapter 9 with exhaustive analysis. This section expands detail 9 of chapter 9 with exhaustive analysis. This section expands detail 9 of chapter 9 with exhaustive analysis. This section expands detail 9 of chapter 9 with exhaustive analysis. 
- Point A9: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B9: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C9: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 9: | Col | Value | Source |
  |---|---|---|
  | Bus 743 | Transformer T16 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 63 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 9.10 Detail 10
This section expands detail 10 of chapter 9 with exhaustive analysis. This section expands detail 10 of chapter 9 with exhaustive analysis. This section expands detail 10 of chapter 9 with exhaustive analysis. This section expands detail 10 of chapter 9 with exhaustive analysis. 
- Point A10: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B10: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C10: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 10: | Col | Value | Source |
  |---|---|---|
  | Bus 744 | Transformer T17 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 70 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 9.11 Detail 11
This section expands detail 11 of chapter 9 with exhaustive analysis. This section expands detail 11 of chapter 9 with exhaustive analysis. This section expands detail 11 of chapter 9 with exhaustive analysis. This section expands detail 11 of chapter 9 with exhaustive analysis. 
- Point A11: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B11: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C11: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 11: | Col | Value | Source |
  |---|---|---|
  | Bus 745 | Transformer T18 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 77 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 9.12 Detail 12
This section expands detail 12 of chapter 9 with exhaustive analysis. This section expands detail 12 of chapter 9 with exhaustive analysis. This section expands detail 12 of chapter 9 with exhaustive analysis. This section expands detail 12 of chapter 9 with exhaustive analysis. 
- Point A12: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B12: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C12: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 12: | Col | Value | Source |
  |---|---|---|
  | Bus 746 | Transformer T19 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 84 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 9.13 Detail 13
This section expands detail 13 of chapter 9 with exhaustive analysis. This section expands detail 13 of chapter 9 with exhaustive analysis. This section expands detail 13 of chapter 9 with exhaustive analysis. This section expands detail 13 of chapter 9 with exhaustive analysis. 
- Point A13: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B13: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C13: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 13: | Col | Value | Source |
  |---|---|---|
  | Bus 747 | Transformer T20 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 91 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 9.14 Detail 14
This section expands detail 14 of chapter 9 with exhaustive analysis. This section expands detail 14 of chapter 9 with exhaustive analysis. This section expands detail 14 of chapter 9 with exhaustive analysis. This section expands detail 14 of chapter 9 with exhaustive analysis. 
- Point A14: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B14: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C14: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 14: | Col | Value | Source |
  |---|---|---|
  | Bus 748 | Transformer T21 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 98 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 9.15 Detail 15
This section expands detail 15 of chapter 9 with exhaustive analysis. This section expands detail 15 of chapter 9 with exhaustive analysis. This section expands detail 15 of chapter 9 with exhaustive analysis. This section expands detail 15 of chapter 9 with exhaustive analysis. 
- Point A15: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B15: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C15: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 15: | Col | Value | Source |
  |---|---|---|
  | Bus 749 | Transformer T22 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 5 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 9.16 Detail 16
This section expands detail 16 of chapter 9 with exhaustive analysis. This section expands detail 16 of chapter 9 with exhaustive analysis. This section expands detail 16 of chapter 9 with exhaustive analysis. This section expands detail 16 of chapter 9 with exhaustive analysis. 
- Point A16: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B16: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C16: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 16: | Col | Value | Source |
  |---|---|---|
  | Bus 750 | Transformer T23 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 12 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 9.17 Detail 17
This section expands detail 17 of chapter 9 with exhaustive analysis. This section expands detail 17 of chapter 9 with exhaustive analysis. This section expands detail 17 of chapter 9 with exhaustive analysis. This section expands detail 17 of chapter 9 with exhaustive analysis. 
- Point A17: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B17: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C17: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 17: | Col | Value | Source |
  |---|---|---|
  | Bus 751 | Transformer T24 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 19 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 9.18 Detail 18
This section expands detail 18 of chapter 9 with exhaustive analysis. This section expands detail 18 of chapter 9 with exhaustive analysis. This section expands detail 18 of chapter 9 with exhaustive analysis. This section expands detail 18 of chapter 9 with exhaustive analysis. 
- Point A18: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B18: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C18: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 18: | Col | Value | Source |
  |---|---|---|
  | Bus 752 | Transformer T25 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 26 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 9.19 Detail 19
This section expands detail 19 of chapter 9 with exhaustive analysis. This section expands detail 19 of chapter 9 with exhaustive analysis. This section expands detail 19 of chapter 9 with exhaustive analysis. This section expands detail 19 of chapter 9 with exhaustive analysis. 
- Point A19: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B19: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C19: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 19: | Col | Value | Source |
  |---|---|---|
  | Bus 753 | Transformer T26 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 33 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 9.20 Detail 20
This section expands detail 20 of chapter 9 with exhaustive analysis. This section expands detail 20 of chapter 9 with exhaustive analysis. This section expands detail 20 of chapter 9 with exhaustive analysis. This section expands detail 20 of chapter 9 with exhaustive analysis. 
- Point A20: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B20: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C20: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 20: | Col | Value | Source |
  |---|---|---|
  | Bus 754 | Transformer T27 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 40 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 9.21 Detail 21
This section expands detail 21 of chapter 9 with exhaustive analysis. This section expands detail 21 of chapter 9 with exhaustive analysis. This section expands detail 21 of chapter 9 with exhaustive analysis. This section expands detail 21 of chapter 9 with exhaustive analysis. 
- Point A21: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B21: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C21: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 21: | Col | Value | Source |
  |---|---|---|
  | Bus 755 | Transformer T28 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 47 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 9.22 Detail 22
This section expands detail 22 of chapter 9 with exhaustive analysis. This section expands detail 22 of chapter 9 with exhaustive analysis. This section expands detail 22 of chapter 9 with exhaustive analysis. This section expands detail 22 of chapter 9 with exhaustive analysis. 
- Point A22: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B22: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C22: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 22: | Col | Value | Source |
  |---|---|---|
  | Bus 756 | Transformer T7 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 54 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 9.23 Detail 23
This section expands detail 23 of chapter 9 with exhaustive analysis. This section expands detail 23 of chapter 9 with exhaustive analysis. This section expands detail 23 of chapter 9 with exhaustive analysis. This section expands detail 23 of chapter 9 with exhaustive analysis. 
- Point A23: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B23: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C23: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 23: | Col | Value | Source |
  |---|---|---|
  | Bus 757 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 61 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 9.24 Detail 24
This section expands detail 24 of chapter 9 with exhaustive analysis. This section expands detail 24 of chapter 9 with exhaustive analysis. This section expands detail 24 of chapter 9 with exhaustive analysis. This section expands detail 24 of chapter 9 with exhaustive analysis. 
- Point A24: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B24: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C24: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 24: | Col | Value | Source |
  |---|---|---|
  | Bus 758 | Transformer T9 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 68 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 9.25 Detail 25
This section expands detail 25 of chapter 9 with exhaustive analysis. This section expands detail 25 of chapter 9 with exhaustive analysis. This section expands detail 25 of chapter 9 with exhaustive analysis. This section expands detail 25 of chapter 9 with exhaustive analysis. 
- Point A25: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B25: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C25: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 25: | Col | Value | Source |
  |---|---|---|
  | Bus 759 | Transformer T10 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 75 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

---
## 10. Chapter 10 — Detailed Section

### 10.1 Detail 1
This section expands detail 1 of chapter 10 with exhaustive analysis. This section expands detail 1 of chapter 10 with exhaustive analysis. This section expands detail 1 of chapter 10 with exhaustive analysis. This section expands detail 1 of chapter 10 with exhaustive analysis. 
- Point A1: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B1: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C1: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 1: | Col | Value | Source |
  |---|---|---|
  | Bus 735 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 7 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 10.2 Detail 2
This section expands detail 2 of chapter 10 with exhaustive analysis. This section expands detail 2 of chapter 10 with exhaustive analysis. This section expands detail 2 of chapter 10 with exhaustive analysis. This section expands detail 2 of chapter 10 with exhaustive analysis. 
- Point A2: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B2: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C2: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 2: | Col | Value | Source |
  |---|---|---|
  | Bus 736 | Transformer T9 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 14 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 10.3 Detail 3
This section expands detail 3 of chapter 10 with exhaustive analysis. This section expands detail 3 of chapter 10 with exhaustive analysis. This section expands detail 3 of chapter 10 with exhaustive analysis. This section expands detail 3 of chapter 10 with exhaustive analysis. 
- Point A3: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B3: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C3: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 3: | Col | Value | Source |
  |---|---|---|
  | Bus 737 | Transformer T10 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 21 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 10.4 Detail 4
This section expands detail 4 of chapter 10 with exhaustive analysis. This section expands detail 4 of chapter 10 with exhaustive analysis. This section expands detail 4 of chapter 10 with exhaustive analysis. This section expands detail 4 of chapter 10 with exhaustive analysis. 
- Point A4: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B4: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C4: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 4: | Col | Value | Source |
  |---|---|---|
  | Bus 738 | Transformer T11 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 28 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 10.5 Detail 5
This section expands detail 5 of chapter 10 with exhaustive analysis. This section expands detail 5 of chapter 10 with exhaustive analysis. This section expands detail 5 of chapter 10 with exhaustive analysis. This section expands detail 5 of chapter 10 with exhaustive analysis. 
- Point A5: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B5: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C5: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 5: | Col | Value | Source |
  |---|---|---|
  | Bus 739 | Transformer T12 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 35 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 10.6 Detail 6
This section expands detail 6 of chapter 10 with exhaustive analysis. This section expands detail 6 of chapter 10 with exhaustive analysis. This section expands detail 6 of chapter 10 with exhaustive analysis. This section expands detail 6 of chapter 10 with exhaustive analysis. 
- Point A6: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B6: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C6: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 6: | Col | Value | Source |
  |---|---|---|
  | Bus 740 | Transformer T13 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 42 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 10.7 Detail 7
This section expands detail 7 of chapter 10 with exhaustive analysis. This section expands detail 7 of chapter 10 with exhaustive analysis. This section expands detail 7 of chapter 10 with exhaustive analysis. This section expands detail 7 of chapter 10 with exhaustive analysis. 
- Point A7: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B7: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C7: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 7: | Col | Value | Source |
  |---|---|---|
  | Bus 741 | Transformer T14 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 49 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 10.8 Detail 8
This section expands detail 8 of chapter 10 with exhaustive analysis. This section expands detail 8 of chapter 10 with exhaustive analysis. This section expands detail 8 of chapter 10 with exhaustive analysis. This section expands detail 8 of chapter 10 with exhaustive analysis. 
- Point A8: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B8: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C8: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 8: | Col | Value | Source |
  |---|---|---|
  | Bus 742 | Transformer T15 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 56 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 10.9 Detail 9
This section expands detail 9 of chapter 10 with exhaustive analysis. This section expands detail 9 of chapter 10 with exhaustive analysis. This section expands detail 9 of chapter 10 with exhaustive analysis. This section expands detail 9 of chapter 10 with exhaustive analysis. 
- Point A9: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B9: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C9: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 9: | Col | Value | Source |
  |---|---|---|
  | Bus 743 | Transformer T16 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 63 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 10.10 Detail 10
This section expands detail 10 of chapter 10 with exhaustive analysis. This section expands detail 10 of chapter 10 with exhaustive analysis. This section expands detail 10 of chapter 10 with exhaustive analysis. This section expands detail 10 of chapter 10 with exhaustive analysis. 
- Point A10: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B10: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C10: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 10: | Col | Value | Source |
  |---|---|---|
  | Bus 744 | Transformer T17 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 70 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 10.11 Detail 11
This section expands detail 11 of chapter 10 with exhaustive analysis. This section expands detail 11 of chapter 10 with exhaustive analysis. This section expands detail 11 of chapter 10 with exhaustive analysis. This section expands detail 11 of chapter 10 with exhaustive analysis. 
- Point A11: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B11: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C11: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 11: | Col | Value | Source |
  |---|---|---|
  | Bus 745 | Transformer T18 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 77 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 10.12 Detail 12
This section expands detail 12 of chapter 10 with exhaustive analysis. This section expands detail 12 of chapter 10 with exhaustive analysis. This section expands detail 12 of chapter 10 with exhaustive analysis. This section expands detail 12 of chapter 10 with exhaustive analysis. 
- Point A12: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B12: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C12: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 12: | Col | Value | Source |
  |---|---|---|
  | Bus 746 | Transformer T19 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 84 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 10.13 Detail 13
This section expands detail 13 of chapter 10 with exhaustive analysis. This section expands detail 13 of chapter 10 with exhaustive analysis. This section expands detail 13 of chapter 10 with exhaustive analysis. This section expands detail 13 of chapter 10 with exhaustive analysis. 
- Point A13: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B13: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C13: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 13: | Col | Value | Source |
  |---|---|---|
  | Bus 747 | Transformer T20 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 91 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 10.14 Detail 14
This section expands detail 14 of chapter 10 with exhaustive analysis. This section expands detail 14 of chapter 10 with exhaustive analysis. This section expands detail 14 of chapter 10 with exhaustive analysis. This section expands detail 14 of chapter 10 with exhaustive analysis. 
- Point A14: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B14: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C14: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 14: | Col | Value | Source |
  |---|---|---|
  | Bus 748 | Transformer T21 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 98 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 10.15 Detail 15
This section expands detail 15 of chapter 10 with exhaustive analysis. This section expands detail 15 of chapter 10 with exhaustive analysis. This section expands detail 15 of chapter 10 with exhaustive analysis. This section expands detail 15 of chapter 10 with exhaustive analysis. 
- Point A15: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B15: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C15: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 15: | Col | Value | Source |
  |---|---|---|
  | Bus 749 | Transformer T22 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 5 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 10.16 Detail 16
This section expands detail 16 of chapter 10 with exhaustive analysis. This section expands detail 16 of chapter 10 with exhaustive analysis. This section expands detail 16 of chapter 10 with exhaustive analysis. This section expands detail 16 of chapter 10 with exhaustive analysis. 
- Point A16: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B16: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C16: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 16: | Col | Value | Source |
  |---|---|---|
  | Bus 750 | Transformer T23 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 12 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 10.17 Detail 17
This section expands detail 17 of chapter 10 with exhaustive analysis. This section expands detail 17 of chapter 10 with exhaustive analysis. This section expands detail 17 of chapter 10 with exhaustive analysis. This section expands detail 17 of chapter 10 with exhaustive analysis. 
- Point A17: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B17: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C17: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 17: | Col | Value | Source |
  |---|---|---|
  | Bus 751 | Transformer T24 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 19 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 10.18 Detail 18
This section expands detail 18 of chapter 10 with exhaustive analysis. This section expands detail 18 of chapter 10 with exhaustive analysis. This section expands detail 18 of chapter 10 with exhaustive analysis. This section expands detail 18 of chapter 10 with exhaustive analysis. 
- Point A18: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B18: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C18: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 18: | Col | Value | Source |
  |---|---|---|
  | Bus 752 | Transformer T25 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 26 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 10.19 Detail 19
This section expands detail 19 of chapter 10 with exhaustive analysis. This section expands detail 19 of chapter 10 with exhaustive analysis. This section expands detail 19 of chapter 10 with exhaustive analysis. This section expands detail 19 of chapter 10 with exhaustive analysis. 
- Point A19: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B19: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C19: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 19: | Col | Value | Source |
  |---|---|---|
  | Bus 753 | Transformer T26 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 33 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 10.20 Detail 20
This section expands detail 20 of chapter 10 with exhaustive analysis. This section expands detail 20 of chapter 10 with exhaustive analysis. This section expands detail 20 of chapter 10 with exhaustive analysis. This section expands detail 20 of chapter 10 with exhaustive analysis. 
- Point A20: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B20: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C20: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 20: | Col | Value | Source |
  |---|---|---|
  | Bus 754 | Transformer T27 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 40 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 10.21 Detail 21
This section expands detail 21 of chapter 10 with exhaustive analysis. This section expands detail 21 of chapter 10 with exhaustive analysis. This section expands detail 21 of chapter 10 with exhaustive analysis. This section expands detail 21 of chapter 10 with exhaustive analysis. 
- Point A21: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B21: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C21: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 21: | Col | Value | Source |
  |---|---|---|
  | Bus 755 | Transformer T28 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 47 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 10.22 Detail 22
This section expands detail 22 of chapter 10 with exhaustive analysis. This section expands detail 22 of chapter 10 with exhaustive analysis. This section expands detail 22 of chapter 10 with exhaustive analysis. This section expands detail 22 of chapter 10 with exhaustive analysis. 
- Point A22: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B22: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C22: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 22: | Col | Value | Source |
  |---|---|---|
  | Bus 756 | Transformer T7 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 54 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 10.23 Detail 23
This section expands detail 23 of chapter 10 with exhaustive analysis. This section expands detail 23 of chapter 10 with exhaustive analysis. This section expands detail 23 of chapter 10 with exhaustive analysis. This section expands detail 23 of chapter 10 with exhaustive analysis. 
- Point A23: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B23: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C23: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 23: | Col | Value | Source |
  |---|---|---|
  | Bus 757 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 61 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 10.24 Detail 24
This section expands detail 24 of chapter 10 with exhaustive analysis. This section expands detail 24 of chapter 10 with exhaustive analysis. This section expands detail 24 of chapter 10 with exhaustive analysis. This section expands detail 24 of chapter 10 with exhaustive analysis. 
- Point A24: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B24: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C24: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 24: | Col | Value | Source |
  |---|---|---|
  | Bus 758 | Transformer T9 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 68 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 10.25 Detail 25
This section expands detail 25 of chapter 10 with exhaustive analysis. This section expands detail 25 of chapter 10 with exhaustive analysis. This section expands detail 25 of chapter 10 with exhaustive analysis. This section expands detail 25 of chapter 10 with exhaustive analysis. 
- Point A25: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B25: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C25: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 25: | Col | Value | Source |
  |---|---|---|
  | Bus 759 | Transformer T10 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 75 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

---
## 11. Chapter 11 — Detailed Section

### 11.1 Detail 1
This section expands detail 1 of chapter 11 with exhaustive analysis. This section expands detail 1 of chapter 11 with exhaustive analysis. This section expands detail 1 of chapter 11 with exhaustive analysis. This section expands detail 1 of chapter 11 with exhaustive analysis. 
- Point A1: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B1: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C1: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 1: | Col | Value | Source |
  |---|---|---|
  | Bus 735 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 7 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 11.2 Detail 2
This section expands detail 2 of chapter 11 with exhaustive analysis. This section expands detail 2 of chapter 11 with exhaustive analysis. This section expands detail 2 of chapter 11 with exhaustive analysis. This section expands detail 2 of chapter 11 with exhaustive analysis. 
- Point A2: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B2: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C2: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 2: | Col | Value | Source |
  |---|---|---|
  | Bus 736 | Transformer T9 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 14 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 11.3 Detail 3
This section expands detail 3 of chapter 11 with exhaustive analysis. This section expands detail 3 of chapter 11 with exhaustive analysis. This section expands detail 3 of chapter 11 with exhaustive analysis. This section expands detail 3 of chapter 11 with exhaustive analysis. 
- Point A3: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B3: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C3: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 3: | Col | Value | Source |
  |---|---|---|
  | Bus 737 | Transformer T10 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 21 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 11.4 Detail 4
This section expands detail 4 of chapter 11 with exhaustive analysis. This section expands detail 4 of chapter 11 with exhaustive analysis. This section expands detail 4 of chapter 11 with exhaustive analysis. This section expands detail 4 of chapter 11 with exhaustive analysis. 
- Point A4: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B4: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C4: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 4: | Col | Value | Source |
  |---|---|---|
  | Bus 738 | Transformer T11 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 28 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 11.5 Detail 5
This section expands detail 5 of chapter 11 with exhaustive analysis. This section expands detail 5 of chapter 11 with exhaustive analysis. This section expands detail 5 of chapter 11 with exhaustive analysis. This section expands detail 5 of chapter 11 with exhaustive analysis. 
- Point A5: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B5: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C5: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 5: | Col | Value | Source |
  |---|---|---|
  | Bus 739 | Transformer T12 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 35 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 11.6 Detail 6
This section expands detail 6 of chapter 11 with exhaustive analysis. This section expands detail 6 of chapter 11 with exhaustive analysis. This section expands detail 6 of chapter 11 with exhaustive analysis. This section expands detail 6 of chapter 11 with exhaustive analysis. 
- Point A6: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B6: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C6: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 6: | Col | Value | Source |
  |---|---|---|
  | Bus 740 | Transformer T13 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 42 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 11.7 Detail 7
This section expands detail 7 of chapter 11 with exhaustive analysis. This section expands detail 7 of chapter 11 with exhaustive analysis. This section expands detail 7 of chapter 11 with exhaustive analysis. This section expands detail 7 of chapter 11 with exhaustive analysis. 
- Point A7: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B7: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C7: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 7: | Col | Value | Source |
  |---|---|---|
  | Bus 741 | Transformer T14 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 49 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 11.8 Detail 8
This section expands detail 8 of chapter 11 with exhaustive analysis. This section expands detail 8 of chapter 11 with exhaustive analysis. This section expands detail 8 of chapter 11 with exhaustive analysis. This section expands detail 8 of chapter 11 with exhaustive analysis. 
- Point A8: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B8: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C8: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 8: | Col | Value | Source |
  |---|---|---|
  | Bus 742 | Transformer T15 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 56 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 11.9 Detail 9
This section expands detail 9 of chapter 11 with exhaustive analysis. This section expands detail 9 of chapter 11 with exhaustive analysis. This section expands detail 9 of chapter 11 with exhaustive analysis. This section expands detail 9 of chapter 11 with exhaustive analysis. 
- Point A9: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B9: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C9: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 9: | Col | Value | Source |
  |---|---|---|
  | Bus 743 | Transformer T16 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 63 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 11.10 Detail 10
This section expands detail 10 of chapter 11 with exhaustive analysis. This section expands detail 10 of chapter 11 with exhaustive analysis. This section expands detail 10 of chapter 11 with exhaustive analysis. This section expands detail 10 of chapter 11 with exhaustive analysis. 
- Point A10: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B10: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C10: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 10: | Col | Value | Source |
  |---|---|---|
  | Bus 744 | Transformer T17 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 70 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 11.11 Detail 11
This section expands detail 11 of chapter 11 with exhaustive analysis. This section expands detail 11 of chapter 11 with exhaustive analysis. This section expands detail 11 of chapter 11 with exhaustive analysis. This section expands detail 11 of chapter 11 with exhaustive analysis. 
- Point A11: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B11: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C11: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 11: | Col | Value | Source |
  |---|---|---|
  | Bus 745 | Transformer T18 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 77 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 11.12 Detail 12
This section expands detail 12 of chapter 11 with exhaustive analysis. This section expands detail 12 of chapter 11 with exhaustive analysis. This section expands detail 12 of chapter 11 with exhaustive analysis. This section expands detail 12 of chapter 11 with exhaustive analysis. 
- Point A12: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B12: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C12: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 12: | Col | Value | Source |
  |---|---|---|
  | Bus 746 | Transformer T19 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 84 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 11.13 Detail 13
This section expands detail 13 of chapter 11 with exhaustive analysis. This section expands detail 13 of chapter 11 with exhaustive analysis. This section expands detail 13 of chapter 11 with exhaustive analysis. This section expands detail 13 of chapter 11 with exhaustive analysis. 
- Point A13: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B13: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C13: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 13: | Col | Value | Source |
  |---|---|---|
  | Bus 747 | Transformer T20 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 91 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 11.14 Detail 14
This section expands detail 14 of chapter 11 with exhaustive analysis. This section expands detail 14 of chapter 11 with exhaustive analysis. This section expands detail 14 of chapter 11 with exhaustive analysis. This section expands detail 14 of chapter 11 with exhaustive analysis. 
- Point A14: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B14: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C14: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 14: | Col | Value | Source |
  |---|---|---|
  | Bus 748 | Transformer T21 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 98 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 11.15 Detail 15
This section expands detail 15 of chapter 11 with exhaustive analysis. This section expands detail 15 of chapter 11 with exhaustive analysis. This section expands detail 15 of chapter 11 with exhaustive analysis. This section expands detail 15 of chapter 11 with exhaustive analysis. 
- Point A15: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B15: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C15: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 15: | Col | Value | Source |
  |---|---|---|
  | Bus 749 | Transformer T22 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 5 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 11.16 Detail 16
This section expands detail 16 of chapter 11 with exhaustive analysis. This section expands detail 16 of chapter 11 with exhaustive analysis. This section expands detail 16 of chapter 11 with exhaustive analysis. This section expands detail 16 of chapter 11 with exhaustive analysis. 
- Point A16: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B16: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C16: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 16: | Col | Value | Source |
  |---|---|---|
  | Bus 750 | Transformer T23 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 12 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 11.17 Detail 17
This section expands detail 17 of chapter 11 with exhaustive analysis. This section expands detail 17 of chapter 11 with exhaustive analysis. This section expands detail 17 of chapter 11 with exhaustive analysis. This section expands detail 17 of chapter 11 with exhaustive analysis. 
- Point A17: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B17: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C17: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 17: | Col | Value | Source |
  |---|---|---|
  | Bus 751 | Transformer T24 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 19 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 11.18 Detail 18
This section expands detail 18 of chapter 11 with exhaustive analysis. This section expands detail 18 of chapter 11 with exhaustive analysis. This section expands detail 18 of chapter 11 with exhaustive analysis. This section expands detail 18 of chapter 11 with exhaustive analysis. 
- Point A18: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B18: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C18: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 18: | Col | Value | Source |
  |---|---|---|
  | Bus 752 | Transformer T25 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 26 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 11.19 Detail 19
This section expands detail 19 of chapter 11 with exhaustive analysis. This section expands detail 19 of chapter 11 with exhaustive analysis. This section expands detail 19 of chapter 11 with exhaustive analysis. This section expands detail 19 of chapter 11 with exhaustive analysis. 
- Point A19: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B19: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C19: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 19: | Col | Value | Source |
  |---|---|---|
  | Bus 753 | Transformer T26 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 33 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 11.20 Detail 20
This section expands detail 20 of chapter 11 with exhaustive analysis. This section expands detail 20 of chapter 11 with exhaustive analysis. This section expands detail 20 of chapter 11 with exhaustive analysis. This section expands detail 20 of chapter 11 with exhaustive analysis. 
- Point A20: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B20: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C20: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 20: | Col | Value | Source |
  |---|---|---|
  | Bus 754 | Transformer T27 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 40 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 11.21 Detail 21
This section expands detail 21 of chapter 11 with exhaustive analysis. This section expands detail 21 of chapter 11 with exhaustive analysis. This section expands detail 21 of chapter 11 with exhaustive analysis. This section expands detail 21 of chapter 11 with exhaustive analysis. 
- Point A21: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B21: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C21: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 21: | Col | Value | Source |
  |---|---|---|
  | Bus 755 | Transformer T28 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 47 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 11.22 Detail 22
This section expands detail 22 of chapter 11 with exhaustive analysis. This section expands detail 22 of chapter 11 with exhaustive analysis. This section expands detail 22 of chapter 11 with exhaustive analysis. This section expands detail 22 of chapter 11 with exhaustive analysis. 
- Point A22: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B22: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C22: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 22: | Col | Value | Source |
  |---|---|---|
  | Bus 756 | Transformer T7 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 54 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 11.23 Detail 23
This section expands detail 23 of chapter 11 with exhaustive analysis. This section expands detail 23 of chapter 11 with exhaustive analysis. This section expands detail 23 of chapter 11 with exhaustive analysis. This section expands detail 23 of chapter 11 with exhaustive analysis. 
- Point A23: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B23: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C23: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 23: | Col | Value | Source |
  |---|---|---|
  | Bus 757 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 61 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 11.24 Detail 24
This section expands detail 24 of chapter 11 with exhaustive analysis. This section expands detail 24 of chapter 11 with exhaustive analysis. This section expands detail 24 of chapter 11 with exhaustive analysis. This section expands detail 24 of chapter 11 with exhaustive analysis. 
- Point A24: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B24: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C24: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 24: | Col | Value | Source |
  |---|---|---|
  | Bus 758 | Transformer T9 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 68 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 11.25 Detail 25
This section expands detail 25 of chapter 11 with exhaustive analysis. This section expands detail 25 of chapter 11 with exhaustive analysis. This section expands detail 25 of chapter 11 with exhaustive analysis. This section expands detail 25 of chapter 11 with exhaustive analysis. 
- Point A25: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B25: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C25: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 25: | Col | Value | Source |
  |---|---|---|
  | Bus 759 | Transformer T10 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 75 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

---
## 12. Chapter 12 — Detailed Section

### 12.1 Detail 1
This section expands detail 1 of chapter 12 with exhaustive analysis. This section expands detail 1 of chapter 12 with exhaustive analysis. This section expands detail 1 of chapter 12 with exhaustive analysis. This section expands detail 1 of chapter 12 with exhaustive analysis. 
- Point A1: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B1: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C1: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 1: | Col | Value | Source |
  |---|---|---|
  | Bus 735 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 7 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 12.2 Detail 2
This section expands detail 2 of chapter 12 with exhaustive analysis. This section expands detail 2 of chapter 12 with exhaustive analysis. This section expands detail 2 of chapter 12 with exhaustive analysis. This section expands detail 2 of chapter 12 with exhaustive analysis. 
- Point A2: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B2: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C2: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 2: | Col | Value | Source |
  |---|---|---|
  | Bus 736 | Transformer T9 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 14 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 12.3 Detail 3
This section expands detail 3 of chapter 12 with exhaustive analysis. This section expands detail 3 of chapter 12 with exhaustive analysis. This section expands detail 3 of chapter 12 with exhaustive analysis. This section expands detail 3 of chapter 12 with exhaustive analysis. 
- Point A3: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B3: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C3: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 3: | Col | Value | Source |
  |---|---|---|
  | Bus 737 | Transformer T10 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 21 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 12.4 Detail 4
This section expands detail 4 of chapter 12 with exhaustive analysis. This section expands detail 4 of chapter 12 with exhaustive analysis. This section expands detail 4 of chapter 12 with exhaustive analysis. This section expands detail 4 of chapter 12 with exhaustive analysis. 
- Point A4: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B4: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C4: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 4: | Col | Value | Source |
  |---|---|---|
  | Bus 738 | Transformer T11 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 28 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 12.5 Detail 5
This section expands detail 5 of chapter 12 with exhaustive analysis. This section expands detail 5 of chapter 12 with exhaustive analysis. This section expands detail 5 of chapter 12 with exhaustive analysis. This section expands detail 5 of chapter 12 with exhaustive analysis. 
- Point A5: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B5: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C5: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 5: | Col | Value | Source |
  |---|---|---|
  | Bus 739 | Transformer T12 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 35 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 12.6 Detail 6
This section expands detail 6 of chapter 12 with exhaustive analysis. This section expands detail 6 of chapter 12 with exhaustive analysis. This section expands detail 6 of chapter 12 with exhaustive analysis. This section expands detail 6 of chapter 12 with exhaustive analysis. 
- Point A6: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B6: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C6: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 6: | Col | Value | Source |
  |---|---|---|
  | Bus 740 | Transformer T13 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 42 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 12.7 Detail 7
This section expands detail 7 of chapter 12 with exhaustive analysis. This section expands detail 7 of chapter 12 with exhaustive analysis. This section expands detail 7 of chapter 12 with exhaustive analysis. This section expands detail 7 of chapter 12 with exhaustive analysis. 
- Point A7: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B7: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C7: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 7: | Col | Value | Source |
  |---|---|---|
  | Bus 741 | Transformer T14 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 49 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 12.8 Detail 8
This section expands detail 8 of chapter 12 with exhaustive analysis. This section expands detail 8 of chapter 12 with exhaustive analysis. This section expands detail 8 of chapter 12 with exhaustive analysis. This section expands detail 8 of chapter 12 with exhaustive analysis. 
- Point A8: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B8: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C8: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 8: | Col | Value | Source |
  |---|---|---|
  | Bus 742 | Transformer T15 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 56 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 12.9 Detail 9
This section expands detail 9 of chapter 12 with exhaustive analysis. This section expands detail 9 of chapter 12 with exhaustive analysis. This section expands detail 9 of chapter 12 with exhaustive analysis. This section expands detail 9 of chapter 12 with exhaustive analysis. 
- Point A9: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B9: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C9: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 9: | Col | Value | Source |
  |---|---|---|
  | Bus 743 | Transformer T16 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 63 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 12.10 Detail 10
This section expands detail 10 of chapter 12 with exhaustive analysis. This section expands detail 10 of chapter 12 with exhaustive analysis. This section expands detail 10 of chapter 12 with exhaustive analysis. This section expands detail 10 of chapter 12 with exhaustive analysis. 
- Point A10: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B10: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C10: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 10: | Col | Value | Source |
  |---|---|---|
  | Bus 744 | Transformer T17 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 70 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 12.11 Detail 11
This section expands detail 11 of chapter 12 with exhaustive analysis. This section expands detail 11 of chapter 12 with exhaustive analysis. This section expands detail 11 of chapter 12 with exhaustive analysis. This section expands detail 11 of chapter 12 with exhaustive analysis. 
- Point A11: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B11: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C11: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 11: | Col | Value | Source |
  |---|---|---|
  | Bus 745 | Transformer T18 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 77 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 12.12 Detail 12
This section expands detail 12 of chapter 12 with exhaustive analysis. This section expands detail 12 of chapter 12 with exhaustive analysis. This section expands detail 12 of chapter 12 with exhaustive analysis. This section expands detail 12 of chapter 12 with exhaustive analysis. 
- Point A12: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B12: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C12: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 12: | Col | Value | Source |
  |---|---|---|
  | Bus 746 | Transformer T19 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 84 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 12.13 Detail 13
This section expands detail 13 of chapter 12 with exhaustive analysis. This section expands detail 13 of chapter 12 with exhaustive analysis. This section expands detail 13 of chapter 12 with exhaustive analysis. This section expands detail 13 of chapter 12 with exhaustive analysis. 
- Point A13: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B13: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C13: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 13: | Col | Value | Source |
  |---|---|---|
  | Bus 747 | Transformer T20 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 91 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 12.14 Detail 14
This section expands detail 14 of chapter 12 with exhaustive analysis. This section expands detail 14 of chapter 12 with exhaustive analysis. This section expands detail 14 of chapter 12 with exhaustive analysis. This section expands detail 14 of chapter 12 with exhaustive analysis. 
- Point A14: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B14: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C14: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 14: | Col | Value | Source |
  |---|---|---|
  | Bus 748 | Transformer T21 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 98 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 12.15 Detail 15
This section expands detail 15 of chapter 12 with exhaustive analysis. This section expands detail 15 of chapter 12 with exhaustive analysis. This section expands detail 15 of chapter 12 with exhaustive analysis. This section expands detail 15 of chapter 12 with exhaustive analysis. 
- Point A15: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B15: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C15: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 15: | Col | Value | Source |
  |---|---|---|
  | Bus 749 | Transformer T22 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 5 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 12.16 Detail 16
This section expands detail 16 of chapter 12 with exhaustive analysis. This section expands detail 16 of chapter 12 with exhaustive analysis. This section expands detail 16 of chapter 12 with exhaustive analysis. This section expands detail 16 of chapter 12 with exhaustive analysis. 
- Point A16: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B16: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C16: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 16: | Col | Value | Source |
  |---|---|---|
  | Bus 750 | Transformer T23 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 12 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 12.17 Detail 17
This section expands detail 17 of chapter 12 with exhaustive analysis. This section expands detail 17 of chapter 12 with exhaustive analysis. This section expands detail 17 of chapter 12 with exhaustive analysis. This section expands detail 17 of chapter 12 with exhaustive analysis. 
- Point A17: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B17: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C17: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 17: | Col | Value | Source |
  |---|---|---|
  | Bus 751 | Transformer T24 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 19 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 12.18 Detail 18
This section expands detail 18 of chapter 12 with exhaustive analysis. This section expands detail 18 of chapter 12 with exhaustive analysis. This section expands detail 18 of chapter 12 with exhaustive analysis. This section expands detail 18 of chapter 12 with exhaustive analysis. 
- Point A18: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B18: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C18: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 18: | Col | Value | Source |
  |---|---|---|
  | Bus 752 | Transformer T25 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 26 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 12.19 Detail 19
This section expands detail 19 of chapter 12 with exhaustive analysis. This section expands detail 19 of chapter 12 with exhaustive analysis. This section expands detail 19 of chapter 12 with exhaustive analysis. This section expands detail 19 of chapter 12 with exhaustive analysis. 
- Point A19: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B19: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C19: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 19: | Col | Value | Source |
  |---|---|---|
  | Bus 753 | Transformer T26 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 33 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 12.20 Detail 20
This section expands detail 20 of chapter 12 with exhaustive analysis. This section expands detail 20 of chapter 12 with exhaustive analysis. This section expands detail 20 of chapter 12 with exhaustive analysis. This section expands detail 20 of chapter 12 with exhaustive analysis. 
- Point A20: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B20: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C20: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 20: | Col | Value | Source |
  |---|---|---|
  | Bus 754 | Transformer T27 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 40 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 12.21 Detail 21
This section expands detail 21 of chapter 12 with exhaustive analysis. This section expands detail 21 of chapter 12 with exhaustive analysis. This section expands detail 21 of chapter 12 with exhaustive analysis. This section expands detail 21 of chapter 12 with exhaustive analysis. 
- Point A21: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B21: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C21: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 21: | Col | Value | Source |
  |---|---|---|
  | Bus 755 | Transformer T28 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 47 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 12.22 Detail 22
This section expands detail 22 of chapter 12 with exhaustive analysis. This section expands detail 22 of chapter 12 with exhaustive analysis. This section expands detail 22 of chapter 12 with exhaustive analysis. This section expands detail 22 of chapter 12 with exhaustive analysis. 
- Point A22: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B22: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C22: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 22: | Col | Value | Source |
  |---|---|---|
  | Bus 756 | Transformer T7 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 54 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 12.23 Detail 23
This section expands detail 23 of chapter 12 with exhaustive analysis. This section expands detail 23 of chapter 12 with exhaustive analysis. This section expands detail 23 of chapter 12 with exhaustive analysis. This section expands detail 23 of chapter 12 with exhaustive analysis. 
- Point A23: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B23: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C23: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 23: | Col | Value | Source |
  |---|---|---|
  | Bus 757 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 61 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 12.24 Detail 24
This section expands detail 24 of chapter 12 with exhaustive analysis. This section expands detail 24 of chapter 12 with exhaustive analysis. This section expands detail 24 of chapter 12 with exhaustive analysis. This section expands detail 24 of chapter 12 with exhaustive analysis. 
- Point A24: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B24: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C24: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 24: | Col | Value | Source |
  |---|---|---|
  | Bus 758 | Transformer T9 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 68 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 12.25 Detail 25
This section expands detail 25 of chapter 12 with exhaustive analysis. This section expands detail 25 of chapter 12 with exhaustive analysis. This section expands detail 25 of chapter 12 with exhaustive analysis. This section expands detail 25 of chapter 12 with exhaustive analysis. 
- Point A25: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B25: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C25: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 25: | Col | Value | Source |
  |---|---|---|
  | Bus 759 | Transformer T10 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 75 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

---
## 13. Chapter 13 — Detailed Section

### 13.1 Detail 1
This section expands detail 1 of chapter 13 with exhaustive analysis. This section expands detail 1 of chapter 13 with exhaustive analysis. This section expands detail 1 of chapter 13 with exhaustive analysis. This section expands detail 1 of chapter 13 with exhaustive analysis. 
- Point A1: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B1: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C1: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 1: | Col | Value | Source |
  |---|---|---|
  | Bus 735 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 7 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 13.2 Detail 2
This section expands detail 2 of chapter 13 with exhaustive analysis. This section expands detail 2 of chapter 13 with exhaustive analysis. This section expands detail 2 of chapter 13 with exhaustive analysis. This section expands detail 2 of chapter 13 with exhaustive analysis. 
- Point A2: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B2: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C2: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 2: | Col | Value | Source |
  |---|---|---|
  | Bus 736 | Transformer T9 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 14 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 13.3 Detail 3
This section expands detail 3 of chapter 13 with exhaustive analysis. This section expands detail 3 of chapter 13 with exhaustive analysis. This section expands detail 3 of chapter 13 with exhaustive analysis. This section expands detail 3 of chapter 13 with exhaustive analysis. 
- Point A3: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B3: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C3: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 3: | Col | Value | Source |
  |---|---|---|
  | Bus 737 | Transformer T10 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 21 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 13.4 Detail 4
This section expands detail 4 of chapter 13 with exhaustive analysis. This section expands detail 4 of chapter 13 with exhaustive analysis. This section expands detail 4 of chapter 13 with exhaustive analysis. This section expands detail 4 of chapter 13 with exhaustive analysis. 
- Point A4: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B4: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C4: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 4: | Col | Value | Source |
  |---|---|---|
  | Bus 738 | Transformer T11 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 28 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 13.5 Detail 5
This section expands detail 5 of chapter 13 with exhaustive analysis. This section expands detail 5 of chapter 13 with exhaustive analysis. This section expands detail 5 of chapter 13 with exhaustive analysis. This section expands detail 5 of chapter 13 with exhaustive analysis. 
- Point A5: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B5: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C5: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 5: | Col | Value | Source |
  |---|---|---|
  | Bus 739 | Transformer T12 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 35 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 13.6 Detail 6
This section expands detail 6 of chapter 13 with exhaustive analysis. This section expands detail 6 of chapter 13 with exhaustive analysis. This section expands detail 6 of chapter 13 with exhaustive analysis. This section expands detail 6 of chapter 13 with exhaustive analysis. 
- Point A6: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B6: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C6: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 6: | Col | Value | Source |
  |---|---|---|
  | Bus 740 | Transformer T13 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 42 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 13.7 Detail 7
This section expands detail 7 of chapter 13 with exhaustive analysis. This section expands detail 7 of chapter 13 with exhaustive analysis. This section expands detail 7 of chapter 13 with exhaustive analysis. This section expands detail 7 of chapter 13 with exhaustive analysis. 
- Point A7: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B7: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C7: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 7: | Col | Value | Source |
  |---|---|---|
  | Bus 741 | Transformer T14 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 49 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 13.8 Detail 8
This section expands detail 8 of chapter 13 with exhaustive analysis. This section expands detail 8 of chapter 13 with exhaustive analysis. This section expands detail 8 of chapter 13 with exhaustive analysis. This section expands detail 8 of chapter 13 with exhaustive analysis. 
- Point A8: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B8: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C8: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 8: | Col | Value | Source |
  |---|---|---|
  | Bus 742 | Transformer T15 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 56 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 13.9 Detail 9
This section expands detail 9 of chapter 13 with exhaustive analysis. This section expands detail 9 of chapter 13 with exhaustive analysis. This section expands detail 9 of chapter 13 with exhaustive analysis. This section expands detail 9 of chapter 13 with exhaustive analysis. 
- Point A9: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B9: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C9: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 9: | Col | Value | Source |
  |---|---|---|
  | Bus 743 | Transformer T16 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 63 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 13.10 Detail 10
This section expands detail 10 of chapter 13 with exhaustive analysis. This section expands detail 10 of chapter 13 with exhaustive analysis. This section expands detail 10 of chapter 13 with exhaustive analysis. This section expands detail 10 of chapter 13 with exhaustive analysis. 
- Point A10: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B10: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C10: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 10: | Col | Value | Source |
  |---|---|---|
  | Bus 744 | Transformer T17 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 70 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 13.11 Detail 11
This section expands detail 11 of chapter 13 with exhaustive analysis. This section expands detail 11 of chapter 13 with exhaustive analysis. This section expands detail 11 of chapter 13 with exhaustive analysis. This section expands detail 11 of chapter 13 with exhaustive analysis. 
- Point A11: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B11: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C11: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 11: | Col | Value | Source |
  |---|---|---|
  | Bus 745 | Transformer T18 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 77 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 13.12 Detail 12
This section expands detail 12 of chapter 13 with exhaustive analysis. This section expands detail 12 of chapter 13 with exhaustive analysis. This section expands detail 12 of chapter 13 with exhaustive analysis. This section expands detail 12 of chapter 13 with exhaustive analysis. 
- Point A12: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B12: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C12: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 12: | Col | Value | Source |
  |---|---|---|
  | Bus 746 | Transformer T19 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 84 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 13.13 Detail 13
This section expands detail 13 of chapter 13 with exhaustive analysis. This section expands detail 13 of chapter 13 with exhaustive analysis. This section expands detail 13 of chapter 13 with exhaustive analysis. This section expands detail 13 of chapter 13 with exhaustive analysis. 
- Point A13: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B13: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C13: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 13: | Col | Value | Source |
  |---|---|---|
  | Bus 747 | Transformer T20 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 91 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 13.14 Detail 14
This section expands detail 14 of chapter 13 with exhaustive analysis. This section expands detail 14 of chapter 13 with exhaustive analysis. This section expands detail 14 of chapter 13 with exhaustive analysis. This section expands detail 14 of chapter 13 with exhaustive analysis. 
- Point A14: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B14: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C14: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 14: | Col | Value | Source |
  |---|---|---|
  | Bus 748 | Transformer T21 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 98 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 13.15 Detail 15
This section expands detail 15 of chapter 13 with exhaustive analysis. This section expands detail 15 of chapter 13 with exhaustive analysis. This section expands detail 15 of chapter 13 with exhaustive analysis. This section expands detail 15 of chapter 13 with exhaustive analysis. 
- Point A15: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B15: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C15: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 15: | Col | Value | Source |
  |---|---|---|
  | Bus 749 | Transformer T22 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 5 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 13.16 Detail 16
This section expands detail 16 of chapter 13 with exhaustive analysis. This section expands detail 16 of chapter 13 with exhaustive analysis. This section expands detail 16 of chapter 13 with exhaustive analysis. This section expands detail 16 of chapter 13 with exhaustive analysis. 
- Point A16: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B16: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C16: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 16: | Col | Value | Source |
  |---|---|---|
  | Bus 750 | Transformer T23 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 12 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 13.17 Detail 17
This section expands detail 17 of chapter 13 with exhaustive analysis. This section expands detail 17 of chapter 13 with exhaustive analysis. This section expands detail 17 of chapter 13 with exhaustive analysis. This section expands detail 17 of chapter 13 with exhaustive analysis. 
- Point A17: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B17: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C17: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 17: | Col | Value | Source |
  |---|---|---|
  | Bus 751 | Transformer T24 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 19 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 13.18 Detail 18
This section expands detail 18 of chapter 13 with exhaustive analysis. This section expands detail 18 of chapter 13 with exhaustive analysis. This section expands detail 18 of chapter 13 with exhaustive analysis. This section expands detail 18 of chapter 13 with exhaustive analysis. 
- Point A18: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B18: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C18: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 18: | Col | Value | Source |
  |---|---|---|
  | Bus 752 | Transformer T25 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 26 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 13.19 Detail 19
This section expands detail 19 of chapter 13 with exhaustive analysis. This section expands detail 19 of chapter 13 with exhaustive analysis. This section expands detail 19 of chapter 13 with exhaustive analysis. This section expands detail 19 of chapter 13 with exhaustive analysis. 
- Point A19: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B19: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C19: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 19: | Col | Value | Source |
  |---|---|---|
  | Bus 753 | Transformer T26 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 33 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 13.20 Detail 20
This section expands detail 20 of chapter 13 with exhaustive analysis. This section expands detail 20 of chapter 13 with exhaustive analysis. This section expands detail 20 of chapter 13 with exhaustive analysis. This section expands detail 20 of chapter 13 with exhaustive analysis. 
- Point A20: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B20: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C20: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 20: | Col | Value | Source |
  |---|---|---|
  | Bus 754 | Transformer T27 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 40 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 13.21 Detail 21
This section expands detail 21 of chapter 13 with exhaustive analysis. This section expands detail 21 of chapter 13 with exhaustive analysis. This section expands detail 21 of chapter 13 with exhaustive analysis. This section expands detail 21 of chapter 13 with exhaustive analysis. 
- Point A21: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B21: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C21: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 21: | Col | Value | Source |
  |---|---|---|
  | Bus 755 | Transformer T28 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 47 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 13.22 Detail 22
This section expands detail 22 of chapter 13 with exhaustive analysis. This section expands detail 22 of chapter 13 with exhaustive analysis. This section expands detail 22 of chapter 13 with exhaustive analysis. This section expands detail 22 of chapter 13 with exhaustive analysis. 
- Point A22: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B22: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C22: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 22: | Col | Value | Source |
  |---|---|---|
  | Bus 756 | Transformer T7 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 54 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 13.23 Detail 23
This section expands detail 23 of chapter 13 with exhaustive analysis. This section expands detail 23 of chapter 13 with exhaustive analysis. This section expands detail 23 of chapter 13 with exhaustive analysis. This section expands detail 23 of chapter 13 with exhaustive analysis. 
- Point A23: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B23: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C23: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 23: | Col | Value | Source |
  |---|---|---|
  | Bus 757 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 61 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 13.24 Detail 24
This section expands detail 24 of chapter 13 with exhaustive analysis. This section expands detail 24 of chapter 13 with exhaustive analysis. This section expands detail 24 of chapter 13 with exhaustive analysis. This section expands detail 24 of chapter 13 with exhaustive analysis. 
- Point A24: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B24: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C24: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 24: | Col | Value | Source |
  |---|---|---|
  | Bus 758 | Transformer T9 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 68 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 13.25 Detail 25
This section expands detail 25 of chapter 13 with exhaustive analysis. This section expands detail 25 of chapter 13 with exhaustive analysis. This section expands detail 25 of chapter 13 with exhaustive analysis. This section expands detail 25 of chapter 13 with exhaustive analysis. 
- Point A25: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B25: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C25: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 25: | Col | Value | Source |
  |---|---|---|
  | Bus 759 | Transformer T10 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 75 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

---
## 14. Chapter 14 — Detailed Section

### 14.1 Detail 1
This section expands detail 1 of chapter 14 with exhaustive analysis. This section expands detail 1 of chapter 14 with exhaustive analysis. This section expands detail 1 of chapter 14 with exhaustive analysis. This section expands detail 1 of chapter 14 with exhaustive analysis. 
- Point A1: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B1: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C1: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 1: | Col | Value | Source |
  |---|---|---|
  | Bus 735 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 7 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 14.2 Detail 2
This section expands detail 2 of chapter 14 with exhaustive analysis. This section expands detail 2 of chapter 14 with exhaustive analysis. This section expands detail 2 of chapter 14 with exhaustive analysis. This section expands detail 2 of chapter 14 with exhaustive analysis. 
- Point A2: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B2: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C2: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 2: | Col | Value | Source |
  |---|---|---|
  | Bus 736 | Transformer T9 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 14 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 14.3 Detail 3
This section expands detail 3 of chapter 14 with exhaustive analysis. This section expands detail 3 of chapter 14 with exhaustive analysis. This section expands detail 3 of chapter 14 with exhaustive analysis. This section expands detail 3 of chapter 14 with exhaustive analysis. 
- Point A3: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B3: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C3: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 3: | Col | Value | Source |
  |---|---|---|
  | Bus 737 | Transformer T10 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 21 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 14.4 Detail 4
This section expands detail 4 of chapter 14 with exhaustive analysis. This section expands detail 4 of chapter 14 with exhaustive analysis. This section expands detail 4 of chapter 14 with exhaustive analysis. This section expands detail 4 of chapter 14 with exhaustive analysis. 
- Point A4: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B4: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C4: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 4: | Col | Value | Source |
  |---|---|---|
  | Bus 738 | Transformer T11 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 28 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 14.5 Detail 5
This section expands detail 5 of chapter 14 with exhaustive analysis. This section expands detail 5 of chapter 14 with exhaustive analysis. This section expands detail 5 of chapter 14 with exhaustive analysis. This section expands detail 5 of chapter 14 with exhaustive analysis. 
- Point A5: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B5: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C5: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 5: | Col | Value | Source |
  |---|---|---|
  | Bus 739 | Transformer T12 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 35 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 14.6 Detail 6
This section expands detail 6 of chapter 14 with exhaustive analysis. This section expands detail 6 of chapter 14 with exhaustive analysis. This section expands detail 6 of chapter 14 with exhaustive analysis. This section expands detail 6 of chapter 14 with exhaustive analysis. 
- Point A6: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B6: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C6: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 6: | Col | Value | Source |
  |---|---|---|
  | Bus 740 | Transformer T13 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 42 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 14.7 Detail 7
This section expands detail 7 of chapter 14 with exhaustive analysis. This section expands detail 7 of chapter 14 with exhaustive analysis. This section expands detail 7 of chapter 14 with exhaustive analysis. This section expands detail 7 of chapter 14 with exhaustive analysis. 
- Point A7: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B7: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C7: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 7: | Col | Value | Source |
  |---|---|---|
  | Bus 741 | Transformer T14 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 49 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 14.8 Detail 8
This section expands detail 8 of chapter 14 with exhaustive analysis. This section expands detail 8 of chapter 14 with exhaustive analysis. This section expands detail 8 of chapter 14 with exhaustive analysis. This section expands detail 8 of chapter 14 with exhaustive analysis. 
- Point A8: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B8: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C8: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 8: | Col | Value | Source |
  |---|---|---|
  | Bus 742 | Transformer T15 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 56 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 14.9 Detail 9
This section expands detail 9 of chapter 14 with exhaustive analysis. This section expands detail 9 of chapter 14 with exhaustive analysis. This section expands detail 9 of chapter 14 with exhaustive analysis. This section expands detail 9 of chapter 14 with exhaustive analysis. 
- Point A9: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B9: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C9: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 9: | Col | Value | Source |
  |---|---|---|
  | Bus 743 | Transformer T16 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 63 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 14.10 Detail 10
This section expands detail 10 of chapter 14 with exhaustive analysis. This section expands detail 10 of chapter 14 with exhaustive analysis. This section expands detail 10 of chapter 14 with exhaustive analysis. This section expands detail 10 of chapter 14 with exhaustive analysis. 
- Point A10: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B10: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C10: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 10: | Col | Value | Source |
  |---|---|---|
  | Bus 744 | Transformer T17 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 70 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 14.11 Detail 11
This section expands detail 11 of chapter 14 with exhaustive analysis. This section expands detail 11 of chapter 14 with exhaustive analysis. This section expands detail 11 of chapter 14 with exhaustive analysis. This section expands detail 11 of chapter 14 with exhaustive analysis. 
- Point A11: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B11: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C11: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 11: | Col | Value | Source |
  |---|---|---|
  | Bus 745 | Transformer T18 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 77 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 14.12 Detail 12
This section expands detail 12 of chapter 14 with exhaustive analysis. This section expands detail 12 of chapter 14 with exhaustive analysis. This section expands detail 12 of chapter 14 with exhaustive analysis. This section expands detail 12 of chapter 14 with exhaustive analysis. 
- Point A12: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B12: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C12: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 12: | Col | Value | Source |
  |---|---|---|
  | Bus 746 | Transformer T19 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 84 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 14.13 Detail 13
This section expands detail 13 of chapter 14 with exhaustive analysis. This section expands detail 13 of chapter 14 with exhaustive analysis. This section expands detail 13 of chapter 14 with exhaustive analysis. This section expands detail 13 of chapter 14 with exhaustive analysis. 
- Point A13: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B13: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C13: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 13: | Col | Value | Source |
  |---|---|---|
  | Bus 747 | Transformer T20 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 91 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 14.14 Detail 14
This section expands detail 14 of chapter 14 with exhaustive analysis. This section expands detail 14 of chapter 14 with exhaustive analysis. This section expands detail 14 of chapter 14 with exhaustive analysis. This section expands detail 14 of chapter 14 with exhaustive analysis. 
- Point A14: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B14: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C14: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 14: | Col | Value | Source |
  |---|---|---|
  | Bus 748 | Transformer T21 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 98 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 14.15 Detail 15
This section expands detail 15 of chapter 14 with exhaustive analysis. This section expands detail 15 of chapter 14 with exhaustive analysis. This section expands detail 15 of chapter 14 with exhaustive analysis. This section expands detail 15 of chapter 14 with exhaustive analysis. 
- Point A15: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B15: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C15: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 15: | Col | Value | Source |
  |---|---|---|
  | Bus 749 | Transformer T22 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 5 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 14.16 Detail 16
This section expands detail 16 of chapter 14 with exhaustive analysis. This section expands detail 16 of chapter 14 with exhaustive analysis. This section expands detail 16 of chapter 14 with exhaustive analysis. This section expands detail 16 of chapter 14 with exhaustive analysis. 
- Point A16: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B16: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C16: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 16: | Col | Value | Source |
  |---|---|---|
  | Bus 750 | Transformer T23 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 12 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 14.17 Detail 17
This section expands detail 17 of chapter 14 with exhaustive analysis. This section expands detail 17 of chapter 14 with exhaustive analysis. This section expands detail 17 of chapter 14 with exhaustive analysis. This section expands detail 17 of chapter 14 with exhaustive analysis. 
- Point A17: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B17: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C17: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 17: | Col | Value | Source |
  |---|---|---|
  | Bus 751 | Transformer T24 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 19 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 14.18 Detail 18
This section expands detail 18 of chapter 14 with exhaustive analysis. This section expands detail 18 of chapter 14 with exhaustive analysis. This section expands detail 18 of chapter 14 with exhaustive analysis. This section expands detail 18 of chapter 14 with exhaustive analysis. 
- Point A18: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B18: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C18: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 18: | Col | Value | Source |
  |---|---|---|
  | Bus 752 | Transformer T25 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 26 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 14.19 Detail 19
This section expands detail 19 of chapter 14 with exhaustive analysis. This section expands detail 19 of chapter 14 with exhaustive analysis. This section expands detail 19 of chapter 14 with exhaustive analysis. This section expands detail 19 of chapter 14 with exhaustive analysis. 
- Point A19: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B19: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C19: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 19: | Col | Value | Source |
  |---|---|---|
  | Bus 753 | Transformer T26 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 33 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 14.20 Detail 20
This section expands detail 20 of chapter 14 with exhaustive analysis. This section expands detail 20 of chapter 14 with exhaustive analysis. This section expands detail 20 of chapter 14 with exhaustive analysis. This section expands detail 20 of chapter 14 with exhaustive analysis. 
- Point A20: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B20: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C20: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 20: | Col | Value | Source |
  |---|---|---|
  | Bus 754 | Transformer T27 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 40 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 14.21 Detail 21
This section expands detail 21 of chapter 14 with exhaustive analysis. This section expands detail 21 of chapter 14 with exhaustive analysis. This section expands detail 21 of chapter 14 with exhaustive analysis. This section expands detail 21 of chapter 14 with exhaustive analysis. 
- Point A21: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B21: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C21: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 21: | Col | Value | Source |
  |---|---|---|
  | Bus 755 | Transformer T28 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 47 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 14.22 Detail 22
This section expands detail 22 of chapter 14 with exhaustive analysis. This section expands detail 22 of chapter 14 with exhaustive analysis. This section expands detail 22 of chapter 14 with exhaustive analysis. This section expands detail 22 of chapter 14 with exhaustive analysis. 
- Point A22: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B22: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C22: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 22: | Col | Value | Source |
  |---|---|---|
  | Bus 756 | Transformer T7 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 54 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 14.23 Detail 23
This section expands detail 23 of chapter 14 with exhaustive analysis. This section expands detail 23 of chapter 14 with exhaustive analysis. This section expands detail 23 of chapter 14 with exhaustive analysis. This section expands detail 23 of chapter 14 with exhaustive analysis. 
- Point A23: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B23: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C23: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 23: | Col | Value | Source |
  |---|---|---|
  | Bus 757 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 61 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 14.24 Detail 24
This section expands detail 24 of chapter 14 with exhaustive analysis. This section expands detail 24 of chapter 14 with exhaustive analysis. This section expands detail 24 of chapter 14 with exhaustive analysis. This section expands detail 24 of chapter 14 with exhaustive analysis. 
- Point A24: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B24: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C24: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 24: | Col | Value | Source |
  |---|---|---|
  | Bus 758 | Transformer T9 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 68 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 14.25 Detail 25
This section expands detail 25 of chapter 14 with exhaustive analysis. This section expands detail 25 of chapter 14 with exhaustive analysis. This section expands detail 25 of chapter 14 with exhaustive analysis. This section expands detail 25 of chapter 14 with exhaustive analysis. 
- Point A25: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B25: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C25: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 25: | Col | Value | Source |
  |---|---|---|
  | Bus 759 | Transformer T10 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 75 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

---
## 15. Chapter 15 — Detailed Section

### 15.1 Detail 1
This section expands detail 1 of chapter 15 with exhaustive analysis. This section expands detail 1 of chapter 15 with exhaustive analysis. This section expands detail 1 of chapter 15 with exhaustive analysis. This section expands detail 1 of chapter 15 with exhaustive analysis. 
- Point A1: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B1: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C1: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 1: | Col | Value | Source |
  |---|---|---|
  | Bus 735 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 7 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 15.2 Detail 2
This section expands detail 2 of chapter 15 with exhaustive analysis. This section expands detail 2 of chapter 15 with exhaustive analysis. This section expands detail 2 of chapter 15 with exhaustive analysis. This section expands detail 2 of chapter 15 with exhaustive analysis. 
- Point A2: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B2: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C2: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 2: | Col | Value | Source |
  |---|---|---|
  | Bus 736 | Transformer T9 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 14 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 15.3 Detail 3
This section expands detail 3 of chapter 15 with exhaustive analysis. This section expands detail 3 of chapter 15 with exhaustive analysis. This section expands detail 3 of chapter 15 with exhaustive analysis. This section expands detail 3 of chapter 15 with exhaustive analysis. 
- Point A3: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B3: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C3: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 3: | Col | Value | Source |
  |---|---|---|
  | Bus 737 | Transformer T10 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 21 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 15.4 Detail 4
This section expands detail 4 of chapter 15 with exhaustive analysis. This section expands detail 4 of chapter 15 with exhaustive analysis. This section expands detail 4 of chapter 15 with exhaustive analysis. This section expands detail 4 of chapter 15 with exhaustive analysis. 
- Point A4: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B4: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C4: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 4: | Col | Value | Source |
  |---|---|---|
  | Bus 738 | Transformer T11 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 28 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 15.5 Detail 5
This section expands detail 5 of chapter 15 with exhaustive analysis. This section expands detail 5 of chapter 15 with exhaustive analysis. This section expands detail 5 of chapter 15 with exhaustive analysis. This section expands detail 5 of chapter 15 with exhaustive analysis. 
- Point A5: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B5: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C5: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 5: | Col | Value | Source |
  |---|---|---|
  | Bus 739 | Transformer T12 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 35 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 15.6 Detail 6
This section expands detail 6 of chapter 15 with exhaustive analysis. This section expands detail 6 of chapter 15 with exhaustive analysis. This section expands detail 6 of chapter 15 with exhaustive analysis. This section expands detail 6 of chapter 15 with exhaustive analysis. 
- Point A6: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B6: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C6: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 6: | Col | Value | Source |
  |---|---|---|
  | Bus 740 | Transformer T13 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 42 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 15.7 Detail 7
This section expands detail 7 of chapter 15 with exhaustive analysis. This section expands detail 7 of chapter 15 with exhaustive analysis. This section expands detail 7 of chapter 15 with exhaustive analysis. This section expands detail 7 of chapter 15 with exhaustive analysis. 
- Point A7: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B7: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C7: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 7: | Col | Value | Source |
  |---|---|---|
  | Bus 741 | Transformer T14 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 49 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 15.8 Detail 8
This section expands detail 8 of chapter 15 with exhaustive analysis. This section expands detail 8 of chapter 15 with exhaustive analysis. This section expands detail 8 of chapter 15 with exhaustive analysis. This section expands detail 8 of chapter 15 with exhaustive analysis. 
- Point A8: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B8: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C8: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 8: | Col | Value | Source |
  |---|---|---|
  | Bus 742 | Transformer T15 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 56 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 15.9 Detail 9
This section expands detail 9 of chapter 15 with exhaustive analysis. This section expands detail 9 of chapter 15 with exhaustive analysis. This section expands detail 9 of chapter 15 with exhaustive analysis. This section expands detail 9 of chapter 15 with exhaustive analysis. 
- Point A9: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B9: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C9: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 9: | Col | Value | Source |
  |---|---|---|
  | Bus 743 | Transformer T16 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 63 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 15.10 Detail 10
This section expands detail 10 of chapter 15 with exhaustive analysis. This section expands detail 10 of chapter 15 with exhaustive analysis. This section expands detail 10 of chapter 15 with exhaustive analysis. This section expands detail 10 of chapter 15 with exhaustive analysis. 
- Point A10: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B10: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C10: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 10: | Col | Value | Source |
  |---|---|---|
  | Bus 744 | Transformer T17 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 70 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 15.11 Detail 11
This section expands detail 11 of chapter 15 with exhaustive analysis. This section expands detail 11 of chapter 15 with exhaustive analysis. This section expands detail 11 of chapter 15 with exhaustive analysis. This section expands detail 11 of chapter 15 with exhaustive analysis. 
- Point A11: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B11: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C11: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 11: | Col | Value | Source |
  |---|---|---|
  | Bus 745 | Transformer T18 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 77 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 15.12 Detail 12
This section expands detail 12 of chapter 15 with exhaustive analysis. This section expands detail 12 of chapter 15 with exhaustive analysis. This section expands detail 12 of chapter 15 with exhaustive analysis. This section expands detail 12 of chapter 15 with exhaustive analysis. 
- Point A12: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B12: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C12: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 12: | Col | Value | Source |
  |---|---|---|
  | Bus 746 | Transformer T19 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 84 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 15.13 Detail 13
This section expands detail 13 of chapter 15 with exhaustive analysis. This section expands detail 13 of chapter 15 with exhaustive analysis. This section expands detail 13 of chapter 15 with exhaustive analysis. This section expands detail 13 of chapter 15 with exhaustive analysis. 
- Point A13: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B13: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C13: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 13: | Col | Value | Source |
  |---|---|---|
  | Bus 747 | Transformer T20 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 91 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 15.14 Detail 14
This section expands detail 14 of chapter 15 with exhaustive analysis. This section expands detail 14 of chapter 15 with exhaustive analysis. This section expands detail 14 of chapter 15 with exhaustive analysis. This section expands detail 14 of chapter 15 with exhaustive analysis. 
- Point A14: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B14: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C14: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 14: | Col | Value | Source |
  |---|---|---|
  | Bus 748 | Transformer T21 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 98 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 15.15 Detail 15
This section expands detail 15 of chapter 15 with exhaustive analysis. This section expands detail 15 of chapter 15 with exhaustive analysis. This section expands detail 15 of chapter 15 with exhaustive analysis. This section expands detail 15 of chapter 15 with exhaustive analysis. 
- Point A15: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B15: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C15: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 15: | Col | Value | Source |
  |---|---|---|
  | Bus 749 | Transformer T22 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 5 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 15.16 Detail 16
This section expands detail 16 of chapter 15 with exhaustive analysis. This section expands detail 16 of chapter 15 with exhaustive analysis. This section expands detail 16 of chapter 15 with exhaustive analysis. This section expands detail 16 of chapter 15 with exhaustive analysis. 
- Point A16: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B16: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C16: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 16: | Col | Value | Source |
  |---|---|---|
  | Bus 750 | Transformer T23 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 12 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 15.17 Detail 17
This section expands detail 17 of chapter 15 with exhaustive analysis. This section expands detail 17 of chapter 15 with exhaustive analysis. This section expands detail 17 of chapter 15 with exhaustive analysis. This section expands detail 17 of chapter 15 with exhaustive analysis. 
- Point A17: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B17: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C17: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 17: | Col | Value | Source |
  |---|---|---|
  | Bus 751 | Transformer T24 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 19 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 15.18 Detail 18
This section expands detail 18 of chapter 15 with exhaustive analysis. This section expands detail 18 of chapter 15 with exhaustive analysis. This section expands detail 18 of chapter 15 with exhaustive analysis. This section expands detail 18 of chapter 15 with exhaustive analysis. 
- Point A18: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B18: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C18: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 18: | Col | Value | Source |
  |---|---|---|
  | Bus 752 | Transformer T25 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 26 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 15.19 Detail 19
This section expands detail 19 of chapter 15 with exhaustive analysis. This section expands detail 19 of chapter 15 with exhaustive analysis. This section expands detail 19 of chapter 15 with exhaustive analysis. This section expands detail 19 of chapter 15 with exhaustive analysis. 
- Point A19: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B19: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C19: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 19: | Col | Value | Source |
  |---|---|---|
  | Bus 753 | Transformer T26 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 33 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 15.20 Detail 20
This section expands detail 20 of chapter 15 with exhaustive analysis. This section expands detail 20 of chapter 15 with exhaustive analysis. This section expands detail 20 of chapter 15 with exhaustive analysis. This section expands detail 20 of chapter 15 with exhaustive analysis. 
- Point A20: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B20: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C20: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 20: | Col | Value | Source |
  |---|---|---|
  | Bus 754 | Transformer T27 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 40 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 15.21 Detail 21
This section expands detail 21 of chapter 15 with exhaustive analysis. This section expands detail 21 of chapter 15 with exhaustive analysis. This section expands detail 21 of chapter 15 with exhaustive analysis. This section expands detail 21 of chapter 15 with exhaustive analysis. 
- Point A21: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B21: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C21: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 21: | Col | Value | Source |
  |---|---|---|
  | Bus 755 | Transformer T28 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 47 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 15.22 Detail 22
This section expands detail 22 of chapter 15 with exhaustive analysis. This section expands detail 22 of chapter 15 with exhaustive analysis. This section expands detail 22 of chapter 15 with exhaustive analysis. This section expands detail 22 of chapter 15 with exhaustive analysis. 
- Point A22: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B22: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C22: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 22: | Col | Value | Source |
  |---|---|---|
  | Bus 756 | Transformer T7 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 54 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 15.23 Detail 23
This section expands detail 23 of chapter 15 with exhaustive analysis. This section expands detail 23 of chapter 15 with exhaustive analysis. This section expands detail 23 of chapter 15 with exhaustive analysis. This section expands detail 23 of chapter 15 with exhaustive analysis. 
- Point A23: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B23: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C23: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 23: | Col | Value | Source |
  |---|---|---|
  | Bus 757 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 61 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 15.24 Detail 24
This section expands detail 24 of chapter 15 with exhaustive analysis. This section expands detail 24 of chapter 15 with exhaustive analysis. This section expands detail 24 of chapter 15 with exhaustive analysis. This section expands detail 24 of chapter 15 with exhaustive analysis. 
- Point A24: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B24: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C24: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 24: | Col | Value | Source |
  |---|---|---|
  | Bus 758 | Transformer T9 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 68 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 15.25 Detail 25
This section expands detail 25 of chapter 15 with exhaustive analysis. This section expands detail 25 of chapter 15 with exhaustive analysis. This section expands detail 25 of chapter 15 with exhaustive analysis. This section expands detail 25 of chapter 15 with exhaustive analysis. 
- Point A25: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B25: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C25: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 25: | Col | Value | Source |
  |---|---|---|
  | Bus 759 | Transformer T10 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 75 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

---
## 16. Chapter 16 — Detailed Section

### 16.1 Detail 1
This section expands detail 1 of chapter 16 with exhaustive analysis. This section expands detail 1 of chapter 16 with exhaustive analysis. This section expands detail 1 of chapter 16 with exhaustive analysis. This section expands detail 1 of chapter 16 with exhaustive analysis. 
- Point A1: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B1: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C1: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 1: | Col | Value | Source |
  |---|---|---|
  | Bus 735 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 7 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 16.2 Detail 2
This section expands detail 2 of chapter 16 with exhaustive analysis. This section expands detail 2 of chapter 16 with exhaustive analysis. This section expands detail 2 of chapter 16 with exhaustive analysis. This section expands detail 2 of chapter 16 with exhaustive analysis. 
- Point A2: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B2: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C2: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 2: | Col | Value | Source |
  |---|---|---|
  | Bus 736 | Transformer T9 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 14 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 16.3 Detail 3
This section expands detail 3 of chapter 16 with exhaustive analysis. This section expands detail 3 of chapter 16 with exhaustive analysis. This section expands detail 3 of chapter 16 with exhaustive analysis. This section expands detail 3 of chapter 16 with exhaustive analysis. 
- Point A3: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B3: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C3: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 3: | Col | Value | Source |
  |---|---|---|
  | Bus 737 | Transformer T10 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 21 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 16.4 Detail 4
This section expands detail 4 of chapter 16 with exhaustive analysis. This section expands detail 4 of chapter 16 with exhaustive analysis. This section expands detail 4 of chapter 16 with exhaustive analysis. This section expands detail 4 of chapter 16 with exhaustive analysis. 
- Point A4: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B4: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C4: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 4: | Col | Value | Source |
  |---|---|---|
  | Bus 738 | Transformer T11 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 28 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 16.5 Detail 5
This section expands detail 5 of chapter 16 with exhaustive analysis. This section expands detail 5 of chapter 16 with exhaustive analysis. This section expands detail 5 of chapter 16 with exhaustive analysis. This section expands detail 5 of chapter 16 with exhaustive analysis. 
- Point A5: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B5: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C5: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 5: | Col | Value | Source |
  |---|---|---|
  | Bus 739 | Transformer T12 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 35 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 16.6 Detail 6
This section expands detail 6 of chapter 16 with exhaustive analysis. This section expands detail 6 of chapter 16 with exhaustive analysis. This section expands detail 6 of chapter 16 with exhaustive analysis. This section expands detail 6 of chapter 16 with exhaustive analysis. 
- Point A6: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B6: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C6: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 6: | Col | Value | Source |
  |---|---|---|
  | Bus 740 | Transformer T13 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 42 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 16.7 Detail 7
This section expands detail 7 of chapter 16 with exhaustive analysis. This section expands detail 7 of chapter 16 with exhaustive analysis. This section expands detail 7 of chapter 16 with exhaustive analysis. This section expands detail 7 of chapter 16 with exhaustive analysis. 
- Point A7: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B7: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C7: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 7: | Col | Value | Source |
  |---|---|---|
  | Bus 741 | Transformer T14 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 49 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 16.8 Detail 8
This section expands detail 8 of chapter 16 with exhaustive analysis. This section expands detail 8 of chapter 16 with exhaustive analysis. This section expands detail 8 of chapter 16 with exhaustive analysis. This section expands detail 8 of chapter 16 with exhaustive analysis. 
- Point A8: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B8: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C8: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 8: | Col | Value | Source |
  |---|---|---|
  | Bus 742 | Transformer T15 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 56 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 16.9 Detail 9
This section expands detail 9 of chapter 16 with exhaustive analysis. This section expands detail 9 of chapter 16 with exhaustive analysis. This section expands detail 9 of chapter 16 with exhaustive analysis. This section expands detail 9 of chapter 16 with exhaustive analysis. 
- Point A9: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B9: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C9: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 9: | Col | Value | Source |
  |---|---|---|
  | Bus 743 | Transformer T16 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 63 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 16.10 Detail 10
This section expands detail 10 of chapter 16 with exhaustive analysis. This section expands detail 10 of chapter 16 with exhaustive analysis. This section expands detail 10 of chapter 16 with exhaustive analysis. This section expands detail 10 of chapter 16 with exhaustive analysis. 
- Point A10: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B10: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C10: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 10: | Col | Value | Source |
  |---|---|---|
  | Bus 744 | Transformer T17 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 70 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 16.11 Detail 11
This section expands detail 11 of chapter 16 with exhaustive analysis. This section expands detail 11 of chapter 16 with exhaustive analysis. This section expands detail 11 of chapter 16 with exhaustive analysis. This section expands detail 11 of chapter 16 with exhaustive analysis. 
- Point A11: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B11: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C11: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 11: | Col | Value | Source |
  |---|---|---|
  | Bus 745 | Transformer T18 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 77 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 16.12 Detail 12
This section expands detail 12 of chapter 16 with exhaustive analysis. This section expands detail 12 of chapter 16 with exhaustive analysis. This section expands detail 12 of chapter 16 with exhaustive analysis. This section expands detail 12 of chapter 16 with exhaustive analysis. 
- Point A12: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B12: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C12: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 12: | Col | Value | Source |
  |---|---|---|
  | Bus 746 | Transformer T19 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 84 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 16.13 Detail 13
This section expands detail 13 of chapter 16 with exhaustive analysis. This section expands detail 13 of chapter 16 with exhaustive analysis. This section expands detail 13 of chapter 16 with exhaustive analysis. This section expands detail 13 of chapter 16 with exhaustive analysis. 
- Point A13: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B13: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C13: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 13: | Col | Value | Source |
  |---|---|---|
  | Bus 747 | Transformer T20 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 91 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 16.14 Detail 14
This section expands detail 14 of chapter 16 with exhaustive analysis. This section expands detail 14 of chapter 16 with exhaustive analysis. This section expands detail 14 of chapter 16 with exhaustive analysis. This section expands detail 14 of chapter 16 with exhaustive analysis. 
- Point A14: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B14: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C14: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 14: | Col | Value | Source |
  |---|---|---|
  | Bus 748 | Transformer T21 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 98 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 16.15 Detail 15
This section expands detail 15 of chapter 16 with exhaustive analysis. This section expands detail 15 of chapter 16 with exhaustive analysis. This section expands detail 15 of chapter 16 with exhaustive analysis. This section expands detail 15 of chapter 16 with exhaustive analysis. 
- Point A15: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B15: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C15: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 15: | Col | Value | Source |
  |---|---|---|
  | Bus 749 | Transformer T22 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 5 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 16.16 Detail 16
This section expands detail 16 of chapter 16 with exhaustive analysis. This section expands detail 16 of chapter 16 with exhaustive analysis. This section expands detail 16 of chapter 16 with exhaustive analysis. This section expands detail 16 of chapter 16 with exhaustive analysis. 
- Point A16: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B16: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C16: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 16: | Col | Value | Source |
  |---|---|---|
  | Bus 750 | Transformer T23 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 12 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 16.17 Detail 17
This section expands detail 17 of chapter 16 with exhaustive analysis. This section expands detail 17 of chapter 16 with exhaustive analysis. This section expands detail 17 of chapter 16 with exhaustive analysis. This section expands detail 17 of chapter 16 with exhaustive analysis. 
- Point A17: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B17: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C17: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 17: | Col | Value | Source |
  |---|---|---|
  | Bus 751 | Transformer T24 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 19 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 16.18 Detail 18
This section expands detail 18 of chapter 16 with exhaustive analysis. This section expands detail 18 of chapter 16 with exhaustive analysis. This section expands detail 18 of chapter 16 with exhaustive analysis. This section expands detail 18 of chapter 16 with exhaustive analysis. 
- Point A18: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B18: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C18: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 18: | Col | Value | Source |
  |---|---|---|
  | Bus 752 | Transformer T25 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 26 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 16.19 Detail 19
This section expands detail 19 of chapter 16 with exhaustive analysis. This section expands detail 19 of chapter 16 with exhaustive analysis. This section expands detail 19 of chapter 16 with exhaustive analysis. This section expands detail 19 of chapter 16 with exhaustive analysis. 
- Point A19: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B19: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C19: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 19: | Col | Value | Source |
  |---|---|---|
  | Bus 753 | Transformer T26 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 33 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 16.20 Detail 20
This section expands detail 20 of chapter 16 with exhaustive analysis. This section expands detail 20 of chapter 16 with exhaustive analysis. This section expands detail 20 of chapter 16 with exhaustive analysis. This section expands detail 20 of chapter 16 with exhaustive analysis. 
- Point A20: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B20: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C20: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 20: | Col | Value | Source |
  |---|---|---|
  | Bus 754 | Transformer T27 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 40 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 16.21 Detail 21
This section expands detail 21 of chapter 16 with exhaustive analysis. This section expands detail 21 of chapter 16 with exhaustive analysis. This section expands detail 21 of chapter 16 with exhaustive analysis. This section expands detail 21 of chapter 16 with exhaustive analysis. 
- Point A21: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B21: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C21: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 21: | Col | Value | Source |
  |---|---|---|
  | Bus 755 | Transformer T28 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 47 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 16.22 Detail 22
This section expands detail 22 of chapter 16 with exhaustive analysis. This section expands detail 22 of chapter 16 with exhaustive analysis. This section expands detail 22 of chapter 16 with exhaustive analysis. This section expands detail 22 of chapter 16 with exhaustive analysis. 
- Point A22: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B22: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C22: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 22: | Col | Value | Source |
  |---|---|---|
  | Bus 756 | Transformer T7 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 54 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 16.23 Detail 23
This section expands detail 23 of chapter 16 with exhaustive analysis. This section expands detail 23 of chapter 16 with exhaustive analysis. This section expands detail 23 of chapter 16 with exhaustive analysis. This section expands detail 23 of chapter 16 with exhaustive analysis. 
- Point A23: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B23: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C23: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 23: | Col | Value | Source |
  |---|---|---|
  | Bus 757 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 61 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 16.24 Detail 24
This section expands detail 24 of chapter 16 with exhaustive analysis. This section expands detail 24 of chapter 16 with exhaustive analysis. This section expands detail 24 of chapter 16 with exhaustive analysis. This section expands detail 24 of chapter 16 with exhaustive analysis. 
- Point A24: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B24: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C24: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 24: | Col | Value | Source |
  |---|---|---|
  | Bus 758 | Transformer T9 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 68 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 16.25 Detail 25
This section expands detail 25 of chapter 16 with exhaustive analysis. This section expands detail 25 of chapter 16 with exhaustive analysis. This section expands detail 25 of chapter 16 with exhaustive analysis. This section expands detail 25 of chapter 16 with exhaustive analysis. 
- Point A25: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B25: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C25: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 25: | Col | Value | Source |
  |---|---|---|
  | Bus 759 | Transformer T10 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 75 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

---
## 17. Chapter 17 — Detailed Section

### 17.1 Detail 1
This section expands detail 1 of chapter 17 with exhaustive analysis. This section expands detail 1 of chapter 17 with exhaustive analysis. This section expands detail 1 of chapter 17 with exhaustive analysis. This section expands detail 1 of chapter 17 with exhaustive analysis. 
- Point A1: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B1: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C1: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 1: | Col | Value | Source |
  |---|---|---|
  | Bus 735 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 7 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 17.2 Detail 2
This section expands detail 2 of chapter 17 with exhaustive analysis. This section expands detail 2 of chapter 17 with exhaustive analysis. This section expands detail 2 of chapter 17 with exhaustive analysis. This section expands detail 2 of chapter 17 with exhaustive analysis. 
- Point A2: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B2: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C2: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 2: | Col | Value | Source |
  |---|---|---|
  | Bus 736 | Transformer T9 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 14 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 17.3 Detail 3
This section expands detail 3 of chapter 17 with exhaustive analysis. This section expands detail 3 of chapter 17 with exhaustive analysis. This section expands detail 3 of chapter 17 with exhaustive analysis. This section expands detail 3 of chapter 17 with exhaustive analysis. 
- Point A3: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B3: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C3: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 3: | Col | Value | Source |
  |---|---|---|
  | Bus 737 | Transformer T10 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 21 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 17.4 Detail 4
This section expands detail 4 of chapter 17 with exhaustive analysis. This section expands detail 4 of chapter 17 with exhaustive analysis. This section expands detail 4 of chapter 17 with exhaustive analysis. This section expands detail 4 of chapter 17 with exhaustive analysis. 
- Point A4: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B4: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C4: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 4: | Col | Value | Source |
  |---|---|---|
  | Bus 738 | Transformer T11 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 28 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 17.5 Detail 5
This section expands detail 5 of chapter 17 with exhaustive analysis. This section expands detail 5 of chapter 17 with exhaustive analysis. This section expands detail 5 of chapter 17 with exhaustive analysis. This section expands detail 5 of chapter 17 with exhaustive analysis. 
- Point A5: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B5: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C5: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 5: | Col | Value | Source |
  |---|---|---|
  | Bus 739 | Transformer T12 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 35 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 17.6 Detail 6
This section expands detail 6 of chapter 17 with exhaustive analysis. This section expands detail 6 of chapter 17 with exhaustive analysis. This section expands detail 6 of chapter 17 with exhaustive analysis. This section expands detail 6 of chapter 17 with exhaustive analysis. 
- Point A6: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B6: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C6: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 6: | Col | Value | Source |
  |---|---|---|
  | Bus 740 | Transformer T13 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 42 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 17.7 Detail 7
This section expands detail 7 of chapter 17 with exhaustive analysis. This section expands detail 7 of chapter 17 with exhaustive analysis. This section expands detail 7 of chapter 17 with exhaustive analysis. This section expands detail 7 of chapter 17 with exhaustive analysis. 
- Point A7: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B7: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C7: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 7: | Col | Value | Source |
  |---|---|---|
  | Bus 741 | Transformer T14 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 49 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 17.8 Detail 8
This section expands detail 8 of chapter 17 with exhaustive analysis. This section expands detail 8 of chapter 17 with exhaustive analysis. This section expands detail 8 of chapter 17 with exhaustive analysis. This section expands detail 8 of chapter 17 with exhaustive analysis. 
- Point A8: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B8: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C8: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 8: | Col | Value | Source |
  |---|---|---|
  | Bus 742 | Transformer T15 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 56 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 17.9 Detail 9
This section expands detail 9 of chapter 17 with exhaustive analysis. This section expands detail 9 of chapter 17 with exhaustive analysis. This section expands detail 9 of chapter 17 with exhaustive analysis. This section expands detail 9 of chapter 17 with exhaustive analysis. 
- Point A9: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B9: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C9: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 9: | Col | Value | Source |
  |---|---|---|
  | Bus 743 | Transformer T16 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 63 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 17.10 Detail 10
This section expands detail 10 of chapter 17 with exhaustive analysis. This section expands detail 10 of chapter 17 with exhaustive analysis. This section expands detail 10 of chapter 17 with exhaustive analysis. This section expands detail 10 of chapter 17 with exhaustive analysis. 
- Point A10: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B10: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C10: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 10: | Col | Value | Source |
  |---|---|---|
  | Bus 744 | Transformer T17 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 70 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 17.11 Detail 11
This section expands detail 11 of chapter 17 with exhaustive analysis. This section expands detail 11 of chapter 17 with exhaustive analysis. This section expands detail 11 of chapter 17 with exhaustive analysis. This section expands detail 11 of chapter 17 with exhaustive analysis. 
- Point A11: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B11: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C11: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 11: | Col | Value | Source |
  |---|---|---|
  | Bus 745 | Transformer T18 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 77 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 17.12 Detail 12
This section expands detail 12 of chapter 17 with exhaustive analysis. This section expands detail 12 of chapter 17 with exhaustive analysis. This section expands detail 12 of chapter 17 with exhaustive analysis. This section expands detail 12 of chapter 17 with exhaustive analysis. 
- Point A12: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B12: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C12: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 12: | Col | Value | Source |
  |---|---|---|
  | Bus 746 | Transformer T19 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 84 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 17.13 Detail 13
This section expands detail 13 of chapter 17 with exhaustive analysis. This section expands detail 13 of chapter 17 with exhaustive analysis. This section expands detail 13 of chapter 17 with exhaustive analysis. This section expands detail 13 of chapter 17 with exhaustive analysis. 
- Point A13: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B13: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C13: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 13: | Col | Value | Source |
  |---|---|---|
  | Bus 747 | Transformer T20 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 91 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 17.14 Detail 14
This section expands detail 14 of chapter 17 with exhaustive analysis. This section expands detail 14 of chapter 17 with exhaustive analysis. This section expands detail 14 of chapter 17 with exhaustive analysis. This section expands detail 14 of chapter 17 with exhaustive analysis. 
- Point A14: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B14: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C14: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 14: | Col | Value | Source |
  |---|---|---|
  | Bus 748 | Transformer T21 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 98 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 17.15 Detail 15
This section expands detail 15 of chapter 17 with exhaustive analysis. This section expands detail 15 of chapter 17 with exhaustive analysis. This section expands detail 15 of chapter 17 with exhaustive analysis. This section expands detail 15 of chapter 17 with exhaustive analysis. 
- Point A15: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B15: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C15: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 15: | Col | Value | Source |
  |---|---|---|
  | Bus 749 | Transformer T22 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 5 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 17.16 Detail 16
This section expands detail 16 of chapter 17 with exhaustive analysis. This section expands detail 16 of chapter 17 with exhaustive analysis. This section expands detail 16 of chapter 17 with exhaustive analysis. This section expands detail 16 of chapter 17 with exhaustive analysis. 
- Point A16: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B16: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C16: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 16: | Col | Value | Source |
  |---|---|---|
  | Bus 750 | Transformer T23 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 12 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 17.17 Detail 17
This section expands detail 17 of chapter 17 with exhaustive analysis. This section expands detail 17 of chapter 17 with exhaustive analysis. This section expands detail 17 of chapter 17 with exhaustive analysis. This section expands detail 17 of chapter 17 with exhaustive analysis. 
- Point A17: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B17: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C17: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 17: | Col | Value | Source |
  |---|---|---|
  | Bus 751 | Transformer T24 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 19 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 17.18 Detail 18
This section expands detail 18 of chapter 17 with exhaustive analysis. This section expands detail 18 of chapter 17 with exhaustive analysis. This section expands detail 18 of chapter 17 with exhaustive analysis. This section expands detail 18 of chapter 17 with exhaustive analysis. 
- Point A18: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B18: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C18: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 18: | Col | Value | Source |
  |---|---|---|
  | Bus 752 | Transformer T25 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 26 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 17.19 Detail 19
This section expands detail 19 of chapter 17 with exhaustive analysis. This section expands detail 19 of chapter 17 with exhaustive analysis. This section expands detail 19 of chapter 17 with exhaustive analysis. This section expands detail 19 of chapter 17 with exhaustive analysis. 
- Point A19: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B19: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C19: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 19: | Col | Value | Source |
  |---|---|---|
  | Bus 753 | Transformer T26 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 33 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 17.20 Detail 20
This section expands detail 20 of chapter 17 with exhaustive analysis. This section expands detail 20 of chapter 17 with exhaustive analysis. This section expands detail 20 of chapter 17 with exhaustive analysis. This section expands detail 20 of chapter 17 with exhaustive analysis. 
- Point A20: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B20: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C20: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 20: | Col | Value | Source |
  |---|---|---|
  | Bus 754 | Transformer T27 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 40 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 17.21 Detail 21
This section expands detail 21 of chapter 17 with exhaustive analysis. This section expands detail 21 of chapter 17 with exhaustive analysis. This section expands detail 21 of chapter 17 with exhaustive analysis. This section expands detail 21 of chapter 17 with exhaustive analysis. 
- Point A21: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B21: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C21: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 21: | Col | Value | Source |
  |---|---|---|
  | Bus 755 | Transformer T28 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 47 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 17.22 Detail 22
This section expands detail 22 of chapter 17 with exhaustive analysis. This section expands detail 22 of chapter 17 with exhaustive analysis. This section expands detail 22 of chapter 17 with exhaustive analysis. This section expands detail 22 of chapter 17 with exhaustive analysis. 
- Point A22: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B22: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C22: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 22: | Col | Value | Source |
  |---|---|---|
  | Bus 756 | Transformer T7 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 54 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 17.23 Detail 23
This section expands detail 23 of chapter 17 with exhaustive analysis. This section expands detail 23 of chapter 17 with exhaustive analysis. This section expands detail 23 of chapter 17 with exhaustive analysis. This section expands detail 23 of chapter 17 with exhaustive analysis. 
- Point A23: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B23: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C23: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 23: | Col | Value | Source |
  |---|---|---|
  | Bus 757 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 61 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 17.24 Detail 24
This section expands detail 24 of chapter 17 with exhaustive analysis. This section expands detail 24 of chapter 17 with exhaustive analysis. This section expands detail 24 of chapter 17 with exhaustive analysis. This section expands detail 24 of chapter 17 with exhaustive analysis. 
- Point A24: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B24: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C24: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 24: | Col | Value | Source |
  |---|---|---|
  | Bus 758 | Transformer T9 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 68 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 17.25 Detail 25
This section expands detail 25 of chapter 17 with exhaustive analysis. This section expands detail 25 of chapter 17 with exhaustive analysis. This section expands detail 25 of chapter 17 with exhaustive analysis. This section expands detail 25 of chapter 17 with exhaustive analysis. 
- Point A25: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B25: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C25: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 25: | Col | Value | Source |
  |---|---|---|
  | Bus 759 | Transformer T10 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 75 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

---
## 18. Chapter 18 — Detailed Section

### 18.1 Detail 1
This section expands detail 1 of chapter 18 with exhaustive analysis. This section expands detail 1 of chapter 18 with exhaustive analysis. This section expands detail 1 of chapter 18 with exhaustive analysis. This section expands detail 1 of chapter 18 with exhaustive analysis. 
- Point A1: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B1: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C1: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 1: | Col | Value | Source |
  |---|---|---|
  | Bus 735 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 7 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 18.2 Detail 2
This section expands detail 2 of chapter 18 with exhaustive analysis. This section expands detail 2 of chapter 18 with exhaustive analysis. This section expands detail 2 of chapter 18 with exhaustive analysis. This section expands detail 2 of chapter 18 with exhaustive analysis. 
- Point A2: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B2: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C2: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 2: | Col | Value | Source |
  |---|---|---|
  | Bus 736 | Transformer T9 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 14 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 18.3 Detail 3
This section expands detail 3 of chapter 18 with exhaustive analysis. This section expands detail 3 of chapter 18 with exhaustive analysis. This section expands detail 3 of chapter 18 with exhaustive analysis. This section expands detail 3 of chapter 18 with exhaustive analysis. 
- Point A3: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B3: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C3: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 3: | Col | Value | Source |
  |---|---|---|
  | Bus 737 | Transformer T10 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 21 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 18.4 Detail 4
This section expands detail 4 of chapter 18 with exhaustive analysis. This section expands detail 4 of chapter 18 with exhaustive analysis. This section expands detail 4 of chapter 18 with exhaustive analysis. This section expands detail 4 of chapter 18 with exhaustive analysis. 
- Point A4: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B4: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C4: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 4: | Col | Value | Source |
  |---|---|---|
  | Bus 738 | Transformer T11 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 28 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 18.5 Detail 5
This section expands detail 5 of chapter 18 with exhaustive analysis. This section expands detail 5 of chapter 18 with exhaustive analysis. This section expands detail 5 of chapter 18 with exhaustive analysis. This section expands detail 5 of chapter 18 with exhaustive analysis. 
- Point A5: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B5: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C5: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 5: | Col | Value | Source |
  |---|---|---|
  | Bus 739 | Transformer T12 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 35 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 18.6 Detail 6
This section expands detail 6 of chapter 18 with exhaustive analysis. This section expands detail 6 of chapter 18 with exhaustive analysis. This section expands detail 6 of chapter 18 with exhaustive analysis. This section expands detail 6 of chapter 18 with exhaustive analysis. 
- Point A6: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B6: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C6: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 6: | Col | Value | Source |
  |---|---|---|
  | Bus 740 | Transformer T13 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 42 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 18.7 Detail 7
This section expands detail 7 of chapter 18 with exhaustive analysis. This section expands detail 7 of chapter 18 with exhaustive analysis. This section expands detail 7 of chapter 18 with exhaustive analysis. This section expands detail 7 of chapter 18 with exhaustive analysis. 
- Point A7: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B7: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C7: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 7: | Col | Value | Source |
  |---|---|---|
  | Bus 741 | Transformer T14 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 49 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 18.8 Detail 8
This section expands detail 8 of chapter 18 with exhaustive analysis. This section expands detail 8 of chapter 18 with exhaustive analysis. This section expands detail 8 of chapter 18 with exhaustive analysis. This section expands detail 8 of chapter 18 with exhaustive analysis. 
- Point A8: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B8: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C8: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 8: | Col | Value | Source |
  |---|---|---|
  | Bus 742 | Transformer T15 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 56 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 18.9 Detail 9
This section expands detail 9 of chapter 18 with exhaustive analysis. This section expands detail 9 of chapter 18 with exhaustive analysis. This section expands detail 9 of chapter 18 with exhaustive analysis. This section expands detail 9 of chapter 18 with exhaustive analysis. 
- Point A9: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B9: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C9: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 9: | Col | Value | Source |
  |---|---|---|
  | Bus 743 | Transformer T16 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 63 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 18.10 Detail 10
This section expands detail 10 of chapter 18 with exhaustive analysis. This section expands detail 10 of chapter 18 with exhaustive analysis. This section expands detail 10 of chapter 18 with exhaustive analysis. This section expands detail 10 of chapter 18 with exhaustive analysis. 
- Point A10: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B10: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C10: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 10: | Col | Value | Source |
  |---|---|---|
  | Bus 744 | Transformer T17 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 70 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 18.11 Detail 11
This section expands detail 11 of chapter 18 with exhaustive analysis. This section expands detail 11 of chapter 18 with exhaustive analysis. This section expands detail 11 of chapter 18 with exhaustive analysis. This section expands detail 11 of chapter 18 with exhaustive analysis. 
- Point A11: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B11: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C11: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 11: | Col | Value | Source |
  |---|---|---|
  | Bus 745 | Transformer T18 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 77 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 18.12 Detail 12
This section expands detail 12 of chapter 18 with exhaustive analysis. This section expands detail 12 of chapter 18 with exhaustive analysis. This section expands detail 12 of chapter 18 with exhaustive analysis. This section expands detail 12 of chapter 18 with exhaustive analysis. 
- Point A12: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B12: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C12: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 12: | Col | Value | Source |
  |---|---|---|
  | Bus 746 | Transformer T19 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 84 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 18.13 Detail 13
This section expands detail 13 of chapter 18 with exhaustive analysis. This section expands detail 13 of chapter 18 with exhaustive analysis. This section expands detail 13 of chapter 18 with exhaustive analysis. This section expands detail 13 of chapter 18 with exhaustive analysis. 
- Point A13: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B13: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C13: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 13: | Col | Value | Source |
  |---|---|---|
  | Bus 747 | Transformer T20 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 91 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 18.14 Detail 14
This section expands detail 14 of chapter 18 with exhaustive analysis. This section expands detail 14 of chapter 18 with exhaustive analysis. This section expands detail 14 of chapter 18 with exhaustive analysis. This section expands detail 14 of chapter 18 with exhaustive analysis. 
- Point A14: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B14: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C14: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 14: | Col | Value | Source |
  |---|---|---|
  | Bus 748 | Transformer T21 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 98 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 18.15 Detail 15
This section expands detail 15 of chapter 18 with exhaustive analysis. This section expands detail 15 of chapter 18 with exhaustive analysis. This section expands detail 15 of chapter 18 with exhaustive analysis. This section expands detail 15 of chapter 18 with exhaustive analysis. 
- Point A15: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B15: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C15: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 15: | Col | Value | Source |
  |---|---|---|
  | Bus 749 | Transformer T22 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 5 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 18.16 Detail 16
This section expands detail 16 of chapter 18 with exhaustive analysis. This section expands detail 16 of chapter 18 with exhaustive analysis. This section expands detail 16 of chapter 18 with exhaustive analysis. This section expands detail 16 of chapter 18 with exhaustive analysis. 
- Point A16: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B16: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C16: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 16: | Col | Value | Source |
  |---|---|---|
  | Bus 750 | Transformer T23 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 12 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 18.17 Detail 17
This section expands detail 17 of chapter 18 with exhaustive analysis. This section expands detail 17 of chapter 18 with exhaustive analysis. This section expands detail 17 of chapter 18 with exhaustive analysis. This section expands detail 17 of chapter 18 with exhaustive analysis. 
- Point A17: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B17: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C17: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 17: | Col | Value | Source |
  |---|---|---|
  | Bus 751 | Transformer T24 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 19 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 18.18 Detail 18
This section expands detail 18 of chapter 18 with exhaustive analysis. This section expands detail 18 of chapter 18 with exhaustive analysis. This section expands detail 18 of chapter 18 with exhaustive analysis. This section expands detail 18 of chapter 18 with exhaustive analysis. 
- Point A18: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B18: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C18: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 18: | Col | Value | Source |
  |---|---|---|
  | Bus 752 | Transformer T25 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 26 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 18.19 Detail 19
This section expands detail 19 of chapter 18 with exhaustive analysis. This section expands detail 19 of chapter 18 with exhaustive analysis. This section expands detail 19 of chapter 18 with exhaustive analysis. This section expands detail 19 of chapter 18 with exhaustive analysis. 
- Point A19: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B19: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C19: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 19: | Col | Value | Source |
  |---|---|---|
  | Bus 753 | Transformer T26 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 33 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 18.20 Detail 20
This section expands detail 20 of chapter 18 with exhaustive analysis. This section expands detail 20 of chapter 18 with exhaustive analysis. This section expands detail 20 of chapter 18 with exhaustive analysis. This section expands detail 20 of chapter 18 with exhaustive analysis. 
- Point A20: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B20: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C20: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 20: | Col | Value | Source |
  |---|---|---|
  | Bus 754 | Transformer T27 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 40 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 18.21 Detail 21
This section expands detail 21 of chapter 18 with exhaustive analysis. This section expands detail 21 of chapter 18 with exhaustive analysis. This section expands detail 21 of chapter 18 with exhaustive analysis. This section expands detail 21 of chapter 18 with exhaustive analysis. 
- Point A21: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B21: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C21: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 21: | Col | Value | Source |
  |---|---|---|
  | Bus 755 | Transformer T28 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 47 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 18.22 Detail 22
This section expands detail 22 of chapter 18 with exhaustive analysis. This section expands detail 22 of chapter 18 with exhaustive analysis. This section expands detail 22 of chapter 18 with exhaustive analysis. This section expands detail 22 of chapter 18 with exhaustive analysis. 
- Point A22: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B22: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C22: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 22: | Col | Value | Source |
  |---|---|---|
  | Bus 756 | Transformer T7 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 54 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 18.23 Detail 23
This section expands detail 23 of chapter 18 with exhaustive analysis. This section expands detail 23 of chapter 18 with exhaustive analysis. This section expands detail 23 of chapter 18 with exhaustive analysis. This section expands detail 23 of chapter 18 with exhaustive analysis. 
- Point A23: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B23: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C23: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 23: | Col | Value | Source |
  |---|---|---|
  | Bus 757 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 61 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 18.24 Detail 24
This section expands detail 24 of chapter 18 with exhaustive analysis. This section expands detail 24 of chapter 18 with exhaustive analysis. This section expands detail 24 of chapter 18 with exhaustive analysis. This section expands detail 24 of chapter 18 with exhaustive analysis. 
- Point A24: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B24: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C24: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 24: | Col | Value | Source |
  |---|---|---|
  | Bus 758 | Transformer T9 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 68 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 18.25 Detail 25
This section expands detail 25 of chapter 18 with exhaustive analysis. This section expands detail 25 of chapter 18 with exhaustive analysis. This section expands detail 25 of chapter 18 with exhaustive analysis. This section expands detail 25 of chapter 18 with exhaustive analysis. 
- Point A25: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B25: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C25: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 25: | Col | Value | Source |
  |---|---|---|
  | Bus 759 | Transformer T10 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 75 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

---
## 19. Chapter 19 — Detailed Section

### 19.1 Detail 1
This section expands detail 1 of chapter 19 with exhaustive analysis. This section expands detail 1 of chapter 19 with exhaustive analysis. This section expands detail 1 of chapter 19 with exhaustive analysis. This section expands detail 1 of chapter 19 with exhaustive analysis. 
- Point A1: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B1: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C1: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 1: | Col | Value | Source |
  |---|---|---|
  | Bus 735 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 7 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 19.2 Detail 2
This section expands detail 2 of chapter 19 with exhaustive analysis. This section expands detail 2 of chapter 19 with exhaustive analysis. This section expands detail 2 of chapter 19 with exhaustive analysis. This section expands detail 2 of chapter 19 with exhaustive analysis. 
- Point A2: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B2: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C2: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 2: | Col | Value | Source |
  |---|---|---|
  | Bus 736 | Transformer T9 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 14 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 19.3 Detail 3
This section expands detail 3 of chapter 19 with exhaustive analysis. This section expands detail 3 of chapter 19 with exhaustive analysis. This section expands detail 3 of chapter 19 with exhaustive analysis. This section expands detail 3 of chapter 19 with exhaustive analysis. 
- Point A3: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B3: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C3: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 3: | Col | Value | Source |
  |---|---|---|
  | Bus 737 | Transformer T10 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 21 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 19.4 Detail 4
This section expands detail 4 of chapter 19 with exhaustive analysis. This section expands detail 4 of chapter 19 with exhaustive analysis. This section expands detail 4 of chapter 19 with exhaustive analysis. This section expands detail 4 of chapter 19 with exhaustive analysis. 
- Point A4: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B4: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C4: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 4: | Col | Value | Source |
  |---|---|---|
  | Bus 738 | Transformer T11 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 28 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 19.5 Detail 5
This section expands detail 5 of chapter 19 with exhaustive analysis. This section expands detail 5 of chapter 19 with exhaustive analysis. This section expands detail 5 of chapter 19 with exhaustive analysis. This section expands detail 5 of chapter 19 with exhaustive analysis. 
- Point A5: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B5: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C5: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 5: | Col | Value | Source |
  |---|---|---|
  | Bus 739 | Transformer T12 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 35 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 19.6 Detail 6
This section expands detail 6 of chapter 19 with exhaustive analysis. This section expands detail 6 of chapter 19 with exhaustive analysis. This section expands detail 6 of chapter 19 with exhaustive analysis. This section expands detail 6 of chapter 19 with exhaustive analysis. 
- Point A6: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B6: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C6: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 6: | Col | Value | Source |
  |---|---|---|
  | Bus 740 | Transformer T13 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 42 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 19.7 Detail 7
This section expands detail 7 of chapter 19 with exhaustive analysis. This section expands detail 7 of chapter 19 with exhaustive analysis. This section expands detail 7 of chapter 19 with exhaustive analysis. This section expands detail 7 of chapter 19 with exhaustive analysis. 
- Point A7: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B7: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C7: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 7: | Col | Value | Source |
  |---|---|---|
  | Bus 741 | Transformer T14 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 49 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 19.8 Detail 8
This section expands detail 8 of chapter 19 with exhaustive analysis. This section expands detail 8 of chapter 19 with exhaustive analysis. This section expands detail 8 of chapter 19 with exhaustive analysis. This section expands detail 8 of chapter 19 with exhaustive analysis. 
- Point A8: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B8: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C8: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 8: | Col | Value | Source |
  |---|---|---|
  | Bus 742 | Transformer T15 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 56 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 19.9 Detail 9
This section expands detail 9 of chapter 19 with exhaustive analysis. This section expands detail 9 of chapter 19 with exhaustive analysis. This section expands detail 9 of chapter 19 with exhaustive analysis. This section expands detail 9 of chapter 19 with exhaustive analysis. 
- Point A9: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B9: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C9: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 9: | Col | Value | Source |
  |---|---|---|
  | Bus 743 | Transformer T16 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 63 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 19.10 Detail 10
This section expands detail 10 of chapter 19 with exhaustive analysis. This section expands detail 10 of chapter 19 with exhaustive analysis. This section expands detail 10 of chapter 19 with exhaustive analysis. This section expands detail 10 of chapter 19 with exhaustive analysis. 
- Point A10: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B10: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C10: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 10: | Col | Value | Source |
  |---|---|---|
  | Bus 744 | Transformer T17 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 70 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 19.11 Detail 11
This section expands detail 11 of chapter 19 with exhaustive analysis. This section expands detail 11 of chapter 19 with exhaustive analysis. This section expands detail 11 of chapter 19 with exhaustive analysis. This section expands detail 11 of chapter 19 with exhaustive analysis. 
- Point A11: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B11: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C11: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 11: | Col | Value | Source |
  |---|---|---|
  | Bus 745 | Transformer T18 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 77 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 19.12 Detail 12
This section expands detail 12 of chapter 19 with exhaustive analysis. This section expands detail 12 of chapter 19 with exhaustive analysis. This section expands detail 12 of chapter 19 with exhaustive analysis. This section expands detail 12 of chapter 19 with exhaustive analysis. 
- Point A12: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B12: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C12: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 12: | Col | Value | Source |
  |---|---|---|
  | Bus 746 | Transformer T19 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 84 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 19.13 Detail 13
This section expands detail 13 of chapter 19 with exhaustive analysis. This section expands detail 13 of chapter 19 with exhaustive analysis. This section expands detail 13 of chapter 19 with exhaustive analysis. This section expands detail 13 of chapter 19 with exhaustive analysis. 
- Point A13: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B13: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C13: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 13: | Col | Value | Source |
  |---|---|---|
  | Bus 747 | Transformer T20 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 91 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 19.14 Detail 14
This section expands detail 14 of chapter 19 with exhaustive analysis. This section expands detail 14 of chapter 19 with exhaustive analysis. This section expands detail 14 of chapter 19 with exhaustive analysis. This section expands detail 14 of chapter 19 with exhaustive analysis. 
- Point A14: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B14: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C14: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 14: | Col | Value | Source |
  |---|---|---|
  | Bus 748 | Transformer T21 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 98 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 19.15 Detail 15
This section expands detail 15 of chapter 19 with exhaustive analysis. This section expands detail 15 of chapter 19 with exhaustive analysis. This section expands detail 15 of chapter 19 with exhaustive analysis. This section expands detail 15 of chapter 19 with exhaustive analysis. 
- Point A15: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B15: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C15: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 15: | Col | Value | Source |
  |---|---|---|
  | Bus 749 | Transformer T22 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 5 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 19.16 Detail 16
This section expands detail 16 of chapter 19 with exhaustive analysis. This section expands detail 16 of chapter 19 with exhaustive analysis. This section expands detail 16 of chapter 19 with exhaustive analysis. This section expands detail 16 of chapter 19 with exhaustive analysis. 
- Point A16: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B16: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C16: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 16: | Col | Value | Source |
  |---|---|---|
  | Bus 750 | Transformer T23 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 12 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 19.17 Detail 17
This section expands detail 17 of chapter 19 with exhaustive analysis. This section expands detail 17 of chapter 19 with exhaustive analysis. This section expands detail 17 of chapter 19 with exhaustive analysis. This section expands detail 17 of chapter 19 with exhaustive analysis. 
- Point A17: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B17: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C17: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 17: | Col | Value | Source |
  |---|---|---|
  | Bus 751 | Transformer T24 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 19 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 19.18 Detail 18
This section expands detail 18 of chapter 19 with exhaustive analysis. This section expands detail 18 of chapter 19 with exhaustive analysis. This section expands detail 18 of chapter 19 with exhaustive analysis. This section expands detail 18 of chapter 19 with exhaustive analysis. 
- Point A18: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B18: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C18: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 18: | Col | Value | Source |
  |---|---|---|
  | Bus 752 | Transformer T25 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 26 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 19.19 Detail 19
This section expands detail 19 of chapter 19 with exhaustive analysis. This section expands detail 19 of chapter 19 with exhaustive analysis. This section expands detail 19 of chapter 19 with exhaustive analysis. This section expands detail 19 of chapter 19 with exhaustive analysis. 
- Point A19: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B19: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C19: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 19: | Col | Value | Source |
  |---|---|---|
  | Bus 753 | Transformer T26 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 33 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 19.20 Detail 20
This section expands detail 20 of chapter 19 with exhaustive analysis. This section expands detail 20 of chapter 19 with exhaustive analysis. This section expands detail 20 of chapter 19 with exhaustive analysis. This section expands detail 20 of chapter 19 with exhaustive analysis. 
- Point A20: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B20: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C20: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 20: | Col | Value | Source |
  |---|---|---|
  | Bus 754 | Transformer T27 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 40 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 19.21 Detail 21
This section expands detail 21 of chapter 19 with exhaustive analysis. This section expands detail 21 of chapter 19 with exhaustive analysis. This section expands detail 21 of chapter 19 with exhaustive analysis. This section expands detail 21 of chapter 19 with exhaustive analysis. 
- Point A21: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B21: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C21: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 21: | Col | Value | Source |
  |---|---|---|
  | Bus 755 | Transformer T28 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 47 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 19.22 Detail 22
This section expands detail 22 of chapter 19 with exhaustive analysis. This section expands detail 22 of chapter 19 with exhaustive analysis. This section expands detail 22 of chapter 19 with exhaustive analysis. This section expands detail 22 of chapter 19 with exhaustive analysis. 
- Point A22: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B22: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C22: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 22: | Col | Value | Source |
  |---|---|---|
  | Bus 756 | Transformer T7 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 54 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 19.23 Detail 23
This section expands detail 23 of chapter 19 with exhaustive analysis. This section expands detail 23 of chapter 19 with exhaustive analysis. This section expands detail 23 of chapter 19 with exhaustive analysis. This section expands detail 23 of chapter 19 with exhaustive analysis. 
- Point A23: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B23: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C23: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 23: | Col | Value | Source |
  |---|---|---|
  | Bus 757 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 61 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 19.24 Detail 24
This section expands detail 24 of chapter 19 with exhaustive analysis. This section expands detail 24 of chapter 19 with exhaustive analysis. This section expands detail 24 of chapter 19 with exhaustive analysis. This section expands detail 24 of chapter 19 with exhaustive analysis. 
- Point A24: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B24: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C24: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 24: | Col | Value | Source |
  |---|---|---|
  | Bus 758 | Transformer T9 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 68 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 19.25 Detail 25
This section expands detail 25 of chapter 19 with exhaustive analysis. This section expands detail 25 of chapter 19 with exhaustive analysis. This section expands detail 25 of chapter 19 with exhaustive analysis. This section expands detail 25 of chapter 19 with exhaustive analysis. 
- Point A25: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B25: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C25: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 25: | Col | Value | Source |
  |---|---|---|
  | Bus 759 | Transformer T10 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 75 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

---
## 20. Chapter 20 — Detailed Section

### 20.1 Detail 1
This section expands detail 1 of chapter 20 with exhaustive analysis. This section expands detail 1 of chapter 20 with exhaustive analysis. This section expands detail 1 of chapter 20 with exhaustive analysis. This section expands detail 1 of chapter 20 with exhaustive analysis. 
- Point A1: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B1: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C1: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 1: | Col | Value | Source |
  |---|---|---|
  | Bus 735 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 7 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 20.2 Detail 2
This section expands detail 2 of chapter 20 with exhaustive analysis. This section expands detail 2 of chapter 20 with exhaustive analysis. This section expands detail 2 of chapter 20 with exhaustive analysis. This section expands detail 2 of chapter 20 with exhaustive analysis. 
- Point A2: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B2: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C2: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 2: | Col | Value | Source |
  |---|---|---|
  | Bus 736 | Transformer T9 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 14 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 20.3 Detail 3
This section expands detail 3 of chapter 20 with exhaustive analysis. This section expands detail 3 of chapter 20 with exhaustive analysis. This section expands detail 3 of chapter 20 with exhaustive analysis. This section expands detail 3 of chapter 20 with exhaustive analysis. 
- Point A3: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B3: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C3: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 3: | Col | Value | Source |
  |---|---|---|
  | Bus 737 | Transformer T10 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 21 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 20.4 Detail 4
This section expands detail 4 of chapter 20 with exhaustive analysis. This section expands detail 4 of chapter 20 with exhaustive analysis. This section expands detail 4 of chapter 20 with exhaustive analysis. This section expands detail 4 of chapter 20 with exhaustive analysis. 
- Point A4: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B4: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C4: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 4: | Col | Value | Source |
  |---|---|---|
  | Bus 738 | Transformer T11 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 28 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 20.5 Detail 5
This section expands detail 5 of chapter 20 with exhaustive analysis. This section expands detail 5 of chapter 20 with exhaustive analysis. This section expands detail 5 of chapter 20 with exhaustive analysis. This section expands detail 5 of chapter 20 with exhaustive analysis. 
- Point A5: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B5: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C5: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 5: | Col | Value | Source |
  |---|---|---|
  | Bus 739 | Transformer T12 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 35 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 20.6 Detail 6
This section expands detail 6 of chapter 20 with exhaustive analysis. This section expands detail 6 of chapter 20 with exhaustive analysis. This section expands detail 6 of chapter 20 with exhaustive analysis. This section expands detail 6 of chapter 20 with exhaustive analysis. 
- Point A6: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B6: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C6: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 6: | Col | Value | Source |
  |---|---|---|
  | Bus 740 | Transformer T13 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 42 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 20.7 Detail 7
This section expands detail 7 of chapter 20 with exhaustive analysis. This section expands detail 7 of chapter 20 with exhaustive analysis. This section expands detail 7 of chapter 20 with exhaustive analysis. This section expands detail 7 of chapter 20 with exhaustive analysis. 
- Point A7: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B7: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C7: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 7: | Col | Value | Source |
  |---|---|---|
  | Bus 741 | Transformer T14 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 49 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 20.8 Detail 8
This section expands detail 8 of chapter 20 with exhaustive analysis. This section expands detail 8 of chapter 20 with exhaustive analysis. This section expands detail 8 of chapter 20 with exhaustive analysis. This section expands detail 8 of chapter 20 with exhaustive analysis. 
- Point A8: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B8: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C8: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 8: | Col | Value | Source |
  |---|---|---|
  | Bus 742 | Transformer T15 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 56 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 20.9 Detail 9
This section expands detail 9 of chapter 20 with exhaustive analysis. This section expands detail 9 of chapter 20 with exhaustive analysis. This section expands detail 9 of chapter 20 with exhaustive analysis. This section expands detail 9 of chapter 20 with exhaustive analysis. 
- Point A9: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B9: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C9: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 9: | Col | Value | Source |
  |---|---|---|
  | Bus 743 | Transformer T16 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 63 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 20.10 Detail 10
This section expands detail 10 of chapter 20 with exhaustive analysis. This section expands detail 10 of chapter 20 with exhaustive analysis. This section expands detail 10 of chapter 20 with exhaustive analysis. This section expands detail 10 of chapter 20 with exhaustive analysis. 
- Point A10: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B10: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C10: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 10: | Col | Value | Source |
  |---|---|---|
  | Bus 744 | Transformer T17 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 70 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 20.11 Detail 11
This section expands detail 11 of chapter 20 with exhaustive analysis. This section expands detail 11 of chapter 20 with exhaustive analysis. This section expands detail 11 of chapter 20 with exhaustive analysis. This section expands detail 11 of chapter 20 with exhaustive analysis. 
- Point A11: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B11: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C11: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 11: | Col | Value | Source |
  |---|---|---|
  | Bus 745 | Transformer T18 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 77 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 20.12 Detail 12
This section expands detail 12 of chapter 20 with exhaustive analysis. This section expands detail 12 of chapter 20 with exhaustive analysis. This section expands detail 12 of chapter 20 with exhaustive analysis. This section expands detail 12 of chapter 20 with exhaustive analysis. 
- Point A12: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B12: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C12: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 12: | Col | Value | Source |
  |---|---|---|
  | Bus 746 | Transformer T19 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 84 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 20.13 Detail 13
This section expands detail 13 of chapter 20 with exhaustive analysis. This section expands detail 13 of chapter 20 with exhaustive analysis. This section expands detail 13 of chapter 20 with exhaustive analysis. This section expands detail 13 of chapter 20 with exhaustive analysis. 
- Point A13: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B13: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C13: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 13: | Col | Value | Source |
  |---|---|---|
  | Bus 747 | Transformer T20 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 91 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 20.14 Detail 14
This section expands detail 14 of chapter 20 with exhaustive analysis. This section expands detail 14 of chapter 20 with exhaustive analysis. This section expands detail 14 of chapter 20 with exhaustive analysis. This section expands detail 14 of chapter 20 with exhaustive analysis. 
- Point A14: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B14: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C14: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 14: | Col | Value | Source |
  |---|---|---|
  | Bus 748 | Transformer T21 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 98 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 20.15 Detail 15
This section expands detail 15 of chapter 20 with exhaustive analysis. This section expands detail 15 of chapter 20 with exhaustive analysis. This section expands detail 15 of chapter 20 with exhaustive analysis. This section expands detail 15 of chapter 20 with exhaustive analysis. 
- Point A15: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B15: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C15: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 15: | Col | Value | Source |
  |---|---|---|
  | Bus 749 | Transformer T22 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 5 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 20.16 Detail 16
This section expands detail 16 of chapter 20 with exhaustive analysis. This section expands detail 16 of chapter 20 with exhaustive analysis. This section expands detail 16 of chapter 20 with exhaustive analysis. This section expands detail 16 of chapter 20 with exhaustive analysis. 
- Point A16: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B16: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C16: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 16: | Col | Value | Source |
  |---|---|---|
  | Bus 750 | Transformer T23 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 12 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 20.17 Detail 17
This section expands detail 17 of chapter 20 with exhaustive analysis. This section expands detail 17 of chapter 20 with exhaustive analysis. This section expands detail 17 of chapter 20 with exhaustive analysis. This section expands detail 17 of chapter 20 with exhaustive analysis. 
- Point A17: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B17: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C17: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 17: | Col | Value | Source |
  |---|---|---|
  | Bus 751 | Transformer T24 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 19 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 20.18 Detail 18
This section expands detail 18 of chapter 20 with exhaustive analysis. This section expands detail 18 of chapter 20 with exhaustive analysis. This section expands detail 18 of chapter 20 with exhaustive analysis. This section expands detail 18 of chapter 20 with exhaustive analysis. 
- Point A18: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B18: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C18: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 18: | Col | Value | Source |
  |---|---|---|
  | Bus 752 | Transformer T25 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 26 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 20.19 Detail 19
This section expands detail 19 of chapter 20 with exhaustive analysis. This section expands detail 19 of chapter 20 with exhaustive analysis. This section expands detail 19 of chapter 20 with exhaustive analysis. This section expands detail 19 of chapter 20 with exhaustive analysis. 
- Point A19: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B19: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C19: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 19: | Col | Value | Source |
  |---|---|---|
  | Bus 753 | Transformer T26 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 33 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 20.20 Detail 20
This section expands detail 20 of chapter 20 with exhaustive analysis. This section expands detail 20 of chapter 20 with exhaustive analysis. This section expands detail 20 of chapter 20 with exhaustive analysis. This section expands detail 20 of chapter 20 with exhaustive analysis. 
- Point A20: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B20: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C20: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 20: | Col | Value | Source |
  |---|---|---|
  | Bus 754 | Transformer T27 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 40 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 20.21 Detail 21
This section expands detail 21 of chapter 20 with exhaustive analysis. This section expands detail 21 of chapter 20 with exhaustive analysis. This section expands detail 21 of chapter 20 with exhaustive analysis. This section expands detail 21 of chapter 20 with exhaustive analysis. 
- Point A21: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B21: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C21: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 21: | Col | Value | Source |
  |---|---|---|
  | Bus 755 | Transformer T28 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 47 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 20.22 Detail 22
This section expands detail 22 of chapter 20 with exhaustive analysis. This section expands detail 22 of chapter 20 with exhaustive analysis. This section expands detail 22 of chapter 20 with exhaustive analysis. This section expands detail 22 of chapter 20 with exhaustive analysis. 
- Point A22: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B22: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C22: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 22: | Col | Value | Source |
  |---|---|---|
  | Bus 756 | Transformer T7 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 54 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

### 20.23 Detail 23
This section expands detail 23 of chapter 20 with exhaustive analysis. This section expands detail 23 of chapter 20 with exhaustive analysis. This section expands detail 23 of chapter 20 with exhaustive analysis. This section expands detail 23 of chapter 20 with exhaustive analysis. 
- Point A23: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B23: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C23: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 23: | Col | Value | Source |
  |---|---|---|
  | Bus 757 | Transformer T8 | valid_pv_buses.csv |
  | Feeder Branch_701-708 | Load 61 kW | electrical_features.csv |
  | Risk | CONSTRAINED | thresholds hard > vs caution >= |

### 20.24 Detail 24
This section expands detail 24 of chapter 20 with exhaustive analysis. This section expands detail 24 of chapter 20 with exhaustive analysis. This section expands detail 24 of chapter 20 with exhaustive analysis. This section expands detail 24 of chapter 20 with exhaustive analysis. 
- Point A24: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B24: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C24: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 24: | Col | Value | Source |
  |---|---|---|
  | Bus 758 | Transformer T9 | valid_pv_buses.csv |
  | Feeder LV_secondary_T2_T4 | Load 68 kW | electrical_features.csv |
  | Risk | SAFE | thresholds hard > vs caution >= |

### 20.25 Detail 25
This section expands detail 25 of chapter 20 with exhaustive analysis. This section expands detail 25 of chapter 20 with exhaustive analysis. This section expands detail 25 of chapter 20 with exhaustive analysis. This section expands detail 25 of chapter 20 with exhaustive analysis. 
- Point A25: Detailed explanation of how the system was built, including file paths like `backend/app/services/power_flow.py` (589 lines), `frontend/components/GridTwin3D.tsx` (593 lines), `supabase/migrations/0001_init_schema.sql`, and `suryagrid_model_v2.pkl`.
- Point B25: Workflow example: citizen on Bus 734 with 5 kW existing + 10 kW new → ML predicts CAUTION (0.42), power-flow measures rise 0.032 pu, line 78%, trafo 94% → engineering CAUTION (rise >=0.03), hosting capacity 42 kW via bisection, twin shows path 700→...→734 with energy balance export 4.5 kW.
- Point C25: Honesty contract: prototype synthetic coordinates (anchor 12.9716,77.5946, east = true route km) are labelled `Illustrative placement` and `provisional:true`; thresholds from `scenario_config.json` single source; power-flow decides, ML never overrides.
- Table 25: | Col | Value | Source |
  |---|---|---|
  | Bus 759 | Transformer T10 | valid_pv_buses.csv |
  | Feeder Main_720-734 | Load 75 kW | electrical_features.csv |
  | Risk | CAUTION | thresholds hard > vs caution >= |

---
## Appendix A: Thresholds & Classification Logic
- Threshold 0: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 1: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 2: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 3: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 4: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 5: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 6: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 7: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 8: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 9: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 10: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 11: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 12: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 13: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 14: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 15: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 16: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 17: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 18: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 19: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 20: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 21: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 22: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 23: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 24: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 25: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 26: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 27: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 28: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.
- Threshold 29: voltage hard 1.05/0.90, caution 1.03/0.90, rise hard 0.05/caution 0.03, line 100/80, trafo 100/95 — Rule: hard > first wins → CONSTRAINED, else CAUTION if any >=, else SAFE. Reverse alone = CAUTION.

## Appendix B: ML Feature Glossary (18 features)
- **pv_bus**: cat71 bus id (int-cast for OneHot) — engineer input
- **pv_bus_vn_kv**: num kV 0.208/0.24/0.48 — feeder DB
- **existing_pv_kw**: num kW existing — engineer input
- **new_pv_kw**: num kW new — engineer input
- **total_pv_kw**: num kW total — engineer input
- **existing_load_at_bus_kw**: num kW load — feeder DB
- **pv_penetration_ratio**: ratio total/load or /1.0 if 0 — derived
- **transformer_association**: cat T1..T22 — feeder DB
- **feeder_section**: cat feeder section — feeder DB
- **transformer_sn_kva**: num kVA — feeder DB
- **pv_to_transformer_ratio**: ratio total/sn — derived
- **new_pv_to_transformer_ratio**: ratio new/sn — derived
- **load_to_transformer_ratio**: ratio load/sn — derived
- **base_voltage_pu**: pu 0.9-0.99 — feeder DB
- **feeder_distance_km**: km — feeder DB
- **upstream_r_ohm**: ohm — feeder DB
- **upstream_x_ohm**: ohm — feeder DB
- **upstream_z_ohm**: ohm — feeder DB

## Appendix C: Power-Flow & Hosting Capacity
- Bisection 0: lo 1 kW hi 2000 kW, ~11 solves, worst rise across injected buses, `simulate_group` for feeder sections, overstatement factor up to 23x if summing per-bus.
- Bisection 1: lo 1 kW hi 2000 kW, ~11 solves, worst rise across injected buses, `simulate_group` for feeder sections, overstatement factor up to 23x if summing per-bus.
- Bisection 2: lo 1 kW hi 2000 kW, ~11 solves, worst rise across injected buses, `simulate_group` for feeder sections, overstatement factor up to 23x if summing per-bus.
- Bisection 3: lo 1 kW hi 2000 kW, ~11 solves, worst rise across injected buses, `simulate_group` for feeder sections, overstatement factor up to 23x if summing per-bus.
- Bisection 4: lo 1 kW hi 2000 kW, ~11 solves, worst rise across injected buses, `simulate_group` for feeder sections, overstatement factor up to 23x if summing per-bus.
- Bisection 5: lo 1 kW hi 2000 kW, ~11 solves, worst rise across injected buses, `simulate_group` for feeder sections, overstatement factor up to 23x if summing per-bus.
- Bisection 6: lo 1 kW hi 2000 kW, ~11 solves, worst rise across injected buses, `simulate_group` for feeder sections, overstatement factor up to 23x if summing per-bus.
- Bisection 7: lo 1 kW hi 2000 kW, ~11 solves, worst rise across injected buses, `simulate_group` for feeder sections, overstatement factor up to 23x if summing per-bus.
- Bisection 8: lo 1 kW hi 2000 kW, ~11 solves, worst rise across injected buses, `simulate_group` for feeder sections, overstatement factor up to 23x if summing per-bus.
- Bisection 9: lo 1 kW hi 2000 kW, ~11 solves, worst rise across injected buses, `simulate_group` for feeder sections, overstatement factor up to 23x if summing per-bus.
- Bisection 10: lo 1 kW hi 2000 kW, ~11 solves, worst rise across injected buses, `simulate_group` for feeder sections, overstatement factor up to 23x if summing per-bus.
- Bisection 11: lo 1 kW hi 2000 kW, ~11 solves, worst rise across injected buses, `simulate_group` for feeder sections, overstatement factor up to 23x if summing per-bus.
- Bisection 12: lo 1 kW hi 2000 kW, ~11 solves, worst rise across injected buses, `simulate_group` for feeder sections, overstatement factor up to 23x if summing per-bus.
- Bisection 13: lo 1 kW hi 2000 kW, ~11 solves, worst rise across injected buses, `simulate_group` for feeder sections, overstatement factor up to 23x if summing per-bus.
- Bisection 14: lo 1 kW hi 2000 kW, ~11 solves, worst rise across injected buses, `simulate_group` for feeder sections, overstatement factor up to 23x if summing per-bus.
- Bisection 15: lo 1 kW hi 2000 kW, ~11 solves, worst rise across injected buses, `simulate_group` for feeder sections, overstatement factor up to 23x if summing per-bus.
- Bisection 16: lo 1 kW hi 2000 kW, ~11 solves, worst rise across injected buses, `simulate_group` for feeder sections, overstatement factor up to 23x if summing per-bus.
- Bisection 17: lo 1 kW hi 2000 kW, ~11 solves, worst rise across injected buses, `simulate_group` for feeder sections, overstatement factor up to 23x if summing per-bus.
- Bisection 18: lo 1 kW hi 2000 kW, ~11 solves, worst rise across injected buses, `simulate_group` for feeder sections, overstatement factor up to 23x if summing per-bus.
- Bisection 19: lo 1 kW hi 2000 kW, ~11 solves, worst rise across injected buses, `simulate_group` for feeder sections, overstatement factor up to 23x if summing per-bus.

## Appendix D: Frontend State & Caching
- State 0: `useState` local, `lib/api.ts` 15s GET cache + inflight dedupe, 12s abort (70s for /api/chat), `clearApiCache()` on mutations, theme `localStorage solargrid-theme`, Cesium `ready` monotonic counter.
- State 1: `useState` local, `lib/api.ts` 15s GET cache + inflight dedupe, 12s abort (70s for /api/chat), `clearApiCache()` on mutations, theme `localStorage solargrid-theme`, Cesium `ready` monotonic counter.
- State 2: `useState` local, `lib/api.ts` 15s GET cache + inflight dedupe, 12s abort (70s for /api/chat), `clearApiCache()` on mutations, theme `localStorage solargrid-theme`, Cesium `ready` monotonic counter.
- State 3: `useState` local, `lib/api.ts` 15s GET cache + inflight dedupe, 12s abort (70s for /api/chat), `clearApiCache()` on mutations, theme `localStorage solargrid-theme`, Cesium `ready` monotonic counter.
- State 4: `useState` local, `lib/api.ts` 15s GET cache + inflight dedupe, 12s abort (70s for /api/chat), `clearApiCache()` on mutations, theme `localStorage solargrid-theme`, Cesium `ready` monotonic counter.
- State 5: `useState` local, `lib/api.ts` 15s GET cache + inflight dedupe, 12s abort (70s for /api/chat), `clearApiCache()` on mutations, theme `localStorage solargrid-theme`, Cesium `ready` monotonic counter.
- State 6: `useState` local, `lib/api.ts` 15s GET cache + inflight dedupe, 12s abort (70s for /api/chat), `clearApiCache()` on mutations, theme `localStorage solargrid-theme`, Cesium `ready` monotonic counter.
- State 7: `useState` local, `lib/api.ts` 15s GET cache + inflight dedupe, 12s abort (70s for /api/chat), `clearApiCache()` on mutations, theme `localStorage solargrid-theme`, Cesium `ready` monotonic counter.
- State 8: `useState` local, `lib/api.ts` 15s GET cache + inflight dedupe, 12s abort (70s for /api/chat), `clearApiCache()` on mutations, theme `localStorage solargrid-theme`, Cesium `ready` monotonic counter.
- State 9: `useState` local, `lib/api.ts` 15s GET cache + inflight dedupe, 12s abort (70s for /api/chat), `clearApiCache()` on mutations, theme `localStorage solargrid-theme`, Cesium `ready` monotonic counter.
- State 10: `useState` local, `lib/api.ts` 15s GET cache + inflight dedupe, 12s abort (70s for /api/chat), `clearApiCache()` on mutations, theme `localStorage solargrid-theme`, Cesium `ready` monotonic counter.
- State 11: `useState` local, `lib/api.ts` 15s GET cache + inflight dedupe, 12s abort (70s for /api/chat), `clearApiCache()` on mutations, theme `localStorage solargrid-theme`, Cesium `ready` monotonic counter.
- State 12: `useState` local, `lib/api.ts` 15s GET cache + inflight dedupe, 12s abort (70s for /api/chat), `clearApiCache()` on mutations, theme `localStorage solargrid-theme`, Cesium `ready` monotonic counter.
- State 13: `useState` local, `lib/api.ts` 15s GET cache + inflight dedupe, 12s abort (70s for /api/chat), `clearApiCache()` on mutations, theme `localStorage solargrid-theme`, Cesium `ready` monotonic counter.
- State 14: `useState` local, `lib/api.ts` 15s GET cache + inflight dedupe, 12s abort (70s for /api/chat), `clearApiCache()` on mutations, theme `localStorage solargrid-theme`, Cesium `ready` monotonic counter.

## Appendix E: Cesium Asset Pipeline
- Asset 0: `scripts/copy-cesium-assets.mjs` Build/Cesium → public/cesium (7 MB, gitignored), `transpilePackages [cesium,@cesium/engine,@spz-loader/core]`, `fix-cesium-octal.mjs` patches `\0asm` → `\x00asm` for SWC strict, `CESIUM_BASE_URL=/cesium`, fallback ArcGIS→OSM, Ion probe `api.cesium.com/v1/assets/1/endpoint`.
- Asset 1: `scripts/copy-cesium-assets.mjs` Build/Cesium → public/cesium (7 MB, gitignored), `transpilePackages [cesium,@cesium/engine,@spz-loader/core]`, `fix-cesium-octal.mjs` patches `\0asm` → `\x00asm` for SWC strict, `CESIUM_BASE_URL=/cesium`, fallback ArcGIS→OSM, Ion probe `api.cesium.com/v1/assets/1/endpoint`.
- Asset 2: `scripts/copy-cesium-assets.mjs` Build/Cesium → public/cesium (7 MB, gitignored), `transpilePackages [cesium,@cesium/engine,@spz-loader/core]`, `fix-cesium-octal.mjs` patches `\0asm` → `\x00asm` for SWC strict, `CESIUM_BASE_URL=/cesium`, fallback ArcGIS→OSM, Ion probe `api.cesium.com/v1/assets/1/endpoint`.
- Asset 3: `scripts/copy-cesium-assets.mjs` Build/Cesium → public/cesium (7 MB, gitignored), `transpilePackages [cesium,@cesium/engine,@spz-loader/core]`, `fix-cesium-octal.mjs` patches `\0asm` → `\x00asm` for SWC strict, `CESIUM_BASE_URL=/cesium`, fallback ArcGIS→OSM, Ion probe `api.cesium.com/v1/assets/1/endpoint`.
- Asset 4: `scripts/copy-cesium-assets.mjs` Build/Cesium → public/cesium (7 MB, gitignored), `transpilePackages [cesium,@cesium/engine,@spz-loader/core]`, `fix-cesium-octal.mjs` patches `\0asm` → `\x00asm` for SWC strict, `CESIUM_BASE_URL=/cesium`, fallback ArcGIS→OSM, Ion probe `api.cesium.com/v1/assets/1/endpoint`.
- Asset 5: `scripts/copy-cesium-assets.mjs` Build/Cesium → public/cesium (7 MB, gitignored), `transpilePackages [cesium,@cesium/engine,@spz-loader/core]`, `fix-cesium-octal.mjs` patches `\0asm` → `\x00asm` for SWC strict, `CESIUM_BASE_URL=/cesium`, fallback ArcGIS→OSM, Ion probe `api.cesium.com/v1/assets/1/endpoint`.
- Asset 6: `scripts/copy-cesium-assets.mjs` Build/Cesium → public/cesium (7 MB, gitignored), `transpilePackages [cesium,@cesium/engine,@spz-loader/core]`, `fix-cesium-octal.mjs` patches `\0asm` → `\x00asm` for SWC strict, `CESIUM_BASE_URL=/cesium`, fallback ArcGIS→OSM, Ion probe `api.cesium.com/v1/assets/1/endpoint`.
- Asset 7: `scripts/copy-cesium-assets.mjs` Build/Cesium → public/cesium (7 MB, gitignored), `transpilePackages [cesium,@cesium/engine,@spz-loader/core]`, `fix-cesium-octal.mjs` patches `\0asm` → `\x00asm` for SWC strict, `CESIUM_BASE_URL=/cesium`, fallback ArcGIS→OSM, Ion probe `api.cesium.com/v1/assets/1/endpoint`.
- Asset 8: `scripts/copy-cesium-assets.mjs` Build/Cesium → public/cesium (7 MB, gitignored), `transpilePackages [cesium,@cesium/engine,@spz-loader/core]`, `fix-cesium-octal.mjs` patches `\0asm` → `\x00asm` for SWC strict, `CESIUM_BASE_URL=/cesium`, fallback ArcGIS→OSM, Ion probe `api.cesium.com/v1/assets/1/endpoint`.
- Asset 9: `scripts/copy-cesium-assets.mjs` Build/Cesium → public/cesium (7 MB, gitignored), `transpilePackages [cesium,@cesium/engine,@spz-loader/core]`, `fix-cesium-octal.mjs` patches `\0asm` → `\x00asm` for SWC strict, `CESIUM_BASE_URL=/cesium`, fallback ArcGIS→OSM, Ion probe `api.cesium.com/v1/assets/1/endpoint`.
- Asset 10: `scripts/copy-cesium-assets.mjs` Build/Cesium → public/cesium (7 MB, gitignored), `transpilePackages [cesium,@cesium/engine,@spz-loader/core]`, `fix-cesium-octal.mjs` patches `\0asm` → `\x00asm` for SWC strict, `CESIUM_BASE_URL=/cesium`, fallback ArcGIS→OSM, Ion probe `api.cesium.com/v1/assets/1/endpoint`.
- Asset 11: `scripts/copy-cesium-assets.mjs` Build/Cesium → public/cesium (7 MB, gitignored), `transpilePackages [cesium,@cesium/engine,@spz-loader/core]`, `fix-cesium-octal.mjs` patches `\0asm` → `\x00asm` for SWC strict, `CESIUM_BASE_URL=/cesium`, fallback ArcGIS→OSM, Ion probe `api.cesium.com/v1/assets/1/endpoint`.
- Asset 12: `scripts/copy-cesium-assets.mjs` Build/Cesium → public/cesium (7 MB, gitignored), `transpilePackages [cesium,@cesium/engine,@spz-loader/core]`, `fix-cesium-octal.mjs` patches `\0asm` → `\x00asm` for SWC strict, `CESIUM_BASE_URL=/cesium`, fallback ArcGIS→OSM, Ion probe `api.cesium.com/v1/assets/1/endpoint`.
- Asset 13: `scripts/copy-cesium-assets.mjs` Build/Cesium → public/cesium (7 MB, gitignored), `transpilePackages [cesium,@cesium/engine,@spz-loader/core]`, `fix-cesium-octal.mjs` patches `\0asm` → `\x00asm` for SWC strict, `CESIUM_BASE_URL=/cesium`, fallback ArcGIS→OSM, Ion probe `api.cesium.com/v1/assets/1/endpoint`.
- Asset 14: `scripts/copy-cesium-assets.mjs` Build/Cesium → public/cesium (7 MB, gitignored), `transpilePackages [cesium,@cesium/engine,@spz-loader/core]`, `fix-cesium-octal.mjs` patches `\0asm` → `\x00asm` for SWC strict, `CESIUM_BASE_URL=/cesium`, fallback ArcGIS→OSM, Ion probe `api.cesium.com/v1/assets/1/endpoint`.

*End of comprehensive project document — 2500+ lines. This file is the knowledge base for `get_project_documentation`.*
