"use client";

import { supabase } from "@/lib/supabase";
import type {
  ApplicationTimeline,
  Assessment,
  BuildingFootprint,
  CFAEstimate,
  Bus,
  CitizenMapData,
  ConnectionPoint,
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

const _cache = new Map<string, { data: unknown; expiry: number }>();
const _inflight = new Map<string, Promise<unknown>>();
const CACHE_TTL_MS = 15_000;
function cacheKey(path: string, init: RequestInit): string | null {
  if ((init.method ?? "GET") !== "GET") return null;
  if (path.includes("/timeline") || path.includes("/summary")) return null;
  return `${path}`;
}
async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const key = cacheKey(path, init);
  if (key) {
    const hit = _cache.get(key);
    if (hit && Date.now() < hit.expiry) return hit.data as T;
    const inflight = _inflight.get(key);
    if (inflight) return (await inflight) as T;
  }
  const doFetch = async (): Promise<T> => {
  let res: Response;
  try {
    const controller = new AbortController();
    const isChat = path.includes("/api/chat");
    const timeoutMs = isChat ? 70_000 : 30_000;
    const timeout = setTimeout(() => controller.abort(), timeoutMs);
    res = await fetch(`${BASE}${path}`, {
      ...init,
      signal: init.signal ?? controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(await authHeader()),
        ...(init.headers ?? {}),
      },
      cache: "no-store",
    });
    clearTimeout(timeout);
  } catch (e) {
    if ((e as Error).name === "AbortError") throw new ApiError(0, "Backend timed out");
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

  const data = (await res.json()) as T;
  if (key) {
    _cache.set(key, { data, expiry: Date.now() + CACHE_TTL_MS });
    _inflight.delete(key);
  } else {
    // Invalidate GET caches that could be stale after a mutation
    if ((init.method ?? "GET") !== "GET") {
      for (const k of Array.from(_cache.keys())) {
        if (k.startsWith("/api/applications") || k.startsWith("/api/discom") || k.startsWith("/api/vendor") || k.startsWith("/api/citizen")) {
          _cache.delete(k);
        }
      }
      _inflight.clear();
    }
  }
  return data;
  };
  if (key) {
    const p = doFetch();
    _inflight.set(key, p as Promise<unknown>);
    try { return await p; } finally { _inflight.delete(key); }
  }
  return doFetch();
}
export function clearApiCache() { _cache.clear(); _inflight.clear(); }

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

  /**
   * The connection point that will screen this address.
   *
   * The form asks for a location, not a bus: which LV bus serves an address is
   * a DISCOM record and not something on an electricity bill. One rule decides
   * it, on the server, for every application.
   */
  connectionPoint: (latitude: number, longitude: number) =>
    request<ConnectionPoint>(
      `/api/grid/connection-point?latitude=${latitude}&longitude=${longitude}`
    ),

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
      installation_return?: { notes: string; returned_at: string | null } | null;
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

  /** Houses/locality for one bus — deterministic synthetic offsets, ML untouched. */
  busHouses: (busId: string) =>
    request<{
      pv_bus: string;
      locality: Record<string, unknown>;
      bus_position: { latitude: number; longitude: number; distance_km: number };
      houses: { house_id: string; pv_bus: string; latitude: number; longitude: number }[];
      path: string[];
      provisional: boolean;
    }>(`/api/grid/buses/${busId}/houses`),

  /** All 71 bus localities with house counts. */
  localities: () =>
    request<{ buses: Record<string, unknown>[]; count: number }>("/api/grid/localities"),

  /** SolarGrid AI Grid Assistant — NVIDIA NIM via FastAPI. */
  chat: (payload: {
    message: string;
    context?: {
      page?: string;
      application_id?: string | null;
      pv_bus?: string | null;
      selected_asset_id?: string | null;
      selected_asset_type?: string | null;
      assessment_id?: string | null;
    };
    history?: { role: string; content: string }[];
  }) =>
    request<{
      reply: string;
      actions: { type: string; payload: Record<string, unknown> }[];
      context_used?: Record<string, unknown> | null;
    }>("/api/chat", { method: "POST", body: JSON.stringify(payload) }),

  chatHealth: () => request<{ nvidia_configured: boolean; nvidia_model: string; status: string }>("/api/chat/health"),
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

  /** Return submitted work for correction with a reason. */
  returnInstallation: (id: string, reason: string) =>
    request<{ installation: Installation }>(`/api/discom/installations/${id}/return`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }),

  /** Short-lived link to a completion photo, for review. */
  installationPhotoUrl: (documentId: string) =>
    request<{ url: string }>(`/api/discom/documents/${documentId}/url`),

  /** Vendors breaching the quality-flag rule, with evidence. */
  ratingFlags: () =>
    request<{ flags: { vendor: { id: string; business_name: string; status: string; rating: number | null }; flag: Record<string, unknown> }[]; count: number }>(
      "/api/discom/vendors/rating-flags"
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
  opportunities: () => request<SolarApplication[]>("/api/vendor/opportunities"),
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
  claimOpportunity: (applicationId: string) =>
    request<{ appointment: Lead; installation: Installation }>(`/api/vendor/opportunities/${applicationId}/claim`, { method: "POST" }),
  vendorApplications: () => request<Record<string, unknown>[]>("/api/vendor/applications"),
  vendorApplicationDetail: (id: string) => request<Record<string, unknown>>(`/api/vendor/applications/${id}`),
  /** VERIFIED is refused server-side — only a DISCOM reviewer can set it. */
  updateInstallation: (id: string, status: InstallationStatusValue, kw?: number) =>
    request<Installation>(`/api/vendor/installations/${id}/status`, {
      method: "POST",
      body: JSON.stringify({ status, installed_capacity_kw: kw ?? null }),
    }),
  /** Save the completion report draft (equipment, dates, checklist, photos). */
  saveInstallationReport: (id: string, body: Record<string, unknown>) =>
    request<Installation>(`/api/vendor/installations/${id}/report`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  /** Validate the COMPLETED report and submit it for DISCOM verification. */
  submitInstallation: (id: string) =>
    request<Installation>(`/api/vendor/installations/${id}/submit`, { method: "POST" }),
  /** Short-lived link to one of this vendor's own documents. */
  documentUrl: (documentId: string) =>
    request<{ url: string }>(`/api/vendor/documents/${documentId}/url`),

  /** This vendor's own average, count and recent feedback. */
  myRatings: () =>
    request<{ average: number | null; count: number; reviews: { rating: number; tags: string[]; comment: string | null; created_at: string }[] }>(
      "/api/vendor/ratings"
    ),

  /** Upload a site photo/document for the completion report. */
  uploadInstallationPhoto: async (file: File, documentType: string, notes?: string) => {
    const { supabase } = await import("@/lib/supabase");
    const { data } = await supabase.auth.getSession();
    const token = data.session?.access_token;
    const form = new FormData();
    form.append("document_type", documentType);
    form.append("file", file);
    if (notes) form.append("notes", notes);
    const res = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"}/api/vendor/documents/upload`,
      { method: "POST", headers: token ? { Authorization: `Bearer ${token}` } : {}, body: form }
    );
    if (!res.ok) {
      let detail = `Upload failed (${res.status})`;
      try {
        const body = await res.json();
        if (typeof body.detail === "string") detail = body.detail;
      } catch { /* no JSON body */ }
      throw new ApiError(res.status, detail);
    }
    return (await res.json()) as { document: { id: string; file_name: string | null } };
  },
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
  reviewEligibility: (applicationId: string, vendorId: string) =>
    request<{ eligible: boolean; reason: string }>(
      `/api/applications/${applicationId}/reviews/eligibility?vendor_id=${vendorId}`
    ),
  submitReview: (applicationId: string, body: { vendor_id: string; rating: number; tags: string[]; comment?: string }) =>
    request<Record<string, unknown>>(`/api/applications/${applicationId}/reviews`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  vendorReviewSummary: (vendorId: string) =>
    request<{ average: number | null; count: number; tag_histogram: Record<string, number>; reviews: Record<string, unknown>[] }>(
      `/api/vendors/${vendorId}/reviews`
    ),
};
