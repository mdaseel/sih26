"use client";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ApiError, clearApiCache, vendorApi } from "@/lib/api";
import { supabase } from "@/lib/supabase";

type Detail = {
  application: Record<string, unknown> & { application_number:string; applicant_name:string; pv_bus:string; new_pv_kw:number; existing_pv_kw:number; total_pv_kw:number; status:string; latitude:number|null; longitude:number|null; sanctioned_load_kw:number|null; address_line:string|null; district:string|null; state:string|null; pincode:string|null; consumer_number:string|null; contact_phone:string|null; roof_type:string|null; roof_area_sqm:number|null; reviewed_by:string|null };
  installation: Record<string, unknown> | null;
  history: { from_status:string|null; to_status:string; created_at:string; note:string|null }[];
  documents: { id:string; document_type:string; file_path:string; is_verified:boolean; uploaded_by_party:string; created_at:string }[];
  vendor_documents: unknown[];
  subsidy: { amount:number; currency:string; eligible_capacity_kw:number } | null;
  discom: { full_name:string|null; discom_name:string|null; email:string|null } | null;
};

const STAGE_LABELS: Record<string,string> = {
  SUBMITTED:"Application", ASSESSED:"Feasibility", APPROVED:"DISCOM Approved", VENDOR_SELECTED:"Vendor Selected",
  INSTALLING:"Installation", INSTALLED:"Inspection", VERIFIED:"Commissioning & Subsidy"
};

export default function VendorAppDetail(){
  const { id } = useParams<{id:string}>();
  const [data, setData]=useState<Detail|null>(null);
  const [error,setError]=useState<string|null>(null);
  const [busy,setBusy]=useState(false);
  const [note,setNote]=useState("");

  async function load(){
    const { data: sess } = await supabase.auth.getSession();
    const token = sess.session?.access_token;
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL||"http://localhost:8000"}/api/vendor/applications/${id}`,{
      headers: token?{Authorization:`Bearer ${token}`}:{},
    });
    if(!res.ok){ const t=await res.text(); throw new Error(t); }
    setData(await res.json());
  }
  useEffect(()=>{ load().catch(e=>setError(e instanceof Error?e.message:"Failed")); },[id]);

  async function updateStatus(status:string){
    setBusy(true); setError(null);
    try{
      const inst = data?.installation as { id:string } | null;
      if(!inst) throw new Error("No installation yet — claim the opportunity from dashboard first");
      await vendorApi.updateInstallation(inst.id, status as never);
      clearApiCache();
      await load();
    }catch(e){ setError((e as ApiError).message || (e as Error).message); } finally{ setBusy(false); }
  }

  if(error && !data) return <div className="card"><p className="text-sm text-red-600">{error}</p></div>;
  if(!data) return <div className="h-64 rounded-2xl shimmer" />;
  const a = data.application as Detail["application"];
  const inst = data.installation as Record<string,unknown> | null;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div><h1 className="text-xl font-bold font-mono" style={{color:"rgb(var(--ink))"}}>{a.application_number as string}</h1><p className="text-sm" style={{color:"rgb(var(--ink-faint))"}}>{a.applicant_name as string} · Bus {a.pv_bus as string} · {Number(a.new_pv_kw).toFixed(1)} kWp</p></div>
        <span className="rounded-full border px-3 py-1 text-xs font-bold" style={{borderColor:"rgb(var(--line))", background:"rgb(var(--panel))"}}>{a.status as string}</span>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card space-y-3">
          <h2 className="font-bold" style={{color:"rgb(var(--ink))"}}>Customer & Site</h2>
          <div className="grid gap-3 sm:grid-cols-2 text-sm">
            <Field label="Consumer" value={a.applicant_name as string} />
            <Field label="Consumer No." value={a.consumer_number as string||"—"} />
            <Field label="Mobile" value={a.contact_phone as string||"—"} />
            <Field label="Sanctioned Load" value={`${a.sanctioned_load_kw ?? "—"} kW`} />
            <Field label="Proposed" value={`${Number(a.new_pv_kw).toFixed(1)} kWp`} />
            <Field label="Existing Solar" value={`${Number(a.existing_pv_kw).toFixed(1)} kW`} />
            <Field label="Total after" value={`${Number(a.total_pv_kw).toFixed(1)} kW`} />
            <Field label="Location" value={`${a.latitude ?? "—"}, ${a.longitude ?? "—"}`} />
          </div>
          <div className="rounded-xl border p-3 text-xs" style={{borderColor:"rgb(var(--line))", background:"rgb(var(--panel-raised))"}}>
            <div style={{color:"rgb(var(--ink-faint))"}}>Address</div><div style={{color:"rgb(var(--ink))"}}>{[a.address_line, a.district, a.state, a.pincode].filter(Boolean).join(", ")||"—"}</div>
            {a.latitude!=null && <a href={`https://www.openstreetmap.org/?mlat=${a.latitude}&mlon=${a.longitude}#map=16/${a.latitude}/${a.longitude}`} target="_blank" rel="noreferrer" className="mt-2 inline-block text-xs font-semibold" style={{color:"rgb(var(--accent-strong))"}}>Open in map →</a>}
          </div>
          <div className="rounded-xl border p-3 text-xs" style={{borderColor:"rgb(var(--line))"}}><b>DISCOM:</b> {data.discom?.discom_name || "—"} · Reviewer {data.discom?.full_name || a.reviewed_by || "—"}</div>
        </div>

        <div className="card space-y-3">
          <h2 className="font-bold" style={{color:"rgb(var(--ink))"}}>Subsidy & Capacity</h2>
          {data.subsidy ? <div className="rounded-xl border p-4" style={{borderColor:"rgb(var(--line))", background:"rgb(220 252 231)"}}><div className="text-xs" style={{color:"rgb(var(--ink-faint))"}}>Indicative CFA</div><div className="text-2xl font-bold" style={{color:"rgb(22 101 52)"}}>{data.subsidy.currency} {data.subsidy.amount.toLocaleString()} <span className="text-xs font-normal">for {data.subsidy.eligible_capacity_kw} kWp</span></div></div> : <p className="text-sm" style={{color:"rgb(var(--ink-faint))"}}>No subsidy estimate.</p>}
          <div className="rounded-xl border p-3" style={{borderColor:"rgb(var(--line))"}}><div className="text-xs font-bold" style={{color:"rgb(var(--ink))"}}>Vendor Actions</div>
            <p className="text-xs mt-1" style={{color:"rgb(var(--ink-faint))"}}>You may advance installation stages. Status syncs to citizen & DISCOM instantly.</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {["SITE_VISIT","SCHEDULED","IN_PROGRESS","COMPLETED","VERIFICATION_PENDING"].map(s=>(
                <button key={s} disabled={busy} onClick={()=>updateStatus(s)} className="rounded-full border px-3 py-1.5 text-xs font-semibold hover:scale-[1.02] active:scale-95" style={{borderColor:"rgb(var(--line))", background:"rgb(var(--panel))"}}>{s.replace(/_/g," ")}</button>
              ))}
            </div>
            {inst && <p className="mt-2 text-xs">Current installation: <b>{String((inst as {status:string}).status)}</b> { (inst as {discom_verified:boolean}).discom_verified && <span className="text-emerald-600">· DISCOM verified</span>}</p>}
            {error && <p className="mt-2 text-xs text-red-600">{error}</p>}
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="font-bold mb-3" style={{color:"rgb(var(--ink))"}}>Timeline — Registration → Commissioning</h2>
        <ol className="relative border-l pl-6" style={{borderColor:"rgb(var(--line))"}}>
          {data.history.length===0 ? <p className="text-sm" style={{color:"rgb(var(--ink-faint))"}}>No history yet.</p> : data.history.map((h,i)=>(
            <li key={i} className="mb-4">
              <span className="absolute -left-1.5 h-3 w-3 rounded-full" style={{background: h.to_status==="VERIFIED"?"rgb(34 197 94)": h.to_status==="REJECTED"?"rgb(239 68 68)":"rgb(var(--accent))"}} />
              <div className="text-sm font-semibold" style={{color:"rgb(var(--ink))"}}>{STAGE_LABELS[h.to_status] || h.to_status} <span className="text-xs font-normal" style={{color:"rgb(var(--ink-faint))"}}>· {new Date(h.created_at).toLocaleString()}</span></div>
              {h.note && <div className="text-xs" style={{color:"rgb(var(--ink-faint))"}}>{h.note}</div>}
            </li>
          ))}
        </ol>
      </div>

      <div className="card">
        <h2 className="font-bold mb-3" style={{color:"rgb(var(--ink))"}}>Documents — Consumer / Vendor / DISCOM</h2>
        {data.documents.length===0 ? <p className="text-sm" style={{color:"rgb(var(--ink-faint))"}}>No documents yet.</p> : (
          <div className="space-y-2">
            {data.documents.map((d)=>(
              <div key={d.id} className="flex items-center justify-between rounded-xl border px-4 py-3" style={{borderColor:"rgb(var(--line))"}}>
                <div><div className="text-sm font-medium" style={{color:"rgb(var(--ink))"}}>{d.document_type} <span className="ml-2 rounded-full border px-2 py-0.5 text-xs" style={{borderColor:"rgb(var(--line))"}}>{d.uploaded_by_party}</span></div><div className="text-xs" style={{color:"rgb(var(--ink-faint))"}}>{d.file_path} · {d.is_verified?"Verified":"Pending"}</div></div>
                <a href={d.file_path} target="_blank" rel="noreferrer" className="btn-ghost !py-1.5 !text-xs">View / Download</a>
              </div>
            ))}
          </div>
        )}
      </div>

      <p className="text-xs" style={{color:"rgb(var(--ink-ghost))"}}>All data live from DB. Status changes here propagate to citizen tracking and DISCOM instantly via status_history trigger + cache invalidation.</p>
    </div>
  );
}
function Field({label,value}:{label:string; value:string}){ return <div><div className="text-xs font-semibold uppercase tracking-widest" style={{color:"rgb(var(--ink-faint))"}}>{label}</div><div className="text-sm font-medium" style={{color:"rgb(var(--ink))"}}>{value}</div></div>; }
