"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { supabase } from "@/lib/supabase";

async function roleForUser(userId: string): Promise<string | null> {
  const { data } = await supabase.from("profiles").select("role").eq("id", userId).single();
  return (data as { role?: string } | null)?.role ?? null;
}

export default function DiscomLogin() {
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
    if (role !== "DISCOM" && role !== "ADMIN") {
      await supabase.auth.signOut();
      const hint = role==="VENDOR" ? "/vendor/login" : "/login";
      setError(`This portal is for DISCOM/ADMIN only. Your role is ${role ?? "unknown"}. Sign in at ${hint}.`);
      setBusy(false); return;
    }
    setBusy(false); router.replace("/discom/dashboard");
  }
  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-semibold" style={{color:"rgb(var(--ink))"}}>SolarGrid<span style={{color:"rgb(var(--accent))"}}> DISCOM</span></h1>
          <p className="mt-2 text-sm" style={{color:"rgb(var(--ink-faint))"}}>Review console — DISCOM / ADMIN only</p>
        </div>
        <form onSubmit={onSubmit} className="card space-y-4 !p-6" style={{boxShadow:"0 16px 40px rgb(var(--shadow) / 0.1)"}}>
          <div><label className="label" htmlFor="email">Email</label><input id="email" type="email" required className="input" value={email} onChange={e=>setEmail(e.target.value)} autoComplete="email" placeholder="demo.discom@solargrid.test" /></div>
          <div><label className="label" htmlFor="password">Password</label><input id="password" type="password" required className="input" value={password} onChange={e=>setPassword(e.target.value)} autoComplete="current-password" /></div>
          {error && <p className="rounded-xl border p-3 text-xs" style={{borderColor:"rgb(220 38 38 / 0.3)", background:"rgb(254 226 226)", color:"rgb(153 27 27)"}}>{error}</p>}
          <button type="submit" disabled={busy} className="btn-primary w-full !py-3">{busy?"Signing in…":"Sign in → DISCOM"}</button>
          <p className="text-center text-xs" style={{color:"rgb(var(--ink-faint))"}}>Not DISCOM? <Link href="/login" className="font-semibold hover:underline" style={{color:"rgb(var(--accent-strong))"}}>Citizen</Link> · <Link href="/vendor/login" className="font-semibold hover:underline" style={{color:"rgb(var(--accent-strong))"}}>Vendor</Link></p>
        </form>
        <div className="mt-4 rounded-xl border p-3 text-xs" style={{borderColor:"rgb(var(--line))", background:"rgb(var(--panel)/0.8)", color:"rgb(var(--ink-faint))"}}>
          <div className="font-semibold" style={{color:"rgb(var(--ink))"}}>Demo credentials</div>
          <div className="mt-1 font-mono">demo.discom@solargrid.test / abc12345</div>
        </div>
      </div>
    </div>
  );
}
