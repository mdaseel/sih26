/**
 * Types mirroring the backend response models.
 *
 * Every electrical field here is produced by the power flow on the server.
 * The frontend renders these values and never computes, estimates, or
 * interpolates one of its own.
 */

export type RiskLevel = "SAFE" | "CAUTION" | "CONSTRAINED";

export type ConstraintKind =
  | "none"
  | "voltage"
  | "voltage_rise"
  | "line_loading"
  | "transformer_loading"
  | "caution";

export type ApplicationStatus =
  | "DRAFT"
  | "SUBMITTED"
  | "ASSESSING"
  | "ASSESSED"
  | "UNDER_DISCOM_REVIEW"
  | "APPROVED"
  | "ENGINEERING_REVIEW"
  | "REJECTED"
  | "VENDOR_SELECTED"
  | "INSTALLING"
  | "INSTALLED"
  | "VERIFIED"
  | "CANCELLED";

export interface MLPrediction {
  prediction: RiskLevel;
  safe_probability: number;
  caution_probability: number;
  constrained_probability: number;
  model_file: string;
  model_version: string;
  feature_count: number;
  /**
   * The 18 inputs the forest was given. Pre-simulation only: bus identity,
   * declared capacities and the network constants for that connection point.
   * The power-flow results are deliberately not among them.
   */
  features_used: Record<string, number | string>;
  /** How many trees voted. Read from the fitted model, not assumed. */
  tree_count: number | null;
}

export interface EngineeringVerdict {
  engineering_risk: RiskLevel;
  constraint_type: ConstraintKind;
  constraint_reason: string;
  thresholds_snapshot: Record<string, number>;
}

export interface EngineeringMetrics {
  pv_bus: string;
  existing_pv_kw: number;
  new_pv_kw: number;
  total_pv_kw: number;

  base_voltage_pu: number;
  pv_voltage_pu: number;
  voltage_rise_pu: number;
  feeder_min_voltage_pu: number;
  feeder_max_voltage_pu: number;
  min_voltage_bus: string;
  max_voltage_bus: string;

  base_max_line_loading_pct: number;
  max_line_loading_pct: number;
  worst_line: string;
  base_max_transformer_loading_pct: number;
  max_transformer_loading_pct: number;
  worst_transformer: string;

  base_total_p_kw: number;
  pv_total_p_kw: number;
  power_loss_kw: number;
  delta_losses_kw: number;
  reverse_power_flow: boolean;
  reverse_reason: string;
  solar_penetration_pct: number;

  converged: boolean;
  engine: string;
  engine_version: string;
  network_file: string;
  runtime_ms: number;
}

/**
 * Spare capacity at the connection point.
 *
 * The verdict says whether this system may connect; this says by how much. On
 * this feeder the limits run from 50 kW to 538 kW depending on the bus, so a
 * SAFE verdict on its own withholds the number that actually differs between
 * one roof and another.
 *
 * Null on the assessment when the backend could not compute it. Absent is not
 * the same as ample and the UI must not draw it as such.
 */
export interface Headroom {
  bus_id: string;
  hosting_capacity_kw: number;
  existing_pv_kw: number;
  requested_new_pv_kw: number;
  headroom_after_kw: number;
  utilisation_pct: number | null;
  limiting_constraint: string;
  limiting_reason: string;
  saturated: boolean;
  method: string;
  /**
   * "assessment" when computed with the verdict shown; "current" when
   * recomputed now for a stored result, and so describing today's network.
   */
  as_of: "assessment" | "current";
}

export interface Assessment {
  application_id: string | null;
  simulation_id: string | null;
  assessment_id: string | null;
  ml: MLPrediction;
  engineering: EngineeringVerdict;
  metrics: EngineeringMetrics;
  headroom: Headroom | null;
  ml_agrees_with_engineering: boolean;
  authority: string;
  data_class: string;
  disclaimer: string;
  persisted: boolean;
}

export interface BuildingFootprint {
  osm_id: string;
  footprint: [number, number][];
  height_m: number;
  levels: number | null;
  height_source: "height" | "levels" | "assumed" | string;
  name: string | null;
  building_type: string | null;
  is_site?: boolean;
  area_sqm: number;
}

export interface SolarApplication {
  id: string;
  application_number: string;
  applicant_id: string;
  applicant_name: string;
  contact_phone: string | null;
  address_line: string | null;
  district: string | null;
  state: string | null;
  pincode: string | null;
  latitude: number | null;
  longitude: number | null;
  consumer_number: string | null;
  connection_type: string | null;
  /** Derived by the backend from the connection point — never asked of the applicant. */
  sanctioned_load_kw: number | null;
  monthly_consumption_kwh: number | null;
  roof_area_sqm: number | null;
  roof_type: string | null;
  shading_level: string | null;
  pv_bus: string;
  existing_pv_kw: number;
  new_pv_kw: number;
  total_pv_kw: number;
  status: ApplicationStatus;
  solar_placement?: Record<string, unknown> | null;
  created_at: string;
}

/**
 * The connection point resolved for an address, with the grid data attached.
 *
 * `provisional` is not decoration. The feeder is a synthetic research network
 * whose buses were given map coordinates at an arbitrary anchor, so the
 * assignment is a real computation over a layout that is not where any of this
 * physically is. The DISCOM confirms the actual connection point.
 */
export interface ConnectionPoint {
  pv_bus: string;
  assignment_method: "NEAREST_MAPPED_BUS" | "FALLBACK_FIRST_ELIGIBLE";
  /** Distance from the applicant's coordinates to the assigned bus, km. */
  separation_km: number | null;
  provisional: boolean;
  note: string;

  voltage_level_kv: number;
  voltage_level_label: string | null;
  phase_configuration: string | null;
  transformer: string;
  transformer_sn_kva: number;
  feeder_section: string;
  connected_load_kw: number;
  base_voltage_pu: number;
  feeder_distance_km: number;
  upstream_r_ohm: number;
  upstream_x_ohm: number;
  upstream_z_ohm: number;
  data_source: string;
}

export interface Bus {
  bus_id: string;
  vn_kv: number;
  existing_load_kw: number;
  transformer_association: string;
  feeder_section: string;
  transformer_sn_kva: number;
  base_voltage_pu: number;
  feeder_distance_km: number;
  upstream_r_ohm: number;
  upstream_x_ohm: number;
  upstream_z_ohm: number;
  phase_configuration: string | null;
  voltage_level_label: string | null;
}

export interface GridSummary {
  feeder_id: string;
  network: {
    network_file: string;
    engine: string;
    engine_version: string;
    buses: number;
    lines: number;
    transformers: number;
    loads: number;
    regulator_handling: string;
  };
  eligible_bus_count: number;
  thresholds: Record<string, number>;
  threshold_source: string;
  data_class: string;
  provenance: string;
}

// ---------------------------------------------------------------
//  Digital twin (Phase 4)
// ---------------------------------------------------------------

export interface TwinNode {
  id: string;
  type: "SUBSTATION" | "BUS" | "TRANSFORMER" | "HOUSE";
  label: string;
  x: number;
  y: number;
  vn_kv: number | null;
  sn_kva: number | null;
  hops_from_source: number;
  pv_eligible: boolean;
  existing_load_kw: number | null;
  attributes: Record<string, unknown>;
}

export interface TwinEdge {
  id: string;
  source: string;
  target: string;
  type: "LINE" | "TRANSFORMER" | "SWITCH" | "SERVICE";
  label: string;
  length_km: number | null;
}

export interface TwinTopology {
  nodes: TwinNode[];
  edges: TwinEdge[];
  path: string[];
  serving_transformer: {
    index: number;
    name: string;
    sn_kva: number;
    hv_bus: string;
    lv_bus: string;
  } | null;
  source_bus: string;
  layout_source: string;
}

export interface BusDelta {
  before_pu: number;
  after_pu: number;
  delta_pu: number;
}

export interface LineDelta {
  name: string;
  before_pct: number;
  after_pct: number;
  p_before_kw: number;
  p_after_kw: number;
  direction_before: "FORWARD" | "REVERSE";
  direction_after: "FORWARD" | "REVERSE";
  reversed_by_pv: boolean;
}

export interface TransformerDelta extends LineDelta {
  sn_kva: number;
}

export interface EnergyBalance {
  grid_supply_before_kw: number;
  grid_supply_after_kw: number;
  solar_generation_kw: number;
  local_consumption_kw: number;
  self_consumed_kw: number;
  local_export_kw: number;
  feeder_load_kw: number;
  note: string;
}

export interface TwinElements {
  path: string[];
  buses: Record<string, BusDelta>;
  lines: Record<string, LineDelta>;
  transformers: Record<string, TransformerDelta>;
  energy_balance: EnergyBalance;
}

export interface TwinResponse {
  assessment: Assessment;
  topology: TwinTopology;
  elements: TwinElements;
}

// ---------------------------------------------------------------
//  GIS map (Phase 5)
// ---------------------------------------------------------------

export type MapLayerId =
  | "risk"
  | "voltage"
  | "transformer_loading"
  | "line_loading"
  | "solar_penetration"
  | "hosting_capacity";

export interface MapAsset {
  asset_type: "SUBSTATION" | "FEEDER" | "TRANSFORMER" | "BUS" | "LINE" | "CUSTOMER_POINT";
  asset_code: string;
  name: string | null;
  vn_kv: number | null;
  sn_kva: number | null;
  transformer_association: string | null;
  feeder_section: string | null;
  existing_load_kw: number | null;
  base_voltage_pu: number | null;
  pv_eligible: boolean;
  latitude: number | null;
  longitude: number | null;
  geometry_source: string;
  parent_asset_code: string | null;
  attributes: Record<string, unknown>;
}

export interface MapApplication {
  id: string;
  application_number: string;
  applicant_name: string;
  pv_bus: string;
  existing_pv_kw: number;
  new_pv_kw: number;
  total_pv_kw: number;
  status: ApplicationStatus;
  latitude: number;
  longitude: number;
  engineering_risk: RiskLevel | null;
  ml_prediction: RiskLevel | null;
  constraint_type: string | null;
  constraint_reason: string | null;
  pv_voltage_pu: number | null;
  voltage_rise_pu: number | null;
  max_transformer_loading_pct: number | null;
  max_line_loading_pct: number | null;
  reverse_power_flow: boolean | null;
  solar_penetration_pct: number | null;
}

export interface MapData {
  assets: MapAsset[];
  applications: MapApplication[];
  pending_pv_by_bus: Record<string, number>;
  thresholds: Record<string, number>;
  anchor_note: string;
  data_class: string;
  liveness: string;
}

// ---------------------------------------------------------------
//  Citizen map — installers and the way to them, not the feeder
// ---------------------------------------------------------------

export interface CitizenMapApplication {
  id: string;
  application_number: string;
  address_line: string | null;
  district: string | null;
  state: string | null;
  pincode: string | null;
  latitude: number | null;
  longitude: number | null;
  status: ApplicationStatus;
  new_pv_kw: number;
  total_pv_kw: number;
  created_at: string;
}

export interface CitizenMapVendor {
  id: string;
  business_name: string;
  representative_name: string | null;
  phone: string | null;
  email: string | null;
  address_line: string | null;
  district: string | null;
  state: string | null;
  latitude: number | null;
  longitude: number | null;
  rating: number | null;
  completed_installations: number | null;
  installation_capacity_kw: number | null;
  years_experience: number | null;
  service_areas: string[];
  verified: boolean;
  verified_at: string | null;
  /** This installer accepted one of your bookings. */
  engaged: boolean;
  /** You asked; they have not answered yet. */
  requested: boolean;
}

export interface CitizenMapRoute extends RouteDistance {
  appointment_id: string;
  application_id: string;
  application_number: string;
  vendor_id: string;
  vendor_name: string;
  appointment_status: AppointmentStatusValue;
  scheduled_at: string;
}

export interface CitizenMapData {
  applications: CitizenMapApplication[];
  located_applications: number;
  vendors: CitizenMapVendor[];
  routes: CitizenMapRoute[];
  routing: { provider: string; returns_real_routes: boolean; integration_point: string };
  distance_note: string;
  location_note: string;
}

export interface ApplicationTimeline {
  application_id: string;
  history: StatusHistoryRow[];
}

export interface HostingCapacityRow {
  bus_id: string;
  transformer_association: string | null;
  feeder_section: string | null;
  hosting_capacity_kw: number;
  limiting_constraint: string | null;
  limiting_reason: string | null;
  method: string | null;
}

// ---------------------------------------------------------------
//  DISCOM (Phase 6)
// ---------------------------------------------------------------

export interface Me {
  id: string;
  email: string | null;
  role: "CITIZEN" | "DISCOM" | "VENDOR" | "ADMIN";
  is_discom: boolean;
  full_name: string | null;
  discom_name: string | null;
}

export interface DiscomSummary {
  total_applications: number;
  pending_review: number;
  approved: number;
  rejected: number;
  by_risk: Record<"SAFE" | "CAUTION" | "CONSTRAINED" | "NOT_ASSESSED", number>;
  approved_solar_kw: number;
  pending_solar_kw: number;
  declared_existing_solar_kw: number;
  ml_engineering_disagreements: number;
  capacity_note: string;
  network: GridSummary["network"];
  data_class: string;
}

export interface DiscomApplication extends SolarApplication {
  engineering_risk: RiskLevel | null;
  ml_prediction: RiskLevel | null;
  constraint_type: string | null;
  constraint_reason: string | null;
  ml_agrees_with_engineering: boolean | null;
  assessed: boolean;
  reviewed_by: string | null;
  reviewed_at: string | null;
  review_notes: string | null;
}

export interface StoredAssessmentRow {
  id: string;
  ml_prediction: RiskLevel;
  safe_probability: number;
  caution_probability: number;
  constrained_probability: number;
  engineering_risk: RiskLevel;
  constraint_type: string;
  constraint_reason: string;
  ml_agrees_with_engineering: boolean;
  model_file: string;
  feature_count: number;
  thresholds_snapshot: Record<string, number>;
  created_at: string;
}

export interface StatusHistoryRow {
  id: string;
  from_status: ApplicationStatus | null;
  to_status: ApplicationStatus;
  note: string | null;
  created_at: string;
}

export interface DiscomApplicationDetail {
  application: DiscomApplication;
  assessment: StoredAssessmentRow | null;
  simulation: Record<string, number | string | boolean | null> | null;
  history: StatusHistoryRow[];
  bus: Bus | null;
}

export interface TransformerRow {
  name: string;
  sn_kva: number | null;
  vn_kv: number | null;
  base_loading_pct: number | null;
  loading_status: RiskLevel | null;
  connection_points: number;
  served_buses: number;
  min_hosting_capacity_kw: number | null;
  total_load_kw: number;
  pending_pv_kw: number;
  approved_pv_kw: number;
}

export interface FeederRow {
  feeder_section: string;
  connection_points: number;
  total_load_kw: number;
  hosting_capacity_kw: number;
  min_hosting_capacity_kw: number | null;
  pending_pv_kw: number;
  approved_pv_kw: number;
  remaining_capacity_kw: number;
  applications: number;
  capacity_note: string;
}

export interface DecisionResult {
  application: DiscomApplication | null;
  decision: string;
  override_of_engineering_objection: boolean;
  engineering_risk: RiskLevel | null;
  note: string;
}

// ---------------------------------------------------------------
//  What-if + hosting capacity (Phase 7)
// ---------------------------------------------------------------

export interface WhatIfPoint {
  new_pv_kw: number;
  converged: boolean;
  engineering_risk: RiskLevel | null;
  constraint_type?: string;
  constraint_reason?: string;
  ml_prediction?: RiskLevel;
  ml_constrained_probability?: number;
  metrics?: EngineeringMetrics;
  error?: string;
}

export interface HostingCapacityDetail {
  bus_id: string;
  existing_pv_kw: number;
  hosting_capacity_kw: number;
  limiting_constraint: string;
  limiting_reason: string;
  risk_at_capacity: string;
  power_flows_run: number;
  method: string;
  resolution_kw: number;
  ceiling_kw: number;
  saturated: boolean;
  notes: string[];
}

export interface WhatIfResult {
  pv_bus: string;
  existing_pv_kw: number;
  bus: Bus;
  points: WhatIfPoint[];
  hosting_capacity: HostingCapacityDetail;
  thresholds: Record<string, number>;
  note: string;
}

export interface FeederCapacityRow {
  feeder_section: string;
  connection_points: number;
  current_solar_kw: number;
  pending_solar_kw: number;
  hosting_capacity_kw: number;
  remaining_capacity_kw: number;
  utilisation_pct: number;
  limiting_constraint: string | null;
  limiting_reason: string | null;
  risk: RiskLevel;
  per_bus_kw_at_capacity: number | null;
  sum_of_per_bus_kw: number | null;
  overstatement_factor: number | null;
  method: string | null;
  distribution: string | null;
}

export interface FeederCapacityResult {
  sections: FeederCapacityRow[];
  method_note: string;
  risk_note: string;
}

// ---------------------------------------------------------------
//  Vendors (Phase 8)
// ---------------------------------------------------------------

export type VendorStatusValue =
  | "PENDING"
  | "UNDER_REVIEW"
  | "APPROVED"
  | "REJECTED"
  | "SUSPENDED";

export interface RouteDistance {
  distance_km: number;
  duration_minutes: number | null;
  method: string;
  is_route: boolean;
  note: string;
  /** [[lon, lat], ...]. A real road path when is_route, otherwise the two ends joined. */
  geometry: [number, number][] | null;
}

export interface PublicVendor {
  id: string;
  business_name: string;
  representative_name: string | null;
  verified: boolean;
  verified_at: string | null;
  email: string | null;
  phone: string | null;
  address_line: string | null;
  district: string | null;
  state: string | null;
  service_areas: string[];
  serves_this_district: boolean;
  rating: number | null;
  completed_installations: number | null;
  installation_capacity_kw: number | null;
  years_experience: number | null;
  distance: RouteDistance | null;
}

export interface VendorDiscovery {
  vendors: PublicVendor[];
  total: number;
  with_distance: number;
  routing: { provider: string; returns_real_routes: boolean; integration_point: string };
  distance_note: string;
  location_note: string;
  application_id?: string;
  customer_location_known?: boolean;
}

export interface VendorRecord {
  id: string;
  owner_id: string | null;
  business_name: string;
  representative_name: string | null;
  email: string | null;
  phone: string | null;
  district: string | null;
  state: string | null;
  service_areas: string[];
  installation_capacity_kw: number | null;
  years_experience: number | null;
  rating: number | null;
  completed_installations: number;
  status: VendorStatusValue;
  is_active: boolean;
  verified_at: string | null;
  rejection_reason: string | null;
  created_at: string;
}

export interface VendorReviewList {
  vendors: VendorRecord[];
  counts: Record<string, number>;
  visible_to_customers: number;
}

// ---------------------------------------------------------------
//  Vendor portal (Phase 9)
// ---------------------------------------------------------------

export type InstallationStatusValue =
  | "PENDING"
  | "SITE_VISIT"
  | "SCHEDULED"
  | "IN_PROGRESS"
  | "COMPLETED"
  | "VERIFICATION_PENDING"
  | "VERIFIED";

export type AppointmentStatusValue =
  | "REQUESTED"
  | "CONFIRMED"
  | "RESCHEDULED"
  | "COMPLETED"
  | "CANCELLED";

/** Only the fields a vendor is given about an engaged customer. */
export interface VendorVisibleApplication {
  id: string;
  application_number: string;
  applicant_name: string;
  contact_phone: string | null;
  address_line: string | null;
  district: string | null;
  state: string | null;
  pincode: string | null;
  latitude: number | null;
  longitude: number | null;
  pv_bus: string;
  existing_pv_kw: number;
  new_pv_kw: number;
  total_pv_kw: number;
  status: ApplicationStatus;
  roof_type: string | null;
  roof_area_sqm: number | null;
  shading_level: string | null;
  created_at: string;
}

export interface Lead {
  id: string;
  application_id: string;
  vendor_id: string;
  citizen_id: string;
  scheduled_at: string;
  duration_minutes: number;
  purpose: string;
  status: AppointmentStatusValue;
  notes: string | null;
  created_at: string;
  application: VendorVisibleApplication | null;
}

export interface Installation {
  id: string;
  application_id: string;
  vendor_id: string | null;
  status: InstallationStatusValue;
  installed_capacity_kw: number | null;
  started_at: string | null;
  completed_at: string | null;
  discom_verified: boolean;
  discom_verified_at: string | null;
  verification_notes: string | null;
  created_at: string;
  application?: VendorVisibleApplication | null;
}

export interface VendorSummary {
  vendor: {
    id: string;
    business_name: string;
    status: VendorStatusValue;
    is_active: boolean;
    visible_to_customers: boolean;
    rating: number | null;
    completed_installations: number | null;
  };
  new_leads: number;
  confirmed_appointments: number;
  installations: number;
  installations_by_status: Record<string, number>;
  awaiting_discom_verification: number;
  verified: number;
  verification_note: string;
}

export interface VendorDocument {
  id: string;
  document_type: string;
  file_path: string;
  file_name: string | null;
  is_verified: boolean;
  notes: string | null;
  created_at: string;
}

export interface DocumentType {
  code: string;
  label: string;
  required: boolean;
}

export interface VendorProfile {
  vendor: VendorRecord;
  documents: VendorDocument[];
  document_types: DocumentType[];
  visible_to_customers: boolean;
}

export interface VendorProject {
  application_id: string;
  application: VendorVisibleApplication | null;
  installation: Installation;
  appointments: Lead[];
}

// ---------------------------------------------------------------
//  PM Surya Ghar / CFA (Phase 10)
// ---------------------------------------------------------------

export interface SchemeOverview {
  scheme_code: string;
  overview: {
    title: string;
    summary: string;
    what_it_covers: string[];
    official_portal_url: string;
    not_official_portal: string;
  };
  eligibility: { code: string; label: string; detail: string }[];
  process_steps: {
    step: number;
    actor: string;
    title: string;
    detail: string;
    in_this_app: boolean;
  }[];
  cfa_rules: {
    currency: string;
    slabs: { up_to_kw: number; rate_per_kw: number }[];
    max_subsidy: number | null;
    max_eligible_capacity_kw: number | null;
    applies_to: string;
    verification_required: boolean;
    verification_note: string;
    verified_on: string | null;
    source_url: string | null;
  };
  official_links: { label: string; url: string; detail: string }[];
  configuration: {
    keys: string[];
    effective_from: string | null;
    verification_required: boolean;
    verification_note: string | null;
    editable_at: string;
  };
  disclaimer: string;
  not_official_portal: string;
}

export interface CFAEstimate {
  capacity_kw: number;
  eligible_capacity_kw: number;
  amount: number;
  currency: string;
  breakdown: {
    from_kw: number;
    to_kw: number;
    kw: number;
    rate_per_kw: number;
    amount: number;
  }[];
  capped: boolean;
  max_subsidy: number | null;
  indicative: boolean;
  disclaimer: string;
  not_official_portal: string;
  configuration_verified: boolean;
  verification_note: string;
  source_url: string | null;
  effective_from: string | null;
}
