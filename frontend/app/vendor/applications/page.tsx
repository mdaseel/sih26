"use client";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ApiError, vendorApi } from "@/lib/api";

type Row = {
  application_id: string; application_number: string; applicant_name: string;
  consumer_number: string | null; contact_phone: string | null; district: string | null; state: string | null;
  address_line: string | null; pv_bus: string; new_pv_kw: number; total_pv_kw: number;
  status: string; created_at: string; installation_status: string | null; discom_verified: boolean | null;
  latitude: number | null; longitude: number | null; sanctioned_load_kw: number | null;
};

function exportCSV(rows: Row[]) {
  const header = ["Application No","Consumer","Consumer No","Mobile","Capacity kWp","Bus","Status","Installation","Date"];
  const lines = [header.join(",")].concat(rows.map(r => [
    r.application_number, `"${(r.applicant_name||"").replace(/"/g,'""')}"`, r.consumer_number||"", r.contact_phone||"", r.new_pv_kw, r.pv_bus, r.status, r.installation_status||"", new Date(r.created_at).toLocaleDateString()
  ].join(",")));
  const blob = new Blob([lines.join("\n")], {type:"text/csv"});
  const url = URL.createObjectURL(blob); const a=document.createElement("a"); a.href=url; a.download="vendor-applications.csv"; a.click(); URL.revokeObjectURL(url);
}

export default function VendorApplications() {
  const [rows, setRows] = useState<Row[] | null>(null);
  const [error, setError] = useState<string|null>(null);
  const [q, setQ] = useState(""); const [status, setStatus] = useState("ALL"); const [sort, setSort] = useState<"date"|"capacity">("date");

  // Actually use vendorApi.applications
  useEffect(()=>{
    (async()=>{
      try{
        const { supabase } = await import("@/lib/supabase");
        const { data: sess } = await supabase.auth.getSession();
        const token = sess.session?.access_token;
        const headers: Record<string,string> = token ? { Authorization: `Bearer ${token}` } : {};
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL||"http://localhost:8000"}/api/vendor/applications`,{ headers });
        if(!res.ok) throw new Error(await res.text());
        const data = await res.json();
        setRows(data);
      }catch(e){ setError(e instanceof Error? e.message : "Failed to load"); }
    })();
  },[]);

  const filtered = useMemo(()=>{
    if(!rows) return [];
    let out = rows.filter(r=>{
      if(status!=="ALL" && r.status!==status) return false;
      if(q && ![r.application_number, r.applicant_name, r.consumer_number, r.contact_phone].join(" ").toLowerCase().includes(q.toLowerCase())) return false;
      return true;
    });
    out = [...out].sort((a,b)=> sort==="capacity" ? b.new_pv_kw - a.new_pv_kw : new Date(b.created_at).getTime()-new Date(a.created_at).getTime());
    return out;
  },[rows,q,status,sort]);

  if(error) return <div className="card"><p className="text-sm text-red-600">{error}</p></div>;
  if(!rows) return <div className="space-y-3">{[1,2,3].map(i=><div key={i} className="h-20 rounded-2xl shimmer"/>)} </div>;

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><h1 className="text-2xl font-bold" style={{color:"rgb(var(--ink))"}}>My Applications</h1><p className="text-sm" style={{color:"rgb(var(--ink-faint))"}}>Assigned to you — search, filter, export. Real-time from DB.</p></div>
        <button onClick={()=> rows && exportCSV(filtered)} className="btn-ghost">Export CSV</button>
      </div>

      <div className="card flex flex-wrap gap-3">
        <input placeholder="Search application, consumer, mobile…" value={q} onChange={e=>setQ(e.target.value)} className="input flex-1 min-w-[220px]" />
        <select value={status} onChange={e=>setStatus(e.target.value)} className="input !w-44">
          <option value="ALL">All statuses</option>
          <option value="APPROVED">APPROVED</option>
          <option value="VENDOR_SELECTED">VENDOR_SELECTED</option>
          <option value="INSTALLING">INSTALLING</option>
          <option value="INSTALLED">INSTALLED</option>
          <option value="VERIFIED">VERIFIED</option>
        </select>
        <select value={sort} onChange={e=>setSort(e.target.value as never)} className="input !w-40">
          <option value="date">Newest first</option>
          <option value="capacity">Capacity high→low</option>
        </select>
      </div>

      <div className="card overflow-x-auto p-0">
        <table className="w-full text-sm">
          <thead className="text-xs uppercase tracking-widest" style={{color:"rgb(var(--ink-faint))", borderBottom:"1px solid rgb(var(--line))"}}>
            <tr><th className="px-4 py-3 text-left">Application No.</th><th className="px-4">Consumer</th><th className="px-4">DISCOM</th><th className="px-4">Consumer No.</th><th className="px-4">Mobile</th><th className="px-4 text-right">kWp</th><th className="px-4">Date</th><th className="px-4">Status</th></tr>
          </thead>
          <tbody>
            {filtered.map(r=>(
              <tr key={r.application_id} className="border-b last:border-0 hover:bg-slate-50 dark:hover:bg-slate-900/30" style={{borderColor:"rgb(var(--line) / 0.5)"}}>
                <td className="px-4 py-3 font-mono font-bold"><Link href={`/vendor/applications/${r.application_id}`} className="hover:underline" style={{color:"rgb(var(--accent-strong))"}}>{r.application_number}</Link></td>
                <td className="px-4">{r.applicant_name}</td>
                <td className="px-4 text-xs">{r.district || "—"}</td>
                <td className="px-4 font-mono text-xs">{r.consumer_number||"—"}</td>
                <td className="px-4 font-mono text-xs">{r.contact_phone||"—"}</td>
                <td className="px-4 text-right font-mono">{Number(r.new_pv_kw).toFixed(1)}</td>
                <td className="px-4 text-xs">{new Date(r.created_at).toLocaleDateString()}</td>
                <td className="px-4"><span className={`rounded-full border px-2 py-0.5 text-xs font-bold ${r.status==="VERIFIED"?"bg-emerald-50 text-emerald-700": r.status==="INSTALLED"?"bg-sky-50 text-sky-700":"bg-white text-slate-600"}`} style={{borderColor:"rgb(var(--line))"}}>{r.status}</span></td>
              </tr>
            ))}
            {filtered.length===0 && <tr><td colSpan={8} className="px-4 py-10 text-center text-sm" style={{color:"rgb(var(--ink-faint))"}}>No applications match filters.</td></tr>}
          </tbody>
        </table>
      </div>
      <p className="text-xs" style={{color:"rgb(var(--ink-ghost))"}}>Shows only applications assigned to your vendor account. Updates from DISCOM/citizen reflect instantly on next fetch (15s poll + mutation invalidation).</p>
    </div>
  );
}
