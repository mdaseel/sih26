"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { supabase, supabaseConfigured } from "@/lib/supabase";

async function roleForUser(userId: string): Promise<string | null> {
  const { data } = await supabase.from("profiles").select("role").eq("id", userId).single();
  return (data as { role?: string } | null)?.role ?? null;
}

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  async function onSubmit(e: React.FormEvent) {
    e.preventDefault(); setError(null); setBusy(true);
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) { setError(error.message); setBusy(false); return; }
    const userId = data.user?.id;
    if (userId) {
      const role = await roleForUser(userId).catch(()=>null);
      if (role !== "CITIZEN") {
        await supabase.auth.signOut();
        const portal = role === "VENDOR" ? "/vendor/login" : role === "DISCOM" || role === "ADMIN" ? "/discom/login" : "/login";
        setError(`This citizen portal is for CITIZEN accounts only. Your role is ${role}. Please sign in at ${portal}`);
        setBusy(false);
        return;
      }
    }
    setBusy(false);
    router.replace("/citizen/dashboard");
  }
  return (
    <div className="flex min-h-screen items-center justify-center px-6 py-10" style={{ background: "radial-gradient(800px 400px at 50% -10%, rgb(var(--accent) / 0.12), transparent), radial-gradient(600px 400px at 90% 90%, rgb(var(--brand) / 0.12), transparent), rgb(var(--surface))" }}>
      <div className="w-full max-w-sm animate-scale-in">
        <div className="mb-8 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl text-lg font-black" style={{ background: "rgb(var(--brand))", color: "rgb(var(--brand-ink))" }}>◈</div>
          <h1 className="mt-4 text-2xl font-bold tracking-tight" style={{ color: "rgb(var(--ink))" }}>Citizen — Welcome back</h1>
          <p className="mt-2 text-sm" style={{ color: "rgb(var(--ink-faint))" }}>CITIZEN accounts only. Vendors: use Vendor login. DISCOM: use DISCOM login.</p>
        </div>
        {!supabaseConfigured && <p className="mb-4 rounded-xl border p-3 text-xs" style={{ borderColor: "rgb(220 38 38 / 0.3)", background: "rgb(254 226 226)", color: "rgb(153 27 27)" }}>Supabase not configured.</p>}
        <form onSubmit={onSubmit} className="card space-y-4 !p-6" style={{ boxShadow: "0 16px 40px rgb(var(--shadow) / 0.1)" }}>
          <div><label className="label" htmlFor="email">Email</label><input id="email" type="email" required className="input" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" placeholder="demo.citizen@solargrid.local" /></div>
          <div><label className="label" htmlFor="password">Password</label><input id="password" type="password" required className="input" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" placeholder="••••••••" /></div>
          {error && <p className="rounded-xl border p-3 text-xs animate-slide-up" style={{ borderColor: "rgb(220 38 38 / 0.3)", background: "rgb(254 226 226)", color: "rgb(153 27 27)" }}>{error}</p>}
          <button type="submit" disabled={busy} className="btn-primary w-full !py-3 text-sm">{busy ? "Signing in…" : "Sign in → Citizen"}</button>
          <div className="flex justify-center gap-4 text-xs">
            <Link href="/vendor/login" className="hover:underline" style={{color:"rgb(var(--accent-strong))"}}>Vendor login</Link>
            <Link href="/discom/login" className="hover:underline" style={{color:"rgb(var(--accent-strong))"}}>DISCOM login</Link>
          </div>
          <p className="text-center text-sm" style={{ color: "rgb(var(--ink-faint))" }}>No citizen account? <Link href="/register" className="font-semibold hover:underline" style={{ color: "rgb(var(--accent-strong))" }}>Register</Link></p>
        </form>
        <div className="mt-4 rounded-xl border p-3 text-xs" style={{ borderColor: "rgb(var(--line))", background: "rgb(var(--panel) / 0.8)" }}>
          <div className="font-semibold" style={{ color: "rgb(var(--ink))" }}>Demo credentials</div>
          <div className="mt-1 font-mono" style={{ color: "rgb(var(--ink-faint))" }}>mohamedaaris019@gmail.com / Aaris@2617</div>
        </div>
      </div>
    </div>
  );
}
