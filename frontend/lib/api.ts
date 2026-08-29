"use client";

import { supabase } from "@/lib/supabase";
import type {
  ApplicationTimeline,
  Assessment,
  BuildingFootprint,
  CFAEstimate,
  Bus,
  CitizenMapData,
  GridSummary,
  DecisionResult,
  DiscomApplication,
  DiscomApplicationDetail,
  DiscomSummary,
  FeederCapacityResult,
  FeederRow,
  HostingCapacityRow,
  MapData,
  Me,
  SchemeOverview,
  SolarApplication,
  TransformerRow,
  TwinResponse,
  Installation,
  InstallationStatusValue,
  Lead,
  VendorDiscovery,
  VendorProfile,
  VendorProject,
  VendorReviewList,
  VendorStatusValue,
  VendorSummary,
  WhatIfResult,
} from "@/lib/types";

/**
 * Typed client for the SolarGrid backend.
 *
 * Every request carries the caller's Supabase JWT, so the backend resolves the
 * user and Row Level Security applies to the same identity. There is no
 * client-side authorization here: this module decides what to *ask for*, the
 * server decides what is *allowed*.
 */

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function authHeader(): Promise<Record<string, string>> {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(await authHeader()),
        ...(init.headers ?? {}),
      },
      cache: "no-store",
    });
  } catch {
    throw new ApiError(
      0,
      `Cannot reach the backend at ${BASE}. Start it with: uvicorn app.main:app --port 8000`
    );
  }

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") {
        detail = body.detail;
      } else if (Array.isArray(body.detail)) {
        // FastAPI validation errors
        detail = body.detail
          .map((e: { loc?: string[]; msg?: string }) =>
            `${e.loc?.slice(1).join(".") ?? "field"}: ${e.msg ?? "invalid"}`
          )
          .join("; ");
      }
    } catch {
      /* response had no JSON body */
    }
    throw new ApiError(res.status, detail);
  }

  return (await res.json()) as T;
}

export const api = {
  health: () =>
    request<{
      status: string;
      artifacts_present: boolean;
      supabase_configured: boolean;
      persistence_available: boolean;
      data_class: string;
    }>("/health"),

  gridSummary: () => request<GridSummary>("/api/grid/summary"),

  buses: () => request<Bus[]>("/api/grid/buses"),

  siteBuildings: (latitude: number, longitude: number) =>
    request<{
      buildings: BuildingFootprint[];
      available: boolean;
      note?: string;
      count?: number;
    }>(`/api/site-context?latitude=${latitude}&longitude=${longitude}`),

  /** Stateless assessment — used for the pre-submission preview. */
  assess: (payload: {
    pv_bus: string;
    existing_pv_kw: number;
    new_pv_kw: number;
  }) =>
    request<Assessment>("/api/assess", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  createApplication: (payload: Record<string, unknown>) =>
    request<SolarApplication>("/api/applications", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  listApplications: () => request<SolarApplication[]>("/api/applications"),

  getApplication: (id: string) =>
    request<{
      application: SolarApplication;
      latest_assessment: Record<string, unknown> | null;
    }>(`/api/applications/${id}`),

  /**
   * Every status the application has actually held, oldest first.
   *
   * Written by a database trigger on each transition, so this is a record of
   * what happened. A stage with no row here is a stage that has not been
   * reached — the tracker must show it as pending, never as done.
   */
  applicationTimeline: (id: string) =>
    request<ApplicationTimeline>(`/api/applications/${id}/timeline`),

  /** Reads the stored assessment. Does not re-simulate. */
  storedAssessment: (id: string) =>
    request<Assessment>(`/api/applications/${id}/assessment`),

  /** Runs the pipeline again and records a new result. */
  assessApplication: (id: string) =>
    request<Assessment>(`/api/applications/${id}/assess`, { method: "POST" }),

  /** Everything the geographic map draws. RLS scopes the application pins. */
  map: () => request<MapData>("/api/map"),

  /**
   * The citizen's own map: their sites, verified installers, and the route to
   * any installer who has accepted a booking. No feeder assets — those belong
   * to the DISCOM view.
   */
  citizenMap: () => request<CitizenMapData>("/api/citizen/map"),

  /** Precomputed hosting capacity for every eligible bus. */
  hostingCapacity: () =>
    request<{ buses: HostingCapacityRow[]; count: number }>("/api/grid/hosting-capacity"),

  /** Approved, active vendors only. Unvetted vendors are not addressable here. */
  vendors: (district?: string) =>
    request<VendorDiscovery>(`/api/vendors${district ? `?district=${encodeURIComponent(district)}` : ""}`),

  /** Vendors near one application, nearest first where a distance exists. */
  vendorsForApplication: (id: string) =>
    request<VendorDiscovery>(`/api/applications/${id}/vendors`),

  /** PM Surya Ghar information, entirely from configuration. */
  scheme: () => request<SchemeOverview>("/api/scheme"),

  /** Indicative CFA for a capacity. Not a sanction or a quotation. */
  cfaEstimate: (capacityKw: number) =>
    request<CFAEstimate>(`/api/scheme/estimate?capacity_kw=${capacityKw}`),

  /** Digital twin: the same assessment plus per-element before/after. */
  twin: (payload: { pv_bus: string; existing_pv_kw: number; new_pv_kw: number }) =>
    request<TwinResponse>("/api/twin", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};

/** DISCOM routes. Every one of these is refused server-side for a citizen. */
export const discomApi = {
  me: () => request<Me>("/api/me"),
  summary: () => request<DiscomSummary>("/api/discom/summary"),
  applications: () => request<DiscomApplication[]>("/api/discom/applications"),
  application: (id: string) =>
    request<DiscomApplicationDetail>(`/api/discom/applications/${id}`),
  decide: (id: string, decision: string, notes?: string) =>
    request<DecisionResult>(`/api/discom/applications/${id}/decision`, {
      method: "POST",
      body: JSON.stringify({ decision, notes: notes ?? null }),
    }),
  transformers: () => request<TransformerRow[]>("/api/discom/transformers"),
  feeders: () => request<FeederRow[]>("/api/discom/feeders"),

  /** Capacity sweep at one bus. Every point is a real power-flow solve. */
  whatIf: (pv_bus: string, existing_pv_kw: number, capacities_kw?: number[]) =>
    request<WhatIfResult>("/api/discom/what-if", {
      method: "POST",
      body: JSON.stringify({ pv_bus, existing_pv_kw, capacities_kw }),
    }),

  /** Per-section capacity, measured with all connections energised together. */
  feederCapacity: () =>
    request<FeederCapacityResult>("/api/discom/hosting-capacity/feeders"),

  /** Installations across all vendors. */
  installations: () => request<Installation[]>("/api/discom/installations"),

  /** The only route that can set VERIFIED. */
  verifyInstallation: (id: string, notes?: string) =>
    request<{ installation: Installation; verified_by: string }>(
      `/api/discom/installations/${id}/verify`,
      { method: "POST", body: JSON.stringify({ notes: notes ?? null }) }
    ),

  /** Every vendor, whatever their status, for the review queue. */
  vendors: () => request<VendorReviewList>("/api/discom/vendors"),

  reviewVendor: (id: string, status: VendorStatusValue, reason?: string) =>
    request<{ status: string; visible_to_customers: boolean }>(
      `/api/discom/vendors/${id}/review`,
      { method: "POST", body: JSON.stringify({ status, reason: reason ?? null }) }
    ),
};

/** Vendor portal. Every route resolves the caller's vendor profile server-side. */
export const vendorApi = {
  summary: () => request<VendorSummary>("/api/vendor/summary"),
  leads: () => request<Lead[]>("/api/vendor/leads"),
  respondToLead: (appointmentId: string, accept: boolean, note?: string) =>
    request<{ accepted: boolean; installation: Installation | null }>(
      `/api/vendor/leads/${appointmentId}/respond`,
      { method: "POST", body: JSON.stringify({ accept, note: note ?? null }) }
    ),
  appointments: () => request<Lead[]>("/api/vendor/appointments"),
  updateAppointment: (id: string, body: Record<string, unknown>) =>
    request<Lead>(`/api/vendor/appointments/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  installations: () => request<Installation[]>("/api/vendor/installations"),
  /** VERIFIED is refused server-side — only a DISCOM reviewer can set it. */
  updateInstallation: (id: string, status: InstallationStatusValue, kw?: number) =>
    request<Installation>(`/api/vendor/installations/${id}/status`, {
      method: "POST",
      body: JSON.stringify({ status, installed_capacity_kw: kw ?? null }),
    }),
  projects: () => request<VendorProject[]>("/api/vendor/projects"),
  profile: () => request<VendorProfile>("/api/vendor/profile"),
  updateProfile: (body: Record<string, unknown>) =>
    request<Record<string, unknown>>("/api/vendor/profile", {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  addDocument: (body: Record<string, unknown>) =>
    request<Record<string, unknown>>("/api/vendor/documents", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  register: (body: Record<string, unknown>) =>
    request<{ vendor: Record<string, unknown>; note: string }>("/api/vendors/register", {
      method: "POST",
      body: JSON.stringify(body),
    }),
};

/** Citizen engages an installer. */
export const engagementApi = {
  selectVendor: (applicationId: string, vendorId: string, scheduledAt: string, notes?: string) =>
    request<{ appointment: Lead }>(`/api/applications/${applicationId}/select-vendor`, {
      method: "POST",
      body: JSON.stringify({
        vendor_id: vendorId,
        scheduled_at: scheduledAt,
        notes: notes ?? null,
      }),
    }),
  appointments: (applicationId: string) =>
    request<Lead[]>(`/api/applications/${applicationId}/appointments`),
};
