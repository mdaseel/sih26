"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { supabase } from "@/lib/supabase";

async function roleForUser(userId: string): Promise<string | null> {
  const { data } = await supabase.from("profiles").select("role").eq("id", userId).single();
  return (data as { role?: string } | null)?.role ?? null;
}

export default function VendorLogin() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  async function onSubmit(e: React.FormEvent) {
    e.preventDefault(); setError(null); setBusy(true);
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) { setError(error.message); setBusy(false); return; }
    const role = await roleForUser(data.user!.id).catch(()=>null);
    if (role !== "VENDOR") {
      await supabase.auth.signOut();
      const hint = role==="CITIZEN" ? "Use /login (citizen portal)" : role==="DISCOM" ? "Use /discom/login" : "/login";
      setError(`This portal is for VENDOR accounts only. Your role is ${role ?? "unknown"}. Please sign in at ${hint}. ${role==="CITIZEN" ? "If you just registered as vendor, your role was fixed — try again, or use vendor@gmail.com which is now VENDOR." : ""}`);
      setBusy(false); return;
    }
    setBusy(false); router.replace("/vendor/dashboard");
  }
  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-semibold" style={{color:"rgb(var(--ink))"}}>SolarGrid<span style={{color:"#10b981"}}> Vendor</span></h1>
          <p className="mt-2 text-sm" style={{color:"rgb(var(--ink-faint))"}}>Installer portal — VENDOR only</p>
        </div>
        <form onSubmit={onSubmit} className="card space-y-4 !p-6" style={{boxShadow:"0 16px 40px rgb(var(--shadow)/0.1)"}}>
          <div><label className="label" htmlFor="email">Email</label><input id="email" type="email" required className="input" value={email} onChange={e=>setEmail(e.target.value)} autoComplete="email" placeholder="vendor@gmail.com" /></div>
          <div><label className="label" htmlFor="password">Password</label><input id="password" type="password" required className="input" value={password} onChange={e=>setPassword(e.target.value)} autoComplete="current-password" /></div>
          {error && <p className="rounded-lg border p-3 text-xs" style={{borderColor:"rgb(220 38 38 / 0.3)", background:"rgb(254 226 226)", color:"rgb(153 27 27)"}}>{error}</p>}
          <button type="submit" disabled={busy} className="btn-primary w-full !py-3">{busy?"Signing in…":"Sign in → Vendor"}</button>
          <div className="flex justify-center gap-4 text-xs"><Link href="/login" className="hover:underline" style={{color:"rgb(var(--accent-strong))"}}>Citizen login</Link><Link href="/discom/login" className="hover:underline" style={{color:"rgb(var(--accent-strong))"}}>DISCOM login</Link></div>
        </form>
        <p className="mt-4 text-center text-sm" style={{color:"rgb(var(--ink-faint))"}}>New installer? <Link href="/vendor/register" className="hover:underline" style={{color:"#10b981"}}>Register</Link></p>
        <div className="mt-4 rounded-xl border p-3 text-xs" style={{borderColor:"rgb(var(--line))", background:"rgb(var(--panel)/0.8)", color:"rgb(var(--ink-faint))"}}>
          <div className="font-semibold" style={{color:"rgb(var(--ink))"}}>Demo credentials</div>
          <div className="mt-1 font-mono">vendor@gmail.com / vendor@12345</div>
        </div>
      </div>
    </div>
  );
}
